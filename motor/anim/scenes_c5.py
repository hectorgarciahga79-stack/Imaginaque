"""Estilo «cine» — serie APAGON «Planta 8», capítulo 5: monóxido de carbono (generadores y braseros)."""
from engine import *
from cine import *
from cine import teo as _teo
from scenes_c4 import marta, julian, dani, P, smoke, glow, facade, flat, stairs, FL
import cairo, math, random

LUCIA = dict(top=hexc('#B5838D'), top2=hexc('#946A73'), legs=hexc('#3C4658'), legs2=hexc('#2E3646'), shoe=hexc('#E9E4DA'), skin=hexc('#D9A97F'), hair=hexc('#1E1A18'))
PACO = dict(top=hexc('#4F5D6E'), top2=hexc('#3E4A58'), legs=hexc('#3A3D44'), legs2=hexc('#2B2E34'), shoe=hexc('#2B2A2F'), skin=hexc('#E3BFA0'), hair=hexc('#5A4A3E'))
def lucia(*a, **k): k['who'] = LUCIA; return _teo(*a, **k)
def paco(*a, **k): k['who'] = PACO; return _teo(*a, **k)

def generator(c, x, base, s, t, on=True, night=0.0):
    m = lambda cc: mix(cc, C['night1'], night*0.6)
    c.save(); jit = math.sin(t*55)*2.5*s if on else 0; c.translate(x+jit, base); c.scale(s, s)
    # marco tubular
    c.set_source_rgb(*OUT); c.set_line_width(10)
    rrect(c, -150, -230, 300, 230, 14); c.stroke()
    box(c, -130, -200, 180, 170, m(C['red']), 18)            # depósito/motor
    box(c, -110, -250, 140, 60, m(C['red2']), 16)            # depósito superior
    circle(c, -40, -250, 16); fs(c, m(C['dark']), 3)          # tapón
    box(c, 60, -170, 80, 120, m(C['dark2']), 8)               # alternador
    for i in range(4): c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(4); c.move_to(70, -150+i*26); c.line_to(130, -150+i*26); c.stroke()
    box(c, 140, -110, 40, 24, m(C['steel2']), 6, 3)           # escape
    c.restore()
    if on:
        for i in range(5):  # humo del escape
            ph = (t*0.7+i/5) % 1
            xx = x+(180+ph*160)*s; yy = base-(98+ph*220)*s
            g = cairo.RadialGradient(xx, yy, 2, xx, yy, (30+ph*90)*s)
            g.add_color_stop_rgba(0, 0.55, 0.55, 0.58, 0.45*(1-ph)); g.add_color_stop_rgba(1, 0.55, 0.55, 0.58, 0)
            c.set_source(g); c.arc(xx, yy, (30+ph*90)*s, 0, 2*math.pi); c.fill()

def brasero(c, x, base, s, t):
    c.save(); c.translate(x, base); c.scale(s, s)
    c.set_source_rgb(*OUT); c.set_line_width(8)
    for dx in (-90, 0, 90): c.move_to(dx*0.8, -60); c.line_to(dx, 0)
    c.stroke()
    c.new_path(); c.move_to(-130, -140); c.line_to(130, -140); c.line_to(100, -60); c.line_to(-100, -60); c.close_path(); fs(c, C['steel2'])
    r = random.Random(5)
    for i in range(14):
        bx = r.uniform(-105, 105); by = r.uniform(-160, -140)
        hot = 0.5+0.5*math.sin(t*4+i)
        circle(c, bx, by, r.uniform(14, 22)); fs(c, mix((0.25, 0.1, 0.08), (1, 0.45, 0.15), hot), 2)
    c.restore()
    glow(c, x, base-150*s, 380*s, (1, 0.45, 0.15), 0.35)

def cross(c, x, y, r, k):
    if k <= 0: return
    c.set_source_rgba(*C['red2'], 0.95); c.set_line_width(26); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x-r, y-r); c.line_to(x-r+2*r*min(1, k*2), y-r+2*r*min(1, k*2))
    if k > 0.5: c.move_to(x+r, y-r); c.line_to(x+r-2*r*(k-0.5)*2, y-r+2*r*(k-0.5)*2)
    c.stroke(); c.set_line_cap(cairo.LINE_CAP_BUTT)

def co_wisps(c, t, a=0.18, seed=7):
    r = random.Random(seed)
    for i in range(10):
        bx = r.uniform(0, W); by = r.uniform(400, 1300); ph = r.uniform(0, 6)
        c.new_path(); c.move_to(bx, by)
        for j in range(1, 8):
            c.line_to(bx+j*40+math.sin(t*1.2+ph+j)*30, by-j*25+math.cos(t+ph+j)*20)
        c.set_source_rgba(0.85, 0.9, 1, a*(0.5+0.5*math.sin(t*1.5+ph))); c.set_line_width(18); c.stroke()

def siren(c, t, a=0.35):
    on = (t*3) % 1 < 0.5
    col = (1, 0.15, 0.1) if on else (0.15, 0.35, 1)
    g = cairo.RadialGradient(W*(0.15 if on else 0.85), 1500, 20, W*(0.15 if on else 0.85), 1500, 900)
    g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0); c.set_source(g); c.paint()

# ---------------- escenas ----------------
def c5_0(c, lt, d, t):   # gancho: mano en el cristal entre el humo
    k = ease(P(lt, d))
    c.save(); z = 1.15+0.35*k; c.translate(W/2, 800); c.scale(z, z); c.translate(-W/2-30*k, -800+20*k)
    grad_bg(c, hexc("#120E10"), hexc("#060507"))
    rrect(c, 230, 420, 620, 760, 6); fs(c, hexc('#3A3436'), 0)
    rrect(c, 260, 450, 560, 700, 2); c.set_source_rgb(0.55, 0.25, 0.12); c.fill()
    glow(c, 540, 820, 420, (1, 0.5, 0.2), 0.35+0.15*math.sin(t*8))
    smoke(c, t, 260, 450, 820, 1150, 16, 0.55, seed=13, rise=50, col=(0.1, 0.09, 0.1))
    c.set_source_rgb(*hexc('#3A3436')); c.set_line_width(16); c.move_to(540, 450); c.line_to(540, 1150); c.move_to(260, 780); c.line_to(820, 780); c.stroke()
    hx, hy = 430, 640+10*math.sin(t*3)
    c.set_source_rgba(0.98, 0.88, 0.82, 0.75); rrect(c, hx-26, hy-22, 52, 54, 18); c.fill()
    for f in range(4): rrect(c, hx-25+f*13, hy-72, 10, 52, 5); c.fill()
    rrect(c, hx+22, hy-28, 11, 36, 5); c.fill()
    knock_marks(c, 600, 560, lt)
    c.restore()
    # primer plano oscuro: marco de la ventana del vecino
    c.set_source_rgba(0.02, 0.02, 0.03, 0.95); c.rectangle(0, 0, 120, H); c.fill(); c.rectangle(W-90, 0, 90, H); c.fill()
    c.rectangle(0, 1500, W, H-1500); c.fill()
    if lt > d*0.6: chip(c, "LUCÍA · 4º", W/2, 1380, lt-d*0.6, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.7, 0.09)

def c5_1(c, lt, d, t):   # bomberos: escalera hasta el 4º
    k = ease(P(lt, d))
    facade(c, t, 0.7*(1-k*0.6), 0.6, 1.25-0.15*k, lerp(560, W/2, k), 1000)
    siren(c, t, 0.4)
    # escalera del camión
    c.save(); c.translate(980, 1650); c.rotate(-2.2+0.0*k)
    L = lerp(200, 980, ease(P(lt, d, 0, 0.6)))
    c.set_source_rgb(*C['steel']); c.set_line_width(14); c.move_to(0, -26); c.line_to(L, -26); c.move_to(0, 26); c.line_to(L, 26); c.stroke()
    c.set_line_width(8)
    for i in range(0, int(L), 50): c.move_to(i, -26); c.line_to(i, 26)
    c.stroke(); c.restore()
    if lt > d*0.55:
        silhouette(c, lerp(760, 650, P(lt, d, 0.55, 1)), lerp(1060, 930, P(lt, d, 0.55, 1)), 170, t)
    if lt > d*0.3: chip(c, "BOMBEROS", W/2, 400, lt-d*0.3, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.58)

def c5_2(c, lt, d, t):   # Lucía tose, está bien; huele a gasolina
    grad_bg(c, C['night2'], C['night1'])
    siren(c, t, 0.22)
    c.rectangle(0, 1380, W, H-1380); c.set_source_rgb(*mix(C['grey2'], C['night1'], 0.6)); c.fill()
    cam = 30*ease(P(lt, d))
    c.save(); c.translate(-cam, 0)
    dani(c, 430, 1460, 560, "carry", t, face=1, expr="worried", lit=0.8)
    lucia(c, 610, 1460, 380, "think" if math.sin(t*5) > 0.3 else "stand", t, face=-1, expr="sleep" if math.sin(t*5) > 0.3 else "neutral", lit=0.85)
    marta(c, 840, 1460, 530, "stand", t, face=-1, expr="neutral", lit=0.75)
    c.restore()
    if lt < d*0.5 and (t*2) % 1 < 0.6: txt(c, "COF", 700, 900, 50, C['paper'], "Anton")
    if lt > d*0.2: chip(c, "ESTÁ BIEN", 520, 560, lt-d*0.2, ic_check, size=34)
    if lt > d*0.62: chip(c, "…HUELE A GASOLINA", W/2, 1640, lt-d*0.62, ic_warn, size=32)
    post(c, t, 0.6)

def c5_3(c, lt, d, t):   # Paco mete un generador en la cocina
    counter_kitchen(c, 900, night=0.75)
    c.rectangle(0, 1260, W, H-1260); c.set_source_rgb(*mix(C['tile'], C['night1'], 0.7)); c.fill()
    glow(c, 640, 1100, 500, (1, 0.9, 0.6), 0.18)
    x = lerp(1250, 720, ease(P(lt, d, 0, 0.5)))
    generator(c, x, 1300, 1.25, t, on=lt > d*0.5, night=0.3)
    paco(c, x-300, 1320, 540, "carry" if lt < d*0.5 else "stand", t, face=1, walk=lt*1.6 if lt < d*0.5 else 0, expr="focus", lit=0.75)
    if lt > d*0.5:
        for i in range(3):
            c.set_source_rgba(1, 1, 1, 0.5); c.set_line_width(5); r = 60+((t*120+i*40) % 120)
            c.arc(x, 1180, r, -2.2, -0.9); c.stroke()
    chip(c, "PACO · 3º", 330, 500, lt-0.3, size=32, bg=C['gold'])
    if lt > d*0.6: chip(c, "GENERADOR EN LA COCINA", W/2, 1600, lt-d*0.6, ic_warn, size=32)
    post(c, t, 0.58)

def c5_4(c, lt, d, t):   # Marta se queda helada
    grad_bg(c, hexc("#1B2233"), hexc("#0B0E16"))
    glow(c, 820, 700, 700, (0.75, 0.88, 1), 0.25)
    s = 1+0.2*ease(P(lt, d))
    c.save(); c.translate(W/2, 1500); c.scale(s, s); c.translate(-W/2, -1500)
    marta(c, 480, 1820, 1150, "stand", t, face=1, expr="shock" if lt > d*0.3 else "worried", look=(0.5, 0.2), lit=0.85, shadow=False)
    c.restore()
    if lt > d*0.45: chip(c, "APAGÓN · ABRIL 2025", W/2, 420, lt-d*0.45, ic_bolt, size=34)
    post(c, t, 0.65)

def c5_5(c, lt, d, t):   # dato real: Taboadela (Ourense)
    grad_bg(c, hexc("#141A26"), hexc("#07090E"))
    generator(c, W/2, 1560, 1.3+0.1*ease(P(lt, d)), t, on=True, night=0.5)
    c.save(); c.translate(W/2, 640); k = pop(lt-0.3, 0.45); c.scale(max(k, 1e-3), max(k, 1e-3))
    c.set_source_rgba(0, 0, 0, 0.3); rrect(c, -410+10, -250+14, 820, 500, 22); c.fill()
    rrect(c, -410, -250, 820, 500, 22); fs(c, C['paper'], 0)
    rrect(c, -290, -220, 580, 56, 28); fs(c, C['dark'], 0); txt(c, "TABOADELA (OURENSE) · 2025", 0, -180, 30, C['paper'])
    txt(c, "3 MUERTOS", 0, -50, 100, C['red'], "Anton")
    txt(c, "MATRIMONIO E HIJO", 0, 40, 50, C['ink'], "Anton")
    txt(c, "INTOXICADOS POR MONÓXIDO", 0, 110, 42, C['ink'], "Anton")
    c.restore()
    if lt > d*0.6: chip(c, "INDICIOS: UN GENERADOR", W/2, 1000, lt-d*0.6, ic_warn, size=32)
    post(c, t, 0.6)

def c5_6(c, lt, d, t):   # REGLA 1: generador nunca dentro
    wall_room(c, C['wall2'], 1300, 0.6)
    window_city(c, 600, 420, 360, 420, t, night=0.95, lights_out=1)
    generator(c, 360, 1360, 1.2, t, on=True, night=0.3)
    cross(c, 400, 1150, 230, P(lt, d, 0.5, 0.8))
    if lt > d*0.12: rule_card(c, 1, "NUNCA UN GENERADOR", "DENTRO DE CASA", W/2, 560, lt-d*0.12)
    if lt > d*0.6: chip(c, "NI EN EL GARAJE · NI CON VENTANAS ABIERTAS", W/2, 1560, lt-d*0.6, ic_warn, size=26)
    post(c, t, 0.55)

def c5_7(c, lt, d, t):   # fuera, a más de 6 m
    grad_bg(c, C['night2'], C['night1'])
    c.rectangle(0, 1300, W, H-1300); c.set_source_rgb(*mix(C['leaf2'], C['night1'], 0.6)); c.fill()
    pan = 120*ease(P(lt, d))
    c.save(); c.translate(-pan, 0)
    box(c, -40, 600, 420, 700, mix(C['wall2'], C['night1'], 0.6), 4)
    box(c, 220, 760, 110, 150, mix(C['gold'], C['night1'], 0.3), 4)
    box(c, 90, 1000, 140, 300, mix(C['wood'], C['night1'], 0.5), 4)
    generator(c, 1000, 1400, 0.8, t, on=True, night=0.3)
    k = ease(P(lt, d, 0.1, 0.45)); x1 = lerp(390, 880, k)
    c.set_source_rgb(*C['paper']); c.set_line_width(6); c.set_dash([18, 12]); c.move_to(390, 1250); c.line_to(x1, 1250); c.stroke(); c.set_dash([])
    for xx in (390, x1): c.move_to(xx, 1220); c.line_to(xx, 1280); c.stroke()
    if k > 0.95: txt(c, "MÁS DE 6 M", 635, 1210, 56, C['paper'], "Anton")
    c.restore()
    if lt > d*0.3: chip(c, "SIEMPRE FUERA", W/2, 420, lt-d*0.3, ic_check, size=38)
    if lt > d*0.55: chip(c, "LEJOS DE PUERTAS Y VENTANAS", W/2, 1600, lt-d*0.55, ic_warn, size=30)
    post(c, t, 0.55)

def c5_8(c, lt, d, t):   # el CO no huele ni se ve
    flat(c, t, 0.85, candle_on=False)
    co_wisps(c, t, 0.12+0.15*P(lt, d))
    z = 1+0.1*ease(P(lt, d))
    c.save(); c.translate(W/2, 1300); c.scale(z, z); c.translate(-W/2, -1300)
    julian(c, 300, FL+60, 520, "sit", t, face=1, expr="sleep", lit=0.7)
    c.restore()
    if lt > d*0.15: chip(c, "MONÓXIDO DE CARBONO", W/2, 360, lt-d*0.15, ic_warn, size=34, bg=C['dark'], fg=C['paper'])
    if lt > d*0.4: chip(c, "NO HUELE", 330, 520, lt-d*0.4, size=34)
    if lt > d*0.55: chip(c, "NO SE VE", 750, 520, lt-d*0.55, size=34)
    post(c, t, 0.65)

def c5_9(c, lt, d, t):   # REGLA 2: braseros de leña o carbón
    wall_room(c, C['wall'], 1300, 0.7)
    brasero(c, W/2, 1420, 1.3+0.08*math.sin(t), t)
    co_wisps(c, t, 0.15, seed=3)
    cross(c, W/2, 1220, 240, P(lt, d, 0.55, 0.85))
    if lt > d*0.1: rule_card(c, 2, "NADA DE BRASEROS", "EN SITIOS CERRADOS", W/2, 560, lt-d*0.1)
    if lt > d*0.6: chip(c, "NUNCA PARA DORMIR", W/2, 1640, lt-d*0.6, ic_warn, size=34)
    post(c, t, 0.55)

def c5_10(c, lt, d, t):  # Lucía: mareo y náuseas
    flat(c, t, 0.8)
    wob = 0.03*math.sin(t*2.3)*P(lt, d, 0.2, 0.6)
    c.save(); c.translate(W/2, 1200); c.rotate(wob); s = 1+0.12*ease(P(lt, d)); c.scale(s, s); c.translate(-W/2, -1200)
    lucia(c, 560, FL+40, 420, "think", t, face=-1, expr="worried", look=(0, 0.3), lit=0.8)
    dani(c, 820, FL+40, 540, "reach", t, face=-1, expr="shock", lit=0.75)
    c.restore()
    for i in range(3):  # espirales de mareo
        a = t*3+i*2.1; c.set_source_rgba(1, 1, 1, 0.6); c.set_line_width(5)
        c.arc(560+math.cos(a)*90, 760+math.sin(a)*24, 14, 0, 2*math.pi); c.stroke()
    if lt > d*0.3: chip(c, "MAREO", 330, 480, lt-d*0.3, ic_warn, size=36)
    if lt > d*0.55: chip(c, "NÁUSEAS", 760, 480, lt-d*0.55, ic_warn, size=36)
    post(c, t, 0.6)

def c5_11(c, lt, d, t):  # REGLA 3: aire fresco y 112
    wall_room(c, C['wall2'], 1500, 0.8)
    window_city(c, 90, 960, 420, 460, t, night=0.95, lights_out=1)
    co_wisps(c, -t*1.5, 0.12, seed=11)
    c.save(); s = 0.62+0.06*ease(P(lt, d)); phone_alert(c, 780, 1220, s, t, "LLAMA AL", "112", "", "EMERGENCIAS"); c.restore()
    if lt > d*0.08: rule_card(c, 3, "¿DOLOR DE CABEZA, MAREO?", "AIRE FRESCO · 112", W/2, 520, lt-d*0.08)
    if lt > d*0.55: chip(c, "SAL FUERA", 300, 1320, lt-d*0.55, ic_check, size=36)
    post(c, t, 0.55)

def c5_12(c, lt, d, t):  # Marta abre las ventanas; Julián sale
    wall_room(c, C['wall2'], FL, 0.75)
    k = ease(P(lt, d, 0, 0.4))
    window_city(c, 520, 380, 440, 520, t, night=0.95, lights_out=1)
    c.save(); c.translate(520, 380); c.scale(1-0.85*k, 1)          # hoja de la ventana que se abre
    c.rectangle(0, 0, 220, 520); c.set_source_rgba(0.7, 0.8, 0.9, 0.35); c.fill_preserve(); c.set_source_rgb(*OUT); c.set_line_width(10); c.stroke(); c.restore()
    for i in range(5):   # cortina al viento
        x = 440+i*30; c.new_path(); c.move_to(x, 360); c.curve_to(x+40*k*math.sin(t*2+i), 600, x+80*k, 800, x+30*k*math.sin(t*1.7+i), 960)
        c.set_source_rgb(*mix(hexc('#B5838D'), C['night1'], 0.5)); c.set_line_width(28); c.stroke()
    marta(c, lerp(300, 440, k), FL+40, 520, "reach", t, face=1, expr="focus", lit=0.8)
    door(c, 130, FL, 220, 660, open_=0.7*P(lt, d, 0.5, 0.7), night=0.8, t=t)
    if lt > d*0.5: julian(c, lerp(260, 90, ease(P(lt, d, 0.5, 1))), FL+40, 520, "stand", t, face=-1, walk=lt*1.8, expr="focus", lit=0.7)
    if lt > d*0.3: chip(c, "VENTANAS ABIERTAS", W/2, 1500, lt-d*0.3, ic_check, size=32)
    post(c, t, 0.58)

def c5_13(c, lt, d, t):  # Julián llama en el 3º; Paco no abre
    k = ease(P(lt, d))
    c.save(); z = 1+0.25*k; c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2, -900)
    stairs(c, t, 0.9)
    darken(c, 0.25)
    door(c, 640, FL, 300, 720, night=0.85, knock=1.0 if (t % 1.4) < 0.5 and lt < d*0.7 else 0.0, t=t)
    c.set_source_rgb(*OUT); c.rectangle(560, 470, 160, 50); c.fill(); txt(c, "3º B", 640, 508, 32, C['paper'])
    julian(c, 330, FL+40, 520, "reach", t, face=1, expr="worried", lit=0.6)
    # rugido del generador bajo la puerta
    for i in range(4):
        yy = FL+10; xx = 520+i*80+math.sin(t*40+i)*6
        c.set_source_rgba(1, 0.9, 0.7, 0.4); c.set_line_width(4); c.move_to(xx, yy); c.line_to(xx+30, yy+20+math.sin(t*50+i)*8); c.stroke()
    if lt < d*0.7: knock_marks(c, 640, 380, lt)
    c.restore()
    if lt > d*0.35: chip(c, "BRRRRR…", 820, 1500, lt-d*0.35, size=34, bg=C['dark'], fg=C['paper'])
    if lt > d*0.75: chip(c, "NADIE ABRE", W/2, 360, lt-d*0.75, ic_warn, size=40, bg=C['red'], fg=C['paper'])
    post(c, t, 0.7, 0.09)

SCENES = {"C5": [c5_0, c5_1, c5_2, c5_3, c5_4, c5_5, c5_6, c5_7, c5_8, c5_9, c5_10, c5_11, c5_12, c5_13]}
BOOMS = {"C5": [0, 13]}
CALM = {"C5"}

def cover_c5(c):   # portada: Paco y el generador rugiendo en la cocina
    counter_kitchen(c, 1000, night=0.45)
    c.rectangle(0, 1360, W, H-1360); c.set_source_rgb(*mix(C['tile'], C['night1'], 0.45)); c.fill()
    glow(c, 720, 1150, 650, (1, 0.55, 0.2), 0.35)
    generator(c, 690, 1460, 1.55, 0.37, on=True, night=0.1)
    for i in range(4):
        c.set_source_rgba(1, 1, 1, 0.75); c.set_line_width(9); c.arc(560, 1180, 90+i*45, -2.4, -1.2); c.stroke()
    paco(c, 250, 1470, 680, "alarm", 0.2, face=1, expr="shock", lit=1.0)
    smoke(c, 1.0, 650, 750, 1080, 1100, 8, 0.35, seed=2, rise=0, col=(0.6, 0.6, 0.62))
    vig(c, 0.3)

COVER = {"C5": cover_c5}
