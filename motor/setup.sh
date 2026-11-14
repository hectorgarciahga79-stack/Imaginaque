#!/usr/bin/env bash
# ImaginaQue — prepara el motor en una sesión nueva. Ejecutar desde la carpeta donde se descargaron los archivos del motor.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /home/claude/anim/el /home/claude/anim/build /home/claude/anim/final /home/claude/tiktok/fonts /home/claude/tiktok/sfx /home/claude/tiktok/audio ~/.fonts
cp "$SRC"/anim/*.py "$SRC"/anim/render_tl.sh /home/claude/anim/
cp "$SRC"/tiktok/fonts/*.ttf /home/claude/tiktok/fonts/ && cp "$SRC"/tiktok/fonts/*.ttf ~/.fonts/
cp "$SRC"/tiktok/sfx/*.wav /home/claude/tiktok/sfx/
cp "$SRC"/tiktok/audio/music.wav /home/claude/tiktok/audio/
[ -f /home/claude/tiktok/scripts.json ] || echo '{}' > /home/claude/tiktok/scripts.json
cp "$SRC"/tiktok/series.json /home/claude/tiktok/series.json
mkdir -p /home/claude/tiktok/portadas && cp "$SRC"/tiktok/portadas/*.png /home/claude/tiktok/portadas/ 2>/dev/null || true
python3 - <<'PY'
import json
S = json.load(open("/home/claude/tiktok/scripts.json")); ser = json.load(open("/home/claude/tiktok/series.json"))
for k, e in ser["episodios"].items():
    if "scenes" in e: S.setdefault(k, {"story": e["title"], "part": e["ep"], "title": e["title"], "style": "cine", "series": e["serie"], "scenes": e["scenes"]})
json.dump(S, open("/home/claude/tiktok/scripts.json", "w"), ensure_ascii=False, indent=1)
PY
fc-cache -f >/dev/null 2>&1 || true
python3 -c "import cairo" 2>/dev/null || pip install --break-system-packages -q pycairo
python3 -c "import faster_whisper" 2>/dev/null || pip install --break-system-packages -q faster-whisper
python3 -c "import librosa, soundfile" 2>/dev/null || pip install --break-system-packages -q librosa soundfile
which ffmpeg >/dev/null || (apt-get install -y -q ffmpeg >/dev/null 2>&1 || pip install --break-system-packages -q imageio-ffmpeg)
python3 - <<'EOF'
import sys; sys.path.insert(0, "/home/claude/anim")
import cairo, engine, styles, cine, scenes
print("MOTOR OK · cairo", cairo.version, "· escenas:", ", ".join(sorted(scenes.SCENES)))
EOF
