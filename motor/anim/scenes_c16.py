"""Estilo «cine» — serie APAGON «Planta 8», parte 16: cansancio y peleas en el portal; el sótano."""
from engine import *
from cine import *
from cine import teo as _teo
from scenes_c4 import marta, julian, dani, P, smoke, glow, stairs, flat, candle, FL
from scenes_c5 import paco, generator
import cairo, math, random

TOMAS = dict(top=hexc('#3E6E9E'), top2=hexc('#2F5880'), legs=hexc('#3A3D44'), legs2=hexc('#2B2E34'), shoe=hexc('#E9E4DA'), skin=hexc('#EBC9A8'), hair=hexc('#8A5A3A'))
def tomas(*a, **k): k['who'] = TOMAS; return _teo(*a, **k)

def bucket(c, x, base, s=1.0, fill=0.8, night=0.5):
    m = lambda cc: mix(cc, C['night1'], night*0.5)
    c.save(); c.translate(x, base); c.scale(s, s)
    c.new_path(); c.move_to(-60, -130); c.line_to(60, -130); c.line_to(45, 0); c.line_to(-45, 0); c.close_path(); fs(c, m(C['red']), 3)
    if fill > 0:
        c.save(); c.translate(0, -130); c.scale(1, 0.25); circle(c, 0, 0, 58); c.restore(); fs(c, m(C['water']), 2)
    c.set_source_rgb(*OUT); c.set_line_width(4); c.arc(0, -130, 60, math.pi, 2*math.pi); c.stroke()
    c.restore()

def key(c, x, y, s, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    circle(c, 0, 0, 46); fs(c, C['gold'], 4); circle(c, 0, 0, 18); fs(c, C['night1'], 3)
    box(c, 40, -12, 170, 24, C['gold'], 4, 4)
    for dx in (150, 185): box(c, dx, 8, 18, 34, C['gold'], 2, 3)
    # etiqueta
    c.set_source_rgb(*OUT); c.set_line_width(3); c.move_to(-30, 30); c.line_to(-70, 110); c.stroke()
    c.save(); c.translate(-90, 170); c.rotate(-0.25); box(c, -90, -55, 180, 110, C['paper'], 10, 4)
    txt(c, "SÓTANO", 0, 14, 38, C['ink'], "Anton"); c.restore()
    c.restore()

def lobby(c, t, night=0.8, cam=0.0):
    """portal del edificio: buzones, puerta de cristal, suelo de baldosa"""
    wall_room(c, C['wall2'], FL, night)
    c.save(); c.translate(-cam, 0)
    # buzones
    for r in range(3):
        for k in range(5):
            box(c, 120+k*95, 520+r*80, 85, 70, mix(C['steel2'], C['night1'], night*0.6), 4, 3)
            c.rectangle(135+k*95, 540+r*80, 55, 8); c.set_source_rgba(0, 0, 0, 0.5); c.fill()
    # puerta de cristal a la calle
    box(c, 720, 380, 300, 880, mix(C['dark2'], C['night1'], night*0.5), 4)
    c.rectangle(745, 405, 250, 830); c.set_source_rgb(*mix(C['glass'], C['night1'], night*0.85)); c.fill()
    c.restore()
    c.rectangle(0, FL, W, H-FL); c.set_source_rgb(*mix(C['tile'], C['night1'], night*0.8)); c.fill()
    for i in range(12):
        c.set_source_rgba(0, 0, 0, 0.15); c.set_line_width(3); c.move_to(i*100-cam*0.5, FL); c.line_to(i*140-300-cam, H); c.stroke()

def torch_beam(c, x, y, ang, L=700, a=0.45):
    c.save(); c.translate(x, y); c.rotate(ang)
    g = cairo.LinearGradient(0, 0, L, 0); g.add_color_stop_rgba(0, 1, 0.95, 0.8, a); g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0)
    c.new_path(); c.move_to(0, 0); c.line_to(L, -L*0.22); c.line_to(L, L*0.22); c.close_path(); c.set_source(g); c.fill(); c.restore()

# ---------------- escenas ----------------
def c16_0(c, lt, d, t):   # gancho: la llave tiembla en la mano
    k = ease(P(lt, d))
    grad_bg(c, hexc("#1A1410"), hexc("#07060A"))
    glow(c, 600, 820, 620, (1, 0.62, 0.28), 0.45+0.08*math.sin(t*9))
    c.save(); z = 1.0+0.3*k; c.translate(W/2, 860); c.scale(z, z); c.translate(-W/2, -860)
    shake = math.sin(t*38)*4
    # mano
    c.set_source_rgb(*hexc('#E8C3A0')); rrect(c, 330+shake, 900, 300, 220, 80); c.fill()
    key(c, 520+shake, 860, 1.4, -0.35+0.03*math.sin(t*20))
    for f in range(4):
        c.set_source_rgb(*hexc('#D2A884')); rrect(c, 330+f*62+shake, 860, 52, 120, 26); c.fill()
    c.restore()
    c.set_source_rgba(0.02, 0.02, 0.03, 0.92); c.rectangle(0, 0, W, 300); c.fill(); c.rectangle(0, 1450, W, H-1450); c.fill()
    candle(c, 180, 1440, 0.7, t)
    if lt > d*0.55: chip(c, "SÓTANO", W/2, 1340, lt-d*0.55, ic_warn, size=38, bg=C['red'], fg=C['paper'])
    post(c, t, 0.75, 0.09)

def c16_1(c, lt, d, t):   # nadie ha dormido; amanece el sexto día
    k = P(lt, d)
    flat(c, t, night=lerp(0.85, 0.55, k), candle_on=lt < d*0.6)
    glow(c, 790, 620, 600, (1, 0.75, 0.5), 0.25*k)
    marta(c, 380, 1300, 560, "sit", t, face=1, expr="sleep" if math.sin(t*1.3) > 0.5 else "worried", lit=0.8)
    time_card(c, "DÍA", "6", "SIN LUZ", W/2, 470, lt-0.3) if lt > 0.3 else None
    post(c, t, 0.6)

def c16_2(c, lt, d, t):   # portal: doce cubos de lluvia
    cam = 60*ease(P(lt, d))
    lobby(c, t, 0.75, cam)
    torch_beam(c, 60, 700, 0.35, 900, 0.3)
    for i in range(12):
        bucket(c, 160+(i % 6)*150-cam*1.2, 1260+(i//6)*90, 0.8, night=0.4)
    if lt > d*0.4: chip(c, "12 CUBOS", W/2, 400, lt-d*0.4, ic_drop, size=36)
    post(c, t, 0.6)

def c16_3(c, lt, d, t):   # Paco y Dani se empujan
    lobby(c, t, 0.75)
    torch_beam(c, 980, 600, 2.7, 900, 0.3)
    push = ease(P(lt, d, 0.35, 0.55))
    paco(c, 380-60*push, 1300, 560, "reach" if lt < d*0.35 else "alarm", t, face=1, expr="angry", lit=0.8)
    dani(c, 700, 1300, 560, "reach" if lt > d*0.35 else "stand", t, face=-1, expr="angry", lit=0.8)
    bucket(c, 540, 1330, 0.9, night=0.4)
    if lt > d*0.6 and (t*2.5) % 1 < 0.6: txt(c, "¡EH!", 800, 640, 90, C['red2'], "Anton")
    if lt < d*0.4: chip(c, "«ES DE QUIEN LA SUBIÓ»", W/2, 420, lt-0.2, size=32)
    post(c, t, 0.62)

def c16_4(c, lt, d, t):   # REGLA 1
    grad_bg(c, hexc("#1B2233"), hexc("#0B0E16"))
    for i, (x, col) in enumerate(((250, C['red']), (540, C['gold']), (830, C['teal']))):
        k = pop(lt-0.4-i*0.25, 0.4)
        if k > 0:
            c.save(); c.translate(x, 1180+math.sin(t*2+i)*8); c.scale(k, k); circle(c, 0, 0, 110); fs(c, col, 4)
            txt(c, ("ESTRÉS", "ANSIEDAD", "MIEDO")[i], 0, 12, 34, C['paper'], "Anton"); c.restore()
    rule_card(c, 1, "ES NORMAL", "SENTIR MIEDO", W/2, 640, lt)
    if lt > d*0.6: chip(c, "NO TE PASA SOLO A TI", W/2, 1420, lt-d*0.6, ic_check, size=32)
    post(c, t, 0.55)

def c16_5(c, lt, d, t):   # Marta se mete en medio
    lobby(c, t, 0.7)
    k = ease(P(lt, d, 0, 0.4))
    paco(c, 260, 1300, 540, "stand", t, face=1, expr="angry", lit=0.75)
    dani(c, 840, 1300, 540, "stand", t, face=-1, expr="worried", lit=0.75)
    marta(c, lerp(1200, 550, k), 1310, 600, "alarm" if k > 0.95 else "stand", t, face=-1, walk=lt*1.6 if k < 0.95 else 0, expr="focus", lit=0.95)
    if lt > d*0.5: chip(c, "«LO HABLAMOS TODOS»", W/2, 420, lt-d*0.5, size=32, bg=C['gold'])
    post(c, t, 0.58)

def c16_6(c, lt, d, t):   # REGLA 2
    grad_bg(c, hexc("#1B2233"), hexc("#0B0E16"))
    for i in range(6):
        a = i/6*2*math.pi+t*0.15; x = W/2+math.cos(a)*300; y = 1200+math.sin(a)*120
        circle(c, x, y, 40); fs(c, (C['red'], C['gold'], C['teal'], C['leaf'], C['steel'], C['water'])[i], 3)
    circle(c, W/2, 1200, 70); fs(c, C['paper'], 3); ic_check(c, W/2, 1200, 30)
    rule_card(c, 2, "RESOLVEDLO", "ENTRE TODOS", W/2, 640, lt)
    if lt > d*0.55: chip(c, "HABLAD · ESCUCHAD · APOYAOS", W/2, 1440, lt-d*0.55, size=30)
    post(c, t, 0.55)

def c16_7(c, lt, d, t):   # reparten el agua por pisos
    lobby(c, t, 0.65)
    for i in range(6):
        k = ease(P(lt, d, i*0.1, i*0.1+0.3))
        bucket(c, lerp(540, 140+i*160, k), lerp(1300, 1240, k), 0.75, night=0.3)
        if k > 0.9: txt(c, f"{i+2}º", 140+i*160, 1290, 30, C['paper'])
    julian(c, 540, 1320, 520, "carry", t, face=1, expr="neutral", lit=0.85)
    if lt > d*0.5: chip(c, "1º CUBO: EL BEBÉ DEL 2º", W/2, 420, lt-d*0.5, ic_drop, size=32)
    post(c, t, 0.55)

def c16_8(c, lt, d, t):   # Julián se duerme de pie
    lobby(c, t, 0.75)
    k = ease(P(lt, d, 0.2, 0.8))
    c.save(); c.translate(520, 1300); c.rotate(-0.12*k); c.translate(-520, -1300)
    julian(c, 520, 1300, 600, "stand", t, face=-1, expr="sleep" if k > 0.3 else "worried", lit=0.8)
    c.restore()
    if k > 0.4:
        for i in range(3):
            ph = (t*0.6+i/3) % 1
            txt(c, "Z", 640+ph*120, 640-ph*160, 40+ph*30, C['paper'], "Anton", a=1-ph)
    post(c, t, 0.65)

def c16_9(c, lt, d, t):   # REGLA 3
    grad_bg(c, hexc("#1B2233"), hexc("#0B0E16"))
    # balanza trabajo / descanso
    ang = 0.15*math.sin(t*1.2)*(1-P(lt, d))
    c.save(); c.translate(W/2, 1100); c.rotate(ang)
    c.set_source_rgb(*C['steel']); c.set_line_width(12); c.move_to(-320, 0); c.line_to(320, 0); c.stroke()
    for sx, lab in ((-1, "TRABAJO"), (1, "DESCANSO")):
        c.set_line_width(4); c.move_to(sx*300, 0); c.line_to(sx*300-60, 140); c.move_to(sx*300, 0); c.line_to(sx*300+60, 140); c.stroke()
        box(c, sx*300-110, 140, 220, 40, C['gold'] if sx < 0 else C['teal'], 10, 3)
        txt(c, lab, sx*300, 240, 34, C['paper'], "Anton")
    c.restore()
    c.set_source_rgb(*C['steel2']); c.rectangle(W/2-10, 1100, 20, 300); c.fill()
    rule_card(c, 3, "EQUILIBRA TRABAJO", "Y DESCANSO", W/2, 600, lt)
    if lt > d*0.55: chip(c, "HORARIOS PARA COMER Y DORMIR", W/2, 1480, lt-d*0.55, ic_clock, size=28)
    post(c, t, 0.55)

def c16_10(c, lt, d, t):  # turnos: unos vigilan, otros duermen
    lobby(c, t, 0.85)
    dani(c, 820, 1300, 540, "stand", t, face=-1, expr="focus", lit=0.7)
    torch_beam(c, 760, 960, 3.3, 700, 0.35)
    julian(c, 300, 1300, 520, "sit", t, face=1, expr="sleep", lit=0.6)
    box(c, 40, 260, 400, 260, C['paper'], 12, 4)
    txt(c, "TURNOS", 240, 320, 40, C['ink'], "Anton")
    for i, s in enumerate(("22-00 DANI·PACO", "00-02 MARTA·TOMÁS", "02-04 JULIÁN·LUCÍA")):
        if lt > 0.3+i*0.35: txt(c, s, 240, 380+i*44, 26, C['ink'])
    post(c, t, 0.62)

def c16_11(c, lt, d, t):  # nada de alcohol
    lobby(c, t, 0.75)
    paco(c, 420, 1300, 560, "reach", t, face=1, expr="neutral", lit=0.8)
    k = ease(P(lt, d, 0.3, 0.7))
    # botella que Marta aparta
    bx = lerp(640, 900, k)
    c.save(); c.translate(bx, 1000); c.rotate(0.4*k)
    box(c, -35, -120, 70, 170, hexc('#5E6650'), 14, 4); box(c, -14, -170, 28, 55, hexc('#5E6650'), 6, 4); c.restore()
    marta(c, 820, 1300, 580, "reach", t, face=-1, expr="focus", lit=0.85)
    if lt > d*0.5:
        c.set_source_rgba(*C['red2'], 0.95); c.set_line_width(18); c.arc(bx, 960, 140, 0, 2*math.pi); c.stroke()
        c.move_to(bx-100, 860); c.line_to(bx+100, 1060); c.stroke()
        chip(c, "NADA DE ALCOHOL", W/2, 420, lt-d*0.5, ic_warn, size=34, bg=C['red'], fg=C['paper'])
    post(c, t, 0.6)

def c16_12(c, lt, d, t):  # bajan al sótano, la llave encaja
    grad_bg(c, hexc("#14161C"), hexc("#050608"))
    k = ease(P(lt, d))
    c.save(); c.translate(-80*k, 0)
    door(c, 760, 1300, 300, 720, night=0.9)
    txt(c, "SÓTANO", 760, 520, 34, C['steel'], "Anton")
    tomas(c, 260, 1320, 470, "stand", t, face=1, expr="worried", lit=0.55)
    julian(c, 420, 1320, 520, "stand", t, face=1, expr="focus", lit=0.6)
    marta(c, lerp(520, 600, k), 1320, 560, "reach" if lt > d*0.5 else "stand", t, face=1, expr="focus", lit=0.75)
    c.restore()
    torch_beam(c, 470, 1000, -0.05, 600, 0.4)
    if lt > d*0.7 and (lt-d*0.7) < 0.8: txt(c, "CLIC", 760-80*k, 860, 64, C['paper'], "Anton")
    post(c, t, 0.72)

def c16_13(c, lt, d, t):  # oscuridad, un motor, luz al fondo
    grad_bg(c, hexc("#08090C"), hexc("#020203"))
    k = ease(P(lt, d))
    c.save(); z = 1+0.25*k; c.translate(W/2, 1000); c.scale(z, z); c.translate(-W/2, -1000)
    # puerta del fondo con luz bajo la rendija
    door(c, W/2, 1200, 260, 620, light=0.0, night=1.0)
    g = cairo.LinearGradient(0, 1200, 0, 1420); g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.8+0.15*math.sin(t*30)); g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
    c.new_path(); c.move_to(W/2-130, 1200); c.line_to(W/2+130, 1200); c.line_to(W/2+300, 1420); c.line_to(W/2-300, 1420); c.close_path(); c.set_source(g); c.fill()
    c.restore()
    for i in range(3):
        r = 80+((t*140+i*60) % 180)
        c.set_source_rgba(1, 1, 1, 0.35*(1-((t*140+i*60) % 180)/180)); c.set_line_width(5); c.arc(W/2, 880, r, -2.3, -0.8); c.stroke()
    if (t*6) % 1 < 0.5: txt(c, "BRRRM", W/2, 700, 52, C['steel'], "Anton")
    silhouette(c, 160, 1500, 480, t)
    if lt > d*0.55: chip(c, "¿QUIÉN TIENE LUZ?", W/2, 1600, lt-d*0.55, ic_bolt, size=36, bg=C['gold'])
    post(c, t, 0.8, 0.1)

SCENES = {"C16": [c16_0, c16_1, c16_2, c16_3, c16_4, c16_5, c16_6, c16_7, c16_8, c16_9, c16_10, c16_11, c16_12, c16_13]}
BOOMS = {"C16": [0, 13]}
CALM = {"C16"}
