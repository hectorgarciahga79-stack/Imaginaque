from engine import *

FLOOR = 1560

def space(c, t, a=1):
    grad_bg(c, PAL['night'], PAL['night2']); stars(c, 140, 7, t, a)

def daysky(c, dark=0.0):
    grad_bg(c, mix(PAL['sky'], (0.15, 0.17, 0.25), dark), mix(PAL['sky2'], (0.3, 0.3, 0.38), dark))

def cloud(c, x, y, s=1, col=(1, 1, 1), a=1):
    c.save(); c.translate(x, y); c.scale(s, s); c.new_path()
    for dx, dy, r in ((-90, 10, 60), (-30, -30, 80), (50, -10, 70), (110, 15, 50)):
        c.new_sub_path(); c.arc(dx, dy, r, 0, 2*math.pi)
    c.set_source_rgba(*col, a); c.fill(); c.restore()

def clouds(c, t, speed=40, dark=0.0, n=5, y0=250, y1=900):
    r = random.Random(11)
    for i in range(n):
        x = (r.random()*W*1.6 + t*speed*(0.6+r.random())) % (W+600) - 300
        cloud(c, x, y0+r.random()*(y1-y0), 0.8+r.random()*0.8, mix((1, 1, 1), (0.45, 0.47, 0.55), dark), 0.95)

def street(c, t, dark=0.0, wind=0.0, roof=0.0, cspeed=40):
    daysky(c, dark); clouds(c, t, cspeed, dark)
    city(c, FLOOR-200, t, wind, roof, lit=dark, dark=dark*0.6)
    road(c, FLOOR-200, 200, t, 0); ground(c, FLOOR, mix(PAL['walk'], (0, 0, 0), dark*0.4), mix(PAL['sole'], (0, 0, 0), dark*0.4))

def arrow(c, x, y, length, t, col=None, thick=60):
    col = col or PAL['yellow']; k = eout(t*3)
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), 1)
    c.new_path(); c.move_to(-length/2, -thick/2); c.line_to(length/2-70, -thick/2); c.line_to(length/2-70, -thick)
    c.line_to(length/2, 0); c.line_to(length/2-70, thick); c.line_to(length/2-70, thick/2); c.line_to(-length/2, thick/2); c.close_path()
    fill_stroke(c, col, 8); c.restore()

def droplet(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-math.pi/2)
    c.new_path(); c.move_to(0, -90); c.curve_to(50, -20, 60, 30, 0, 60); c.curve_to(-60, 30, -50, -20, 0, -90); c.close_path()
    fill_stroke(c, PAL['sea']); c.restore()

def wind_swirl(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s); c.set_line_width(14)
    for k in range(3):
        c.new_path(); c.move_to(-200, -60+k*60)
        c.curve_to(-60, -100+k*60, 60, -20+k*60, 160, -60+k*60)
        c.arc(160, -30+k*60, 30, -math.pi/2, math.pi*0.9)
        c.set_source_rgb(*INK); c.set_line_width(22); c.stroke_preserve(); c.set_source_rgb(1, 1, 1); c.set_line_width(12); c.stroke()
    c.restore()

def bench(c, x, y, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot)
    rrect(c, -110, -70, 220, 30, 8); fill_stroke(c, (0.6, 0.4, 0.25))
    rrect(c, -110, -130, 220, 30, 8); fill_stroke(c, (0.6, 0.4, 0.25))
    rrect(c, -90, -40, 20, 40, 4); fill_stroke(c, (0.3, 0.3, 0.35)); rrect(c, 70, -40, 20, 40, 4); fill_stroke(c, (0.3, 0.3, 0.35))
    c.restore()

def bin_(c, x, y, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.new_path(); c.move_to(-50, -130); c.line_to(50, -130); c.line_to(40, 0); c.line_to(-40, 0); c.close_path(); fill_stroke(c, (0.3, 0.6, 0.4))
    rrect(c, -58, -145, 116, 22, 8); fill_stroke(c, (0.25, 0.5, 0.33)); c.restore()

def big_wave(c, xf, hgt, t):
    """wall of water advancing left->right, front at xf, curling crest."""
    top = FLOOR-hgt
    c.new_path(); c.move_to(-60, H+60); c.line_to(-60, top+40)
    for x in range(-60, int(xf)-140, 40):
        c.line_to(x, top+30*math.sin(x/90+t*4))
    c.curve_to(xf-60, top-120, xf+180, top-60, xf+170, top+120)   # crest curl
    c.curve_to(xf+150, top+40, xf+60, top+40, xf+40, top+150)
    c.curve_to(xf+80, top+500, xf+260, FLOOR-60, xf+320, FLOOR+40)
    c.line_to(xf+320, H+60); c.close_path(); fill_stroke(c, PAL['sea'], 9)
    c.set_source_rgba(1, 1, 1, .9); c.set_line_width(16)
    for k in range(4):
        c.new_path(); c.move_to(xf-120-k*160, top+60+k*25); c.curve_to(xf-60-k*160, top+20+k*25, xf-k*160, top+40+k*25, xf+20-k*160, top+90+k*25); c.stroke()
    r = random.Random(5)
    for i in range(14):
        circle(c, xf+r.uniform(60, 330), FLOOR-r.uniform(0, hgt*0.9), r.uniform(10, 26)); fill_stroke(c, PAL['white'], 5)

# ---------------- A1 ----------------
def a1_0(c, lt, d, t):  # Tierra deja de girar, de golpe
    stop = d*0.62
    space(c, t)
    rot = (min(lt, stop))*0.32
    amp = 22*(1-eout((lt-stop)/0.6)) if lt > stop else 0
    c.save(); shake(c, lt, amp)
    globe(c, W/2, 860, 360, rot)
    if lt < stop:
        c.set_source_rgba(1, 1, 1, .6); c.set_line_width(10)
        for k in range(3):
            c.new_path(); c.arc(W/2, 860, 420+k*30, math.pi*0.15+k*0.1+lt*2 % 0.5, math.pi*0.45+k*0.1+lt*2 % 0.5); c.stroke()
    c.restore()
    label_tag(c, "MAÑANA · 11:15", W/2, 380, 54, PAL['yellow'])
    if lt > stop: burst_text(c, "¡STOP!", 760, 520, (lt-stop), 120, PAL['red'], 0.15)

def a1_1(c, lt, d, t):  # frenazo / golpe
    hit = d*0.55
    street(c, t)
    if lt < hit:
        leo(c, 300+lt*120, FLOOR+10, 0.95, "stand", "neutral", t, walk=lt*1.6)
    else:
        k = lt-hit
        leo(c, 300+hit*120+k*k*1400+k*500, FLOOR-80-k*420, 0.95, "fly", "shock", t, tilt=0.6+k*2)
        speed_lines(c, t, 18, 1, (1, 1, 1), 0.9, y0=500, y1=1400)
        burst_text(c, "¡PUM!", 650, 650, k, 140)

def a1_2(c, lt, d, t):  # 1.300 km/h
    space(c, t)
    globe(c, W/2, 1250, 300, t*0.05, spain_pin=True)
    gauge(c, W/2, 560, 240, 1270, 1700, "km/h", lt/(d*0.7))
    leo(c, W/2+150, 1250-285, 0.28, "stand", "neutral", t, tilt=0.35)

def a1_3(c, lt, d, t):  # notebook velocidad
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    notebook(c, W/2, 820, 900, 900, [("Ecuador: ~1.670 km/h", INK), ("España: ~1.270 km/h", PAL['red']), ("Y no lo notas.", INK)],
             lt/d*1.15, "VELOCIDAD DEL SUELO")
    leo(c, 860, FLOOR+40, 0.75, "think", "smirk", t)

def a1_4(c, lt, d, t):  # planeta se para, tú no
    mid = d*0.45
    street(c, t, cspeed=0)
    if lt < mid:
        leo(c, W/2, FLOOR+10, 0.95, "stand", "neutral", t)
        label_tag(c, "EL PLANETA: 0 km/h", W/2, 420, 52, PAL['white'])
    else:
        k = lt-mid
        leo(c, W/2+k*k*700+k*250, FLOOR-60-k*160, 0.95, "fly", "shock", t, tilt=0.4)
        speed_lines(c, t, 22, 1, (1, 1, 1), 0.9, y0=600, y1=1450)
        label_tag(c, "TÚ: 1.270 km/h", W/2, 420, 58, PAL['red'], PAL['white'])

def a1_5(c, lt, d, t):  # ni tú, ni coches, ni agua, ni aire
    daysky(c); clouds(c, t, 900)
    speed_lines(c, t, 30, 1, (1, 1, 1), 0.8)
    items = [("TÚ", 0.0), ("LOS COCHES", 0.25), ("EL AGUA", 0.5), ("EL AIRE", 0.72)]
    for i, (name, start) in enumerate(items):
        k = lt/d-start
        if k < 0: continue
        x = -250+k*(W+500)/0.55; y = 500+i*270
        c.save()
        if i == 0: leo(c, x, y+260, 0.55, "fly", "shock", t, tilt=0.5)
        elif i == 1: car(c, x, y+110, 0.9, PAL['red'], rot=0.15+k)
        elif i == 2: droplet(c, x, y, 1.3)
        else: wind_swirl(c, x, y, 1.1, t)
        c.restore()
        label_tag(c, name, W/2, 380 if i == len([1 for _, s in items if lt/d >= s])-1 else -200, 64, PAL['yellow'])
    ground(c, 1700)

def a1_6(c, lt, d, t):  # todo disparado hacia el este
    street(c, t, dark=0.15, wind=1.0, cspeed=700)
    tree(c, 120, FLOOR, 0.9, bend=0.6+0.1*math.sin(t*12), leaves=0.9)
    lamp(c, 640, FLOOR, 560)
    leo(c, 650, FLOOR-480, 0.7, "cling", "scared", t, tilt=-1.45)
    k = lt/d
    bench(c, 200+k*1300, FLOOR, rot=k*3); bin_(c, -100+k*1500, FLOOR, rot=k*5)
    speed_lines(c, t, 24, 1, (1, 1, 1), 0.7, y0=300, y1=1500)
    arrow(c, W/2, 400, 700, lt, PAL['yellow'])
    text(c, "ESTE", W/2-40, 425, 70, INK, outline=0)

def a1_7(c, lt, d, t):  # el aire sería lo peor
    dark = clamp(lt/d)*0.7
    daysky(c, dark); clouds(c, t, 1200, dark, n=8, y0=150, y1=1100)
    speed_lines(c, t, 26, 1, (1, 1, 1), 0.5)
    leo(c, W/2, 2250, 2.1, "stand", "worried", t, look=(0.2, -1))

def a1_8(c, lt, d, t):  # viento > huracán, arrasando ciudades
    street(c, t, dark=0.55, wind=2.0, roof=clamp(lt/d*1.3), cspeed=1500)
    speed_lines(c, t, 40, 1, (1, 1, 1), 0.85, y0=200, y1=1500, speed=4200)
    k = eout(lt/0.5)
    c.save(); c.translate(W/2, 420); c.scale(max(k, 1e-3), max(k, 1e-3))
    rrect(c, -430, -170, 860, 340, 36); fill_stroke(c, PAL['white'], 8)
    text(c, "HURACÁN CATEGORÍA 5", 0, -80, 52, INK, font="Montserrat", outline=0, bold=True)
    text(c, "+252 km/h", 0, -10, 70, PAL['land_d'], outline=0)
    text(c, "ESTE VIENTO: +1.000 km/h", 0, 120, 72, PAL['red'], outline=0)
    c.restore()

def a1_9(c, lt, d, t):  # océanos tierra adentro
    daysky(c, 0.5); clouds(c, t, 300, 0.5)
    city(c, FLOOR, t, 0.5, 0.0, lit=0.3, scale=0.8, dark=0.4)
    ground(c, FLOOR)
    big_wave(c, -420+eout(lt/d)*1150, 820, t)

def a1_10(c, lt, d, t):  # lo más raro no es ese día
    grad_bg(c, hexc("#FF9A5A"), hexc("#FFD59A"))
    sun(c, 780, 600, 120, 0)
    for i, x in enumerate((120, 330, 900)):
        building(c, x, FLOOR, 200, 260+i*60, mix(PAL['b5'], (0.2, 0.1, 0.1), .3), roof_off=1, seed=i)
    ground(c, FLOOR, hexc("#B88A6A"), hexc("#9C7052"))
    leo(c, 520, FLOOR+20, 0.9, "sit", "worried", t, look=(0.6, -0.6))
    label_tag(c, "EL SOL NO SE MUEVE", W/2, 380, 52, PAL['white'])

def a1_11(c, lt, d, t):  # parte dos
    space(c, t)
    k = eout(lt/d)
    globe(c, W/2, 900, 340+60*k, 0.31, terminator=0.0)
    text(c, "DÍA", W/2-190, 900, 70, PAL['yellow'])
    text(c, "NOCHE", W/2+190, 900, 70, PAL['line'])
    if lt > d*0.6: burst_text(c, "PARTE 2 →", W/2, 400, lt-d*0.6, 110, PAL['yellow'], -0.06)

SCENES = {"A1": [a1_0, a1_1, a1_2, a1_3, a1_4, a1_5, a1_6, a1_7, a1_8, a1_9, a1_10, a1_11]}
BOOMS = {"A1": [1, 4, 8]}
CALM = set()

import importlib as _il
import glob as _g, os as _o
for _m in sorted(_o.path.basename(p)[:-3] for p in _g.glob(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "scenes_*.py"))):
    try:
        _mod = _il.reload(_il.import_module(_m))
        SCENES.update(_mod.SCENES); BOOMS.update(_mod.BOOMS); CALM.update(getattr(_mod, 'CALM', set()))
    except ModuleNotFoundError:
        pass
