"""Estilo «cine» — «Planta 8», capítulos 2 (Rosa, la del 9º, sin agua) y 3 (la radio de Julián)."""
from engine import *
from cine import *
from scenes_c4 import marta, julian, P, stairs, flat, glow, smoke, candle, FL
from scenes_c import facade as _facade
from cine import teo as _teo
import cairo, math, random

ROSA = dict(top=hexc('#7E5A8C'), top2=hexc('#654872'), legs=hexc('#3E3A44'), legs2=hexc('#2F2C34'), shoe=hexc('#2B2A2F'), skin=hexc('#E9C9AE'), hair=hexc('#8A8580'), bun=True)
def rosa(*a, **k): k['who'] = ROSA; return _teo(*a, **k)

def jug(c, x, base, s=1, fill=0.0):
    c.save(); c.translate(x, base); c.scale(s, s)
    rrect(c, -70, -200, 140, 200, 24); fs(c, tint(C['glass'], 0.3), 3)
    if fill > 0:
        c.save(); rrect(c, -66, -196, 132, 192, 22); c.clip(); c.rectangle(-70, -196*fill, 140, 200); c.set_source_rgba(*C['water'], 0.85); c.fill(); c.restore()
    box(c, -22, -228, 44, 30, C['teal'], 6, 3)
    c.set_source_rgb(*OUT); c.set_line_width(10); c.arc(40, -150, 40, -1.4, 1.4); c.stroke()
    c.restore()

def torch(c, x, y, ang, t, power=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    g = cairo.LinearGradient(0, 0, 520, 0); g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.45*power); g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
    c.new_path(); c.move_to(0, 0); c.line_to(520, -110); c.line_to(520, 110); c.close_path(); c.set_source(g); c.fill()
    box(c, -60, -14, 64, 28, C['dark2'], 6, 3); c.restore()

def radio(c, x, y, s, t, on=True, vol=1.0, wave=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    box(c, -200, -120, 400, 240, hexc('#8C5A3C'), 22)
    rrect(c, -170, -90, 180, 180, 16); fs(c, hexc('#5E3F2C'), 3)
    for i in range(7): c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(5); c.move_to(-160, -70+i*24); c.line_to(0, -70+i*24); c.stroke()
    rrect(c, 30, -90, 150, 60, 8); fs(c, hexc('#E9DFC4') if on else hexc('#7A7468'), 3)
    nx = 40+110*((t*0.05) % 1 if on else 0.4); c.set_source_rgb(*C['red']); c.set_line_width(4); c.move_to(nx, -84); c.line_to(nx, -36); c.stroke()
    for kx, a in ((70, 0.0), (150, -2.2+3.6*vol)):
        circle(c, kx, 40, 34); fs(c, C['dark2'], 3)
        c.set_source_rgb(*C['paper']); c.set_line_width(5); c.move_to(kx, 40); c.line_to(kx+math.cos(a-1.57)*26, 40+math.sin(a-1.57)*26); c.stroke()
    c.set_source_rgb(*OUT); c.set_line_width(6); c.move_to(160, -120); c.line_to(250, -300); c.stroke()
    c.restore()
    if on and wave > 0:
        for i in range(3):
            r = 60+((t*120+i*70) % 210)
            c.set_source_rgba(*C['paper'], 0.5*wave*(1-(r-60)/210)); c.set_line_width(5)
            c.arc(x-80*s, y, r*s, -0.8, 0.8); c.stroke(); c.arc(x-80*s, y, r*s, math.pi-0.8, math.pi+0.8); c.stroke()

def battery(c, x, y, s, lvl, col=None):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -120, -60, 240, 120, 18); fs(c, C['paper'], 5); box(c, 120, -24, 20, 48, C['ink'], 4, 0)
    col = col or (C['red'] if lvl < 0.2 else C['leaf'])
    if lvl > 0: rrect(c, -108, -48, 216*lvl, 96, 10); c.set_source_rgb(*col); c.fill()
    c.restore()

def wcistern(c, x, base, t, flush=0.0):
    box(c, x-110, base-560, 220, 170, C['paper'], 16)
    box(c, x-30, base-390, 60, 120, C['paper'], 8)
    box(c, x-150, base-280, 300, 70, C['paper'], 30)
    box(c, x-110, base-210, 220, 210, C['paper'], 20)
    if flush > 0:
        for i in range(10):
            ph = (t*2+i/10) % 1; circle(c, x-60+i*12, base-460+ph*200, 10); c.set_source_rgba(*C['water'], 0.8*flush); c.fill()

def title_rule(c, n, lt, t):
    grad_bg(c, hexc('#1C2234'), hexc('#0C0F18'))
    k = pop(lt, 0.4)
    c.save(); c.translate(W/2, 760); c.scale(max(k, 1e-3), max(k, 1e-3)); c.rotate(-0.04)
    rrect(c, -320, -130, 640, 260, 20); fs(c, C['red'], 0)
    txt(c, f"REGLA #{n}", 0, 50, 140, C['paper'], "Anton"); c.restore()

# ================== C2 ==================
def c2_0(c, lt, d, t):   # tres golpes en la puerta
    k = ease(P(lt, d))
    c.save(); z = 1+0.15*k; c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2, -900)
    wall_room(c, C['wall2'], FL, 0.95)
    door(c, 640, FL, 300, 720, light=0.35, night=0.95, knock=1.0 if (lt % 1.6) < 0.6 else 0, t=t)
    marta(c, 260, FL+30, 520, "listen", t, face=1, expr="shock", look=(0.6, 0), lit=0.45)
    knock_marks(c, 660, 620, lt)
    c.restore()
    c.set_source_rgba(0.02, 0.02, 0.04, 0.9); c.rectangle(0, 0, 120, H); c.fill(); c.rectangle(W-90, 0, 90, H); c.fill()
    post(c, t, 0.7, 0.09)

def c2_1(c, lt, d, t):   # «Marta, soy Rosa…»
    wall_room(c, C['wall2'], FL, 0.95)
    door(c, 540, FL, 300, 720, light=0.55, night=0.95, t=t)
    c.rectangle(440, FL+2, 50, 26); c.rectangle(590, FL+2, 50, 26); c.set_source_rgba(0, 0, 0, 0.7); c.fill()
    chip(c, "«MARTA, SOY ROSA»", W/2, 420, lt-0.2, size=40)
    if lt > d*0.5: chip(c, "«¿TIENES AGUA?»", W/2, 520, lt-d*0.5, ic_drop, size=40, bg=C['gold'])
    post(c, t, 0.7)

def c2_2(c, lt, d, t):   # abre: Rosa con garrafa y linterna
    wall_room(c, C['wall2'], FL, 0.85)
    door(c, 760, FL, 300, 720, open_=ease(P(lt, d, 0, 0.4)), light=0.0, night=0.85, t=t)
    rosa(c, 800, FL+40, 520, "carry", t, face=-1, expr="worried", lit=0.7)
    jug(c, 700, FL-160, 0.7, 0)
    torch(c, 860, 980, math.pi+0.5, t, 0.35+0.15*math.sin(t*9)*(lt > d*0.5))
    marta(c, 300, FL+40, 520, "stand", t, face=1, expr="focus", lit=0.6)
    if lt > d*0.5: chip(c, "ROSA · 9º", 800, 470, lt-d*0.5, size=32, bg=C['gold'], anchor=(800, 660))
    post(c, t, 0.6)

def c2_3(c, lt, d, t):   # 9º: ni una gota
    grad_bg(c, hexc("#20283A"), hexc("#11151F"))
    lvl = lerp(0.6, 0.27, ease(P(lt, d, 0, 0.5)))
    building_section(c, 470, 1160, 10, 78, 520, t, 9, lvl, False)
    chip(c, "9º: NI UNA GOTA", 760, 330, lt-0.3, ic_drop, size=34, bg=C['red'], fg=C['paper'], anchor=(560, 470))
    if lt > d*0.5: chip(c, "BOMBAS PARADAS", 330, 1270, lt-d*0.5, ic_bolt, size=30, anchor=(600, 1240))
    post(c, t, 0.45)

def c2_4(c, lt, d, t):   # y aquí va la primera regla
    title_rule(c, 1, lt, t); post(c, t, 0.5)

def c2_5(c, lt, d, t):   # 1,5 L por persona y día
    wall_room(c, floor_y=FL, night=0.5)
    for i in range(6): bottle(c, 160+i*150, FL+10, 1.1, fill=1.0 if lt > 0.3+i*0.2 else 0.0)
    rule_card(c, 1, "1,5 L DE AGUA", "POR PERSONA Y DÍA", W/2, 520, lt-0.2, ic_drop)
    if lt > d*0.6: chip(c, "SOLO PARA BEBER · MÍNIMO", W/2, 840, lt-d*0.6, size=30)
    post(c, t, 0.5)

def c2_6(c, lt, d, t):   # Marta hace cuentas
    wall_room(c, floor_y=FL, night=0.55)
    marta(c, 300, FL+40, 540, "think", t, expr="focus", look=(0.6, 0.3), lit=0.7)
    n = int(1+11*ease(P(lt, d, 0.1, 0.7)))
    for i in range(n): bottle(c, 560+(i % 4)*110, FL+10-(i//4)*190, 0.85, 1.0)
    chip(c, f"{n} BOTELLAS", 760, 420, lt-0.2, ic_drop, size=34)
    if lt > d*0.7: chip(c, "PARA DÍAS", 760, 520, lt-d*0.7, ic_check, size=34, bg=C['leaf'], fg=C['paper'])
    post(c, t, 0.5)

def c2_7(c, lt, d, t):   # la bañera tiene trampa
    c.set_source_rgb(*C['wall2']); c.paint(); tiles(c, 300, FL, C['tile'])
    c.rectangle(0, FL, W, H-FL); c.set_source_rgb(*C['floor2']); c.fill(); darken(c, 0.3)
    bathtub(c, 540, FL+10, fill=0.85, t=t)
    if lt > d*0.25:
        a = P(lt, d, 0.25, 0.4); c.set_source_rgba(*C['red'], a); c.set_line_width(22)
        c.move_to(300, 980); c.line_to(780, 1240); c.move_to(780, 980); c.line_to(300, 1240); c.stroke()
    if lt > d*0.35: rule_card(c, 2, "LA BAÑERA", "NO ES PARA BEBER", W/2, 520, lt-d*0.35)
    post(c, t, 0.5)

def c2_8(c, lt, d, t):   # cisterna: 6–9 L
    c.set_source_rgb(*C['wall2']); c.paint(); tiles(c, 300, FL, C['tile'])
    c.rectangle(0, FL, W, H-FL); c.set_source_rgb(*C['floor2']); c.fill(); darken(c, 0.3)
    wcistern(c, 300, FL+10, t, flush=P(lt, d, 0.1, 0.3))
    stat_card(c, "CADA DESCARGA", "6–9", "LITROS", 720, 620, lt-0.3, ic_drop)
    post(c, t, 0.5)

def c2_9(c, lt, d, t):   # separa: beber / lo demás
    wall_room(c, floor_y=FL, night=0.5)
    c.set_source_rgba(*C['paper'], 0.6); c.set_line_width(6); c.set_dash([20, 16]); c.move_to(W/2, 420); c.line_to(W/2, FL); c.stroke(); c.set_dash([])
    for i in range(4): bottle(c, 110+i*100, FL+10, 0.9, 1.0)
    c.save(); c.translate(780, 0); c.scale(0.5, 0.5); c.translate(-540, FL+10); bathtub(c, 540, FL+10, 0.8, t); c.restore()
    chip(c, "BEBER", 270, 520, lt-0.3, ic_drop, size=40, bg=C['water'], fg=C['paper'])
    chip(c, "LAVARSE · VÁTER", 800, 520, lt-0.9, size=34)
    post(c, t, 0.5)

def c2_10(c, lt, d, t):  # llena la garrafa de Rosa
    wall_room(c, floor_y=FL, night=0.6)
    k = P(lt, d, 0.1, 0.9)
    bottle(c, 530, 860, 1.2, 1-k)
    c.save(); c.translate(530, 700); c.rotate(2.2); c.translate(-530, -700); c.restore()
    water_stream(c, 560, 720, 1080, t, 0.9)
    jug(c, 560, FL+10, 1.1, k)
    rosa(c, 840, FL+40, 520, "stand", t, face=-1, expr="neutral", lit=0.7)
    marta(c, 270, FL+40, 520, "reach", t, face=1, expr="focus", lit=0.7)
    post(c, t, 0.55)

def c2_11(c, lt, d, t):  # linterna mejor que velas
    wall_room(c, floor_y=FL, night=0.85)
    candle(c, 300, 1100, 1.2, t, lit=lt < d*0.4)
    if lt < d*0.4: glow(c, 300, 960, 400, a=0.4)
    else:
        a = 1-0.5*math.sin(t*0)
        torch(c, 640, 1060, -0.3, t, 1.0)
    if lt > d*0.4:
        c.set_source_rgba(*C['red'], 0.9); c.set_line_width(14); c.move_to(220, 900); c.line_to(380, 1120); c.stroke()
    rule_card(c, 3, "LINTERNA", "MEJOR QUE VELAS", W/2, 520, lt-0.2, ic_bolt)
    if lt > d*0.55: chip(c, "+ PILAS DE REPUESTO", 760, 1180, lt-d*0.55, ic_check, size=30)
    post(c, t, 0.55)

def c2_12(c, lt, d, t):  # le da sus pilas
    wall_room(c, C['wall2'], FL, 0.8)
    door(c, 860, FL, 260, 680, open_=0.7, night=0.8, t=t)
    marta(c, 380, FL+40, 520, "reach", t, face=1, expr="neutral", lit=0.7)
    rosa(c, 720, FL+40, 520, "listen", t, face=-1, expr="worried", lit=0.7)
    for i in range(4):
        x = lerp(470, 600, ease(P(lt, d, 0.1, 0.5)))+i*22
        box(c, x, 820, 18, 50, C['gold'], 4, 2)
    post(c, t, 0.6)

def c2_13(c, lt, d, t):  # «va a durar días»
    grad_bg(c, hexc('#1A1E2A'), hexc('#07080D'))
    s = 1+0.15*ease(P(lt, d)); c.save(); c.translate(W/2, 1400); c.scale(s, s); c.translate(-W/2, -1400)
    rosa(c, 500, 1700, 1100, "stand", t, face=1, expr="worried", look=(0.6, 0.2), lit=0.6, shadow=False)
    c.restore()
    torch(c, 140, 1500, -0.6, t, 0.4)
    chip(c, "5º: TIENE UNA RADIO", W/2, 400, lt-0.6, size=34)
    if lt > d*0.55:
        kk = pop(lt-d*0.55, 0.35); c.save(); c.translate(W/2, 1500); c.scale(max(kk, 1e-3), max(kk, 1e-3))
        txt(c, "VA A DURAR DÍAS", 0, 0, 100, C['red2'], "Anton"); c.restore()
    post(c, t, 0.7, 0.09)

# ================== C3 ==================
def c3_0(c, lt, d, t):   # día 2: baja a oscuras al 5º
    k = ease(P(lt, d))
    c.save(); z = 1.05+0.15*k; c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2+40*k, -900)
    stairs(c, t, 0.92, beam=(lerp(600, 380, k)+40, lerp(1080, 1240, k)-260, 2.4))
    marta(c, lerp(620, 300, k), lerp(1080, 1300, k), 420, "phone", t, face=-1, walk=lt*1.4, expr="focus", lit=0.6)
    c.restore()
    time_card(c, "APAGÓN", "DÍA 2", f"PLANTA {max(5, 8-int(3*k))}", W/2, 360, lt-3.4)
    post(c, t, 0.65, 0.08)

def c3_1(c, lt, d, t):   # móvil sin cobertura
    stairs(c, t, 0.92); darken(c, 0.3)
    phone_alert(c, W/2, 800, 0.9, t, "SIN COBERTURA", "¿QUÉ PASA", "AHÍ FUERA?", "0 BARRAS")
    post(c, t, 0.6)

def c3_2(c, lt, d, t):   # Julián abre con un transistor
    wall_room(c, C['wall2'], FL, 0.85)
    door(c, 760, FL, 300, 720, open_=ease(P(lt, d, 0, 0.4)), light=0.5*P(lt, d, 0, 0.4), night=0.85, t=t)
    julian(c, 790, FL+40, 530, "phone", t, face=-1, expr="focus", lit=0.75)
    radio(c, 712, 860, 0.18, t)
    marta(c, 300, FL+40, 520, "stand", t, face=1, expr="neutral", lit=0.6)
    if lt > d*0.45: chip(c, "JULIÁN · 5º", 780, 450, lt-d*0.45, size=32, bg=C['gold'], anchor=(790, 640))
    post(c, t, 0.6)

def c3_3(c, lt, d, t):   # «Pasa»
    flat(c, t, 0.75, candle_on=False)
    radio(c, 230, 980, 0.38, t)
    julian(c, 520, FL+40, 530, "stand", t, face=-1, expr="neutral", lit=0.8)
    marta(c, 820, FL+40, 520, "stand", t, face=-1, expr="focus", lit=0.75)
    chip(c, "«ES LO ÚNICO QUE FUNCIONA»", W/2, 420, lt-0.4, size=32)
    post(c, t, 0.55)

def c3_4(c, lt, d, t):   # REGLA 1: radio a pilas o manivela
    grad_bg(c, hexc("#2A2420"), hexc("#14110F"))
    radio(c, W/2, 1100, 0.9+0.05*ease(P(lt, d)), t)
    rule_card(c, 1, "RADIO A PILAS", "O DE MANIVELA", W/2, 470, lt-0.2)
    post(c, t, 0.5)

def c3_5(c, lt, d, t):   # manivela: se recarga a mano
    grad_bg(c, hexc("#2A2420"), hexc("#14110F"))
    radio(c, W/2, 900, 0.8, t)
    a = t*5; cx, cy = W/2+240, 1120
    c.set_source_rgb(*C['steel']); c.set_line_width(18); c.move_to(cx, cy); c.line_to(cx+math.cos(a)*110, cy+math.sin(a)*110); c.stroke()
    circle(c, cx+math.cos(a)*110, cy+math.sin(a)*110, 22); fs(c, C['red'], 3); circle(c, cx, cy, 18); fs(c, C['dark'], 3)
    battery(c, 300, 1250, 0.8, P(lt, d, 0.1, 0.9))
    chip(c, "SIN PILAS · SIN ENCHUFE", W/2, 420, lt-0.4, ic_check, size=32)
    post(c, t, 0.5)

def c3_6(c, lt, d, t):   # 28-A-2025: radios y pilas agotadas
    grad_bg(c, hexc("#20283A"), hexc("#0E121C"))
    for i in range(4):
        box(c, 140+i*210, 1150, 170, 18, C['wood2'], 2)
    c.save(); c.translate(W/2, 640); k = pop(lt-0.3, 0.45); c.scale(max(k, 1e-3), max(k, 1e-3))
    rrect(c, -410, -230, 820, 460, 22); fs(c, C['paper'], 0)
    rrect(c, -270, -200, 540, 56, 28); fs(c, C['dark'], 0); txt(c, "28 ABRIL 2025 · BAZARES", 0, -160, 30, C['paper'])
    txt(c, "AGOTADAS", 0, 0, 120, C['red'], "Anton")
    txt(c, "RADIOS PORTÁTILES Y PILAS", 0, 90, 44, C['ink'], "Anton")
    c.restore()
    chip(c, "ESTANTES VACÍOS", W/2, 1060, lt-d*0.6, size=30)
    post(c, t, 0.55)

def c3_7(c, lt, d, t):   # baja el volumen: ahorrar pilas
    flat(c, t, 0.8, candle_on=False)
    v = 1-0.8*ease(P(lt, d, 0.1, 0.6))
    radio(c, W/2, 900, 0.75, t, vol=v, wave=v)
    julian(c, 200, FL+40, 520, "reach", t, face=1, expr="focus", lit=0.75)
    battery(c, 820, 1250, 0.6, 0.35)
    chip(c, "AHORRAR PILAS", 820, 1140, lt-d*0.5, size=30)
    post(c, t, 0.55)

def c3_8(c, lt, d, t):   # REGLA 2: kit 72 h
    wall_room(c, floor_y=FL, night=0.55)
    box(c, 280, 900, 520, 340, C['red'], 30); box(c, 440, 860, 200, 60, C['dark'], 20, 3)
    rrect(c, 500, 1010, 80, 120, 4); c.set_source_rgb(*C['paper']); c.fill(); rrect(c, 480, 1040, 120, 60, 4); c.fill()
    countdown(c, 72*60*(1-0.1*P(lt, d)), W/2, 1380, lt-0.4, label="HORAS")
    rule_card(c, 2, "KIT PARA", "3 DÍAS · 72 H", W/2, 500, lt-0.2)
    post(c, t, 0.5)

def c3_9(c, lt, d, t):   # REGLA 3: batería externa cargada
    grad_bg(c, hexc("#20283A"), hexc("#0E121C"))
    battery(c, W/2, 1100, 1.4, 0.2+0.8*ease(P(lt, d, 0.1, 0.6)))
    rule_card(c, 3, "BATERÍA EXTERNA", "CARGADA ANTES", W/2, 520, lt-0.2, ic_bolt)
    if lt > d*0.6: chip(c, "SIN LUZ NO SE RECARGA", W/2, 1330, lt-d*0.6, ic_warn, size=30)
    post(c, t, 0.5)

def c3_10(c, lt, d, t):  # 12 %
    flat(c, t, 0.85, candle_on=False)
    marta(c, 360, FL+40, 540, "phone", t, face=1, expr="worried", look=(0.6, 0.4), lit=0.7)
    glow(c, 430, 860, 240, (0.75, 0.88, 1), 0.35)
    battery(c, 760, 640, 1.0, 0.12)
    txt(c, "12 %", 760, 820, 90, C['red2'], "Anton")
    post(c, t, 0.6)

def c3_11(c, lt, d, t):  # la música se corta: aviso oficial
    grad_bg(c, hexc("#1A1E2A"), hexc("#07080D"))
    cut = lt > d*0.3
    radio(c, W/2, 1000, 0.8, t, wave=0 if cut else 1)
    if cut:
        k = pop(lt-d*0.3, 0.3); c.save(); c.translate(W/2, 520); c.scale(max(k, 1e-3), max(k, 1e-3))
        rrect(c, -340, -70, 680, 140, 16); fs(c, C['red'], 0); txt(c, "AVISO OFICIAL", 0, 32, 80, C['paper'], "Anton"); c.restore()
    post(c, t, 0.6)

def c3_12(c, lt, d, t):  # no salgan de casa esta noche
    flat(c, t, 0.9, candle_on=False); darken(c, 0.3)
    phone_alert(c, W/2, 820, 0.95, t, "LOCUTORA", "NO SALGAN", "ESTA NOCHE", "SIN MOTIVO")
    if lt > d*0.6: chip(c, "¿POR QUÉ?", W/2, 1260, lt-d*0.6, size=40, bg=C['gold'])
    post(c, t, 0.65)

def c3_13(c, lt, d, t):  # silencio; pasos subiendo
    k = ease(P(lt, d))
    stairs(c, t, 0.95, beam=(240, 1500, -1.1+0.1*math.sin(t*3)) if lt > d*0.5 else None)
    darken(c, 0.25)
    if lt > d*0.5:
        silhouette(c, lerp(200, 330, k), lerp(1600, 1450, k), 380, t)
        for i in range(3):
            kk = pop(((lt*1.2) % 1.6)-i*0.25, 0.2)
            if kk > 0:
                c.save(); c.translate(560+i*120, 1200-i*90); c.scale(kk, kk); txt(c, "PASOS", 0, 0, 46, C['paper'], "Anton"); c.restore()
    if lt < d*0.5:
        txt(c, "· · ·", W/2, 820, 90, C['paper'], "Anton", a=0.6)
    post(c, t, 0.75, 0.09)

SCENES = {"C2": [c2_0, c2_1, c2_2, c2_3, c2_4, c2_5, c2_6, c2_7, c2_8, c2_9, c2_10, c2_11, c2_12, c2_13],
          "C3": [c3_0, c3_1, c3_2, c3_3, c3_4, c3_5, c3_6, c3_7, c3_8, c3_9, c3_10, c3_11, c3_12, c3_13]}
BOOMS = {"C2": [0, 13], "C3": [11, 13]}
CALM = {"C2", "C3"}
