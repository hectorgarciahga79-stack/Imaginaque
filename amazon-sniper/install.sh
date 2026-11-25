#!/usr/bin/env bash
# AMAZON SNIPER - instalacion en Linux / macOS.
# Uso:  ./install.sh            (instala dependencias, compila la web y registra los servicios)
#       ./install.sh --no-service
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

python3 -m venv .venv
.venv/bin/pip install --upgrade pip >/dev/null
.venv/bin/pip install -r engine/requirements.txt
(cd web && npm ci && npm run build)

if [[ "${1:-}" == "--no-service" ]]; then
  echo "Instalado sin servicios. Arranque manual: ./start.sh"; exit 0
fi

case "$(uname -s)" in
  Linux)
    mkdir -p ~/.config/systemd/user
    for u in engine web; do
      sed "s#%h/amazon-sniper#$ROOT#g" "deploy/linux/amazon-sniper-$u.service" > ~/.config/systemd/user/amazon-sniper-$u.service
    done
    systemctl --user daemon-reload
    systemctl --user enable --now amazon-sniper-engine amazon-sniper-web
    # keep running after logout / at boot without an open session
    loginctl enable-linger "$USER" 2>/dev/null || echo "(opcional) sudo loginctl enable-linger $USER  para que arranque sin iniciar sesión"
    echo "Servicios activos:  systemctl --user status amazon-sniper-engine"
    ;;
  Darwin)
    mkdir -p ~/Library/LaunchAgents
    for u in engine web; do
      sed "s#__ROOT__#$ROOT#g" "deploy/macos/com.amazonsniper.$u.plist" > ~/Library/LaunchAgents/com.amazonsniper.$u.plist
      launchctl unload ~/Library/LaunchAgents/com.amazonsniper.$u.plist 2>/dev/null || true
      launchctl load -w ~/Library/LaunchAgents/com.amazonsniper.$u.plist
    done
    echo "Agentes cargados (launchctl list | grep amazonsniper)"
    ;;
esac
echo "Panel privado: http://127.0.0.1:3210"
echo "Diagnóstico de acceso real:  (cd engine && ../.venv/bin/python -m sniper doctor)"
