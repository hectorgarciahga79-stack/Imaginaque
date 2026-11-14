"""Portada a partir de una imagen base de Héctor (3:4) + insignia «PARTE n» (solo n ≥ 2).
Uso: python3 cover_img.py BASE.png OUT_PREFIX [--part n] [--bx 0.5 --by 0.82]
→ OUT_PREFIX_3x4.png (la imagen con la parte, para subir como portada) y OUT_PREFIX_9x16.png (1080x1920, para los primeros 0,6 s del vídeo).
bx/by: posición de la insignia en fracción de la imagen base (centro)."""
import sys, argparse, math
sys.path.insert(0, "/home/claude/anim")
import cairo
from PIL import Image, ImageFilter

def badge(c, x, y, part, s=1.0):
    c.save(); c.translate(x, y); c.rotate(-0.06); c.scale(s, s)
    # trazo de pincel rojo (estilo de las portadas)
    w, h = 470, 150
    c.new_path(); c.move_to(-w/2-20, -h/2+8)
    for i in range(13): c.line_to(-w/2+i*w/12, -h/2+(8 if i % 2 else -6))
    c.line_to(w/2+26, -h/2+14); c.line_to(w/2+6, 0); c.line_to(w/2+30, h/2-10)
    for i in range(12, -1, -1): c.line_to(-w/2+i*w/12, h/2+(6 if i % 2 else -8))
    c.line_to(-w/2-30, h/2-14); c.line_to(-w/2-8, 0); c.close_path()
    c.set_source_rgba(0, 0, 0, 0.55); c.save(); c.translate(10, 12); c.fill_preserve(); c.restore(); c.new_path()
    c.new_path(); c.move_to(-w/2-20, -h/2+8)
    for i in range(13): c.line_to(-w/2+i*w/12, -h/2+(8 if i % 2 else -6))
    c.line_to(w/2+26, -h/2+14); c.line_to(w/2+6, 0); c.line_to(w/2+30, h/2-10)
    for i in range(12, -1, -1): c.line_to(-w/2+i*w/12, h/2+(6 if i % 2 else -8))
    c.line_to(-w/2-30, h/2-14); c.line_to(-w/2-8, 0); c.close_path()
    g = cairo.LinearGradient(0, -h/2, 0, h/2); g.add_color_stop_rgb(0, 0.86, 0.1, 0.1); g.add_color_stop_rgb(1, 0.62, 0.04, 0.05)
    c.set_source(g); c.fill()
    # texto: PARTE (blanco) + número (amarillo), con contorno oscuro
    c.select_font_face("Anton", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
    parts = [("PARTE ", (0.98, 0.97, 0.95)), (str(part), (1.0, 0.82, 0.12))]
    sizes = [96, 122]; widths = []
    for (t, _), sz in zip(parts, sizes): c.set_font_size(sz); widths.append(c.text_extents(t)[4])
    x0 = -sum(widths)/2
    for (t, col), sz, wd in zip(parts, sizes, widths):
        c.set_font_size(sz); c.move_to(x0, sz*0.36); c.text_path(t)
        c.set_source_rgb(0.08, 0.06, 0.07); c.set_line_width(12); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        c.set_source_rgb(*col); c.fill(); x0 += wd
    c.restore()

def make(base, prefix, part=None, bx=0.5, by=0.82):
    im = Image.open(base).convert("RGB")
    p34 = f"{prefix}_3x4.png"; im.save(p34)
    if part and int(part) >= 2:
        s = cairo.ImageSurface.create_from_png(p34); c = cairo.Context(s)
        badge(c, im.width*bx, im.height*by, int(part), im.width/1086)
        s.write_to_png(p34)
    top = Image.open(p34).convert("RGB")
    W, H = 1080, 1920
    bg = top.resize((int(H*top.width/top.height), H)).crop((0, 0, W, H)) if False else top.resize((int(top.width*H/top.height), H))
    bg = bg.crop(((bg.width-W)//2, 0, (bg.width-W)//2+W, H)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.eval(bg, lambda v: int(v*0.3))
    fg = top.resize((W, int(top.height*W/top.width)))
    bg.paste(fg, (0, (H-fg.height)//2)); p916 = f"{prefix}_9x16.png"; bg.save(p916)
    return p34, p916

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("base"); ap.add_argument("prefix"); ap.add_argument("--part", type=int)
    ap.add_argument("--bx", type=float, default=0.5); ap.add_argument("--by", type=float, default=0.82)
    a = ap.parse_args(); print(*make(a.base, a.prefix, a.part, a.bx, a.by))
