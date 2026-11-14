"""Estilo «cine» — serie APAGON «Planta 8», parte 17: el generador del sótano (generador comunitario bien usado)."""
from engine import *
from cine import *
from cine import teo as _teo
from scenes_c4 import marta, julian, dani, P, smoke, glow, flat, stairs, FL
from scenes_c5 import generator, paco, co_wisps, cross
import cairo, math, random

ROSA = dict(top=hexc('#7E6A9A'), top2=hexc('#64557C'), legs=hexc('#3C4658'), legs2=hexc('#2E3646'), shoe=hexc('#E9E4DA'), skin=hexc('#EAC9AE'), hair=hexc('#B9B4AE'), bun=True)
TOMAS = dict(top=hexc('#3E7CB1'), top2=hexc('#2F6290'), legs=hexc('#2B2E34'), legs2=hexc('#22252A'), shoe=hexc('#E9E4DA'), skin=hexc('#E3BFA0'), hair=hexc('#3A2A20'))
def rosa(*a, **k): k['who'] = ROSA; return _teo(*a, **k)
def tomas(*a, **k): k['who'] = TOMAS; return _teo(*a, **k)

def basement(c, t, night=0.85):
    grad_bg(c, mix(hexc('#3A3E46'), hexc('#07080B'), night*0.7), mix(hexc('#24262C'), hexc('#040405'), night*0.7))
    c.rectangle(0, 1300, W, H-1300); c.set_source_rgb(*mix(hexc('#55534E'), (0.02, 0.02, 0.03), night*0.75)); c.fill()
    for i in range(5):   # trasteros con rejilla
        x = -60+i*250; box(c, x, 560, 220, 740, mix(hexc('#6B5E50'), (0.03, 0.03, 0.04), night*0.75), 2, 3)
        c.set_source_rgba(0, 0, 0, 0.45); c.set_line_width(3)
        for j in range(8): c.move_to(x+10, 600+j*40); c.line_to(x+210, 600+j*40)
        c.stroke()
    c.set_source_rgb(*mix(C['steel2'], (0.02, 0.02, 0.03), night*0.6)); c.set_line_width(18); c.move_to(0, 470); c.line_to(W, 470); c.stroke()

def beam(c, x0, y0, x1, y1, w=260, a=0.28):
    c.new_path(); c.move_to(x0, y0); c.line_to(x1-w, y1); c.line_to(x1+w, y1); c.close_path()
    g = cairo.LinearGradient(x0, y0, x1, y1); g.add_color_stop_rgba(0, 1, 0.95, 0.75, a); g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
    c.set_source(g); c.fill()

def mini_fridge(c, x, base, s=1.0, night=0.6):
    box(c, x-90*s, base-260*s, 180*s, 260*s, mix(C['paper'], (0.05, 0.05, 0.07), night), 14)
    c.set_source_rgba(0, 0, 0, 0.5); c.set_line_width(5); c.move_to(x-90*s, base-170*s); c.line_to(x+90*s, base-170*s); c.stroke()
    box(c, x+55*s, base-150*s, 12*s, 60*s, C['steel2'], 4, 2)

def cable(c, x0, y0, x1, y1, sag=60, col=None):
    c.new_path(); c.move_to(x0, y0); c.curve_to(x0+(x1-x0)*0.3, y0+sag, x0+(x1-x0)*0.7, y1+sag, x1, y1)
    c.set_source_rgb(*(col or hexc('#1A1A1E'))); c.set_line_width(10); c.stroke()

def patio(c, t, night=0.8, lights=0.0):
    grad_bg(c, mix(hexc('#2A3550'), hexc('#090C14'), night*0.6), mix(hexc('#1A2135'), hexc('#05070C'), night*0.6))
    box(c, -40, 260, 1160, 1060, mix(C['wall2'], C['night1'], night*0.7), 2)
    for r in range(3):
        for k in range(4):
            on = lights > 0 and (r+k) % 3 == 0
            box(c, 90+k*250, 360+r*300, 150, 190, (1, 0.85, 0.5) if on else mix(hexc('#1B2030'), C['night1'], 0.3), 4)
    c.rectangle(0, 1320, W, H-1320); c.set_source_rgb(*mix(C['grey2'], C['night1'], night*0.6)); c.fill()

def bulb(c, x, y, on, t):
    if on > 0: glow(c, x, y, 520, (1, 0.85, 0.5), 0.45*on)
    c.set_source_rgb(*OUT); c.set_line_width(4); c.move_to(x, y-120); c.line_to(x, y-20); c.stroke()
    circle(c, x, y, 26); fs(c, (1, 0.9, 0.6) if on > 0 else (0.3, 0.3, 0.3), 3)

# ---------------- escenas ----------------
def c17_0(c, lt, d, t):   # gancho: linterna en el sótano, ruido de motor
    k = ease(P(lt, d))
    c.save(); z = 1.1+0.3*k; c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2-40*k, -900)
    basement(c, t, 0.95)
    glow(c, 820, 1100, 380, (1, 0.5, 0.2), 0.25+0.1*math.sin(t*20))
    beam(c, 120, 1700, 820, 1000, 300, 0.3)
    smoke(c, t, 600, 800, 1080, 1250, 10, 0.25, seed=4, rise=40)
    c.restore()
    c.set_source_rgba(0.01, 0.01, 0.02, 0.95); c.rectangle(0, 1560, W, H-1560); c.fill(); c.rectangle(0, 0, 110, H); c.fill()
    for i in range(3):
        c.set_source_rgba(1, 1, 1, 0.55); c.set_line_width(5); r = 50+((t*140+i*40) % 120); c.arc(820, 1100, r, -2.3, -0.8); c.stroke()
    if lt > d*0.4: chip(c, "BRRRRR…", 780, 520, lt-d*0.4, size=38, bg=C['dark'], fg=C['paper'])
    if lt > d*0.65: chip(c, "HUELE A GASOLINA", W/2, 1660, lt-d*0.65, ic_warn, size=34, bg=C['red'], fg=C['paper'])
    post(c, t, 0.7, 0.09)

def c17_1(c, lt, d, t):   # generador + cable a la nevera
    basement(c, t, 0.85)
    pan = 140*ease(P(lt, d))
    c.save(); c.translate(-pan, 0)
    generator(c, 420, 1400, 1.0, t, on=True, night=0.4)
    cable(c, 560, 1290, 940, 1330, 40)
    mini_fridge(c, 1020, 1400, 1.0, 0.45)
    c.restore()
    beam(c, 540, 1900, 600, 1150, 330, 0.25)
    if lt > d*0.2: chip(c, "TRASTERO 5º B", 330, 430, lt-d*0.2, size=32, bg=C['gold'])
    if lt > d*0.55: chip(c, "UN CABLE… A UNA NEVERA", W/2, 1560, lt-d*0.55, ic_bolt, size=32)
    post(c, t, 0.65)

def c17_2(c, lt, d, t):   # Rosa medio dormida en el suelo
    basement(c, t, 0.9)
    s = 1+0.18*ease(P(lt, d))
    c.save(); c.translate(W/2, 1300); c.scale(s, s); c.translate(-W/2, -1300)
    mini_fridge(c, 300, 1400, 1.0, 0.5)
    box(c, 545, 1150, 190, 250, mix(C['wood'], C['night1'], 0.5), 6)
    rosa(c, 600, 1400, 400, "sit", t, face=-1, expr="sleep", lit=0.7)
    co_wisps(c, t, 0.12)
    c.restore()
    beam(c, 980, 1900, 600, 1150, 300, 0.3)
    if lt > d*0.35: chip(c, "ROSA · 5º B", 620, 520, lt-d*0.35, size=36, bg=C['paper'])
    post(c, t, 0.7)

def c17_3(c, lt, d, t):   # monóxido: apagan y la sacan
    basement(c, t, 0.85)
    k = P(lt, d, 0.45, 1)
    generator(c, 860, 1400, 0.85, t, on=lt < d*0.35, night=0.4)
    x = lerp(560, 160, ease(k))
    julian(c, x-130, 1460, 500, "carry", t, face=-1, walk=lt*1.6 if k > 0 else 0, expr="focus", lit=0.7)
    rosa(c, x, 1460, 400, "stand", t, face=-1, walk=lt*1.6 if k > 0 else 0, expr="sleep", lit=0.7)
    marta(c, lerp(900, 640, P(lt, d, 0, 0.35)), 1460, 520, "reach" if lt < d*0.4 else "stand", t, face=1 if lt < d*0.4 else -1, expr="shock", lit=0.75)
    chip(c, "¡MONÓXIDO!", W/2, 440, lt-0.15, ic_warn, size=46, bg=C['red'], fg=C['paper'])
    if lt > d*0.35: chip(c, "MOTOR APAGADO", 820, 1600, lt-d*0.35, ic_check, size=30)
    post(c, t, 0.6)

def c17_4(c, lt, d, t):   # REGLA 1
    basement(c, t, 0.7)
    generator(c, W/2, 1420, 1.1, t, on=True, night=0.3)
    co_wisps(c, t, 0.14)
    cross(c, W/2, 1200, 240, P(lt, d, 0.5, 0.8))
    if lt > d*0.1: rule_card(c, 1, "NADA DE GENERADORES", "EN SÓTANOS NI GARAJES", W/2, 560, lt-d*0.1)
    if lt > d*0.6: chip(c, "NI CON LA PUERTA ABIERTA", W/2, 1600, lt-d*0.6, ic_warn, size=32)
    post(c, t, 0.55)

def c17_5(c, lt, d, t):   # en el patio, Rosa tose; insulina
    patio(c, t, 0.85)
    s = 1+0.12*ease(P(lt, d))
    c.save(); c.translate(W/2, 1400); c.scale(s, s); c.translate(-W/2, -1400)
    box(c, 425, 1165, 190, 255, mix(C['wood'], C['night1'], 0.5), 6)
    rosa(c, 480, 1420, 420, "sit", t, face=1, expr="worried" if lt > d*0.3 else "sleep", lit=0.8)
    marta(c, 760, 1480, 540, "reach", t, face=-1, expr="worried", lit=0.8)
    c.restore()
    if lt < d*0.5 and (t*2) % 1 < 0.6: txt(c, "COF", 420, 860, 54, C['paper'], "Anton")
    if lt > d*0.3: chip(c, "ESTÁ BIEN", 320, 440, lt-d*0.3, ic_check, size=34)
    if lt > d*0.6: chip(c, "EN LA NEVERA: SU INSULINA", W/2, 1640, lt-d*0.6, ic_drop, size=30)
    post(c, t, 0.6)

def c17_6(c, lt, d, t):   # vecinos: el motor podría ayudar a todos
    patio(c, t, 0.85)
    generator(c, W/2, 1460, 0.75, t, on=False, night=0.4)
    for i, (f, x) in enumerate(((julian, 170), (dani, 360), (tomas, 760), (marta, 930))):
        f(c, x, 1500, 470 if f is not tomas else 420, "think" if i == 3 else "stand", t+i, face=1 if x < W/2 else -1, expr="focus", lit=0.75)
    if lt > d*0.25: chip(c, "LUZ PARA TODO EL EDIFICIO", W/2, 420, lt-d*0.25, ic_bolt, size=32)
    if lt > d*0.6: chip(c, "…PERO BIEN HECHO", W/2, 1640, lt-d*0.6, ic_warn, size=34)
    post(c, t, 0.6)

def c17_7(c, lt, d, t):   # Dani quiere enchufarlo al portal
    grad_bg(c, mix(C['wall2'], C['night1'], 0.75), mix(C['wall'], C['night1'], 0.8))
    c.rectangle(0, 1300, W, H-1300); c.set_source_rgb(*mix(C['tile'], C['night1'], 0.7)); c.fill()
    box(c, 660, 900, 150, 200, C['paper'], 12)
    for dx in (-25, 25): circle(c, 735+dx, 1000, 14); fs(c, OUT, 0)
    k = ease(P(lt, d, 0.1, 0.7))
    dani(c, 360, 1360, 560, "reach", t, face=1, expr="focus", lit=0.8)
    c.save(); c.translate(lerp(560, 700, k), lerp(1060, 1000, k))
    box(c, -40, -30, 80, 60, hexc('#1A1A1E'), 10); c.set_source_rgb(*C['steel']); c.set_line_width(8)
    c.move_to(36, -14); c.line_to(70, -14); c.move_to(36, 14); c.line_to(70, 14); c.stroke(); c.restore()
    cable(c, 0, 1250, lerp(560, 700, k)-40, lerp(1060, 1000, k), 120)
    if lt > d*0.35: chip(c, "ENCHUFE DEL PORTAL", W/2, 420, lt-d*0.35, ic_bolt, size=34)
    if lt > d*0.7: chip(c, "¡ESPERA!", 820, 1560, lt-d*0.7, ic_warn, size=40, bg=C['red'], fg=C['paper'])
    post(c, t, 0.6)

def c17_8(c, lt, d, t):   # REGLA 2: nunca a un enchufe de pared
    wall_room(c, C['wall2'], 1300, 0.65)
    box(c, 420, 980, 240, 300, C['paper'], 16)
    for dx in (-40, 40): circle(c, 540+dx, 1130, 22); fs(c, OUT, 0)
    if math.sin(t*25) > 0.3:
        c.set_source_rgb(1, 0.9, 0.3); c.set_line_width(8)
        c.move_to(700, 1050); c.line_to(760, 1110); c.line_to(730, 1120); c.line_to(800, 1200); c.stroke()
    cross(c, 540, 1130, 200, P(lt, d, 0.5, 0.8))
    if lt > d*0.08: rule_card(c, 2, "NUNCA A UN ENCHUFE", "DE LA PARED", W/2, 520, lt-d*0.08)
    if lt > d*0.55: chip(c, "PELIGRO: VECINOS Y OPERARIOS", W/2, 1540, lt-d*0.55, ic_warn, size=28, bg=C['red'], fg=C['paper'])
    post(c, t, 0.55)

def c17_9(c, lt, d, t):   # en el patio, alargadores, cargas por turnos
    patio(c, t, 0.85)
    generator(c, 860, 1480, 0.8, t, on=True, night=0.3)
    cable(c, 720, 1400, 160, 1430, 50, hexc('#E2A63B'))
    mini_fridge(c, 160, 1500, 0.6, 0.3)
    for i in range(4):
        x = 330+i*95; box(c, x, 1380, 60, 110, hexc('#26252A'), 10, 3)
        lvl = clamp((lt/d)*1.2-i*0.1); box(c, x+10, 1480-90*lvl, 40, 90*lvl, C['leaf'] if 'leaf' in C else (0.4, 0.8, 0.4), 4, 0)
    k = ease(P(lt, d, 0, 0.5))
    c.set_source_rgb(*C['paper']); c.set_line_width(6); c.set_dash([18, 12]); c.move_to(600, 1600); c.line_to(lerp(600, 840, k), 1600); c.stroke(); c.set_dash([])
    if lt > d*0.1: chip(c, "EN EL PATIO · LEJOS DE VENTANAS", W/2, 420, lt-d*0.1, ic_check, size=28)
    if lt > d*0.45: chip(c, "ALARGADORES DE EXTERIOR", W/2, 540, lt-d*0.45, ic_bolt, size=30)
    if lt > d*0.7: chip(c, "MÓVILES · RADIO · NEVERA", W/2, 1700, lt-d*0.7, size=30, bg=C['gold'])
    post(c, t, 0.55)

def c17_10(c, lt, d, t):  # Tomás va a rellenar con el motor caliente
    patio(c, t, 0.95)
    generator(c, 700, 1480, 1.0, t, on=lt < d*0.2, night=0.4)
    for i in range(3):  # calor
        x = 640+i*50; c.new_path(); c.move_to(x, 1220)
        for j in range(6): c.line_to(x+math.sin(t*6+j+i)*14, 1220-j*30)
        c.set_source_rgba(1, 0.5, 0.2, 0.6); c.set_line_width(6); c.stroke()
    x = lerp(220, 380, ease(P(lt, d, 0, 0.5)))
    tomas(c, x, 1500, 470, "carry", t, face=1, walk=lt*1.6 if lt < d*0.5 else 0, expr="focus", lit=0.75)
    box(c, x+40, 1180, 90, 120, C['red'], 10)
    if lt > d*0.4: chip(c, "MOTOR CALIENTE", 700, 940, lt-d*0.4, ic_warn, size=34, bg=C['red'], fg=C['paper'])
    post(c, t, 0.65, 0.09)

def c17_11(c, lt, d, t):  # REGLA 3: apagar y enfriar antes de repostar
    patio(c, t, 0.7)
    generator(c, W/2, 1500, 1.0, t, on=False, night=0.3)
    countdown(c, max(0, 15-int(lt*2.5)), 820, 1660, lt, label="ENFRIANDO")
    if lt > d*0.08: rule_card(c, 3, "APÁGALO Y QUE SE ENFRÍE", "ANTES DE ECHAR GASOLINA", W/2, 520, lt-d*0.08)
    if lt > d*0.55: chip(c, "SI SE DERRAMA, PUEDE ARDER", 380, 1720, lt-d*0.55, ic_warn, size=28)
    post(c, t, 0.55)

def c17_12(c, lt, d, t):  # luz en el patio; Rosa mira a Marta
    on = clamp(lt/0.6)
    patio(c, t, 0.8, lights=on)
    bulb(c, W/2, 520, on, t)
    rosa(c, 380, 1500, 430, "stand", t, face=1, expr="worried", lit=0.6+0.4*on)
    marta(c, 720, 1500, 540, "stand", t, face=-1, expr="neutral", lit=0.6+0.4*on)
    if lt > d*0.4: chip(c, "DÍA 6 · HAY LUZ", W/2, 1660, lt-d*0.4, ic_bolt, size=34)
    post(c, t, 0.5)

def c17_13(c, lt, d, t):  # Paco en la puerta del sótano
    k = ease(P(lt, d))
    c.save(); z = 1+0.25*k; c.translate(W/2, 1000); c.scale(z, z); c.translate(-W/2, -1000)
    patio(c, t, 0.85, lights=1)
    door(c, 600, 1320, 280, 700, open_=P(lt, d, 0.2, 0.45), light=0.0, night=0.9, t=t)
    if lt > d*0.35: paco(c, 760, 1340, 560, "stand", t, face=-1, expr="angry", lit=0.55)
    rosa(c, 300, 1340, 420, "stand", t, face=1, expr="shock" if lt > d*0.4 else "worried", lit=0.8)
    c.restore()
    if lt > d*0.55: chip(c, "«ESE GENERADOR ES MÍO»", W/2, 420, lt-d*0.55, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.72, 0.09)

SCENES = {"C17": [c17_0, c17_1, c17_2, c17_3, c17_4, c17_5, c17_6, c17_7, c17_8, c17_9, c17_10, c17_11, c17_12, c17_13]}
BOOMS = {"C17": [0, 13]}
CALM = {"C17"}
