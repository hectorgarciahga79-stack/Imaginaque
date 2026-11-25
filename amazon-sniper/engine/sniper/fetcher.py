"""Polite page fetcher.

* one request at a time, minimum delay + jitter, hourly cap
* honours robots.txt for the generic user-agent
* detects Amazon's refusal pages (503 "Lo sentimos", "seguir comprando"
  interstitial, CAPTCHA, AWS WAF challenge) and reports them as BLOCKED.
  It never tries to solve, click through or disguise itself around them:
  the caller backs off that kind of page instead.
"""
from __future__ import annotations

import random
import re
import sqlite3
import time
import urllib.robotparser
from dataclasses import dataclass

import requests

from . import db
from .config import Settings


@dataclass
class FetchResult:
    url: str
    status: int
    html: str
    outcome: str        # ok | blocked | error | robots_disallowed | rate_limited
    detail: str = ""
    ms: int = 0


BLOCK_PATTERNS = [
    (re.compile(r"api-services-support@amazon\.com", re.I), "amazon_automated_access_notice"),
    (re.compile(r"Introduce los caracteres que ves|Type the characters you see|/errors/validateCaptcha", re.I), "captcha"),
    (re.compile(r"AwsWafIntegration|awswaf\.com/.+challenge", re.I), "waf_challenge"),
    (re.compile(r"Haz clic en el botón de abajo para seguir comprando|Click the button below to continue shopping", re.I), "continue_shopping_interstitial"),
]


def detect_block(status: int, html: str) -> str | None:
    head = html[:20000]
    for rx, name in BLOCK_PATTERNS:
        if rx.search(head):
            return name
    if status in (429, 503):
        return f"http_{status}"
    if status == 200 and len(html) < 6000 and "<title>" in head and "Amazon" not in head:
        return "suspiciously_small_page"
    return None


class Fetcher:
    def __init__(self, conn: sqlite3.Connection, settings: Settings):
        self.conn = conn
        self.s = settings
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.user_agent,
            "Accept-Language": settings.accept_language,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        self._last_request = 0.0
        self._robots: urllib.robotparser.RobotFileParser | None = None
        self._robots_at = 0.0
        self._pw = None  # lazy Playwright backend

    # ---------------- politeness ----------------
    def update_settings(self, s: Settings) -> None:
        self.s = s
        self.session.headers["User-Agent"] = s.user_agent
        self.session.headers["Accept-Language"] = s.accept_language

    def _robots_ok(self, url: str) -> bool:
        if not self.s.respect_robots:
            return True
        if self._robots is None or time.time() - self._robots_at > 86400:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.session.get(self.s.base_url + "/robots.txt", timeout=self.s.request_timeout_s)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except requests.RequestException:
                rp.parse([])
            self._robots, self._robots_at = rp, time.time()
        return self._robots.can_fetch("*", url)

    def requests_last_hour(self) -> int:
        return self.conn.execute(
            "SELECT COUNT(*) FROM fetch_log WHERE ts > ?", (time.time() - 3600,)
        ).fetchone()[0]

    def wait_turn(self) -> None:
        delay = self.s.min_delay_s + random.uniform(0, self.s.jitter_s)
        elapsed = time.time() - self._last_request
        if elapsed < delay:
            time.sleep(delay - elapsed)

    # ---------------- fetching ----------------
    def get(self, url: str, kind: str) -> FetchResult:
        if not self._robots_ok(url):
            res = FetchResult(url, 0, "", "robots_disallowed", "robots.txt disallows this URL")
            self._log(kind, res)
            return res
        if self.requests_last_hour() >= self.s.max_requests_per_hour:
            return FetchResult(url, 0, "", "rate_limited", "hourly request cap reached")
        self.wait_turn()
        t0 = time.time()
        try:
            if self.s.fetch_backend == "playwright":
                status, html = self._get_playwright(url)
            else:
                r = self.session.get(url, timeout=self.s.request_timeout_s)
                r.encoding = r.encoding or "utf-8"
                status, html = r.status_code, r.text
            ms = int((time.time() - t0) * 1000)
            block = detect_block(status, html)
            if block:
                res = FetchResult(url, status, html, "blocked", block, ms)
            elif status >= 400:
                res = FetchResult(url, status, html, "error", f"http_{status}", ms)
            else:
                res = FetchResult(url, status, html, "ok", "", ms)
        except Exception as e:  # network errors, timeouts, browser errors
            res = FetchResult(url, 0, "", "error", f"{type(e).__name__}: {e}"[:300], int((time.time() - t0) * 1000))
        self._last_request = time.time()
        self._log(kind, res)
        return res

    def _get_playwright(self, url: str) -> tuple[int, str]:
        """Plain page render in headless Chromium. No stealth plugins, no
        challenge solving: if Amazon shows a challenge we just report it."""
        if self._pw is None:
            from playwright.sync_api import sync_playwright  # optional dependency
            pw = sync_playwright().start()
            browser = pw.chromium.launch()
            ctx = browser.new_context(locale="es-ES", timezone_id="Europe/Madrid", user_agent=self.s.user_agent)
            self._pw = (pw, browser, ctx)
        page = self._pw[2].new_page()
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=int(self.s.request_timeout_s * 1000))
            page.wait_for_timeout(1500)
            return (resp.status if resp else 0), page.content()
        finally:
            page.close()

    def close(self) -> None:
        if self._pw:
            try:
                self._pw[1].close()
                self._pw[0].stop()
            except Exception:
                pass
            self._pw = None

    def _log(self, kind: str, res: FetchResult) -> None:
        self.conn.execute(
            "INSERT INTO fetch_log(ts,kind,url,status,outcome,bytes,ms,detail) VALUES(?,?,?,?,?,?,?,?)",
            (db.now(), kind, res.url, res.status, res.outcome, len(res.html or ""), res.ms, res.detail),
        )
