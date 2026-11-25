"""Continuous background process + supervisor (auto-restart)."""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from . import db
from .config import Settings, save_defaults
from .engine import Engine

_stop = False


def _handle_stop(signum, frame):  # noqa: ARG001
    global _stop
    _stop = True


class SingleInstance:
    """OS file lock so two engines never hammer Amazon at the same time."""

    def __init__(self, path: Path):
        self.path = path
        self.fh = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = open(self.path, "a+")
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write(str(os.getpid()))
        self.fh.flush()
        return True


def _sleep(seconds: float, conn) -> None:
    end = time.time() + seconds
    while not _stop and time.time() < end:
        time.sleep(min(2.0, end - time.time()))
        db.state_set(conn, "heartbeat", time.time())


def run(max_tasks: int | None = None, quiet: bool = False) -> int:
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)
    conn = db.connect()
    lock = SingleInstance(db.db_path().parent / "engine.lock")
    if not lock.acquire():
        print("Ya hay un motor AMAZON SNIPER en marcha (lock ocupado).", file=sys.stderr)
        return 3
    save_defaults(conn)
    engine = Engine(conn)
    if conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
        engine.seed()
    engine.reidentify()
    db.state_set(conn, "started_at", time.time())
    db.state_set(conn, "pid", os.getpid())
    db.state_set(conn, "status", "running")
    db.state_set(conn, "current_task", None)
    db.log_event(conn, "info", f"Motor iniciado (pid {os.getpid()})")
    done = 0
    last_maint = last_queries = 0.0
    try:
        while not _stop:
            s = Settings.load(conn)
            engine.s = s
            engine.fetcher.update_settings(s)
            db.state_set(conn, "heartbeat", time.time())
            if s.paused:
                db.state_set(conn, "status", "paused")
                _sleep(15, conn)
                continue
            now = time.time()
            if now - last_maint > 600:
                engine.reverify_due()
                db.trim(conn)
                last_maint = now
            if now - last_queries > 3600:
                engine.generate_queries()
                last_queries = now
            task = engine.next_task()
            if task is None:
                blocks = {k: v for k, v in engine.blocks().items() if v.get("until", 0) > now}
                db.state_set(conn, "status", "backoff" if blocks else "waiting")
                nxt = conn.execute("SELECT MIN(next_run_at) FROM tasks WHERE enabled=1").fetchone()[0] or now + 60
                _sleep(max(5.0, min(60.0, nxt - now)), conn)
                continue
            db.state_set(conn, "status", "running")
            if not quiet:
                print(time.strftime("%H:%M:%S"), task["kind"], task["label"], flush=True)
            engine.run_task(task)
            db.state_set(conn, "current_task", None)
            done += 1
            if max_tasks and done >= max_tasks:
                break
    finally:
        db.state_set(conn, "status", "stopped")
        db.state_set(conn, "current_task", None)
        db.log_event(conn, "info", "Motor detenido")
        engine.fetcher.close()
    return 0


def supervise() -> int:
    """Keeps `run` alive: restarts it with exponential backoff if it crashes."""
    signal.signal(signal.SIGINT, _handle_stop)
    signal.signal(signal.SIGTERM, _handle_stop)
    backoff = 5
    while not _stop:
        started = time.time()
        proc = subprocess.Popen([sys.executable, "-m", "sniper", "run", "--quiet"], cwd=str(Path(__file__).resolve().parents[1]))
        while proc.poll() is None:
            if _stop:
                proc.terminate()
                try:
                    proc.wait(30)
                except subprocess.TimeoutExpired:
                    proc.kill()
                return 0
            time.sleep(1)
        code = proc.returncode
        if code == 0 or code == 3:  # clean stop or another instance holds the lock
            if code == 3:
                time.sleep(60)
                continue
            return 0
        if time.time() - started > 600:
            backoff = 5
        print(f"[supervisor] motor terminó con código {code}; reinicio en {backoff}s", file=sys.stderr, flush=True)
        time.sleep(backoff)
        backoff = min(backoff * 2, 300)
    return 0
