"""Estilo Leo 2D luminoso (alterna con el manga de Q5) — ¿Y si…? Q6: ¿y si la Tierra se parara 1 segundo?"""
from engine import *
from scenes import daysky, clouds
from cine import chip, stat_card, post, txt, box, fs, ic_check, ic_warn, ic_clock, ic_drop, ic_bolt, C, OUT
from scenes_q3 import spain_map, pin, P
from props import calendar
import cairo, math, random

GY = 1290

def room(c, k_shake=0.0, t=0.0, crack=0.0):
    grad_bg(c, hexc("#FBE3C4"), hexc("#F3CFA2"))
    # ventana con ciudad
    wx, wy, ww, wh = 640, 420, 380, 520
    rrect(c, wx, wy, ww, wh, 14); fill_stroke(c, PAL['sky'], 9)
    c.save(); rrect(c, wx, wy, ww, wh, 14); c.clip()
    grad_bg(c, PAL['sky'], PAL['sky2'], wy, wy+wh)
    c.save(); c.translate(wx-40, wy+40); c.scale(0.42, 0.42); city(c, 1150, t); c.restore()
    c.restore()
    c.set_source_rgb(*INK); c.set_line_width(9); c.move_to(wx+ww/2, wy); c.line_to(wx+ww/2, wy+wh); c.stroke()
    if crack > 0:
        r = random.Random(4); c.set_source_rgb(1, 1, 1); c.set_line_width(6)
        for i in range(9):
            a = r.uniform(0, 2*math.pi); L = r.uniform(80, 260)*crack
            c.move_to(wx+ww*0.6, wy+wh*0.45); c.line_to(wx+ww*0.6+math.cos(a)*L, wy+wh*0.45+math.sin(a)*L); c.stroke()
    # suelo y sofá
    c.rectangle(0, GY, W, H-GY); c.set_source_rgb(*hexc("#B8865A")); c.fill()
    c.set_source_rgb(*INK); c.set_line_width(LW); c.move_to(0, GY); c.line_to(W, GY); c.stroke()
    rrect(c, 60, 1010, 440, 200, 40); fill_stroke(c, PAL['b5'])
    rrect(c, 40, 1120, 480, 170, 40); fill_stroke(c, mix(PAL['b5'], (1, 1, 1), 0.15))
    # lámpara y cuadro
    rrect(c, 160, 520, 220, 160, 8); fill_stroke(c, PAL['b3'], 7)
    sun(c, 270, 600, 34, t)

def cow(c, x, y, s=1.0, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    for lx in (-80, -40, 50, 90):
        rrect(c, lx-14, -60, 28, 90, 12); fill_stroke(c, PAL['white'], 5)
    rrect(c, -130, -190, 260, 150, 60); fill_stroke(c, PAL['white'], 6)
    for (sx, sy, r) in ((-60, -140, 32), (40, -110, 26), (80, -160, 20)):
        circle(c, sx, sy, r); c.set_source_rgb(*INK); c.fill()
    rrect(c, 110, -250, 110, 100, 40); fill_stroke(c, PAL['white'], 6)
    rrect(c, 150, -200, 80, 52, 24); fill_stroke(c, hexc("#F6B7C3"), 5)
    circle(c, 150, -225, 9); c.set_source_rgb(*INK); c.fill()
    c.restore()

def lighthouse(c, x, base, s=1.0):
    c.save(); c.translate(x, base); c.scale(s, s)
    c.new_path(); c.move_to(-60, 0); c.line_to(60, 0); c.line_to(36, -420); c.line_to(-36, -420); c.close_path(); fill_stroke(c, PAL['white'])
    for i in range(3):
        y = -60-i*130; c.new_path(); c.move_to(-56+i*8, y); c.line_to(56-i*8, y); c.line_to(52-i*8, y-50); c.line_to(-52+i*8, y-50); c.close_path(); fill_stroke(c, PAL['red'], 5)
    rrect(c, -46, -500, 92, 80, 10); fill_stroke(c, PAL['yellow'])
    c.restore()

def flag(c, x, base, t):
    c.set_source_rgb(*INK); c.set_line_width(10); c.move_to(x, base); c.line_to(x, base-360); c.stroke()
    c.new_path(); c.move_to(x, base-360)
    for i in range(0, 181, 20): c.line_to(x+i, base-360+math.sin(i/40+t*4)*10)
    for i in range(180, -1, -20): c.line_to(x+i, base-250+math.sin(i/40+t*4)*10)
    c.close_path(); fill_stroke(c, PAL['red'], 6)

def bar_cmp(c, rows, x0, y0, wmax, k, vmax):
    for i, (lab, val, col) in enumerate(rows):
        y = y0+i*170
        txt(c, lab, x0, y-18, 34, INK, align="left")
        rrect(c, x0, y, wmax, 80, 20); fs(c, PAL['white'], 4)
        kk = ease(clamp(k*1.6-i*0.5)); kk = 1.0 if kk > 0.97 else kk
        if kk > 0.01:
            rrect(c, x0, y, wmax*val/vmax*kk, 80, 20); fs(c, col, 4)
        txt(c, f"{int(round(val*kk)):,} km/h".replace(",", "."), x0+wmax-36, y+58, 44, INK, "Anton", align="right")

# ---------------- escenas ----------------
def q6_0(c, lt, d, t):   # gancho: la Tierra se para 1 s y sales disparado por la ventana
    stop = 1.6
    z = 1.0+0.06*ease(P(lt, d))
    c.save(); c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2, -900)
    if lt > stop: shake(c, lt, 14*max(0, 1-(lt-stop)/1.2))
    room(c, 0, t, crack=ease(clamp((lt-stop-0.5)/0.4)))
    if lt < stop:
        leo(c, 420, GY, 0.95, "stand", "happy", t, walk=0)
    else:
        k = ease(clamp((lt-stop)/1.1))
        x = lerp(420, 980, k); y = lerp(GY, 860, k)
        speed_lines(c, t, 18, 1, (1, 1, 1), 0.85, 5, 500, 1250, 360, 3000)
        leo(c, x, y, lerp(0.95, 0.55, k), "fly", "shock", t, tilt=0.5*k)
    c.restore()
    chip(c, "LA TIERRA SE PARA", W/2, 340, lt-0.1, ic_warn, size=46, bg=PAL['red'], fg=C['paper'])
    if lt > 0.6: chip(c, "SOLO 1 SEGUNDO", W/2, 440, lt-0.6, ic_clock, size=40, bg=PAL['yellow'])
    if lt > stop: burst_text(c, "¡FRENAZO!", W/2, 1180, lt-stop, 130, PAL['yellow'])
    post(c, t, 0.2, 0.04)

def q6_1(c, lt, d, t):   # en el ecuador el suelo gira a 1.670 km/h
    grad_bg(c, PAL['night'], PAL['night2']); stars(c, 120, 2, t)
    globe(c, W/2, 700, 330, t*0.18)
    # ecuador
    c.set_source_rgb(*PAL['red']); c.set_line_width(10); c.set_dash([26, 16], -t*120)
    c.save(); c.translate(W/2, 700); c.scale(1, 0.16); c.arc(0, 0, 330, 0, math.pi); c.restore(); c.stroke(); c.set_dash([])
    # flecha de giro
    k = P(lt, d, 0.1, 0.5)
    c.set_source_rgb(*PAL['yellow']); c.set_line_width(16)
    c.save(); c.translate(W/2, 700); c.scale(1, 0.3); c.arc(0, 0, 420, 0.3*math.pi, (0.3+0.5*k)*math.pi); c.restore(); c.stroke()
    if lt > 0.8: chip(c, "ECUADOR", W/2+250, 760, lt-0.8, size=34, bg=PAL['red'], fg=C['paper'])
    if lt > d*0.4: stat_card(c, "EL SUELO GIRA A", f"{int(1670*eout(P(lt, d, 0.4, 0.75))):,}".replace(",", "."), "km/h", W/2, 1200, lt-d*0.4, icon=ic_bolt)
    chip(c, "AHORA MISMO VAS A TODA PASTILLA", W/2, 300, lt-0.1, size=32, bg=C['paper'])
    post(c, t, 0.2, 0.04)

def q6_2(c, lt, d, t):   # en Madrid ~1.270 km/h: más rápido que el sonido
    spain_map(c, t)
    pin(c, 500, 820, "MADRID", lt-0.05)
    k = P(lt, d, 0.2, 0.7)
    bar_cmp(c, [("MADRID GIRA A", 1270, PAL['red']), ("EL SONIDO VA A", 1235, PAL['b3'])], 120, 1010, 840, k, 1300)
    if lt > d*0.62: chip(c, "¡MÁS RÁPIDO QUE EL SONIDO!", W/2, 380, lt-d*0.62, ic_bolt, size=40, bg=PAL['yellow'])
    post(c, t, 0.25, 0.04)

def q6_3(c, lt, d, t):   # si el planeta frena, tú no: coches, vacas y mar siguen
    daysky(c); clouds(c, t, 60, n=4, y0=300, y1=560)
    k = P(lt, d)
    c.save(); shake(c, t, 6)
    ground(c, GY-160)
    road(c, GY-140, 140, t, 0)
    speed_lines(c, t, 22, 1, (1, 1, 1), 0.8, 9, 320, 1250, 420, 3400)
    xs = (t*900) % (W+800)
    car(c, xs-300, GY-90, 1.0, PAL['red'], 0.15+0.1*math.sin(t*7), t)
    car(c, xs-900, GY-80, 0.9, PAL['b3'], -0.2, t)
    cow(c, ((t*700+500) % (W+700))-300, 900+60*math.sin(t*3), 1.0, 0.4*math.sin(t*2.5))
    leo(c, ((t*800+200) % (W+600))-200, 760, 0.6, "fly", "shock", t, tilt=0.4)
    c.restore()
    wave(c, t, GY+40, 260*ease(P(lt, d, 0.5, 1.0)), PAL['sea'], x_off=-t*800, crest=False)
    chip(c, "TÚ NO FRENAS", W/2, 330, lt-0.1, ic_warn, size=44, bg=PAL['red'], fg=C['paper'])
    for i, s in enumerate(("COCHES", "VACAS", "EL MAR")):
        if lt > 1.2+i*0.7: chip(c, s, 230+i*310, 450, lt-1.2-i*0.7, size=34, bg=PAL['yellow'])
    post(c, t, 0.2, 0.04)

def q6_4(c, lt, d, t):   # el aire tampoco: viento 3x el peor tornado medido
    daysky(c, 0.35); clouds(c, t*6, 300, 0.4, n=6, y0=280, y1=700)
    k = P(lt, d, 0.1, 0.9)
    city(c, GY-260, t, wind=1.0, roof=ease(k))
    ground(c, GY-260, PAL['ground'], PAL['ground_d'])
    speed_lines(c, t, 34, 1, (1, 1, 1), 0.7, 13, 300, 1000, 500, 4200)
    c.rectangle(70, 1040, W-140, 330); c.set_source_rgba(1, 1, 1, 0.82); c.fill()
    bar_cmp(c, [("TORNADO RÉCORD (EE. UU., 1999)", 486, PAL['b3']), ("VIENTO EN EL ECUADOR", 1670, PAL['red'])], 120, 1110, 840, P(lt, d, 0.3, 0.8), 1700)
    if lt > d*0.75: chip(c, "×3", 900, 980, lt-d*0.75, size=60, bg=PAL['yellow'])
    chip(c, "EL AIRE SIGUE A TODA VELOCIDAD", W/2, 320, lt-0.1, size=32, bg=C['paper'])
    post(c, t, 0.25, 0.05)

def q6_5(c, lt, d, t):   # los océanos se tragan las costas
    daysky(c, 0.25); clouds(c, t, 80, 0.3, n=3, y0=300, y1=520)
    k = ease(P(lt, d))
    ground(c, GY-60, PAL['sand'], PAL['sand_d'])
    lighthouse(c, 820, GY-60, 1.0)
    for i, x in enumerate((560, 680)):
        building(c, x, GY-60, 110, 220+i*60, PAL['b2'] if i else PAL['b1'], t, seed=i+3)
    c.save(); c.translate(-W*0.55*(1-k), 0)
    wave(c, t, GY-80, lerp(500, 900, k), PAL['sea_d'], x_off=t*200)
    wave(c, t+0.5, GY+10, 300, PAL['sea'], x_off=t*300, crest=False)
    c.restore()
    shake(c, t, 4)
    chip(c, "EL MAR SIGUE AVANZANDO", W/2, 330, lt-0.1, ic_drop, size=40, bg=PAL['red'], fg=C['paper'])
    post(c, t, 0.2, 0.05)

def q6_6(c, lt, d, t):   # el único sitio seguro: el Polo Norte
    grad_bg(c, hexc("#9FD8FF"), hexc("#EAF7FF"))
    sun(c, 860, 420, 60, t)
    globe(c, 220, 470, 120, t*0.1)
    c.set_source_rgb(*PAL['red']); circle(c, 220, 352, 16); c.fill()
    c.rectangle(0, GY-170, W, H-GY+170); c.set_source_rgb(*PAL['snow']); c.fill()
    c.set_source_rgb(*PAL['ice']); c.set_line_width(6)
    for i in range(5): c.move_to(80+i*220, GY-120+i % 2*40); c.line_to(200+i*220, GY-90); c.stroke()
    c.set_source_rgb(*INK); c.set_line_width(LW); c.move_to(0, GY-170); c.line_to(W, GY-170); c.stroke()
    flag(c, 800, GY-150, t)
    # Leo da una vuelta lentísima sobre sí mismo
    fac = 1 if math.sin(lt*0.9) > 0 else -1
    leo(c, 430, GY-150, 0.95, "shrug" if lt < d*0.55 else "stand", "smirk" if lt > d*0.55 else "happy", t, facing=fac)
    chip(c, "POLO NORTE", W/2, 320, lt-0.1, ic_check, size=46, bg=PAL['yellow'])
    if lt > d*0.35: chip(c, "1 VUELTA AL DÍA", 770, 620, lt-d*0.35, ic_clock, size=36, bg=C['paper'])
    if lt > d*0.7: chip(c, "CASI NI LO NOTAS", 770, 715, lt-d*0.7, size=34, bg=PAL['b3'])
    post(c, t, 0.2, 0.04)

def q6_7(c, lt, d, t):   # si no volviera a girar: un día = un año (6 meses sol / 6 meses noche)
    grad_bg(c, PAL['night'], PAL['night2']); stars(c, 140, 7, t)
    sun(c, 120, 640, 90, t)
    globe(c, 620, 640, 280, 0.2, terminator=0.0)
    k = P(lt, d, 0.15, 0.6)
    calendar(c, 300, 1100, 0.62*max(pop(lt-0.5), 0.01), "365", "DÍAS = 1 DÍA")
    if lt > d*0.55:
        chip(c, "6 MESES DE SOL", 720, 1010, lt-d*0.55, size=38, bg=PAL['yellow'])
    if lt > d*0.75:
        chip(c, "6 MESES DE NOCHE", 720, 1130, lt-d*0.75, size=38, bg=PAL['night2'], fg=C['paper'])
    chip(c, "SI NO VOLVIERA A GIRAR…", W/2, 320, lt-0.1, size=36, bg=C['paper'])
    post(c, t, 0.25, 0.04)

def pop(t, dur=0.35): return back(t/dur) if t > 0 else 0

def q6_8(c, lt, d, t):   # ya está frenando: +~2 ms por siglo
    grad_bg(c, PAL['night'], PAL['night2']); stars(c, 120, 3, t)
    globe(c, 360, 700, 240, t*0.05)
    # abultamiento de marea hacia la Luna
    c.save(); c.translate(360, 700); c.scale(1.12, 0.96); circle(c, 0, 0, 252); c.restore()
    c.set_source_rgba(*PAL['sea'], 0.35); c.fill()
    mx = 900+10*math.sin(t); moon(c, mx, 560, 80)
    c.set_source_rgba(1, 1, 1, 0.5); c.set_line_width(5); c.set_dash([18, 14], -t*60)
    c.move_to(620, 700); c.line_to(mx-90, 580); c.stroke(); c.set_dash([])
    if lt > 0.4: stat_card(c, "CADA SIGLO, EL DÍA DURA", "+0,002", "s", W/2, 1150, lt-0.4, icon=ic_clock, sub="≈1,8 ms")
    chip(c, "LA TIERRA YA ESTÁ FRENANDO", W/2, 320, lt-0.1, ic_warn, size=36, bg=PAL['red'], fg=C['paper'])
    if lt > d*0.6: chip(c, "CULPA DE LA LUNA (MAREAS)", 780, 820, lt-d*0.6, size=30, bg=C['paper'])
    post(c, t, 0.25, 0.04)

def q6_9(c, lt, d, t):   # ¿a qué te agarrarías?
    daysky(c); clouds(c, t, 40, n=3, y0=300, y1=600)
    ground(c, GY)
    lamp(c, 170, GY, 600); tree(c, 900, GY, 1.0)
    leo(c, W/2, GY, 1.0, "think", "smirk", t)
    for i, (lab, x, y, bg) in enumerate((("FAROLA", 230, 480, PAL['yellow']), ("ÁRBOL", 850, 480, PAL['land']), ("SOFÁ", W/2, 360, PAL['b5']))):
        if lt > 0.2+i*0.4: chip(c, lab, x, y, lt-0.2-i*0.4, size=46, bg=bg)
    if lt > d*0.55: chip(c, "TE LEO EN COMENTARIOS", W/2, 620, lt-d*0.55, ic_check, size=32, bg=C['paper'])
    post(c, t, 0.2, 0.04)

def cover_q6(c):
    room(c, 0, 1.0, crack=1.0)
    speed_lines(c, 1.0, 20, 1, (1, 1, 1), 0.85, 5, 900, 1500, 360, 3000)
    leo(c, 760, 1250, 0.8, "fly", "shock", 1.0, tilt=0.45)

SCENES = {"Q6": [q6_0, q6_1, q6_2, q6_3, q6_4, q6_5, q6_6, q6_7, q6_8, q6_9]}
BOOMS = {"Q6": [0, 4]}
CALM = set()
COVER = {"Q6": cover_q6}
