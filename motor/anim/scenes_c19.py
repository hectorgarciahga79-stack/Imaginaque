"""Estilo «cine» — serie APAGON «Planta 8», parte 19: lo que falló (Hugo, el hermano de Marta; SMS, teléfonos en papel, punto de encuentro)."""
from engine import *
from cine import *
from cine import teo as _teo
from scenes_c4 import marta, julian, P, glow, stairs, FL
from scenes_c5 import paco, generator, cross
from scenes_c17 import rosa, bulb
from scenes_c16 import torch_beam
from scenes_c18 import street
import cairo, math, random

# Hugo: hermano de Marta (mismo pelo castaño), parka verde oscuro, vaqueros
HUGO = dict(top=hexc('#3F5E5A'), top2=hexc('#2F4A46'), legs=hexc('#34465E'), legs2=hexc('#283850'), shoe=hexc('#E9E4DA'), skin=hexc('#E8C3A0'), hair=hexc('#6B4A32'))
def hugo(*a, **k): k['who'] = HUGO; return _teo(*a, **k)

def home(c, t, night=0.8, lamp=1.0):
    """piso de Marta: pared, ventana a la ciudad, lámpara de pie encendida"""
    wall_room(c, C['wall2'], 1300, night)
    window_city(c, 620, 380, 360, 460, t, night=0.95, lights_out=0.6)
    lx, ly = 250, 640
    if lamp > 0: glow(c, lx, ly, 620, (1, 0.82, 0.5), 0.55*lamp)
    c.set_source_rgb(*OUT); c.set_line_width(8); c.move_to(lx, ly+60); c.line_to(lx, 1290); c.stroke()
    box(c, lx-60, 1280, 120, 22, C['dark2'], 8, 3)
    c.new_path(); c.move_to(lx-90, ly+70); c.line_to(lx+90, ly+70); c.line_to(lx+55, ly-60); c.line_to(lx-55, ly-60); c.close_path()
    fs(c, (1, 0.9, 0.62) if lamp > 0 else C['steel'], 4)

def phone(c, x, y, s, t, fn, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rrect(c, -150, -290, 300, 580, 36); fs(c, C['dark'], 5)
    rrect(c, -132, -268, 264, 536, 24); fs(c, hexc('#EDEBE6'), 0)
    fn(c); c.restore()

def bubble(c, s1, s2, x, y, w, col, k, fg=None, size=30):
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    rrect(c, -w/2, -55, w, 110, 26); fs(c, col, 3)
    txt(c, s1, 0, -8, size, fg or C['ink']); txt(c, s2, 0, 32, size, fg or C['ink'])
    c.restore()

def bars(c, x, y, n_on, t):
    for i in range(4):
        h = 24+i*18; box(c, x+i*30, y-h, 20, h, C['ink'] if i < n_on else C['steel'], 3, 0)

def notepad(c, x, y, lines, k, rot=-0.04):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_source_rgba(0, 0, 0, 0.3); rrect(c, -230+10, -280+12, 460, 560, 10); c.fill()
    rrect(c, -230, -280, 460, 560, 10); fs(c, hexc('#FBF6E4'), 4)
    for i in range(7):
        c.set_source_rgba(0.35, 0.55, 0.8, 0.5); c.set_line_width(2); c.move_to(-200, -170+i*64); c.line_to(200, -170+i*64); c.stroke()
    c.set_source_rgba(0.85, 0.3, 0.3, 0.6); c.move_to(-160, -270); c.line_to(-160, 270); c.stroke()
    n = k*len(lines)
    for i, s in enumerate(lines):
        kk = clamp(n-i)
        if kk <= 0: break
        sub = s[:max(1, int(len(s)*kk))]
        txt(c, sub, -140, -182+i*64, 32, hexc('#1F2E5A'), align="left")
    c.restore()

def landline(c, x, base, t, ring=0.0):
    box(c, x-150, base-90, 300, 90, C['red2'], 20)
    box(c, x-170, base-150, 340, 70, C['red'], 30)
    for r in range(3):
        for k in range(3):
            circle(c, x-50+k*50, base-62+r*0, 0)
    for k in range(4): box(c, x-110+k*60, base-70, 44, 40, C['paper'], 6, 3)
    c.set_source_rgb(*OUT); c.set_line_width(6); c.move_to(x+160, base-120)
    for i in range(10): c.line_to(x+180+i*12, base-120+math.sin(i*1.6+t*3)*16)
    c.stroke()

def photo_card(c, x, y, s, k, rot=0.05):
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s*max(k, 1e-3), s*max(k, 1e-3))
    c.set_source_rgba(0, 0, 0, 0.35); rrect(c, -200+12, -160+14, 400, 320, 6); c.fill()
    rrect(c, -200, -160, 400, 320, 6); fs(c, C['paper'], 4)
    box(c, -175, -135, 350, 230, hexc('#5B6F9A'), 2, 0)
    box(c, -120, -20, 240, 80, hexc('#3B4150'), 20, 3); box(c, -80, -70, 150, 60, hexc('#3B4150'), 18, 3)
    box(c, -60, -62, 110, 44, hexc('#9FC3D3'), 8, 2); circle(c, -5, -40, 16); fs(c, HUGO['skin'], 2)
    circle(c, -80, 62, 22); fs(c, C['dark'], 3); circle(c, 80, 62, 22); fs(c, C['dark'], 3)
    txt(c, "HUGO", 0, 132, 30, C['ink'], "Anton")
    c.restore()

def bill(c, x, y, rot, s=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    box(c, -90, -45, 180, 90, hexc('#E2A63B'), 6, 3); circle(c, 0, 0, 26); fs(c, hexc('#C98F2A'), 2)
    txt(c, "50", -55, 12, 30, C['ink'], "Anton"); txt(c, "50", 55, 12, 30, C['ink'], "Anton")
    c.restore()

def note_paper(c, x, y, rot, s=1.0, line="VEN SOLA"):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    box(c, -110, -80, 220, 160, hexc('#FBF6E4'), 4, 3)
    txt(c, line, 0, 10, 28, hexc('#1F2E5A'))
    c.restore()

def pen(c, x, y, rot, s=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    box(c, -26, -110, 52, 200, hexc('#D9ECF2'), 16); box(c, -26, -40, 52, 60, C['paper'], 4, 3); box(c, -16, -140, 32, 34, C['teal'], 6)
    c.restore()

# ---------------- escenas ----------------
def c19_0(c, lt, d, t):   # gancho: alguien en el piso de Marta con la lámpara encendida → su hermano Hugo
    k = ease(P(lt, d))
    c.save(); z = 1.08+0.2*k; c.translate(W/2, 1050); c.scale(z, z); c.translate(-W/2+40*k, -1050)
    home(c, t, 0.85, lamp=0.9+0.1*math.sin(t*3))
    turn = 1 if lt > d*0.62 else -1
    hugo(c, 470, 1500, 560, "stand" if turn < 0 else "listen", t, face=turn, expr="neutral" if turn < 0 else "shock", lit=0.35 if lt < d*0.45 else 0.85)
    c.restore()
    marta(c, 930, 1700, 600, "stand", t, face=-1, expr="shock", lit=0.55)
    if lt > 2.4: time_card(c, "APAGÓN", "DÍA 7", "PLANTA 8 · 8º B", W/2, 330, lt-2.4)
    if lt > d*0.7: chip(c, "ES SU HERMANO, HUGO", W/2, 1660, lt-d*0.7, size=36, bg=C['gold'])
    post(c, t, 0.7, 0.09)

def c19_1(c, lt, d, t):   # lleva dos días buscándola; ha cruzado la ciudad andando
    street(c, t, lit_left=0.0, lit_right=0.0, night=0.95)
    x = lerp(-80, 1160, (lt/max(d, 0.1)))
    hugo(c, x, 1520, 470, "stand", t, face=1, walk=lt*1.4, expr="focus", lit=0.6)
    if lt > d*0.15: chip(c, "2 DÍAS BUSCÁNDOLA", W/2, 420, lt-d*0.15, ic_clock, size=34, bg=C['gold'])
    if lt > d*0.55: chip(c, "TODA LA CIUDAD A PIE", W/2, 1660, lt-d*0.55, size=34, bg=C['paper'])
    post(c, t, 0.65)

def c19_2(c, lt, d, t):   # «te mandé un mensaje» · «me llegó dos días tarde»
    home(c, t, 0.75)
    hugo(c, 260, 1560, 520, "stand", t, face=1, expr="worried", lit=0.85)
    marta(c, 880, 1560, 540, "phone", t, face=-1, expr="focus", lit=0.8)
    k = ease(P(lt, d, 0.1, 0.35))
    def scr(cc):
        txt(cc, "HUGO", 0, -220, 30, C['ink'], "Anton")
        bubble(cc, "NO TE FÍES DE NADIE", "DE TU EDIFICIO", 0, -80, 244, C['paper'], 1, size=21)
        txt(cc, "Enviado: hace 2 días", 0, 30, 22, C['steel2'] if 'steel2' in C else C['ink'])
        txt(cc, "Recibido: día 2", 0, 70, 22, C['red'])
    phone(c, W/2, lerp(1900, 900, k), 1.0, t, scr, rot=-0.04)
    if lt > d*0.6: chip(c, "2 DÍAS TARDE", W/2, 420, lt-d*0.6, ic_warn, size=38, bg=C['red'], fg=C['paper'])
    post(c, t, 0.55)

def c19_3(c, lt, d, t):   # REGLA 1: red saturada → SMS
    wall_room(c, C['wall'], 1300, 0.55)
    k1 = P(lt, d, 0.3, 0.55); k2 = P(lt, d, 0.6, 0.85)
    def call(cc):
        bars(cc, -60, -180, 1, t); txt(cc, "LLAMANDO…", 0, -60, 30, C['ink'], "Anton")
        circle(cc, 0, 70, 60); fs(cc, C['red'], 3)
        txt(cc, "RED OCUPADA", 0, 190, 24, C['red'])
    def sms(cc):
        bars(cc, -60, -180, 1, t); txt(cc, "SMS", 0, -60, 34, C['ink'], "Anton")
        bubble(cc, "ESTOY BIEN.", "VOY A CASA.", 0, 60, 230, hexc('#9ED88A'), 1)
        if k2 > 0: txt(cc, "ENTREGADO ✓", 0, 190, 24, hexc('#2E7D32'))
    phone(c, 300, 1000, 0.85, t, call, rot=-0.05)
    phone(c, 780, 1000, 0.85, t, sms, rot=0.05)
    cross(c, 300, 1060, 110, k1)
    if lt > d*0.05: rule_card(c, 1, "RED SATURADA:", "MANDA UN SMS", W/2, 480, lt-d*0.05, ic_check)
    if lt > d*0.6: chip(c, "EL SMS SUELE ENTRAR", W/2, 1660, lt-d*0.6, ic_check, size=28, bg=C['gold'])
    post(c, t, 0.55)

def c19_4(c, lt, d, t):   # intentó llamar desde un fijo… no se sabía su número
    wall_room(c, C['wall2'], 1300, 0.7)
    box(c, 360, 1080, 380, 30, C['wood'], 6)
    landline(c, 540, 1080, t)
    hugo(c, 850, 1560, 540, "think", t, face=-1, expr="worried", lit=0.8)
    digits = "6 _ _  _ _ _  _ _ _"
    if lt > d*0.2: chip(c, digits, W/2, 420, lt-d*0.2, size=40, bg=C['paper'])
    if lt > d*0.6: chip(c, "¿SU NÚMERO? NI IDEA", W/2, 1660, lt-d*0.6, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.55)

def c19_5(c, lt, d, t):   # REGLA 2: teléfonos importantes en papel
    wall_room(c, C['wall'], 1300, 0.55)
    notepad(c, 560, 1000, ["MARTA  6__ ___ ___", "HUGO   6__ ___ ___", "MAMÁ   9__ ___ ___", "EMERGENCIAS 112"], P(lt, d, 0.2, 0.75))
    # móvil sin batería que cae
    k = P(lt, d, 0.55, 0.9)
    def dead(cc):
        box(cc, -60, -30, 120, 60, C['paper'], 8, 3); box(cc, -55, -25, 14, 50, C['red'], 2, 0); box(cc, 60, -12, 10, 24, C['ink'], 2, 0)
    phone(c, 900, 1100+k*80, 0.45, t, dead, rot=0.2+k*0.3)
    if lt > d*0.05: rule_card(c, 2, "APUNTA EN PAPEL", "LOS TELÉFONOS CLAVE", W/2, 420, lt-d*0.05, ic_check)
    if lt > d*0.65: chip(c, "SI EL MÓVIL MUERE, SE VAN CON ÉL", W/2, 1660, lt-d*0.65, ic_warn, size=28, bg=C['gold'])
    post(c, t, 0.55)

def c19_6(c, lt, d, t):   # nunca quedaron en dónde verse
    grad_bg(c, hexc('#2A3550'), hexc('#0B0F18'))
    mini_map(c, W/2, 860, 0.8, t)
    for i, (x, y, col) in enumerate(((330, 700, MARTA['top']), (760, 1040, HUGO['top']))):
        k = pop(lt-0.2-i*0.3)
        if k > 0:
            c.save(); c.translate(x, y); c.scale(k, k); c.new_path(); c.arc(0, -40, 34, math.pi, 0); c.line_to(0, 20); c.close_path(); fs(c, col, 4); circle(c, 0, -40, 12); fs(c, C['paper'], 2); c.restore()
    if lt > d*0.4:
        c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(6); c.set_dash([18, 14]); c.move_to(330, 700); c.curve_to(560, 600, 520, 1100, 760, 1040); c.stroke(); c.set_dash([])
        txt(c, "?", 545, 900+math.sin(t*4)*10, 140, C['red'], "Anton")
    if lt > d*0.55: chip(c, "¿DÓNDE NOS VEMOS?", W/2, 1660, lt-d*0.55, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.55)

def c19_7(c, lt, d, t):   # REGLA 3: punto de encuentro + contacto fuera de la ciudad
    grad_bg(c, hexc('#2A3550'), hexc('#0B0F18'))
    mini_map(c, 430, 1000, 0.62, lt)
    kp = pop(lt-d*0.25, 0.4)
    if kp > 0:
        c.save(); c.translate(430, 960); c.scale(kp, kp); c.new_path(); c.arc(0, -50, 46, math.pi, 0); c.line_to(0, 30); c.close_path(); fs(c, C['red'], 4); circle(c, 0, -50, 16); fs(c, C['paper'], 2); c.restore()
        chip(c, "LA PLAZA, A LAS 12", 430, 1220, lt-d*0.25, ic_check, size=28, bg=C['paper'])
    k = P(lt, d, 0.5, 0.8)
    if k > 0:
        c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(6); c.set_dash([18, 14]); c.move_to(600, 880); c.line_to(lerp(600, 860, ease(k)), lerp(880, 820, ease(k))); c.stroke(); c.set_dash([])
        if k > 0.6:
            phone(c, 880, 960, 0.55, t, lambda cc: (txt(cc, "TÍA LOLA", 0, -40, 34, C['ink'], "Anton"), txt(cc, "OTRA CIUDAD", 0, 20, 26, C['red'])), rot=0.06)
    if lt > d*0.05: rule_card(c, 3, "PACTA UN PUNTO", "DE ENCUENTRO", W/2, 420, lt-d*0.05, ic_check)
    if lt > d*0.55: chip(c, "+ UN CONTACTO FUERA DE TU CIUDAD", W/2, 1660, lt-d*0.55, ic_check, size=28, bg=C['gold'])
    post(c, t, 0.55)

def c19_8(c, lt, d, t):   # Marta enseña la foto del buzón; Hugo se queda blanco
    home(c, t, 0.75)
    hugo(c, 300, 1560, 540, "stand" if lt < d*0.5 else "listen", t, face=1, expr="neutral" if lt < d*0.5 else "shock", lit=0.85)
    marta(c, 860, 1560, 540, "reach", t, face=-1, expr="focus", lit=0.8)
    photo_card(c, 620, 820, 1.0, pop(lt-0.2, 0.5), rot=0.06+0.02*math.sin(t*2))
    if lt > d*0.6: chip(c, "HUGO SE QUEDA BLANCO", W/2, 1660, lt-d*0.6, ic_warn, size=34, bg=C['red'], fg=C['paper'])
    post(c, t, 0.6)

def c19_9(c, lt, d, t):   # «Paco me prestó dinero. Mucho. Y yo desaparecí.»
    home(c, t, 0.85, lamp=0.6)
    s = 1+0.18*ease(P(lt, d))
    c.save(); c.translate(420, 1300); c.scale(s, s); c.translate(-420, -1300)
    hugo(c, 420, 1560, 560, "think", t, face=1, expr="worried", lit=0.7)
    c.restore()
    r = random.Random(4)
    for i in range(7):
        ph = (lt*0.35+i/7) % 1
        bill(c, 600+r.uniform(-60, 380), 300+ph*1000, r.uniform(-0.6, 0.6)+t*0.6*(1 if i % 2 else -1), 0.9)
    if lt > d*0.15: chip(c, "«PACO ME PRESTÓ DINERO»", W/2, 420, lt-d*0.15, size=34, bg=C['paper'])
    if lt > d*0.6: chip(c, "«Y YO DESAPARECÍ»", W/2, 1660, lt-d*0.6, size=36, bg=C['dark'], fg=C['paper'])
    post(c, t, 0.7, 0.09)

def c19_10(c, lt, d, t):  # Rosa escribía las notas; Paco le traía la insulina a cambio
    wall_room(c, C['wall2'], 1300, 0.75)
    rosa(c, 230, 1560, 470, "think", t, face=1, expr="worried", lit=0.8)
    paco(c, 860, 1560, 580, "stand", t, face=-1, expr="angry", lit=0.75)
    k = P(lt, d, 0.4, 0.8)
    note_paper(c, lerp(340, 700, ease(k)), 760-120*math.sin(k*math.pi), -0.1, 0.9)
    pen(c, lerp(740, 380, ease(k)), 980+120*math.sin(k*math.pi), 0.3, 0.9)
    if lt > d*0.1: chip(c, "ROSA ESCRIBÍA LAS NOTAS", W/2, 420, lt-d*0.1, size=32, bg=C['paper'])
    if lt > d*0.6: chip(c, "A CAMBIO DE INSULINA", W/2, 1660, lt-d*0.6, ic_warn, size=34, bg=C['red'], fg=C['paper'])
    post(c, t, 0.6)

def c19_11(c, lt, d, t):  # las notas, la foto, el generador: todo para llegar a Hugo
    grad_bg(c, hexc('#1A2135'), hexc('#05070C'))
    items = ((230, 640), (540, 560), (850, 640))
    for i, (x, y) in enumerate(items):
        k = pop(lt-0.2-i*0.45, 0.4)
        if k <= 0: continue
        c.save(); c.translate(x, y); c.scale(k, k)
        if i == 0: note_paper(c, 0, 0, -0.08, 0.9)
        elif i == 1: photo_card(c, 0, 0, 0.6, 1, 0.04)
        else: generator(c, 0, 90, 0.45, t, on=False, night=0.2)
        c.restore()
        kk = clamp((lt-0.6-i*0.45)/0.5)
        if kk > 0:
            c.set_source_rgba(*C['red2'], 0.95); c.set_line_width(8)
            c.move_to(x, y+120); c.line_to(lerp(x, W/2, kk), lerp(y+120, 1060, kk)); c.stroke()
    if lt > 1.8:
        k = pop(lt-1.8, 0.4); c.save(); c.translate(W/2, 1120); c.scale(max(k, 1e-3), max(k, 1e-3))
        hugo(c, 0, 220, 300, "stand", t, face=1, expr="shock", lit=0.9, shadow=False); c.restore()
        chip(c, "TODO ERA PARA LLEGAR A HUGO", W/2, 1660, lt-1.8, ic_warn, size=30, bg=C['gold'])
    post(c, t, 0.7)

def c19_12(c, lt, d, t):  # una linterna sube planta por planta
    k = ease(P(lt, d))
    stairs(c, t, 0.95)
    by = lerp(1500, 700, k); bx = 300+200*math.sin(k*math.pi*2)
    torch_beam(c, bx, by, -1.2+0.3*math.sin(t*2), 700, 0.55)
    circle(c, bx, by, 14); fs(c, (1, 0.95, 0.7), 2)
    fl = 2+int(k*5.99)
    chip(c, f"PLANTA {fl}", 760, 560, 1.0, ic_warn, size=38, bg=C['dark'], fg=C['paper'])
    for i in range(3):
        c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(4); r = 30+((t*120+i*30) % 90); c.arc(bx, by+60, r, 0.3, 2.8); c.stroke()
    if lt > d*0.4: chip(c, "ALGUIEN SUBE", W/2, 1660, lt-d*0.4, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.8, 0.09)

def c19_13(c, lt, d, t):  # «Sé que estás ahí, Hugo». ¿Tú abrirías?
    k = ease(P(lt, d))
    c.save(); z = 1+0.25*k; c.translate(W/2, 950); c.scale(z, z); c.translate(-W/2, -950)
    wall_room(c, C['wall2'], 1320, 0.92)
    door(c, 560, 1320, 300, 720, open_=0.0, light=0.0, night=0.9, knock=1.0 if (lt > d*0.3 and (t % 1.2) < 0.4) else 0.0, t=t)
    box(c, 140, 520, 160, 70, C['paper'], 8); txt(c, "8º B", 220, 570, 40, C['ink'], "Anton")
    # luz de linterna por la rendija
    c.new_path(); c.move_to(410, 1320); c.line_to(710, 1320); c.line_to(820, 1400); c.line_to(300, 1400); c.close_path()
    c.set_source_rgba(1, 0.92, 0.7, 0.35+0.15*math.sin(t*9)); c.fill()
    c.restore()
    marta(c, 160, 1700, 560, "stand", t, face=1, expr="shock", lit=0.45)
    hugo(c, 940, 1700, 560, "listen", t, face=-1, expr="shock", lit=0.45)
    if lt > d*0.2: chip(c, "«SÉ QUE ESTÁS AHÍ, HUGO»", W/2, 420, lt-d*0.2, ic_warn, size=32, bg=C['red'], fg=C['paper'])
    if lt > d*0.62: chip(c, "¿TÚ ABRIRÍAS LA PUERTA?", W/2, 1620, lt-d*0.62, size=36, bg=C['gold'])
    post(c, t, 0.75, 0.09)

SCENES = {"C19": [c19_0, c19_1, c19_2, c19_3, c19_4, c19_5, c19_6, c19_7, c19_8, c19_9, c19_10, c19_11, c19_12, c19_13]}
BOOMS = {"C19": [0, 13]}
CALM = {"C19"}
