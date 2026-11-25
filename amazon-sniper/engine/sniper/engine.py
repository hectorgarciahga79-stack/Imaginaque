"""Research engine: task queue, discovery, recording, evaluation, verification."""
from __future__ import annotations

import json
import re
import sqlite3
import time
from urllib.parse import quote_plus

from . import db
from .analysis import Evaluation, Observation, evaluate
from .catalog import COMBO_BRANDS, SEARCH_SEEDS, Identity, category_priority, identify
from .config import Settings
from .fetcher import FetchResult, Fetcher
from .notify import maybe_notify
from .parsers import Item, parse_listing, parse_product, parse_search

ROOT_STORES = [
    # (store, priority, name)
    ("computers", 2, "Informática"),
    ("videogames", 5, "Videojuegos"),
    ("electronics", 6, "Electrónica"),
]
# Known high-priority nodes (verified on amazon.es). More are discovered automatically.
KNOWN_NODES = [
    ("computers", "937935031", "Tarjetas gráficas", 1),
]
LIST_TYPES = ["bestsellers", "new-releases", "movers-and-shakers"]
VERIFY_FROM_SCORE = 75.0


class Engine:
    def __init__(self, conn: sqlite3.Connection, settings: Settings | None = None, fetcher: Fetcher | None = None):
        self.conn = conn
        self.s = settings or Settings.load(conn)
        self.fetcher = fetcher or Fetcher(conn, self.s)

    # ================================================================ seeding
    def seed(self) -> None:
        c = self.conn
        for store, prio, name in ROOT_STORES:
            self._add_category(store, "", name, None, 0, prio)
        for store, node, name, prio in KNOWN_NODES:
            self._add_category(store, node, name, "", 1, prio)
        for prio, q in SEARCH_SEEDS:
            self._add_search(q, prio)
        for b in COMBO_BRANDS["gpu"]:
            for m in COMBO_BRANDS["gpu_models"]:
                self._add_search(f"{b} {m}", 3)
        for b in COMBO_BRANDS["laptop"]:
            for m in COMBO_BRANDS["laptop_models"]:
                self._add_search(f"{b} {m}", 5)
        db.log_event(c, "info", "Semillas de investigación cargadas")

    def _add_category(self, store: str, node: str, name: str, parent: str | None, depth: int, prio: int) -> int:
        added = 0
        for lt in LIST_TYPES:
            r = self.conn.execute(
                "INSERT OR IGNORE INTO categories(node,list_type,store,name,parent,depth,priority,discovered_at) VALUES(?,?,?,?,?,?,?,?)",
                (node, lt, store, name, parent, depth, prio, db.now()),
            )
            added += r.rowcount
            pages = self.s.listing_pages if lt != "movers-and-shakers" else 1
            for pg in range(1, pages + 1):
                path = f"/gp/{lt}/{store}/{node}".rstrip("/") + "/"
                url = self.s.base_url + path + (f"?pg={pg}" if pg > 1 else "")
                # movers & new releases are visited a bit less often than bestsellers
                p = prio + (0 if lt == "bestsellers" else 1) + (pg - 1)
                self.conn.execute(
                    """INSERT OR IGNORE INTO tasks(kind,key,url,label,priority,interval_s,next_run_at)
                       VALUES('listing',?,?,?,?,?,0)""",
                    (f"listing:{lt}:{store}:{node or 'root'}:p{pg}", url, f"{name} · {lt} · p{pg}", p,
                     self._listing_interval(p)),
                )
        return added

    def _add_search(self, query: str, prio: int) -> None:
        key = "search:" + re.sub(r"\s+", " ", query.strip().lower())
        url = f"{self.s.base_url}/s?k={quote_plus(query)}"
        self.conn.execute(
            """INSERT OR IGNORE INTO tasks(kind,key,url,label,priority,interval_s,next_run_at)
               VALUES('search',?,?,?,?,?,0)""",
            (key, url, query, prio, self._search_interval(prio)),
        )

    def _listing_interval(self, prio: int) -> int:
        return int(self.s.listing_interval_min * 60 * (1 + (max(prio, 1) - 1) * 0.5))

    def _search_interval(self, prio: int) -> int:
        return int(self.s.search_cooldown_min * 60 * (1 + (max(prio, 1) - 1) * 0.25))

    # ================================================================ blocks
    def _source_of(self, task_kind: str, url: str) -> str:
        if task_kind == "listing":
            m = re.search(r"/gp/([a-z\-]+)/", url)
            return f"listing:{m.group(1) if m else 'other'}"
        return task_kind

    def blocks(self) -> dict:
        return db.state_get(self.conn, "blocks", {}) or {}

    def is_blocked(self, source: str) -> bool:
        b = self.blocks().get(source)
        return bool(b and b.get("until", 0) > time.time())

    def _register_fetch(self, source: str, res: FetchResult) -> None:
        blocks = self.blocks()
        if res.outcome == "blocked":
            b = blocks.get(source, {"level": 0, "since": time.time()})
            lvl = min(b.get("level", 0), len(self.s.block_backoff_min) - 1)
            b.update(level=b.get("level", 0) + 1, until=time.time() + self.s.block_backoff_min[lvl] * 60,
                     reason=res.detail, last=time.time(), url=res.url)
            blocks[source] = b
            db.log_event(self.conn, "warn", f"Amazon rechaza el acceso automatizado a '{source}' ({res.detail}). "
                         f"Pausa de {self.s.block_backoff_min[lvl]} min. No se intenta eludir.")
        elif res.outcome == "ok" and source in blocks:
            db.log_event(self.conn, "info", f"Acceso a '{source}' restablecido")
            blocks.pop(source, None)
        db.state_set(self.conn, "blocks", blocks)
        if res.outcome == "ok":
            db.state_incr(self.conn, "pages_ok")
        db.state_incr(self.conn, "pages_total")

    # ================================================================ task loop
    def next_task(self) -> sqlite3.Row | None:
        # scan the whole due queue: the first N may all belong to a source Amazon is currently refusing
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE enabled=1 AND next_run_at <= ? ORDER BY priority ASC, next_run_at ASC",
            (time.time(),),
        ).fetchall()
        for t in rows:
            if t["kind"] == "search" and not self.s.enable_search:
                continue
            if t["kind"] == "product" and not self.s.enable_product_pages:
                continue
            if self.is_blocked(self._source_of(t["kind"], t["url"])):
                continue
            return t
        return None

    def run_task(self, t: sqlite3.Row) -> None:
        db.state_set(self.conn, "current_task", {"label": t["label"], "kind": t["kind"], "started": time.time()})
        source = self._source_of(t["kind"], t["url"])
        res = self.fetcher.get(t["url"], t["kind"])
        if res.outcome == "rate_limited":
            self.conn.execute("UPDATE tasks SET next_run_at=? WHERE id=?", (time.time() + 120, t["id"]))
            return
        self._register_fetch(source, res)
        n_items = n_new = 0
        status = res.outcome if res.outcome != "ok" else "ok"
        if res.outcome == "ok":
            try:
                if t["kind"] == "listing":
                    n_items, n_new = self._handle_listing(t, res)
                elif t["kind"] == "search":
                    n_items, n_new = self._handle_search(t, res)
                elif t["kind"] == "product":
                    n_items, n_new = self._handle_product_task(t, res)
                if n_items == 0:
                    status = "ok_empty"
            except Exception as e:  # parser failure must never kill the loop
                status = "parse_error"
                db.log_event(self.conn, "error", f"Error procesando {t['url']}: {type(e).__name__}: {e}")
        interval = t["interval_s"]
        if t["kind"] == "search":
            # adaptive: productive queries come back sooner, sterile ones later
            factor = 1.0 if n_new > 0 else min(8.0, 1.5 ** max(1, t["runs"] % 6))
            interval = int(self._search_interval(t["priority"]) * factor)
        if status not in ("ok", "ok_empty"):
            interval = max(interval, 900)
        self.conn.execute(
            """UPDATE tasks SET last_run_at=?, last_status=?, runs=runs+1, items_last=?, new_items_last=?,
               new_items_total=new_items_total+?, next_run_at=?, interval_s=? WHERE id=?""",
            (time.time(), f"{status}:{res.detail}" if res.detail else status, n_items, n_new, n_new,
             time.time() + interval, interval, t["id"]),
        )
        db.state_set(self.conn, "last_research", {"ts": time.time(), "label": t["label"], "status": status, "items": n_items, "new": n_new})
        if t["kind"] == "product" and t["key"].startswith("product:once:"):
            self.conn.execute("DELETE FROM tasks WHERE id=?", (t["id"],))

    # ================================================================ handlers
    def _handle_listing(self, t, res: FetchResult) -> tuple[int, int]:
        parsed = parse_listing(res.html, self.s.base_url)
        m = re.search(r"listing:([a-z\-]+):([a-z\-]+):([^:]+):p(\d+)", t["key"])
        lt, store, node = m.group(1), m.group(2), m.group(3)
        node = "" if node == "root" else node
        cat_name = parsed["category_name"] or t["label"]
        geo = parsed.get("geo")
        if geo:
            db.state_set(self.conn, "delivery_location", geo)
        # autonomous category discovery
        crow = self.conn.execute("SELECT depth, priority FROM categories WHERE store=? AND node=? LIMIT 1", (store, node)).fetchone()
        depth = crow["depth"] if crow else 0
        if depth < self.s.max_category_depth and m.group(4) == "1":
            for sc in parsed["subcategories"]:
                if sc["store"] != store or sc["node"] == node:
                    continue
                prio = category_priority(sc["name"])
                if prio is None:
                    continue
                if self._add_category(store, sc["node"], sc["name"], node, depth + 1, prio):
                    db.log_event(self.conn, "info", f"Categoría descubierta: {sc['name']} ({store}/{sc['node']}) prioridad {prio}")
        return self._ingest(parsed["items"], "listing", cat_name, node, geo, t["url"])

    def _handle_search(self, t, res: FetchResult) -> tuple[int, int]:
        parsed = parse_search(res.html, self.s.base_url)
        return self._ingest(parsed["items"], "search", t["label"], None, parsed.get("geo"), t["url"])

    def _handle_product_task(self, t, res: FetchResult) -> tuple[int, int]:
        asin = t["key"].split(":")[-1]
        it = parse_product(res.html, self.s.base_url, asin)
        if not it:
            return 0, 0
        return self._ingest([it], "product", None, None, it.extra.get("geo"), t["url"])

    # ================================================================ recording
    def _ingest(self, items: list[Item], source: str, category: str | None, node: str | None,
                geo: str | None, source_url: str) -> tuple[int, int]:
        n_new = 0
        evals: list[tuple[Item, Identity, Evaluation, Observation]] = []
        self.conn.execute("BEGIN")
        try:
            for it in items:
                idn = identify(it.title, category)
                is_new = self._upsert_product(it, idn, category, node)
                n_new += int(is_new)
                if it.price is None:
                    continue
                obs = Observation(asin=it.asin, price=it.price, title=it.title, source=source, geo=geo,
                                  offers_from=it.offers_from, seller=it.seller, fulfillment=it.fulfillment,
                                  condition=it.condition, availability=it.availability, shipping=it.shipping,
                                  list_price=it.list_price)
                # evaluate BEFORE inserting so the observation does not pollute its own reference
                ev = evaluate(self.conn, obs, idn, self.s, verified_product_page=(source == "product"))
                self._insert_observation(it, obs, source, source_url)
                evals.append((it, idn, ev, obs))
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        for it, idn, ev, obs in evals:
            if ev.rejected or ev.score < self.s.store_threshold:
                continue
            opp_id = self._save_opportunity(it, idn, ev, obs, source_url)
            strong = ev.discount is not None and ev.discount >= 0.5 and idn.model_key and ev.reference.source in ("history", "peers")
            if (ev.score >= VERIFY_FROM_SCORE or strong) and source != "product":
                self.verify(opp_id)
            elif source == "product":
                opp = self.conn.execute("SELECT * FROM opportunities WHERE id=?", (opp_id,)).fetchone()
                self._verify_with_product(opp, it)
        return len(items), n_new

    def _upsert_product(self, it: Item, idn: Identity, category: str | None, node: str | None) -> bool:
        row = self.conn.execute("SELECT asin FROM products WHERE asin=?", (it.asin,)).fetchone()
        now = db.now()
        is_acc = int("accesorio" in idn.flags or "videojuego_no_consola" in idn.flags)
        if row:
            self.conn.execute(
                """UPDATE products SET title=COALESCE(NULLIF(?,''),title), family=?, model_key=?, model_label=?,
                   category=COALESCE(?,category), category_node=COALESCE(?,category_node), image=COALESCE(NULLIF(?,''),image),
                   is_accessory=?, last_seen=?, last_price=COALESCE(?,last_price), times_seen=times_seen+1 WHERE asin=?""",
                (it.title, idn.family, idn.model_key, idn.label, category, node, it.image, is_acc, now, it.price, it.asin),
            )
            return False
        self.conn.execute(
            """INSERT INTO products(asin,title,family,model_key,model_label,category,category_node,url,image,is_accessory,
               first_seen,last_seen,last_price,times_seen) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
            (it.asin, it.title, idn.family, idn.model_key, idn.label, category, node, it.url, it.image, is_acc, now, now, it.price),
        )
        return True

    def _insert_observation(self, it: Item, obs: Observation, source: str, source_url: str) -> None:
        last = self.conn.execute(
            "SELECT price, ts FROM observations WHERE asin=? ORDER BY id DESC LIMIT 1", (it.asin,)
        ).fetchone()
        # avoid storing the same price twice within 10 minutes (e.g. same item in two lists)
        if last and last["price"] == obs.price and obs.ts - last["ts"] < 600:
            return
        self.conn.execute(
            """INSERT INTO observations(asin,ts,price,list_price,shipping,seller,ships_from,fulfillment,condition,availability,
               offers_from,offers_count,variant,source,source_url,rank,geo) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (it.asin, obs.ts, obs.price, it.list_price, it.shipping, it.seller, it.ships_from, it.fulfillment, it.condition,
             it.availability, int(it.offers_from), it.offers_count, it.variant, source, source_url, it.rank, obs.geo),
        )

    def _save_opportunity(self, it: Item, idn: Identity, ev: Evaluation, obs: Observation, source_url: str) -> int:
        active = self.conn.execute(
            "SELECT * FROM opportunities WHERE asin=? AND status IN ('candidate','verified','partial') ORDER BY id DESC LIMIT 1",
            (it.asin,),
        ).fetchone()
        payload = dict(
            price=obs.price, reference_price=ev.reference.price, reference_source=ev.reference.source,
            discount=ev.discount, saving=ev.saving, score=ev.score, tier=ev.tier, confidence=ev.confidence,
            components=json.dumps({"weights_applied": ev.components, "reference": ev.reference.__dict__,
                                   "model": idn.label, "family": idn.family}, ensure_ascii=False),
            flags=json.dumps(ev.warnings, ensure_ascii=False), source_url=source_url, seller=obs.seller,
            fulfillment=obs.fulfillment, condition=obs.condition, availability=obs.availability,
        )
        now = db.now()
        if active and active["price"] and abs(active["price"] - obs.price) / active["price"] < 0.01:
            # keep the best (verified) score; refresh the rest
            if obs.source != "product" and active["status"] == "verified":
                payload["score"] = max(active["score"], ev.score)
                payload["tier"] = active["tier"] if active["score"] >= ev.score else ev.tier
            sets = ", ".join(f"{k}=?" for k in payload)
            self.conn.execute(f"UPDATE opportunities SET {sets}, updated_at=? WHERE id=?", (*payload.values(), now, active["id"]))
            return active["id"]
        if active:
            self.conn.execute("UPDATE opportunities SET status='expired', updated_at=? WHERE id=?", (now, active["id"]))
        cols = ", ".join(payload)
        cur = self.conn.execute(
            f"INSERT INTO opportunities(asin,created_at,updated_at,status,{cols}) VALUES(?,?,?,'candidate',{', '.join('?' * len(payload))})",
            (it.asin, now, now, *payload.values()),
        )
        db.state_incr(self.conn, "anomalies_found")
        db.log_event(self.conn, "info", f"Anomalía {ev.score:.0f} pts: {it.title[:90]} a {obs.price} € (ref {ev.reference.price} € · {ev.reference.source})")
        return cur.lastrowid

    # ================================================================ verification
    def verify(self, opp_id: int) -> str:
        """Immediate re-check. Product page first; if Amazon refuses it, re-read the
        page where the anomaly was found (partial verification)."""
        opp = self.conn.execute("SELECT * FROM opportunities WHERE id=?", (opp_id,)).fetchone()
        if not opp:
            return "missing"
        asin = opp["asin"]
        if self.s.enable_product_pages and not self.is_blocked("product"):
            res = self.fetcher.get(f"{self.s.base_url}/dp/{asin}", "product")
            self._register_fetch("product", res)
            if res.outcome == "ok":
                it = parse_product(res.html, self.s.base_url, asin)
                if it is None:
                    return self._finish_verification(opp_id, False, "product_page", None, {"reason": "ficha no reconocida"})
                return self._verify_with_product(opp, it)
        # fallback: re-read the listing / search page that produced the anomaly
        src = opp["source_url"]
        if src:
            kind = "search" if "/s?" in src else "listing"
            source = self._source_of(kind, src)
            if not self.is_blocked(source):
                res = self.fetcher.get(src, kind)
                self._register_fetch(source, res)
                if res.outcome == "ok":
                    items = (parse_search(res.html, self.s.base_url) if kind == "search" else parse_listing(res.html, self.s.base_url))["items"]
                    match = next((i for i in items if i.asin == asin), None)
                    if match is None:
                        return self._finish_verification(opp_id, False, "listing_recheck", None, {"reason": "el producto ya no aparece"})
                    same = match.price is not None and abs(match.price - opp["price"]) / opp["price"] <= 0.02
                    return self._finish_verification(opp_id, same, "listing_recheck", match.price,
                                                     {"reason": "precio confirmado en el listado" if same else "el precio ha cambiado",
                                                      "partial": True})
        return self._finish_verification(opp_id, None, "unavailable", None, {"reason": "ninguna página disponible para verificar"})

    def _verify_with_product(self, opp, it: Item) -> str:
        idn = identify(it.title)
        problems = []
        if it.price is None:
            problems.append("sin precio visible (sin oferta destacada)")
        elif abs(it.price - opp["price"]) / opp["price"] > 0.02:
            problems.append(f"precio actual {it.price} € distinto de {opp['price']} €")
        if it.availability == "out_of_stock":
            problems.append("sin stock")
        if it.condition in ("used", "refurbished"):
            problems.append(f"condición {it.condition}")
        if not it.seller:
            problems.append("vendedor no identificable")
        prod = self.conn.execute("SELECT model_key FROM products WHERE asin=?", (opp["asin"],)).fetchone()
        if prod and prod["model_key"] and idn.model_key and idn.model_key != prod["model_key"]:
            problems.append(f"modelo de la ficha ({idn.label}) no coincide")
        if idn.flags:
            problems.append("ficha marcada: " + ",".join(idn.flags))
        detail = {"seller": it.seller, "fulfillment": it.fulfillment, "condition": it.condition,
                  "availability": it.availability, "variant": it.variant, "shipping": it.shipping,
                  "url": it.url, "problems": problems}
        ok = not problems
        if it.price is not None:
            # store the product-page observation and re-score with verified data
            self._ingest_verified(it, opp)
        return self._finish_verification(opp["id"], ok, "product_page", it.price, detail)

    def _ingest_verified(self, it: Item, opp) -> None:
        idn = identify(it.title)
        obs = Observation(asin=it.asin, price=it.price, title=it.title, source="product", geo=it.extra.get("geo"),
                          offers_from=False, seller=it.seller, fulfillment=it.fulfillment, condition=it.condition,
                          availability=it.availability, shipping=it.shipping, list_price=it.list_price)
        ev = evaluate(self.conn, obs, idn, self.s, verified_product_page=True)
        self._insert_observation(it, obs, "product", it.url)
        if abs(it.price - opp["price"]) / opp["price"] <= 0.02:
            self.conn.execute(
                """UPDATE opportunities SET score=?, tier=?, confidence=?, seller=?, fulfillment=?, condition=?, availability=?,
                   flags=?, components=?, reference_price=?, reference_source=?, discount=?, saving=?, updated_at=? WHERE id=?""",
                (0.0 if ev.rejected else ev.score, ev.tier, ev.confidence, it.seller, it.fulfillment, it.condition,
                 it.availability, json.dumps(ev.warnings + ev.flags, ensure_ascii=False),
                 json.dumps({"weights_applied": ev.components, "reference": ev.reference.__dict__, "model": idn.label,
                             "family": idn.family, "verified_on": "product_page"}, ensure_ascii=False),
                 ev.reference.price, ev.reference.source, ev.discount, ev.saving, db.now(), opp["id"]),
            )

    def _finish_verification(self, opp_id: int, ok: bool | None, method: str, price: float | None, detail: dict) -> str:
        now = db.now()
        self.conn.execute(
            "INSERT INTO verifications(opportunity_id,ts,method,price,ok,detail) VALUES(?,?,?,?,?,?)",
            (opp_id, now, method, price, None if ok is None else int(ok), json.dumps(detail, ensure_ascii=False)),
        )
        if ok is None:
            status = "candidate"
        elif not ok:
            status = "expired"
        else:
            status = "partial" if (method == "listing_recheck" or detail.get("partial")) else "verified"
        self.conn.execute(
            "UPDATE opportunities SET status=?, verified_at=?, verification=?, updated_at=? WHERE id=?",
            (status, now, json.dumps({"method": method, "ok": ok, **detail}, ensure_ascii=False), now, opp_id),
        )
        if status == "verified":
            db.state_incr(self.conn, "verified_total")
        if status in ("verified", "partial"):
            maybe_notify(self.conn, self.s, opp_id)
        return status

    def reverify_due(self) -> int:
        """Keep live opportunities honest: re-check and expire when gone."""
        due = self.conn.execute(
            """SELECT id FROM opportunities WHERE status IN ('verified','partial','candidate') AND score >= ?
               AND COALESCE(verified_at, created_at) < ? ORDER BY score DESC LIMIT 3""",
            (VERIFY_FROM_SCORE, time.time() - self.s.reverify_interval_min * 60),
        ).fetchall()
        for r in due:
            self.verify(r["id"])
        # candidates that could never be verified fade out after 24 h
        self.conn.execute(
            "UPDATE opportunities SET status='expired' WHERE status='candidate' AND created_at < ?", (time.time() - 86400,)
        )
        return len(due)

    def reidentify(self) -> int:
        """Re-run product identification over the whole catalogue (after rule updates)."""
        n = 0
        for r in self.conn.execute("SELECT asin, title, category FROM products").fetchall():
            idn = identify(r["title"] or "", r["category"])
            is_acc = int("accesorio" in idn.flags or "videojuego_no_consola" in idn.flags)
            self.conn.execute("UPDATE products SET family=?, model_key=?, model_label=?, is_accessory=? WHERE asin=?",
                              (idn.family, idn.model_key, idn.label, is_acc, r["asin"]))
            n += 1
        return n

    # ================================================================ query generation
    def generate_queries(self) -> int:
        """New query combinations from models the engine has discovered itself."""
        rows = self.conn.execute(
            """SELECT model_label, family, COUNT(*) n FROM products
               WHERE model_label IS NOT NULL AND is_accessory=0 AND family IN ('gpu','cpu','console','laptop','desktop','apple','phone','ssd','monitor','tv')
               GROUP BY model_label ORDER BY n DESC LIMIT 200"""
        ).fetchall()
        fam_prio = {"gpu": 1, "cpu": 2, "desktop": 3, "laptop": 4, "console": 5, "ssd": 8, "monitor": 10, "tv": 11, "apple": 12, "phone": 13}
        before = self.conn.execute("SELECT COUNT(*) FROM tasks WHERE kind='search'").fetchone()[0]
        for r in rows:
            label = r["model_label"]
            q = label if r["family"] not in ("laptop", "desktop") else label.replace("Portátil", "portátil gaming").replace("PC ", "PC gaming ")
            self._add_search(q, fam_prio.get(r["family"], 14))
        after = self.conn.execute("SELECT COUNT(*) FROM tasks WHERE kind='search'").fetchone()[0]
        if after > before:
            db.log_event(self.conn, "info", f"{after - before} búsquedas nuevas generadas a partir de modelos descubiertos")
        return after - before
