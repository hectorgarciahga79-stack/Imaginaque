#!/usr/bin/env bash
# ImaginaQue · montaje de un vídeo 3D de bloques, siguiendo NIGHTLY.md (sección «ESTILO 3D DE BLOQUES»).
# No sustituye nada del motor: solo encadena sus scripts y se puede reanudar (los fotogramas hechos se saltan).
#
# Uso:  scripts/montar3d.sh <vid> <TOTAL_s> [post_modulo]
#   LOOK=cine (por defecto): luz cinematográfica, cielo, niebla, contorno, polvo, DOF, desenfoque de movimiento y
#            transiciones (anim3d/lux.py) entre el render y el etalonaje. LOOK=classic: exactamente como antes.
#   ej. scripts/montar3d.sh q30 77.3 post_q9
# Requisitos previos (pasos 3–5 del manual):
#   /home/claude/t3d/shots_<vid>.py, audio_<vid>.py, subs_<vid>.py
#   /home/claude/anim/build/<VID>/voice.wav   (voz de ElevenLabs)
#   /home/claude/t3d/au/<vid>_words.json      (palabras con tiempos, faster-whisper)
# Salida: /home/claude/t3d/final/<VID>.mp4 (calidad máxima) y <VID>_tt.mp4 (< 10 MB, para subir desde Chrome).
set -euo pipefail
vid="$1"; TOTAL="$2"; POST="${3:-post_q9}"; VID="${vid^^}"; export LOOK="${LOOK:-cine}"
T=/home/claude/t3d; FR="$T/fr_$vid"; PP="$T/pp_$vid"; LOG="$T/log_$vid"; mkdir -p "$FR" "$PP" "$LOG" "$T/final"
[ "$LOOK" = cine ] && { FR="$T/fr_${vid}_cine"; PP="$T/pp_${vid}_cine"; mkdir -p "$FR" "$PP"; }
cd "$T"
export EGL_PLATFORM=surfaceless HF_HUB_DISABLE_XET=1
python3 -c "import OpenEXR" 2>/dev/null || pip install --break-system-packages -q OpenEXR
echo "[1/5] fotogramas 3D ($VID, $TOTAL s) — reanudable"
SHOTS="shots_$vid" FR="$FR" python3 render.py frames 0/2 > "$LOG/fr0.log" 2>&1 &
SHOTS="shots_$vid" FR="$FR" python3 render.py frames 1/2 > "$LOG/fr1.log" 2>&1 &
wait
grep -q "DONE 0" "$LOG/fr0.log" && grep -q "DONE 1" "$LOG/fr1.log" || { echo "ERROR en el render: ver $LOG"; exit 1; }
SRC="$FR"
if [ "$LOOK" = cine ]; then
  echo "[1b/5] luz cinematográfica y efectos de cámara (lux)"
  FR="$FR" FRC="${FR}_lux" python3 lux.py 0/2 > "$LOG/lux0.log" 2>&1 &
  FR="$FR" FRC="${FR}_lux" python3 lux.py 1/2 > "$LOG/lux1.log" 2>&1 &
  wait
  grep -q "LUX DONE 0" "$LOG/lux0.log" && grep -q "LUX DONE 1" "$LOG/lux1.log" || { echo "ERROR en lux: ver $LOG"; exit 1; }
  SRC="${FR}_lux"
fi
echo "[2/5] etalonaje ($POST)"
FR="$SRC" PP="$PP" TOTAL="$TOTAL" python3 "$POST.py" 0/2 > "$LOG/pp0.log" 2>&1 &
FR="$SRC" PP="$PP" TOTAL="$TOTAL" python3 "$POST.py" 1/2 > "$LOG/pp1.log" 2>&1 &
wait
echo "[3/5] audio (música y efectos propios + voz) y normalización -14 LUFS"
python3 "audio_$vid.py" | tail -1
ffmpeg -v error -y -i "mix_$vid.wav" -af loudnorm=I=-14:TP=-1.2 -ar 48000 "mix_n_$vid.wav"
echo "[4/5] subtítulos karaoke"
python3 "subs_$vid.py" | tail -1
echo "[5/5] montaje final"
ffmpeg -v error -y -framerate 24 -i "$PP/p%05d.png" -i "mix_n_$vid.wav" \
  -vf "scale=1080:1920:flags=lanczos,unsharp=5:5:0.4,ass=subs_$vid.ass:fontsdir=/home/claude/tiktok/fonts" \
  -c:v libx264 -preset medium -crf 21 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest "final/$VID.mp4"
# copia < 10 MB para subir desde Chrome: bitrate máximo calculado con la duración (objetivo 9,3 MB)
VBR=$(python3 -c "print(int(9.3*8*1024/float('$TOTAL') - 128))")
ffmpeg -v error -y -i "final/$VID.mp4" -c:v libx264 -preset medium -crf 28 -maxrate ${VBR}k -bufsize $((VBR*2))k -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart "final/${VID}_tt.mp4"
ls -la "final/$VID.mp4" "final/${VID}_tt.mp4"
echo "MONTAJE OK $VID"
