"""Narration with a prosody plan per phrase (pauses, speed, pitch, energy, expressiveness).
Engines: 'chatterbox' (expressive, MIT) or 'kokoro' (Apache-2.0, fallback)."""
import re, random, numpy as np

SR_OUT = 24000
ACTION = ("disparado", "arrasando", "saldrían", "avanzarían", "golpe", "volando", "rechazada", "bloqueada", "congelarse", "calentaría")
REVEAL_START = ("pero", "porque", "y entonces", "que no", "y aquí", "lo que", "y si", "hay más", "así que")

def classify(p, prev):
    w = p.split(); low = p.lower()
    if p.endswith("?"): return "question"
    if len(w) <= 3: return "punch"
    if low.startswith(REVEAL_START) or (prev or "").endswith("..."): return "reveal"
    if any(a in low for a in ACTION): return "action"
    return "info"

# speed, pre-pause (s), pitch shift (semitones), gain (dB), chatterbox exaggeration
STYLE = {
    "info":     (1.06, 0.18, 0.0, 0.0, 0.55),
    "action":   (1.15, 0.14, 0.7, 1.2, 0.80),
    "reveal":   (0.95, 0.42, -0.8, -0.5, 0.50),
    "punch":    (1.00, 0.30, 1.0, 1.8, 0.75),
    "question": (1.04, 0.22, 0.4, 0.5, 0.65),
}

def plan(phrases_with_scene, seed=7):
    r = random.Random(seed); out = []; prev = None; prev_scene = None
    for si, p in phrases_with_scene:
        k = classify(p, prev)
        sp, pause, st, gain, ex = STYLE[k]
        sp *= r.uniform(0.97, 1.03)                      # no perfectly regular cadence
        pause = pause * r.uniform(0.8, 1.25) + (0.12 if si != prev_scene and prev is not None else 0)
        st += r.uniform(-0.35, 0.35)                     # every phrase a slightly different melody
        out.append(dict(scene=si, text=p, kind=k, speed=round(sp, 3), pause=round(pause if prev is not None else 0.25, 3),
                        pitch=round(st, 2), gain=gain, exaggeration=ex))
        prev = p; prev_scene = si
    return out

class Engine:
    def __init__(self, name="chatterbox", ref_wav=None):
        self.name = name; self.ref = ref_wav
        if name == "chatterbox":
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            import torch
            self.m = ChatterboxMultilingualTTS.from_pretrained(device="cpu"); self.sr = self.m.sr
        else:
            from kokoro_onnx import Kokoro
            self.m = Kokoro("/home/claude/tts/kokoro.onnx", "/home/claude/tts/voices.npz"); self.sr = 24000

    NUMW = set("cero uno una dos tres cuatro cinco seis siete ocho nueve diez once doce veinte veinticuatro veintiun veintiuno treinta cien ciento trescientos mil millon millones ochenta".split())
    def ok(self, text, wav):
        """intelligibility gate: transcribe and compare (numbers ignored), plus a speaking-rate sanity check"""
        import asr, soundfile as sf, tempfile
        dur = len(wav)/SR_OUT; cps = len(text)/max(dur, 0.1)
        if not (7 <= cps <= 24): return False, 1.0
        f = tempfile.mktemp(suffix=".wav"); sf.write(f, wav, SR_OUT)
        hyp, _ = asr.transcribe(f)
        r = " ".join(w for w in asr.norm(text) if w not in self.NUMW)
        h = " ".join(w for w in asr.norm(hyp) if not any(ch.isdigit() for ch in w) and w not in self.NUMW)
        e = asr.wer(r, h)
        return e <= 0.2, e

    def say(self, item):
        if self.name == "chatterbox":
            best = None
            for attempt in range(4):
                wav = self._say(item)
                good, e = self.ok(item["text"], wav)
                if good: return wav
                if best is None or e < best[0]: best = (e, wav)
            if best[0] <= 0.34: return best[1]
            if not hasattr(self, "fallback"): self.fallback = Engine("kokoro")
            item = dict(item); item["fallback"] = True
            return self.fallback._say(item)
        return self._say(item)

    def _say(self, item):
        if self.name == "chatterbox":
            kw = dict(language_id="es", exaggeration=item["exaggeration"], cfg_weight=0.35 if item["exaggeration"] > 0.6 else 0.45)
            if self.ref: kw["audio_prompt_path"] = self.ref
            wav = self.m.generate(item["text"], **kw).squeeze(0).numpy()
            sr = self.sr
        else:
            wav, sr = self.m.create(item["text"], voice="em_alex", speed=item["speed"], lang="es")
        wav = wav.astype(np.float32)
        import librosa
        if sr != SR_OUT: wav = librosa.resample(wav, orig_sr=sr, target_sr=SR_OUT)
        if self.name == "chatterbox" and abs(item["speed"]-1) > 0.02:
            wav = librosa.effects.time_stretch(wav, rate=item["speed"])
        if abs(item["pitch"]) > 0.15:
            wav = librosa.effects.pitch_shift(wav, sr=SR_OUT, n_steps=item["pitch"])
        wav *= 10**(item["gain"]/20)
        a = np.abs(wav); idx = np.where(a > 0.01)[0]
        if len(idx): wav = wav[max(0, idx[0]-240): idx[-1]+480]
        # short fades to avoid clicks
        n = min(240, len(wav)//4); ramp = np.linspace(0, 1, n)
        wav[:n] *= ramp; wav[-n:] *= ramp[::-1]
        return wav
