"""Serie ZOMBI (apocalipsis) — estilo cine con gancho 3D (clip IA en la escena 0). Episodio Z1: supermercado."""
from engine import *
from cine import *

FL = 1260
def P(lt, d, a=0.0, b=1.0): return clamp((lt/d-a)/(b-a)) if d > 0 else 1.0

PROD = [C['red2'], C['gold'], C['leaf'], C['water'], C['cream'], hexc("#B5838D"), hexc("#E9C46A")]

def shelf(c, x, top, w, rows=4, night=0.0, seed=1, gap=None):
    m = lambda cc: mix(cc, C['night1'], night)
    r = random.Random(seed); rh = (FL-top)/rows
    box(c, x, top, w, FL-top, m(C['steel2']), 4)
    for i in range(rows):
        y = top+(i+1)*rh
        box(c, x-6, y-14, w+12, 16, m(C['steel']), 3, 3)
        xx = x+10
        while xx < x+w-40:
            pw = r.uniform(34, 60); ph = r.uniform(rh*0.4, rh*0.75)
            if gap is None or not (gap[0] < xx < gap[1] and i == gap[2]):
                rrect(c, xx, y-14-ph, pw, ph, 5); fs(c, m(r.choice(PROD)), 3)
            xx += pw+6

def store_bg(c, t, night=0.6, emergency=0.0):
    wall_room(c, C['wall2'], FL, night)
    c.rectangle(0, FL, W, H-FL); c.set_source_rgb(*mix(C['tile'], C['night1'], night*0.8)); c.fill()
    for i in range(12):
        c.set_source_rgba(0, 0, 0, 0.08); c.set_line_width(3); c.move_to(i*100-200, FL); c.line_to(i*160-500, H); c.stroke()
    if emergency > 0:
        a = emergency*(0.55+0.25*math.sin(t*2.5))
        g = cairo.RadialGradient(W/2, 300, 20, W/2, 300, 1100); g.add_color_stop_rgba(0, 0.9, 0.15, 0.1, 0.35*a); g.add_color_stop_rgba(1, 0.5, 0.05, 0.05, 0)
        c.set_source(g); c.paint()
        rrect(c, W/2-60, 290, 120, 30, 10); c.set_source_rgba(1, 0.2, 0.15, a); c.fill()

def shambler(c, x, base, h, t, ph=0.0, a=1.0):
    """silueta genérica tambaleante (sin rasgos de ningún personaje conocido)"""
    u = h/520; sw = math.sin(t*2.2+ph)
    c.save(); c.translate(x, base); c.rotate(0.08*sw+0.12); c.set_source_rgba(0.05, 0.06, 0.07, a)
    for dx, k in ((-24, 1), (24, -1)):
        c.save(); c.translate(dx*u, -250*u); c.rotate(0.18*sw*k); rrect(c, -14*u, 0, 28*u, 250*u, 12*u); c.fill(); c.restore()
    c.new_path(); c.move_to(-56*u, -230*u); c.curve_to(-68*u, -330*u, -58*u, -420*u, -36*u, -440*u); c.line_to(42*u, -436*u)
    c.curve_to(62*u, -410*u, 68*u, -330*u, 56*u, -230*u); c.close_path(); c.fill()
    c.save(); c.translate(30*u, -420*u); c.rotate(-1.2+0.1*sw); rrect(c, 0, -12*u, 200*u, 24*u, 12*u); c.fill(); c.restore()
    c.save(); c.translate(-20*u, -415*u); c.rotate(-1.35-0.1*sw); rrect(c, 0, -12*u, 190*u, 24*u, 12*u); c.fill(); c.restore()
    circle(c, 14*u, -490*u, 52*u); c.fill(); c.restore()

def storefront(c, t, night=0.85, shutter=0.0, lights=1.0, crowd=0.0):
    """vista desde dentro: cristalera a la calle, persiana metálica que baja"""
    store_bg(c, t, night)
    gx, gy, gw, gh = 90, 330, 900, 820
    c.rectangle(gx, gy, gw, gh); c.set_source_rgb(*C['night2']); c.fill()
    c.save(); c.rectangle(gx, gy, gw, gh); c.clip()
    r = random.Random(3)
    for i in range(6):
        bx = gx+i*170-20; bh = r.uniform(300, 600)
        c.rectangle(bx, gy+gh-bh, 150, bh); c.set_source_rgb(*mix(C['night1'], C['dusk1'], 0.5)); c.fill()
    c.rectangle(gx, gy+gh-120, gw, 120); c.set_source_rgb(*C['night1']); c.fill()
    for i in range(int(2+crowd*6)):
        shambler(c, gx+120+i*130+math.sin(t*0.3+i)*30, gy+gh-20, 300+(i % 3)*30, t, i, 0.95)
    c.restore()
    if lights > 0:
        c.set_source_rgba(1, 0.95, 0.8, 0.18*lights); c.rectangle(gx, gy, gw, gh); c.fill()
    for xx in (gx+gw/3, gx+2*gw/3):
        c.set_source_rgb(*C['steel2']); c.set_line_width(14); c.move_to(xx, gy); c.line_to(xx, gy+gh); c.stroke()
    rrect(c, gx-14, gy-14, gw+28, gh+28, 4); c.set_source_rgb(*C['steel2']); c.set_line_width(16); c.stroke()
    if shutter > 0:
        sh = gh*shutter
        c.rectangle(gx, gy, gw, sh); c.set_source_rgb(*mix(C['steel'], C['night1'], 0.35)); c.fill()
        c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(4)
        for yy in range(int(gy+30), int(gy+sh), 34): c.move_to(gx, yy); c.line_to(gx+gw, yy)
        c.stroke(); box(c, gx+gw/2-60, gy+sh-28, 120, 24, C['dark2'], 6, 3)
    box(c, gx-30, gy-90, gw+60, 70, C['dark'], 6)

def jug(c, x, base, s=1.0, k=1.0):
    if k <= 0: return
    c.save(); c.translate(x, base); c.scale(s*min(1, k*1.4), s*min(1, k*1.4))
    rrect(c, -50, -150, 100, 150, 18); fs(c, tint(C['water'], 0.45), 3)
    rrect(c, -46, -100, 92, 96, 14); fs(c, C['water'], 0, 0.8)
    box(c, -16, -172, 32, 24, C['teal'], 5, 3); c.set_source_rgb(*OUT); c.set_line_width(5)
    c.arc(26, -150, 18, -math.pi/2, math.pi/2); c.stroke()
    c.restore()

def cart(c, x, base, s=1.0, t=0, lit=1.0):
    c.save(); c.translate(x, base); c.scale(s, s)
    col = mix(C['steel'], C['night1'], 1-lit)
    c.set_source_rgb(*col); c.set_line_width(8)
    c.move_to(-160, -260); c.line_to(140, -260); c.line_to(110, -90); c.line_to(-130, -90); c.close_path(); c.stroke()
    for i in range(1, 6): c.move_to(-160+i*50, -260); c.line_to(-130+i*40, -90); c.stroke()
    c.move_to(140, -260); c.line_to(200, -320); c.stroke(); c.move_to(-130, -90); c.line_to(-140, -30); c.line_to(120, -30); c.stroke()
    for wx in (-120, 100):
        circle(c, wx, -14, 16); fs(c, mix(C['dark'], C['night1'], 1-lit), 3)
        c.set_source_rgb(*C['paper']); c.set_line_width(3); a = t*8
        c.move_to(wx, -14); c.line_to(wx+math.cos(a)*12, -14+math.sin(a)*12); c.stroke()
    c.restore()

# ---------------- escenas Z1 ----------------
def z1_0(c, lt, d, t):   # gancho: Teo escondido tras la estantería, siluetas tras el cristal
    k = ease(clamp(lt/d))
    c.save(); z = 1+0.08*k; c.translate(W/2, 800); c.scale(z, z); c.translate(-W/2, -800)
    storefront(c, t, 0.9, 0, 0.15, crowd=0.4+0.6*k)
    c.restore()
    g = cairo.RadialGradient(W/2, 300, 30, W/2, 300, 1200); g.add_color_stop_rgba(0, 0.9, 0.1, 0.08, 0.25+0.1*math.sin(t*2.5)); g.add_color_stop_rgba(1, 0.4, 0.05, 0.05, 0)
    c.set_source(g); c.paint()
    shelf(c, -260, 380, 420, 4, 0.75, seed=9)
    teo(c, 250, FL+40, 600, "listen", t, face=1, expr="shock", look=(0.8, 0), lit=0.55)
    post(c, t, 0.65, 0.08)

def z1_1(c, lt, d, t):   # el mejor sitio… si no haces ruido
    store_bg(c, t, 0.35)
    for i, x in enumerate((-120, 700)): shelf(c, x, 420, 500, 4, 0.35, seed=i)
    teo(c, 470, FL+40, 560, "stand", t, expr="focus", look=(0.2, -0.3), lit=0.9)
    chip(c, "EL MEJOR SITIO", W/2, 360, lt-0.3, ic_check)
    if lt > d*0.55:
        k = P(lt, d, 0.55, 0.75)
        c.save(); c.translate(W/2, 520); c.scale(back(k*1.2), back(k*1.2)); circle(c, 0, 0, 80); fs(c, C['red'], 5)
        c.set_source_rgb(*C['paper']); c.set_line_width(12); c.move_to(-40, 0); c.line_to(40, 0); c.stroke(); c.restore()
        chip(c, "SIN RUIDO", W/2, 640, lt-d*0.65, ic_warn)
    post(c, t, 0.5)

def z1_2(c, lt, d, t):   # 22:00, reponiendo; gritos fuera
    store_bg(c, t, 0.45)
    shelf(c, 520, 420, 560, 4, 0.45, seed=4, gap=(700, 900, 2))
    k = P(lt, d, 0.1, 0.7)
    teo(c, 380, FL+40, 560, "carry" if lt < d*0.6 else "listen", t, expr="focus" if lt < d*0.6 else "shock", look=(-0.6 if lt > d*0.6 else 0.4, 0), lit=0.85)
    box(c, 420, 920, 120, 90, C['wood'], 6, 3) if lt < d*0.6 else None
    time_card(c, "BROTE · DÍA 1", "22:00", "SUPERMERCADO DE BARRIO", W/2, 360, lt-0.15)
    if lt > d*0.6:
        for i in range(3):
            kk = pop(lt-d*0.6-i*0.15)
            if kk > 0:
                c.save(); c.translate(120+i*40, 760-i*80); c.scale(kk, kk); txt(c, "!", 0, 0, 70, C['red'], "Anton"); c.restore()
    post(c, t, 0.55)

def z1_3(c, lt, d, t):   # baja la persiana y apaga escaparate
    sh = ease(P(lt, d, 0.15, 0.75))
    storefront(c, t, 0.85, sh, lights=1-P(lt, d, 0.6, 0.8), crowd=0.2)
    teo(c, 300, FL+40, 520, "reach", t, face=1, expr="focus", lit=0.6)
    if lt > d*0.4: rule_card(c, 1, "OSCURIDAD", "Y SILENCIO", W/2, 520, lt-d*0.4, ic_bolt)
    post(c, t, 0.6)

def z1_4(c, lt, d, t):   # desde la calle parece vacía
    grad_bg(c, C['night1'], C['night2'])
    c.rectangle(0, 1100, W, H); c.set_source_rgb(*hexc("#1A1E26")); c.fill()
    box(c, 140, 420, 800, 680, hexc("#2C303A"), 4)
    c.rectangle(200, 520, 680, 520); c.set_source_rgb(*mix(C['steel'], C['night1'], 0.6)); c.fill()
    c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(4)
    for yy in range(540, 1040, 30): c.move_to(200, yy); c.line_to(880, yy)
    c.stroke()
    box(c, 160, 440, 760, 60, hexc("#3A3F4B"), 4)
    for i in range(4):
        x = (lerp(-200, 1300, ((t*0.05+i*0.27) % 1)))
        shambler(c, x, 1240, 380, t, i, 0.97)
    chip(c, "TIENDA «VACÍA»", W/2, 360, lt-0.3, ic_check)
    post(c, t, 0.65)

def z1_5(c, lt, d, t):   # el agua, no la comida
    store_bg(c, t, 0.55, emergency=1.0)
    shelf(c, 40, 460, 420, 4, 0.55, seed=7)
    box(c, 560, 700, 460, 560, mix(C['steel2'], C['night1'], 0.4), 4)
    for i in range(6):
        jug(c, 620+(i % 3)*140, 990+(i//3)*250, 0.9, pop(lt-0.2-i*0.15))
    teo(c, 420, FL+40, 540, "think", t, expr="focus", lit=0.7)
    if lt > d*0.45: rule_card(c, 2, "PRIMERO", "EL AGUA", W/2, 520, lt-d*0.45, ic_drop)
    post(c, t, 0.6)

def z1_6(c, lt, d, t):   # 3 días sin agua / semanas sin comida
    grad_bg(c, hexc("#20283A"), hexc("#11151F"))
    stat_card(c, "SIN BEBER", "≈ 3", "DÍAS", W/2, 520, lt-0.2, ic_drop)
    chip(c, "SIN COMER: SEMANAS", W/2, 800, lt-d*0.45, ic_clock, size=42)
    k = P(lt, d, 0.1, 0.9)
    c.set_source_rgba(*C['red'], 0.9); c.set_line_width(14); c.move_to(W/2-300, 1020); c.line_to(W/2-300+600*min(1, k*1.6)*0.25, 1020); c.stroke()
    c.set_source_rgba(*C['leaf'], 0.9); c.move_to(W/2-300, 1060); c.line_to(W/2-300+600*k, 1060); c.stroke()
    txt(c, "AGUA", W/2-320, 1030, 26, C['paper'], align="right"); txt(c, "COMIDA", W/2-320, 1070, 26, C['paper'], align="right")
    post(c, t, 0.4)

def z1_7(c, lt, d, t):   # 4 L por persona y día
    store_bg(c, t, 0.55, emergency=0.6)
    for i in range(4):
        jug(c, 230+i*200, 1150, 1.25, pop(lt-0.2-i*0.12))
    stat_card(c, "POR PERSONA Y DÍA", "≈ 4", "LITROS", W/2, 520, lt-0.5, ic_drop)
    chip(c, "BEBER + ASEARSE", W/2, 760, lt-d*0.55, ic_check)
    post(c, t, 0.55)

def z1_8(c, lt, d, t):   # cuenta las garrafas: meses… si está solo
    store_bg(c, t, 0.6, emergency=0.8)
    for row in range(3):
        for i in range(6): jug(c, 470+i*95, 900+row*150, 0.75, 1.0)
    teo(c, 260, FL+40, 520, "think", t, expr="focus" if lt < d*0.7 else "worried", look=(0.6, 0.2), lit=0.7)
    n = int(18*ease(P(lt, d, 0.05, 0.5)))
    chip(c, f"{n} GARRAFAS", 700, 380, lt-0.1, ic_drop)
    if lt > d*0.6: chip(c, "SI ESTÁ SOLO…", 700, 500, lt-d*0.6, ic_warn, bg=C['gold'])
    post(c, t, 0.6)

def z1_9(c, lt, d, t):   # un carrito rueda en congelados
    store_bg(c, t, 0.85, emergency=1.0)
    for i in range(3):
        box(c, 560+i*170, 520, 150, 740, mix(hexc("#8FB8C9"), C['night1'], 0.6), 6)
        c.set_source_rgba(0.75, 0.9, 1, 0.15); rrect(c, 570+i*170, 540, 130, 700, 4); c.fill()
    x = lerp(1250, 760, ease(P(lt, d, 0.2, 1.0)))
    cart(c, x, FL+20, 1.0, t, lit=0.5)
    teo(c, 240, FL+40, 520, "listen", t, face=1, expr="shock", look=(0.8, 0), lit=0.55)
    chip(c, "CONGELADOS", 800, 420, lt-0.2, size=28)
    post(c, t, 0.7, 0.09)

def z1_10(c, lt, d, t):  # alguien más se había quedado dentro
    store_bg(c, t, 0.95, emergency=0.7)
    shelf(c, -60, 460, 380, 4, 0.9, seed=2); shelf(c, 760, 460, 380, 4, 0.9, seed=3)
    k = ease(P(lt, d, 0.0, 0.8))
    silhouette(c, W/2, lerp(1120, 1180, k), lerp(380, 560, k), t)
    cart(c, W/2+40, lerp(1120, 1200, k)+10, lerp(0.6, 0.85, k), t, lit=0.3)
    teo(c, 160, FL+60, 560, "stand", t, expr="shock", look=(0.8, 0), lit=0.4, shadow=False)
    post(c, t, 0.75, 0.1)

SCENES = {"Z1": [z1_0, z1_1, z1_2, z1_3, z1_4, z1_5, z1_6, z1_7, z1_8, z1_9, z1_10]}
BOOMS = {"Z1": [5, 10]}
CALM = {"Z1"}
