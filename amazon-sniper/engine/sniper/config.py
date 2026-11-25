"""Engine configuration. Defaults here; overrides live in the `settings` table
(editable from the web UI) and are re-read by the daemon every cycle."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field, fields


@dataclass
class Settings:
    # --- access / politeness ---
    base_url: str = "https://www.amazon.es"
    fetch_backend: str = "http"          # http | playwright
    min_delay_s: float = 15.0            # minimum seconds between requests
    jitter_s: float = 10.0               # random extra delay
    max_requests_per_hour: int = 120
    request_timeout_s: float = 30.0
    respect_robots: bool = True
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    accept_language: str = "es-ES,es;q=0.9"
    # backoff when Amazon refuses automated access for a kind of page (minutes)
    block_backoff_min: list = field(default_factory=lambda: [20, 60, 180, 360, 720])

    # --- research loop ---
    paused: bool = False
    listing_interval_min: int = 30       # base re-visit interval for priority-1 listings
    search_cooldown_min: int = 180       # do not repeat a query sooner than this
    discover_interval_h: int = 24        # category tree re-discovery
    listing_pages: int = 2               # pages per bestseller list (30 items each)
    max_category_depth: int = 3
    enable_search: bool = True
    enable_product_pages: bool = True
    reverify_interval_min: int = 15      # re-check live opportunities

    # --- scoring / alerting ---
    notify_threshold: float = 85.0       # notify only when score > this
    store_threshold: float = 60.0        # keep opportunities from this score
    min_history_obs: int = 3             # observations needed for "own history" reference
    min_history_span_h: float = 24.0
    min_peers: int = 3                   # equivalent products needed for peer reference
    allow_partial_verification_alerts: bool = True  # alert when only listing re-check was possible
    partial_min_score: float = 90.0      # ...but only if the score is at least this
    desktop_notifications: bool = True

    @classmethod
    def load(cls, conn: sqlite3.Connection | None = None) -> "Settings":
        s = cls()
        if conn is None:
            return s
        names = {f.name: f for f in fields(cls)}
        for row in conn.execute("SELECT key, value FROM settings"):
            k = row["key"]
            if k not in names:
                continue
            try:
                setattr(s, k, json.loads(row["value"]))
            except (TypeError, ValueError):
                pass
        # Hard floor requested by the owner: never notify below 85.
        s.notify_threshold = max(85.0, float(s.notify_threshold))
        s.min_delay_s = max(3.0, float(s.min_delay_s))
        return s

    def to_dict(self) -> dict:
        return asdict(self)


def save_defaults(conn: sqlite3.Connection) -> None:
    """Insert defaults for keys not yet present so the UI can show/edit them."""
    for k, v in Settings().to_dict().items():
        conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, json.dumps(v)))
