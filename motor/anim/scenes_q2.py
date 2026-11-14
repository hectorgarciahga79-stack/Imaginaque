"""Estilo «cine» al atardecer + infografía — ¿Y SI…? Q2: ¿y si los zombis corrieran (y nunca se cansaran)?
Zombis genéricos propios (piel verdosa, ropa rota); ningún personaje ni marca de terceros."""
from engine import *
from cine import *
from cine import POSE
from scenes_c4 import P
import cairo, math, random

POSE["zarms"] = (0.12, 0.06, 0, -0.06, 0, 1.5, 0.05, 1.35, 0.12)
ZOMB = [dict(top=hexc(t), top2=shade(hexc(t), 0.25), legs=hexc('#3A3D44'), legs2=hexc('#2B2E34'), shoe=hexc('#2B2A2F'),
             skin=hexc(s), hair=hexc('#2E2B28')) for t, s in (("#6E5A4E", "#9DB08F"), ("#4F5D6E", "#8FA08A"), ("#7A4E4E", "#A3B596"), ("#5E6650", "#94A88C"))]
HUNT = dict(top=hexc('#B07A4A'), top2=hexc('#8C5E36'), legs=hexc('#8C5E36'), legs2=hexc('#6F4A2A'), shoe=hexc('#6F4A2A'), skin=hexc('#8A5A3C'), hair=hexc('#1E1A18'))
DUSK1, DUSK2 = hexc("#F08A5D"), hexc("#FBD38D")

def zombie(c, x, y, h, t, ph=0.0, face=-1, run=1.0, lit=1.0, i=0):
    teo(c, x, y, h, "zarms", t, face=face, walk=(t*1.6*run+ph) if run else 0, expr="angry", look=(0.2, 0.1), who=ZOMB[i % len(ZOMB)], lit=lit)

def runner(c, x, y, h, t, speed=2.2, face=1, expr="shock", tired=0.0):
    teo(c, x, y, h, "stand", t, face=face, walk=t*speed, expr=expr, look=(-0.3, 0))
    if tired > 0:
        for k in range(3):
            ph = (t*1.5+k/3) % 1
            circle(c, x-face*(30+k*20)*h/520, y-h*0.95+ph*80, 9*h/520); c.set_source_rgba(*C['water'], tired*(1-ph)); c.fill()

def dusk_street(c, t, scroll=0.0, horizon=880):
    grad_bg(c, DUSK1, DUSK2, 0, horizon)
    sun(c, 820, horizon-120, 110, t)
    r = random.Random(4)
    for i in range(9):
        w = r.uniform(140, 220); hh = r.uniform(220, 520); x = (i*150 - scroll*0.3) % (W+300) - 150
        box(c, x, horizon-hh, w, hh, mix(hexc('#5B4A6E'), hexc('#3A3550'), (i % 3)/3), 4, 0)
        for wy in range(int(horizon-hh+30), horizon-40, 70):
            for wx in range(int(x+20), int(x+w-30), 50):
                if r.random() < 0.35: c.rectangle(wx, wy, 22, 30); c.set_source_rgba(1, 0.85, 0.5, 0.8); c.fill()
    c.rectangle(0, horizon, W, H-horizon); c.set_source_rgb(*hexc('#4A4552')); c.fill()
    c.rectangle(0, horizon, W, 30); c.set_source_rgb(*hexc('#8E8596')); c.fill()
    for i in range(8):
        x = (i*200 - scroll) % (W+200) - 100
        c.rectangle(x, horizon+260, 110, 16); c.set_source_rgb(*hexc('#E8DCC8')); c.fill()

def speedo(c, x, y, r, val, vmax, label, t, col=None):
    k = eout(clamp(t/0.8))
    v = val*k
    c.save(); c.translate(x, y)
    circle(c, 0, 0, r); fs(c, C['paper'], 6)
    c.set_line_width(22)
    for i, cc in enumerate((C['leaf'], C['gold'], C['red'])):
        c.new_path(); a0 = math.pi*0.75+i*math.pi*0.5; c.arc(0, 0, r-30, a0, a0+math.pi*0.5); c.set_source_rgb(*cc); c.stroke()
    ang = math.pi*0.75+1.5*math.pi*clamp(v/vmax)
    c.set_source_rgb(*OUT); c.set_line_width(12); c.move_to(0, 0); c.line_to(math.cos(ang)*(r-50), math.sin(ang)*(r-50)); c.stroke()
    circle(c, 0, 0, 18); c.set_source_rgb(*OUT); c.fill()
    txt(c, f"{int(round(v))}", 0, r*0.62, r*0.55, col or C['red'], "Anton")
    txt(c, label, 0, r*0.62+r*0.28, r*0.2, OUT)
    c.restore()

def kudu(c, x, y, s, t, fall=0.0):
    c.save(); c.translate(x, y); c.rotate(fall*1.3); c.scale(s, s)
    sw = math.sin(t*9)*(1-fall)
    col = hexc('#9C6B45'); col2 = hexc('#7E5434')
    for dx, k in ((-70, 1), (-40, -1), (55, 1), (85, -1)):
        c.save(); c.translate(dx, -120); c.rotate(0.35*sw*k); rrect(c, -8, 0, 16, 120, 8); fs(c, col2, 3); c.restore()
    c.new_path(); c.move_to(-110, -150); c.curve_to(-120, -220, 60, -230, 110, -170); c.curve_to(120, -120, -100, -100, -110, -150); c.close_path(); fs(c, col, 4)
    c.set_source_rgba(1, 1, 1, 0.8); c.set_line_width(4)
    for sx in (-40, -10, 20, 50): c.move_to(sx, -215); c.line_to(sx+6, -125); c.stroke()
    c.new_path(); c.move_to(95, -190); c.line_to(150, -270); c.line_to(185, -250); c.line_to(130, -170); c.close_path(); fs(c, col, 4)
    c.new_path(); c.move_to(150, -275); c.curve_to(200, -300, 205, -250, 190, -232); c.line_to(170, -246); c.close_path(); fs(c, col2, 3)
    c.set_source_rgb(*OUT); c.set_line_width(6)
    c.new_path(); c.move_to(160, -280); c.curve_to(130, -330, 190, -350, 160, -400); c.stroke()
    c.new_path(); c.move_to(172, -280); c.curve_to(150, -330, 215, -345, 190, -400); c.stroke()
    c.restore()

# ---------------- escenas ----------------
def q2_0(c, lt, d, t):   # gancho: los zombis corren detrás de ti
    k = ease(P(lt, d))
    c.save(); z = 1.0+0.18*k; c.translate(W/2, 1100); c.scale(z, z); c.translate(-W/2, -1100)
    dusk_street(c, t, scroll=t*420)
    speed_lines(c, t, n=18, dirx=-1, col=(1, 1, 1), a=0.35, y0=900, y1=1500, length=300, speed=1800)
    for i in range(4):
        zombie(c, 160+i*100+math.sin(t*2+i)*18, 1330+(i % 2)*40, 360+(i % 2)*40, t, ph=i*0.3, face=1, i=i)
    runner(c, 760+math.sin(t*1.5)*20, 1380, 460, t, speed=2.6, face=1, expr="shock")
    c.restore()
    if lt > 0.25: chip(c, "NO SE CANSAN NUNCA", W/2, 470, lt-0.25, ic_warn, size=40, bg=C['red'], fg=C['paper'])
    post(c, t, 0.4, 0.06)

def q2_1(c, lt, d, t):   # menos de lo que dura una canción
    grad_bg(c, hexc("#2B2140"), hexc("#14101F"))
    k = P(lt, d, 0.1, 0.9)
    box(c, 190, 560, 700, 520, hexc('#3A2F55'), 30, 5)
    for i in range(18):
        hh = 40+abs(math.sin(t*5+i*0.7))*140
        box(c, 240+i*34, 860-hh, 22, hh, C['gold'] if i % 3 else C['red2'], 6, 0)
    box(c, 240, 930, 600, 20, hexc('#5B4E7A'), 10, 0)
    box(c, 240, 930, 600*k*0.55, 20, C['gold'], 10, 0)
    txt(c, "0:00", 240, 1000, 30, C['paper'], align="left"); txt(c, "3:30", 840, 1000, 30, C['paper'], align="right")
    circle(c, 240+600*k*0.55, 940, 18); fs(c, C['paper'], 3)
    for i in range(3):
        ph = (t*0.6+i/3) % 1; x = 300+i*240; y = 520-ph*180
        c.save(); c.translate(x, y); c.set_source_rgba(*C['paper'], 1-ph); circle(c, 0, 0, 20); c.fill(); c.rectangle(16, -80, 6, 80); c.fill(); c.restore()
    if lt > d*0.35: chip(c, "TE PILLAN ANTES DEL FINAL", W/2, 1200, lt-d*0.35, ic_clock, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.45, 0.06)

def q2_2(c, lt, d, t):   # adulto normal: ~25 km/h
    dusk_street(c, t, scroll=t*700)
    speed_lines(c, t, n=24, dirx=-1, col=(1, 1, 1), a=0.5, y0=900, y1=1450, length=380, speed=2400)
    runner(c, 560, 1360, 520, t, speed=3.0, face=1, expr="focus")
    speedo(c, W/2, 520, 200, 25, 50, "KM/H", lt-0.2)
    if lt > d*0.5: chip(c, "ESPRINT · ADULTO NORMAL", W/2, 790, lt-d*0.5, size=32, bg=C['gold'])
    post(c, t, 0.35, 0.05)

def q2_3(c, lt, d, t):   # Bolt: más de 44
    grad_bg(c, hexc("#C9472F"), hexc("#E9845A"))
    for i in range(6):
        c.rectangle(0, 900+i*90, W, 6); c.set_source_rgba(1, 1, 1, 0.85); c.fill()
    c.rectangle(0, 1440, W, 300); c.set_source_rgb(*hexc('#3E7A4A')); c.fill()
    k = ease(P(lt, d, 0.05, 0.6))
    for i, (lab, val, col) in enumerate((("TÚ", 25, C['teal']), ("RÉCORD", 44, C['gold']))):
        y = 1010+i*200; w = 860*val/50*k
        box(c, 110, y, w, 110, col, 14, 5)
        txt(c, lab, 140, y+72, 44, C['paper'], "Anton", align="left")
        if k > 0.3: txt(c, f"{int(val*k)} km/h", 110+w-20, y+75, 48, OUT, "Anton", align="right")
    c.save(); c.translate(W/2, 600); c.scale(1.5, 1.5); c.translate(-W/2, -600)
    stat_card(c, "USAIN BOLT · BERLÍN 2009", "44", "km/h", W/2, 600, lt-0.3, icon=ic_bolt, sub="PUNTA MÁX."); c.restore()
    post(c, t, 0.35, 0.05)

def q2_4(c, lt, d, t):   # el turbo se agota en ~10 s
    grad_bg(c, hexc("#1F2B3A"), hexc("#0E1620"))
    k = P(lt, d, 0.05, 0.9)
    box(c, 300, 560, 440, 220, C['paper'], 26, 6); box(c, 740, 620, 40, 100, C['paper'], 8, 5)
    lvl = 1-k
    box(c, 320, 580, 400*lvl+2, 180, C['leaf'] if lvl > 0.5 else C['gold'] if lvl > 0.2 else C['red'], 16, 0)
    txt(c, f"{max(0, 10-int(k*10))} s", W/2, 720, 90, OUT, "Anton")
    runner(c, W/2+math.sin(t)*30, 1380, 480, t, speed=lerp(3.0, 1.4, k), face=1, expr="worried" if k > 0.5 else "focus", tired=k)
    if lt > d*0.25: chip(c, "TURBO: ~10 SEGUNDOS", W/2, 450, lt-d*0.25, ic_bolt, size=40, bg=C['gold'])
    post(c, t, 0.45, 0.06)

def q2_5(c, lt, d, t):   # bajas a trote: 10 km/h
    dusk_street(c, t, scroll=t*260)
    runner(c, 600, 1370, 500, t, speed=1.3, face=1, expr="worried", tired=0.9)
    speedo(c, W/2, 520, 190, 10, 50, "KM/H", lt-0.2, col=C['teal'])
    if lt > d*0.5: chip(c, "TROTE (EN FORMA)", W/2, 790, lt-d*0.5, size=32, bg=C['paper'])
    post(c, t, 0.35, 0.05)

def q2_6(c, lt, d, t):   # el zombi sigue a 15 por hora
    dusk_street(c, t, scroll=t*380, horizon=900)
    zombie(c, 470, 1390, 560, t, ph=0.2, face=1, run=1.2, i=1)
    speedo(c, W/2, 520, 190, 15, 50, "KM/H", lt-0.2)
    if lt > d*0.4: chip(c, "SIN JADEAR", 280, 800, lt-d*0.4, ic_warn, size=32, bg=C['red'], fg=C['paper'])
    if lt > d*0.62: chip(c, "SIN PARAR", 800, 860, lt-d*0.62, ic_clock, size=32, bg=C['gold'])
    post(c, t, 0.4, 0.06)

def q2_7(c, lt, d, t):   # 100 m de ventaja → te alcanza en < 2 min
    grad_bg(c, hexc("#EDE3D2"), hexc("#D8C8AE"))
    k = P(lt, d, 0.05, 0.85)
    T = 102*k            # segundos simulados (cálculo en notes)
    def you(tt): return 70*min(tt, 10)/10 + max(0, tt-10)*2.78 + 100
    def zom(tt): return 4.17*tt
    x0, x1, y = 90, 990, 900
    span = 520.0
    box(c, x0-20, y-70, x1-x0+40, 140, hexc('#C9B79A'), 70, 5)
    for i in range(0, 6):
        xx = x0+(x1-x0)*i/5; c.set_source_rgb(*OUT); c.set_line_width(3); c.move_to(xx, y+80); c.line_to(xx, y+100); c.stroke()
        txt(c, f"{int(span*i/5)} m", xx, y+140, 26, OUT)
    px = x0+(x1-x0)*you(T)/span; zx = x0+(x1-x0)*zom(T)/span
    teo(c, px, y+40, 250, "stand", t, face=1, walk=t*(2.6 if T < 10 else 1.3), expr="shock", shadow=False)
    zombie(c, zx, y+40, 250, t, face=1, run=1.0, i=2)
    gap = max(0.0, you(T)-zom(T))
    stat_card(c, "VENTAJA", f"{int(gap)}", "m", 300, 520, lt-0.1, icon=ic_warn)
    countdown(c, T, 760, 520, lt-0.3, label="HUYENDO", danger=gap < 40)
    if k >= 0.98: chip(c, "¡TE ALCANZA! < 2 MIN", W/2, 1200, lt-d*0.85, ic_warn, size=44, bg=C['red'], fg=C['paper'])
    post(c, t, 0.3, 0.05)

def q2_8(c, lt, d, t):   # esto ya ha pasado… al revés
    k = ease(P(lt, d, 0.2, 0.8))
    grad_bg(c, hexc("#E7A35A"), hexc("#F6D69A"))
    zombie(c, lerp(330, 720, k), 1250, 380, t, face=1, i=0, run=1.0)
    teo(c, lerp(720, 330, k), 1250, 380, "stand", t, face=1, walk=t*2.0, expr="shock" if k < 0.5 else "focus", who=None if k < 0.5 else HUNT)
    c.set_source_rgb(*OUT); c.set_line_width(14); c.new_path(); c.arc(W/2, 900, 380, -2.6, -0.5); c.stroke()
    c.new_path(); c.move_to(W/2+380*math.cos(-0.5)+30, 900+380*math.sin(-0.5)-40); c.line_to(W/2+380*math.cos(-0.5)-10, 900+380*math.sin(-0.5)+40); c.line_to(W/2+380*math.cos(-0.5)-60, 900+380*math.sin(-0.5)-20); c.close_path(); c.fill()
    if lt > d*0.5: chip(c, "PERO AL REVÉS", W/2, 450, lt-d*0.5, size=48, bg=C['red'], fg=C['paper'])
    post(c, t, 0.35, 0.05)

def q2_9(c, lt, d, t):   # caza por persistencia en el Kalahari
    grad_bg(c, hexc("#F7B267"), hexc("#FCE7B2"), 0, 1000)
    sun(c, 250, 420, 130, t)
    for i in range(5):
        hw = 1000-i*8+math.sin(t*3+i)*6
        c.set_source_rgba(1, 1, 1, 0.12); c.rectangle(0, hw, W, 4); c.fill()
    c.rectangle(0, 1000, W, H-1000); c.set_source_rgb(*hexc('#D9A55E')); c.fill()
    for i, x in enumerate((120, 980, 760)):
        c.set_source_rgb(*hexc('#7E8A4A')); circle(c, x, 1000, 50+i*10); c.fill()
    k = P(lt, d)
    kx = lerp(700, 780, k); fall = clamp((k-0.75)/0.2)
    kudu(c, kx, 1350, 1.05, t, fall)
    for i in range(2):
        teo(c, 240+i*170+math.sin(t+i)*10, 1400+i*20, 400, "stand", t, face=1, walk=t*1.4+i*0.4, expr="focus", who=HUNT)
    if lt > 0.3: chip(c, "40 °C", 820, 520, lt-0.3, ic_warn, size=46, bg=C['red'], fg=C['paper'])
    if lt > d*0.35: chip(c, "DE 2 A 6 HORAS", 760, 660, lt-d*0.35, ic_clock, size=36, bg=C['paper'])
    if lt > d*0.75: chip(c, "CAE AGOTADO", W/2, 800, lt-d*0.75, size=36, bg=C['gold'])
    post(c, t, 0.3, 0.05)

def q2_10(c, lt, d, t):  # no somos los más rápidos: somos los que no paran
    grad_bg(c, hexc("#2B2140"), hexc("#14101F"))
    k = P(lt, d)
    c.rectangle(0, 1250, W, H-1250); c.set_source_rgb(*hexc('#3A3550')); c.fill()
    runner(c, 330, 1320, 440, t, speed=1.5, face=1, expr="focus")
    zombie(c, 780, 1320, 440, t, face=-1, i=3)
    if lt > 0.2: chip(c, "NO SOMOS LOS MÁS RÁPIDOS", W/2, 480, lt-0.2, size=36, bg=C['paper'])
    if lt > d*0.45: chip(c, "SOMOS LOS QUE NO PARAN", W/2, 620, lt-d*0.45, ic_check, size=40, bg=C['gold'])
    if lt > d*0.75: chip(c, "COMO ÉL", 780, 780, lt-d*0.75, ic_warn, size=34, bg=C['red'], fg=C['paper'], anchor=(780, 860))
    post(c, t, 0.45, 0.06)

def q2_11(c, lt, d, t):  # ¿tú qué harías?
    dusk_street(c, t, scroll=0)
    teo(c, 540, 1400, 600, "think", t, face=1, expr="focus", look=(0.3, -0.3))
    for i in range(3):
        zombie(c, 1000+i*60, 1180, 220, t, face=-1, i=i, run=0.6, lit=0.6)
    for i, (lab, x, y, col) in enumerate((("¿CORRER?", 260, 560, C['gold']), ("¿ESCONDERTE?", 780, 480, C['teal']), ("¿AL TEJADO?", 560, 720, C['red']))):
        if lt > 0.2+i*0.45: chip(c, lab, x, y, lt-0.2-i*0.45, size=38, bg=col, fg=C['paper'] if i else OUT)
    if lt > d*0.6: chip(c, "TE LEO EN COMENTARIOS", W/2, 1260, lt-d*0.6, ic_check, size=34, bg=C['paper'])
    post(c, t, 0.35, 0.05)

def cover_q2(c):
    dusk_street(c, 1.0, scroll=200)
    for i in range(4): zombie(c, 120+i*120, 1350+(i % 2)*30, 420, 1.0+i*0.3, ph=i*0.3, face=1, i=i)
    runner(c, 800, 1420, 560, 1.2, speed=2.6, face=1, expr="shock")

SCENES = {"Q2": [q2_0, q2_1, q2_2, q2_3, q2_4, q2_5, q2_6, q2_7, q2_8, q2_9, q2_10, q2_11]}
BOOMS = {"Q2": [7, 9]}
CALM = set()
COVER = {"Q2": cover_q2}
