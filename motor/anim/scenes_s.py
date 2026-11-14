"""Test batch scenes: S1 stickman (growth), S2 mapa (all humanity in one place), S3 pizarra (slow sound)."""
from engine import *
from styles import *
from props import check

G = 1250  # ground line (captions live below ~1350)

def prog(lt, d, a=0.0, b=1.0):
    return clamp((lt/d-a)/(b-a)) if d > 0 else 1.0

# ============================================================ S1 — STICKMAN
def world(c, ppm, t, hero_m, pose="stand", face="neutral", hx=0.0, buckle=0.0, rot=0.0, cars_alert=0.0, people=True, phase=None):
    """everything measured in metres; hero feet at (W/2+hx, G); ppm = pixels per metre"""
    paper_bg(c)
    # sky band + ground
    c.set_source_rgb(*hexc("#EAF1F7")); c.rectangle(0, 0, W, G); c.fill()
    for i, (cx, alt, s) in enumerate(((-900, 1500, 1.0), (700, 2200, 1.2), (-200, 3200, 0.9))):
        y = G-alt*ppm
        if -200 < y < H: cloud_ink(c, W/2+cx*ppm*0.3+(t*8 % 60), y, clamp(0.4+ppm*0.4, 0.4, 1.6)*s)
    c.set_source_rgb(*hexc("#CFE3C4")); c.rectangle(0, G, W, H-G); c.fill()
    c.set_source_rgb(*INKB); c.set_line_width(6); c.move_to(0, G); c.line_to(W, G); c.stroke()
    X = lambda m: W/2+hx+m*ppm
    # road with cars (ants)
    if ppm < 15:
        c.set_source_rgb(0.55, 0.55, 0.6); c.rectangle(0, G+8, W, clamp(7*ppm, 4, 26)); c.fill()
        for i in range(14):
            m = -300+i*45+((t*14*(1 if i % 2 else -1)) % 45)
            x = X(m)
            if -60 < x < W+60:
                tiny_car(c, x, G+2, max(0.12, ppm/12), PAL['red'] if i % 3 == 0 else ACC2)
                if cars_alert > 0 and i % 2 == 0: ink_text(c, "!", x, G-max(20, 3*ppm)-20*cars_alert, 40, ACC)
    # house 7 m, building 28 m (9 floors)
    hw = 9*ppm
    if X(10)-hw < W and ppm > 1.2:
        ink_rect(c, X(10)-hw/2, G-6*ppm, hw, 6*ppm, max(2, 0.12*ppm), hexc("#F4D6A0"))
        c.new_path(); c.move_to(X(10)-hw/2-ppm*0.6, G-6*ppm); c.line_to(X(10), G-9*ppm); c.line_to(X(10)+hw/2+ppm*0.6, G-6*ppm); c.close_path()
        c.set_source_rgb(*ACC); c.fill_preserve(); c.set_source_rgb(*INKB); c.set_line_width(max(2, 0.12*ppm)); c.stroke()
    if ppm < 60:
        ink_building(c, X(-14), G, 16*ppm, 28*ppm, 9)
    if people and ppm > 25:
        stick(c, X(-1.3), G, 1.75*ppm, "stand", t+1.3, face="shock" if hero_m > 2.5 else "neutral", col=hexc("#555B66"))
    lw = clamp(hero_m*ppm*0.04, 4, 34)
    stick(c, X(0), G, hero_m*ppm, pose, t, face=face, buckle=buckle, rot=rot, lw=lw, phase=phase, col=INKB)

def ruler(c, x, top, bot, label, t, col=ACC):
    c.set_source_rgb(*col); c.set_line_width(6)
    c.move_to(x, bot); c.line_to(x, top); c.stroke()
    for y in (top, bot): c.move_to(x-18, y); c.line_to(x+18, y); c.stroke()
    ink_label(c, label, x, (top+bot)/2, t, 70, col)

def grow_m(lt, d, m0, m1, a=0.15, b=0.75):
    return m0*(m1/m0)**ease(prog(lt, d, a, b))

def clock10(c, x, y, r, t, col=ACC):
    circle(c, x, y, r); c.set_source_rgb(1, 1, 1); c.fill_preserve(); c.set_source_rgb(*INKB); c.set_line_width(7); c.stroke()
    a = (t % 10)/10*2*math.pi
    c.new_path(); c.move_to(x, y); c.arc(x, y, r-10, -math.pi/2, -math.pi/2+a); c.close_path(); c.set_source_rgba(*col, 0.35); c.fill()
    c.set_source_rgb(*INKB); c.move_to(x, y); c.line_to(x+math.sin(a)*(r-14), y-math.cos(a)*(r-14)); c.stroke()

def s1_0(c, lt, d, t):
    world(c, 260, t, 1.75, "think" if lt < d*0.5 else "shock", "neutral" if lt < d*0.5 else "shock")
    clock10(c, 830, 470, 95, lt*10/d)
    ink_label(c, "×2 CADA 10 s", W/2, 420, lt-0.3, 80)

def s1_1(c, lt, d, t):
    m = grow_m(lt, d, 1.75, 3.5); ppm = 260*(1.75/m)**0.55
    world(c, ppm, t, m, "cheer", "happy")
    ruler(c, W/2+180+m*ppm*0.1, G-m*ppm, G, f"{m:.1f} m".replace(".", ","), lt-d*0.55)
    clock10(c, 900, 420, 70, lt*10/d)

def s1_2(c, lt, d, t):
    m = grow_m(lt, d, 3.5, 7.0, 0.05, 0.5); ppm = 150*(3.5/m)**0.6
    world(c, ppm, t, m, "shock" if lt > d*0.5 else "stand", "shock" if lt > d*0.5 else "neutral", hx=-140)
    # bedroom box breaking
    k = prog(lt, d, 0.45, 0.7)
    x0, w_, h_ = W/2-140-3*ppm, 6*ppm, 2.6*ppm
    c.save(); c.translate(x0+w_/2, G-h_); c.rotate(-0.8*k); c.translate(-(x0+w_/2), -(G-h_))
    c.set_source_rgb(*INKB); c.set_line_width(8); c.move_to(x0, G-h_-120*k); c.line_to(x0+w_, G-h_-120*k); c.stroke(); c.restore()
    c.set_source_rgb(*INKB); c.set_line_width(8)
    for xx in (x0, x0+w_): c.move_to(xx, G); c.line_to(xx-60*k*(1 if xx == x0 else -1), G-h_); c.stroke()
    if k > 0: scribble_lines(c, x0, G-h_-60, w_, int(10*k), 3, INKB, 5)
    if lt > d*0.55: burst_text(c, "¡CRAC!", 760, 470, lt-d*0.55, 90, ACC, 0.1)
    ruler(c, W/2-140+m*ppm*0.35+60, G-m*ppm, G, "7 m", lt-d*0.3)

def s1_3(c, lt, d, t):
    m = grow_m(lt, d, 7, 28, 0.05, 0.6); ppm = 75*(7/m)**0.75
    world(c, ppm, t, m, "stand" if lt < d*0.6 else "point", "neutral", hx=200)
    ruler(c, W/2+200+90, G-m*ppm, G, f"{m:.0f} m", lt-d*0.3)
    if lt > d*0.55: ink_label(c, "= 9 PLANTAS", W/2-200, 440, lt-d*0.55, 72, ACC2)

def s1_4(c, lt, d, t):
    m = grow_m(lt, d, 28, 112, 0.0, 0.45); ppm = 9.5*(28/m)**0.9
    world(c, ppm, t, m, "lookdown", "smirk" if lt < d*0.6 else "worried", cars_alert=prog(lt, d, 0.6, 0.7))
    ruler(c, W/2+170, G-m*ppm, G, f"{m:.0f} m", lt-d*0.2)
    if lt > d*0.35:
        k = eout(prog(lt, d, 0.35, 0.5)); r = 210
        c.save(); circle(c, 250, 1030, r*k); c.set_source_rgb(1, 1, 1); c.fill_preserve(); c.set_source_rgb(*INKB); c.set_line_width(8); c.stroke()
        circle(c, 250, 1030, r*k); c.clip()
        for i in range(5): tiny_car(c, 120+i*60+(lt*40 % 60), 1080+(i % 2)*40, 0.9, ACC if i % 2 else ACC2)
        c.restore()
        c.set_source_rgb(*INKB); c.set_line_width(6); c.move_to(250+r*k*0.7, 1030+r*k*0.7); c.line_to(250+r*k*1.05, 1030+r*k*1.05); c.stroke()
        if lt > d*0.4: ink_text(c, "HORMIGAS", 250, 780, 64)

def cube(c, x, y, s, col):
    # isometric cube, front-bottom corner at (x, y)
    dx, dy = s*0.866, s*0.5
    faces = [((0, 0), (dx, -dy), (dx, -dy-s), (0, -s)), ((0, 0), (-dx, -dy), (-dx, -dy-s), (0, -s)), ((0, -s), (dx, -dy-s), (0, -2*dy-s), (-dx, -dy-s))]
    for f, sh in zip(faces, (0.85, 0.7, 1.0)):
        c.new_path()
        for i, (u, v) in enumerate(f): (c.move_to if i == 0 else c.line_to)(x+u, y+v)
        c.close_path(); c.set_source_rgb(*(v_*sh for v_ in col)); c.fill_preserve(); c.set_source_rgb(*INKB); c.set_line_width(5); c.stroke()

def s1_5(c, lt, d, t):
    paper_bg(c)
    ink_text(c, "ALTURA ×2", 300, 470, 80, ACC2)
    cube(c, 300, 1000, 150, hexc("#9EC5FE"))
    k = prog(lt, d, 0.4, 0.95); n = int(8*k+0.999) if k > 0 else 0
    ink_text(c, "PESO ×8", 790, 470, 80, ACC)
    s = 110; order = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
    order.sort(key=lambda p: (p[2], -(p[0]+p[1])))
    for i, (a, b, z) in enumerate(order[:n]):
        x = 790+(a-b)*s*0.866; y = 1060+(a+b)*s*0.5-z*s
        drop = (1-eout(clamp((k*8-i)*1.2)))*200
        cube(c, x, y-s*0.5-drop, s, hexc("#FFADAD"))
    if n >= 8: ink_label(c, "×8", 790, 640, lt-d*0.95+0.3, 90)

def s1_6(c, lt, d, t):
    paper_bg(c)
    k = eout(prog(lt, d, 0.05, 0.5)); kb = eout(prog(lt, d, 0.3, 0.75))
    for x, val, lab, col, kk in ((330, 8, "PESO", ACC, k), (750, 4, "HUESOS", ACC2, kb)):
        h = 90*val*kk
        ink_rect(c, x-110, G-h, 220, h, 7, col)
        ink_text(c, lab, x, G+90, 70)
        if kk > 0.2: ink_text(c, f"×{val}", x, G-h-30, 100, col)
    # bone doodle cracking
    if lt > d*0.7:
        burst_text(c, "¡NO DA!", W/2, 360, lt-d*0.7, 90, ACC, -0.08)

def s1_7(c, lt, d, t):
    m = 7000; ppm = 880/m*(1+0.06*prog(lt, d))
    paper_bg(c); world(c, ppm, t, m, "stand", "worried", people=False)
    # plane passing
    px = -200+(lt/d)*1500; py = G-4500*ppm
    c.save(); c.translate(px, py)
    rrect(c, -70, -12, 140, 24, 12); c.set_source_rgb(1, 1, 1); c.fill_preserve(); c.set_source_rgb(*INKB); c.set_line_width(5); c.stroke()
    c.move_to(-10, 0); c.line_to(-40, 45); c.line_to(10, 0); c.stroke(); c.restore()
    ruler(c, W/2+190, G-m*ppm, G, "7.000 m", lt-0.4)
    if lt > d*0.3: ink_label(c, "2 MINUTOS", 300, 600, lt-d*0.3, 64, ACC2)

def s1_8(c, lt, d, t):
    m = 7000; ppm = 880/m
    b = ease(prog(lt, d, 0.2, 0.9))
    c.save()
    if b > 0.3: shake(c, t, 6*b)
    world(c, ppm, t, m, "stand", "scared", buckle=b, people=False)
    c.restore()
    if lt > d*0.35:
        for i, (x, y) in enumerate(((470, G-260), (610, G-240))):
            if lt > d*(0.35+i*0.15): burst_text(c, "CRAC", x+(-120 if i == 0 else 140), y-60, lt-d*(0.35+i*0.15), 60, ACC, 0.15*(1 if i else -1))

def s1_9(c, lt, d, t):
    m = 7000; ppm = 880/m
    fall = ease(prog(lt, d, 0.0, 0.3)); imp = lt-d*0.3
    c.save()
    if imp > 0: shake(c, t, 28*max(0, 1-imp/2.2))
    world(c, ppm, t, m, "scared", "scared", rot=fall*1.45, people=False, hx=-100*fall)
    if imp > 0:
        # shockwave + ground cracks
        r = imp*900
        c.set_source_rgba(*ACC, max(0, 0.7-imp*0.3)); c.set_line_width(14)
        c.save(); c.translate(W/2, G); c.scale(1, 0.18); c.new_path(); c.arc(0, 0, r, 0, 2*math.pi); c.stroke(); c.restore()
        rr = random.Random(2); c.set_source_rgb(*INKB); c.set_line_width(6)
        for i in range(9):
            x = rr.uniform(60, W-60); y = G+10; c.move_to(x, y)
            for j in range(4): x += rr.uniform(-40, 40); y += 25*min(1, imp*2); c.line_to(x, y)
        c.stroke()
        burst_text(c, "TERREMOTO", W/2, 520, imp-d*0.25, 110, ACC, -0.06)
    c.restore()

def s1_10(c, lt, d, t):
    world(c, 300, t, 1.75, "sit", "worried", hx=40)
    # chair
    c.set_source_rgb(*INKB); c.set_line_width(8)
    x = W/2+40; c.move_to(x-120, G-230); c.line_to(x+60, G-230); c.move_to(x-110, G-230); c.line_to(x-110, G); c.move_to(x+50, G-230); c.line_to(x+50, G)
    c.move_to(x-120, G-230); c.line_to(x-130, G-520); c.stroke()
    if lt > d*0.45: ink_label(c, "NO TE MUEVAS", W/2, 470, lt-d*0.45, 84, ACC)
    if lt > d*0.75: ink_text(c, "¿Tú qué harías?", W/2, 640, 64, ACC2, font="Montserrat")

# ============================================================ S2 — MAPA
def s2_0(c, lt, d, t):
    map_bg(c, t)
    k = eout(prog(lt, d, 0.0, 0.8))
    world_dots(c, W/2, 820, 430, k, 0, t)
    counter(c, 8_000_000_000*k, W/2, 470, 110, GOLD)
    hud_text(c, "PERSONAS", W/2, 560, 54, (1, 1, 1), font="Montserrat")

def s2_1(c, lt, d, t):
    map_bg(c, t)
    k = prog(lt, d, 0.1, 0.9); n = 1+int(48*ease(k))
    s = 120; x0, y0 = W/2-3.5*s, 500
    for i in range(49):
        gx, gy = i % 7, i//7
        c.rectangle(x0+gx*s, y0+gy*s, s, s); c.set_source_rgba(*CYAN, 0.5); c.set_line_width(3); c.stroke()
    order = sorted(range(49), key=lambda i: abs(i % 7-3)+abs(i//7-3))
    for j, i in enumerate(order[:n]):
        gx, gy = i % 7, i//7
        person_icon(c, x0+gx*s+s/2, y0+gy*s+s*0.88, 30, GOLD if j else HOT)
    hud_text(c, "1 m²", W/2, 430, 100, GOLD)

def s2_2(c, lt, d, t):
    map_bg(c, t)
    k = eout(prog(lt, d, 0.05, 0.75))
    side = 120+480*k
    c.rectangle(W/2-side/2, 820-side/2, side, side); c.set_source_rgba(*GOLD, 0.25); c.fill_preserve(); c.set_source_rgb(*GOLD); c.set_line_width(6); c.stroke()
    counter(c, 8200*k, W/2, 470, 140, GOLD, " km²")
    hud_text(c, "8.000 M × 1 m²", W/2, 1200, 60, CYAN, font="Montserrat")

def s2_3(c, lt, d, t):
    map_bg(c, t)
    if lt < d*0.45:
        hud_text(c, "?", W/2, 900, 420, GOLD, a=0.5+0.5*abs(math.sin(lt*4)))
    else:
        k = eout(prog(lt, d, 0.45, 0.75))
        c.save(); c.translate(W/2, 900); c.scale(max(k, 1e-3), max(k, 1e-3)); c.translate(-W/2, -900)
        madrid_shape(c, W/2, 900, 330, 0, t); c.restore()
        hud_text(c, "COMUNIDAD DE MADRID", W/2, 400, 74, GOLD)
        hud_text(c, "8.028 km²", W/2, 480, 60, (1, 1, 1), font="Montserrat")
        hud_text(c, "(silueta aproximada)", W/2, 1290, 34, CYAN, font="Montserrat", a=0.7)

def s2_4(c, lt, d, t):
    map_bg(c, t)
    madrid_shape(c, W/2, 900, 330, eout(prog(lt, d, 0.05, 0.85)), t)
    for name, (u, v) in (("SOMOSIERRA", MADRID[0]), ("ARANJUEZ", (0.35, 0.92))):
        x, y = W/2+u*330, 900+v*330
        circle(c, x, y, 12); c.set_source_rgb(*HOT); c.fill()
        hud_text(c, name, x, y+(-30 if v < 0 else 70), 50, (1, 1, 1), font="Montserrat")
    counter(c, 8_000_000_000*eout(prog(lt, d, 0.05, 0.85)), W/2, 400, 80, GOLD)

def s2_5(c, lt, d, t):
    map_bg(c, t)
    e = eout(prog(lt, d, 0.0, 0.5))
    world_dots(c, W/2, 820, 430, 1.0, e, t)
    circle(c, W/2+70, 760, 16+6*math.sin(t*6)); c.set_source_rgb(*HOT); c.fill()
    hud_text(c, "TODO LO DEMÁS: VACÍO", W/2, 450, 72, (1, 1, 1))
    if lt > d*0.45:
        for i, s in enumerate(("CIUDADES FANTASMA", "OCÉANOS SIN BARCOS")):
            if lt > d*(0.45+i*0.2): label_tag(c, s, W/2, 1140+i*100, 44, NAVY2, CYAN)

def s2_6(c, lt, d, t):
    map_bg(c, t)
    madrid_shape(c, W/2, 840, 300, 1.0, t)
    check(c, W/2, 840, 2.2, True) if lt < d*0.7 else None
    hud_text(c, "¿ESPACIO?", W/2, 420, 96, (1, 1, 1))
    if lt > d*0.5: hud_text(c, "NO ES EL PROBLEMA", W/2, 520, 64, GOLD)

def s2_7(c, lt, d, t):
    k = prog(lt, d, 0.0, 0.3)
    map_bg(c, t); c.set_source_rgba(*HOT, 0.25*k); c.paint()
    hud_text(c, "CALOR", W/2, 420, 130, HOT)
    kb = eout(prog(lt, d, 0.25, 0.8)); base = 1180
    bar(c, 210, base, 260, 620, kb, HOT, "8.000 M CUERPOS", "820 GW")
    bar(c, 610, base, 260, 620, kb*142.6/820, CYAN, "TODA ESPAÑA", "143 GW")
    if lt > d*0.82: label_tag(c, "≈ ×6", 340, 520, 64, HOT, (1, 1, 1))

def s2_8(c, lt, d, t):
    map_bg(c, t)
    k = eout(prog(lt, d, 0.05, 0.8))
    counter(c, 20_000_000_000*k, W/2, 470, 100, CYAN)
    hud_text(c, "LITROS DE AGUA / DÍA", W/2, 560, 54, (1, 1, 1), font="Montserrat")
    r = random.Random(5)
    for i in range(int(60*k)):
        x = r.uniform(120, W-120); y = (r.uniform(600, 1300)+lt*400*r.uniform(0.6, 1.2)) % 700+620
        c.new_path(); c.move_to(x, y-30); c.curve_to(x+22, y, x+18, y+22, x, y+22); c.curve_to(x-18, y+22, x-22, y, x, y-30)
        c.set_source_rgba(*CYAN, 0.85); c.fill()

def s2_9(c, lt, d, t):
    map_bg(c, t)
    p = 0.5+0.5*math.sin(t*7)
    c.set_source_rgba(*HOT, 0.15+0.15*p); c.paint()
    madrid_shape(c, W/2, 860, 320, 1.0, t, HOT)
    # warning triangle
    k = back(prog(lt, d, 0.2, 0.5)*1)
    if k > 0:
        c.save(); c.translate(W/2, 470); c.scale(max(k, 1e-3), max(k, 1e-3))
        c.new_path(); c.move_to(0, -130); c.line_to(150, 120); c.line_to(-150, 120); c.close_path()
        c.set_source_rgb(*GOLD); c.fill_preserve(); c.set_source_rgb(*NAVY); c.set_line_width(12); c.stroke()
        hud_text(c, "!", 0, 95, 170, NAVY); c.restore()

def s2_10(c, lt, d, t):
    map_bg(c, t)
    world_dots(c, W/2, 820, 430, eout(prog(lt, d, 0.2, 0.7)), 0, t)
    hud_text(c, "CABEMOS…", W/2, 440, 110, GOLD)
    if lt > d*0.5: hud_text(c, "PERO MEJOR SEPARADITOS", W/2, 1240, 58, (1, 1, 1))

# ============================================================ S3 — PIZARRA
def board_title(c, s, lt, k_speed=1.6, y=430, size=86, col=MARK):
    hand_text(c, s, W/2, y, lt*k_speed, size, col)

def s3_0(c, lt, d, t):
    board_bg(c)
    x = 160+eout(prog(lt, d))*520
    board_person(c, x, 1150, 380, prog(lt, d, 0, 0.15)*1.2, t, phase=lt*1.4, face="happy")
    sound_arcs(c, x+90, 950, 40, 3, MBLUE, 7, 0.9)
    board_title(c, "SONIDO = 5 km/h", lt, 1.2)
    marker_hand(c, (W/2+330*min(1, lt*1.2), 440), t) if lt < 1.0 else None
    hand_text(c, "(paso de peatón)", W/2, 520, (lt-0.8)*1.5, 48, MBLUE, font="Montserrat")

def s3_1(c, lt, d, t):
    board_bg(c)
    hand_text(c, "AHORA:", W/2, 560, lt*2, 70)
    hand_text(c, "+1.200 km/h", W/2, 720, lt*1.5-0.3, 140, MRED)
    k = prog(lt, d, 0.55, 0.75)
    if k > 0:
        tip = draw_partial(c, [(220, 760), (860, 640)], k, MARK, 14)
        if k < 1: marker_hand(c, tip, t)
        hand_text(c, "→ 5 km/h", W/2, 960, (lt-d*0.75)*3, 120, MBLUE)

def two_people(c, lt, t, f1="happy", f2="neutral", p2="stand"):
    board_person(c, 220, 1150, 340, 1, t, face=f1, pose="point")
    board_person(c, 860, 1150, 340, 1, t, face=f2, pose=p2)
    c.set_source_rgb(*MARK); c.set_line_width(5)
    c.move_to(260, 1200); c.line_to(820, 1200); c.stroke()
    for x in (260, 820): c.move_to(x, 1180); c.line_to(x, 1220); c.stroke()
    hand_text(c, "10 m", W/2, 1180, 1, 48, MARK, font="Montserrat")

def s3_2(c, lt, d, t):
    board_bg(c); two_people(c, lt, t)
    speech(c, 330, 690, 1.0, "¡HOLA!", MBLUE, lt)

def s3_3(c, lt, d, t):
    board_bg(c); two_people(c, lt, t, "happy", "neutral" if lt < d*0.7 else "happy", "think" if lt < d*0.85 else "cheer")
    k = prog(lt, d, 0.0, 0.92); x = 330+k*420
    hand_text(c, "HOLA", x, 840, 1, 64, MBLUE)
    sound_arcs(c, x+90, 820, 30, 3, MBLUE, 6, 0.7)
    sec = 7*k
    hand_text(c, f"{sec:0.1f} s".replace(".", ","), W/2, 540, 1, 150, MRED)
    for i in range(3):
        hand_text(c, "…", 860, 820-i*0, 1 if lt*2 % 3 > i else 0, 70, MARK)

def s3_4(c, lt, d, t):
    board_bg(c)
    k = prog(lt, d, 0.0, 1.0)
    wx = 300+k*220; px = 160+ease(k)*760
    hand_text(c, "HOLA", wx, 820, 1, 72, MBLUE); sound_arcs(c, wx+100, 800, 30, 3, MBLUE, 6, 0.7)
    board_person(c, px, 1150, 360, 1, t, phase=lt*2.6, face="happy")
    c.set_source_rgb(*MARK); c.set_line_width(5)
    for i in range(4): c.move_to(px-140-i*10, 900+i*50); c.line_to(px-260-i*30, 900+i*50)
    c.stroke()
    board_title(c, "MÁS RÁPIDO QUE TU VOZ", lt, 1.4, 470, 72, MRED)

def s3_5(c, lt, d, t):
    board_bg(c)
    p = lt/d
    if p < 0.4:
        k = prog(lt, d, 0.0, 0.12)
        bolt = [(640, 300), (560, 520), (640, 520), (540, 760)]
        draw_partial(c, bolt, k*1.0, GOLD, 18); draw_partial(c, bolt, k, MARK, 5)
        if k >= 1 and int(t*10) % 3 == 0: c.set_source_rgba(1, 1, 0.7, 0.3); c.paint()
        hand_text(c, "5 km → 1 HORA", W/2, 950, (lt-d*0.12)*2, 100, MRED)
    else:
        # house + clock + dinner
        q = prog(lt, d, 0.4, 1.0)
        house = [(300, 1100), (300, 850), (450, 720), (600, 850), (600, 1100), (300, 1100)]
        tip = draw_partial(c, house, q*3, MARK, 8)
        if q*3 < 1: marker_hand(c, tip, t)
        circle(c, 820, 700, 120); c.set_source_rgb(*MARK); c.set_line_width(8); c.stroke()
        a = q*2*math.pi*1.0
        c.move_to(820, 700); c.line_to(820+math.sin(a)*95, 700-math.cos(a)*95); c.stroke()
        c.move_to(820, 700); c.line_to(820+math.sin(a/12)*60, 700-math.cos(a/12)*60); c.stroke()
        hand_text(c, "cenas...", 450, 1250-30, (q-0.4)*3, 72, MBLUE, font="Montserrat")
        hand_text(c, "zzz", 820, 960, (q-0.6)*3, 60, MARK)

def s3_6(c, lt, d, t):
    board_bg(c)
    c.save()
    if lt < 1.2: shake(c, t, 22*(1-lt/1.2))
    burst_text(c, "¡BUM!", W/2, 760, lt, 190, MRED, -0.1)
    c.restore()

def s3_7(c, lt, d, t):
    board_bg(c)
    # stage + band
    c.set_source_rgb(*MARK); c.set_line_width(8); c.rectangle(240, 560, 600, 40); c.stroke()
    for i, x in enumerate((360, 540, 720)): board_person(c, x, 560, 190, 1, t+i, pose="cheer" if (int(t*2)+i) % 2 else "stand", face="happy")
    # audience rows
    k = prog(lt, d, 0, 1)
    wave_y = 620+k*700
    for r in range(6):
        y = 700+r*110
        heard = y < wave_y
        for j in range(8):
            x = 150+j*112+(r % 2)*40
            bob = -12*abs(math.sin(t*6+j)) if heard else 0
            circle(c, x, y+bob, 26); c.set_source_rgb(*(MBLUE if heard else MARK)); c.set_line_width(5); c.stroke()
    c.set_source_rgba(*MBLUE, 0.6); c.set_line_width(6); c.move_to(80, wave_y); c.line_to(W-80, wave_y); c.stroke()
    hand_text(c, "FONDO: 1 MIN TARDE", W/2, 420, (lt-d*0.4)*2, 70, MRED)

def s3_8(c, lt, d, t):
    board_bg(c)
    c.set_source_rgb(*MARK); c.set_line_width(6); c.move_to(0, 1050); c.line_to(W, 1050); c.move_to(0, 1210); c.line_to(W, 1210); c.stroke()
    k = prog(lt, d, 0, 0.6); cx = -150+k*1400
    c.save(); c.translate(cx, 1130)
    rrect(c, -110, -60, 220, 70, 20); c.set_source_rgb(*BOARD); c.fill_preserve(); c.set_source_rgb(*MARK); c.set_line_width(7); c.stroke()
    for wx in (-60, 60): circle(c, wx, 12, 24); c.stroke()
    c.restore()
    sx = -150+prog(lt, d, 0.35, 1.0)*900
    hand_text(c, "BRRRUM", sx, 960, 1 if lt > d*0.35 else 0, 80, MBLUE)
    board_person(c, 540, 1040, 260, 1, t, face="shock" if lt > d*0.4 else "neutral")
    board_title(c, "OYES EL COCHE… DESPUÉS", lt, 1.3, 470, 66, MRED)

def s3_9(c, lt, d, t):
    board_bg(c)
    sky = [(60, 1150), (60, 900), (180, 900), (180, 760), (300, 760), (300, 980), (420, 980), (420, 640), (560, 640), (560, 1000),
           (680, 1000), (680, 820), (820, 820), (820, 940), (1020, 940), (1020, 1150)]
    tip = draw_partial(c, sky, prog(lt, d, 0, 0.35), MARK, 8)
    if lt < d*0.35: marker_hand(c, tip, t)
    for i, (x, y) in enumerate(((240, 740), (490, 620), (750, 800), (930, 920))):
        ph = (t*0.7+i*0.37) % 1
        sound_arcs(c, x, y, 20+ph*120, 3, MBLUE, 5, (1-ph)*0.9 if lt > d*0.3 else 0, 1.2)
    hand_text(c, "ECO", W/2, 470, (lt-d*0.35)*2, 160, MRED)
    hand_text(c, "que no se acaba nunca", W/2, 560, (lt-d*0.5)*2, 50, MARK, font="Montserrat")

def s3_10(c, lt, d, t):
    board_bg(c)
    board_person(c, 230, 1150, 360, 1, t, pose="point", face="worried")
    speech(c, 360, 690, 1.0, "¡EH!", MRED, lt)
    run = prog(lt, d, 0.35, 1.0)
    board_person(c, 760+run*420, 1150, 360, 1, t, phase=lt*2.6 if run > 0 else None, face="shock" if run > 0 else "neutral")
    left = max(0, 7-lt*7/d)
    hand_text(c, f"{left:0.0f} s", W/2, 600, 1, 130, MBLUE)
    if lt > d*0.7: hand_text(c, "¡CORRE!", W/2, 430, (lt-d*0.7)*3, 90, MRED)

SCENES = {
    "S1": [s1_0, s1_1, s1_2, s1_3, s1_4, s1_5, s1_6, s1_7, s1_8, s1_9, s1_10],
    "S2": [s2_0, s2_1, s2_2, s2_3, s2_4, s2_5, s2_6, s2_7, s2_8, s2_9, s2_10],
    "S3": [s3_0, s3_1, s3_2, s3_3, s3_4, s3_5, s3_6, s3_7, s3_8, s3_9, s3_10],
}
BOOMS = {"S1": [9], "S2": [7], "S3": [6]}
