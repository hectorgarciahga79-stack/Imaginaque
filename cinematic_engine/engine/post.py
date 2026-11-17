"""Postproducción y exportación con FFmpeg.

Montaje de los planos renderizados -> reescalado a 1080x1920 -> transiciones
(fundidos, destellos en los cortes clave) -> etalonaje 'neon noir' (balance
de color sombras cian / altas magenta, saturación, curva) -> viñeta, grano de
película y enfoque -> subtítulos animados (ASS) -> audio normalizado a
-14 LUFS -> H.264 High, yuv420p, +faststart (TikTok / YouTube Shorts).
"""
import glob
import json
import os
import subprocess

from . import subtitles as SUB

GRADES = {
    # sombras frías, altas cálidas/magenta; contraste y saturación de 'noche de neón'
    "neon_noir": "colorbalance=rs=-0.05:gs=0.0:bs=0.08:rm=0.03:gm=-0.03:bm=0.04:rh=0.06:gh=0.0:bh=0.03,"
                 "eq=contrast=1.07:saturation=1.22:gamma=0.97,"
                 "curves=all='0/0 0.12/0.09 0.5/0.52 0.88/0.92 1/1'",
    "neutral": "eq=contrast=1.03:saturation=1.05",
}


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("FFmpeg falló:\n" + " ".join(cmd) + "\n" + r.stderr[-3000:])
    return r


def assemble(sb, proj, prof, output=None):
    fps = sb["fps"]
    W, H = sb["output"]["width"], sb["output"]["height"]
    rdir = os.path.join(proj, "renders", prof["name"])
    vdir = os.path.join(proj, "video")
    os.makedirs(vdir, exist_ok=True)
    out = output or os.path.join(vdir, "final.mp4" if prof["name"] != "preview" else "preview.mp4")
    inputs, filters = [], []
    t = 0.0
    cuts = []
    for i, shot in enumerate(sb["shots"]):
        files = sorted(glob.glob(os.path.join(rdir, shot["id"], "*.png")))
        files = [f for f in files if os.path.getsize(f) > 0]
        if not files:
            raise RuntimeError("Faltan fotogramas del plano %s en %s" % (shot["id"], rdir))
        n_exp = int(round(shot["duration"] * fps))
        rate = len(files) / shot["duration"]
        inputs += ["-framerate", "%.6f" % rate, "-pattern_type", "glob", "-i", os.path.join(rdir, shot["id"], "*.png")]
        filters.append(
            "[%d:v]scale=%d:%d:flags=lanczos,setsar=1,fps=%d,trim=duration=%.4f,setpts=PTS-STARTPTS[v%d]"
            % (i, W, H, fps, shot["duration"], i))
        if i:
            cuts.append(t)
        t += shot["duration"]
    total = t
    n = len(sb["shots"])
    filters.append("".join("[v%d]" % i for i in range(n)) + "concat=n=%d:v=1:a=0[cat]" % n)
    g = sb.get("grade", {})
    chain = [GRADES.get(g.get("preset", "neon_noir"), GRADES["neutral"])]
    # destellos en cortes marcados (inicio de persecución / cámara lenta)
    flash_at = [c for c in cuts if any(abs(c - x) < 0.05 for x in g.get("flash_cuts", []))]
    for c in flash_at:
        chain.append("eq=brightness=0.35:enable='between(t,%.3f,%.3f)'" % (c, c + 1.5 / fps))
        chain.append("eq=brightness=0.15:enable='between(t,%.3f,%.3f)'" % (c + 1.5 / fps, c + 3.5 / fps))
    chain.append("vignette=angle=%.3f:mode=forward" % (0.55 * g.get("vignette", 0.35) + 0.2))
    if g.get("sharpen", 0.6):
        chain.append("unsharp=5:5:%.2f:5:5:0" % g.get("sharpen", 0.6))
    if g.get("grain", 7):
        chain.append("noise=alls=%d:allf=t" % g.get("grain", 7))
    chain.append("fade=t=in:st=0:d=0.45,fade=t=out:st=%.3f:d=0.5" % (total - 0.5))
    # subtítulos
    timing = os.path.join(proj, "audio", "narration_timing.json")
    phrases = json.load(open(timing, encoding="utf-8")) if os.path.exists(timing) else [
        {"text": p["text"], "start": p["at"], "end": p["at"] + 1.0} for p in sb.get("narration", {}).get("phrases", [])]
    ass = os.path.join(vdir, "subtitulos.ass")
    SUB.build_ass(phrases, ass, W, H, sb.get("subtitles"), sb.get("titles"))
    fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
    chain.append("ass='%s':fontsdir='%s'" % (ass.replace(":", "\\:"), fonts_dir))
    chain.append("format=yuv420p")
    filters.append("[cat]" + ",".join(chain) + "[vout]")
    audio = os.path.join(proj, "audio", "banda_sonora.wav")
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs
    if os.path.exists(audio):
        cmd += ["-i", audio]
    cmd += ["-filter_complex", ";".join(filters), "-map", "[vout]"]
    if os.path.exists(audio):
        cmd += ["-map", "%d:a" % n, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(fps * 2), "-bf", "2",
            "-x264-params", "aq-mode=3", "-maxrate", "25M", "-bufsize", "50M",
            "-movflags", "+faststart", "-t", "%.3f" % total, out]
    _run(cmd)
    return out


def qa(video, proj):
    """Control de calidad automático del MP4 + hoja de contactos."""
    pr = json.loads(_run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video]).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), None)
    rep = {
        "file": video,
        "size_mb": round(int(pr["format"]["size"]) / 1e6, 2),
        "duration": float(pr["format"]["duration"]),
        "video": {"codec": v["codec_name"], "profile": v.get("profile"), "width": v["width"], "height": v["height"],
                  "pix_fmt": v["pix_fmt"], "fps": v["r_frame_rate"], "bitrate_kbps": int(pr["format"]["bit_rate"]) // 1000},
        "audio": {"codec": a["codec_name"], "sample_rate": a["sample_rate"], "channels": a["channels"]} if a else None,
    }
    # sonoridad integrada
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    for line in r.splitlines()[::-1]:
        if line.strip().startswith("I:"):
            rep["loudness_lufs"] = float(line.split()[1])
            break
    # negros / congelados
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", video, "-vf", "blackdetect=d=0.3:pic_th=0.97,freezedetect=n=0.002:d=0.6",
                        "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    rep["black_segments"] = [l.split("]")[-1].strip() for l in r.splitlines() if "black_start" in l]
    rep["frozen_segments"] = [l.split("]")[-1].strip() for l in r.splitlines() if "freeze_start" in l]
    checks = {
        "vertical_1080x1920": v["width"] == 1080 and v["height"] == 1920,
        "h264": v["codec_name"] == "h264",
        "yuv420p": v["pix_fmt"] == "yuv420p",
        "audio_aac": bool(a) and a["codec_name"] == "aac",
        "duration_ok": abs(rep["duration"] - 20.0) < 0.3,
        "loudness_tiktok": abs(rep.get("loudness_lufs", -99) + 14) < 1.5,
    }
    rep["checks"] = checks
    sheet = os.path.join(os.path.dirname(video), os.path.splitext(os.path.basename(video))[0] + "_contactos.jpg")
    _run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vf", "fps=1,scale=216:384,tile=10x2", "-frames:v", "1", sheet])
    rep["contact_sheet"] = sheet
    return rep
