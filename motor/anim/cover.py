"""Portada (miniatura TikTok) — divertida, llamativa y con sentido. Sin IA: fotograma propio + tipografía.
Uso:
  python3 cover.py VID --src out/VID.mp4 --at 4.2 --hook "¡EL VECINO METIÓ|UN GENERADOR EN CASA!" [--movie "Planta 8"] [--part 5] [--sticker "¿SOBREVIVES?"]
  → build/VID/cover.png (1080x1920)
part 1 o sin part: NO se pone «PARTE». part ≥ 2: insignia «PARTE n».
El texto importante va entre y=300 y y=1350 (fuera de la zona de la interfaz de TikTok)."""
import sys, os, argparse, subprocess, math, random
sys.path.insert(0, "/home/claude/anim")
from engine import *
from cine import *
import cairo

def outlined(c, s, x, y, size, fill, stroke=(0.08, 0.07, 0.09), lw=14, fam="Anton", rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    e = c.text_extents(s); c.move_to(-e[2]/2-e[0], 0); c.text_path(s)
    c.set_source_rgb(*stroke); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgb(*fill); c.fill(); c.restore()
    return e[2]

def fit(c, s, size, maxw, fam="Anton"):
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    while size > 30:
        c.set_font_size(size)
        if c.text_extents(s)[2] <= maxw: break
        size -= 4
    return size

def burst(c, x, y, r, n, col, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.new_path()
    for i in range(n*2):
        a = i*math.pi/n; rr = r if i % 2 == 0 else r*0.78
        c.line_to(math.cos(a)*rr, math.sin(a)*rr)
    c.close_path(); c.set_source_rgb(*col); c.fill_preserve(); c.set_source_rgb(0.08, 0.07, 0.09); c.set_line_width(8); c.stroke(); c.restore()

def make(vid, src, at, hook, movie=None, part=None, sticker=None, out=None, hy=660, zy=0.55, scene_mod=None, bx=None, by=830):
    B = f"/home/claude/anim/build/{vid}"; os.makedirs(B, exist_ok=True)
    bgp = f"{B}/cover_bg.png"
    if scene_mod and ":" in scene_mod:   # MOD:VID:escena:fracción → fotograma limpio (sin subtítulos) dibujado con la función de escena
        import importlib; mod, sv, si, fr = scene_mod.split(":"); m = importlib.import_module(mod); fn = m.SCENES[sv][int(si)]
        sf_, cc = new_surface(); cc.set_source_rgb(0, 0, 0); cc.paint(); fn(cc, float(fr)*5.0, 5.0, 10+float(fr)*5.0); sf_.write_to_png(bgp); zy = None
    elif scene_mod:   # portada dibujada a medida: COVER[vid](c) en el módulo de escenas (preferible: composición limpia)
        import importlib; m = importlib.import_module(scene_mod); sf_, cc = new_surface(); m.COVER[vid](cc); sf_.write_to_png(bgp); zy = None
    else: subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{at}", "-i", src, "-frames:v", "1", "-vf", f"scale={W}:{H},eq=brightness=0.06:contrast=1.15:saturation=1.35:gamma=1.25", bgp], check=True)
    surf, c = new_surface()
    img = cairo.ImageSurface.create_from_png(bgp)
    # fondo: fotograma con zoom suave + contraste
    c.save()
    if zy is not None: c.translate(W/2, H*zy); c.scale(1.15, 1.15); c.translate(-W/2, -H*zy)
    c.set_source_surface(img, 0, 0); c.paint(); c.restore()
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.6); g.add_color_stop_rgba(0.3, 0, 0, 0, 0.0); g.add_color_stop_rgba(0.72, 0, 0, 0, 0.0); g.add_color_stop_rgba(1, 0, 0, 0, 0.85)
    c.set_source(g); c.paint()
    yel = hexc('#FFD23F'); red = hexc('#E0503F'); white = hexc('#FBF8F1')
    # nombre de la historia (arriba)
    if movie:
        s = fit(c, movie.upper(), 150, W-160)
        outlined(c, movie.upper(), W/2, 410, s, white, lw=16)
    # gancho divertido en dos líneas, en pegatina amarilla inclinada
    lines = [l.strip() for l in hook.split("|") if l.strip()]
    c.save(); c.translate(W/2, hy); c.rotate(-0.05)
    sizes = [fit(c, l, 96, W-200) for l in lines]; sz = min(sizes)
    hh = sz*1.18*len(lines)+60
    c.set_source_rgba(0, 0, 0, 0.45); rrect(c, -W/2+70+12, -hh/2+16, W-140, hh, 30); c.fill()
    rrect(c, -W/2+70, -hh/2, W-140, hh, 30); c.set_source_rgb(*yel); c.fill_preserve(); c.set_source_rgb(0.08, 0.07, 0.09); c.set_line_width(8); c.stroke()
    for i, l in enumerate(lines):
        y = -hh/2+30+sz*1.18*(i+0.82)
        c.select_font_face("Anton", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(sz)
        e = c.text_extents(l); c.move_to(-e[2]/2-e[0], y); c.set_source_rgb(0.08, 0.07, 0.09); c.show_text(l)
    c.restore()
    # insignia PARTE n (solo desde la parte 2)
    if part and int(part) >= 2:
        px, py = (bx or W-185), by
        burst(c, px, py, 150, 14, red, 0.2)
        outlined(c, "PARTE", px, py-25, 48, white, lw=8, rot=0.12)
        outlined(c, str(int(part)), px, py+75, 110, yel, lw=12, rot=0.12)
    # pegatina secundaria opcional (pregunta / reto)
    if sticker:
        c.save(); c.translate(300, 1500); c.rotate(-0.1)
        font(c, 44, True); tw = c.text_extents(sticker)[2]; w = tw+70; h = 84
        rrect(c, -w/2, -h/2, w, h, 42); c.set_source_rgb(*red); c.fill_preserve(); c.set_source_rgb(0.08, 0.07, 0.09); c.set_line_width(6); c.stroke()
        txt(c, sticker, 0, 16, 44, white); c.restore()
    vig(c, 0.35)
    out = out or f"{B}/cover.png"; surf.write_to_png(out); return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("vid"); ap.add_argument("--src"); ap.add_argument("--at", type=float, default=3.0)
    ap.add_argument("--hook", required=True); ap.add_argument("--movie"); ap.add_argument("--part", type=int); ap.add_argument("--sticker"); ap.add_argument("--out"); ap.add_argument("--hy", type=float, default=660); ap.add_argument("--zy", type=float, default=0.55); ap.add_argument("--scene"); ap.add_argument("--bx", type=float); ap.add_argument("--by", type=float, default=830)
    a = ap.parse_args(); print("COVER", make(a.vid, a.src, a.at, a.hook, a.movie, a.part, a.sticker, a.out, a.hy, a.zy, a.scene, a.bx, a.by))
