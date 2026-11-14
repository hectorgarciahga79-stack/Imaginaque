"""Estilo «cine» — serie APAGON «Planta 8», parte 18: la luz vuelve… a medias (insulina, desenchufar, comida)."""
from engine import *
from cine import *
from cine import teo as _teo
from scenes_c4 import marta, julian, dani, P, smoke, glow, flat, FL
from scenes_c5 import generator, paco, cross
from scenes_c17 import rosa, tomas, patio, bulb, mini_fridge, cable, beam
import cairo, math, random

def street(c, t, lit_left=0.0, lit_right=0.0, night=0.9):
    """calle de noche vista desde el portal: mitad izquierda (enfrente) y derecha (su acera)"""
    grad_bg(c, mix(hexc('#2A3550'), hexc('#05070C'), night*0.7), mix(hexc('#1A2135'), hexc('#030409'), night*0.7))
    r = random.Random(11)
    for i, (x, w, h) in enumerate(((-40, 300, 820), (250, 280, 700), (520, 260, 900), (770, 340, 760))):
        on = lit_left if x < 500 else lit_right
        box(c, x, 1300-h, w, h, mix(hexc('#3B4150'), C['night1'], 0.5*(1-on)), 2, 3)
        for wy in range(1300-h+40, 1260, 90):
            for wx in range(x+30, x+w-50, 70):
                lit = on > 0 and r.random() < 0.6
                box(c, wx, wy, 40, 54, (1, 0.85, 0.5) if lit else mix(hexc('#1B2030'), C['night1'], 0.3), 3, 0, a=1)
    c.rectangle(0, 1300, W, H-1300); c.set_source_rgb(*mix(C['grey2'], C['night1'], 0.8)); c.fill()
    for x, on in ((180, lit_left), (430, lit_left), (720, lit_right), (960, lit_right)):
        c.set_source_rgb(*hexc('#2B2A2F')); c.rectangle(x-8, 760, 16, 560); c.fill()
        box(c, x-40, 740, 80, 30, hexc('#2B2A2F'), 8, 3)
        if on > 0: glow(c, x, 790, 380, (1, 0.8, 0.45), 0.55*on); c.new_path(); c.move_to(x-36, 770); c.line_to(x+36, 770); c.line_to(x+150, 1320); c.line_to(x-150, 1320); c.close_path(); c.set_source_rgba(1, 0.85, 0.5, 0.12*on); c.fill()

def appliance_row(c, x0, base, unplug, t):
    """tele, microondas y calentador enchufados a una regleta; unplug 0..1 los desconecta en orden"""
    # tele
    box(c, x0, base-260, 260, 170, hexc('#1A1A1E'), 10); box(c, x0+20, base-245, 220, 135, hexc('#2C3442'), 4, 0)
    box(c, x0+110, base-90, 40, 90, hexc('#26252A'), 4, 3)
    # microondas
    box(c, x0+300, base-190, 230, 140, C['paper'], 10); box(c, x0+320, base-170, 140, 100, hexc('#2C3442'), 6, 3)
    for i in range(3): circle(c, x0+495, base-150+i*35, 8); fs(c, C['steel2'], 2)
    # calentador
    box(c, x0+580, base-330, 150, 280, C['cream'], 30); circle(c, x0+655, base-160, 22); fs(c, C['red'], 3)
    box(c, x0+40, base-50, 700, 50, mix(C['wood'], C['night1'], 0.4), 6)
    # regleta + cables
    box(c, x0+250, base+80, 260, 50, C['paper'], 12, 3)
    for i, xx in enumerate((x0+130, x0+415, x0+655)):
        k = clamp(unplug*3-i)
        px, py = x0+290+i*80, base+105
        ex, ey = lerp(px, px+(i-1)*90, k), lerp(py, py+170, k)
        cable(c, xx, base-50, ex, ey-30, 60)
        box(c, ex-22, ey-40, 44, 36, hexc('#1A1A1E'), 6, 3)
        if k < 0.05 and math.sin(t*9+i) > 0.7: chip(c, "", px, py-70, 1, ic_bolt, size=22, bg=C['gold'])

# ---------------- escenas ----------------
def c18_0(c, lt, d, t):   # gancho: Paco en el patio, «ese generador es mío»
    k = ease(P(lt, d))
    c.save(); z = 1.05+0.22*k; c.translate(W/2, 1100); c.scale(z, z); c.translate(-W/2, -1100)
    patio(c, t, 0.9)
    generator(c, 560, 1480, 0.8, t, on=False, night=0.4)
    paco(c, 820, 1500, 580, "reach", t, face=-1, expr="angry", lit=0.75)
    rosa(c, 280, 1500, 430, "stand", t, face=1, expr="worried", lit=0.7)
    c.restore()
    if lt > 2.4: time_card(c, "APAGÓN", "DÍA 6", "PLANTA 8 · NOCHE", W/2, 330, lt-2.4)
    if lt > d*0.5: chip(c, "«ESE GENERADOR ES MÍO»", W/2, 1660, lt-d*0.5, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.72, 0.09)

def c18_1(c, lt, d, t):   # Rosa confiesa: la gasolina, la insulina
    patio(c, t, 0.85)
    s = 1+0.15*ease(P(lt, d))
    c.save(); c.translate(380, 1450); c.scale(s, s); c.translate(-380, -1450)
    rosa(c, 380, 1500, 470, "think", t, face=1, expr="worried", lit=0.8)
    box(c, 640, 1290, 110, 160, C['red'], 12); box(c, 665, 1260, 50, 40, C['red2'], 8, 3)
    c.restore()
    if lt > d*0.25: chip(c, "«LE COGÍ LA GASOLINA»", W/2, 420, lt-d*0.25, size=34, bg=C['paper'])
    if lt > d*0.6:
        k = pop(lt-d*0.6)
        c.save(); c.translate(820, 1050); c.scale(max(k, 1e-3), max(k, 1e-3)); c.rotate(0.15)
        box(c, -40, -110, 80, 200, hexc('#D9ECF2'), 16); box(c, -40, -40, 80, 70, C['paper'], 4, 3)
        box(c, -22, -150, 44, 44, C['teal'], 8); txt(c, "INSULINA", 0, 4, 18, C['ink']); c.restore()
    post(c, t, 0.6)

def c18_2(c, lt, d, t):   # Julián niega: casi te mata el humo
    patio(c, t, 0.85)
    julian(c, 700, 1500, 540, "stand", t, face=-1, expr="focus", lit=0.8, look=(math.sin(t*5)*0.3, 0))
    rosa(c, 340, 1500, 430, "stand", t, face=1, expr="worried", lit=0.75)
    for i in range(3):
        ph = (t*0.5+i/3) % 1; c.set_source_rgba(0.6, 0.6, 0.63, 0.25*(1-ph)); circle(c, 200+i*60, 1200-ph*500, 50+ph*80); c.fill()
    if lt > d*0.3: chip(c, "CASI TE MATA EL HUMO", W/2, 420, lt-d*0.3, ic_warn, size=34, bg=C['red'], fg=C['paper'])
    if lt > d*0.65: chip(c, "…Y NO HACÍA FALTA", W/2, 1660, lt-d*0.65, size=34, bg=C['gold'])
    post(c, t, 0.6)

def c18_3(c, lt, d, t):   # REGLA 1: insulina 28 días fuera de la nevera, 15–30 ºC
    wall_room(c, C['wall2'], 1300, 0.55)
    k = ease(P(lt, d, 0.2, 0.6))
    box(c, 360, 1080, 360, 30, C['wood'], 6)
    c.save(); c.translate(540, 1080-k*30)
    box(c, -45, -230, 90, 230, hexc('#D9ECF2'), 18); box(c, -45, -150, 90, 80, C['paper'], 4, 3); box(c, -26, -275, 52, 50, C['teal'], 8)
    c.restore()
    sx = lerp(980, 900, k); circle(c, sx, 330, 60); fs(c, C['gold'], 4)
    cross(c, sx, 330, 90, P(lt, d, 0.6, 0.85))
    if lt > d*0.05: rule_card(c, 1, "INSULINA: HASTA 28 DÍAS", "FUERA DE LA NEVERA", W/2, 560, lt-d*0.05, ic_check)
    if lt > d*0.4: chip(c, "ENTRE 15 Y 30 ºC", 300, 1300, lt-d*0.4, ic_clock, size=32, bg=C['gold'])
    if lt > d*0.7: chip(c, "LEJOS DEL SOL", 780, 1300, lt-d*0.7, ic_warn, size=32)
    post(c, t, 0.55)

def c18_4(c, lt, d, t):   # Paco deja el bidón: para la nevera de todos
    patio(c, t, 0.85)
    k = ease(P(lt, d, 0.2, 0.6))
    paco(c, 640, 1500, 580, "carry" if k < 1 else "stand", t, face=-1, expr="neutral", lit=0.8)
    bx, by = lerp(560, 470, k), lerp(1210, 1380, k)
    box(c, bx-55, by-80, 110, 160, C['red'], 12); box(c, bx-25, by-110, 50, 40, C['red2'], 8, 3)
    mini_fridge(c, 200, 1500, 0.8, 0.4)
    if lt > d*0.55: chip(c, "«PARA LA NEVERA DE TODOS»", W/2, 420, lt-d*0.55, ic_check, size=32, bg=C['paper'])
    post(c, t, 0.55)

def c18_5(c, lt, d, t):   # madrugada: zumbido, se encienden las farolas de enfrente
    on = clamp((lt-d*0.35)/0.5)
    if on > 0 and on < 1 and math.sin(t*40) > 0.3: on *= 0.3
    street(c, t, lit_left=on, lit_right=0, night=0.95)
    for i in range(3):
        c.set_source_rgba(1, 1, 1, 0.5); c.set_line_width(5); r = 40+((t*160+i*40) % 120); c.arc(300, 780, r, -0.6, 0.6); c.stroke()
    if lt > d*0.1: chip(c, "BZZZZ…", 300, 520, lt-d*0.1, size=40, bg=C['dark'], fg=C['paper'])
    if lt > d*0.55: chip(c, "05:12", 820, 440, lt-d*0.55, ic_clock, size=34, bg=C['gold'])
    post(c, t, 0.7, 0.09)

def c18_6(c, lt, d, t):   # vuelve la luz… solo en medio barrio
    street(c, t, lit_left=1, lit_right=0, night=0.95)
    k = ease(P(lt, d, 0.3, 0.8))
    c.set_source_rgba(1, 1, 1, 0.85); c.set_line_width(8); c.set_dash([30, 18])
    c.move_to(W/2, 300+0*k); c.line_to(W/2, 300+1050*k); c.stroke(); c.set_dash([])
    marta(c, 760, 1560, 520, "stand", t, face=-1, expr="worried", lit=0.55)
    if lt > d*0.1: chip(c, "CON LUZ", 260, 360, lt-d*0.1, ic_bolt, size=34, bg=C['gold'])
    if lt > d*0.45: chip(c, "SIN LUZ", 820, 360, lt-d*0.45, ic_warn, size=34, bg=C['dark'], fg=C['paper'])
    post(c, t, 0.6)

def c18_7(c, lt, d, t):   # Tomás lo tiene todo enchufado; Marta le frena
    wall_room(c, C['wall'], 1300, 0.75)
    appliance_row(c, 160, 1120, 0, t)
    tomas(c, 160, 1560, 470, "stand", t, face=1, expr="neutral", lit=0.7)
    if lt > d*0.45: marta(c, 900, 1560, 540, "reach", t, face=-1, expr="focus", lit=0.75)
    if lt > d*0.15: chip(c, "TELE · MICRO · CALENTADOR", W/2, 420, lt-d*0.15, ic_bolt, size=30)
    if lt > d*0.6: chip(c, "¡ESPERA!", 820, 1700, lt-d*0.6, ic_warn, size=40, bg=C['red'], fg=C['paper'])
    post(c, t, 0.6)

def c18_8(c, lt, d, t):   # REGLA 2: desenchufa; una lámpara encendida
    wall_room(c, C['wall'], 1300, 0.7)
    appliance_row(c, 160, 1160, P(lt, d, 0.25, 0.75), t)
    on = 1.0 if lt > d*0.85 else 0.0
    bulb(c, 930, 860, on, t)
    if lt > d*0.05: rule_card(c, 2, "EN UN APAGÓN,", "DESENCHUFA LOS APARATOS", W/2, 480, lt-d*0.05, ic_bolt)
    if lt > d*0.55: chip(c, "DEJA UNA LÁMPARA ENCENDIDA", W/2, 1660, lt-d*0.55, ic_check, size=30, bg=C['gold'])
    post(c, t, 0.55)

def c18_9(c, lt, d, t):   # a las seis se enciende la bombilla del patio; ascensor muerto
    on = clamp((lt-0.2)/0.4)
    if lt < d*0.5:
        patio(c, t, 0.75, lights=on)
        bulb(c, W/2, 520, on, t)
        marta(c, 300, 1500, 520, "stand", t, face=1, expr="neutral", lit=0.6+0.4*on)
        julian(c, 780, 1500, 520, "stand", t, face=-1, expr="neutral", lit=0.6+0.4*on)
        if lt > 0.3: chip(c, "06:00 · HAY LUZ", W/2, 1660, lt-0.3, ic_bolt, size=34, bg=C['gold'])
    else:
        lt2 = lt-d*0.5
        wall_room(c, C['wall2'], 1300, 0.6)
        box(c, 340, 560, 400, 740, C['steel2'], 8); box(c, 350, 570, 185, 720, C['steel'], 2, 3); box(c, 545, 570, 185, 720, C['steel'], 2, 3)
        box(c, 470, 470, 140, 60, hexc('#1A1A1E'), 8); txt(c, "– –", 540, 515, 40, C['red'], "Anton")
        circle(c, 800, 900, 26); fs(c, hexc('#3A2A2A'), 3)
        cross(c, 540, 930, 220, clamp(lt2/0.6))
        chip(c, "ASCENSOR: NADA", W/2, 420, lt2, ic_warn, size=34, bg=C['red'], fg=C['paper'])
        if lt2 > 0.6: chip(c, "EL AGUA NO SUBE", W/2, 1660, lt2-0.6, ic_drop, size=34)
    post(c, t, 0.55)

def c18_10(c, lt, d, t):  # Rosa abre su nevera: el pollo huele raro
    wall_room(c, C['wall2'], 1300, 0.5)
    op = ease(P(lt, d, 0.1, 0.4))
    fridge(c, 700, 1300, open_=op, night=0.3)
    if op > 0.5:
        box(c, 610, 1060, 180, 90, hexc('#E9C9A0'), 30)
        for i in range(3):
            ph = (t*0.8+i/3) % 1; c.set_source_rgba(0.45, 0.7, 0.3, 0.8*(1-ph)); c.set_line_width(6)
            c.new_path(); x = 650+i*50
            c.move_to(x, 1040-ph*120)
            for j in range(4): c.line_to(x+math.sin(j*1.7+t*5)*12, 1040-ph*120-j*24)
            c.stroke()
    rosa(c, 330, 1560, 460, "reach", t, face=1, expr="neutral" if lt < d*0.6 else "focus", lit=0.85)
    if lt > d*0.45: chip(c, "HUELE RARO", 700, 420, lt-d*0.45, ic_warn, size=36, bg=C['red'], fg=C['paper'])
    if lt > d*0.75: chip(c, "«LO APROVECHO»", 330, 860, lt-d*0.75, size=30, bg=C['paper'])
    post(c, t, 0.55)

def c18_11(c, lt, d, t):  # REGLA 3: 2 h por encima de 4 ºC → basura
    wall_room(c, C['wall2'], 1300, 0.5)
    # termómetro
    tx, ty = 230, 1240; lvl = clamp(lt/(d*0.6))
    box(c, tx-26, ty-480, 52, 480, C['paper'], 26); circle(c, tx, ty+10, 46); fs(c, C['red'], 4)
    box(c, tx-12, ty-60-360*lvl, 24, 60+360*lvl, C['red'], 12, 0)
    c.set_source_rgb(*OUT); c.set_line_width(4); c.move_to(tx+30, ty-200); c.line_to(tx+80, ty-200); c.stroke()
    txt(c, "4 ºC", tx+150, ty-188, 38, C['ink'], "Anton")
    # cubo de basura
    k = ease(P(lt, d, 0.5, 0.85))
    box(c, 700, 1100, 230, 220, C['steel2'], 14); box(c, 680, 1070, 270, 40, C['steel'], 10)
    box(c, lerp(560, 760, k), lerp(900, 1050, k), 170, 80, hexc('#E9C9A0'), 28)
    if lt > d*0.05: rule_card(c, 3, "+2 HORAS A MÁS DE 4 ºC:", "A LA BASURA", W/2, 480, lt-d*0.05, ic_warn)
    if lt > d*0.55: chip(c, "2 HORAS O MÁS", 560, 1660, lt-d*0.55, ic_clock, size=36, bg=C['red'], fg=C['paper'])
    post(c, t, 0.55)

def c18_12(c, lt, d, t):  # la puerta del 8º entreabierta, una lámpara encendida… Marta vive sola
    k = ease(P(lt, d))
    c.save(); z = 1+0.3*k; c.translate(W/2, 950); c.scale(z, z); c.translate(-W/2, -950)
    wall_room(c, C['wall2'], 1320, 0.92)
    door(c, 560, 1320, 300, 720, open_=0.25+0.1*P(lt, d, 0.3, 0.6), light=0.55+0.1*math.sin(t*3), night=0.9, t=t)
    box(c, 140, 520, 160, 70, C['paper'], 8); txt(c, "8º B", 220, 570, 40, C['ink'], "Anton")
    c.restore()
    marta(c, 150, 1700, 560, "stand", t, face=1, expr="shock" if lt > d*0.55 else "worried", lit=0.45)
    if lt > d*0.35: chip(c, "ALGUIEN ENCENDIÓ LA LÁMPARA", W/2, 420, lt-d*0.35, ic_warn, size=30, bg=C['red'], fg=C['paper'])
    if lt > d*0.75: chip(c, "MARTA VIVE SOLA", W/2, 1620, lt-d*0.75, size=36, bg=C['dark'], fg=C['paper'])
    post(c, t, 0.75, 0.09)

SCENES = {"C18": [c18_0, c18_1, c18_2, c18_3, c18_4, c18_5, c18_6, c18_7, c18_8, c18_9, c18_10, c18_11, c18_12]}
BOOMS = {"C18": [0, 12]}
CALM = {"C18"}
