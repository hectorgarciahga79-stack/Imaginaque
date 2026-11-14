"""Estilo «cine» — serie APAGON «Planta 8», capítulo 4: velas e incendios (Marta, Julián, Dani)."""
from engine import *
from cine import *
from cine import teo as _teo
import cairo, math, random

FL = 1260
JULIAN = dict(top=hexc('#7A5A44'), top2=hexc('#5E4535'), legs=hexc('#4A4A52'), legs2=hexc('#38383F'), shoe=hexc('#2B2A2F'), skin=hexc('#E3BFA0'), hair=hexc('#C9C4BC'))
DANI = dict(top=hexc('#5E7F3E'), top2=hexc('#4A6630'), legs=hexc('#2F3A52'), legs2=hexc('#252E42'), shoe=hexc('#E9E4DA'), skin=hexc('#D9A97F'), hair=hexc('#1E1A18'))

def marta(*a, **k): k['who'] = MARTA; return _teo(*a, **k)
def julian(*a, **k): k['who'] = JULIAN; return _teo(*a, **k)
def dani(*a, **k): k['who'] = DANI; return _teo(*a, **k)

def P(lt, d, a=0.0, b=1.0): return clamp((lt/d-a)/(b-a)) if d > 0 else 1.0

def smoke(c, t, x0, y0, x1, y1, n=16, a=0.35, seed=3, rise=60, col=(0.32, 0.31, 0.33)):
    r = random.Random(seed)
    for i in range(n):
        bx = r.uniform(x0, x1); by = r.uniform(y0, y1); rr = r.uniform(70, 170); ph = r.uniform(0, 6)
        x = bx+math.sin(t*0.6+ph)*40; y = by-((t*rise+ph*40) % 220)
        g = cairo.RadialGradient(x, y, 5, x, y, rr)
        g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
        c.set_source(g); c.arc(x, y, rr, 0, 2*math.pi); c.fill()

def glow(c, x, y, r, col=(1, 0.6, 0.25), a=0.5):
    g = cairo.RadialGradient(x, y, 5, x, y, r); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g); c.paint()

def flame(c, x, y, s, t):
    fl = 1+0.12*math.sin(t*13)+0.06*math.sin(t*29)
    c.new_path(); c.move_to(x, y-60*s*fl); c.curve_to(x+26*s, y-14*s, x+20*s, y+8*s, x, y+10*s); c.curve_to(x-20*s, y+8*s, x-26*s, y-14*s, x, y-60*s*fl); fs(c, C['gold'], 0)
    c.new_path(); c.move_to(x, y-30*s*fl); c.curve_to(x+11*s, y-6*s, x+8*s, y+6*s, x, y+8*s); c.curve_to(x-8*s, y+6*s, x-11*s, y-6*s, x, y-30*s*fl); fs(c, (1, 0.95, 0.7), 0)

def candle(c, x, base, s, t, lit=True):
    box(c, x-22*s, base-110*s, 44*s, 110*s, C['cream'], 5, 3)
    c.set_source_rgb(*OUT); c.set_line_width(3); c.move_to(x, base-110*s); c.line_to(x, base-124*s); c.stroke()
    if lit: flame(c, x, base-128*s, s, t)

def stairs(c, t, night=0.85, smoke_k=0.0, beam=None):
    grad_bg(c, mix(C['wall2'], C['night1'], night), mix(C['wall'], C['night1'], night*0.95))
    # tramos de escalera en zigzag
    for f in range(3):
        y0 = 1500-f*520
        for s in range(9):
            x = 160+s*70 if f % 2 == 0 else 920-s*70
            yy = y0-s*48
            c.rectangle(min(x, x+70*(1 if f % 2 == 0 else -1)), yy, 72, 48+520); c.set_source_rgb(*mix(C['steel2'], C['night1'], night*0.8)); c.fill()
            c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(3); c.move_to(x, yy); c.line_to(x+70*(1 if f % 2 == 0 else -1), yy); c.stroke()
        # barandilla
        c.set_source_rgb(*mix(C['wood2'], C['night1'], night*0.6)); c.set_line_width(10)
        if f % 2 == 0: c.move_to(160, y0-160); c.line_to(790, y0-160-8*48)
        else: c.move_to(920, y0-160); c.line_to(290, y0-160-8*48)
        c.stroke()
    c.set_source_rgba(0.3, 1, 0.5, 0.28); rrect(c, 760, 330, 180, 60, 10); c.fill()
    txt(c, "SALIDA", 850, 372, 30, (0.6, 1, 0.75))
    if beam:
        bx, by, ang = beam
        c.save(); c.translate(bx, by); c.rotate(ang)
        g = cairo.LinearGradient(0, 0, 700, 0); g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.55); g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0)
        c.new_path(); c.move_to(0, 0); c.line_to(700, -150); c.line_to(700, 150); c.close_path(); c.set_source(g); c.fill(); c.restore()
    if smoke_k > 0: smoke(c, t, 0, 900, W, 1700, 22, 0.42*smoke_k, rise=45)

def flat(c, t, night=0.8, candle_on=True):
    wall_room(c, C['wall2'], FL, night)
    window_city(c, 600, 380, 380, 480, t, night=0.95, lights_out=1)
    # mesa con radio y vela
    box(c, 80, 1060, 360, 30, mix(C['wood'], C['night1'], night*0.5), 6)
    box(c, 110, 1090, 26, 170, mix(C['wood2'], C['night1'], night*0.5), 4, 3); box(c, 384, 1090, 26, 170, mix(C['wood2'], C['night1'], night*0.5), 4, 3)
    box(c, 120, 980, 150, 80, mix(C['dark2'], C['night1'], 0.2), 10, 3); circle(c, 160, 1020, 22); fs(c, C['steel2'], 3)
    c.set_source_rgb(*OUT); c.set_line_width(4); c.move_to(250, 985); c.line_to(300, 900); c.stroke()
    if candle_on:
        glow(c, 370, 990, 520, a=0.45); candle(c, 370, 1060, 0.6, t)

# ---------------- escenas ----------------
def c4_0(c, lt, d, t):   # gancho: pasos en la escalera, ¡fuego!
    k = ease(P(lt, d))
    c.save(); z = 1.0+0.22*k; c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2-60*k, -900+40*k)
    stairs(c, t, 0.9, smoke_k=P(lt, d, 0.2, 0.9), beam=(lerp(330, 560, k), lerp(1240, 1080, k), -0.9+0.25*math.sin(t*2)))
    dani(c, lerp(260, 560, k), lerp(1330, 1080, k), 420, "stand", t, face=1, walk=lt*1.8, expr="shock", lit=0.6)
    c.restore()
    # primer plano oscuro: barandilla
    c.set_source_rgba(0.03, 0.03, 0.05, 0.92); c.set_line_width(46); c.move_to(-40, 1500); c.line_to(W+40, 1180); c.stroke()
    for x in range(40, W, 160): c.rectangle(x, 1180+(W-x)*0.3-20, 22, 520); c.fill()
    if lt > d*0.72:
        kk = pop(lt-d*0.72, 0.3); c.save(); c.translate(W/2, 520); c.rotate(-0.08); c.scale(max(kk, 1e-3), max(kk, 1e-3))
        txt(c, "¡FUEGO!", 0, 0, 170, C['red2'], "Anton"); c.restore()
    post(c, t, 0.62, 0.08)

def c4_1(c, lt, d, t):   # Dani tose: una vela, las cortinas del 4º
    stairs(c, t, 0.85, smoke_k=0.6)
    darken(c, 0.15)
    glow(c, 300, 1000, 420, (0.75, 0.88, 1), 0.25)
    dani(c, 640, FL+60, 540, "think", t, face=-1, expr="worried", look=(0.2, 0.3), lit=0.75)
    marta(c, 280, FL+60, 520, "stand", t, face=1, expr="shock", lit=0.7)
    if lt > d*0.15: chip(c, "DANI · 6º", 700, 470, lt-d*0.15, size=30, bg=C['gold'], anchor=(650, 700))
    if lt > d*0.55: chip(c, "4º: UNA VELA, LAS CORTINAS", W/2, 1420, lt-d*0.55, ic_warn, size=32)
    post(c, t, 0.58)

def c4_2(c, lt, d, t):   # dato real: Madrid, 28-A-2025
    grad_bg(c, hexc("#1A1410"), hexc("#0B0A0C"))
    glow(c, W/2, 1250, 700, a=0.5)
    c.save(); s = 1+0.12*ease(P(lt, d)); c.translate(W/2, 1300); c.scale(s, s); candle(c, 0, 120, 1.6, t); c.restore()
    c.save(); c.translate(W/2, 640); k = pop(lt-0.3, 0.45); c.scale(max(k, 1e-3), max(k, 1e-3))
    c.set_source_rgba(0, 0, 0, 0.3); rrect(c, -410+10, -250+14, 820, 500, 22); c.fill()
    rrect(c, -410, -250, 820, 500, 22); fs(c, C['paper'], 0)
    rrect(c, -270, -220, 540, 56, 28); fs(c, C['dark'], 0); txt(c, "MADRID · 28 ABRIL 2025", 0, -180, 30, C['paper'])
    txt(c, "APAGÓN", 0, -60, 90, C['red'], "Anton")
    txt(c, "UNA MUJER MUERE", 0, 40, 56, C['ink'], "Anton")
    txt(c, "EN UN INCENDIO EN CASA", 0, 105, 44, C['ink'], "Anton")
    c.restore()
    if lt > d*0.6: chip(c, "POLICÍA: PUDO CAUSARLO UNA VELA", W/2, 1000, lt-d*0.6, ic_warn, size=30)
    post(c, t, 0.6)

def c4_3(c, lt, d, t):   # Marta quiere subir; Julián la sujeta
    stairs(c, t, 0.85, smoke_k=0.5)
    x = lerp(380, 560, ease(P(lt, d, 0, 0.45)))
    marta(c, x, FL+60, 520, "reach" if lt > d*0.45 else "stand", t, face=1, walk=0 if lt > d*0.45 else lt*1.8, expr="focus", lit=0.75)
    julian(c, lerp(150, x-150, ease(P(lt, d, 0.4, 0.7))), FL+60, 530, "reach" if lt > d*0.5 else "stand", t, face=1, expr="worried", lit=0.7)
    chip(c, "SU CASA: 8º", 820, 430, lt-0.3, ic_bolt, size=32, anchor=(820, 600))
    if lt > d*0.6: chip(c, "¡NO!", 300, 600, lt-d*0.6, size=44, bg=C['red'], fg=C['paper'])
    post(c, t, 0.58)

def c4_4(c, lt, d, t):   # REGLA 1: humo en la escalera → no salgas
    c.save(); z = 1.05+0.08*ease(P(lt, d)); c.translate(W/2, 960); c.scale(z, z); c.translate(-W/2, -960)
    stairs(c, t, 0.9, smoke_k=0.4+0.6*P(lt, d))
    c.restore()
    smoke(c, t*1.3, 0, 300, W, 1500, 18, 0.25+0.25*P(lt, d), seed=9, rise=70)
    if lt > d*0.12: rule_card(c, 1, "¿HUMO EN LA ESCALERA?", "NO SALGAS", W/2, 640, lt-d*0.12)
    if lt > d*0.6: chip(c, "AHÍ SE ACUMULAN HUMO Y CALOR", W/2, 1000, lt-d*0.6, ic_warn, size=30)
    post(c, t, 0.6)

def c4_5(c, lt, d, t):   # cierran la puerta; toallas en el cubo
    flat(c, t, 0.8)
    door(c, 860, FL, 260, 680, open_=0.6*(1-ease(P(lt, d, 0, 0.35))), light=0.0, night=0.8, t=t)
    if lt < d*0.3: smoke(c, t, 760, 700, 960, 1200, 6, 0.4, seed=5)
    box(c, 520, 1150, 120, 110, C['steel2'], 10, 3); c.rectangle(530, 1160, 100, 20); c.set_source_rgb(*C['water']); c.fill()
    julian(c, 440, FL+40, 520, "carry", t, face=1, expr="focus", lit=0.8)
    if lt > d*0.4:
        box(c, 470+30*math.sin(t*4), 1080, 120, 50, C['sky'], 8, 3)
        for i in range(3): circle(c, 500+i*30, 1150+((t*300+i*40) % 90), 6); fs(c, C['water'], 0)
    post(c, t, 0.55)

def c4_6(c, lt, d, t):   # REGLA 2: toallas mojadas en las rendijas
    wall_room(c, C['wall2'], 1150, 0.75)
    door(c, W/2, 1150, 520, 900, night=0.75, t=t)
    k = ease(P(lt, d, 0.05, 0.4))
    # humo que entra por debajo hasta que la toalla tapa
    smoke(c, t, 300, 1150, 780, 1250, 6, 0.4*(1-k), seed=4, rise=30)
    box(c, lerp(-500, 280, k), 1120, 520, 70, C['sky'], 20, 4)
    for i in range(5): c.set_source_rgba(0.3, 0.5, 0.7, 0.6); c.set_line_width(4); c.move_to(lerp(-460, 320, k)+i*95, 1130); c.line_to(lerp(-460, 320, k)+i*95, 1180); c.stroke()
    if k > 0.9: chip(c, "MOJADAS", 820, 1050, lt-d*0.42, ic_drop, size=30, anchor=(700, 1140))
    if lt > d*0.35: rule_card(c, 2, "TOALLAS MOJADAS", "EN LAS RENDIJAS", W/2, 520, lt-d*0.35, ic_drop)
    post(c, t, 0.55)

def c4_7(c, lt, d, t):   # 112: la llamada no sale
    flat(c, t, 0.85)
    marta(c, 330, FL+40, 540, "phone", t, face=1, expr="worried", look=(0.6, 0.4), lit=0.7)
    glow(c, 400, 860, 260, (0.75, 0.88, 1), 0.35)
    fail = lt > d*0.45
    c.save(); s = 0.6+0.1*ease(P(lt, d, 0, 0.3)); phone_alert(c, 760, 760, s, t, "LLAMANDO…" if not fail else "SIN RED", "112", "" if not fail else "FALLIDA", "APAGÓN"); c.restore()
    post(c, t, 0.6)

def facade(c, t, smoke_k=1.0, people=0.0, zoom=1.0, cx=W/2, cy=900):
    c.save(); c.translate(cx, cy); c.scale(zoom, zoom); c.translate(-W/2, -900)
    grad_bg(c, C['night1'], C['night2'])
    bx, bw, base, fh = 220, 640, 1560, 112
    c.rectangle(bx, base-10*fh, bw, 10*fh+600); c.set_source_rgb(*mix(C['wall2'], C['night1'], 0.8)); c.fill()
    for f in range(10):
        y = base-(f+1)*fh+26
        for j in range(4):
            x = bx+40+j*150
            fire = (f == 3 and j in (1, 2))
            c.rectangle(x, y, 100, 66); c.set_source_rgb(*((1, 0.5, 0.15) if fire else C['night1'])); c.fill()
            if fire:
                g = cairo.RadialGradient(x+50, y+33, 5, x+50, y+33, 200); g.add_color_stop_rgba(0, 1, 0.55, 0.2, 0.5+0.15*math.sin(t*9+j)); g.add_color_stop_rgba(1, 1, 0.5, 0.2, 0)
                c.set_source(g); c.arc(x+50, y+33, 200, 0, 2*math.pi); c.fill()
        # balcón del 5º
        if f == 4:
            c.rectangle(bx+30, y+66, 260, 10); c.set_source_rgb(*C['steel2']); c.fill()
    if smoke_k > 0: smoke(c, t, bx+180, base-5*fh-200, bx+500, base-4*fh, 14, 0.5*smoke_k, seed=11, rise=80, col=(0.12, 0.11, 0.12))
    c.rectangle(0, base, W, 600); c.set_source_rgb(*C['night1']); c.fill()
    if people > 0:
        r = random.Random(2)
        for i in range(7):
            x = 80+i*140+r.uniform(-20, 20)
            silhouette(c, x, base+120, 200*people, t+i)
            if i % 2 == 0:
                c.set_source_rgba(0.05, 0.05, 0.07, 1); c.set_line_width(14); c.move_to(x+10, base-40); c.line_to(x+60, base-120); c.stroke()
    c.restore()

def c4_8(c, lt, d, t):   # balcón: avisan desde allí
    facade(c, t, 0.8, 0.0, 1.0+0.6*ease(P(lt, d)), lerp(W/2, 420, ease(P(lt, d))), lerp(900, 1050, ease(P(lt, d))))
    k = ease(P(lt, d))
    marta(c, lerp(500, 380, k), lerp(1210, 1150, k), lerp(150, 330, k), "alarm", t, face=1, expr="shock", lit=0.85, shadow=False)
    julian(c, lerp(560, 640, k), lerp(1210, 1150, k), lerp(155, 340, k), "alarm", t+0.4, face=-1, expr="focus", lit=0.85, shadow=False)
    fy = lerp(1210, 1150, k); bh = lerp(60, 130, k)
    c.set_source_rgba(0.12, 0.13, 0.16, 1); c.rectangle(0, fy-8, W, 16); c.fill(); c.rectangle(0, fy-bh, W, 10); c.fill()
    for xx in range(0, W, int(lerp(16, 40, k))): c.rectangle(xx, fy-bh, 5, bh); c.fill()
    if lt > d*0.4: chip(c, "AVISA DESDE EL BALCÓN", W/2, 420, lt-d*0.4, ic_warn, size=32)
    post(c, t, 0.55)

def c4_9(c, lt, d, t):   # REGLA 3: velas a 30 cm; apágalas al salir
    wall_room(c, C['wall'], FL, 0.7)
    # cortina
    for i in range(6):
        x = 640+i*60; c.new_path(); c.move_to(x, 300); c.curve_to(x+30*math.sin(t+i), 700, x-20, 1000, x+10, FL)
        c.set_source_rgb(*mix(hexc('#B5838D'), C['night1'], 0.45)); c.set_line_width(56); c.stroke()
    box(c, 120, 1100, 420, 30, C['wood'], 6)
    out = lt > d*0.82
    if not out: glow(c, 320, 1000, 520, a=0.5)
    candle(c, 320, 1100, 0.9, t, lit=not out)
    if out:
        for i in range(3): smoke(c, t, 300, 900, 340, 980, 3, 0.4, seed=20+i, rise=40)
    # regla de 30 cm
    k = ease(P(lt, d, 0.05, 0.3))
    if k > 0:
        x1 = lerp(320, 640, k)
        c.set_source_rgb(*C['paper']); c.set_line_width(6); c.move_to(320, 1000); c.line_to(x1, 1000); c.stroke()
        for xx in (320, x1): c.move_to(xx, 975); c.line_to(xx, 1025); c.stroke()
        if k > 0.95: txt(c, "≥ 30 CM", 480, 960, 48, C['paper'], "Anton")
    if lt > d*0.25: rule_card(c, 3, "VELAS A 30 CM", "DE LO QUE ARDA", W/2, 560, lt-d*0.25)
    if lt > d*0.62: chip(c, "APÁGALAS AL SALIR", W/2, 1380, lt-d*0.62, ic_check, size=34)
    post(c, t, 0.55)

def c4_10(c, lt, d, t):  # la calle: vecinos señalan el 4º
    k = ease(P(lt, d))
    facade(c, t, 1.0, 1.0, 1.15-0.15*k, W/2, lerp(1100, 900, k))
    chip(c, "4º", 760, 640, lt-0.8, ic_warn, size=40, bg=C['red'], fg=C['paper'], anchor=(560, 1150))
    post(c, t, 0.55)

def c4_11(c, lt, d, t):  # Dani: su hermana estaba en el 4º
    grad_bg(c, hexc("#2A1A14"), hexc("#0D0B0C"))
    glow(c, 200, 1500, 900, (1, 0.5, 0.2), 0.35+0.1*math.sin(t*7))
    s = 1+0.15*ease(P(lt, d))
    c.save(); c.translate(W/2, 1400); c.scale(s, s); c.translate(-W/2, -1400)
    dani(c, 500, 1700, 1100, "stand", t, face=1, expr="shock" if lt > d*0.35 else "worried", look=(0.6, 0.5), lit=0.8, shadow=False)
    c.restore()
    if lt > d*0.45: chip(c, "SU HERMANA: EN EL 4º", W/2, 420, lt-d*0.45, ic_warn, size=36)
    post(c, t, 0.62)

def c4_12(c, lt, d, t):  # golpes en el cristal, entre el humo
    k = ease(P(lt, d))
    c.save(); z = 1+0.2*k; c.translate(W/2, 820); c.scale(z, z); c.translate(-W/2, -820)
    grad_bg(c, hexc("#120E10"), hexc("#060507"))
    rrect(c, 230, 420, 620, 760, 6); fs(c, hexc('#3A3436'), 0)
    rrect(c, 260, 450, 560, 700, 2); c.set_source_rgb(*(0.55, 0.25, 0.12)); c.fill()
    glow(c, 540, 820, 420, (1, 0.5, 0.2), 0.35+0.15*math.sin(t*8))
    smoke(c, t, 260, 450, 820, 1150, 16, 0.55, seed=13, rise=50, col=(0.1, 0.09, 0.1))
    c.set_source_rgb(*hexc('#3A3436')); c.set_line_width(16); c.move_to(540, 450); c.line_to(540, 1150); c.move_to(260, 780); c.line_to(820, 780); c.stroke()
    if lt > d*0.35:
        a = P(lt, d, 0.35, 0.55)
        for (hx, hy) in ((440, 700), (650, 620)):
            c.set_source_rgba(0.95, 0.85, 0.8, 0.45*a); rrect(c, hx-34, hy-30, 68, 70, 22); c.fill()
            for f in range(4): rrect(c, hx-32+f*17, hy-92, 13, 66, 6); c.fill()
            rrect(c, hx+30, hy-36, 14, 46, 6); c.fill()
        knock_marks(c, 540, 560, lt-d*0.35)
    c.restore()
    post(c, t, 0.75, 0.09)

SCENES = {"C4": [c4_0, c4_1, c4_2, c4_3, c4_4, c4_5, c4_6, c4_7, c4_8, c4_9, c4_10, c4_11, c4_12]}
BOOMS = {"C4": [0, 12]}
CALM = {"C4"}
