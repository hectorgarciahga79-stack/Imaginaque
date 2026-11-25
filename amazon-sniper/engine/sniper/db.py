"""SQLite storage: the engine's own memory (products, price history, opportunities...)."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]  # amazon-sniper/
DEFAULT_DB = ROOT / "data" / "sniper.db"

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS products (
    asin            TEXT PRIMARY KEY,
    title           TEXT,
    brand           TEXT,
    family          TEXT,          -- gpu, cpu, console, laptop, desktop, ssd, ram, monitor, tv, apple, phone, motherboard, other
    model_key       TEXT,          -- canonical model, e.g. gpu:rtx-5090
    model_label     TEXT,          -- human label, e.g. RTX 5090
    category        TEXT,          -- Amazon category name where it was found
    category_node   TEXT,
    url             TEXT,
    image           TEXT,
    is_accessory    INTEGER DEFAULT 0,
    first_seen      REAL,
    last_seen       REAL,
    last_price      REAL,
    times_seen      INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_products_model ON products(model_key);
CREATE INDEX IF NOT EXISTS idx_products_last_seen ON products(last_seen);

CREATE TABLE IF NOT EXISTS observations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    asin            TEXT NOT NULL,
    ts              REAL NOT NULL,
    price           REAL,          -- price we observed (EUR)
    list_price      REAL,          -- Amazon strike-through / recommended price, informative only
    shipping        REAL,          -- shipping cost if known
    seller          TEXT,
    ships_from      TEXT,
    fulfillment     TEXT,          -- amazon | fba | third_party | unknown
    condition       TEXT,          -- new | used | refurbished | unknown
    availability    TEXT,          -- in_stock | out_of_stock | limited | unknown
    offers_from     INTEGER DEFAULT 0, -- 1 when price is "N ofertas desde X" (lowest of several offers, may be used)
    offers_count    INTEGER,
    variant         TEXT,
    source          TEXT,          -- listing | search | product
    source_url      TEXT,
    rank            INTEGER,
    geo             TEXT           -- delivery location shown by Amazon (prices differ: VAT)
);
CREATE INDEX IF NOT EXISTS idx_obs_asin_ts ON observations(asin, ts);
CREATE INDEX IF NOT EXISTS idx_obs_ts ON observations(ts);

CREATE TABLE IF NOT EXISTS opportunities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    asin            TEXT NOT NULL,
    created_at      REAL NOT NULL,
    updated_at      REAL NOT NULL,
    price           REAL,
    reference_price REAL,
    reference_source TEXT,         -- history | peers | prior
    discount        REAL,          -- 0..1 versus reference
    saving          REAL,
    score           REAL,
    tier            TEXT,          -- discard | interesting | exceptional | extreme
    confidence      TEXT,          -- ALTA | MEDIA | BAJA
    components      TEXT,          -- JSON breakdown
    flags           TEXT,          -- JSON list of warnings
    status          TEXT,          -- candidate | verified | partial | expired | rejected
    verified_at     REAL,
    verification    TEXT,          -- JSON last verification detail
    notified        INTEGER DEFAULT 0,
    source_url      TEXT,
    seller          TEXT,
    fulfillment     TEXT,
    condition       TEXT,
    availability    TEXT
);
CREATE INDEX IF NOT EXISTS idx_opp_asin ON opportunities(asin);
CREATE INDEX IF NOT EXISTS idx_opp_score ON opportunities(score);

CREATE TABLE IF NOT EXISTS verifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id  INTEGER NOT NULL,
    ts              REAL NOT NULL,
    method          TEXT,          -- product_page | listing_recheck
    price           REAL,
    ok              INTEGER,
    detail          TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id  INTEGER,
    ts              REAL NOT NULL,
    title           TEXT,
    body            TEXT,
    score           REAL,
    url             TEXT,
    seen            INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    kind            TEXT NOT NULL,  -- listing | search | product | discover
    key             TEXT NOT NULL UNIQUE,
    url             TEXT NOT NULL,
    label           TEXT,
    priority        INTEGER DEFAULT 5,   -- 1 = highest
    interval_s      INTEGER DEFAULT 3600,
    next_run_at     REAL DEFAULT 0,
    last_run_at     REAL,
    last_status     TEXT,
    runs            INTEGER DEFAULT 0,
    items_last      INTEGER DEFAULT 0,
    new_items_last  INTEGER DEFAULT 0,
    new_items_total INTEGER DEFAULT 0,
    enabled         INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(enabled, next_run_at);

CREATE TABLE IF NOT EXISTS categories (
    node            TEXT NOT NULL,
    list_type       TEXT NOT NULL,  -- bestsellers | new-releases | movers-and-shakers
    store           TEXT NOT NULL,  -- computers | electronics | videogames ...
    name            TEXT,
    parent          TEXT,
    depth           INTEGER,
    priority        INTEGER,
    discovered_at   REAL,
    PRIMARY KEY (store, node, list_type)
);

CREATE TABLE IF NOT EXISTS fetch_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              REAL NOT NULL,
    kind            TEXT,
    url             TEXT,
    status          INTEGER,
    outcome         TEXT,          -- ok | blocked | error | robots_disallowed
    bytes           INTEGER,
    ms              INTEGER,
    detail          TEXT
);
CREATE INDEX IF NOT EXISTS idx_fetch_ts ON fetch_log(ts);

CREATE TABLE IF NOT EXISTS engine_state (
    key             TEXT PRIMARY KEY,
    value           TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key             TEXT PRIMARY KEY,
    value           TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              REAL NOT NULL,
    level           TEXT,
    message         TEXT
);
"""


def db_path() -> Path:
    p = os.environ.get("SNIPER_DB")
    return Path(p) if p else DEFAULT_DB


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(path) if path else db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    conn.executescript(SCHEMA)
    return conn


# ---------- small helpers ----------

def now() -> float:
    return time.time()


def state_get(conn: sqlite3.Connection, key: str, default: Any = None) -> Any:
    row = conn.execute("SELECT value FROM engine_state WHERE key=?", (key,)).fetchone()
    if not row:
        return default
    try:
        return json.loads(row["value"])
    except (TypeError, ValueError):
        return row["value"]


def state_set(conn: sqlite3.Connection, key: str, value: Any) -> None:
    conn.execute(
        "INSERT INTO engine_state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(value, ensure_ascii=False)),
    )


def state_incr(conn: sqlite3.Connection, key: str, by: int = 1) -> int:
    v = int(state_get(conn, key, 0) or 0) + by
    state_set(conn, key, v)
    return v


def log_event(conn: sqlite3.Connection, level: str, message: str) -> None:
    conn.execute("INSERT INTO events(ts,level,message) VALUES(?,?,?)", (now(), level, message[:2000]))


def trim(conn: sqlite3.Connection) -> None:
    """Keep auxiliary logs bounded (resource control)."""
    conn.execute("DELETE FROM events WHERE id < (SELECT COALESCE(MAX(id),0) - 5000 FROM events)")
    conn.execute("DELETE FROM fetch_log WHERE id < (SELECT COALESCE(MAX(id),0) - 20000 FROM fetch_log)")


def rows(cur: Iterable[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in cur]
