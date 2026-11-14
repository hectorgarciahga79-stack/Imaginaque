#!/usr/bin/env bash
# ImaginaQue · prepara el motor en una sesión de Claude Code (nube u ordenador).
# Usa el setup.sh y el setup3d.sh originales del Motor: no los sustituye.
# Idempotente: se puede ejecutar en cada sesión.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p /home/claude
# Librerías gráficas del sistema que Blender necesita para renderizar sin pantalla (el ordenador de Héctor ya las traía).
if [ ! -e /usr/lib/x86_64-linux-gnu/libEGL.so.1 ]; then
  (apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libegl1 libegl-mesa0 libgl1-mesa-dri libgles2) >/dev/null 2>&1 || echo "AVISO: no se pudo instalar libEGL (el render 3D fallará)"
fi
rm -rf /home/claude/motor
cp -r "$REPO/motor" /home/claude/motor
cd /home/claude/motor
bash setup.sh            # → "MOTOR OK" (2,5D cine, align, cover, voz)
bash anim3d/setup3d.sh   # → "MOTOR 3D OK" (Blender bpy, motor 3D de bloques)
