"""Estilo «cine» — vídeo independiente ¿Y SI…? Q1: ¿y si todos saltáramos al mar a la vez?"""
from engine import *
from cine import *
from cine import teo as _teo
from scenes_c4 import P, glow
import cairo, math, random

SKY1, SKY2 = hexc("#7EC8E3"), hexc("#FDE7C2")
SEA1, SEA2 = hexc("#2E86AB"), hexc("#155E80")
SAND = hexc("#F2D49B")
COLS = [C['red'], C['gold'], C['teal'], C['leaf'], hexc('#B5838D'), hexc('#5B6F9A'), hexc('#E07A5F')]

def mini(c, x, y, h, col, t=0.0, jump=0.0, arms=0.0):
    """personita simple: y = pies"""
    u = h/100.0; y = y-jump
    c.save(); c.translate(x, y)
    c.set_source_rgb(*shade(col, 0.25)); c.set_line_width(9*u); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(-8*u, 0); c.line_to(-4*u, -38*u); c.move_to(8*u, 0); c.line_to(4*u, -38*u); c.stroke()
    rrect(c, -15*u, -78*u, 30*u, 44*u, 12*u); c.set_source_rgb(*col); c.fill()
    c.set_source_rgb(*col); c.set_line_width(8*u)
    a = -2.3*arms
    for sx in (-1, 1):
        c.move_to(sx*13*u, -70*u); c.line_to(sx*13*u+sx*math.sin(0.4-a)*26*u, -70*u+math.cos(0.4-a)*26*u); c.stroke()
    circle(c, 0, -92*u, 14*u); c.set_source_rgb(*hexc('#F0D2B4')); c.fill()
    c.set_line_cap(cairo.LINE_CAP_BUTT); c.restore()

def sky(c, top=SKY1, bot=SKY2): grad_bg(c, top, bot)

def sea(c, y, t, amp=14, col1=SEA1, col2=SEA2):
    g = cairo.LinearGradient(0, y, 0, H); g.add_color_stop_rgb(0, *col1); g.add_color_stop_rgb(1, *col2)
    c.new_path(); c.move_to(0, H); c.line_to(0, y)
    for x in range(0, W+20, 20): c.line_to(x, y+amp*math.sin(x/90+t*2.2)+amp*0.5*math.sin(x/37-t*3))
    c.line_to(W, H); c.close_path(); c.set_source(g); c.fill()
    c.set_source_rgba(1, 1, 1, 0.5); c.set_line_width(5)
    for x in range(0, W, 20):
        yy = y+amp*math.sin(x/90+t*2.2)+amp*0.5*math.sin(x/37-t*3)
        if x == 0: c.move_to(x, yy)
        else: c.line_to(x, yy)
    c.stroke()

def splash(c, x, y, k, s=1.0):
    if k <= 0 or k >= 1: return
    for i in range(7):
        a = -math.pi/2+(i-3)*0.35; r = 90*s*k
        circle(c, x+math.cos(a)*r, y+math.sin(a)*r*1.3+k*k*60*s, 12*s*(1-k)+3); c.set_source_rgba(1, 1, 1, 0.85*(1-k)); c.fill()

def teo(*a, **k): return _teo(*a, **k)

# ---------------- escenas ----------------
def q1_0(c, lt, d, t):   # gancho: multitud saltando al mar
    k = ease(P(lt, d))
    c.save(); z = 1.0+0.25*k; c.translate(W/2, 1000); c.scale(z, z); c.translate(-W/2, -1000)
    sky(c); sun(c, 820, 420, 90, t)
    sea(c, 980, t)
    c.new_path(); c.move_to(0, 1180); c.curve_to(300, 1120, 600, 1200, W, 1150); c.line_to(W, H); c.line_to(0, H); c.close_path(); c.set_source_rgb(*SAND); c.fill()
    r = random.Random(3)
    for i in range(60):
        x = r.uniform(20, W-20); base = r.uniform(1190, 1560); ph = r.uniform(0, 1)
        jp = ((t*0.8+ph) % 1)
        jump = math.sin(jp*math.pi)*90 if jp < 0.6 else 0
        mini(c, x, base, r.uniform(70, 110), r.choice(COLS), t, jump, arms=1 if jump > 10 else 0)
    for i in range(6):
        ph = (t*0.7+i/6) % 1
        splash(c, 120+i*170, 1000, ph, 1.2)
    c.restore()
    if lt > d*0.45: chip(c, "¿CUÁNTO SUBE EL MAR?", W/2, 600, lt-d*0.45, ic_drop, size=40, bg=C['gold'])
    post(c, t, 0.35, 0.05)

def q1_1(c, lt, d, t):   # miles de millones, el chapuzón más grande
    sky(c, hexc("#9AD4EA"), SKY2)
    k = ease(P(lt, d))
    rows = 9
    for rr in range(rows):
        y = 700+rr*95; hh = 40+rr*8
        n = int(10+rr*3)
        for i in range(n):
            x = (i+0.5)*W/n+(rr % 2)*20
            mini(c, x, y, hh, COLS[(i+rr) % len(COLS)], t, abs(math.sin(t*3+i+rr))*12*k)
    font(c, 40)
    time_card(c, "PERSONAS", "MILES DE", "MILLONES", W/2, 380, lt-0.2, col=C['teal'])
    post(c, t, 0.3, 0.05)

def q1_2(c, lt, d, t):   # 287 millones de toneladas
    grad_bg(c, hexc("#1F3B57"), hexc("#0E1C2B"))
    k = ease(P(lt, d, 0, 0.5))
    # báscula
    box(c, 240, 1180, 600, 60, C['steel2'], 10)
    box(c, 520, 1060, 40, 120, C['steel'], 6)
    box(c, 200, 1000-40*math.sin(t*3)*(1-k), 680, 60, C['steel'], 12)
    for i in range(22):
        x = 240+(i % 11)*55; y = 990-(i//11)*95-40*math.sin(t*3)*(1-k)
        mini(c, x, y, 85, COLS[i % len(COLS)], t)
    stat_card(c, "ADULTOS DEL MUNDO", "287", "MILL. t", W/2, 520, lt-0.4, icon=ic_check, sub="ESTUDIO 2012")
    post(c, t, 0.4, 0.06)

def q1_3(c, lt, d, t):   # el cuerpo pesa casi como el agua
    grad_bg(c, hexc("#E9F4F8"), hexc("#CFE6EF"))
    k = ease(P(lt, d, 0.1, 0.7))
    # tanque
    box(c, 260, 560, 560, 760, hexc('#DDEEF5'), 16, 6)
    lvl = 1100-110*k
    c.rectangle(266, lvl, 548, 1314-lvl); c.set_source_rgba(*SEA1, 0.75); c.fill()
    c.set_source_rgb(*C['red2']); c.set_line_width(6); c.move_to(220, 1100); c.line_to(260, 1100); c.stroke()
    c.move_to(220, lvl); c.line_to(260, lvl); c.stroke()
    teo(c, 540, lerp(820, 1220, k), 420, "stand", t, face=1, expr="neutral", look=(0, -0.2))
    c.rectangle(266, lvl, 548, 1314-lvl); c.set_source_rgba(*SEA1, 0.35); c.fill()
    if lt > d*0.4: chip(c, "CUERPO ≈ AGUA", W/2, 440, lt-d*0.4, ic_drop, size=40)
    if k > 0.5: chip(c, "VOLUMEN DESPLAZADO", 820, 1040, lt-d*0.55, size=26, bg=C['gold'], anchor=(270, lvl+50))
    post(c, t, 0.3, 0.05)

def q1_4(c, lt, d, t):   # 361 millones de km² de océano
    grad_bg(c, hexc("#0B1830"), hexc("#050A16"))
    stars(c, 140, 2, t)
    globe(c, W/2, 900, 380, t*0.06)
    stat_card(c, "OCÉANOS", "361", "MILL. km²", W/2, 1420, lt-0.4, icon=ic_drop, sub="71 % DEL PLANETA")
    post(c, t, 0.45, 0.06)

def q1_5(c, lt, d, t):   # el mar subiría menos de una milésima de mm
    k = ease(P(lt, d, 0.1, 0.8))
    sky(c)
    sea(c, 860, t, amp=6)
    # regla gigante
    box(c, 760, 380, 120, 1000, C['gold'], 6, 4)
    for i in range(21):
        y = 400+i*46; c.set_source_rgb(*OUT); c.set_line_width(4 if i % 5 else 7)
        c.move_to(760, y); c.line_to(760+(30 if i % 5 else 60), y); c.stroke()
    # lupa
    c.save(); c.translate(380, 680); circle(c, 0, 0, 220); fs(c, hexc('#E9F4F8'), 10)
    c.save(); circle(c, 0, 0, 214); c.clip()
    c.rectangle(-220, 40-6*k, 440, 300); c.set_source_rgb(*SEA1); c.fill()
    c.set_source_rgb(*C['red2']); c.set_line_width(5); c.set_dash([16, 10]); c.move_to(-220, 40); c.line_to(220, 40); c.stroke(); c.set_dash([])
    c.restore(); c.set_source_rgb(*OUT); c.set_line_width(28); c.move_to(150, 160); c.line_to(260, 270); c.stroke(); c.restore()
    if lt > d*0.45: chip(c, "< 0,001 mm", 380, 1000, lt-d*0.45, ic_drop, size=48, bg=C['red'], fg=C['paper'])
    post(c, t, 0.3, 0.05)

def q1_6(c, lt, d, t):   # decenas de veces menos que un pelo
    grad_bg(c, hexc("#FFF6E8"), hexc("#F6E1C4"))
    k = ease(P(lt, d, 0, 0.5))
    # pelo enorme (sección)
    c.save(); c.translate(W/2, 820)
    w = 520*k+20
    g = cairo.LinearGradient(-w/2, 0, w/2, 0); g.add_color_stop_rgb(0, *hexc('#3A2A1E')); g.add_color_stop_rgb(0.5, *hexc('#7A5640')); g.add_color_stop_rgb(1, *hexc('#3A2A1E'))
    c.rectangle(-w/2, -500, w, 1000); c.set_source(g); c.fill()
    c.restore()
    # línea fina de la subida del mar
    c.set_source_rgb(*SEA1); c.rectangle(W/2+300, 320, 6, 1000); c.fill()
    if lt > d*0.3: chip(c, "UN PELO", W/2, 360, lt-d*0.3, size=36)
    if lt > d*0.5: chip(c, "SUBIDA DEL MAR", W/2+250, 1220, lt-d*0.5, ic_drop, size=28, bg=C['gold'], anchor=(W/2+303, 1100))
    if lt > d*0.7: chip(c, "NI UNA OLA LO NOTA", W/2, 1380, lt-d*0.7, ic_check, size=34, bg=C['teal'], fg=C['paper'])
    post(c, t, 0.3, 0.05)

def q1_7(c, lt, d, t):   # probemos con algo más pequeño: la Albufera
    k = ease(P(lt, d))
    grad_bg(c, hexc("#CFE8D0"), hexc("#A9D3AE"))
    c.save(); z = lerp(0.7, 1.15, k); c.translate(W/2, 880); c.scale(z, z); c.translate(-W/2, -880)
    # campos de arroz
    for i in range(8):
        for j in range(10):
            box(c, 40+i*130, 360+j*120, 120, 110, mix(C['leaf'], hexc('#C9D98C'), ((i+j) % 3)/3), 4, 2)
    # lago
    c.new_path(); c.move_to(300, 620); c.curve_to(520, 520, 820, 600, 830, 840); c.curve_to(840, 1060, 620, 1180, 430, 1100)
    c.curve_to(250, 1030, 220, 760, 300, 620); c.close_path(); c.set_source_rgb(*SEA1); c.fill_preserve(); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    # mar al lado
    c.rectangle(940, 300, 200, 1400); c.set_source_rgb(*SEA2); c.fill()
    c.restore()
    if lt > d*0.35: chip(c, "ALBUFERA · VALENCIA", W/2, 420, lt-d*0.35, ic_drop, size=40, bg=C['gold'])
    post(c, t, 0.3, 0.05)

def lake_section(c, t, level_px, person=True, building=True):
    sky(c, hexc("#9AD4EA"), SKY2)
    floor = 1250
    c.rectangle(0, floor, W, H-floor); c.set_source_rgb(*hexc('#7A5C45')); c.fill()
    if building:
        for f in range(4):
            box(c, 760, floor-(f+1)*150, 260, 150, mix(C['wall'], C['wall2'], f % 2), 4, 4)
            for wx in (790, 900): box(c, wx, floor-(f+1)*150+40, 80, 70, hexc('#BFD3D8'), 4, 3)
    if person: teo(c, 300, floor, 300, "stand", t, face=1, expr="shock" if level_px > 260 else "neutral")
    top = floor-level_px
    c.rectangle(0, top, W, level_px+10); c.set_source_rgba(*SEA1, 0.7); c.fill()
    c.set_source_rgba(1, 1, 1, 0.6); c.set_line_width(5); c.move_to(0, top); c.line_to(W, top); c.stroke()
    return top

def q1_8(c, lt, d, t):   # 21 km², 1,5 m de profundidad
    top = lake_section(c, t, 190, building=False)
    stat_card(c, "LAGO DE LA ALBUFERA", "21", "km²", W/2, 480, lt-0.2, icon=ic_drop)
    if lt > d*0.45: chip(c, "MÁX. 1,5 m", 640, top-40, lt-d*0.45, size=34, bg=C['red'], fg=C['paper'])
    post(c, t, 0.3, 0.05)

def q1_9(c, lt, d, t):   # sube casi 14 m: más que un edificio de 4 plantas
    k = ease(P(lt, d, 0.05, 0.7))
    top = lake_section(c, t, lerp(190, 680, k), person=True)
    if lt > d*0.4: chip(c, "+14 m", 640, max(360, top-60), lt-d*0.4, ic_drop, size=56, bg=C['red'], fg=C['paper'])
    if lt > d*0.7: chip(c, "MÁS QUE 4 PLANTAS", W/2, 1420, lt-d*0.7, size=34, bg=C['gold'])
    post(c, t, 0.3, 0.05)

def q1_10(c, lt, d, t):  # no cabríamos: 220 personas por m²
    grad_bg(c, hexc("#FFF6E8"), hexc("#F6E1C4"))
    k = ease(P(lt, d, 0, 0.7))
    x0, y0, s = 190, 520, 700
    box(c, x0, y0, s, s, hexc('#E9DCC4'), 6, 8)
    n = int(220*k)
    r = random.Random(9)
    for i in range(n):
        gx = i % 15; gy = i // 15
        x = x0+25+gx*44+r.uniform(-4, 4); y = y0+48+gy*44
        circle(c, x, y, 16); c.set_source_rgb(*COLS[i % len(COLS)]); c.fill()
    txt(c, "1 m", W/2, y0+s+60, 40, C['ink'], "Anton")
    if lt > 0.2: chip(c, f"{n} PERSONAS / m²", W/2, 420, lt-0.2, ic_warn, size=40, bg=C['red'], fg=C['paper'])
    post(c, t, 0.3, 0.05)

def q1_11(c, lt, d, t):  # para el océano somos casi nada
    k = ease(P(lt, d))
    grad_bg(c, hexc("#0B1830"), hexc("#050A16"))
    stars(c, 140, 4, t)
    globe(c, W/2, 880, lerp(700, 330, k), t*0.05)
    circle(c, W/2+40, 780, 6); c.set_source_rgb(*C['gold']); c.fill()
    if lt > d*0.5: chip(c, "TODOS NOSOTROS", W/2+40, 560, lt-d*0.5, size=30, bg=C['gold'], anchor=(W/2+40, 780))
    post(c, t, 0.45, 0.06)

def q1_12(c, lt, d, t):  # ¿dónde nos meterías tú?
    sky(c); sea(c, 1100, t, amp=10)
    teo(c, 540, 1300, 640, "think", t, face=1, expr="focus", look=(0.3, -0.3))
    for i, (lab, x, y) in enumerate((("¿UNA PISCINA?", 250, 560), ("¿UN LAGO?", 820, 520), ("¿UNA BAÑERA?", 540, 400))):
        if lt > 0.3+i*0.5: chip(c, lab, x, y, lt-0.3-i*0.5, size=34, bg=COLS[i])
    if lt > d*0.6: chip(c, "TE LEO EN COMENTARIOS", W/2, 1420, lt-d*0.6, ic_check, size=34, bg=C['teal'], fg=C['paper'])
    post(c, t, 0.3, 0.05)

SCENES = {"Q1": [q1_0, q1_1, q1_2, q1_3, q1_4, q1_5, q1_6, q1_7, q1_8, q1_9, q1_10, q1_11, q1_12]}
BOOMS = {"Q1": [5, 9]}
CALM = set()
