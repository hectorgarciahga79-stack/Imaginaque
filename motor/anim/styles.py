"""Extra visual styles for ImaginaQue: STICKMAN (paper + ink), MAPA (infographic/simulation), PIZARRA (whiteboard drawn live)."""
from engine import *

# ---------------------------------------------------------------- STICKMAN
PAPER = hexc("#F7F3EA"); INKB = hexc("#1E1E24"); ACC = hexc("#E63946"); ACC2 = hexc("#1D7AF2")

def paper_bg(c, grid=True, tint=None):
    c.set_source_rgb(*(tint or PAPER)); c.paint()
    if grid:
        c.set_source_rgba(0.2, 0.3, 0.5, 0.07); c.set_line_width(2)
        for x in range(0, W, 60): c.move_to(x, 0); c.line_to(x, H)
        for y in range(0, H, 60): c.move_to(0, y); c.line_to(W, y)
        c.stroke()

def _seg(c, x, y, ang, L):
    x2, y2 = x+math.sin(ang)*L, y+math.cos(ang)*L
    c.move_to(x, y); c.line_to(x2, y2); return x2, y2

POSES = {  # (hip_bend, l_thigh, l_shin, r_thigh, r_shin, l_arm, l_fore, r_arm, r_fore) angles in rad (0 = straight down)
    "stand": (0, 0.12, 0, -0.12, 0, 0.25, 0.1, -0.25, -0.1),
    "cheer": (0, 0.15, 0, -0.15, 0, 2.6, 0.2, -2.6, -0.2),
    "scared": (0.05, 0.25, -0.2, -0.25, 0.2, 2.2, 1.2, -2.2, -1.2),
    "think": (0, 0.1, 0, -0.1, 0, 0.3, 0.1, -2.4, -2.9),
    "sit": (0, 1.45, -1.5, 1.35, -1.45, 0.5, 0.9, -0.5, -0.9),
    "crouch": (0.15, 1.0, -1.4, 0.8, -1.3, 0.6, 1.2, -0.6, -1.2),
    "point": (0, 0.12, 0, -0.12, 0, 0.25, 0.1, -1.6, -1.6),
    "lookdown": (0.25, 0.1, 0, -0.1, 0, 0.5, 0.3, -0.5, -0.3),
    "shrug": (0, 0.12, 0, -0.12, 0, 1.0, 2.3, -1.0, -2.3),
}

def stick(c, x, y, h, pose="stand", t=0.0, phase=None, run=False, face="neutral", col=None, rot=0.0, lw=None, buckle=0.0):
    """Feet baseline at (x, y); total height h. phase -> walk/run cycle. buckle 0..1 bends knees under load."""
    col = col or INKB
    P = list(POSES.get(pose, POSES["stand"]))
    if phase is not None:
        a = math.sin(phase*2*math.pi); amp = 0.75 if run else 0.45
        P[1], P[3] = a*amp, -a*amp; P[2], P[4] = -max(0, -a)*0.9, -max(0, a)*0.9
        P[5], P[7] = -a*amp*1.2+0.1, a*amp*1.2-0.1; P[6], P[8] = -0.6 if run else -0.2, 0.6 if run else 0.2
        if run: P[0] = 0.18
    if buckle > 0:
        P[1] = 0.35+buckle*0.9; P[2] = -0.7-buckle*1.4; P[3] = -0.35-buckle*0.9; P[4] = 0.7+buckle*1.4
    lw = lw or max(3, h*0.045)
    c.save(); c.translate(x, y); c.rotate(rot)
    leg = h*0.46; th, sh = leg*0.5, leg*0.5
    hip_y = -leg*(0.55+0.45*math.cos(abs(P[1])*0.5))*(1-buckle*0.25) if pose in ("sit", "crouch") or buckle else -leg
    body = h*0.32; arm = h*0.3; head_r = h*0.11
    c.set_source_rgb(*col); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    # legs
    for th_a, sh_a in ((P[1], P[2]), (P[3], P[4])):
        kx, ky = _seg(c, 0, hip_y, th_a, th); _seg(c, kx, ky, th_a+sh_a, sh)
    # torso
    nx, ny = math.sin(P[0]+math.pi)*body*-1, hip_y-math.cos(P[0])*body
    c.move_to(0, hip_y); c.line_to(nx, ny)
    sx, sy = nx-math.sin(P[0])*body*-0.12, ny+body*0.12
    for ua, fa in ((P[5], P[6]), (P[7], P[8])):
        ex, ey = _seg(c, sx, sy, ua, arm*0.5); _seg(c, ex, ey, ua+fa, arm*0.5)
    c.stroke()
    # head
    hx, hy = nx+math.sin(P[0])*head_r, ny-head_r*1.15
    circle(c, hx, hy, head_r); c.set_source_rgb(*PAPER); c.fill_preserve(); c.set_source_rgb(*col); c.stroke()
    # face
    blink = (t % 3.3) < 0.12
    er = max(1.5, head_r*0.12)
    for dx in (-0.35, 0.35):
        if blink or face == "sleepy": c.move_to(hx+dx*head_r-er, hy-head_r*0.1); c.line_to(hx+dx*head_r+er, hy-head_r*0.1); c.set_line_width(lw*0.5); c.stroke()
        else:
            circle(c, hx+dx*head_r, hy-head_r*0.1, er*(1.8 if face in ("shock", "scared") else 1)); c.fill()
    c.set_line_width(lw*0.55)
    if face in ("shock", "scared"):
        circle(c, hx, hy+head_r*0.45, head_r*0.2); c.stroke()
    elif face == "happy":
        c.new_path(); c.arc(hx, hy+head_r*0.15, head_r*0.4, 0.3, math.pi-0.3); c.stroke()
    elif face == "worried":
        c.new_path(); c.arc(hx, hy+head_r*0.75, head_r*0.35, math.pi+0.4, 2*math.pi-0.4); c.stroke()
    else:
        c.move_to(hx-head_r*0.3, hy+head_r*0.45); c.line_to(hx+head_r*0.3, hy+head_r*0.45); c.stroke()
    if face in ("worried", "scared"):
        c.set_source_rgb(*ACC2); c.new_path(); c.move_to(hx+head_r*1.05, hy-head_r*0.5)
        c.curve_to(hx+head_r*0.9, hy-head_r*0.1, hx+head_r*1.25, hy-head_r*0.1, hx+head_r*1.05, hy-head_r*0.5); c.fill()
    c.restore()
    return (x, y-h)

def ink_text(c, s, x, y, size=80, col=None, font="Anton", align="center", a=1):
    return text(c, s, x, y, size, col or INKB, font=font, align=align, outline=0, a=a)

def ink_label(c, s, x, y, t, size=64, col=None):
    k = back(t*3)
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3)); c.rotate(-0.03)
    c.select_font_face("Anton"); c.set_font_size(size)
    xb, yb, tw, th, _, _ = c.text_extents(s)
    rrect(c, -tw/2-26, -size*0.85, tw+52, size*1.25, 14); c.set_source_rgb(*(col or ACC)); c.fill()
    c.set_source_rgb(1, 1, 1); c.move_to(-tw/2-xb, size*0.2); c.show_text(s); c.restore()

def scribble_lines(c, x, y, w, n, seed, col=None, lw=4):
    r = random.Random(seed); c.set_source_rgb(*(col or INKB)); c.set_line_width(lw)
    for i in range(n):
        c.move_to(x+r.uniform(0, w), y+r.uniform(-10, 10)); c.rel_line_to(r.uniform(-40, 40), r.uniform(10, 40))
    c.stroke()

def ink_rect(c, x, y, w, h, lw=6, fill=None):
    c.rectangle(x, y, w, h)
    if fill: c.set_source_rgb(*fill); c.fill_preserve()
    c.set_source_rgb(*INKB); c.set_line_width(lw); c.stroke()

def tiny_car(c, x, y, s, col):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -40, -26, 80, 22, 6); c.set_source_rgb(*col); c.fill_preserve(); c.set_source_rgb(*INKB); c.set_line_width(3); c.stroke()
    for wx in (-22, 22): circle(c, wx, -4, 7); c.set_source_rgb(*INKB); c.fill()
    c.restore()

def ink_building(c, x, base, w, h, floors, k=1.0):
    ink_rect(c, x-w/2, base-h*k, w, h*k, 6, hexc("#DDE3EC"))
    fh = h/floors
    for f in range(floors):
        yy = base-(f+1)*fh
        if yy < base-h*k: break
        for j in range(3):
            c.rectangle(x-w/2+12+j*(w-24)/3, yy+fh*0.25, (w-24)/3-12, fh*0.45)
    c.set_source_rgb(*INKB); c.set_line_width(3); c.stroke()

def cloud_ink(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s); c.new_path()
    for dx, dy, r in ((-60, 10, 45), (-15, -20, 60), (45, -5, 50), (85, 15, 35)):
        c.new_sub_path(); c.arc(dx, dy, r, 0, 2*math.pi)
    c.set_source_rgb(1, 1, 1); c.fill_preserve(); c.set_source_rgb(*INKB); c.set_line_width(4/s); c.stroke(); c.restore()

# ---------------------------------------------------------------- MAPA
NAVY = hexc("#0B1D33"); NAVY2 = hexc("#12304F"); CYAN = hexc("#4CC9F0"); GOLD = hexc("#FFC845"); HOT = hexc("#FF5A5F")

def map_bg(c, t=0):
    grad_bg(c, NAVY, NAVY2)
    c.set_source_rgba(0.3, 0.8, 0.95, 0.08); c.set_line_width(2)
    for x in range(0, W, 80): c.move_to(x, 0); c.line_to(x, H)
    for y in range(0, H, 80): c.move_to(0, y); c.line_to(W, y)
    c.stroke()
    # scanning line
    y = (t*220) % H; c.set_source_rgba(0.3, 0.8, 0.95, 0.12); c.rectangle(0, y, W, 6); c.fill()

def hud_text(c, s, x, y, size=60, col=None, align="center", font="Anton", a=1):
    return text(c, s, x, y, size, col or CYAN, font=font, align=align, outline=0, a=a)

def counter(c, value, x, y, size, col=GOLD, suffix=""):
    s = f"{int(value):,}".replace(",", ".")+suffix
    hud_text(c, s, x, y, size, col)

def person_icon(c, x, y, s, col):
    circle(c, x, y-s*1.6, s*0.45); c.set_source_rgb(*col); c.fill()
    rrect(c, x-s*0.45, y-s*1.05, s*0.9, s*1.05, s*0.35); c.fill()

# rough outline of the Comunidad de Madrid (stylised, normalised -1..1, north up)
MADRID = [(0.05, -1.0), (0.32, -0.62), (0.52, -0.38), (0.78, -0.12), (0.92, 0.18), (0.70, 0.38), (0.58, 0.72), (0.30, 0.95),
          (0.05, 0.80), (-0.22, 0.88), (-0.48, 0.62), (-0.80, 0.55), (-0.95, 0.28), (-0.72, 0.02), (-0.55, -0.28), (-0.30, -0.55), (-0.12, -0.82)]

def madrid_shape(c, cx, cy, s, fill_k=0.0, t=0, col=CYAN):
    c.new_path()
    for i, (u, v) in enumerate(MADRID):
        (c.move_to if i == 0 else c.line_to)(cx+u*s, cy+v*s)
    c.close_path()
    c.set_source_rgba(*col, 0.12); c.fill_preserve(); c.set_source_rgb(*col); c.set_line_width(6); c.stroke()
    if fill_k > 0:
        c.save(); c.new_path()
        for i, (u, v) in enumerate(MADRID): (c.move_to if i == 0 else c.line_to)(cx+u*s, cy+v*s)
        c.close_path(); c.clip()
        r = random.Random(4); n = int(900*fill_k)
        for i in range(n):
            x = cx+r.uniform(-1, 1)*s; y = cy+r.uniform(-1, 1)*s
            circle(c, x, y, 5+r.random()*3); c.set_source_rgba(*GOLD, 0.85); c.fill()
        c.restore()

def bar(c, x, y, w, h, k, col, label, val):
    c.rectangle(x, y-h, w, h); c.set_source_rgba(1, 1, 1, 0.08); c.fill()
    c.rectangle(x, y-h*k, w, h*k); c.set_source_rgb(*col); c.fill()
    hud_text(c, label, x+w/2, y+70, 44, (1, 1, 1), font="Montserrat")
    hud_text(c, val, x+w/2, y-h*k-24, 64, col)

def world_dots(c, cx, cy, s, k=1.0, empty=0.0, t=0):
    r = random.Random(9)
    for i in range(700):
        a = r.random()*2*math.pi; d = math.sqrt(r.random())
        x = cx+math.cos(a)*d*s; y = cy+math.sin(a)*d*s*0.55
        on = r.random() < k*(1-empty)
        circle(c, x, y, 4); c.set_source_rgba(*(GOLD if on else (0.4, 0.55, 0.7)), 0.9 if on else 0.35); c.fill()

# ---------------------------------------------------------------- PIZARRA
BOARD = hexc("#FBFBF8"); MARK = hexc("#22252B"); MRED = hexc("#D62828"); MBLUE = hexc("#1D4ED8")

def board_bg(c):
    c.set_source_rgb(*BOARD); c.paint()
    g = cairo.RadialGradient(W/2, H/2, 200, W/2, H/2, H*0.8)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.10); c.set_source(g); c.paint()

def path_len(pts):
    return sum(math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1))

def draw_partial(c, pts, k, col=MARK, lw=8):
    """draw polyline pts up to fraction k; returns tip position"""
    if k <= 0 or len(pts) < 2: return None
    L = path_len(pts)*clamp(k); acc = 0
    c.set_source_rgb(*col); c.set_line_width(lw); c.move_to(*pts[0]); tip = pts[0]
    for i in range(len(pts)-1):
        d = math.dist(pts[i], pts[i+1])
        if acc+d >= L:
            f = (L-acc)/d if d else 0; tip = (pts[i][0]+(pts[i+1][0]-pts[i][0])*f, pts[i][1]+(pts[i+1][1]-pts[i][1])*f)
            c.line_to(*tip); break
        c.line_to(*pts[i+1]); acc += d; tip = pts[i+1]
    c.stroke(); return tip

def marker_hand(c, tip, t):
    if not tip: return
    x, y = tip; y += math.sin(t*20)*2
    c.save(); c.translate(x, y); c.rotate(-0.6)
    rrect(c, -10, -150, 20, 150, 8); c.set_source_rgb(0.15, 0.15, 0.18); c.fill()
    rrect(c, -12, -170, 24, 40, 8); c.set_source_rgb(*MRED); c.fill()
    c.new_path(); c.move_to(-10, 0); c.line_to(10, 0); c.line_to(0, 18); c.close_path(); c.set_source_rgb(*MARK); c.fill()
    c.restore()

def circle_pts(cx, cy, r, n=40, a0=0, a1=2*math.pi):
    return [(cx+math.cos(a0+(a1-a0)*i/n)*r, cy+math.sin(a0+(a1-a0)*i/n)*r) for i in range(n+1)]

def wobble(pts, amt=2, seed=1):
    r = random.Random(seed); return [(x+r.uniform(-amt, amt), y+r.uniform(-amt, amt)) for x, y in pts]

def hand_text(c, s, x, y, k, size=70, col=MARK, align="center", font="Anton"):
    n = int(len(s)*clamp(k))
    if n <= 0: return
    c.select_font_face(font); c.set_font_size(size)
    xb, yb, tw, th, _, _ = c.text_extents(s)
    ox = {"center": -tw/2-xb, "left": -xb}[align]
    c.move_to(x+ox, y); c.set_source_rgb(*col); c.show_text(s[:n])

def board_person(c, x, y, h, k=1.0, t=0, phase=None, pose="stand", face="neutral", col=MARK):
    """stick figure drawn with marker (fade-in as it 'draws')"""
    if k <= 0: return
    c.push_group(); stick(c, x, y, h, pose, t, phase=phase, face=face, col=col); pat = c.pop_group()
    c.save(); c.set_source(pat)
    # reveal from top to bottom
    c.rectangle(0, 0, W, y-h*1.2+h*1.4*clamp(k)); c.clip(); c.paint(); c.restore()

def sound_arcs(c, x, y, r0, n, col=MBLUE, lw=7, a=1.0, spread=0.7):
    c.set_line_width(lw); c.set_source_rgba(*col, a)
    for i in range(n):
        c.new_path(); c.arc(x, y, r0+i*26, -spread, spread); c.stroke()

def speech(c, x, y, s, txt, col=MARK, k=1.0):
    k = back(k*3)
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3)*s, max(k, 1e-3)*s)
    rrect(c, -150, -70, 300, 120, 40); c.set_source_rgb(1, 1, 1); c.fill_preserve(); c.set_source_rgb(*col); c.set_line_width(6); c.stroke()
    text(c, txt, 0, 18, 64, col, outline=0); c.restore()
