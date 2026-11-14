"""Estilo «cine» — serie APAGON «Planta 8», parte 20 (FINAL): Paco en la puerta, el rellano lleno, efectivo,
vuelve la luz, aparatos de uno en uno, agua para varios días, y el mensaje de Rosa del primer día."""
from engine import *
from cine import *
from scenes_c4 import marta, julian, P, glow, stairs
from scenes_c5 import paco
from scenes_c16 import torch_beam, tomas
from scenes_c17 import rosa, bulb
from scenes_c19 import hugo, home, phone, bubble, bill, note_paper
import cairo, math, random

def landing(c, t, night=0.85, light=0.0):
    """rellano de la 8ª: pared, puerta del 8º B, placa, ascensor"""
    wall_room(c, C['wall2'], 1320, night*(1-0.7*light))
    # ascensor a la derecha
    ex = 860
    box(c, ex-150, 600, 300, 720, mix(C['steel2'], C['night1'], night*0.6), 6)
    box(c, ex-140, 610, 138, 700, mix(C['steel'], C['night1'], night*0.6), 2, 3)
    box(c, ex+2, 610, 138, 700, mix(C['steel'], C['night1'], night*0.6), 2, 3)
    on = light > 0.5
    circle(c, ex+190, 960, 18); fs(c, hexc('#5BD38A') if on else hexc('#3A2A2A'), 3)
    box(c, ex-60, 540, 120, 46, C['dark'], 6, 3)
    txt(c, "8" if on else "--", ex, 576, 34, hexc('#FFC845') if on else C['steel'], "Anton")
    if light > 0:
        c.set_source_rgba(1, 0.95, 0.8, 0.18*light); c.paint()

def door_scene(c, t, night=0.9, knock=0.0, open_=0.0, light=0.0):
    wall_room(c, C['wall2'], 1320, night)
    door(c, 560, 1320, 300, 720, open_=open_, light=light, night=night, knock=knock, t=t)
    box(c, 140, 520, 160, 70, C['paper'], 8); txt(c, "8º B", 220, 570, 40, C['ink'], "Anton")

def peephole(c, t, k, who_fn):
    """vista a través de la mirilla: círculo con distorsión, Paco con linterna"""
    c.set_source_rgb(0, 0, 0); c.paint()
    r = lerp(120, 420, ease(k))
    c.save(); c.arc(W/2, 900, r, 0, 2*math.pi); c.clip()
    grad_bg(c, hexc('#2A2E3A'), hexc('#0B0D14'))
    torch_beam(c, 620, 1050, -2.4+0.15*math.sin(t*2), 600, 0.4)
    c.save(); c.translate(W/2, 900); c.scale(1.25, 1.25); c.translate(-W/2, -900)
    who_fn(c, W/2, 1500, 760, "stand", t, face=-1, expr="angry", lit=0.75)
    c.restore()
    g = cairo.RadialGradient(W/2, 900, r*0.4, W/2, 900, r); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.85)
    c.set_source(g); c.paint()
    c.restore()
    c.set_source_rgb(*OUT); c.set_line_width(14); c.arc(W/2, 900, r, 0, 2*math.pi); c.stroke()

def cash_stack(c, x, y, n, t, s=1.0):
    for i in range(n):
        bill(c, x+((i*37) % 60)-30, y-i*22, -0.08+0.05*math.sin(i*1.7), s)

def atm(c, x, base, t, dead=True, night=0.8):
    m = lambda cc: mix(cc, C['night1'], night*0.5)
    box(c, x-210, base-760, 420, 760, m(hexc('#5E6B7A')), 16)
    box(c, x-160, base-690, 320, 220, hexc('#11151F') if dead else hexc('#9FC3D3'), 10)
    if dead:
        txt(c, "FUERA DE", x, base-600, 34, C['red'], "Anton"); txt(c, "SERVICIO", x, base-550, 34, C['red'], "Anton")
    for r in range(3):
        for k in range(3): box(c, x-110+k*80, base-420+r*70, 60, 50, m(C['steel']), 6, 3)
    box(c, x-120, base-160, 240, 26, C['dark'], 6, 3)

def card_reader(c, x, y, t, dead=True):
    box(c, x-110, y-180, 220, 360, C['dark2'], 26)
    box(c, x-80, y-150, 160, 110, hexc('#11151F') if dead else hexc('#9ED88A'), 8, 3)
    if dead: txt(c, "SIN RED", x, y-82, 26, C['red'], "Anton")
    for r in range(3):
        for k in range(3): box(c, x-70+k*50, y-20+r*50, 40, 36, C['steel'], 5, 2)

def appliance(c, kind, x, base, on, t):
    col = C['paper']
    if kind == "tv":
        box(c, x-120, base-170, 240, 150, C['dark'], 10)
        box(c, x-105, base-158, 210, 124, hexc('#9FC3D3') if on else hexc('#11151F'), 4, 2)
        box(c, x-30, base-20, 60, 20, C['dark2'], 4, 3)
    elif kind == "micro":
        box(c, x-120, base-140, 240, 140, col, 14)
        box(c, x-100, base-120, 140, 100, hexc('#FFE3A0') if on else hexc('#3B4150'), 8, 3)
        for i in range(3): circle(c, x+75, base-100+i*35, 10); fs(c, C['steel'], 2)
    elif kind == "heater":
        box(c, x-90, base-220, 180, 220, col, 18)
        circle(c, x, base-110, 46); fs(c, hexc('#E2A63B') if on else C['steel'], 3)
    elif kind == "fridge":
        box(c, x-100, base-300, 200, 300, col, 16)
        c.set_source_rgb(*OUT); c.set_line_width(4); c.move_to(x-100, base-190); c.line_to(x+100, base-190); c.stroke()
        box(c, x+60, base-270, 12, 60, C['steel2'], 6, 2)
    # piloto
    circle(c, x, base+28, 13); fs(c, hexc('#5BD38A') if on else hexc('#3A2A2A'), 3)

def jug(c, x, base, s=1.0, fill=1.0):
    box(c, x-60*s, base-200*s, 120*s, 200*s, hexc('#CFE8F2'), 22*s, 4)
    if fill > 0:
        c.save(); rrect(c, x-56*s, base-196*s, 112*s, 192*s, 20*s); c.clip()
        c.rectangle(x-60*s, base-196*s*fill, 120*s, 200*s); c.set_source_rgba(0.35, 0.65, 0.85, 0.8); c.fill(); c.restore()
    box(c, x-26*s, base-236*s, 52*s, 40*s, C['teal'], 8*s, 3)

# ---------------- escenas ----------------
def c20_0(c, lt, d, t):   # gancho: golpes en la puerta, «sé que estás ahí, Hugo»
    k = ease(P(lt, d))
    c.save(); z = 1.05+0.22*k; c.translate(W/2, 900); c.scale(z, z); c.translate(-W/2, -900)
    kn = 1.0 if (t % 1.1) < 0.45 else 0.0
    door_scene(c, t, 0.9, knock=kn)
    c.new_path(); c.move_to(410, 1320); c.line_to(710, 1320); c.line_to(820, 1400); c.line_to(300, 1400); c.close_path()
    c.set_source_rgba(1, 0.92, 0.7, 0.3+0.15*math.sin(t*9)); c.fill()
    if kn: knock_marks(c, 640, 760, t)
    c.restore()
    marta(c, 150, 1720, 600, "listen", t, face=1, expr="shock", lit=0.5)
    hugo(c, 950, 1720, 600, "stand", t, face=-1, expr="shock", lit=0.5)
    if lt > 0.9: time_card(c, "APAGÓN", "DÍA 8", "PLANTA 8 · 8º B", W/2, 330, lt-0.9)
    if lt > d*0.62: chip(c, "«SÉ QUE ESTÁS AHÍ, HUGO»", W/2, 1660, lt-d*0.62, ic_warn, size=32, bg=C['red'], fg=C['paper'])
    post(c, t, 0.75, 0.09)

def c20_1(c, lt, d, t):   # Hugo va a abrir; Marta le frena; mirilla: Paco, solo
    if lt < d*0.45:
        door_scene(c, t, 0.85)
        hugo(c, 520, 1640, 600, "reach", t, face=1, walk=lt*1.2 if lt < d*0.25 else 0, expr="focus", lit=0.6)
        if lt > d*0.2:
            marta(c, 200, 1660, 600, "reach", t, face=1, expr="angry", lit=0.6)
            chip(c, "¡NO ABRAS!", W/2, 420, lt-d*0.2, ic_warn, size=40, bg=C['red'], fg=C['paper'])
    else:
        peephole(c, t, P(lt, d, 0.45, 0.7), paco)
        if lt > d*0.62: chip(c, "ES PACO. SOLO.", W/2, 1600, lt-d*0.62, size=38, bg=C['gold'])
    post(c, t, 0.7, 0.09)

def c20_2(c, lt, d, t):   # «no vengo a pegar a nadie… vengo a cobrar»
    grad_bg(c, hexc('#2A2E3A'), hexc('#0B0D14'))
    stairs(c, t, 0.92)
    torch_beam(c, 760, 1180, -2.6+0.1*math.sin(t*1.5), 650, 0.45)
    k = ease(P(lt, d, 0, 0.6))
    paco(c, lerp(980, 820, k), 1640, 640, "stand", t, face=-1, expr="angry", lit=0.75)
    if lt > d*0.1: chip(c, "«NO VENGO A PEGAR A NADIE»", W/2, 420, lt-d*0.1, size=30, bg=C['paper'])
    if lt > d*0.55: chip(c, "«VENGO A COBRAR»", W/2, 520, lt-d*0.55, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.75, 0.09)

def c20_3(c, lt, d, t):   # pasos en la escalera: Rosa, Julián y Tomás llenan el rellano
    landing(c, t, 0.85)
    paco(c, 520, 1560, 560, "stand", t, face=1, expr="shock" if lt > d*0.4 else "angry", lit=0.75)
    for i, (fn, x0, x1) in enumerate(((rosa, -150, 120), (julian, -250, 260), (tomas, 1250, 940))):
        kk = ease(P(lt, d, 0.15+i*0.15, 0.5+i*0.15))
        x = lerp(x0, x1, kk)
        fn(c, x, 1700, 560, "stand", t, face=1 if x1 > x0 else -1, walk=lt*1.3 if 0 < kk < 1 else 0, expr="focus", lit=0.7)
    for i in range(3):
        c.set_source_rgba(1, 1, 1, 0.3); c.set_line_width(4); r = 30+((t*120+i*30) % 90); c.arc(120, 1500, r, -1.2, 1.2); c.stroke()
    if lt > d*0.3: chip(c, "PASOS EN LA ESCALERA", W/2, 420, lt-d*0.3, size=32, bg=C['dark'], fg=C['paper'])
    if lt > d*0.7: chip(c, "PACO YA NO ESTÁ SOLO", W/2, 1660, lt-d*0.7, size=34, bg=C['gold'])
    post(c, t, 0.7)

def c20_4(c, lt, d, t):   # Rosa: «yo escribí las notas. Se acabó»
    k = ease(P(lt, d))
    landing(c, t, 0.8)
    c.save(); z = 1.0+0.12*k; c.translate(300, 1300); c.scale(z, z); c.translate(-300, -1300)
    rosa(c, 300, 1680, 640, "reach", t, face=1, expr="focus", lit=0.85)
    c.restore()
    paco(c, 860, 1680, 600, "stand", t, face=-1, expr="worried", lit=0.75)
    for i in range(3):
        kk = pop(lt-0.3-i*0.25)
        if kk > 0:
            c.save(); c.translate(560+(i-1)*150, 820-i*30); c.scale(kk, kk); note_paper(c, 0, 0, -0.1+i*0.1, 0.7, ("VEN SOLA", "LO SÉ TODO", "NO SALGAS")[i]); c.restore()
    if lt > d*0.15: chip(c, "«YO ESCRIBÍ LAS NOTAS»", W/2, 420, lt-d*0.15, size=34, bg=C['paper'])
    if lt > d*0.62: chip(c, "«SE ACABÓ»", W/2, 1660, lt-d*0.62, size=40, bg=C['red'], fg=C['paper'])
    post(c, t, 0.65)

def c20_5(c, lt, d, t):   # Paco baja la linterna: sin luz no hay cajeros
    grad_bg(c, hexc('#202838'), hexc('#080A10'))
    if lt < d*0.45:
        landing(c, t, 0.85)
        a = lerp(-0.4, 1.3, ease(P(lt, d, 0, 0.4)))
        torch_beam(c, 620, 1180, a, 500, 0.4)
        paco(c, 620, 1680, 680, "think", t, face=-1, expr="worried", lit=0.8)
        chip(c, "PACO BAJA LA LINTERNA", W/2, 420, lt, size=32, bg=C['dark'], fg=C['paper'])
    else:
        street(c, t, 0.0, 0.0, 0.95)
        atm(c, W/2, 1450, t, dead=True)
        if lt > d*0.55: chip(c, "SIN LUZ, NO HAY CAJEROS", W/2, 420, lt-d*0.55, ic_bolt, size=32, bg=C['red'], fg=C['paper'])
        if lt > d*0.75: chip(c, "«UNA SEMANA SIN PODER PAGAR»", W/2, 1660, lt-d*0.75, size=28, bg=C['paper'])
    post(c, t, 0.7)

def c20_6(c, lt, d, t):   # REGLA 1: efectivo en casa
    wall_room(c, C['wall'], 1300, 0.5)
    atm(c, 280, 1300, t, dead=True, night=0.4)
    card_reader(c, 800, 1060, t, dead=True)
    cross(c, 280, 900, 150, P(lt, d, 0.3, 0.45)); cross(c, 800, 1000, 120, P(lt, d, 0.4, 0.55))
    n = int(1+7*ease(P(lt, d, 0.55, 0.85)))
    if lt > d*0.55:
        c.save(); c.translate(W/2, 1250); s = pop(lt-d*0.55, 0.4); c.scale(max(s, 1e-3), max(s, 1e-3))
        box(c, -200, -40, 400, 120, hexc('#7A5640'), 12)
        cash_stack(c, 0, -40, n, t, 0.9); c.restore()
    if lt > d*0.05: rule_card(c, 1, "TEN ALGO DE", "EFECTIVO EN CASA", W/2, 420, lt-d*0.05, ic_check)
    if lt > d*0.7: chip(c, "CAJEROS Y DATÁFONOS PUEDEN FALLAR", W/2, 1660, lt-d*0.7, ic_warn, size=26, bg=C['gold'])
    post(c, t, 0.55)

def c20_7(c, lt, d, t):   # Hugo abre la puerta, le da todo lo que lleva, promete el resto
    op = ease(P(lt, d, 0.0, 0.35))
    door_scene(c, t, 0.75, open_=op, light=0.25*op)
    hugo(c, 440, 1660, 600, "reach", t, face=1, expr="worried", lit=0.85)
    paco(c, 820, 1660, 600, "reach" if lt > d*0.4 else "stand", t, face=-1, expr="neutral", lit=0.8)
    if lt > d*0.35:
        kk = ease(P(lt, d, 0.35, 0.6)); x = lerp(520, 720, kk); y = 1100-120*math.sin(kk*math.pi)
        for i in range(3): bill(c, x+i*18, y-i*16, -0.1+i*0.08, 0.8)
    if lt > d*0.3: chip(c, "TODO LO QUE LLEVA ENCIMA", W/2, 420, lt-d*0.3, size=32, bg=C['paper'])
    if lt > d*0.68: chip(c, "«Y TE DEVUELVO EL RESTO»", W/2, 1660, lt-d*0.68, ic_check, size=32, bg=C['gold'])
    post(c, t, 0.6)

def c20_8(c, lt, d, t):   # un zumbido: neveras, vuelve la luz en todo el barrio
    on = clamp((lt-d*0.35)/0.4)
    if lt < d*0.6:
        landing(c, t, 0.85, light=on)
        for i in range(4):
            c.set_source_rgba(1, 1, 1, 0.35*(1-on*0.5)); c.set_line_width(5); r = 40+((t*160+i*35) % 140); c.arc(860, 960, r, 0, 2*math.pi); c.stroke()
        marta(c, 260, 1700, 600, "listen", t, face=1, expr="shock", lit=0.6+0.4*on)
        chip(c, "BZZZZ…", W/2, 420, lt, size=40, bg=C['dark'], fg=C['paper'])
    else:
        # barrio entero: ventanas encendiéndose en cascada
        kk = P(lt, d, 0.6, 0.95)
        grad_bg(c, hexc('#1A2135'), hexc('#05070C'))
        c.save(); c.translate(W/2, 960); s = 1.32-0.08*kk; c.scale(s, s); c.translate(-W/2, -960)
        window_city(c, 40, 240, 1000, 1440, t, night=0.95, lights_out=1-kk)
        c.restore()
        chip(c, "¡HA VUELTO LA LUZ!", W/2, 420, lt-d*0.6, ic_bolt, size=40, bg=C['gold'])
        if lt > d*0.78: chip(c, "EN TODO EL BARRIO", W/2, 1660, lt-d*0.78, size=34, bg=C['paper'])
    post(c, t, 0.5)

def c20_9(c, lt, d, t):   # REGLA 2: aparatos de uno en uno
    wall_room(c, C['wall2'], 1300, 0.35)
    kinds = ("fridge", "tv", "micro", "heater")
    xs = (200, 430, 660, 890)
    for i, (kd, x) in enumerate(zip(kinds, xs)):
        on = lt > d*(0.3+i*0.14)
        appliance(c, kd, x, 1180, on, t)
        if on and lt < d*(0.3+i*0.14)+0.5:
            glow(c, x, 1080, 200, (1, 0.9, 0.5), 0.35)
    # contador 1, 2, 3, 4
    n = sum(1 for i in range(4) if lt > d*(0.3+i*0.14))
    if n: txt(c, f"{n}", W/2, 1440, 120, C['gold'], "Anton")
    if lt > d*0.05: rule_card(c, 2, "VUELVE LA LUZ:", "DE UNO EN UNO", W/2, 420, lt-d*0.05, ic_check)
    if lt > d*0.75: chip(c, "NO LO ENCIENDAS TODO A LA VEZ", W/2, 1660, lt-d*0.75, ic_warn, size=28, bg=C['gold'])
    post(c, t, 0.5)

def c20_10(c, lt, d, t):  # REGLA 3: agua para varios días, ~4 L por persona y día
    grad_bg(c, hexc('#2A3550'), hexc('#0B0F18'))
    n = int(1+5*ease(P(lt, d, 0.25, 0.7)))
    for i in range(6):
        if i < n:
            kk = pop(lt-d*0.25-i*0.12, 0.3)
            if kk <= 0: continue
            c.save(); x = 180+(i % 3)*360; y = 1040+(i//3)*330; c.translate(x, y); c.scale(kk, kk)
            jug(c, 0, 0, 1.0); txt(c, f"DÍA {i+1}", 0, 70, 30, C['paper'], "Anton"); c.restore()
    if lt > d*0.05: rule_card(c, 3, "AGUA PARA", "VARIOS DÍAS", W/2, 420, lt-d*0.05, ic_drop)
    if lt > d*0.55: chip(c, "≈ 4 LITROS POR PERSONA Y DÍA", W/2, 1660, lt-d*0.55, ic_drop, size=30, bg=C['gold'])
    post(c, t, 0.5)

def c20_11(c, lt, d, t):  # el móvil vibra: llegan todos los mensajes de la semana
    home(c, t, 0.4, lamp=1.0)
    marta(c, 220, 1700, 560, "phone", t, face=1, expr="focus", lit=0.95)
    sh = math.sin(t*70)*6 if (t % 0.9) < 0.35 else 0
    k = ease(P(lt, d, 0.05, 0.3))
    n = int(1+30*ease(P(lt, d, 0.2, 0.85)))
    def scr(cc):
        txt(cc, "MENSAJES", 0, -220, 30, C['ink'], "Anton")
        for i in range(5):
            box(cc, -120, -170+i*80, 240, 62, C['paper'] if i % 2 else hexc('#9ED88A'), 14, 2)
        circle(cc, 100, -230, 34); fs(cc, C['red'], 3); txt(cc, str(n), 100, -218, 30, C['paper'], "Anton")
    phone(c, 720+sh, lerp(1900, 1000, k), 1.0, t, scr, rot=0.05)
    if lt > d*0.4: chip(c, "TODA LA SEMANA DE GOLPE", W/2, 420, lt-d*0.4, size=32, bg=C['gold'])
    post(c, t, 0.5)

def c20_12(c, lt, d, t):  # el último, de Rosa, del primer día: «tengo miedo. Ayúdame» · giro final
    if lt < d*0.42:
        grad_bg(c, hexc('#1A2135'), hexc('#05070C'))
        k = ease(P(lt, d, 0.0, 0.12))
        def scr(cc):
            txt(cc, "ROSA · 3ºA", 0, -220, 30, C['ink'], "Anton")
            txt(cc, "DÍA 1 · 19:12", 0, -175, 24, C['red'])
            bubble(cc, "MARTA, TENGO", "MIEDO. AYÚDAME.", 0, -50, 244, C['paper'], P(lt, d, 0.1, 0.25), size=22)
        c.save(); c.translate(W/2, 950); z = 1.2+0.15*k; c.scale(z, z); c.translate(-W/2, -950)
        phone(c, W/2, lerp(1800, 960, k), 1.45, t, scr)
        c.restore()
        if lt > d*0.2: chip(c, "EL ÚLTIMO MENSAJE. DEL PRIMER DÍA", W/2, 290, lt-d*0.2, ic_warn, size=26, bg=C['red'], fg=C['paper'])
        post(c, t, 0.75, 0.09)
    else:
        # rellano con luz: todos juntos; las notas caen y se vuelven «AYUDA»
        kk = ease(P(lt, d, 0.42, 0.7))
        landing(c, t, 0.5, light=1.0)
        marta(c, 170, 1700, 520, "stand", t, face=1, expr="worried", lit=1)
        rosa(c, 390, 1700, 500, "stand", t, face=-1, expr="neutral", lit=1)
        hugo(c, 610, 1700, 520, "stand", t, face=-1, expr="neutral", lit=1)
        julian(c, 790, 1700, 500, "stand", t, face=-1, expr="neutral", lit=1)
        tomas(c, 960, 1700, 520, "stand", t, face=-1, expr="neutral", lit=1)
        for i in range(3 if lt < d-2.6 else 0):
            y = lerp(500, 820, kk)+i*40; x = 300+i*240
            line = ("VEN SOLA", "LO SÉ TODO", "NO SALGAS")[i] if kk < 0.6 else "AYÚDAME"
            note_paper(c, x, y, -0.15+i*0.15+0.05*math.sin(t*2+i), 0.75, line)
        if lt > d*0.55: chip(c, "NO ERAN AMENAZAS", W/2, 380, lt-d*0.55, size=34, bg=C['dark'], fg=C['paper'])
        if lt > d*0.66: chip(c, "ERAN UNA PETICIÓN DE AYUDA", W/2, 1660, lt-d*0.66, ic_check, size=30, bg=C['gold'])
        darken(c, clamp((lt-(d-2.6))/0.5)*0.6)
        post(c, t, 0.55)

from scenes_c5 import cross
from scenes_c18 import street

SCENES = {"C20": [c20_0, c20_1, c20_2, c20_3, c20_4, c20_5, c20_6, c20_7, c20_8, c20_9, c20_10, c20_11, c20_12]}
BOOMS = {"C20": [0, 8]}
CALM = {"C20"}
