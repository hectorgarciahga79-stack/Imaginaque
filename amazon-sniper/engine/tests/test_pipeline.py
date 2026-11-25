"""End-to-end pipeline test WITHOUT network.

Uses the real saved bestseller page; the 'price error' is injected ONLY inside
this test (one RTX 5070 re-priced to 179 €) and the product page is a minimal
test double with Amazon's public element ids. Nothing touches the real DB.
"""
from pathlib import Path

from sniper import db
from sniper.config import Settings
from sniper.engine import Engine
from sniper.fetcher import FetchResult

FIX = Path(__file__).parent / "fixtures"
REAL_LISTING = (FIX / "bestsellers_gpu.html").read_text(encoding="utf-8", errors="ignore")
TARGET = "B0DX7GSX7B"  # MSI GeForce RTX 5070 12G GAMING TRIO OC, really listed at 894,13 € in the fixture

PRODUCT_PAGE = """<html><head><title>Amazon.es</title></head><body>
<span id="glow-ingress-line2">Estados Unidos</span>
<span id="productTitle"> MSI GeForce RTX 5070 12G GAMING TRIO OC - Tarjeta gráfica | 12 GB GDDR7 </span>
<div id="corePrice_feature_div"><span class="a-price"><span class="a-offscreen">{price}</span>
<span class="a-price-whole">{whole}<span class="a-price-decimal">,</span></span><span class="a-price-fraction">{frac}</span></span></div>
<div id="availability"><span>En stock</span></div>
<div id="merchantInfoFeature_feature_div">Vendido por Amazon</div>
<div id="fulfillerInfoFeature_feature_div">Enviado por Amazon</div>
<div id="deliveryBlockMessage">Entrega GRATIS el viernes</div>
<input id="add-to-cart-button" type="submit"/>
</body></html>"""


class FakeFetcher:
    def __init__(self):
        self.listing_html = REAL_LISTING
        self.product_price = "179,00"
        self.calls = []

    def update_settings(self, s):
        pass

    def close(self):
        pass

    def get(self, url, kind):
        self.calls.append((kind, url))
        if "/dp/" in url:
            w, f = self.product_price.split(",")
            return FetchResult(url, 200, PRODUCT_PAGE.format(price=self.product_price + " €", whole=w, frac=f), "ok")
        return FetchResult(url, 200, self.listing_html, "ok")


def make_engine(tmp_path):
    conn = db.connect(tmp_path / "e2e.db")
    s = Settings()
    s.desktop_notifications = False
    for k, v in s.to_dict().items():
        conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (k, __import__("json").dumps(v)))
    fake = FakeFetcher()
    eng = Engine(conn, s, fake)
    eng.seed()
    return conn, eng, fake


def run_gpu_listing(conn, eng):
    t = conn.execute("SELECT * FROM tasks WHERE key='listing:bestsellers:computers:937935031:p1'").fetchone()
    eng.run_task(t)


def test_full_pipeline_detects_verifies_and_alerts(tmp_path):
    conn, eng, fake = make_engine(tmp_path)

    # 1) first pass: real prices -> builds own memory, no anomalies
    run_gpu_listing(conn, eng)
    assert conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 30
    assert conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0] == 0
    # pretend that observation happened yesterday
    conn.execute("UPDATE observations SET ts = ts - 86400")
    # discovery added sub-categories
    assert conn.execute("SELECT COUNT(DISTINCT node) FROM categories").fetchone()[0] > 3

    # 2) the price error appears on the listing
    fake.listing_html = REAL_LISTING.replace("894,13", "179,00")
    assert fake.listing_html != REAL_LISTING
    run_gpu_listing(conn, eng)

    opp = conn.execute("SELECT * FROM opportunities WHERE asin=?", (TARGET,)).fetchone()
    assert opp is not None, "anomaly not detected"
    assert opp["price"] == 179.0
    assert opp["status"] == "verified", opp["verification"]
    assert opp["fulfillment"] == "amazon"
    assert opp["score"] > 85, (opp["score"], opp["components"])
    # verification fetched the product page
    assert any(k == "product" and TARGET in u for k, u in fake.calls)
    alert = conn.execute("SELECT * FROM alerts WHERE opportunity_id=?", (opp["id"],)).fetchone()
    assert alert is not None and "RTX 5070" in alert["title"]
    # only one alert in the whole run (no noise)
    assert conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] == 1


def test_price_gone_on_verification_expires_and_never_alerts(tmp_path):
    conn, eng, fake = make_engine(tmp_path)
    run_gpu_listing(conn, eng)
    conn.execute("UPDATE observations SET ts = ts - 86400")
    fake.listing_html = REAL_LISTING.replace("894,13", "179,00")
    fake.product_price = "894,13"  # Amazon already fixed it when we re-check
    run_gpu_listing(conn, eng)
    opp = conn.execute("SELECT * FROM opportunities WHERE asin=? ORDER BY id LIMIT 1", (TARGET,)).fetchone()
    assert opp["status"] == "expired"
    assert conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] == 0


def test_blocked_source_backs_off_and_is_skipped(tmp_path):
    conn, eng, fake = make_engine(tmp_path)
    blocked = (FIX / "blocked_503.html").read_text(encoding="utf-8")
    fake.get = lambda url, kind: FetchResult(url, 503, blocked, "blocked", "amazon_automated_access_notice")
    t = conn.execute("SELECT * FROM tasks WHERE kind='search' ORDER BY priority LIMIT 1").fetchone()
    eng.run_task(t)
    assert eng.is_blocked("search")
    nxt = eng.next_task()
    assert nxt is None or nxt["kind"] != "search"
    assert conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 0  # nothing invented


def test_blocked_sources_do_not_starve_available_ones(tmp_path):
    conn, eng, fake = make_engine(tmp_path)
    import time as _t
    from sniper import db as _db
    far = _t.time() + 3600
    _db.state_set(conn, "blocks", {"search": {"until": far}, "listing:bestsellers": {"until": far}})
    t = eng.next_task()
    assert t is not None
    assert "/gp/new-releases/" in t["url"] or "/gp/movers-and-shakers/" in t["url"]
