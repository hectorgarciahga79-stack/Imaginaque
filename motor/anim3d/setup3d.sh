#!/usr/bin/env bash
# Motor 3D de bloques (estilo aprobado por Héctor el 06-11-2026). Ejecutar tras setup.sh.
set -e
mkdir -p /home/claude/t3d/au
cp /home/claude/motor/anim3d/*.py /home/claude/t3d/
python3 -c "import bpy" 2>/dev/null || pip install --break-system-packages -q bpy
python3 -c "import cv2, scipy" 2>/dev/null || pip install --break-system-packages -q opencv-python-headless scipy
python3 -c "import bpy; print('MOTOR 3D OK · bpy', bpy.app.version_string)"
