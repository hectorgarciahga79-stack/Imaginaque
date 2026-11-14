"""Tiny 2D cartoon engine on pycairo. Flat colors + thick outlines, 1080x1920."""
import cairo, math, random

W, H, FPS = 1080, 1920, 30
INK = (0.13, 0.12, 0.16)
LW = 7  # outline width

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

PAL = {k: hexc(v) for k, v in dict(
    skin="#F2C29B", skin_d="#D9A27A", hair="#3A2A22", hoodie="#F28C28", hoodie_d="#D16F12",
    jeans="#3C5A99", jeans_d="#2E477A", shoe="#FFFFFF", sole="#C9C9D1",
    sky="#8FD3FF", sky2="#D9F1FF", night="#0E1530", night2="#27325E",
    ground="#7CC36A", ground_d="#5FA552", road="#5B5F6B", walk="#B9BCC6",
    sea="#2E8BD6", sea_d="#1E6CB0", land="#58B05A", land_d="#3F8F45",
    white="#FFFFFF", yellow="#FFD23F", red="#E84A3F", paper="#FBF7EC", line="#9DC3E6",
    b1="#E9C46A", b2="#F4A261", b3="#8AB6D6", b4="#C7CEEA", b5="#B5838D", win="#FFF3B0",
    sand="#F2CF8B", sand_d="#E0B56A", snow="#EEF5FF", ice="#BFE3F5", money="#7BC67E",
).items()}

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(x):  # easeInOutCubic
    x = clamp(x); return 4*x*x*x if x < .5 else 1-((-2*x+2)**3)/2
def eout(x): x = clamp(x); return 1-(1-x)**3
def back(x):  # overshoot
    x = clamp(x); c1 = 1.70158; c3 = c1+1; return 1+c3*(x-1)**3+c1*(x-1)**2
def lerp(a, b, t): return a+(b-a)*t

def new_surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)
    return s, c

def fill_stroke(c, col, lw=LW, ink=INK, a=1):
    c.set_source_rgba(*col, a); c.fill_preserve()
    if lw: c.set_source_rgba(*ink, a); c.set_line_width(lw); c.stroke()
    else: c.new_path()

def rrect(c, x, y, w, h, r):
    r = min(r, w/2, h/2)
    c.new_sub_path(); c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi); c.close_path()

def circle(c, x, y, r): c.new_sub_path(); c.arc(x, y, r, 0, 2*math.pi)

def grad_bg(c, top, bot, y0=0, y1=H):
    g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
    c.set_source(g); c.paint()

def mix(a, b, t): return tuple(lerp(x, y, t) for x, y in zip(a, b))

# ---------- text ----------
def text(c, s, x, y, size=70, col=PAL['white'], font="Anton", align="center", outline=10, ink=INK, a=1, bold=False):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    xb, yb, tw, th, xa, ya = c.text_extents(s)
    ox = {"center": -tw/2-xb, "left": -xb, "right": -tw-xb}[align]
    c.move_to(x+ox, y); c.text_path(s)
    if outline:
        c.set_source_rgba(*ink, a); c.set_line_width(outline); c.stroke_preserve()
    c.set_source_rgba(*col, a); c.fill()
    return tw

def label_tag(c, s, x, y, size=46, bg=PAL['white'], fg=INK, a=1):
    c.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    xb, yb, tw, th, xa, ya = c.text_extents(s)
    pw, ph = tw+56, size*1.6
    c.save(); c.translate(x, y)
    rrect(c, -pw/2, -ph/2, pw, ph, ph/2); fill_stroke(c, bg, 6, a=a)
    c.move_to(-tw/2-xb, size*0.36); c.set_source_rgba(*fg, a); c.show_text(s); c.restore()

def burst_text(c, s, x, y, t, size=150, col=PAL['yellow'], rot=-0.12):
    """comic onomatopoeia popping in"""
    k = back(t*3)
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(max(k, 1e-3), max(k, 1e-3))
    # star burst
    c.new_path(); n = 14
    for i in range(n*2):
        r = (size*1.35 if i % 2 == 0 else size*0.95); ang = i*math.pi/n
        c.line_to(r*math.cos(ang)*1.25, r*math.sin(ang)*0.8)
    c.close_path(); fill_stroke(c, PAL['white'], 8)
    text(c, s, 0, size*0.35, size, col, outline=14)
    c.restore()

# ---------- notebook card (musikky-style) ----------
def notebook(c, x, y, w, h, lines, t, title=None, rot=-0.03):
    """lines: list of (text, color). Written progressively over t in [0,1]."""
    c.save(); c.translate(x, y); c.rotate(rot)
    k = eout(t*4)
    c.translate(0, (1-k)*300)
    c.set_source_rgba(0, 0, 0, .25); rrect(c, -w/2+14, -h/2+18, w, h, 20); c.fill()
    rrect(c, -w/2, -h/2, w, h, 20); fill_stroke(c, PAL['paper'], 6)
    c.set_source_rgba(*PAL['line'], .8); c.set_line_width(3)
    yy = -h/2+150
    while yy < h/2-20:
        c.move_to(-w/2+20, yy); c.line_to(w/2-20, yy); c.stroke(); yy += 92
    c.set_source_rgba(*PAL['red'], .7); c.set_line_width(4); c.move_to(-w/2+90, -h/2+10); c.line_to(-w/2+90, h/2-10); c.stroke()
    # rings
    for i in range(6):
        circle(c, -w/2+40+i*(w-80)/5, -h/2, 16); fill_stroke(c, PAL['sole'], 5)
    if title:
        text(c, title, -w/2+120, -h/2+120, 64, PAL['red'], font="Anton", align="left", outline=0)
    total = sum(len(s) for s, _ in lines); shown = int(total*clamp((t-0.12)/0.6))
    yy = -h/2+150+92*1-18
    for s, col in lines:
        n = min(len(s), shown); shown -= n
        if n > 0:
            c.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(58)
            c.move_to(-w/2+120, yy); c.set_source_rgb(*col); c.show_text(s[:n])
        yy += 92
    c.restore()

# ---------- character: "Leo" ----------
def leo(c, x, y, s=1.0, pose="stand", expr="neutral", t=0.0, facing=1, walk=0.0, hoodie=None, hair=None, skin=None, look=(0, 0), tilt=0.0):
    """Feet center at (x,y). Height ~ 560*s. pose: stand|phone|scared|point|sit|fly|cling|shrug|think
    expr: neutral|happy|shock|scared|worried|smirk|sleepy|angry"""
    P = dict(PAL)
    if hoodie: P['hoodie'] = hoodie; P['hoodie_d'] = mix(hoodie, (0, 0, 0), .2)
    if hair: P['hair'] = hair
    if skin: P['skin'] = skin
    c.save(); c.translate(x, y); c.scale(s*facing, s); c.rotate(tilt)
    bob = math.sin(t*2.2)*4 if pose not in ("fly",) else 0
    sw = math.sin(walk*math.pi*2)
    # legs
    def leg(dx, ang, col):
        c.save(); c.translate(dx, -215); c.rotate(ang)
        rrect(c, -30, 0, 60, 200, 26); fill_stroke(c, col)
        rrect(c, -36, 175, 92, 46, 22); fill_stroke(c, P['shoe'])
        c.restore()
    if pose == "sit":
        c.save(); c.translate(0, -130)
        rrect(c, -70, -40, 220, 70, 30); fill_stroke(c, P['jeans'])
        rrect(c, 120, -40, 70, 160, 30); fill_stroke(c, P['jeans'])
        rrect(c, 110, 100, 100, 46, 22); fill_stroke(c, P['shoe']); c.restore()
        by = -150
    elif pose == "fly":
        leg(-34, 0.9, P['jeans_d']); leg(30, 1.2, P['jeans']); by = -210
    else:
        leg(-34, sw*0.45, P['jeans_d']); leg(30, -sw*0.45, P['jeans']); by = -210
    by += bob
    # back arm
    def arm(sx, ang, col, hand=True, length=170):
        c.save(); c.translate(sx, by-170); c.rotate(ang)
        rrect(c, -28, -10, 56, length, 26); fill_stroke(c, col)
        if hand: circle(c, 0, length+4, 28); fill_stroke(c, P['skin'])
        c.restore()
    A = {  # (back arm angle, front arm angle)
        "stand": (0.12+sw*0.35, -0.12-sw*0.35), "phone": (0.15, -2.35), "scared": (2.6, -2.6),
        "point": (0.1, -1.55), "sit": (0.3, -0.5), "fly": (2.2, -2.0), "cling": (-2.4, -2.8),
        "shrug": (1.1, -1.1), "think": (0.15, -2.6), "cheer": (2.8, -2.8)}[pose]
    jit = math.sin(t*40)*0.06 if pose == "scared" else 0
    arm(-78, A[0]+jit, P['hoodie_d'])
    # torso (hoodie)
    rrect(c, -95, by-230, 190, 250, 60); fill_stroke(c, P['hoodie'])
    c.set_source_rgba(*P['hoodie_d'], 1); rrect(c, -55, by-80, 110, 60, 20); c.fill()  # pocket
    c.set_source_rgba(*INK, 1); c.set_line_width(5); c.move_to(-20, by-225); c.line_to(-26, by-150); c.move_to(20, by-225); c.line_to(26, by-150); c.stroke()
    # head
    hy = by-330
    c.save(); c.translate(0, hy)
    circle(c, 0, 0, 120); fill_stroke(c, P['skin'])
    circle(c, -118, 10, 26); fill_stroke(c, P['skin'])  # ear (back)
    # hair
    c.new_path(); c.move_to(-118, -10)
    c.curve_to(-140, -120, -40, -175, 40, -150); c.curve_to(110, -140, 140, -60, 122, -18)
    c.curve_to(95, -70, 60, -60, 30, -95); c.curve_to(10, -60, -40, -70, -70, -95)
    c.curve_to(-80, -50, -100, -40, -118, -10); c.close_path(); fill_stroke(c, P['hair'])
    # face
    lx, ly = look
    blink = (t % 3.7) < 0.12
    ey = -5
    for ex in (-38, 42):
        if expr == "sleepy" or blink:
            c.set_source_rgb(*INK); c.set_line_width(6); c.move_to(ex-20, ey); c.line_to(ex+20, ey); c.stroke()
        else:
            er = 30 if expr in ("shock", "scared") else 25
            circle(c, ex, ey, er); fill_stroke(c, PAL['white'], 5)
            pr = 9 if expr in ("shock", "scared") else 12
            circle(c, ex+8+lx*8, ey+2+ly*8, pr); c.set_source_rgb(*INK); c.fill()
    # brows
    bshape = {"neutral": (0, 0), "happy": (-4, 0), "shock": (-22, 0), "scared": (-16, 0.35), "worried": (-12, 0.4),
              "smirk": (-6, -0.25), "sleepy": (4, 0), "angry": (-4, -0.45)}[expr]
    c.set_source_rgb(*P['hair']); c.set_line_width(12)
    for i, ex in enumerate((-38, 42)):
        sgn = -1 if i == 0 else 1
        c.move_to(ex-24, ey-42+bshape[0]+sgn*bshape[1]*-24); c.line_to(ex+24, ey-42+bshape[0]-sgn*bshape[1]*-24); c.stroke()
    # nose
    c.set_source_rgb(*P['skin_d'] if 'skin_d' in P else PAL['skin_d']); circle(c, 8, 30, 12); c.fill()
    # mouth
    c.set_source_rgb(*INK); c.set_line_width(7)
    if expr in ("shock", "scared"):
        c.save(); c.translate(6, 72); c.scale(1, 1.3); circle(c, 0, 0, 20); c.restore(); fill_stroke(c, (0.55, 0.15, 0.18), 6)
    elif expr == "happy":
        c.new_path(); c.arc(6, 55, 32, 0.15, math.pi-0.15); c.close_path(); fill_stroke(c, (0.55, 0.15, 0.18), 6)
    elif expr == "worried":
        c.new_path(); c.move_to(-22, 78); c.curve_to(-5, 62, 15, 62, 32, 78); c.stroke()
    elif expr == "smirk":
        c.new_path(); c.move_to(-18, 68); c.curve_to(0, 78, 20, 72, 36, 56); c.stroke()
    elif expr == "angry":
        c.new_path(); c.move_to(-20, 74); c.line_to(32, 70); c.stroke()
    else:
        c.new_path(); c.move_to(-18, 66); c.curve_to(0, 76, 18, 76, 32, 64); c.stroke()
    if expr in ("worried", "scared"):  # sweat drop
        c.new_path(); c.move_to(110, -60); c.curve_to(95, -30, 100, -10, 112, -10); c.curve_to(124, -10, 128, -30, 110, -60); fill_stroke(c, PAL['ice'], 4)
    c.restore()
    # front arm (+ phone)
    if pose in ("phone", "think"):
        c.save(); c.translate(78, by-170); c.rotate(A[1]); rrect(c, -28, -10, 56, 150, 26); fill_stroke(c, P['hoodie'])
        c.restore()
        if pose == "phone":
            px, py = 78+math.sin(A[1])*-150, by-170+math.cos(A[1])*150
            rrect(c, px-34, py-70, 68, 120, 14); fill_stroke(c, (0.15, 0.15, 0.2), 5)
            rrect(c, px-26, py-60, 52, 96, 8); c.set_source_rgb(*PAL['sky']); c.fill()
            circle(c, px, py+8, 28); fill_stroke(c, P['skin'])
        else:
            circle(c, 30, by-260, 28); fill_stroke(c, P['skin'])
    else:
        arm(78, A[1]-jit, P['hoodie'])
    c.restore()

def leo_head(c, x, y, s, expr="neutral", t=0, look=(0, 0)):
    """big close-up head only (for reaction shots)."""
    c.save(); c.translate(x, y+330*s*0.0)
    leo(c, 0, 0, s, "stand", expr, t, look=look)
    c.restore()

# ---------- props / backgrounds ----------
def stars(c, n=120, seed=1, tw=0.0, a=1):
    r = random.Random(seed)
    for i in range(n):
        x, y, rr = r.random()*W, r.random()*H, r.random()*3+1
        al = a*(0.5+0.5*math.sin(tw*3+i))
        circle(c, x, y, rr); c.set_source_rgba(1, 1, 1, al); c.fill()

def globe(c, x, y, r, rot=0.0, night=0.0, spain_pin=False, terminator=None, oceans_to_poles=0.0):
    """rot: longitude shift in [0,1) per revolution. terminator: x-fraction where night starts (None=no)."""
    c.save(); c.translate(x, y)
    circle(c, 0, 0, r+10); c.set_source_rgba(0.5, 0.8, 1, 0.25); c.fill()  # atmosphere
    circle(c, 0, 0, r); c.set_source_rgb(*PAL['sea']); c.fill_preserve(); c.save(); c.clip()
    # continents as blobs that wrap
    conts = [(0.05, -0.35, 0.22, 0.30), (0.12, 0.25, 0.14, 0.32), (0.42, -0.30, 0.28, 0.22), (0.47, 0.15, 0.13, 0.30),
             (0.70, -0.30, 0.30, 0.25), (0.78, 0.35, 0.12, 0.12), (0.30, 0.0, 0.05, 0.05)]
    for (u, v, w_, h_) in conts:
        for k in (-1, 0, 1):
            uu = ((u - rot) % 1.0) + k
            cx = (uu-0.5)*2*r*1.6
            if abs(cx) > r*1.6: continue
            sq = math.cos(clamp(cx/(r*1.6), -1, 1)*math.pi/2)
            c.save(); c.translate(cx*0.62, v*r); c.scale(max(0.05, sq), 1)
            c.new_path(); seed = random.Random(int(u*1000))
            pts = 9
            for i in range(pts):
                a = i/pts*2*math.pi; rr = 1+0.25*seed.random()
                c.line_to(math.cos(a)*w_*r*rr, math.sin(a)*h_*r*rr)
            c.close_path(); c.set_source_rgb(*PAL['land']); c.fill_preserve(); c.set_source_rgb(*PAL['land_d']); c.set_line_width(4); c.stroke()
            c.restore()
    if oceans_to_poles > 0:
        k = oceans_to_poles
        c.set_source_rgba(*PAL['sand'], k); c.rectangle(-r, -r*0.45, 2*r, r*0.9); c.fill()
        c.set_source_rgba(*PAL['land'], k*0.8)
        for i in range(7):
            circle(c, -r+i*r/3, 0, r*0.18); c.fill()
        c.set_source_rgba(*PAL['sea'], k); c.rectangle(-r, -r, 2*r, r*0.55); c.fill(); c.rectangle(-r, r*0.45, 2*r, r*0.55); c.fill()
    # shading
    g = cairo.RadialGradient(-r*0.35, -r*0.35, r*0.1, 0, 0, r*1.05)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.18); g.add_color_stop_rgba(1, 0, 0, 0.1, 0.35)
    c.set_source(g); c.paint()
    if terminator is not None:
        c.set_source_rgba(0.02, 0.03, 0.12, 0.72); c.rectangle(terminator*r, -r, 2*r, 2*r); c.fill()
    if night > 0:
        c.set_source_rgba(0.02, 0.03, 0.12, night); c.paint()
    c.restore()
    circle(c, 0, 0, r); c.set_source_rgb(*INK); c.set_line_width(LW+2); c.stroke()
    if spain_pin:
        px, py = -r*0.05, -r*0.42
        c.new_path(); c.move_to(px, py); c.line_to(px-22, py-50); c.arc(px, py-62, 26, math.pi*0.85, math.pi*2.15); c.close_path()
        fill_stroke(c, PAL['red'], 5); circle(c, px, py-62, 9); c.set_source_rgb(1, 1, 1); c.fill()
    c.restore()

def speed_lines(c, t, n=26, dirx=1, col=(1, 1, 1), a=0.8, seed=3, y0=0, y1=H, length=420, speed=2600):
    r = random.Random(seed)
    c.set_line_width(8)
    for i in range(n):
        y = y0+r.random()*(y1-y0); off = r.random()*W*2
        x = ((off+t*speed) % (W+length*2))-length
        if dirx < 0: x = W-x
        c.set_source_rgba(*col, a*r.uniform(.4, 1))
        c.move_to(x, y); c.line_to(x-length*dirx*r.uniform(.4, 1), y); c.stroke()

def building(c, x, base, w, h, col, t=0, wind=0.0, roof_off=0.0, lit=0.0, seed=0):
    c.save(); c.translate(x, base); c.rotate(wind*0.03)
    rrect(c, -w/2, -h, w, h, 10); fill_stroke(c, col)
    r = random.Random(seed)
    cols = max(2, int(w/70)); rows = max(2, int(h/90))
    for i in range(cols):
        for j in range(rows):
            wx = -w/2+18+i*(w-36)/cols; wy = -h+24+j*(h-40)/rows
            ww = (w-36)/cols-16; wh = (h-40)/rows-26
            on = r.random() < 0.5
            rrect(c, wx, wy, ww, wh, 6); c.set_source_rgb(*(PAL['win'] if on and lit else mix(col, (1, 1, 1), .45))); c.fill()
    if roof_off < 1:
        c.save(); c.translate(roof_off*600, -roof_off*500); c.rotate(roof_off*2.5)
        c.new_path(); c.move_to(-w/2-12, -h); c.line_to(w/2+12, -h); c.line_to(w/2-8, -h-30); c.line_to(-w/2+8, -h-30); c.close_path()
        fill_stroke(c, mix(col, (0, 0, 0), .25), 6); c.restore()
    c.restore()

def city(c, base, t=0, wind=0.0, roof=0.0, lit=0.0, scale=1.0, dark=0.0):
    specs = [(80, 260, 520), (250, 220, 700), (420, 200, 420), (600, 240, 820), (800, 220, 560), (990, 240, 650)]
    cs = [PAL['b3'], PAL['b4'], PAL['b1'], PAL['b5'], PAL['b2'], PAL['b3']]
    for i, (x, w, h) in enumerate(specs):
        col = mix(cs[i], (0.1, 0.1, 0.2), dark)
        building(c, x, base, w*scale, h*scale, col, t, wind*math.sin(t*9+i), clamp(roof*1.4-i*0.12), lit, seed=i)

def ground(c, y, col=None, col2=None):
    col = col or PAL['ground']; col2 = col2 or PAL['ground_d']
    c.rectangle(-50, y, W+100, H-y+50); c.set_source_rgb(*col); c.fill()
    c.set_source_rgb(*col2); c.rectangle(-50, y, W+100, 18); c.fill()
    c.set_source_rgb(*INK); c.set_line_width(LW); c.move_to(-50, y); c.line_to(W+50, y); c.stroke()

def road(c, y, h=220, t=0, speed=0):
    c.rectangle(-50, y, W+100, h); c.set_source_rgb(*PAL['road']); c.fill()
    c.set_source_rgb(1, 1, 1); off = (t*speed) % 200
    for i in range(-1, 8):
        c.rectangle(i*200-off, y+h/2-8, 110, 16); c.fill()
    c.set_source_rgb(*INK); c.set_line_width(LW); c.move_to(-50, y); c.line_to(W+50, y); c.move_to(-50, y+h); c.line_to(W+50, y+h); c.stroke()

def car(c, x, y, s=1, col=None, rot=0.0, t=0):
    col = col or PAL['red']
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rrect(c, -150, -110, 300, 80, 26); fill_stroke(c, col)
    c.new_path(); c.move_to(-90, -110); c.line_to(-55, -175); c.line_to(60, -175); c.line_to(100, -110); c.close_path(); fill_stroke(c, col)
    c.new_path(); c.move_to(-70, -115); c.line_to(-45, -160); c.line_to(0, -160); c.line_to(0, -115); c.close_path(); fill_stroke(c, PAL['sky2'], 5)
    c.new_path(); c.move_to(14, -115); c.line_to(14, -160); c.line_to(52, -160); c.line_to(80, -115); c.close_path(); fill_stroke(c, PAL['sky2'], 5)
    for wx in (-85, 85):
        circle(c, wx, -30, 38); fill_stroke(c, (0.2, 0.2, 0.24)); circle(c, wx, -30, 14); c.set_source_rgb(.8, .8, .85); c.fill()
    c.restore()

def lamp(c, x, base, h=520):
    rrect(c, x-14, base-h, 28, h, 10); fill_stroke(c, (0.3, 0.32, 0.38))
    c.new_path(); c.move_to(x, base-h); c.curve_to(x, base-h-60, x+90, base-h-60, x+100, base-h-20); c.set_source_rgb(*INK); c.set_line_width(22); c.stroke()
    c.new_path(); c.move_to(x, base-h); c.curve_to(x, base-h-60, x+90, base-h-60, x+100, base-h-20); c.set_source_rgb(0.3, 0.32, 0.38); c.set_line_width(12); c.stroke()
    rrect(c, x+70, base-h-24, 60, 30, 10); fill_stroke(c, PAL['win'], 5)

def tree(c, x, base, s=1, bend=0.0, leaves=1.0):
    c.save(); c.translate(x, base); c.scale(s, s)
    c.new_path(); c.move_to(-20, 0); c.curve_to(-18, -120, -10+bend*80, -200, 0+bend*140, -260); c.line_to(30+bend*140, -255)
    c.curve_to(15+bend*80, -190, 20, -110, 22, 0); c.close_path(); fill_stroke(c, (0.55, 0.35, 0.22))
    if leaves > 0:
        for (dx, dy, r) in ((-60, -300, 90), (60, -310, 95), (0, -380, 100), (0, -260, 85)):
            circle(c, dx+bend*200, dy, r*leaves); fill_stroke(c, PAL['land'], 6)
    c.restore()

def wave(c, t, base, height, col=None, x_off=0, crest=True):
    col = col or PAL['sea']
    c.new_path(); c.move_to(-60, H+50); c.line_to(-60, base)
    for i in range(0, W+121, 30):
        x = i-60; y = base - height*(0.5+0.5*math.sin((x+x_off)/160 + t*3))*0.25
        c.line_to(x, y)
    if crest:
        c.line_to(W+60, base-height); c.curve_to(W-80, base-height*1.15, W-260, base-height*0.9, W-180, base-height*0.6)
    c.line_to(W+60, H+50); c.close_path(); fill_stroke(c, col)

def sun(c, x, y, r, t=0, col=None):
    col = col or PAL['yellow']
    c.save(); c.translate(x, y); c.rotate(t*0.4)
    c.set_line_width(14)
    for i in range(12):
        a = i*math.pi/6; c.move_to(math.cos(a)*(r+25), math.sin(a)*(r+25)); c.line_to(math.cos(a)*(r+70), math.sin(a)*(r+70))
    c.set_source_rgb(*INK); c.set_line_width(22); c.stroke_preserve(); c.set_source_rgb(*col); c.set_line_width(12); c.stroke()
    circle(c, 0, 0, r); fill_stroke(c, col); c.restore()

def moon(c, x, y, r):
    circle(c, x, y, r); fill_stroke(c, (0.95, 0.95, 0.85))
    circle(c, x+r*0.45, y-r*0.2, r*0.85); c.set_source_rgb(*PAL['night']); c.fill()

def gauge(c, x, y, r, val, vmax, label, t):
    c.save(); c.translate(x, y)
    circle(c, 0, 0, r); fill_stroke(c, PAL['white'], 8)
    c.set_line_width(26)
    for i, col in enumerate([PAL['land'], PAL['yellow'], PAL['red']]):
        c.new_path(); a0 = math.pi*0.75+i*math.pi*0.5; c.arc(0, 0, r-40, a0, a0+math.pi*0.5); c.set_source_rgb(*col); c.stroke()
    v = val*eout(t)
    ang = math.pi*0.75 + 1.5*math.pi*clamp(v/vmax)
    c.set_source_rgb(*INK); c.set_line_width(14); c.move_to(0, 0); c.line_to(math.cos(ang)*(r-60), math.sin(ang)*(r-60)); c.stroke()
    circle(c, 0, 0, 22); c.set_source_rgb(*INK); c.fill()
    text(c, f"{int(v):,}".replace(",", "."), 0, r*0.55, 96, PAL['red'], outline=10)
    text(c, label, 0, r*0.55+70, 48, INK, font="Montserrat", outline=0, bold=True)
    c.restore()

def phone_big(c, x, y, s, screen_fn, t=0, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rrect(c, -230, -440, 460, 880, 60); fill_stroke(c, (0.12, 0.12, 0.16), 9)
    rrect(c, -205, -410, 410, 820, 40); c.set_source_rgb(0.97, 0.97, 1); c.fill()
    c.save(); rrect(c, -205, -410, 410, 820, 40); c.clip(); screen_fn(c, t); c.restore()
    rrect(c, -60, -425, 120, 20, 10); c.set_source_rgb(0.12, 0.12, 0.16); c.fill()
    c.restore()

def shake(c, t, amp):
    if amp <= 0: return
    c.translate(math.sin(t*61)*amp, math.cos(t*47)*amp)

def vignette(c, a=0.35):
    g = cairo.RadialGradient(W/2, H/2, H*0.25, W/2, H/2, H*0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, a); c.set_source(g); c.paint()
