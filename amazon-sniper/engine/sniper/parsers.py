"""HTML parsers for Amazon.es pages.

* Listing pages (/gp/bestsellers, /gp/new-releases, /gp/movers-and-shakers):
  verified against real pages saved in tests/fixtures.
* Search result pages (/s?k=) and product pages (/dp/ASIN): written against
  Amazon's documented public markup (data-asin, #productTitle, #corePrice...).
  Amazon refuses these pages to the datacenter where this was built, so they
  must be validated on the machine that runs the engine (`sniper doctor`).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup

ASIN_RX = re.compile(r"/(?:dp|gp/product)/([A-Z0-9]{10})")


@dataclass
class Item:
    asin: str
    title: str = ""
    price: float | None = None
    list_price: float | None = None
    shipping: float | None = None
    url: str = ""
    image: str = ""
    rank: int | None = None
    offers_from: bool = False       # "N ofertas desde X €": lowest of several offers (may be used/3rd party)
    offers_count: int | None = None
    seller: str | None = None
    ships_from: str | None = None
    fulfillment: str = "unknown"    # amazon | fba | third_party | unknown
    condition: str = "unknown"      # new | used | refurbished | unknown
    availability: str = "unknown"   # in_stock | out_of_stock | limited | unknown
    variant: str | None = None
    sponsored: bool = False
    extra: dict = field(default_factory=dict)


def parse_eur(text: str | None) -> float | None:
    """'1.239,66 €' -> 1239.66 ; '693,38\xa0€' -> 693.38 ; '1239,66' -> 1239.66"""
    if not text:
        return None
    t = text.replace("\xa0", " ").replace("€", " ").replace("EUR", " ").strip()
    m = re.search(r"\d[\d.\s]*(?:,\d{1,2})?", t)
    if not m:
        return None
    num = m.group(0).replace(" ", "")
    if "," in num:
        whole, frac = num.rsplit(",", 1)
        whole = whole.replace(".", "")
    else:
        # "1.239" (thousands) vs "12.99" (rare decimal point)
        parts = num.split(".")
        if len(parts) > 1 and len(parts[-1]) == 2:
            whole, frac = "".join(parts[:-1]), parts[-1]
        else:
            whole, frac = num.replace(".", ""), "0"
    try:
        return round(float(f"{int(whole)}.{frac}"), 2)
    except ValueError:
        return None


def _a_price(node) -> float | None:
    """Amazon `.a-price` widget: whole + fraction are the reliable parts."""
    if node is None:
        return None
    whole = node.select_one(".a-price-whole")
    frac = node.select_one(".a-price-fraction")
    if whole:
        w = re.sub(r"[^\d]", "", whole.get_text())
        f = re.sub(r"[^\d]", "", frac.get_text()) if frac else "0"
        if w:
            return round(float(f"{int(w)}.{f or '0'}"), 2)
    off = node.select_one(".a-offscreen")
    return parse_eur(off.get_text()) if off else None


def _clean(t: str | None) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()


def _abs(base: str, href: str | None) -> str:
    return urljoin(base, href) if href else ""


def delivery_location(soup) -> str | None:
    """Amazon prices depend on the delivery country (VAT is removed for
    non-EU destinations), so every observation records it."""
    n = soup.select_one("#glow-ingress-line2")
    return _clean(n.get_text()) if n else None


def canonical_url(base: str, asin: str) -> str:
    return f"{base}/dp/{asin}"


# ---------------------------------------------------------------- listings
def parse_listing(html: str, base: str) -> dict:
    """Bestsellers / new releases / movers & shakers pages."""
    soup = BeautifulSoup(html, "lxml")
    items: list[Item] = []
    seen = set()
    for card in soup.select("div.p13n-sc-uncoverable-faceout, div[id][data-asin]"):
        asin = card.get("id") or card.get("data-asin")
        if not asin or not re.fullmatch(r"[A-Z0-9]{10}", asin) or asin in seen:
            continue
        seen.add(asin)
        it = Item(asin=asin, url=canonical_url(base, asin))
        tnode = card.select_one("div[class*=line-clamp]") or card.select_one("a span div")
        img = card.select_one("img")
        it.title = _clean(tnode.get_text() if tnode else (img.get("alt") if img else ""))
        if img:
            it.image = img.get("src", "")
        text = _clean(card.get_text(" "))
        m = re.search(r"(\d+)\s+ofertas?\s+desde", text, re.I)
        if m:
            it.offers_from = True
            it.offers_count = int(m.group(1))
            it.price = _a_price(card.select_one(".a-price"))
        else:
            pnode = card.select_one("span[class*=p13n-sc-price]") or card.select_one(".a-price")
            if pnode is not None:
                it.price = _a_price(pnode) if "a-price" in (pnode.get("class") or []) else parse_eur(pnode.get_text())
        # rank badge lives just before the card
        badge = card.find_previous("span", class_="zg-bdg-text")
        if badge:
            rm = re.search(r"\d+", badge.get_text())
            it.rank = int(rm.group(0)) if rm else None
        items.append(it)

    # rank metadata (covers items 1..50 even when only 30 are rendered)
    ranks = {}
    rec = soup.select_one("[data-client-recs-list]")
    if rec:
        try:
            for e in json.loads(rec["data-client-recs-list"]):
                r = e.get("metadataMap", {}).get("render.zg.rank")
                if r:
                    ranks[e["id"]] = int(r)
        except (ValueError, KeyError, TypeError):
            pass
    for it in items:
        if it.asin in ranks:
            it.rank = ranks[it.asin]

    # category tree for autonomous discovery
    subcats = []
    for a in soup.select("div[role=group] a[href], div[role=treeitem] a[href]"):
        href = a.get("href", "")
        m = re.search(r"/gp/(bestsellers|new-releases|movers-and-shakers)/([a-z\-]+)/(\d+)", href)
        if m:
            subcats.append({"list_type": m.group(1), "store": m.group(2), "node": m.group(3), "name": _clean(a.get_text())})
    title = _clean(soup.title.get_text()) if soup.title else ""
    geo = delivery_location(soup)
    cat = re.sub(r"^Amazon\.es\s+[^:]+:\s*(Los productos más populares en|Las novedades y los futuros lanzamientos más vendidos en|Los productos que más han subido.*? en)\s*", "", title)
    return {"items": items, "subcategories": subcats, "category_name": cat, "title": title, "geo": geo}


# ---------------------------------------------------------------- search
def parse_search(html: str, base: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    items: list[Item] = []
    for card in soup.select("div[data-component-type=s-search-result][data-asin]"):
        asin = card.get("data-asin")
        if not asin or not re.fullmatch(r"[A-Z0-9]{10}", asin):
            continue
        it = Item(asin=asin, url=canonical_url(base, asin))
        h = card.select_one("h2")
        it.title = _clean(h.get_text() if h else "")
        img = card.select_one("img.s-image")
        if img:
            it.image = img.get("src", "")
        prices = card.select("span.a-price:not(.a-text-price)")
        it.price = _a_price(prices[0]) if prices else None
        lp = card.select_one("span.a-price.a-text-price")
        it.list_price = _a_price(lp) if lp else None
        text = _clean(card.get_text(" "))
        it.sponsored = bool(re.search(r"\bPatrocinado\b|\bSponsored\b", text))
        if re.search(r"reacondicionado|renewed|renovado", text, re.I):
            it.condition = "refurbished"
        if re.search(r"No disponible|Actualmente no disponible", text, re.I):
            it.availability = "out_of_stock"
        m = re.search(r"(\d+)\s+ofertas?\s+(?:de\s+productos?\s+)?(?:nuevos?|usados?)?\s*desde", text, re.I)
        if m and it.price is None:
            it.offers_from = True
        items.append(it)
    nxt = soup.select_one("a.s-pagination-next")
    return {"items": items, "next": _abs(base, nxt.get("href")) if nxt else None, "geo": delivery_location(soup)}


# ---------------------------------------------------------------- product page
def parse_product(html: str, base: str, asin: str | None = None) -> Item | None:
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("#productTitle")
    if not title:
        return None
    if asin is None:
        node = soup.select_one("input#ASIN, input[name=ASIN]")
        asin = node.get("value") if node else None
    if not asin:
        m = ASIN_RX.search(html)
        asin = m.group(1) if m else None
    if not asin:
        return None
    it = Item(asin=asin, url=canonical_url(base, asin), title=_clean(title.get_text()))
    it.extra["geo"] = delivery_location(soup)

    core = soup.select_one("#corePrice_feature_div, #corePriceDisplay_desktop_feature_div, #apex_desktop")
    if core:
        it.price = _a_price(core.select_one(".a-price:not(.a-text-price)"))
        lp = core.select_one(".a-price.a-text-price")
        it.list_price = _a_price(lp) if lp else None
    if it.price is None:
        for sel in ("#priceblock_ourprice", "#priceblock_dealprice", "#price_inside_buybox", "#newBuyBoxPrice"):
            n = soup.select_one(sel)
            if n:
                it.price = parse_eur(n.get_text())
                break

    img = soup.select_one("#landingImage, #imgBlkFront")
    if img:
        it.image = img.get("data-old-hires") or img.get("src", "")

    avail = _clean((soup.select_one("#availability") or soup.new_tag("x")).get_text())
    if re.search(r"No disponible|Actualmente no disponible|Currently unavailable", avail, re.I):
        it.availability = "out_of_stock"
    elif re.search(r"Solo queda|Quedan|Only \d+ left", avail, re.I):
        it.availability = "limited"
    elif re.search(r"En stock|Disponible|In stock|Recíbelo|Entrega", avail, re.I):
        it.availability = "in_stock"
    if not soup.select_one("#add-to-cart-button, #buy-now-button"):
        if it.availability == "unknown":
            it.availability = "out_of_stock"
    it.extra["availability_text"] = avail[:200]

    # seller / fulfilment
    seller = soup.select_one("#sellerProfileTriggerId")
    merchant = _clean((soup.select_one("#merchantInfoFeature_feature_div, #merchant-info, #tabular-buybox") or soup.new_tag("x")).get_text(" "))
    ships = _clean((soup.select_one("#fulfillerInfoFeature_feature_div") or soup.new_tag("x")).get_text(" "))
    sold_by = _clean(seller.get_text()) if seller else None
    if not sold_by:
        m = re.search(r"Vendido por\s*:?\s*([^\n]+?)(?:\s+y\s+enviado|\.|$)", merchant)
        sold_by = _clean(m.group(1)) if m else None
    if not sold_by and re.search(r"\bAmazon\b", merchant):
        sold_by = "Amazon"
    it.seller = sold_by
    ship_text = ships or merchant
    it.ships_from = "Amazon" if re.search(r"Amazon", ship_text) else (_clean(ship_text)[:80] or None)
    if sold_by and re.fullmatch(r"Amazon(\.es| EU.*| Espa.*)?", sold_by, re.I):
        it.fulfillment = "amazon"
    elif sold_by and it.ships_from == "Amazon":
        it.fulfillment = "fba"
    elif sold_by:
        it.fulfillment = "third_party"

    # condition
    cond_text = _clean(" ".join(n.get_text(" ") for n in soup.select("#usedBuySection, #renewedTier2AccordionRow, #buyBoxAccordion .a-text-bold, #bylineInfo")))
    full_head = it.title + " " + cond_text
    if re.search(r"Reacondicionado|Renewed|Renovado|Amazon Renewed", full_head, re.I):
        it.condition = "refurbished"
    elif soup.select_one("#usedBuySection") and not soup.select_one("#add-to-cart-button"):
        it.condition = "used"
    else:
        it.condition = "new"

    # shipping
    ship = _clean((soup.select_one("#deliveryBlockMessage, #mir-layout-DELIVERY_BLOCK") or soup.new_tag("x")).get_text(" "))
    if re.search(r"Env[ií]o GRATIS|entrega GRATIS|GRATIS", ship, re.I):
        it.shipping = 0.0
    else:
        m = re.search(r"([\d.,]+)\s*€\s*(?:de\s+)?(?:env[ií]o|gastos)", ship, re.I)
        if m:
            it.shipping = parse_eur(m.group(1))

    # selected variant
    sel = [ _clean(n.get_text()) for n in soup.select("#twister .selection, #variation_size_name .selection, #variation_color_name .selection, #inline-twister-expanded-dimension-text-size_name")]
    sel = [s for s in sel if s]
    it.variant = " | ".join(sel) or None

    offers = soup.select_one("#olpLinkWidget_feature_div, #buybox-see-all-buying-choices")
    if offers:
        m = re.search(r"\((\d+)\)|(\d+)\s+ofertas", offers.get_text())
        if m:
            it.offers_count = int(m.group(1) or m.group(2))
    return it
