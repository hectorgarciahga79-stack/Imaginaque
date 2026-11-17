"""Narración: ElevenLabs (cuenta del usuario) o archivo manual.

Orden de preferencia:
  1. Archivo indicado en el guion (`narration.file`) — p. ej. generado con la
     integración de ElevenLabs de Claude o exportado desde elevenlabs.io.
  2. API REST de ElevenLabs si existe la variable ELEVENLABS_API_KEY
     (usa los créditos de TU cuenta; no se contrata nada).
  3. Sin narración: el vídeo se monta igual (música + SFX + subtítulos).

La pista se divide automáticamente en frases detectando silencios y cada
frase se coloca en el instante `at` del guion (sincronía con las escenas).
"""
import json
import os
import re
import subprocess
import urllib.request

import numpy as np

SR = 48000


def _decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def elevenlabs_tts(text, voice_id, model_id, out_path, api_key):
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128" % voice_id,
        data=json.dumps({"text": text, "model_id": model_id,
                         "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.6}}).encode(),
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r, open(out_path, "wb") as f:
        f.write(r.read())
    return out_path


def split_by_silence(y, n_phrases, thresh_db=-38.0, min_sil=0.18):
    """Segmentos de voz [(ini, fin)] en segundos, fusionando hasta n_phrases."""
    win = int(0.01 * SR)
    frames = len(y) // win
    env = np.sqrt(np.mean(y[: frames * win].reshape(frames, win) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(env)
    voiced = db > thresh_db
    segs = []
    start = None
    sil = 0
    for i, v in enumerate(voiced):
        if v:
            if start is None:
                start = i
            sil = 0
        elif start is not None:
            sil += 1
            if sil * 0.01 >= min_sil:
                segs.append([start * 0.01, (i - sil + 1) * 0.01])
                start = None
                sil = 0
    if start is not None:
        segs.append([start * 0.01, frames * 0.01])
    # fusionar los huecos más pequeños hasta tener n_phrases
    while len(segs) > n_phrases:
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        k = int(np.argmin(gaps))
        segs[k] = [segs[k][0], segs[k + 1][1]]
        del segs[k + 1]
    return segs


def prepare(sb, engine_dir, out_dir):
    """Devuelve dict con la pista de narración colocada (np.array) y las frases
    con tiempos de pantalla reales para los subtítulos."""
    os.makedirs(out_dir, exist_ok=True)
    cfg = sb.get("narration")
    if not cfg:
        return None
    path = cfg.get("file")
    if path and not os.path.isabs(path):
        path = os.path.join(engine_dir, path)
    if not path or not os.path.exists(path):
        key = os.environ.get("ELEVENLABS_API_KEY")
        if key:
            path = os.path.join(out_dir, "narracion_elevenlabs.mp3")
            elevenlabs_tts(cfg["text"], cfg["voice"]["voice_id"], cfg["voice"].get("model_id", "eleven_multilingual_v2"), path, key)
        else:
            print("[narración] No hay archivo ni ELEVENLABS_API_KEY: se monta sin voz. Coloca el audio en", cfg.get("file"))
            return {"track": None, "phrases": [{"text": p["text"], "start": p["at"], "end": p["at"] + 1.2} for p in cfg["phrases"]]}
    y = _decode(path)
    phrases = cfg["phrases"]
    segs = split_by_silence(y, len(phrases))
    if len(segs) != len(phrases):
        print("[narración] aviso: %d segmentos para %d frases; se usa reparto proporcional" % (len(segs), len(phrases)))
    total = sb.get("total_duration") or sum(s["duration"] for s in sb["shots"])
    track = np.zeros(int((total + 1) * SR), dtype=np.float32)
    placed = []
    pad = 0.04
    for p, seg in zip(phrases, segs):
        a = max(0, int((seg[0] - pad) * SR))
        b = min(len(y), int((seg[1] + pad * 2) * SR))
        clip = y[a:b].copy()
        fade = int(0.012 * SR)
        clip[:fade] *= np.linspace(0, 1, fade)
        clip[-fade:] *= np.linspace(1, 0, fade)
        start = int(p["at"] * SR)
        end = min(len(track), start + len(clip))
        track[start:end] += clip[: end - start]
        placed.append({"text": p["text"], "start": p["at"] + pad, "end": p["at"] + (seg[1] - seg[0]) + pad})
    # comprobar solapes
    for a, b in zip(placed, placed[1:]):
        if b["start"] < a["end"]:
            print("[narración] aviso: solape entre '%s' y '%s'" % (a["text"], b["text"]))
    with open(os.path.join(out_dir, "narration_timing.json"), "w") as f:
        json.dump(placed, f, ensure_ascii=False, indent=1)
    return {"track": track, "phrases": placed, "source": path}
