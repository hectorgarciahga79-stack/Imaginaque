"""Local notifications only: an `alerts` row (the web UI turns it into a browser
notification) plus an OS desktop notification when available. No external services."""
from __future__ import annotations

import json
import platform
import shutil
import sqlite3
import subprocess

from . import db
from .config import Settings


def eligible(opp: sqlite3.Row, s: Settings) -> tuple[bool, str]:
    if opp["notified"]:
        return False, "ya notificada"
    if opp["score"] is None or opp["score"] <= s.notify_threshold:
        return False, f"score {opp['score']} <= {s.notify_threshold}"
    if opp["status"] == "verified":
        return True, "verificada en ficha de producto"
    if opp["status"] == "partial":
        if s.allow_partial_verification_alerts and opp["score"] >= s.partial_min_score:
            return True, "verificación parcial (listado) con score extremo"
        return False, "verificación sólo parcial"
    return False, f"estado {opp['status']}"


def maybe_notify(conn: sqlite3.Connection, s: Settings, opp_id: int) -> bool:
    opp = conn.execute(
        """SELECT o.*, p.title, p.model_label FROM opportunities o LEFT JOIN products p ON p.asin=o.asin WHERE o.id=?""",
        (opp_id,),
    ).fetchone()
    if not opp:
        return False
    ok, why = eligible(opp, s)
    if not ok:
        return False
    disc = f"-{opp['discount'] * 100:.0f}%" if opp["discount"] is not None else ""
    title = f"SNIPER {opp['score']:.0f} · {opp['model_label'] or 'Producto'} a {opp['price']:.2f} € {disc}"
    body = (f"{(opp['title'] or '')[:120]}\nHabitual ~{opp['reference_price']:.0f} € ({opp['reference_source']}) · "
            f"Confianza {opp['confidence']} · {why}")
    url = f"{s.base_url}/dp/{opp['asin']}"
    conn.execute(
        "INSERT INTO alerts(opportunity_id,ts,title,body,score,url) VALUES(?,?,?,?,?,?)",
        (opp_id, db.now(), title, body, opp["score"], url),
    )
    conn.execute("UPDATE opportunities SET notified=1 WHERE id=?", (opp_id,))
    db.state_incr(conn, "alerts_total")
    db.log_event(conn, "alert", f"{title} — {url}")
    if s.desktop_notifications:
        desktop_notify(title, body + "\n" + url)
    return True


def desktop_notify(title: str, body: str) -> None:
    try:
        system = platform.system()
        if system == "Linux" and shutil.which("notify-send"):
            subprocess.run(["notify-send", "-u", "critical", "-a", "Amazon Sniper", title, body], timeout=10, check=False)
        elif system == "Darwin":
            script = f'display notification {json.dumps(body[:200])} with title {json.dumps(title[:100])} sound name "Glass"'
            subprocess.run(["osascript", "-e", script], timeout=10, check=False)
        elif system == "Windows":
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$n=New-Object System.Windows.Forms.NotifyIcon;$n.Icon=[System.Drawing.SystemIcons]::Information;"
                f"$n.BalloonTipTitle={json.dumps(title[:60])};$n.BalloonTipText={json.dumps(body[:200])};"
                "$n.Visible=$true;$n.ShowBalloonTip(15000);Start-Sleep -s 16;$n.Dispose()"
            )
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps])
    except Exception:
        pass  # desktop notification is best-effort; the alert row is the source of truth
