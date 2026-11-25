"""Tests. Parser tests use REAL Amazon.es pages saved in tests/fixtures.
Scoring tests use a throw-away in-memory database with synthetic observations
(they test the algorithm; nothing here ever reaches the real database)."""
from pathlib import Path
import time

import pytest

from sniper import db
from sniper.analysis import Observation, evaluate
from sniper.catalog import identify
from sniper.config import Settings
from sniper.fetcher import detect_block
from sniper.parsers import parse_eur, parse_listing

FIX = Path(__file__).parent / "fixtures"
BASE = "https://www.amazon.es"


def read(name):
    return (FIX / name).read_text(encoding="utf-8", errors="ignore")


# ------------------------------------------------------------------ parsers
def test_parse_eur():
    assert parse_eur("693,38\xa0€") == 693.38
    assert parse_eur("1.239,66 €") == 1239.66
    assert parse_eur("2.500 €") == 2500.0
    assert parse_eur("12.99") == 12.99
    assert parse_eur("") is None


def test_listing_real_gpu_bestsellers():
    r = parse_listing(read("bestsellers_gpu.html"), BASE)
    assert r["category_name"] == "Tarjetas gráficas"
    assert len(r["items"]) == 30
    assert r["geo"] == "Estados Unidos"
    first = r["items"][0]
    assert first.asin == "B0F4DVKSZ4" and first.rank == 1 and first.price == 693.38 and not first.offers_from
    offers = [i for i in r["items"] if i.offers_from]
    assert offers and all(i.offers_count for i in offers)
    assert any(s["node"] for s in r["subcategories"])


def test_listing_real_new_releases():
    r = parse_listing(read("new_releases_computers.html"), BASE)
    assert len(r["items"]) == 30
    assert sum(1 for i in r["items"] if i.price) >= 25


@pytest.mark.parametrize("name,expected", [
    ("blocked_503.html", "amazon_automated_access_notice"),
    ("blocked_interstitial.html", "amazon_automated_access_notice"),
    ("blocked_waf_challenge.html", "waf_challenge"),
])
def test_block_detection_on_real_refusals(name, expected):
    assert detect_block(200, read(name)) == expected


def test_real_listing_is_not_blocked():
    assert detect_block(200, read("bestsellers_gpu.html")) is None


# ------------------------------------------------------------------ identity
@pytest.mark.parametrize("title,key,flag", [
    ("ZOTAC GAMING GeForce RTX 5090 Solid OC 32GB GDDR7 Tarjeta gráfica", "gpu:rtx-5090", None),
    ("PNY Tarjeta Gráfica GeForce RTX™ 5070Ti Slim 16GB OC", "gpu:rtx-5070-ti", None),
    ("Soporte de GPU para RTX 4090 anti-sag", None, "accesorio"),
    ("Cable 12VHPWR compatible con RTX 5090", None, "accesorio"),
    ("Caja vacía RTX 5090 Founders Edition", None, "caja_vacia_o_incompleto"),
    ("MSI GeForce RTX 5090 32G - Reacondicionado", "gpu:rtx-5090", "reacondicionado"),
    ("EA SPORTS FC 26 (PS5)", None, "videojuego_no_consola"),
    ("PlayStation 5 - Mando inalámbrico DualSense", None, "accesorio"),
    ("Sony PlayStation 5 Pro Consola - 2TB", "console:ps5-pro", None),
    ("ASUS ROG Strix G18 Portátil Gaming Core Ultra 9 RTX 5090 64GB", "laptop:rtx-5090", None),
    ("AMD Ryzen 9 9950X3D Procesador 16 núcleos AM5", "cpu:ryzen-9-9950x3d", None),
    ("Intel Core i9-14900K Procesador de sobremesa LGA1700", "cpu:i9-14900k", None),
    ("Apple MacBook Pro de 14 pulgadas con chip M4 Pro", "apple:macbook-pro-m4-pro", None),
    ("Lector CD DVD Externo USB compatible con MacBook Pro", None, "accesorio"),
])
def test_identify(title, key, flag):
    i = identify(title)
    if key:
        assert i.model_key == key
    if flag:
        assert flag in i.flags
    else:
        assert not i.flags


# ------------------------------------------------------------------ scoring
@pytest.fixture()
def conn(tmp_path):
    c = db.connect(tmp_path / "t.db")
    yield c
    c.close()


def _peer(conn, asin, title, price, ts):
    idn = identify(title)
    conn.execute("INSERT OR IGNORE INTO products(asin,title,family,model_key,model_label,is_accessory,first_seen,last_seen) VALUES(?,?,?,?,?,0,?,?)",
                 (asin, title, idn.family, idn.model_key, idn.label, ts, ts))
    conn.execute("INSERT INTO observations(asin,ts,price,source,geo) VALUES(?,?,?,?,?)", (asin, ts, price, "listing", "España"))


def _obs(asin, title, price, **kw):
    d = dict(asin=asin, price=price, title=title, source="listing", geo="España")
    d.update(kw)
    return Observation(**d)


def test_rtx5090_at_500_vs_2500_peers_is_extreme(conn):
    now = time.time()
    for n, p in enumerate([2450, 2500, 2550, 2600]):
        _peer(conn, f"PEER{n:06d}", f"MSI GeForce RTX 5090 32G Gaming Trio {n} Tarjeta gráfica", p, now - 3600)
    t = "ASUS ROG Astral GeForce RTX 5090 32GB GDDR7 Tarjeta gráfica"
    ev = evaluate(conn, _obs("TARGET0001", t, 500.0, fulfillment="amazon", condition="new", availability="in_stock", source="product"),
                  identify(t), Settings(), verified_product_page=True)
    assert ev.reference.source == "peers"
    assert ev.discount > 0.79
    assert ev.score > 85, ev.components
    assert ev.tier in ("exceptional", "extreme")


def test_same_but_only_listing_info_still_scores_high(conn):
    now = time.time()
    for n, p in enumerate([2450, 2500, 2550, 2600]):
        _peer(conn, f"PEER{n:06d}", f"MSI GeForce RTX 5090 32G Gaming Trio {n} Tarjeta gráfica", p, now - 3600)
    t = "ASUS ROG Astral GeForce RTX 5090 32GB GDDR7 Tarjeta gráfica"
    ev = evaluate(conn, _obs("TARGET0001", t, 500.0), identify(t), Settings())
    # listing-only data (no seller / condition): high, triggers verification, but cannot alert by itself
    assert 70 <= ev.score <= 85, ev.components


def test_offers_from_price_cannot_notify_without_product_page(conn):
    now = time.time()
    for n, p in enumerate([2450, 2500, 2550, 2600]):
        _peer(conn, f"PEER{n:06d}", f"MSI GeForce RTX 5090 32G Gaming Trio {n} Tarjeta gráfica", p, now - 3600)
    t = "ASUS ROG Astral GeForce RTX 5090 32GB GDDR7 Tarjeta gráfica"
    ev = evaluate(conn, _obs("TARGET0001", t, 500.0, offers_from=True), identify(t), Settings())
    assert ev.score <= 84


def test_accessory_is_rejected(conn):
    t = "Soporte de GPU para RTX 5090 anti-sag"
    ev = evaluate(conn, _obs("ACC0000001", t, 19.0), identify(t), Settings())
    assert ev.rejected and ev.score == 0


def test_normal_20pct_discount_is_discarded(conn):
    now = time.time()
    t = "MSI GeForce RTX 5080 16G Ventus Tarjeta gráfica"
    for k in range(5):
        conn.execute("INSERT INTO observations(asin,ts,price,source,geo) VALUES(?,?,?,?,?)", ("HIST000001", now - 86400 * (k + 1), 1200.0, "listing", "España"))
    ev = evaluate(conn, _obs("HIST000001", t, 960.0), identify(t), Settings())
    assert ev.reference.source == "history"
    assert ev.score < 60


def test_strike_through_price_is_not_a_reference(conn):
    t = "MSI GeForce RTX 5080 16G Ventus Tarjeta gráfica"
    # Amazon claims a crazy list price; we have no own data -> only the (capped) prior
    ev = evaluate(conn, _obs("NOREF00001", t, 990.0, list_price=4999.0), identify(t), Settings())
    assert ev.reference.source == "prior"
    assert ev.score < 60


def test_prior_only_is_capped(conn):
    t = "Sony PlayStation 5 Pro Consola"
    ev = evaluate(conn, _obs("PRIOR00001", t, 70.0, fulfillment="amazon", condition="new", availability="in_stock"), identify(t), Settings())
    assert ev.reference.source == "prior"
    assert ev.score <= 88
    assert ev.confidence == "BAJA"


def test_out_of_stock_is_rejected(conn):
    t = "ZOTAC GAMING GeForce RTX 5090 Solid Tarjeta gráfica"
    ev = evaluate(conn, _obs("OOS0000001", t, 400.0, availability="out_of_stock"), identify(t), Settings())
    assert ev.rejected
