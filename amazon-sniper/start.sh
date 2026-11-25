#!/usr/bin/env bash
# Arranque manual (sin servicios): motor supervisado + panel web, en segundo plano.
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$ROOT/.venv/bin/python"; [[ -x "$PY" ]] || PY=python3
mkdir -p "$ROOT/data"
(cd "$ROOT/engine" && nohup "$PY" -m sniper supervise >> "$ROOT/data/engine.log" 2>&1 &)
(cd "$ROOT/web" && nohup npm run start >> "$ROOT/data/web.log" 2>&1 &)
echo "Motor y panel arrancados. Panel: http://127.0.0.1:3210"
