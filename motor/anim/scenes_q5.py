"""Estilo «manga» luminoso (líneas cinéticas, tramas, auras) — ¿Y si…? Q5: ¿y si despertaras en un anime con poderes?
Héroe, ataque («Tormenta Carmesí») y zombis ORIGINALES; ningún personaje, ataque ni marca de anime existente."""
from engine import *
from cine import *
from cine import POSE
from scenes_c4 import P
from scenes_q1 import mini
from scenes_q2 import zombie, speedo
import cairo, math, random

POSE["crouch"] = (0.25, 1.2, -1.6, 1.0, -1.5, -0.6, 0.4, -0.5, 0.4)
POSE["jump"] = (-0.05, 0.25, -0.5, -0.3, -0.2, 2.6, 0.2, 2.5, 0.2)
POSE["attack"] = (0.08, 0.4, -0.3, -0.35, 0, 1.55, 0.05, 1.45, 0.05)
POSE["fall"] = (0.0, 0.5, -0.8, -0.2, -0.4, 2.2, 0.8, -2.2, -0.8)
HERO = dict(top=hexc('#C8372D'), top2=hexc('#9E2A22'), legs=hexc('#22243A'), legs2=hexc('#16182A'), shoe=hexc('#F4EEE3'),
            skin=hexc('#F0D2B4'), hair=hexc('#1C1A2E'))
CRIM, CRIM2 = hexc('#E8394A'), hexc('#8E1626')
SKYA, SKYB = hexc('#7FD0F5'), hexc('#FFF1C9')
GOLD = hexc('#FFC845')

def hero(c, x, y, h, pose, t, face=1, expr="focus", aura=0.0, look=(0, 0)):
    if aura > 0: halo(c, x, y-h*0.5, h*0.62, t, aura)
    teo(c, x, y, h, pose, t, face=face, expr=expr, look=look, who=HERO, shadow=False)
    # mechones de punta (pelo «anime» propio)
    u = h/520; hx, hy = x+face*4*u, y-h*0.955
    c.save(); c.translate(hx, hy); c.scale(face, 1)
    c.new_path()
    for i, (ax, ay) in enumerate(((-58, 8), (-70, -40), (-30, -30), (-28, -92), (8, -40), (30, -100), (40, -34), (78, -62), (60, 6))):
        c.line_to(ax*u, ay*u)
    c.close_path(); fs(c, HERO['hair'], 3)
    c.restore()

def halo(c, x, y, r, t, a=1.0, col=None):
    col = col or GOLD
    for i in range(3):
        rr = r*(1+0.08*math.sin(t*9+i*2))*(1+i*0.18)
        g = cairo.RadialGradient(x, y, rr*0.2, x, y, rr)
        g.add_color_stop_rgba(0, *col, 0.0); g.add_color_stop_rgba(0.7, *col, 0.25*a); g.add_color_stop_rgba(1, *col, 0)
        c.set_source(g); circle(c, x, y, rr); c.fill()
    r_ = random.Random(int(t*12))
    c.set_line_width(6)
    for i in range(12):
        ang = r_.uniform(0, 2*math.pi); L = r_.uniform(0.6, 1.0)*r
        c.set_source_rgba(*col, 0.7*a); c.move_to(x+math.cos(ang)*r*0.5, y+math.sin(ang)*r*0.8)
        c.line_to(x+math.cos(ang)*(r*0.5+L*0.4), y+math.sin(ang)*(r*0.8+L*0.5)-L*0.3); c.stroke()

def radial(c, cx, cy, t, col=(1, 1, 1), a=0.8, n=60, seed=2, inner=260):
    """líneas de concentración de manga"""
    r = random.Random(seed+int(t*10))
    for i in range(n):
        ang = i/n*2*math.pi + r.uniform(-0.03, 0.03); w = r.uniform(0.008, 0.025)
        ri = inner*r.uniform(0.9, 1.5)
        c.new_path(); c.move_to(cx+math.cos(ang-w)*ri, cy+math.sin(ang-w)*ri)
        c.line_to(cx+math.cos(ang)*1600, cy+math.sin(ang)*1600); c.line_to(cx+math.cos(ang+w)*ri, cy+math.sin(ang+w)*ri)
        c.close_path(); c.set_source_rgba(*col, a); c.fill()

def halftone(c, col, a=0.18, step=34, x0=0, y0=0, x1=W, y1=H, grow=0.0):
    c.set_source_rgba(*col, a)
    for j, y in enumerate(range(int(y0), int(y1), step)):
        for x in range(int(x0)+(j % 2)*step//2, int(x1), step):
            rr = 5+grow*((y-y0)/max(1, y1-y0))*10
            circle(c, x, y, rr); c.fill()

def vlines(c, t, a=0.7, speed=3000, n=30, col=(1, 1, 1), up=True):
    r = random.Random(9)
    c.set_line_width(7)
    for i in range(n):
        x = r.uniform(0, W); L = r.uniform(200, 500); off = r.uniform(0, H*2)
        y = ((off+t*speed) % (H+L*2))-L
        if not up: y = H-y
        c.set_source_rgba(*col, a*r.uniform(0.4, 1)); c.move_to(x, y); c.line_to(x, y+L); c.stroke()

def city_ground(c, base, t, scale=1.0, dark=0.0):
    r = random.Random(7)
    for i in range(12):
        w = r.uniform(70, 150)*scale; hh = r.uniform(120, 420)*scale; x = i*W/11-40
        col = mix([hexc('#F4B860'), hexc('#7FA7C9'), hexc('#E57A5A'), hexc('#9BC48A')][i % 4], hexc('#2A2E3A'), dark)
        box(c, x, base-hh, w, hh, col, 3, 3)
        for wy in range(int(base-hh+18*scale), int(base-14*scale), int(38*scale)+1):
            for wx in range(int(x+12*scale), int(x+w-20*scale), int(30*scale)+1):
                c.rectangle(wx, wy, 14*scale, 18*scale); c.set_source_rgba(1, 1, 1, 0.55*(1-dark)); c.fill()
    c.rectangle(0, base, W, H-base); c.set_source_rgb(*mix(hexc('#6E6A78'), hexc('#1E2028'), dark)); c.fill()

def banana(c, x, y, s, rot=0.0, bite=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.new_path(); c.move_to(-180, -40); c.curve_to(-120, 90, 120, 90, 180, -40); c.curve_to(110, 30, -110, 30, -180, -40); c.close_path()
    fs(c, hexc('#FFD54A'), 5)
    c.new_path(); c.move_to(-170, -36); c.curve_to(-100, 40, 100, 40, 170, -36); c.set_source_rgba(*hexc('#E0A92A'), 0.8); c.set_line_width(6); c.stroke()
    rrect(c, 172, -62, 26, 30, 6); fs(c, hexc('#6B4A2A'), 3)
    circle(c, -182, -40, 9); fs(c, hexc('#3A2A1A'), 0)
    if bite > 0:   # trozo que sobra (marcado)
        c.save(); c.new_path(); c.rectangle(180-360*bite, -80, 360*bite, 160); c.clip()
        c.new_path(); c.move_to(-180, -40); c.curve_to(-120, 90, 120, 90, 180, -40); c.curve_to(110, 30, -110, 30, -180, -40); c.close_path()
        c.set_source_rgba(1, 1, 1, 0.55); c.fill(); c.restore()
    c.restore()

def bar(c, x, y, w, h, k, col, bg=None, lab=None):
    rrect(c, x, y, w, h, h/2); fs(c, bg or C['paper'], 4)
    if k > 0: rrect(c, x+6, y+6, max(h-12, (w-12)*k), h-12, (h-12)/2); fs(c, col, 0)
    if lab: txt(c, lab, x+w/2, y+h*0.68, h*0.5, OUT)

def zrow(c, base, t, n=7, h=330, lit=0.55, look_up=False, spread=150, x0=60):
    for i in range(n):
        x = x0+i*spread + math.sin(t*0.7+i)*8
        teo(c, x, base+(i % 2)*30, h*(0.92+0.08*(i % 3)), "zarms" if not look_up else "stand", t+i, face=1 if i % 2 else -1,
            walk=0 if look_up else t*1.2+i*0.3, expr="angry", look=(0.0, -0.9) if look_up else (0.2, 0.1),
            who=__import__('scenes_q2').ZOMB[i % 4], lit=lit)

# ---------------- escenas ----------------
def q5_0(c, lt, d, t):   # gancho: despiertas en un anime y sales disparado 100 m
    k = P(lt, d, 0.18, 0.75)
    grad_bg(c, SKYA, SKYB)
    halftone(c, hexc('#FFFFFF'), 0.25, 40, 0, 0, W, 700, grow=0.5)
    rise = ease(k)*1400
    c.save(); c.translate(0, rise)
    city_ground(c, 1300, t)
    c.restore()
    if lt < d*0.2:   # agachado, cargando
        sh = math.sin(t*70)*6
        hero(c, W/2+sh, 1300, 520, "crouch", t, expr="focus", aura=0.6+0.4*math.sin(t*12))
        burst_text(c, "¡¿EH?!", 790, 460, lt, 80, PAL['yellow'], -0.1)
    else:
        radial(c, W/2, 760, t, (1, 1, 1), 0.55, 48, 3, 300)
        vlines(c, t, 0.75, 3200)
        y = 1300-ease(clamp((lt-d*0.2)/0.4))*360
        hero(c, W/2, y, 560, "jump", t, expr="shock", aura=1.0)
        if lt > d*0.35: chip(c, "100 METROS ↑", W/2, 400, lt-d*0.35, ic_bolt, size=54, bg=C['red'], fg=C['paper'])
    post(c, t, 0.25, 0.04)

def q5_1(c, lt, d, t):   # despegar a 160 km/h
    grad_bg(c, hexc('#5FB7E8'), SKYB)
    vlines(c, t, 0.8, 3600, 36)
    hero(c, 300, 1250, 470, "jump", t, expr="focus", aura=0.9)
    speedo(c, 760, 760, 230, 160, 200, "KM/H AL DESPEGAR", lt)
    if lt > d*0.55: chip(c, "≈ 44 METROS POR SEGUNDO", W/2, 360, lt-d*0.55, size=30, bg=C['gold'])
    post(c, t, 0.25, 0.04)

def q5_2(c, lt, d, t):   # la energía cabe en un plátano (y sobra)
    grad_bg(c, hexc('#FFF4D6'), hexc('#FFD9A8'))
    halftone(c, hexc('#F3A64A'), 0.22, 36)
    wob = math.sin(t*3)*0.06
    banana(c, W/2, 700, 1.9, -0.15+wob, bite=0.37*ease(P(lt, d, 0.6, 0.85)))
    stat_card(c, "ENERGÍA DEL SALTO (70 KG)", "69", "kJ", W/2, 420, lt-0.2, ic_bolt, sub="≈ 66 kcal de comida")
    if lt > d*0.45:
        kk = ease(P(lt, d, 0.45, 0.8))
        bar(c, 140, 1000, 800, 76, 0.63*kk, CRIM)
        txt(c, "1 PLÁTANO ≈ 105 kcal", W/2, 1140, 40, OUT)
    if lt > d*0.75: chip(c, "¡Y SOBRA UN TROZO!", W/2, 1230, lt-d*0.75, ic_check, size=40, bg=C['leaf'], fg=C['paper'])
    post(c, t, 0.2, 0.04)

def q5_3(c, lt, d, t):   # soltarla en 0,02 s = 3 MW
    flash = lt > d*0.45
    grad_bg(c, hexc('#1C1A2E') if flash else hexc('#2E4A7A'), hexc('#4A2040') if flash else hexc('#7FD0F5'))
    if flash: radial(c, W/2, 820, t, GOLD, 0.5, 56, 5, 200)
    hero(c, W/2, 1290, 470, "crouch" if not flash else "jump", t, expr="focus", aura=1.0 if flash else 0.5)
    # cronómetro
    secs = 0.02*clamp(lt/(d*0.4))
    rrect(c, 250, 330, 580, 170, 30); fs(c, C['paper'], 5)
    txt(c, f"{secs:0.2f} s".replace(".", ","), W/2, 450, 110, CRIM2, "Anton")
    if flash:
        stat_card(c, "POTENCIA", "3", "MEGAVATIOS", W/2, 660, lt-d*0.45, ic_bolt, sub="¡un aerogenerador!")
    post(c, t, 0.3, 0.05)

def q5_4(c, lt, d, t):   # más que mil Bolts empujando
    grad_bg(c, hexc('#FFE08A'), hexc('#FF9F6B'))
    radial(c, W/2, 820, t, (1, 1, 1), 0.35, 40, 7, 200)
    n = int(1000*eout(clamp(lt/(d*0.75))))
    cols = [CRIM, hexc('#2F6F7A'), hexc('#E2A63B'), hexc('#6F8F5A')]
    shown = min(160, n//6+1)
    for i in range(shown):
        cx = 70+(i % 16)*63; cy = 640+(i//16)*66
        mini(c, cx, cy, 58, cols[i % 4], t, jump=abs(math.sin(t*9+i))*6, arms=1.0)
    rrect(c, 200, 300, 680, 170, 30); fs(c, C['paper'], 5)
    txt(c, f"{n:,}".replace(",", "."), W/2, 430, 120, CRIM2, "Anton")
    chip(c, "VELOCISTAS A LA VEZ", W/2, 540, lt, size=34, bg=C['red'], fg=C['paper'])
    chip(c, "1 VELOCISTA TOP ≈ 2,6 kW", W/2, 1330, lt-0.3, size=34, bg=C['ink'], fg=C['paper'])
    post(c, t, 0.25, 0.04)

def q5_5(c, lt, d, t):   # 200 g vs récord 46 g
    grad_bg(c, hexc('#2A2240'), hexc('#5A2A3A'))
    halftone(c, hexc('#FF5A6A'), 0.12, 38)
    v = 200*eout(clamp(lt/(d*0.4)))
    cx, cy, r = W/2, 700, 290
    circle(c, cx, cy, r); fs(c, C['paper'], 6)
    c.set_line_width(26)
    for i, cc in enumerate((C['leaf'], C['gold'], C['red'])):
        c.new_path(); a0 = math.pi*0.75+i*math.pi*0.5; c.arc(cx, cy, r-40, a0, a0+math.pi*0.5); c.set_source_rgb(*cc); c.stroke()
    a46 = math.pi*0.75+1.5*math.pi*46/220
    c.set_source_rgb(*OUT); c.set_line_width(8); c.move_to(cx+math.cos(a46)*(r-70), cy+math.sin(a46)*(r-70)); c.line_to(cx+math.cos(a46)*(r+10), cy+math.sin(a46)*(r+10)); c.stroke()
    ang = math.pi*0.75+1.5*math.pi*clamp(v/220)
    c.set_line_width(14); c.move_to(cx, cy); c.line_to(cx+math.cos(ang)*(r-70), cy+math.sin(ang)*(r-70)); c.stroke()
    circle(c, cx, cy, 22); c.set_source_rgb(*OUT); c.fill()
    txt(c, f"{int(v)} g", cx, cy+r*0.62, 110, CRIM, "Anton")
    if lt > d*0.5:
        chip(c, "RÉCORD EN PRUEBAS: 46 g (1954)", W/2, 330, lt-d*0.5, ic_warn, size=34, bg=C['gold'], anchor=(cx+math.cos(a46)*(r+10), cy+math.sin(a46)*(r+10)))
    if lt > d*0.7: chip(c, "MÁS DE 4 VECES EL RÉCORD", W/2, 1160, lt-d*0.7, size=44, bg=C['red'], fg=C['paper'])
    shake(c, t, 4 if lt > d*0.3 else 0)
    post(c, t, 0.35, 0.05)

def q5_6(c, lt, d, t):   # en el anime aguantas: subes y gritas el ataque
    shout = lt > d*0.55
    if not shout:
        grad_bg(c, hexc('#7FD0F5'), hexc('#FFF1C9'))
        k = P(lt, d, 0, 0.55)
        c.save(); c.translate(0, 900*ease(k)); city_ground(c, 1300, t, 0.9); c.restore()
        vlines(c, t, 0.6, 2600)
        hero(c, W/2, 1180-120*ease(k), 500, "jump", t, expr="happy" if lt > d*0.2 else "focus", aura=0.8)
        if lt > d*0.15: chip(c, "CUERPO DE ANIME: OK ✓", W/2, 380, lt-d*0.15, ic_check, size=38, bg=C['leaf'], fg=C['paper'])
    else:
        lt2 = lt-d*0.55
        grad_bg(c, hexc('#3A0A18'), hexc('#E8394A'))
        radial(c, W/2, 840, t, (1, 0.9, 0.85), 0.6, 64, 11, 220)
        orb = 140+40*math.sin(t*14)
        halo(c, W/2, 640, orb*1.6, t, 1.0, CRIM)
        circle(c, W/2, 640, orb*0.55); fs(c, hexc('#FFE3E6'), 0)
        hero(c, W/2, 1300, 520, "attack", t, expr="angry", aura=1.0)
        burst_text(c, "¡TORMENTA", W/2, 380, lt2, 96, PAL['yellow'], -0.08)
        burst_text(c, "CARMESÍ!", W/2, 560, lt2-0.25, 96, PAL['yellow'], 0.06)
        shake(c, t, 6)
    post(c, t, 0.3, 0.05)

def q5_7(c, lt, d, t):   # error: el grito viaja a 340 m/s
    grad_bg(c, hexc('#9AD4EA'), hexc('#FDE7C2'))
    city_ground(c, 1300, t, 0.7)
    hx, hy = W/2, 560
    for i in range(6):
        rr = ((t*380+i*160) % 960)
        c.set_source_rgba(*CRIM, max(0, 1-rr/960)*0.9); c.set_line_width(12)
        c.new_path(); c.arc(hx, hy, rr, 0, 2*math.pi); c.stroke()
    hero(c, hx, hy+190, 230, "attack", t, expr="angry", aura=0.6)
    burst_text(c, "¡ERROR!", 820, 360, lt, 70, PAL['white'], 0.1)
    if lt > d*0.3: chip(c, "SONIDO: 343 m/s", W/2, 1180, lt-d*0.3, ic_clock, size=44, bg=C['paper'])
    post(c, t, 0.25, 0.04)

def q5_8(c, lt, d, t):   # en 3 s, 1 km... y empieza el apocalipsis zombi
    zk = P(lt, d, 0.5, 0.8)
    grad_bg(c, mix(hexc('#B9E1F0'), hexc('#3A2A40'), zk), mix(hexc('#EAD9B0'), hexc('#6A3A3A'), zk))
    # mapa visto desde arriba
    cx, cy = W/2, 780
    r_ = random.Random(3)
    for i in range(70):
        x = r_.uniform(40, W-120); y = r_.uniform(380, 1220); w = r_.uniform(50, 120); h = r_.uniform(40, 100)
        box(c, x, y, w, h, mix(hexc('#E8E1D2'), hexc('#5A5260'), zk), 4, 2)
    secs = min(3.0, 3.0*clamp(lt/(d*0.5)))
    rr = 430*secs/3
    c.set_source_rgba(*CRIM, 0.18); circle(c, cx, cy, rr); c.fill()
    c.set_source_rgba(*CRIM, 0.95); c.set_line_width(10); circle(c, cx, cy, rr); c.stroke()
    circle(c, cx, cy, 20); fs(c, GOLD, 4)
    rrect(c, 330, 300, 420, 120, 26); fs(c, C['paper'], 5)
    txt(c, f"{secs:0.1f} s · {int(1000*secs/3)} m".replace(".", ","), W/2, 382, 56, OUT, "Anton")
    if zk > 0:
        r2 = random.Random(8)
        for i in range(int(40*zk)):
            ang = r2.uniform(0, 2*math.pi); dist = r2.uniform(120, 420)*(1-0.25*ease(P(lt, d, 0.6, 1.0)))
            zx, zy = cx+math.cos(ang)*dist, cy+math.sin(ang)*dist
            circle(c, zx, zy, 13); fs(c, hexc('#8FA08A'), 3)
        chip(c, "APOCALIPSIS ZOMBI: DÍA 1", W/2, 1290, lt-d*0.5, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.35, 0.05)

def q5_9(c, lt, d, t):   # todos miran arriba · la transformación tarda 3 min
    grad_bg(c, hexc('#2A1E38'), hexc('#7A3A44'))
    halftone(c, hexc('#000000'), 0.18, 36)
    # tú, pequeñito arriba, con aura
    hero(c, W/2+math.sin(t*1.3)*20, 470, 170, "fall", t, expr="shock", aura=0.7)
    zrow(c, 1330, t, 7, 360, 0.5, look_up=True, spread=160, x0=60)
    # barra de transformación
    k = 0.04+0.03*clamp(lt/d)
    bar(c, 140, 620, 800, 70, k, GOLD, lab=None)
    txt(c, "TRANSFORMACIÓN… 0:07 / 3:00" if lt < d*0.5 else "TRANSFORMACIÓN… 0:09 / 3:00", W/2, 600, 34, C['paper'])
    post(c, t, 0.5, 0.06)

def q5_10(c, lt, d, t):  # ¿qué poder elegirías?
    grad_bg(c, hexc('#7FD0F5'), hexc('#FFF1C9'))
    radial(c, W/2, 820, t, (1, 1, 1), 0.4, 44, 13, 300)
    hero(c, W/2, 1300, 470, "think", t, expr="focus", aura=0.5)
    for i, (lab, x, y, bg) in enumerate((("SALTAR", 250, 470, C['red']), ("VOLAR", 820, 420, C['teal']), ("PARAR EL TIEMPO", W/2, 330, C['gold']))):
        if lt > 0.2+i*0.45: chip(c, lab, x, y, lt-0.2-i*0.45, ic_bolt if i < 2 else ic_clock, size=44, bg=bg, fg=C['paper'] if i < 2 else OUT)
    if lt > d*0.6: chip(c, "TE LEO EN COMENTARIOS", W/2, 600, lt-d*0.6, ic_check, size=32, bg=C['paper'])
    post(c, t, 0.25, 0.04)

def cover_q5(c):
    grad_bg(c, SKYA, SKYB)
    radial(c, W/2, 820, 1.0, (1, 1, 1), 0.55, 48, 3, 300)
    c.save(); c.translate(0, 560); city_ground(c, 1300, 0); c.restore()
    hero(c, W/2+120, 1580, 620, "jump", 1.3, expr="shock", aura=1.0)

SCENES = {"Q5": [q5_0, q5_1, q5_2, q5_3, q5_4, q5_5, q5_6, q5_7, q5_8, q5_9, q5_10]}
BOOMS = {"Q5": [0, 6]}
CALM = set()
COVER = {"Q5": cover_q5}
