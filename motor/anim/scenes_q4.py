"""Estilo «cine» luminoso y exagerado — ¿Y si…? Q4: ¿y si drenáramos el mar y lo consiguiéramos?"""
from engine import *
from cine import *
from cine import teo as _teo
from scenes_c4 import P
from scenes_q1 import mini, sky, sea, splash, COLS, SEA1, SEA2, SAND
import cairo, math, random

SALT, SALT2 = hexc("#EDE3CF"), hexc("#CDBB98")
ROCK, ROCK2 = hexc("#8A7A68"), hexc("#6B5D4F")

def teo(*a, **k): return _teo(*a, **k)

def vortex(c, x, y, r, t, a=1.0):
    """remolino gigante (desagüe)"""
    for i in range(14):
        rr = r*(1-i/14)
        c.set_source_rgba(1, 1, 1, 0.55*a*(1-i/16)); c.set_line_width(10-i*0.5)
        a0 = t*(1.5+i*0.35)+i*0.7
        c.save(); c.translate(x, y); c.scale(1, 0.38); c.arc(0, 0, rr, a0, a0+math.pi*1.2); c.restore(); c.stroke()
    c.save(); c.translate(x, y); c.scale(1, 0.38); circle(c, 0, 0, r*0.16); c.restore()
    c.set_source_rgb(0.05, 0.08, 0.12); c.fill()

def seabed(c, y, col=SALT, col2=SALT2):
    g = cairo.LinearGradient(0, y, 0, H); g.add_color_stop_rgb(0, *col); g.add_color_stop_rgb(1, *col2)
    c.rectangle(0, y, W, H-y); c.set_source(g); c.fill()
    r = random.Random(5); c.set_source_rgba(*shade(col2, 0.2), 0.6); c.set_line_width(3)
    for i in range(40):
        x0 = r.uniform(0, W); y0 = r.uniform(y+20, H-200)
        c.move_to(x0, y0); c.line_to(x0+r.uniform(-60, 60), y0+r.uniform(10, 40)); c.stroke()

def ship(c, x, y, s, tilt=0.18):
    """barco hundido genérico de 4 chimeneas (casco partido)"""
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(s, s)
    c.new_path(); c.move_to(-200, -40); c.line_to(200, -40); c.line_to(170, 30); c.line_to(-180, 30); c.close_path(); fs(c, hexc("#2B2A2F"))
    c.rectangle(-200, -40, 400, 14); c.set_source_rgb(*hexc("#E8E1D2")); c.fill()
    c.rectangle(-150, -70, 300, 30); fs(c, hexc("#E8E1D2"))
    for i in range(4):
        box(c, -120+i*70, -130, 34, 60, hexc("#C98A2E"), 3)
        c.rectangle(-120+i*70, -130, 34, 12); c.set_source_rgb(*OUT); c.fill()
    c.restore()

def mountain(c, x, base, w, h, col=ROCK, snow=True):
    c.new_path(); c.move_to(x-w/2, base); c.line_to(x, base-h); c.line_to(x+w/2, base); c.close_path(); fs(c, col)
    if snow:
        c.new_path(); c.move_to(x-w*0.12, base-h*0.76); c.line_to(x, base-h); c.line_to(x+w*0.12, base-h*0.76); c.line_to(x+w*0.04, base-h*0.8); c.line_to(x-w*0.03, base-h*0.74); c.close_path(); fs(c, C['paper'], 3)

# ---------------- escenas ----------------
def q4_0(c, lt, d, t):   # gancho: quitamos el tapón del mar
    k = ease(P(lt, d))
    c.save(); z = 1.0+0.2*k; c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2, -900)
    sky(c); sun(c, 860, 380, 80, t)
    lvl = 760+260*k
    seabed(c, 1100)
    sea(c, lvl, t, amp=12)
    vortex(c, W/2, lvl+170, 470, t, 1-0.3*k)
    # cadena y tapón gigante saliendo volando
    py = 560-300*k; px = W/2+160*k
    c.set_source_rgb(*C['steel2']); c.set_line_width(10)
    for i in range(10):
        circle(c, lerp(px, W/2, i/10), lerp(py, lvl+170, i/10), 12); c.stroke()
    c.save(); c.translate(px, py); c.rotate(0.6*k); rrect(c, -110, -40, 220, 80, 20); fs(c, hexc("#3A3940")); c.restore()
    c.restore()
    if lt > 0.4: chip(c, "¡QUITAMOS EL TAPÓN!", W/2, 470, lt-0.4, ic_drop, size=44, bg=C['gold'])
    post(c, t, 0.3, 0.05)

def q4_1(c, lt, d, t):   # 1.335 millones de km³
    grad_bg(c, hexc("#0B1830"), hexc("#050A16")); stars(c, 120, 3, t)
    globe(c, W/2, 1060, 280, t*0.05)
    k = ease(P(lt, d, 0.25, 0.9))
    # cubo de agua que sale del planeta
    s = 60+160*k; x, y = W/2, 1060-280-s/2-30*k
    c.rectangle(x-s/2, y-s/2, s, s); c.set_source_rgba(*SEA1, 0.9); c.fill_preserve(); c.set_source_rgb(1, 1, 1); c.set_line_width(4); c.stroke()
    stat_card(c, "TODO EL OCÉANO", "1.335", "MILL. km³", W/2, 380, lt-0.3, icon=ic_drop, sub="NOAA")
    post(c, t, 0.4, 0.05)

def q4_2(c, lt, d, t):   # una pajita con la fuerza del Amazonas al revés: ~200.000 años
    sky(c, hexc("#9AD4EA"), hexc("#FDE7C2"))
    sea(c, 1020, t, amp=10)
    # pajita gigante desde el cielo
    c.save(); c.translate(430, 0); c.rotate(-0.1)
    box(c, -60, 120, 120, 1000, C['red2'], 20)
    for i in range(8): c.rectangle(-60, 160+i*120, 120, 40); c.set_source_rgba(1, 1, 1, 0.7); c.fill()
    # agua subiendo por la pajita
    for i in range(6):
        yy = 1040-((t*600+i*170) % 900); circle(c, 0, yy, 22); c.set_source_rgba(*SEA1, 0.9); c.fill()
    c.restore()
    teo(c, 150, 1300, 330, "alarm", t, face=1, expr="shock")
    if lt > 0.3: chip(c, "FUERZA DEL AMAZONAS · AL REVÉS", W/2, 360, lt-0.3, size=34, bg=C['paper'])
    if lt > d*0.5: time_card(c, "TARDARÍAMOS", "≈ 200.000", "AÑOS", 745, 600, lt-d*0.5, col=C['red'])
    post(c, t, 0.3, 0.05)

def q4_3(c, lt, d, t):   # de España a Nueva York andando
    sky(c, hexc("#F7D9A8"), hexc("#FDF1DC")); sun(c, 540, 420, 110, t)
    seabed(c, 900)
    # acantilados
    c.new_path(); c.move_to(0, 700); c.line_to(170, 700); c.line_to(230, 1000); c.line_to(0, 1000); c.close_path(); fs(c, C['leaf'])
    c.new_path(); c.move_to(W, 700); c.line_to(W-170, 700); c.line_to(W-230, 1000); c.line_to(W, 1000); c.close_path(); fs(c, C['leaf'])
    label_tag(c, "NUEVA YORK", 150, 640, 32); label_tag(c, "ESPAÑA", W-110, 640, 32)
    k = P(lt, d, 0.1, 1.0)
    x = lerp(W-260, 300, k)
    teo(c, x, 1180, 300, "stand", t, face=-1, walk=lt*1.6, expr="happy")
    c.set_source_rgba(*SALT2, 0.9); c.set_dash([18, 14]); c.set_line_width(6); c.move_to(W-260, 1200); c.line_to(x, 1200); c.stroke(); c.set_dash([])
    if lt > 0.3: chip(c, "¡ANDANDO!", W/2, 520, lt-0.3, ic_check, size=46, bg=C['gold'])
    post(c, t, 0.25, 0.04)

def q4_4(c, lt, d, t):   # desierto de sal a casi 4 km… con el Titanic
    k = ease(P(lt, d, 0, 0.6))
    c.save(); c.translate(0, -380*k)
    sky(c, hexc("#F7D9A8"), hexc("#FDF1DC"))
    c.rectangle(0, 700, W, 2000); c.set_source_rgb(*SALT); c.fill()
    # talud continental
    c.new_path(); c.move_to(0, 700); c.line_to(300, 700); c.curve_to(420, 900, 420, 1300, 560, 1500); c.line_to(0, 1500); c.close_path(); fs(c, ROCK)
    seabed(c, 1500)
    ship(c, 780, 1480, 1.0)
    teo(c, 300, 700, 200, "stand", t, face=1, expr="shock")
    c.restore()
    if lt > 0.3: chip(c, "−3.800 m", W/2, 420, lt-0.3, size=56, bg=C['red'], fg=C['paper'])
    if lt > d*0.55: chip(c, "TITANIC", 780, 960, lt-d*0.55, size=34, bg=C['paper'], anchor=(780, 1060))
    post(c, t, 0.3, 0.05)

def q4_5(c, lt, d, t):   # fosa de casi 11 km; el Everest cabe y sobran 2
    grad_bg(c, hexc("#F3E6CC"), hexc("#E4D2AE"))
    top, bot = 420, 1300
    # paredes de la fosa
    c.new_path(); c.move_to(0, top); c.line_to(330, top); c.line_to(500, bot); c.line_to(580, bot); c.line_to(750, top); c.line_to(W, top)
    c.line_to(W, H); c.line_to(0, H); c.close_path(); fs(c, ROCK)
    k = ease(P(lt, d, 0.2, 0.65))
    eh = (bot-top)*8849/10935
    mountain(c, 540, lerp(top-40, bot, k), 300, eh, hexc("#9C8B78"))
    if lt > d*0.7:
        y0 = bot-eh; c.set_source_rgb(*C['red']); c.set_line_width(6)
        c.move_to(820, top); c.line_to(820, y0); c.stroke()
        chip(c, "SOBRAN 2 km", 770, (top+y0)/2, lt-d*0.7, size=34, bg=C['red'], fg=C['paper'])
    if lt > 0.2: chip(c, "FOSA DE LAS MARIANAS · 10.935 m", W/2, 330, lt-0.2, size=32, bg=C['paper'])
    if lt > d*0.4: chip(c, "EVEREST 8.849 m", 300, 1180, lt-d*0.4, size=30, bg=C['gold'])
    post(c, t, 0.3, 0.05)

def q4_6(c, lt, d, t):   # la mitad del oxígeno sale del océano
    grad_bg(c, hexc("#DDEFF5"), hexc("#B9DCE8"))
    seabed(c, 1150)
    k = ease(P(lt, d, 0.2, 0.9))
    r = random.Random(3)
    for i in range(26):
        x = r.uniform(80, W-80); y = 1100-((t*120+r.uniform(0, 700)) % 700)
        a = 1-k if i % 2 == 0 else 1.0
        circle(c, x, y, 26); c.set_source_rgba(1, 1, 1, 0.8*a); c.fill()
        txt(c, "O₂", x, y+9, 22, C['water2'], a=a)
    teo(c, 540, 1300, 420, "alarm" if k > 0.5 else "stand", t, face=1, expr="shock" if k > 0.4 else "neutral")
    stat_card(c, "LO FABRICA EL OCÉANO", "≈ 50", "% O₂", W/2, 420, lt-0.3, icon=ic_warn, sub="NOAA")
    post(c, t, 0.3, 0.05)

def q4_7(c, lt, d, t):   # sin mar apenas llovería: todo se seca
    k = ease(P(lt, d))
    grad_bg(c, mix(hexc("#9AD4EA"), hexc("#F2B36B"), k), mix(hexc("#FDE7C2"), hexc("#F7D19A"), k))
    sun(c, 820, 420, 90+50*k, t)
    for i in range(4):
        cloud_x = 200+i*230 + 40*math.sin(t+i)
        cr = 70*(1-k)
        if cr > 4:
            circle(c, cloud_x, 560, cr); c.set_source_rgba(1, 1, 1, 0.9*(1-k)); c.fill()
    ground_y = 1150
    c.rectangle(0, ground_y, W, H-ground_y); c.set_source_rgb(*mix(C['leaf'], hexc("#C9A36B"), k)); c.fill()
    c.set_source_rgba(*shade(hexc("#C9A36B"), 0.4), k); c.set_line_width(4)
    r = random.Random(8)
    for i in range(22):
        x0 = r.uniform(0, W); y0 = r.uniform(ground_y+20, 1330)
        c.move_to(x0, y0); c.line_to(x0+r.uniform(-50, 50), y0+r.uniform(-15, 15)); c.line_to(x0+r.uniform(-90, 90), y0+r.uniform(-10, 25)); c.stroke()
    for i, x in enumerate((180, 900)):
        tree(c, x, ground_y, 0.8, bend=0.0, leaves=1-k)
    teo(c, 540, ground_y+20, 360, "listen", t, face=1, expr="worried" if k > 0.3 else "neutral")
    if lt > 0.3: chip(c, "SIN MAR, APENAS LLUEVE", W/2, 400, lt-0.3, ic_warn, size=40, bg=C['red'], fg=C['paper'])
    post(c, t, 0.3, 0.05)

def q4_8(c, lt, d, t):   # ¿dónde metemos el agua?
    grad_bg(c, hexc("#0B1830"), hexc("#050A16")); stars(c, 120, 6, t)
    globe(c, W/2, 1150, 260, t*0.05)
    k = ease(P(lt, d, 0, 0.5))
    s = 420; y = 640+math.sin(t*2)*14
    c.save(); c.translate(W/2, y); c.rotate(math.sin(t)*0.06)
    rrect(c, -s/2, -s/2, s, s, 30); c.set_source_rgba(*SEA1, 0.92); c.fill_preserve(); c.set_source_rgb(1, 1, 1); c.set_line_width(6); c.stroke()
    for i in range(3):
        c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(5); yy = -s/2+60+i*40+math.sin(t*3+i)*8
        c.move_to(-s/2+30, yy); c.curve_to(-60, yy-20, 60, yy+20, s/2-30, yy); c.stroke()
    c.restore()
    if lt > 0.2: chip(c, "¿Y AHORA DÓNDE LO METEMOS?", W/2, 360, lt-0.2, ic_warn, size=38, bg=C['gold'])
    post(c, t, 0.4, 0.05)

def q4_9(c, lt, d, t):   # capa de casi 9 km sobre los continentes > Everest
    k = ease(P(lt, d, 0.1, 0.75))
    sky(c, hexc("#9AD4EA"), hexc("#FDE7C2"))
    base = 1300
    c.rectangle(0, base, W, H-base); c.set_source_rgb(*C['leaf']); c.fill()
    eh = 820
    mountain(c, 720, base, 560, eh)
    for i in range(5): building(c, 40+i*70, base, 60, 80+i*25, [PAL['b1'], PAL['b2'], PAL['b3'], PAL['b4'], PAL['b5']][i], seed=i)
    lvl = base-k*eh*8960/8849
    c.rectangle(0, lvl, W, base-lvl+4); c.set_source_rgba(*SEA1, 0.75); c.fill()
    c.set_source_rgba(1, 1, 1, 0.7); c.set_line_width(5); c.move_to(0, lvl); c.line_to(W, lvl); c.stroke()
    if lt > d*0.35: chip(c, "CAPA DE ≈ 9 km", 300, max(360, lvl-60), lt-d*0.35, ic_drop, size=40, bg=C['red'], fg=C['paper'])
    if lt > d*0.7: chip(c, "EVEREST, BAJO EL AGUA", 720, 1380-120, lt-d*0.7, size=30, bg=C['gold'])
    post(c, t, 0.3, 0.05)

def q4_10(c, lt, d, t):  # todos debajo del agua · ¿dónde la meterías tú?
    grad_bg(c, hexc("#3B8FC0"), hexc("#155E80"))
    r = random.Random(4)
    for i in range(30):
        x = r.uniform(40, W-40); y = H-((t*160+r.uniform(0, H)) % H)
        circle(c, x, y, r.uniform(6, 18)); c.set_source_rgba(1, 1, 1, 0.35); c.fill()
    bob = math.sin(t*1.5)*20
    teo(c, 540, 1180+bob, 480, "alarm", t, face=1, expr="shock", shadow=False)
    for i, (lab, x, y) in enumerate((("¿EN MARTE?", 250, 560), ("¿EN LA LUNA?", 820, 500), ("¿EN TU BAÑERA?", 540, 380))):
        if lt > 0.3+i*0.5: chip(c, lab, x, y, lt-0.3-i*0.5, size=34, bg=[C['paper'], C['gold'], C['red2']][i], fg=OUT if i < 2 else C['paper'])
    if lt > d*0.65: chip(c, "TE LEO EN COMENTARIOS", W/2, 1290, lt-d*0.65, ic_check, size=32, bg=C['teal'], fg=C['paper'])
    post(c, t, 0.35, 0.05)

SCENES = {"Q4": [q4_0, q4_1, q4_2, q4_3, q4_4, q4_5, q4_6, q4_7, q4_8, q4_9, q4_10]}
BOOMS = {"Q4": [0, 6]}
CALM = set()
