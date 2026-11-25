"""AMAZON SNIPER command line.

  python -m sniper run          # continuous engine (foreground)
  python -m sniper supervise    # engine + automatic restart (use this for services)
  python -m sniper once -n 5    # run 5 research tasks and exit
  python -m sniper doctor       # real access test against amazon.es (no fake data)
  python -m sniper status       # summary of the database / engine state
  python -m sniper reset-blocks # forget backoff state (e.g. after moving to another network)
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from . import db
from .config import Settings, save_defaults


def cmd_doctor() -> int:
    from .fetcher import Fetcher
    from .parsers import parse_listing, parse_product, parse_search

    conn = db.connect()
    save_defaults(conn)
    s = Settings.load(conn)
    s.min_delay_s, s.jitter_s = 4.0, 2.0
    f = Fetcher(conn, s)
    checks = [
        ("listing", s.base_url + "/gp/bestsellers/computers/937935031/", lambda h: len(parse_listing(h, s.base_url)["items"])),
        ("search", s.base_url + "/s?k=RTX+5090", lambda h: len(parse_search(h, s.base_url)["items"])),
        ("product", None, None),
    ]
    asin = None
    ok_all = True
    print("AMAZON SNIPER · diagnóstico de acceso real a", s.base_url)
    for kind, url, count in checks:
        if kind == "product":
            if not asin:
                print("  product : omitido (sin ASIN de prueba)")
                continue
            url = f"{s.base_url}/dp/{asin}"
        res = f.get(url, kind)
        n = None
        if res.outcome == "ok":
            if kind == "product":
                it = parse_product(res.html, s.base_url, asin)
                n = 1 if it else 0
                extra = f"precio={it.price} vendedor={it.seller} stock={it.availability} condición={it.condition}" if it else "ficha no reconocida"
            else:
                n = count(res.html)
                extra = f"{n} productos"
                if kind == "listing" and n:
                    asin = parse_listing(res.html, s.base_url)["items"][0].asin
                if kind == "search" and n:
                    asin = parse_search(res.html, s.base_url)["items"][0].asin
        else:
            extra = res.detail
        good = res.outcome == "ok" and bool(n)
        ok_all &= good
        print(f"  {kind:8}: {'OK ' if good else 'NO '} HTTP {res.status} · {res.outcome} · {extra} · {url}")
    print("\nSi 'search' o 'product' aparecen como bloqueados, el motor sigue funcionando con los listados\n"
          "(más vendidos / novedades) y vuelve a intentar esas páginas con pausas crecientes. Nunca se eluden.")
    return 0 if ok_all else 1


def cmd_status() -> int:
    conn = db.connect()
    q = lambda sql: conn.execute(sql).fetchone()[0]  # noqa: E731
    info = {
        "status": db.state_get(conn, "status"),
        "heartbeat_age_s": round(time.time() - (db.state_get(conn, "heartbeat") or 0)),
        "products": q("SELECT COUNT(*) FROM products"),
        "observations": q("SELECT COUNT(*) FROM observations"),
        "opportunities": q("SELECT COUNT(*) FROM opportunities"),
        "verified": q("SELECT COUNT(*) FROM opportunities WHERE status='verified'"),
        "alerts": q("SELECT COUNT(*) FROM alerts"),
        "tasks": q("SELECT COUNT(*) FROM tasks"),
        "categories": q("SELECT COUNT(DISTINCT node) FROM categories"),
        "blocks": db.state_get(conn, "blocks"),
        "delivery_location": db.state_get(conn, "delivery_location"),
        "last_research": db.state_get(conn, "last_research"),
    }
    print(json.dumps(info, indent=2, ensure_ascii=False))
    top = conn.execute(
        """SELECT o.score,o.status,o.price,o.reference_price,o.reference_source,p.title FROM opportunities o
           JOIN products p USING(asin) ORDER BY o.score DESC LIMIT 10"""
    ).fetchall()
    for r in top:
        print(f"  {r['score']:5.1f} {r['status']:9} {r['price']:9.2f} € ref {r['reference_price'] or 0:9.2f} ({r['reference_source']}) {r['title'][:70]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sniper", description="AMAZON SNIPER engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--quiet", action="store_true")
    sub.add_parser("supervise")
    o = sub.add_parser("once")
    o.add_argument("-n", type=int, default=5)
    sub.add_parser("doctor")
    sub.add_parser("status")
    sub.add_parser("seed")
    sub.add_parser("reset-blocks")
    a = ap.parse_args(argv)

    from . import daemon
    if a.cmd == "run":
        return daemon.run(quiet=a.quiet)
    if a.cmd == "supervise":
        return daemon.supervise()
    if a.cmd == "once":
        return daemon.run(max_tasks=a.n)
    if a.cmd == "doctor":
        return cmd_doctor()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "seed":
        from .engine import Engine
        conn = db.connect()
        save_defaults(conn)
        Engine(conn).seed()
        print("ok")
        return 0
    if a.cmd == "reset-blocks":
        conn = db.connect()
        db.state_set(conn, "blocks", {})
        print("ok")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
