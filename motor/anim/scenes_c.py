"""Estilo «cine» — serie APAGÓN (protagonista: Teo). Episodio piloto C1."""
from engine import *
from cine import *
from cine import teo as _teo
def teo(*a, **k):
    k.setdefault('who', MARTA); return _teo(*a, **k)

FL = 1260   # suelo de interiores (contenido entre y=300 y y=1300)

def P(lt, d, a=0.0, b=1.0): return clamp((lt/d-a)/(b-a)) if d > 0 else 1.0

def facade(c, t, k_off, night=0.85, zoom=1.0):
    grad_bg(c, mix(C['dusk1'], C['night1'], 0.3), C['dusk2'])
    r = random.Random(7)
    # edificios lejanos
    for i in range(9):
        x = i*130-40; h = r.uniform(300, 700)
        c.rectangle(x, 1300-h, 120, h+700); c.set_source_rgb(*mix(C['night2'], C['dusk1'], 0.4)); c.fill()
        for wy in range(int(1300-h)+30, 1300, 50):
            for wx in range(x+15, x+110, 32):
                if r.random() < 0.5 and r.random() > k_off*1.15-0.1*(i % 3):
                    c.rectangle(wx, wy, 14, 18); c.set_source_rgba(1, 0.85, 0.5, 0.9); c.fill()
    # edificio protagonista (10 plantas)
    bx, bw, base, fh = 300, 480, 1420, 100
    c.rectangle(bx, base-10*fh, bw, 10*fh+500); c.set_source_rgb(*mix(C['wall2'], C['night1'], night*0.75)); c.fill()
    c.rectangle(bx-20, base-10*fh-30, bw+40, 34); c.set_source_rgb(*C['night1']); c.fill()
    for f in range(10):
        y = base-(f+1)*fh+22
        for j in range(4):
            x = bx+30+j*112
            off = k_off > (0.15+0.07*((f*4+j) % 9))
            c.rectangle(x, y, 80, 60)
            c.set_source_rgb(*(C['night1'] if off else (1, 0.85, 0.52))); c.fill()
            if f == 7 and j == 1:  # el 8º de Teo
                c.set_source_rgb(*C['gold']); c.set_line_width(5); rrect(c, x-10, y-10, 100, 80, 6); c.stroke()
    darken(c, 0.15)

def living(c, t, night=0.0, lamp=1.0, lights_out=0.0):
    wall_room(c, floor_y=FL, night=night)
    window_city(c, 560, 380, 420, 560, t, night=max(night, 0.75), lights_out=lights_out)
    ceiling_lamp(c, 300, 240, lamp)
    # sofá
    m = lambda cc: mix(cc, C['night1'], night*0.7)
    box(c, 40, 1020, 460, 120, m(C['red']), 30); box(c, 40, 1110, 460, 150, m(shade(C['red'], 0.12)), 20)
    box(c, 20, 1000, 70, 260, m(shade(C['red'], 0.2)), 26); box(c, 450, 1000, 70, 260, m(shade(C['red'], 0.2)), 26)

def hallway(c, t, night=0.6, ind_red=0.0):
    wall_room(c, C['wall2'], FL, night)
    m = lambda cc: mix(cc, C['night1'], night*0.6)
    box(c, 600, 420, 380, 840, m(C['steel2']), 6)
    box(c, 612, 440, 174, 820, m(C['steel']), 2, 3); box(c, 794, 440, 174, 820, m(C['steel']), 2, 3)
    box(c, 720, 340, 140, 60, C['dark'], 10, 3)
    txt(c, "8", 790, 386, 44, C['red'] if ind_red else C['gold'], "Anton")
    box(c, 1000, 760, 40, 90, m(C['steel']), 8, 3); circle(c, 1020, 790, 10); fs(c, C['red'] if ind_red and math.sin(t*6) > 0 else C['dark'], 2)
    # luz de emergencia
    c.set_source_rgba(0.3, 1, 0.5, 0.25); rrect(c, 120, 330, 160, 60, 10); c.fill()
    txt(c, "SALIDA", 200, 372, 30, (0.6, 1, 0.75))

# ---------------- escenas ----------------
def c1_0(c, lt, d, t):   # gancho: el edificio se apaga
    k = P(lt, d, 0.15, 0.85)
    c.save(); z = 1+0.18*ease(P(lt, d)); c.translate(W/2, 820); c.scale(z, z); c.translate(-W/2, -820)
    facade(c, t, k); c.restore()
    if lt > d*0.55: chip(c, "8º PISO", 760, 470, lt-d*0.55, ic_bolt, anchor=(600, 640))
    post(c, t, 0.55)

def c1_1(c, lt, d, t):   # el problema no es la oscuridad
    flick = 1.0 if lt < d*0.35 else (0.0 if lt > d*0.55 else (1.0 if math.sin(lt*40) > 0.2 else 0.0))
    nt = 0.15 if flick else 0.65
    living(c, t, night=nt, lamp=flick, lights_out=P(lt, d, 0.4, 0.9))
    teo(c, 420, FL+30, 560, "stand" if flick else "think", t, face=1, expr="neutral" if flick else "worried", look=(0.3, -0.6), lit=1-nt*0.5)
    if lt > d*0.6: chip(c, "NO ES LA OSCURIDAD", W/2, 400, lt-d*0.6, ic_warn)
    post(c, t, 0.5+0.15*(1-flick))

def c1_2(c, lt, d, t):   # 19:04, Teo solo en casa, móvil
    living(c, t, night=0.65, lamp=0, lights_out=1)
    # brillo del móvil en la cara
    g = cairo.RadialGradient(470, 860, 10, 470, 860, 260); g.add_color_stop_rgba(0, 0.75, 0.88, 1, 0.45); g.add_color_stop_rgba(1, 0.7, 0.85, 1, 0)
    teo(c, 400, FL+30, 560, "phone", t, expr="focus", look=(0.6, 0.6), lit=0.7)
    box(c, 452, 840, 34, 56, (0.8, 0.92, 1), 6, 3)
    c.set_source(g); c.paint()
    time_card(c, "APAGÓN", "DÍA 1", "19:04 · SIN COBERTURA", W/2, 360, lt-0.2)
    post(c, t, 0.6)

def c1_3(c, lt, d, t):   # impulso: el ascensor. Mala idea.
    hallway(c, t, 0.55, ind_red=lt > d*0.55)
    x = lerp(120, 470, ease(P(lt, d, 0, 0.5)))
    teo(c, x, FL+30, 540, "reach" if lt > d*0.5 else "stand", t, face=1, walk=0 if lt > d*0.5 else lt*1.6, expr="focus", lit=0.75)
    if lt > d*0.55: rule_card(c, 1, "NADA DE", "ASCENSORES", W/2, 520, lt-d*0.55)
    post(c, t, 0.55)

def c1_4(c, lt, d, t):   # 286 rescates en Madrid (28-A-2025)
    hallway(c, t, 0.7, ind_red=True)
    darken(c, 0.35)
    n = int(286*ease(P(lt, d, 0.1, 0.7)))
    c.save(); c.translate(W/2, 620)
    c.set_source_rgba(0, 0, 0, 0.3); rrect(c, -400+10, -230+14, 800, 460, 22); c.fill()
    rrect(c, -400, -230, 800, 460, 22); fs(c, C['paper'], 0)
    rrect(c, -260, -200, 520, 56, 28); fs(c, C['dark'], 0); txt(c, "MADRID · 28 ABRIL 2025", 0, -160, 30, C['paper'])
    txt(c, f"{n}", 0, 80, 210, C['red'], "Anton")
    txt(c, "RESCATES EN ASCENSORES", 0, 160, 40, C['ink'])
    c.restore()
    chip(c, "EN UN SOLO DÍA", W/2, 950, lt-d*0.7, ic_clock)
    post(c, t, 0.55)

def c1_5(c, lt, d, t):   # vuelve y abre el grifo
    wall_room(c, floor_y=FL, night=0.35)
    window_city(c, 600, 360, 360, 420, t, night=0.9, lights_out=1)
    light_shaft(c, ((600, 780), (960, 780)), ((380, FL), (1000, FL)), 0.12, (0.75, 0.85, 1))
    counter_kitchen(c, 900, night=0.35, sink_x=700)
    x = lerp(200, 520, ease(P(lt, d, 0, 0.45)))
    teo(c, x, FL+40, 560, "reach" if lt > d*0.45 else "stand", t, walk=0 if lt > d*0.45 else lt*1.6, expr="worried" if lt > d*0.7 else "focus", lit=0.8)
    if lt > d*0.55: water_stream(c, 704, 752, 892, t, drip=True)
    if lt > d*0.75: chip(c, "SOLO GOTEA", 760, 560, lt-d*0.75, ic_drop, anchor=(706, 760))
    post(c, t, 0.5)

def c1_6(c, lt, d, t):   # diagrama: bombas eléctricas
    grad_bg(c, hexc("#20283A"), hexc("#11151F"))
    pw = lt < d*0.35
    lvl = 1.0 if pw else lerp(1.0, 0.27, ease(P(lt, d, 0.35, 0.65)))
    building_section(c, 470, 1160, 10, 78, 520, t, 8, lvl, pw)
    chip(c, "BOMBA ELÉCTRICA", 330, 1270, lt-0.3, ic_bolt, size=30, anchor=(600, 1240))
    if not pw:
        c.set_source_rgba(1, 0.2, 0.15, 0.85); c.set_line_width(10); c.move_to(570, 1205); c.line_to(670, 1285); c.move_to(670, 1205); c.line_to(570, 1285); c.stroke()
    if lt > d*0.62: chip(c, "SIN LUZ: HASTA EL 2º-3º", 540, 330, lt-d*0.62, ic_drop, size=32)
    if lt > d*0.8: chip(c, "MARTA: 8º", 880, 590, lt-d*0.8, size=30, bg=C['gold'], anchor=(730, 620))
    post(c, t, 0.4)

def c1_7(c, lt, d, t):   # llena todo
    c.set_source_rgb(*C['wall2']); c.paint()
    tiles(c, 300, FL, C['tile'])
    c.rectangle(0, FL, W, H-FL); c.set_source_rgb(*C['floor2']); c.fill()
    darken(c, 0.25)
    bathtub(c, 640, FL+10, fill=0.15+0.7*P(lt, d, 0.05, 0.95), t=t)
    water_stream(c, 830, 975, 1080, t, 0.8)
    for i in range(4):
        bottle(c, 120+i*70, FL+20, 0.9, fill=clamp(P(lt, d, 0.3+i*0.12, 0.45+i*0.12)))
    pot(c, 230, FL-150, 0.9, 1.0 if lt > d*0.25 else 0)
    teo(c, 420, FL+40, 520, "carry", t, expr="focus", lit=0.85, shadow=False)
    for i, (s, x, y, a) in enumerate((("BAÑERA", 640, 760, (640, 1100)), ("OLLAS", 240, 480, (240, 1080)), ("BOTELLAS", 860, 480, (260, 1120)))):
        chip(c, s, x, y, lt-0.4-i*0.9, ic_drop, size=30, anchor=a)
    post(c, t, 0.5)

def c1_8(c, lt, d, t):   # nevera 4 h / congelador 48 h
    wall_room(c, floor_y=FL, night=0.5)
    fridge(c, 680, FL+10, night=0.5)
    teo(c, 330, FL+40, 540, "think", t, expr="focus", look=(0.6, -0.2), lit=0.7)
    hrs = 4*3600*(1-P(lt, d, 0.2, 1.0)*0.02)
    countdown(c, hrs/60, W/2, 360, lt-0.1, label="HORAS")
    stat_card(c, "NEVERA CERRADA", "≈ 4", "HORAS", 600, 560, lt-0.5, ic_clock)
    if lt > d*0.5: chip(c, "CONGELADOR LLENO: ≈ 48 H", 640, 1180, lt-d*0.5, ic_clock, size=30)
    post(c, t, 0.5)

def c1_9(c, lt, d, t):   # no la abre. Ni una vez.
    wall_room(c, floor_y=FL, night=0.55)
    fridge(c, 680, FL+10, night=0.55)
    pull = math.sin(P(lt, d, 0, 0.5)*math.pi)
    teo(c, 400+80*pull, FL+40, 540, "reach" if pull > 0.3 else "stand", t, expr="focus", lit=0.7)
    if lt > d*0.45: rule_card(c, 2, "NO ABRAS", "LA NEVERA", W/2, 470, lt-d*0.45, ic_clock)
    post(c, t, 0.55)

def c1_10(c, lt, d, t):  # sobre el papel, varios días
    living(c, t, night=0.85, lamp=0, lights_out=1)
    # vela
    fl = 0.9+0.1*math.sin(t*13)+0.05*math.sin(t*29)
    g = cairo.RadialGradient(620, 1110, 5, 620, 1110, 560*fl); g.add_color_stop_rgba(0, 1, 0.75, 0.4, 0.55); g.add_color_stop_rgba(1, 1, 0.7, 0.4, 0)
    c.set_source(g); c.paint()
    teo(c, 300, FL+30, 520, "sit", t, expr="neutral", look=(0.6, 0.2), lit=0.85)
    box(c, 590, 1140, 60, 120, C['cream'], 6, 3)
    c.new_path(); c.move_to(620, 1080-8*fl); c.curve_to(636, 1115, 632, 1135, 620, 1138); c.curve_to(608, 1135, 604, 1115, 620, 1080-8*fl); fs(c, C['gold'], 0)
    for i, (s, ic) in enumerate((("AGUA", ic_check), ("COMIDA", ic_check), ("LUZ", ic_check))):
        chip(c, s, 780, 420+i*110, lt-0.3-i*0.5, ic, size=32)
    post(c, t, 0.6)

def c1_11(c, lt, d, t):  # alguien llama a la puerta
    wall_room(c, C['wall2'], FL, 0.95)
    door(c, 620, FL, 300, 720, light=0.6+0.2*math.sin(t*3), night=0.95, knock=1.0 if lt > d*0.25 else 0, t=t)
    teo(c, 230, FL+30, 520, "listen" if lt > d*0.3 else "stand", t, face=1, expr="shock" if lt > d*0.3 else "neutral", look=(0.6, 0), lit=0.45)
    if lt > d*0.25: knock_marks(c, 640, 640, lt-d*0.25)
    # sombra de pies bajo la puerta
    if lt > d*0.55:
        a = P(lt, d, 0.55, 0.8)
        for dx in (-50, 40): c.rectangle(620+dx, FL+2, 40, 30); c.set_source_rgba(0, 0, 0, 0.7*a); c.fill()
    post(c, t, 0.7, 0.09)

SCENES = {"C1": [c1_0, c1_1, c1_2, c1_3, c1_4, c1_5, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11]}
BOOMS = {"C1": [3, 11]}
CALM = {"C1"}
