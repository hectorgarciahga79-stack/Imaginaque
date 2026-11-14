"""Estilo «cine»: ilustración plana cinematográfica (paleta apagada, luz de ventana, viñeta, grano),
personaje propio TEO y tarjetas de interfaz (hora, cuenta atrás, etiquetas, reglas, alertas).
Todo dibujado con cairo; nada copiado de otros canales."""
from engine import *
import cairo, math, random

# ---------------- paleta ----------------
C = {k: hexc(v) for k, v in dict(
    wall="#E6D8C1", wall2="#D9C7AA", wood="#8C6A4E", wood2="#6F5240", floor="#7A5C45", floor2="#5E4535",
    dark="#26252A", dark2="#3A3940", ink="#2B2A2F", cream="#F4EEE3", paper="#FBF8F1",
    sky="#C9DCE0", sky2="#EAE3D0", dusk1="#2E3A55", dusk2="#C9775A", night1="#121722", night2="#232B3B",
    red="#C8372D", red2="#E0503F", gold="#E2A63B", teal="#2F6F7A", teal2="#24565F", grey="#5A5F6B", grey2="#474B55",
    skin="#F0D2B4", skin2="#D9B392", hair="#2A2220", steel="#9AA3AD", steel2="#6F7781", water="#6FA8C7", water2="#4E88A8",
    leaf="#6F8F5A", leaf2="#58744A", tile="#DCD6CB", glass="#BFD3D8",
).items()}
OUT = C['ink']; OL = 4  # contorno fino y oscuro (no el grueso de dibujo animado)

def fs(c, col, lw=OL, a=1):
    c.set_source_rgba(*col, a); c.fill_preserve()
    if lw: c.set_source_rgba(*OUT, a); c.set_line_width(lw); c.stroke()
    else: c.new_path()

def box(c, x, y, w, h, col, r=6, lw=OL, a=1): rrect(c, x, y, w, h, r); fs(c, col, lw, a)

def shade(col, k): return mix(col, (0, 0, 0), k)
def tint(col, k): return mix(col, (1, 1, 1), k)

# ---------------- post-proceso ----------------
_GRAIN = None
_GARR = None
def grain(c, t, a=0.07):
    global _GRAIN, _GARR
    if _GRAIN is None:
        import numpy as np
        r = np.random.default_rng(3)
        n = (r.random((540, 540))*255).astype('uint8')
        arr = np.zeros((540, 540, 4), 'uint8'); arr[..., 0] = n; arr[..., 1] = n; arr[..., 2] = n; arr[..., 3] = 255
        _GRAIN = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, 540, 540); _GARR = arr
    c.save(); c.scale(2, 2)
    off = int(t*30) % 7
    p = cairo.SurfacePattern(_GRAIN); p.set_extend(cairo.EXTEND_REPEAT)
    m = cairo.Matrix(); m.translate(off*37 % 540, off*91 % 540); p.set_matrix(m)
    c.set_source(p); c.set_operator(cairo.OPERATOR_OVERLAY); c.paint_with_alpha(a); c.restore()

def vig(c, a=0.45, cx=W/2, cy=H*0.45):
    g = cairo.RadialGradient(cx, cy, H*0.18, cx, cy, H*0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.04, 0.03, 0.05, a); c.set_source(g); c.paint()

def light_shaft(c, pts_top, pts_bot, a=0.18, col=(1, 0.95, 0.82)):
    """haz de luz: cuadrilátero de la ventana al suelo con degradado"""
    (x1, y1), (x2, y2) = pts_top; (x3, y3), (x4, y4) = pts_bot
    g = cairo.LinearGradient(0, min(y1, y2), 0, max(y3, y4)); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    c.new_path(); c.move_to(x1, y1); c.line_to(x2, y2); c.line_to(x4, y4); c.line_to(x3, y3); c.close_path(); c.set_source(g); c.fill()

def dust(c, t, x0, y0, x1, y1, n=26, a=0.5):
    r = random.Random(9)
    for i in range(n):
        x = x0+(r.random()*(x1-x0)+math.sin(t*0.4+i)*30) % (x1-x0); y = y0+(r.random()*(y1-y0)-t*12*(0.5+r.random())) % (y1-y0)
        circle(c, x, y, r.uniform(1.5, 3.5)); c.set_source_rgba(1, 0.97, 0.88, a*(0.4+0.6*abs(math.sin(t+i)))); c.fill()

def darken(c, k):
    if k > 0: c.set_source_rgba(0.03, 0.04, 0.08, k); c.paint()

def post(c, t, v=0.45, g=0.07):
    vig(c, v); grain(c, t, g)

# ---------------- tipografía / interfaz ----------------
def font(c, size, bold=True, fam="Montserrat"):
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)

def txt(c, s, x, y, size=40, col=None, fam="Montserrat", align="center", bold=True, a=1):
    font(c, size, bold, fam); xb, yb, tw, th, xa, ya = c.text_extents(s)
    ox = {"center": -tw/2-xb, "left": -xb, "right": -tw-xb}[align]
    c.move_to(x+ox, y); c.set_source_rgba(*(col or OUT), a); c.show_text(s); return tw

def pop(t, dur=0.35): return back(t/dur) if t > 0 else 0

def chip(c, s, x, y, t, icon=None, size=34, bg=None, fg=None, anchor=None):
    """etiqueta tipo píldora con línea guía opcional hacia anchor=(ax, ay)"""
    k = pop(t)
    if k <= 0: return
    if anchor:
        kk = eout(t/0.5)
        c.set_source_rgba(*C['paper'], 0.95); c.set_line_width(4)
        c.move_to(x, y); c.line_to(lerp(x, anchor[0], kk), lerp(y, anchor[1], kk)); c.stroke()
        circle(c, anchor[0], anchor[1], 9*kk); fs(c, C['paper'], 3)
    font(c, size, True); tw = c.text_extents(s)[2]; pad = 26; iw = 46 if icon else 0
    w = tw+pad*2+iw; h = size*1.6
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    rrect(c, -w/2, -h/2, w, h, h/2); fs(c, bg or C['paper'], 4)
    if icon: icon(c, -w/2+pad+16, 0, 15)
    txt(c, s, -w/2+pad+iw+tw/2, size*0.36, size, fg or OUT)
    c.restore()

def ic_drop(c, x, y, r):
    c.new_path(); c.move_to(x, y-r*1.3); c.curve_to(x+r, y-r*0.2, x+r, y+r, x, y+r); c.curve_to(x-r, y+r, x-r, y-r*0.2, x, y-r*1.3); fs(c, C['water'], 3)

def ic_bolt(c, x, y, r):
    c.new_path(); c.move_to(x+r*0.3, y-r*1.3); c.line_to(x-r*0.7, y+r*0.2); c.line_to(x, y+r*0.2); c.line_to(x-r*0.3, y+r*1.3); c.line_to(x+r*0.8, y-r*0.3); c.line_to(x, y-r*0.3); c.close_path(); fs(c, C['gold'], 3)

def ic_clock(c, x, y, r):
    circle(c, x, y, r); fs(c, C['paper'], 3); c.set_source_rgb(*OUT); c.set_line_width(3); c.move_to(x, y); c.line_to(x, y-r*0.6); c.move_to(x, y); c.line_to(x+r*0.5, y); c.stroke()

def ic_check(c, x, y, r):
    circle(c, x, y, r); fs(c, C['leaf'], 3); c.set_source_rgb(*C['paper']); c.set_line_width(4)
    c.move_to(x-r*0.5, y); c.line_to(x-r*0.1, y+r*0.4); c.line_to(x+r*0.5, y-r*0.4); c.stroke()

def ic_warn(c, x, y, r):
    c.new_path(); c.move_to(x, y-r*1.2); c.line_to(x+r*1.2, y+r); c.line_to(x-r*1.2, y+r); c.close_path(); fs(c, C['red'], 3)
    txt(c, "!", x, y+r*0.75, r*1.3, C['paper'])

def time_card(c, top, big, small, x, y, t, col=None):
    """«APAGÓN / DÍA 1 / 19:04» como en un título de serie"""
    k = pop(t, 0.45)
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    font(c, 40); w = max(c.text_extents(top)[2]+70, 380)
    c.save(); c.rotate(-0.015); rrect(c, -w/2, -60, w, 72, 6); fs(c, col or C['red'], 0); txt(c, top, 0, -11, 40, C['paper']); c.restore()
    txt(c, big, 3, 113, 112, (0, 0, 0), "Anton", a=0.35); txt(c, big, 0, 110, 112, C['paper'], "Anton")
    font(c, 34); w2 = c.text_extents(small)[2]+44
    rrect(c, -w2/2, 136, w2, 52, 26); fs(c, C['gold'], 0); txt(c, small, 0, 174, 34, C['ink'])
    c.restore()

def countdown(c, secs, x, y, t, label="RESTAN", danger=False):
    k = pop(t)
    if k <= 0: return
    m, s = int(secs//60), int(secs % 60)
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    rrect(c, -200, -46, 400, 92, 46); fs(c, C['dark'], 0, 0.85)
    rrect(c, -200, -46, 400, 92, 46); c.set_source_rgb(*(C['red'] if danger and math.sin(t*8) > 0 else C['gold'])); c.set_line_width(5); c.stroke()
    ic_clock(c, -150, 0, 24)
    txt(c, f"{m:02d}:{s:02d}", -20, 22, 60, C['paper'], "Anton")
    txt(c, label, 135, 10, 24, C['gold'])
    c.restore()

def rule_card(c, num, line1, line2, x, y, t, icon=ic_warn):
    k = pop(t, 0.45)
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    c.set_source_rgba(0, 0, 0, 0.3); rrect(c, -380+10, -150+14, 760, 300, 18); c.fill()
    rrect(c, -380, -150, 760, 300, 18); fs(c, C['paper'], 0)
    rrect(c, -110, -128, 220, 50, 25); fs(c, C['dark'], 0); txt(c, f"REGLA #{num}", 0, -92, 30, C['paper'])
    txt(c, line1, 0, -10, 56, C['ink'], "Anton"); txt(c, line2, 0, 60, 56, C['ink'], "Anton")
    c.set_source_rgb(*C['red']); c.set_line_width(5); c.move_to(-200, 92); c.line_to(200, 92); c.stroke()
    icon(c, 0, 124, 18)
    c.restore()

def stat_card(c, label, value, unit, x, y, t, icon=ic_drop, sub=None):
    k = pop(t)
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    c.set_source_rgba(0, 0, 0, 0.25); rrect(c, -230+8, -90+10, 460, 180, 18); c.fill()
    rrect(c, -230, -90, 460, 180, 18); fs(c, C['paper'], 3)
    txt(c, label, 30, -40, 26, C['grey'])
    icon(c, -170, 18, 30)
    tw = txt(c, value, -110, 52, 92, C['ink'], "Anton", align="left")
    txt(c, unit, -110+tw+14, 52, 40, C['water2'], "Anton", align="left")
    if sub:
        font(c, 26); w = c.text_extents(sub)[2]+30
        rrect(c, 230-w-10, -112, w, 44, 22); fs(c, C['teal'], 0); txt(c, sub, 230-w/2-10, -82, 26, C['paper'])
    c.restore()

def phone_alert(c, x, y, s, t, head="ALERTA", l1="", l2="", l3=""):
    c.save(); c.translate(x, y); c.scale(s, s)
    glow = 0.25+0.15*math.sin(t*6)
    g = cairo.RadialGradient(0, 0, 50, 0, 0, 420); g.add_color_stop_rgba(0, 1, 0.25, 0.2, glow); g.add_color_stop_rgba(1, 1, 0.2, 0.2, 0)
    c.set_source(g); c.arc(0, 0, 420, 0, 2*math.pi); c.fill()
    rrect(c, -170, -320, 340, 640, 40); fs(c, C['dark'], 5)
    rrect(c, -150, -296, 300, 592, 28); fs(c, C['red'], 0)
    ic_warn(c, 0, -200, 46)
    txt(c, head, 0, -110, 30, C['paper'])
    txt(c, l1, 0, -30, 50, C['paper'], "Anton"); txt(c, l2, 0, 30, 50, C['paper'], "Anton")
    rrect(c, -110, 80, 220, 54, 12); c.set_source_rgba(1, 1, 1, 0.25); c.fill(); txt(c, l3, 0, 117, 26, C['paper'])
    c.restore()

# ---------------- personaje TEO ----------------
# Teo: pelo oscuro despeinado, sudadera azul petróleo, pantalón gris, zapatillas claras, mochila opcional.
TEO = dict(top=C['teal'], top2=C['teal2'], legs=C['grey'], legs2=C['grey2'], shoe=C['cream'], skin=C['skin'], hair=C['hair'])
MARTA = dict(top=hexc('#D59A2A'), top2=hexc('#B07A1A'), legs=hexc('#3C4658'), legs2=hexc('#2E3646'), shoe=C['paper'], skin=hexc('#E8C3A0'), hair=hexc('#6B4A32'), bun=True)
IKER = dict(top=hexc('#C8372D'), top2=hexc('#9E2A22'), legs=hexc('#3A3D44'), legs2=hexc('#2B2E34'), shoe=hexc('#2B2A2F'), skin=hexc('#D9A97F'), hair=hexc('#1E1A18'))

def _limb(c, x, y, a1, l1, a2, l2, w, col, col2):
    x1 = x+math.sin(a1)*l1; y1 = y+math.cos(a1)*l1
    x2 = x1+math.sin(a1+a2)*l2; y2 = y1+math.cos(a1+a2)*l2
    for lw, cc in ((w+2*OL, OUT), (w, col)):
        c.set_source_rgb(*cc); c.set_line_width(lw); c.move_to(x, y); c.line_to(x1, y1); c.line_to(x2, y2); c.stroke()
    return x2, y2, a1+a2

POSE = {  # (cadera, muslo_i, rodilla_i, muslo_d, rodilla_d, brazo_i, codo_i, brazo_d, codo_d) · ángulo + = hacia delante
    "stand": (0, 0.06, 0, -0.06, 0, 0.12, 0.1, -0.12, 0.1),
    "reach": (0.05, 0.08, 0, -0.04, 0, -0.1, 0.15, 1.35, 0.15),
    "carry": (0.04, 0.06, 0, -0.06, 0, 0.55, 1.0, 0.65, 0.9),
    "think": (0, 0.05, 0, -0.05, 0, 0.12, 0.1, 0.35, 2.45),
    "phone": (0.02, 0.05, 0, -0.05, 0, 0.12, 0.1, 0.9, 1.6),
    "sit":   (0.0, 1.5, -1.5, 1.45, -1.45, 0.4, 0.6, 0.5, 0.5),
    "alarm": (-0.05, 0.12, 0, -0.12, 0, 2.4, 0.3, -2.4, -0.3),
    "listen": (-0.06, 0.06, 0, -0.08, 0, 0.12, 0.1, 0.3, 2.5),
}

def teo(c, x, y, h=520, pose="stand", t=0.0, face=1, walk=0.0, expr="neutral", look=(0, 0), bag=False, shadow=True, lit=1.0, who=None):
    T = who or TEO
    """x,y = pies. h = altura total. walk = fase (>0 anda). face=1 mira a la derecha. lit<1 oscurece (siluetas)."""
    P = list(POSE.get(pose, POSE["stand"]))
    if walk:
        s = math.sin(walk*2*math.pi)
        P[1] = 0.45*s; P[3] = -0.45*s; P[2] = max(0, -0.6*s); P[4] = max(0, 0.6*s)
        if pose == "stand": P[5] = -0.4*s; P[7] = 0.4*s
    u = h/520
    bob = abs(math.sin(walk*2*math.pi))*6*u if walk else math.sin(t*2.1)*2*u
    def col(cc): return mix(cc, C['night1'], 1-lit)
    if shadow:
        c.save(); c.translate(x, y); c.scale(1, 0.18); circle(c, 0, 0, 120*u); c.restore(); c.set_source_rgba(0, 0, 0, 0.22*lit); c.fill()
    c.save(); c.translate(x, y); c.scale(face, 1)
    hip = (0, -240*u+bob*0+(-60*u if pose == "sit" else 0))
    leg = 120*u; lw = 30*u
    for (a, b) in ((P[3], P[4]), (P[1], P[2])):
        ex, ey, ang = _limb(c, hip[0], hip[1]-bob, -a if False else a, leg, b, leg, lw, col(T['legs']), None)
        c.save(); c.translate(ex, ey); c.rotate(-ang*0.3); rrect(c, -16*u, -10*u, 56*u, 24*u, 10*u); fs(c, col(T['shoe']), OL); c.restore()
    # torso
    ty = hip[1]-bob; sh = ty-170*u
    c.save(); c.translate(0, ty); c.rotate(P[0])
    if bag: rrect(c, -78*u, -165*u, 50*u, 130*u, 14*u); fs(c, col(C['wood2']))
    c.new_path(); c.move_to(-46*u, 10*u); c.curve_to(-52*u, -80*u, -50*u, -150*u, -32*u, -175*u); c.line_to(32*u, -175*u)
    c.curve_to(50*u, -150*u, 52*u, -80*u, 46*u, 10*u); c.close_path(); fs(c, col(T['top']))
    c.set_source_rgb(*col(T['top2'])); c.set_line_width(5*u); c.move_to(-30*u, -20*u); c.line_to(30*u, -20*u); c.stroke()  # bolsillo
    c.restore()
    # brazos (de hombro)
    for (a, b, back_) in ((P[7], P[8], True), (P[5], P[6], False)):
        ex, ey, _ = _limb(c, 0, sh+8*u, a, 95*u, b, 90*u, 24*u, col(T['top2'] if back_ else T['top']), None)
        circle(c, ex, ey, 15*u); fs(c, col(T['skin']), OL)
    # cabeza
    hx, hy = 4*u+look[0]*4*u, sh-62*u+look[1]*4*u
    rrect(c, -12*u, sh-30*u, 24*u, 34*u, 6*u); fs(c, col(T['skin']), OL)
    circle(c, hx, hy, 58*u); fs(c, col(T['skin']), OL)
    # pelo despeinado (cubre coronilla y nuca)
    c.new_path(); c.move_to(hx-60*u, hy+14*u); c.curve_to(hx-74*u, hy-60*u, hx-20*u, hy-84*u, hx+22*u, hy-78*u)
    c.curve_to(hx+58*u, hy-72*u, hx+70*u, hy-40*u, hx+58*u, hy-22*u)
    for i, (dx, dy) in enumerate(((40, -30), (30, -44), (14, -30), (0, -46), (-16, -28), (-30, -40), (-38, -6))):
        c.line_to(hx+dx*u, hy+dy*u)
    c.line_to(hx-44*u, hy+20*u); c.close_path(); fs(c, col(T['hair']), OL)
    # oreja
    circle(c, hx-14*u, hy+8*u, 12*u); fs(c, col(C['skin2']), OL-1)
    if T.get('bun'):
        circle(c, hx-46*u, hy-40*u, 26*u); fs(c, col(T['hair']), OL)
    # cara (perfil 3/4 hacia +x)
    ex_ = hx+24*u+look[0]*6*u; ey_ = hy+2*u+look[1]*6*u
    c.set_source_rgb(*col(OUT))
    if expr == "shock": circle(c, ex_, ey_, 7*u); c.fill(); circle(c, ex_+24*u, ey_, 6*u); c.fill()
    elif expr == "sleep": c.set_line_width(4*u); c.move_to(ex_-6*u, ey_); c.line_to(ex_+6*u, ey_); c.stroke()
    else: circle(c, ex_, ey_, 5.5*u); c.fill(); circle(c, ex_+24*u, ey_, 5*u); c.fill()
    c.set_line_width(4*u)
    c.move_to(hx+56*u, ey_+2*u); c.line_to(hx+64*u, ey_+14*u); c.line_to(hx+55*u, ey_+16*u); c.stroke()
    brow = {"worried": (6, -4), "angry": (-6, 6), "shock": (-10, -10), "focus": (-3, 3)}.get(expr, (0, 0))
    c.move_to(ex_-10*u, ey_-16*u+brow[0]*u*0.6); c.line_to(ex_+8*u, ey_-16*u+brow[1]*u*0.6); c.stroke()
    if expr == "shock": circle(c, ex_+12*u, ey_+26*u, 7*u); c.fill()
    elif expr in ("worried", "focus"): c.move_to(ex_+4*u, ey_+28*u); c.line_to(ex_+20*u, ey_+26*u); c.stroke()
    else: c.move_to(ex_+2*u, ey_+26*u); c.curve_to(ex_+8*u, ey_+30*u, ex_+16*u, ey_+30*u, ex_+22*u, ey_+25*u); c.stroke()
    c.restore()

def silhouette(c, x, y, h, t=0):
    """figura desconocida a contraluz"""
    u = h/520; c.save(); c.translate(x, y); c.set_source_rgb(0.06, 0.06, 0.08)
    for dx in (-26, 26): rrect(c, dx*u-14*u, -250*u, 28*u, 250*u, 12*u); c.fill()
    c.new_path(); c.move_to(-60*u, -230*u); c.curve_to(-70*u, -330*u, -60*u, -420*u, -40*u, -440*u); c.line_to(40*u, -440*u)
    c.curve_to(60*u, -420*u, 70*u, -330*u, 60*u, -230*u); c.close_path(); c.fill()
    circle(c, 0, -500*u, 56*u); c.fill(); c.restore()

# ---------------- decorados ----------------
def wall_room(c, wall=None, floor_y=1260, night=0.0):
    wall = wall or C['wall']
    grad_bg(c, mix(tint(wall, 0.08), C['night2'], night), mix(shade(wall, 0.08), C['night1'], night))
    c.rectangle(0, floor_y, W, H-floor_y); c.set_source_rgb(*mix(C['floor'], C['night1'], night*0.85)); c.fill()
    for i in range(9):  # tablas
        c.set_source_rgba(0, 0, 0, 0.12); c.set_line_width(3); c.move_to(0, floor_y+40+i*i*14); c.line_to(W, floor_y+40+i*i*14); c.stroke()
    c.rectangle(0, floor_y-26, W, 26); c.set_source_rgb(*mix(C['wood2'], C['night1'], night*0.85)); c.fill()

def window_city(c, x, y, w, h, t, night=0.0, lights_out=0.0):
    """ventana con ciudad de fondo; night 0..1; lights_out apaga ventanas de los edificios"""
    rrect(c, x-14, y-14, w+28, h+28, 6); fs(c, mix(C['cream'], C['night2'], night*0.7), OL)
    c.save(); rrect(c, x, y, w, h, 2); c.clip()
    grad_bg(c, mix(C['sky'], C['dusk1'], night), mix(C['sky2'], C['dusk2'] if night < 0.9 else C['night2'], night), y, y+h)
    r = random.Random(4)
    for layer, (k, base) in enumerate(((0.55, 0.75), (0.8, 0.92))):
        xx = x-20
        while xx < x+w:
            bw = r.uniform(60, 120); bh = r.uniform(0.25, 0.6)*h*k*1.6
            bc = mix(mix(C['steel2'], C['steel'], layer*0.4), C['night1'], night*0.8)
            c.rectangle(xx, y+h*base-bh+h*0.1, bw-6, bh+h); c.set_source_rgb(*bc); c.fill()
            for wy in range(int(y+h*base-bh+h*0.1)+14, int(y+h), 26):
                for wx in range(int(xx)+10, int(xx+bw-16), 22):
                    on = r.random() < 0.55
                    if night > 0.3 and on and r.random() > lights_out:
                        c.rectangle(wx, wy, 10, 12); c.set_source_rgba(1, 0.86, 0.5, night); c.fill()
            xx += bw
    c.restore()
    c.set_source_rgb(*mix(C['cream'], C['night2'], night*0.7)); c.set_line_width(12)
    c.move_to(x+w/2, y); c.line_to(x+w/2, y+h); c.move_to(x, y+h*0.45); c.line_to(x+w, y+h*0.45); c.stroke()

def ceiling_lamp(c, x, y, on=1.0):
    c.set_source_rgb(*OUT); c.set_line_width(4); c.move_to(x, 0); c.line_to(x, y); c.stroke()
    c.new_path(); c.move_to(x-70, y+60); c.line_to(x-30, y); c.line_to(x+30, y); c.line_to(x+70, y+60); c.close_path(); fs(c, C['dark2'])
    if on > 0:
        g = cairo.RadialGradient(x, y+60, 10, x, y+60, 700); g.add_color_stop_rgba(0, 1, 0.92, 0.7, 0.35*on); g.add_color_stop_rgba(1, 1, 0.9, 0.7, 0)
        c.set_source(g); c.paint()
        c.save(); c.translate(x, y+60); c.scale(1, 0.3); circle(c, 0, 0, 60); c.restore(); c.set_source_rgba(1, 0.95, 0.75, on); c.fill()

def counter_kitchen(c, y=900, night=0.0, sink_x=640):
    m = lambda cc: mix(cc, C['night1'], night*0.75)
    # muebles altos
    for i in range(3): box(c, 60+i*150, 330, 140, 250, m(C['wood']), 4)
    for i in range(3): circle(c, 110+i*150, 560, 6); fs(c, m(C['dark']), 0)
    # estante con botes
    box(c, 40, 640, 420, 18, m(C['wood2']), 2)
    for i, cc in enumerate((C['leaf'], C['gold'], C['red2'], C['cream'], C['water'])):
        box(c, 60+i*78, 580, 56, 60, m(cc), 10, 3)
    # encimera y armarios bajos
    box(c, -10, y, W+20, 40, m(C['tile']), 4)
    for i in range(5): box(c, 10+i*215, y+40, 205, 320, m(C['wood']), 4, 3)
    # fregadero
    box(c, sink_x-150, y-6, 300, 22, m(C['steel2']), 6, 3)
    c.set_source_rgb(*m(C['steel'])); c.set_line_width(22)
    c.move_to(sink_x+90, y); c.line_to(sink_x+90, y-150); c.curve_to(sink_x+90, y-210, sink_x-10, y-210, sink_x-10, y-150); c.stroke()
    c.set_source_rgb(*OUT); c.set_line_width(4); c.move_to(sink_x-24, y-150); c.line_to(sink_x+4, y-150); c.stroke()

def water_stream(c, x, y0, y1, t, k=1.0, drip=False):
    if drip:
        ph = (t*1.3) % 1
        circle(c, x, lerp(y0, y1, ph**2), 8); fs(c, C['water'], 2); return
    if k <= 0: return
    w = 14*k
    c.new_path(); c.move_to(x-w/2, y0)
    for i in range(11):
        yy = lerp(y0, y1, i/10); c.line_to(x-w/2+math.sin(t*20+i)*2*k, yy)
    for i in range(10, -1, -1):
        yy = lerp(y0, y1, i/10); c.line_to(x+w/2+math.sin(t*20+i+1)*2*k, yy)
    c.close_path(); c.set_source_rgba(*C['water'], 0.9); c.fill()

def bottle(c, x, base, s=1, fill=1.0, col=None):
    col = col or C['glass']
    c.save(); c.translate(x, base); c.scale(s, s)
    c.new_path(); c.move_to(-26, 0); c.line_to(-26, -110); c.curve_to(-26, -130, -10, -140, -10, -160); c.line_to(10, -160); c.curve_to(10, -140, 26, -130, 26, -110); c.line_to(26, 0); c.close_path()
    fs(c, tint(col, 0.3), 3)
    if fill > 0:
        c.save(); c.rectangle(-30, -110*fill, 60, 120*fill); c.clip()
        c.new_path(); c.move_to(-26, 0); c.line_to(-26, -110); c.line_to(26, -110); c.line_to(26, 0); c.close_path(); fs(c, C['water'], 0, 0.85); c.restore()
    box(c, -12, -176, 24, 18, C['teal'], 4, 3)
    c.restore()

def pot(c, x, base, s=1, fill=1.0):
    c.save(); c.translate(x, base); c.scale(s, s)
    rrect(c, -90, -110, 180, 110, 14); fs(c, C['steel'])
    if fill > 0: c.rectangle(-84, -100*fill+4, 168, 6); c.set_source_rgb(*C['water']); c.fill()
    for sx in (-1, 1): rrect(c, sx*90-(20 if sx > 0 else -0)-(0 if sx > 0 else 20), -90, 20, 16, 6); fs(c, C['dark'], 3)
    c.restore()

def bathtub(c, x, base, fill=0.0, t=0):
    box(c, x-330, base-230, 660, 230, C['paper'], 60)
    if fill > 0:
        c.save(); rrect(c, x-310, base-210, 620, 200, 50); c.clip()
        yy = base-10-190*fill
        c.new_path(); c.move_to(x-320, yy)
        for i in range(21): c.line_to(x-320+i*32, yy+math.sin(t*3+i*0.8)*4)
        c.line_to(x+320, base); c.line_to(x-320, base); c.close_path(); c.set_source_rgba(*C['water'], 0.85); c.fill()
        c.restore()
    for sx in (-260, 260): box(c, x+sx-20, base-4, 40, 30, C['steel2'], 8, 3)
    c.set_source_rgb(*C['steel']); c.set_line_width(18); c.move_to(x+250, base-230); c.line_to(x+250, base-300); c.line_to(x+190, base-300); c.stroke()

def tiles(c, y0, y1, col=None):
    col = col or C['tile']; c.rectangle(0, y0, W, y1-y0); c.set_source_rgb(*col); c.fill()
    c.set_source_rgba(0, 0, 0, 0.08); c.set_line_width(3)
    for y in range(int(y0), int(y1), 90): c.move_to(0, y); c.line_to(W, y)
    for i, y in enumerate(range(int(y0), int(y1), 90)):
        for x in range(-45*(i % 2), W, 90): c.move_to(x, y); c.line_to(x, y+90)
    c.stroke()

def fridge(c, x, base, open_=0.0, night=0.0):
    m = lambda cc: mix(cc, C['night1'], night*0.6)
    box(c, x-170, base-760, 340, 760, m(C['paper']), 26)
    c.set_source_rgb(*OUT); c.set_line_width(4); c.move_to(x-170, base-500); c.line_to(x+170, base-500); c.stroke()
    for yy in (base-640, base-360): box(c, x+120, yy, 18, 110, m(C['steel2']), 8, 3)
    if open_ > 0:
        c.save(); rrect(c, x-160, base-490, 320, 480, 10); c.clip()
        c.set_source_rgba(1, 0.97, 0.85, 0.9*open_); c.paint(); c.restore()

def door(c, x, base, w=300, h=720, open_=0.0, light=0.0, night=0.0, knock=0.0, t=0):
    m = lambda cc: mix(cc, C['night1'], night*0.7)
    box(c, x-w/2-24, base-h-24, w+48, h+24, m(C['wood2']), 4)
    if light > 0:
        c.rectangle(x-w/2, base-h, w, h); c.set_source_rgba(1, 0.93, 0.75, light); c.fill()
    sx = x-w/2; ww = w*(1-0.85*open_)
    dx = math.sin(t*60)*4*knock
    box(c, sx+dx, base-h, ww, h, m(C['wood']), 3)
    for yy in (base-h+60, base-h+400):
        if ww > 80: box(c, sx+dx+30, yy, ww-60, 260, m(shade(C['wood'], 0.06)), 4, 3)
    circle(c, sx+dx+ww-40, base-h/2, 14); fs(c, m(C['gold']), 3)
    circle(c, sx+dx+ww/2, base-h+170, 10); fs(c, m(C['dark']), 3)  # mirilla
    if light > 0:  # rendija de luz bajo la puerta
        g = cairo.LinearGradient(0, base, 0, base+260); g.add_color_stop_rgba(0, 1, 0.92, 0.7, 0.7*light); g.add_color_stop_rgba(1, 1, 0.92, 0.7, 0)
        c.new_path(); c.move_to(x-w/2, base); c.line_to(x+w/2, base); c.line_to(x+w/2+200, base+260); c.line_to(x-w/2-200, base+260); c.close_path(); c.set_source(g); c.fill()

def knock_marks(c, x, y, t, n=3):
    for i in range(n):
        k = pop((t % 1.4)-i*0.18, 0.2)
        if 0 < k:
            c.save(); c.translate(x+(i-1)*70, y-i*36); c.rotate((i-1)*0.15); c.scale(k, k)
            txt(c, "TOC", 0, 0, 54, C['paper'], "Anton"); c.restore()

def building_section(c, x, base, floors=10, fh=78, w=520, t=0, lit_floor=8, water=1.0, power=True, pump_k=1.0):
    """corte de un edificio: plantas, tubería, grupo de presión en el sótano, agua que sube"""
    top = base-floors*fh
    box(c, x-w/2, top, w, floors*fh, C['wall2'], 4)
    c.new_path(); c.move_to(x-w/2-30, top); c.line_to(x, top-90); c.line_to(x+w/2+30, top); c.close_path(); fs(c, C['wood2'])
    for f in range(floors):
        y = base-(f+1)*fh
        c.set_source_rgba(0, 0, 0, 0.25); c.set_line_width(3); c.move_to(x-w/2, y); c.line_to(x+w/2, y); c.stroke()
        txt(c, f"{f+1}º" if f else "1º", x-w/2+40, y+fh*0.66, 26, C['grey'])
        if f+1 == lit_floor:
            c.rectangle(x-w/2+3, y+3, w-6, fh-6); c.set_source_rgba(*C['gold'], 0.35); c.fill()
    # sótano + bomba
    box(c, x-w/2, base, w, 150, C['grey2'], 4)
    px = x+w/2-110
    box(c, px-60, base+40, 120, 80, C['red'] if power else C['steel2'], 10)
    if power:
        a = t*12*pump_k; c.set_source_rgb(*C['paper']); c.set_line_width(5)
        c.move_to(px+math.cos(a)*24, base+80+math.sin(a)*24); c.line_to(px-math.cos(a)*24, base+80-math.sin(a)*24); c.stroke()
    # tubería
    pxp = x+w/2-60
    c.set_source_rgb(*C['steel2']); c.set_line_width(22); c.move_to(px+60, base+80); c.line_to(pxp+20, base+80); c.line_to(pxp+20, top+20); c.stroke()
    lvl = clamp(water)
    if lvl > 0:
        c.set_source_rgb(*C['water']); c.set_line_width(12)
        yy = base+80-(base+80-top-20)*lvl
        c.move_to(px+60, base+80); c.line_to(pxp+20, base+80); c.line_to(pxp+20, yy); c.stroke()
        # gotas que suben
        if power:
            for i in range(6):
                ph = (t*0.8+i/6) % 1; dy = lerp(base+80, yy, ph)
                circle(c, pxp+20, dy, 5); c.set_source_rgb(*C['paper']); c.fill()
    return top

def mini_map(c, cx, cy, s, t, rings=(), pin=True):
    """vista cenital de manzanas con radios"""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    r = random.Random(2)
    rrect(c, -480, -480, 960, 960, 30); fs(c, hexc("#C9C2B1"), 0)
    for i in range(-4, 5):
        for j in range(-4, 5):
            if (i, j) == (0, 0): continue
            box(c, i*105-40, j*105-40, 80+r.uniform(-10, 10), 80+r.uniform(-10, 10), mix(C['wall2'], C['steel'], r.random()*0.5), 4, 2)
    box(c, -46, -46, 92, 92, C['gold'], 4, 3)
    for k, (rad, lab) in enumerate(rings):
        kk = eout(t*1.2-k*0.3)
        if kk <= 0: continue
        c.set_source_rgba(*C['paper'], 0.9); c.set_line_width(4); c.set_dash([14, 10]); circle(c, 0, 0, rad*kk); c.stroke(); c.set_dash([])
        chip(c, lab, rad*0.72*kk, -rad*0.72*kk, t*1.2-k*0.3, size=26)
    c.restore()
