"""Montaje para RETENCIÓN (TikTok / Shorts).

Convierte una 'historia' (JSON) en un vídeo vertical de 20-35 s pensado para
que nadie deslice:

* La voz manda: la narración (ElevenLabs) se alinea frase a frase, se
  eliminan los silencios largos y cada frase abre un 'beat' visual nuevo
  (cambio de plano cada 1-2,5 s).
* Cada beat reutiliza metraje 3D ya renderizado (o un inserto barato) con
  edición agresiva: zoom de empuje, temblor, congelado, rebobinado, cámara
  lenta/rápida, destello, glitch RGB, blanco y negro.
* Capa gráfica (ASS/libass): texto gancho gigante, subtítulos palabra a
  palabra, círculo rojo para señalar, barra de progreso y tarjeta final con
  la pregunta que invita a comentar.
* Sonido: música sintetizada con 'drop', caída en los momentos de tensión,
  'ducking' bajo la voz y SFX en cada corte (whoosh, golpe, explosión,
  rebobinado, latido, sirena, riser...).

Uso: python run.py viral historias/la_placa.json
"""
import json
import os
import shutil
import subprocess

import numpy as np

from . import audio as A
from . import narration as N
from . import subtitles as SUB

SR = A.SR
FPS = 24
W, H = 1080, 1920
ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ENGINE_DIR, "assets", "fonts")


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("FFmpeg falló:\n" + " ".join(cmd) + "\n" + r.stderr[-2500:])
    return r


# ------------------------------------------------------------------ voz
def align_phrases(segs, phrases):
    """Asigna segmentos de voz consecutivos a cada frase (programación
    dinámica): la duración de cada frase debe parecerse a la esperada por
    su número de caracteres, y los cortes deben caer en los huecos grandes."""
    n, m = len(segs), len(phrases)
    chars = [max(4, len(p["say"])) for p in phrases]
    voiced = sum(b - a for a, b in segs)
    k = voiced / sum(chars)
    INF = 1e18
    cost = [[INF] * (n + 1) for _ in range(m + 1)]
    back = [[0] * (n + 1) for _ in range(m + 1)]
    cost[0][0] = 0.0
    for i in range(1, m + 1):
        exp = chars[i - 1] * k
        for j in range(i, n - (m - i) + 1):
            for s in range(i - 1, j):
                if cost[i - 1][s] >= INF:
                    continue
                dur = sum(b - a for a, b in segs[s:j])
                inner = sum(segs[q + 1][0] - segs[q][1] for q in range(s, j - 1))
                c = ((dur - exp) / max(0.4, exp)) ** 2 + 1.5 * inner
                if cost[i - 1][s] + c < cost[i][j]:
                    cost[i][j] = cost[i - 1][s] + c
                    back[i][j] = s
    out, j = [], n
    for i in range(m, 0, -1):
        s = back[i][j]
        out.append((segs[s][0], segs[j - 1][1]))
        j = s
    return out[::-1]


def _norm(w):
    import unicodedata
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(c for c in w if c.isalnum())


def _script_words(text):
    return [w for w in text.split() if _norm(w)]


def transcribe_words(path):
    """Marcas de tiempo por palabra (faster-whisper local, gratis). Se guardan
    junto al audio (<audio>_words.json) para no repetir el cálculo."""
    cache = os.path.splitext(path)[0] + "_words.json"
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    y16 = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                                       capture_output=True, check=True).stdout, np.float32)
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(y16, language="es", word_timestamps=True, beam_size=1)
    words = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for sg in segs for w in sg.words]
    json.dump(words, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    return words


def build_voice(story, out_dir):
    """Devuelve (pista_voz, tiempos de frase en el vídeo).

    Con marcas por palabra (whisper) cada frase del guion se localiza por
    recuento de palabras y los subtítulos usan los tiempos reales de cada
    palabra; sin ellas, se alinea por silencios (programación dinámica)."""
    nar = story["narration"]
    path = nar["file"] if os.path.isabs(nar["file"]) else os.path.join(ENGINE_DIR, nar["file"])
    y = N._decode(path)
    beats = story["beats"]
    words = transcribe_words(path) if nar.get("word_timing", True) else None
    per_phrase = None
    if words:
        counts = [len(_script_words(b["say"])) for b in beats]
        if sum(counts) == len(words):
            per_phrase, k = [], 0
            for c in counts:
                per_phrase.append(words[k:k + c])
                k += c
        else:
            print("[viral] aviso: el guion tiene %d palabras y la voz %d; alineo por silencios" % (sum(counts), len(words)))
    if per_phrase:
        spans = [(ws[0][0], ws[-1][1]) for ws in per_phrase]
    else:
        segs = N.split_by_silence(y, 999, thresh_db=nar.get("thresh_db", -38.0), min_sil=0.12)
        spans = align_phrases(segs, beats)
    lead = nar.get("lead", 0.12)
    gap = nar.get("gap", 0.14)
    total_est = lead + sum(b - a for a, b in spans) + (gap + 0.6) * len(spans) + 4
    track = np.zeros(int(total_est * SR) + SR, dtype=np.float32)
    t = lead
    timing = []
    for i, ((a, b), beat) in enumerate(zip(spans, beats)):
        t += beat.get("pause", 0.0)
        ia, ib = max(0, int((a - 0.03) * SR)), min(len(y), int((b + 0.07) * SR))
        clip = y[ia:ib].copy()
        f = int(0.01 * SR)
        clip[:f] *= np.linspace(0, 1, f)
        clip[-f:] *= np.linspace(1, 0, f)
        st = int(t * SR)
        track[st:st + len(clip)] += clip
        item = {"text": beat["say"], "start": t + 0.03, "end": t + (b - a) + 0.03}
        if per_phrase:
            sw = _script_words(beat["say"])
            item["words"] = [[t + 0.03 + (w0 - a), t + 0.03 + (w1 - a), txt]
                             for (w0, w1, _), txt in zip(per_phrase[i], sw)]
        timing.append(item)
        t += (ib - ia) / SR + gap
    with open(os.path.join(out_dir, "voz_timing.json"), "w", encoding="utf-8") as fh:
        json.dump(timing, fh, ensure_ascii=False, indent=1)
    return track, timing


def beat_times(timing, story):
    starts = [0.0] + [max(0.0, p["start"] - 0.1) for p in timing[1:]]
    end = timing[-1]["end"] + story.get("end_hold", 2.2)
    ends = starts[1:] + [end]
    return list(zip(starts, ends))


# ------------------------------------------------------------------ vídeo
def _src_dir(story, name):
    src = story["sources"][name]
    return src if os.path.isabs(src) else os.path.join(ENGINE_DIR, src)


def split_beat(story, beat, dur):
    """Divide un beat largo en sub-planos (cambio visual cada 2-4 s).

    'cuts' explícitos: lista de variaciones (heredan del beat). Si no hay y
    el beat dura más de 'max_shot', se reencuadra el mismo plano por tramos
    (zoom y centro alternos), que el ojo percibe como un plano nuevo."""
    cuts = beat.get("cuts")
    if not cuts:
        max_shot = story.get("max_shot", 99)
        if dur <= max_shot:
            return [(beat, dur)]
        k = int(np.ceil(dur / (max_shot * 0.82)))
        a = beat.get("a", 1)
        b = beat.get("b") or (a + 47)
        n = b - a + 1
        frames = [(a + n * j // k, a + n * (j + 1) // k - 1) for j in range(k)]
        frames = [(fa, max(fa + 1, fb)) for fa, fb in frames]
        centers = [[0.5, 0.5], [0.4, 0.55], [0.6, 0.45], [0.5, 0.62]]
        zooms = [[1.0, 1.08], [1.18, 1.26], [1.06, 1.14], [1.24, 1.16]]
        cuts = [{"a": fa, "b": fb, "center": centers[j % 4], "zoom": zooms[j % 4]} for j, (fa, fb) in enumerate(frames)]
        if beat.get("hold"):
            cuts[-1]["hold"] = beat["hold"]
    w = [c.get("w", 1.0) for c in cuts]
    out = []
    for c, wi in zip(cuts, w):
        sub = dict(beat)
        sub.pop("cuts", None)
        sub.pop("hold", None) if "hold" not in c else None
        sub.update(c)
        if out:  # destellos/glitch solo en el primer sub-plano
            sub.pop("flash", None) if "flash" not in c else None
        out.append((sub, dur * wi / sum(w)))
    return out


def render_beat(story, beat, dur, out_path):
    d = _src_dir(story, beat["src"])
    a, b = beat.get("a", 1), beat.get("b")
    files = sorted(f for f in os.listdir(d) if f.endswith(".png") and f[:4].isdigit())
    if b is None:
        b = int(files[-1][:4])
    n_src = b - a + 1
    n_out = max(1, int(round(dur * FPS)))
    hold = int(round(beat.get("hold", 0.0) * FPS))
    play = max(1, n_out - hold)
    stretch = beat.get("speed")
    stretch = (play / n_src) if stretch in (None, "fit") else 1.0 / float(stretch)
    f = ["trim=end_frame=%d" % n_src, "setpts=PTS-STARTPTS"]
    if beat.get("reverse"):
        f.append("reverse")
    f.append("setpts=%.5f*PTS" % stretch)
    f.append("framerate=fps=%d" % FPS if stretch > 1.4 else "fps=%d" % FPS)
    f.append("tpad=stop_mode=clone:stop=%d" % (n_out + 2))
    f.append("trim=end_frame=%d,setpts=PTS-STARTPTS" % n_out)
    # zoom / encuadre / temblor (zoompan sobre imagen ampliada = sin saltos)
    z0, z1 = beat.get("zoom", [1.0, 1.08])
    shake = beat.get("shake", 0)
    if shake:
        z0, z1 = max(z0, 1.06), max(z1, 1.06)
    cx, cy = beat.get("center", [0.5, 0.5])
    N_ = max(1, n_out - 1)
    ease = beat.get("ease", "out")
    prog = "(on/%d)" % N_ if ease == "linear" else "(1-pow(1-on/%d,3))" % N_
    punch = beat.get("punch", 0.045)
    zexp = "%.4f+(%.4f)*%s+%.3f*exp(-on/2.5)" % (z0, z1 - z0, prog, punch)
    sx = "+%d*sin(on*2.7)*exp(-on/%d)" % (shake, max(4, n_out // 2)) if shake else ""
    sy = "+%d*cos(on*3.3)*exp(-on/%d)" % (shake, max(4, n_out // 2)) if shake else ""
    xexp = "max(0,min(iw-iw/zoom,(iw-iw/zoom)*%.3f%s))" % (cx, sx)
    yexp = "max(0,min(ih-ih/zoom,(ih-ih/zoom)*%.3f%s))" % (cy, sy)
    f.append("scale=%d:%d:flags=lanczos" % (W * 3 // 2, H * 3 // 2))
    f.append("zoompan=z='%s':x='%s':y='%s':d=1:s=%dx%d:fps=%d" % (zexp, xexp, yexp, W, H, FPS))
    look = beat.get("look")
    if look == "rewind":
        f.append("hue=s=0.15,eq=contrast=1.25:brightness=-0.02,noise=alls=28:allf=t")
    elif look == "bw":
        f.append("hue=s=0,eq=contrast=1.2")
    elif look == "cold":
        f.append("colorbalance=bs=0.12:bm=0.08:rs=-0.06,eq=saturation=0.7")
    if beat.get("glitch"):
        f.append("rgbashift=rh=-16:bh=16:enable='lt(n,5)'")
    if beat.get("flash"):
        f.append("fade=t=in:st=0:d=0.17:color=white")
    f.append("format=yuv420p")
    cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-start_number", str(a),
           "-i", os.path.join(d, "%04d.png"), "-vf", ",".join(f),
           "-frames:v", str(n_out), "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-an", out_path]
    _run(cmd)
    return out_path


# ------------------------------------------------------------------ gráficos (ASS)
def _ts(t):
    return SUB._ts(t)


def _circle_path(r):
    k = 0.5523 * r
    return ("m 0 %d b %d %d %d %d %d 0 b %d %d %d %d 0 %d b %d %d %d %d %d 0 b %d %d %d %d 0 %d" % (
        -r, k, -r, r, -k, r, r, k, k, r, r, -k, r, -r, k, -r, -k, -r, -r, -k, -r))


EXTRA_STYLES = """Style: Hook,Bebas Neue,196,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,3,0,1,9,4,8,50,50,250,1
Style: HookAccent,Bebas Neue,196,&H0000E5FF,&H0000E5FF,&H00000000,&H64000000,0,0,0,0,100,100,3,0,1,9,4,8,50,50,250,1
Style: Stamp,Bebas Neue,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,6,0,3,0,0,7,60,60,300,1
Style: Draw,Arial,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Q,Bebas Neue,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,2,0,1,10,5,5,60,60,0,1
Style: Badge,Montserrat Black,34,&H00FFFFFF,&H00FFFFFF,&H00D62BFF,&H00D62BFF,0,0,0,0,100,100,2,0,3,10,0,7,0,0,0,1
Style: Tag,Bebas Neue,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,5,2,9,0,0,0,1
Style: Chunk,Montserrat Black,84,&H00FFFFFF,&H00FFFFFF,&H00140014,&H96000000,0,0,0,0,100,100,1,0,1,7,3,2,70,70,520,1
Style: Punch,Montserrat Black,120,&H0000E5FF,&H0000E5FF,&H00140014,&H96000000,0,0,0,0,100,100,1,0,1,9,4,2,60,60,520,1
Style: CTA,Montserrat Black,52,&H00000000,&H00000000,&H0000E5FF,&H0000E5FF,0,0,0,0,100,100,1,0,3,14,0,5,60,60,0,1
"""


def build_overlay(story, timing, spans, out_path):
    sub_cfg = dict({"font": "Montserrat Black", "size": 78, "accent": "#FFE500", "margin_v": 470},
                   **story.get("subtitles", {}))
    tmp = out_path + ".subs"
    subs = [t for t, b in zip(timing, story["beats"]) if not b.get("no_sub")]
    chunked = all("words" in t for t in subs)
    SUB.build_ass([] if chunked else subs, tmp, W, H, sub_cfg, None)
    base = open(tmp, encoding="utf-8").read()
    os.remove(tmp)
    base = base.replace("\n[Events]", "\n" + EXTRA_STYLES + "\n[Events]")
    ev = []
    if chunked:
        ev += chunk_subtitles(subs, sub_cfg)
    banner = story.get("_channel", {}).get("categories", {}).get(story.get("category", ""), None)
    if banner:
        ev.append("Dialogue: 5,%s,%s,Badge,,0,0,0,,{\\an7\\pos(42,64)\\3c%s\\4c%s}%s" % (
            _ts(0), _ts(spans[-1][1]), SUB._ass_color(banner["color"]), SUB._ass_color(banner["color"]), banner["label"]))
        tag = story["_channel"].get("tag")
        if tag:
            ev.append("Dialogue: 5,%s,%s,Tag,,0,0,0,,{\\an9\\pos(1038,64)}%s" % (_ts(0), _ts(spans[-1][1]), tag))
    total = spans[-1][1]
    for beat, (s, e) in zip(story["beats"], spans):
        txt = beat.get("text")
        if txt:
            style = "HookAccent" if beat.get("accent") else "Hook"
            t_in = s + beat.get("text_at", 0.0)
            pop = "{\\fad(40,120)\\fscx150\\fscy150\\t(0,140,\\fscx100\\fscy100)\\frz%.1f}" % beat.get("tilt", -2.0)
            ev.append("Dialogue: 3,%s,%s,%s,,0,0,0,,%s%s" % (_ts(t_in), _ts(e), style, pop, txt))
        if beat.get("stamp"):
            ev.append("Dialogue: 3,%s,%s,Stamp,,0,0,0,,{\\an8\\pos(540,300)\\1c&HFFFFFF&\\3c&H0000CC&\\bord0"
                      "\\fad(0,100)\\t(0,500,\\alpha&H20&)}%s" % (_ts(s), _ts(e), beat["stamp"]))
        if beat.get("circle"):
            x, y, r = beat["circle"]
            ca = beat.get("circle_at", 0.15)
            t_in = (e - beat.get("hold", 0.0)) if ca == "hold" else s + ca
            ev.append("Dialogue: 4,%s,%s,Draw,,0,0,0,,{\\an7\\pos(%d,%d)\\1a&HFF&\\3c&H0010FF&\\bord11\\shad0"
                      "\\fscx170\\fscy170\\t(0,180,\\fscx100\\fscy100)\\p1}%s{\\p0}" % (
                          _ts(t_in), _ts(e), x, y, _circle_path(r)))
    # barra de progreso (arriba): crece durante todo el vídeo
    ev.append("Dialogue: 5,%s,%s,Draw,,0,0,0,,{\\an7\\pos(0,0)\\1c&H0000E5FF&\\bord0\\shad0"
              "\\clip(0,0,0,14)\\t(0,%d,\\clip(0,0,%d,14))\\p1}m 0 0 l %d 0 l %d 14 l 0 14{\\p0}" % (
                  _ts(0), _ts(total), int(total * 1000), W, W, W))
    end = story.get("ending")
    if end:
        t0 = timing[-1]["start"]
        ev.append("Dialogue: 6,%s,%s,Q,,0,0,0,,{\\pos(540,820)\\fad(80,0)\\fscx130\\fscy130"
                  "\\t(0,160,\\fscx100\\fscy100)}%s" % (_ts(t0), _ts(total), end["question"]))
        if end.get("cta"):
            ev.append("Dialogue: 6,%s,%s,CTA,,0,0,0,,{\\pos(540,1060)\\fad(120,0)}%s" % (
                _ts(timing[-1]["end"] + 0.1), _ts(total), end["cta"]))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(base.rstrip("\n") + "\n" + "\n".join(ev) + "\n")
    return out_path


def chunk_subtitles(subs, cfg):
    """Bloques de 2-3 palabras con la palabra hablada resaltada; las frases de
    golpe (<=3 palabras) en grande, amarillas e inclinadas."""
    accent = SUB._ass_color(cfg.get("accent", "#FFE500"))
    mv = cfg.get("margin_v", 520)
    lines = []
    for ph in subs:
        ws = ph["words"]
        if not ws:
            continue
        if len(ws) <= 3:
            txt = " ".join(w[2].upper() for w in ws)
            lines.append("Dialogue: 2,%s,%s,Punch,,0,0,%d,,{\\fad(30,90)\\frz-4\\fscx135\\fscy135"
                         "\\t(0,130,\\fscx100\\fscy100)}%s" % (_ts(ws[0][0] - 0.03), _ts(ph["end"] + 0.3), mv, txt))
            continue
        chunks, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or (len(cur) >= 2 and w[2][-1:] in ",.;:?!…"):
                chunks.append(cur)
                cur = []
        if cur:
            if len(cur) == 1 and chunks and len(chunks[-1]) < 4:
                chunks[-1] += cur
            else:
                chunks.append(cur)
        for k, ch in enumerate(chunks):
            t0 = ch[0][0] - 0.03
            t1 = chunks[k + 1][0][0] - 0.03 if k + 1 < len(chunks) else ph["end"] + 0.3
            parts = []
            for w in ch:
                ws_ = int((w[0] - t0) * 1000)
                we_ = int((w[1] - t0) * 1000)
                parts.append("{\\1c&H00FFFFFF&\\t(%d,%d,\\1c%s\\fscx112\\fscy112)\\t(%d,%d,\\1c&H00FFFFFF&\\fscx100\\fscy100)}%s" % (
                    ws_, ws_ + 1, accent, we_, we_ + 60, w[2].upper()))
            lines.append("Dialogue: 2,%s,%s,Chunk,,0,0,%d,,{\\fad(20,40)\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)}%s" % (
                _ts(t0), _ts(t1), mv, " ".join(parts)))
    return lines


# ------------------------------------------------------------------ sonido
def _tone(f, dur, decay):
    t = np.arange(int(dur * SR)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * decay)


def sfx_bank():
    rng = np.random.default_rng(11)

    def rewind():
        n = int(0.9 * SR)
        t = np.arange(n) / SR
        f = np.geomspace(1800, 180, n)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + A.bp(rng.standard_normal(n), 800, 5000) * 0.5
        x *= np.minimum(1, t / 0.05) * np.exp(-t * 1.2)
        return A.pan(x, 0)

    def scratch():
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        f = 900 + 700 * np.sin(2 * np.pi * 9 * t)
        x = A.bp(rng.standard_normal(n), 400, 3000) * 0.6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
        return A.pan(x * np.exp(-t * 4), 0)

    def heartbeat():
        out = np.zeros(int(1.6 * SR))
        for st in (0.0, 0.28, 0.8, 1.08):
            c = _tone(52, 0.35, 14) * 0.9
            c[:int(0.2 * SR)] += _tone(90, 0.2, 30) * 0.3
            A.place(out[None, :], c[None, :], st)
        return A.pan(np.tanh(out * 1.5), 0)

    def siren():
        n = int(1.8 * SR)
        t = np.arange(n) / SR
        f = np.where((t * 2.2) % 1 < 0.5, 960, 770)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.18
        x = A.lp(x, 2500) * np.minimum(1, t / 0.1) * np.minimum(1, (1.8 - t) / 0.4)
        return A.pan(x, 0.3)

    def screech():
        n = int(1.4 * SR)
        t = np.arange(n) / SR
        f = 1150 + 120 * np.sin(2 * np.pi * 7 * t) + 60 * rng.standard_normal(n).cumsum() / np.sqrt(SR)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + A.bp(rng.standard_normal(n), 1500, 5000) * 0.35
        return A.pan(x * np.minimum(1, t / 0.06) * np.exp(-t * 1.1), -0.2)

    def hit():
        return A.pan(np.tanh(_tone(48, 1.2, 4) * 1.6 + A.lp(rng.standard_normal(int(1.2 * SR)), 600)
                             * np.exp(-np.arange(int(1.2 * SR)) / SR * 18) * 0.6), 0)

    return {
        "whoosh": lambda: A.SFX.whoosh(0.4, True, 1) * 0.6,
        "whoosh_down": lambda: A.SFX.whoosh(0.5, False, 2) * 0.6,
        "riser": lambda: A.SFX.riser(2.2) * 0.8,
        "impact": lambda: A.SFX.impact(1.0),
        "explosion": lambda: A.SFX.explosion(1.0),
        "metal": lambda: A.SFX.metal_crash(1.0),
        "rewind": rewind, "scratch": scratch, "heartbeat": heartbeat, "siren": siren,
        "screech": screech, "hit": hit, "thunder": lambda: A.SFX.thunder(3.0) * 0.7,
    }


SFX_GAIN = {"whoosh": 0.35, "whoosh_down": 0.35, "riser": 0.5, "impact": 0.8, "explosion": 0.9, "metal": 0.5,
            "rewind": 0.55, "scratch": 0.6, "heartbeat": 0.9, "siren": 0.45, "screech": 0.45, "hit": 0.8,
            "thunder": 0.5}


def build_audio(story, voice, timing, spans, out_dir):
    total = spans[-1][1]
    n = int((total + 0.5) * SR)
    v = np.zeros(n)
    v[:min(n, len(voice))] = voice[:n]
    # música: drop en el beat indicado, caídas (filtro + volumen) en los beats 'dip'
    mcfg = dict({"bpm": 100, "root": "A", "drop_at": 4.0}, **story.get("music", {}))
    if "drop_beat" in mcfg:
        mcfg["drop_at"] = spans[mcfg["drop_beat"]][0]
    dips = [list(spans[i]) for i, b in enumerate(story["beats"]) if b.get("music") == "dip"]
    music = A.Music(mcfg, total, {"slowmo": dips, "end_hit": total - 1})
    m = music.render()[:, :n]
    if m.shape[1] < n:
        m = np.pad(m, ((0, 0), (0, n - m.shape[1])))
    # silencios de música ('cut'): golpe de silencio para el impacto
    tvec = np.arange(n) / SR
    for i, b in enumerate(story["beats"]):
        if b.get("music") == "cut":
            s, e = spans[i]
            g = np.clip(np.minimum((tvec - s) / 0.03, (e - tvec) / 0.15), 0, 1)
            m *= 1 - g
    # ducking bajo la voz
    env = A._env_follow(v, 0.01, 0.25)
    m *= 1 - 0.55 * np.clip(env * 3, 0, 1)
    bank = sfx_bank()
    fx = np.zeros((2, n))
    for i, (b, (s, e)) in enumerate(zip(story["beats"], spans)):
        names = b.get("sfx", [] if i == 0 else ["whoosh"])
        for name in names:
            off = 0.0
            if ":" in name:
                name, off = name.split(":")
                off = (e - s - b.get("hold", 0.0)) if off == "hold" else float(off)
            clip = bank[name]() * SFX_GAIN.get(name, 0.5)
            t0 = s + off
            if name == "riser":
                t0 = e - clip.shape[1] / SR + 0.05
            A.place(fx, clip, max(0, t0))
    # normalización por RMS
    def rms(x):
        return np.sqrt(np.mean(x ** 2) + 1e-12)
    voice_st = A.pan(v, 0)
    voice_st *= 10 ** (-16 / 20) / (rms(v[np.abs(v) > 1e-3]) + 1e-9)
    m *= 10 ** (story.get("music_db", -27) / 20) / (rms(m) + 1e-9)
    fx *= 10 ** (story.get("sfx_db", -22) / 20) / (rms(fx[:, np.any(np.abs(fx) > 1e-3, axis=0)]) + 1e-9)
    mix = A.limiter(voice_st + m + fx, 0.95)
    fade = int(0.4 * SR)
    mix[:, -fade:] *= np.linspace(1, 0, fade)
    path = os.path.join(out_dir, "audio.wav")
    A._write_wav(path, mix)
    return path


# ------------------------------------------------------------------ montaje
GRADE = ("colorbalance=rs=-0.04:bs=0.07:rh=0.05:bh=0.02,eq=contrast=1.08:saturation=1.25:gamma=0.97,"
         "vignette=angle=0.45,unsharp=5:5:0.7:5:5:0,noise=alls=3:allf=t")


def load_story(story_path):
    """Historia + valores por defecto del canal (canales/<canal>.json)."""
    story = json.load(open(story_path, encoding="utf-8"))
    ch = story.get("channel")
    if ch:
        cfg = json.load(open(os.path.join(ENGINE_DIR, "canales", ch + ".json"), encoding="utf-8"))
        story["_channel"] = cfg
        for k, v in cfg.get("defaults", {}).items():
            if isinstance(v, dict):
                story[k] = dict(v, **story.get(k, {}))
            else:
                story.setdefault(k, v)
        lib = cfg.get("library")
        if lib:
            libd = json.load(open(os.path.join(ENGINE_DIR, lib), encoding="utf-8"))
            story["sources"] = dict(libd["sources"], **story.get("sources", {}))
            clips = {c["id"]: c for c in libd["clips"]}
            for b in story["beats"]:  # 'clip': id de la biblioteca -> src/a/b/centro
                for target in [b] + b.get("cuts", []):
                    if "clip" in target:
                        c = clips[target["clip"]]
                        for k in ("src", "a", "b", "center"):
                            if k in c:
                                target.setdefault(k, c[k])
    return story


def retention_report(story, timing, spans, clips_count):
    """Comprueba las reglas del canal y devuelve un informe (y errores)."""
    total = spans[-1][1]
    ch = story.get("_channel", {})
    rules = ch.get("rules", {})
    errors, warns = [], []
    if total < rules.get("min_duration", 0):
        errors.append("Duración %.1f s < mínimo %.0f s: amplía el guion (no se rellena)." % (total, rules["min_duration"]))
    if total > rules.get("max_duration", 1e9):
        warns.append("Duración %.1f s > máximo recomendado %.0f s." % (total, rules["max_duration"]))
    shots = [e - s for s, e in spans]
    sections = {}
    for name, (a, b) in rules.get("sections", {}).items():
        a, b = a * total / rules.get("sections_ref", total), b * total / rules.get("sections_ref", total)
        sections[name] = [i for i, (s, e) in enumerate(spans) if a <= s < b]
    surprises = [i for i, b in enumerate(story["beats"]) if b.get("surprise")]
    if len(surprises) < rules.get("min_surprises", 0):
        warns.append("Solo %d momentos sorprendentes marcados (mínimo %d)." % (len(surprises), rules["min_surprises"]))
    if not story.get("ending", {}).get("question"):
        warns.append("Falta la pregunta final para comentarios.")
    first = story["beats"][0]
    if not first.get("text"):
        warns.append("El gancho (beat 0) no tiene texto grande.")
    rep = {"duration": round(total, 2), "phrases": len(spans), "visual_changes": clips_count,
           "avg_seconds_per_change": round(total / max(1, clips_count), 2), "longest_phrase_s": round(max(shots), 2),
           "surprises": surprises, "sections": sections, "warnings": warns, "errors": errors}
    return rep


def make(story_path, out_dir=None):
    story = load_story(story_path)
    name = os.path.splitext(os.path.basename(story_path))[0]
    out_dir = out_dir or os.path.join(ENGINE_DIR, "projects", "virales", name)
    work = os.path.join(out_dir, "beats")
    os.makedirs(work, exist_ok=True)
    voice, timing = build_voice(story, out_dir)
    spans = beat_times(timing, story)
    pre = retention_report(story, timing, spans, 1)
    if pre["errors"]:
        raise SystemExit("[viral] " + " ".join(pre["errors"]))
    clips = []
    t_cum = 0.0
    for i, (beat, (s, e)) in enumerate(zip(story["beats"], spans)):
        import hashlib
        key = hashlib.md5((json.dumps(beat, sort_keys=True) + "%.3f" % (e - s)).encode()).hexdigest()[:8]
        for j, (sub, sd) in enumerate(split_beat(story, beat, e - s)):
            nfr = int(round((t_cum + sd) * FPS)) - int(round(t_cum * FPS))
            t_cum += sd
            sd = nfr / FPS
            p = os.path.join(work, "%02d_%d_%s_%d.mp4" % (i, j, key, nfr))
            if not os.path.exists(p):
                render_beat(story, sub, sd, p)
            clips.append(p)
        print("[viral] beat %02d %.2f-%.2f %s" % (i, s, e, beat["say"]))
    lst = os.path.join(work, "lista.txt")
    with open(lst, "w") as fh:
        fh.writelines("file '%s'\n" % c for c in clips)
    ass = build_overlay(story, timing, spans, os.path.join(out_dir, "graficos.ass"))
    wav = build_audio(story, voice, timing, spans, out_dir)
    total = spans[-1][1]
    out = os.path.join(out_dir, name + ".mp4")
    vf = GRADE + ",ass='%s':fontsdir='%s',format=yuv420p" % (ass, FONTS)
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
          "-vf", vf, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000",
          "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "12M", "-bufsize", "24M", "-profile:v", "high", "-pix_fmt", "yuv420p",
          "-r", str(FPS), "-g", str(FPS * 2), "-movflags", "+faststart",
          "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", "%.3f" % total, out])
    sheet = os.path.join(out_dir, name + "_contactos.jpg")
    _run(["ffmpeg", "-y", "-v", "error", "-i", out, "-vf", "fps=1,scale=216:384,tile=10x%d" % (int(total) // 10 + 1),
          "-frames:v", "1", sheet])
    rep = retention_report(story, timing, spans, len(clips))
    rules = story.get("_channel", {}).get("rules", {})
    from engine import post
    q = post.qa(out, out_dir, (rules.get("min_duration", 20), rules.get("max_duration", 95)))
    rep["qa"] = {"checks": q["checks"], "loudness_lufs": q["loudness_lufs"], "size_mb": q["size_mb"],
                 "black_segments": q["black_segments"], "frozen_segments": q["frozen_segments"]}
    rep["warnings"] += ["QA: falla %s" % k for k, ok in q["checks"].items() if not ok]
    with open(os.path.join(out_dir, "informe_retencion.json"), "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    for w in rep["warnings"]:
        print("[viral] aviso:", w)
    print("[viral] %s  (%.1f s, %d frases, %d cambios visuales, uno cada %.2f s)" % (
        out, total, len(spans), len(clips), total / len(clips)))
    return out
