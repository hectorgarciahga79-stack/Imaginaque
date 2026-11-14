"""TTS (Kokoro, local) + frame rendering + final mux. Usage: python3 pipeline.py A1 [A2 ...]"""
import json, re, os, sys, subprocess, math, importlib
import numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/anim")
from engine import *

ROOT = "/home/claude/anim"; TT = "/home/claude/tiktok"
SCRIPTS = json.load(open(f"{TT}/scripts.json"))
VOICE, SPEED = "em_alex", 1.12
SR = 24000
COVER_S = 0.6   # segundos de portada al inicio del vídeo
TITLES = {"A": "¿Y si la Tierra dejara de girar?", "B": "¿Y si despertaras con 1.000 millones?"}

def phrases_of(text):
    parts = re.split(r"(?<=[.?!])\s+|(?<=\.\.\.)\s+", text)
    return [p.strip() for p in parts if p.strip()]

_k = None
def tts(txt):
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro("/home/claude/tts/kokoro.onnx", "/home/claude/tts/voices.npz")
    s, sr = _k.create(txt, voice=VOICE, speed=SPEED, lang="es")
    # trim leading/trailing silence
    a = np.abs(s); idx = np.where(a > 0.01)[0]
    if len(idx): s = s[max(0, idx[0]-240): idx[-1]+480]
    return s

ENGINE = os.environ.get("TTS_ENGINE", "kokoro")
_eng = None
def build_voice(vid):
    global _eng
    from voice import plan, Engine
    B = f"{ROOT}/build/{vid}"; os.makedirs(B, exist_ok=True)
    tl_path = f"{B}/timeline.json"
    if os.path.exists(tl_path) and os.path.exists(f"{B}/voice.wav") and json.load(open(tl_path)).get("engine") == ENGINE:
        return json.load(open(tl_path))
    scenes = SCRIPTS[vid]["scenes"]
    items = plan([(si, p) for si, (txt, _) in enumerate(scenes) for p in phrases_of(txt)], seed=hash(vid) % 1000)
    out = []; t = 0.0
    tl = {"engine": ENGINE, "scenes": [{"start": None, "end": None} for _ in scenes], "phrases": []}
    import hashlib
    os.makedirs(f"{B}/ph", exist_ok=True); new = 0; maxnew = int(os.environ.get("MAX_NEW", "999"))
    for it in items:
        out.append(np.zeros(int(it["pause"]*SR), np.float32)); t += it["pause"]
        key = hashlib.md5(json.dumps([ENGINE, it["text"], it["speed"], it["pitch"], it["gain"], it["exaggeration"]]).encode()).hexdigest()
        cp = f"{B}/ph/{key}.npy"
        if os.path.exists(cp): a = np.load(cp)
        else:
            if new >= maxnew: print("PARTIAL", vid, flush=True); raise SystemExit(3)
            if _eng is None: _eng = Engine(ENGINE, os.environ.get("TTS_REF"))
            a = _eng.say(it); np.save(cp, a); new += 1
        print(vid, it['kind'], round(len(a)/SR, 2), it['text'][:40], flush=True)
        sc = tl["scenes"][it["scene"]]
        if sc["start"] is None: sc["start"] = t - min(it["pause"], 0.12)
        tl["phrases"].append({**it, "start": t, "end": t+len(a)/SR})
        out.append(a); t += len(a)/SR
        sc["end"] = t
    out.append(np.zeros(int(0.7*SR), np.float32)); t += 0.7
    tl["scenes"][0]["start"] = 0.0; tl["scenes"][-1]["end"] = t
    for i in range(len(scenes)-1):  # cut just before the next scene's speech
        tl["scenes"][i]["end"] = tl["scenes"][i+1]["start"]
    tl["total"] = t
    sf.write(f"{B}/voice.wav", np.concatenate(out), SR)
    json.dump(tl, open(tl_path, "w"), ensure_ascii=False, indent=1)
    return tl

def ts(t):
    h = int(t//3600); m = int(t % 3600//60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

STOP = set("que de la el en y a los las un una lo se no por con es su al del mi tu te le ya o si pero más muy ni".split())
def build_ass(vid, tl):
    B = f"{ROOT}/build/{vid}"; total = tl["total"]
    sc = SCRIPTS[vid]; base = sc.get("title") or TITLES[vid[0]]
    title = (f"{base} · Cap. {sc['part']}" if sc.get("style") == "3d" else f"{base} ({sc['part']})") if sc.get("part") else base
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Cap,Anton,108,&H00FFFFFF,&H00FFFFFF,&H00221F29,&H96000000,0,0,0,0,100,100,1,0,1,8,3,5,110,110,0,1",
           "Style: Title,Montserrat,60,&H00221F29,&H00221F29,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,0,0,3,20,0,8,80,80,190,1",
           "Style: Movie,Anton,130,&H00F2EEE6,&H00F2EEE6,&H00141216,&H96000000,0,0,0,0,100,100,6,0,1,6,4,8,60,60,330,1",
           "Style: End,Anton,96,&H00F2EEE6,&H00F2EEE6,&H00141216,&H96000000,0,0,0,0,100,100,4,0,1,6,4,5,60,60,0,1",
           "Style: MovieSub,Montserrat,40,&H003FD2FF,&H003FD2FF,&H00141216,&H96000000,1,0,0,0,100,100,10,0,1,4,2,8,60,60,500,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    c0 = COVER_S if os.path.exists(f"{B}/cover.png") else 0.0   # portada en los primeros fotogramas
    if sc.get("movie"):   # cartela de película al inicio: NOMBRE (+ «PARTE n» solo desde la parte 2; decisión de Héctor 30-10-2026)
        ass.append(f"Dialogue: 2,{ts(0.15+c0)},{ts(1.7+c0)},Movie,,0,0,0,,{{\\fad(200,300)\\t(0,1500,\\fscx104\\fscy104)}}{sc['movie'].upper()}")
        if int(sc.get('part', 1)) >= 2:
            ass.append(f"Dialogue: 2,{ts(0.3+c0)},{ts(1.7+c0)},MovieSub,,0,0,0,,{{\\fad(350,450)}}PARTE {sc.get('part', 1)}")
    if sc.get("movie") and total-(tl["phrases"][-1]["end"] if tl["phrases"] else total) > 1.5:   # cartela final «CONTINUARÁ»
        e0 = tl["phrases"][-1]["end"]+0.3
        ass.append(f"Dialogue: 2,{ts(e0)},{ts(total)},End,,0,0,0,,{{\\fad(400,300)\\pos(540,820)}}{sc.get('end_text', 'CONTINUARÁ…')}")
        ass.append(f"Dialogue: 2,{ts(e0+0.4)},{ts(total)},MovieSub,,0,0,0,,{{\\fad(400,300)\\an5\\pos(540,930)}}{sc.get('end_sub') or (sc['movie'].upper() + ' · PARTE ' + str(int(sc.get('part', 1))+1))}")
    if sc.get("style") not in ("3d", "cine"):   # estilo 3D: sin rótulo superior (como la referencia); el nombre va en el pie del post
        ass.append(f"Dialogue: 0,{ts(0)},{ts(total)},Title,,0,0,0,,{title}")
    for ph in tl["phrases"]:
        words = ph["text"].split(); chunks = []; cur = []
        for w in words:
            cur.append(w)
            if len(cur) >= 3 or (len(" ".join(cur)) > 13 and len(cur) >= 2) or re.search(r"[,:;]$", w):
                chunks.append(cur); cur = []
        if cur:
            if chunks and len(cur) == 1 and len(chunks[-1]) < 3: chunks[-1] += cur
            else: chunks.append(cur)
        cw = [len(" ".join(x))+2 for x in chunks]; ct = sum(cw); a = ph["start"]; d = ph["end"]-ph["start"]
        for x, wgt in zip(chunks, cw):
            b = a+d*wgt/ct
            cand = [(len(re.sub(r"\W", "", w))+(20 if re.search(r"\d", w) else 0), i) for i, w in enumerate(x) if w.lower().strip(",.¿?¡!…") not in STOP]
            hi = max(cand)[1] if cand else -1
            txt = " ".join(("{\\c&H003FD2FF&}"+w.upper()+"{\\c&H00FFFFFF&}") if i == hi else w.upper() for i, w in enumerate(x))
            if ph.get("kind") == "punch":
                rot = -4 if len(ass) % 2 else 4
                ass.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fs150\\frz{rot}\\c&H003FD2FF&\\fscx135\\fscy135\\t(0,110,\\fscx100\\fscy100)\\pos(540,1420)}}{txt.replace('{\\c&H003FD2FF&}','').replace('{\\c&H00FFFFFF&}','')}")
            else:
                ass.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fscx80\\fscy80\\t(0,80,\\fscx100\\fscy100)\\pos(540,1430)}}{txt}")
            a = b
    open(f"{B}/subs.ass", "w").write("\n".join(ass))

def render_frames(vid, tl, scenes_mod):
    B = f"{ROOT}/build/{vid}"; total = tl["total"]; n = int(math.ceil(total*FPS))
    fns = scenes_mod.SCENES[vid]
    assert len(fns) == len(tl["scenes"]), (len(fns), len(tl["scenes"]))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", f"{B}/frames.mp4"],
                         stdin=subprocess.PIPE)
    surf, c = new_surface()
    PH = tl["phrases"]
    si = 0
    for f in range(n):
        t = f/FPS
        while si < len(tl["scenes"])-1 and t >= tl["scenes"][si]["end"]: si += 1
        sc = tl["scenes"][si]; lt = t-sc["start"]; d = sc["end"]-sc["start"]
        c.save(); c.set_source_rgb(0, 0, 0); c.paint()
        # camera: punch-in at cut + slow drift
        pi_ = max((j for j, ph in enumerate(PH) if ph["start"] <= t), default=0)
        ph = PH[pi_]; pt = t-ph["start"]; sgn = 1 if pi_ % 2 else -1
        if vid in getattr(scenes_mod, "CALM", ()):          # estilo cine: empuje lento de cámara, sin sacudidas
            k = 1.0+0.06*ease(clamp(lt/d))+0.012*(1-eout(pt/0.5))
            c.translate(W/2+sgn*8*ease(clamp(lt/d)), H/2)
        else:
            k = 1.0+0.05*(1-eout(lt/0.25))+0.03*clamp(lt/d)
            k += 0.025*(1-eout(pt/0.35))                      # mini punch on each new phrase (every ~1-3 s)
            c.translate(W/2+sgn*14*eout(pt/0.6), H/2); c.rotate(sgn*0.006*eout(pt/0.6))
            if ph.get("kind") in ("punch", "action") and pt < 0.35: shake(c, t, 9*(1-pt/0.35))
        c.scale(k, k); c.translate(-W/2, -H/2)
        fns[si](c, lt, d, t)
        c.restore()
        p.stdin.write(surf.get_data())
    p.stdin.close(); p.wait()

def mux(vid, tl, booms=()):
    B = f"{ROOT}/build/{vid}"; total = tl["total"]
    sfx_in = []; flt = []; n = 0
    for i, sc in enumerate(tl["scenes"][1:], 1):
        sfx_in += ["-i", f"{TT}/sfx/whoosh.wav"]; flt.append(f"[{n}:a]adelay={int(max(0, sc['start']-0.22)*1000)}:all=1,volume=0.28[x{n}]"); n += 1
    for i in booms:
        sfx_in += ["-i", f"{TT}/sfx/boom.wav"]; flt.append(f"[{n}:a]adelay={int(tl['scenes'][i]['start']*1000)+80}:all=1,volume=0.5[x{n}]"); n += 1
    flt.append("".join(f"[x{k}]" for k in range(n))+f"amix=inputs={n}:normalize=0,apad=whole_dur={total}[s]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *sfx_in, "-filter_complex", ";".join(flt), "-map", "[s]", "-t", f"{total}", "-ar", "48000", f"{B}/sfx.wav"], check=True)
    fc = (f"[1:a]aresample=48000,apad=whole_dur={total},aformat=channel_layouts=stereo,asplit=2[vo1][vo2];"
          f"[2:a]aloop=loop=-1:size=2e9,atrim=0:{total},aresample=48000,aformat=channel_layouts=stereo,volume=0.15,afade=t=in:d=1,afade=t=out:st={total-1.2}:d=1.2[m0];"
          "[m0][vo2]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[m];"
          "[vo1][m][3:a]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a];"
          f"[0:v]subtitles={B}/subs.ass:fontsdir={TT}/fonts[vout]")
    os.makedirs(f"{ROOT}/out", exist_ok=True)
    vin = f"{B}/frames.mp4"
    if os.path.exists(f"{B}/hook.mp4"):   # gancho 3D (clip IA) sobre la escena 0, con fundido a la animación
        e0 = tl["scenes"][0]["end"]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vin, "-i", f"{B}/hook.mp4", "-filter_complex",
                        f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setpts=PTS-STARTPTS,"
                        f"tpad=stop_mode=clone:stop_duration={e0+1},trim=0:{e0+0.4},format=yuva420p,fade=t=out:st={e0-0.1}:d=0.5:alpha=1[h];"
                        "[0:v][h]overlay=0:0:eof_action=pass[v]", "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                        "-pix_fmt", "yuv420p", f"{B}/frames_h.mp4"], check=True)
        vin = f"{B}/frames_h.mp4"
    cov = []
    if os.path.exists(f"{B}/cover.png"):   # portada (cover.py) encima de todo en los primeros COVER_S s: TikTok la usa como miniatura (primer fotograma)
        cov = ["-loop", "1", "-t", f"{COVER_S+0.2}", "-i", f"{B}/cover.png"]
        fc = fc.replace("[vout]", "[sv]") + (f";[4:v]scale={W}:{H},format=yuva420p,fade=t=out:st={COVER_S-0.12}:d=0.12:alpha=1[cv];"
                                             "[sv][cv]overlay=0:0:eof_action=pass[vout]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vin, "-i", f"{B}/voice.wav", "-i", f"{TT}/audio/music.wav", "-i", f"{B}/sfx.wav", *cov,
                    "-filter_complex", fc, "-map", "[vout]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total}", f"{ROOT}/out/{vid}.mp4"], check=True)

if __name__ == "__main__":
    import scenes
    for vid in sys.argv[1:]:
        tl = build_voice(vid); build_ass(vid, tl)
        importlib.reload(scenes)
        render_frames(vid, tl, scenes)
        mux(vid, tl, scenes.BOOMS.get(vid, ()))
        print(vid, "ok", round(tl["total"], 1))
