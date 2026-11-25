"""Reference prices from the engine's own memory + SNIPER SCORE + anti-fake filters.

Reference ("precio habitual") priority:
  1. history  - this ASIN's own observed prices (median), same delivery location
  2. peers    - median current price of *equivalent* products (same model_key)
                observed by the engine in the last days
  3. prior    - orientative catalogue floor (low confidence, score capped)

Amazon's strike-through / recommended price is stored but NEVER used as reference.
"""
from __future__ import annotations

import re
import sqlite3
import statistics
import time
from dataclasses import dataclass, field

from .catalog import Identity
from .config import Settings

HARD_FLAGS = {
    "accesorio": "Accesorio o producto relacionado, no el producto principal",
    "usado": "Producto usado",
    "reacondicionado": "Producto reacondicionado",
    "caja_vacia_o_incompleto": "Caja vacía o producto incompleto",
    "pieza_o_repuesto": "Pieza, repuesto o producto defectuoso",
    "videojuego_no_consola": "Videojuego, no consola",
    "sin_stock": "Sin existencias",
    "envio_desproporcionado": "Gastos de envío desproporcionados",
    "condicion_no_nueva": "Condición distinta de nuevo",
}

WEIGHTS = {
    "vs_habitual": 22, "vs_history_min": 8, "saving_eur": 8, "vs_peers": 12, "value": 8,
    "velocity": 8, "seller": 10, "condition_stock": 8, "coherence": 8, "info_quality": 8,
}
assert sum(WEIGHTS.values()) == 100


@dataclass
class Observation:
    asin: str
    price: float
    title: str
    source: str                       # listing | search | product
    geo: str | None = None
    offers_from: bool = False
    seller: str | None = None
    fulfillment: str = "unknown"
    condition: str = "unknown"
    availability: str = "unknown"
    shipping: float | None = None
    list_price: float | None = None
    ts: float = field(default_factory=time.time)


@dataclass
class Reference:
    price: float | None = None
    source: str | None = None          # history | peers | prior
    history_median: float | None = None
    history_min: float | None = None
    history_n: int = 0
    history_span_h: float = 0.0
    peers_median: float | None = None
    peers_n: int = 0
    prior: float | None = None
    previous_price: float | None = None
    previous_ts: float | None = None


@dataclass
class Evaluation:
    score: float
    tier: str
    confidence: str
    reference: Reference
    discount: float | None
    saving: float | None
    components: dict
    flags: list                       # hard problems (reject)
    warnings: list                    # soft doubts
    rejected: bool


def _curve(d: float) -> float:
    """Discount -> 0..1. Strict: 20 % is worth nothing, 80 % is full."""
    pts = [(0.0, 0.0), (0.2, 0.0), (0.4, 0.3), (0.6, 0.7), (0.8, 1.0), (1.0, 1.0)]
    d = max(0.0, min(1.0, d))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= d <= x1:
            return y0 + (y1 - y0) * (d - x0) / (x1 - x0)
    return 1.0


def _interp(x: float, pts: list[tuple[float, float]]) -> float:
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def tier_for(score: float) -> str:
    if score >= 90:
        return "extreme"
    if score >= 75:
        return "exceptional"
    if score >= 60:
        return "interesting"
    return "discard"


# ----------------------------------------------------------------- references
def build_reference(conn: sqlite3.Connection, obs: Observation, idn: Identity, s: Settings) -> Reference:
    ref = Reference(prior=idn.prior_eur)
    cutoff = obs.ts - 60 * 86400
    geo_clause = "AND COALESCE(geo,'') = COALESCE(?, '')"
    # own history (exclude anything from the current minute = the observation itself)
    hist = conn.execute(
        f"""SELECT price, ts FROM observations
            WHERE asin=? AND price IS NOT NULL AND ts > ? AND ts < ? AND offers_from = ? {geo_clause}
            ORDER BY ts""",
        (obs.asin, cutoff, obs.ts - 60, int(obs.offers_from), obs.geo),
    ).fetchall()
    if hist:
        prices = [r["price"] for r in hist]
        ref.history_median = statistics.median(prices)
        ref.history_min = min(prices)
        ref.history_n = len(prices)
        ref.history_span_h = (hist[-1]["ts"] - hist[0]["ts"]) / 3600
        ref.previous_price, ref.previous_ts = hist[-1]["price"], hist[-1]["ts"]

    # equivalent products (peers): latest price of each other ASIN of the same model
    if idn.model_key:
        peer_rows = conn.execute(
            f"""SELECT o.asin, o.price FROM observations o
                JOIN products p ON p.asin = o.asin
                WHERE p.model_key = ? AND o.asin != ? AND p.is_accessory = 0
                  AND o.price IS NOT NULL AND o.offers_from = 0 AND o.ts > ?
                  AND COALESCE(o.geo,'') = COALESCE(?, '')
                  AND o.id = (SELECT MAX(id) FROM observations o2 WHERE o2.asin = o.asin AND o2.price IS NOT NULL)""",
            (idn.model_key, obs.asin, obs.ts - 14 * 86400, obs.geo),
        ).fetchall()
        peers = [r["price"] for r in peer_rows]
        if peers:
            ref.peers_median = statistics.median(peers)
            ref.peers_n = len(peers)

    if ref.history_n >= max(2, s.min_history_obs - 1) and ref.history_median:
        ref.price, ref.source = ref.history_median, "history"
    elif ref.peers_n >= s.min_peers and ref.peers_median:
        ref.price, ref.source = ref.peers_median, "peers"
    elif ref.history_n >= 1 and ref.peers_n >= 1:
        ref.price, ref.source = max(ref.history_median, ref.peers_median), "history"
    elif ref.prior:
        ref.price, ref.source = ref.prior, "prior"
    return ref


# ----------------------------------------------------------------- score
def evaluate(conn: sqlite3.Connection, obs: Observation, idn: Identity, s: Settings,
             verified_product_page: bool = False) -> Evaluation:
    flags = list(idn.flags)
    warnings = list(idn.warnings)
    if obs.availability == "out_of_stock":
        flags.append("sin_stock")
    if obs.condition in ("used",):
        flags.append("usado")
    if obs.condition == "refurbished":
        flags.append("reacondicionado")
    if obs.shipping and obs.shipping > max(20.0, 0.25 * obs.price):
        flags.append("envio_desproporcionado")

    ref = build_reference(conn, obs, idn, s)
    eff_price = obs.price + (obs.shipping or 0.0)
    comps = {k: 0.0 for k in WEIGHTS}
    discount = saving = None

    if ref.price and ref.price > 0:
        discount = max(0.0, 1 - eff_price / ref.price)
        saving = max(0.0, ref.price - eff_price)
        comps["vs_habitual"] = _curve(discount)
        comps["saving_eur"] = _interp(saving, [(50, 0), (200, 0.3), (500, 0.6), (1500, 1.0)])
        comps["value"] = _interp(ref.price, [(100, 0.15), (250, 0.35), (500, 0.6), (1000, 0.8), (2000, 1.0)])
    if ref.history_min:
        comps["vs_history_min"] = _interp(eff_price / ref.history_min, [(0.5, 1.0), (0.9, 0.2), (1.0, 0.0)])
    if ref.peers_median and ref.peers_n >= 2:
        comps["vs_peers"] = _curve(max(0.0, 1 - eff_price / ref.peers_median)) * (1.0 if ref.peers_n >= s.min_peers else 0.6)
    if ref.previous_price:
        drop = 1 - eff_price / ref.previous_price
        hours = max(0.1, (obs.ts - (ref.previous_ts or obs.ts)) / 3600)
        comps["velocity"] = _curve(drop) * (1.0 if hours <= 48 else 0.7)
    elif ref.source == "peers":
        comps["velocity"] = 0.5      # first sighting already far below equivalent products
    # A listing price that is NOT "N ofertas desde" is the featured offer (buy box), which Amazon
    # only awards to new, buyable offers: better than fully unknown, worse than a checked product page.
    buybox = obs.source in ("listing", "search") and not obs.offers_from
    comps["seller"] = {"amazon": 1.0, "fba": 0.7, "third_party": 0.3}.get(obs.fulfillment, 0.5 if buybox else 0.3)
    if obs.condition == "new" and obs.availability in ("in_stock", "limited"):
        comps["condition_stock"] = 1.0 if obs.availability == "in_stock" else 0.8
    elif obs.availability in ("in_stock", "limited"):
        comps["condition_stock"] = 0.7
    else:
        comps["condition_stock"] = 0.7 if buybox else 0.4
    coh = 1.0 if idn.model_key else 0.3
    coh -= 0.5 * len([w for w in warnings if w.startswith("titulo") or w.startswith("posible")])
    comps["coherence"] = max(0.0, coh)
    info = {"product": 1.0, "search": 0.7, "listing": 0.6}.get(obs.source, 0.5)
    if obs.offers_from:
        info -= 0.3
        warnings.append("precio_desde_varias_ofertas")
    if ref.source == "prior":
        info -= 0.3
        warnings.append("referencia_estimada_sin_historial")
    if obs.geo and not re.search(r"espa|\b\d{5}\b|actualizar|update", obs.geo, re.I):  # Spain / postcode / not set
        info -= 0.1
        warnings.append(f"ubicacion_entrega:{obs.geo}")
    comps["info_quality"] = max(0.0, info)

    score = sum(WEIGHTS[k] * v for k, v in comps.items())

    # ---- strict caps
    if discount is None:
        score = min(score, 40)
    else:
        if discount < 0.35:
            score = min(score, 59)
        elif discount < 0.5:
            score = min(score, 74)
        elif discount < 0.65:
            score = min(score, 89)
        if ref.price and eff_price < 0.03 * ref.price and not (verified_product_page and obs.fulfillment == "amazon"):
            warnings.append("precio_inverosimil_posible_anuncio_erroneo")
            score = min(score, 74)
    if ref.source == "prior":
        score = min(score, 88)
    if obs.offers_from and not verified_product_page:
        score = min(score, 84)      # lowest of several offers may be used / third-party: must be verified
    if not idn.model_key and ref.source != "history":
        score = min(score, 59)

    rejected = bool(flags)
    if rejected:
        score = 0.0
    score = round(max(0.0, min(100.0, score)), 1)

    if ref.source == "history" and ref.history_n >= s.min_history_obs and ref.history_span_h >= s.min_history_span_h:
        confidence = "ALTA" if (verified_product_page or ref.peers_n >= s.min_peers) else "MEDIA"
    elif ref.source in ("history", "peers"):
        confidence = "MEDIA"
    else:
        confidence = "BAJA"
    if obs.offers_from and confidence != "BAJA":
        confidence = "BAJA" if not verified_product_page else confidence

    return Evaluation(score, tier_for(score), confidence, ref, discount, saving,
                      {k: round(v, 3) for k, v in comps.items()}, flags, warnings, rejected)
