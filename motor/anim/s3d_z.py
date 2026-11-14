"""3D · «Los Últimos del Súper» (serie ZOMBI). Decorados + poses por escena. Se ejecuta dentro de render3d.py (bpy)."""
import math, random
from m3d import *

TEO = dict(skin="#F0D2B4", skin2="#D9B392", hair="#2A2220", top="#2F6F7A", top2="#24565F", legs="#5A5F6B", shoe="#F4EEE3", hood=True)
ZOMB = [dict(skin="#8FA08A", skin2="#7C8C77", hair="#2E2B28", top=c, top2=c, legs="#3A3D44", shoe="#2B2A2F", hair_style=hs)
        for c, hs in (("#6E5A4E", "buzz"), ("#4F5D6E", "messy"), ("#7A4E4E", "buzz"), ("#5E6650", "bun"), ("#55505E", "buzz"))]
PROD = ["#C8372D", "#E2A63B", "#6F8F5A", "#6FA8C7", "#F4EEE3", "#B5838D", "#E9C46A", "#2F6F7A"]

def shelf_unit(name, x, y, length=4.0, rows=4, seed=1, rot=0.0, empty_gap=None):
    g = group(name, None, (x, y, 0)); g.rotation_euler = (0, 0, rot)
    box(name+"_back", (0, 0, 1.0), (length, 0.08, 2.0), "#6F7781", 0.01, g)
    box(name+"_base", (0, -0.25, 0.08), (length, 0.6, 0.16), "#474B55", 0.02, g)
    r = random.Random(seed)
    for i in range(rows):
        z = 0.2+i*0.48
        box(f"{name}_s{i}", (0, -0.25, z), (length, 0.55, 0.04), "#9AA3AD", 0.01, g)
        xx = -length/2+0.08
        while xx < length/2-0.15:
            w = r.uniform(0.14, 0.26); h = r.uniform(0.16, 0.36)
            if not (empty_gap and empty_gap[0] < xx < empty_gap[1] and i == empty_gap[2]):
                box(f"{name}_p{i}_{xx:.2f}", (xx+w/2, -0.25+r.uniform(-0.05, 0.05), z+0.02+h/2), (w, 0.3, h), r.choice(PROD), 0.015, g)
            xx += w+0.03
    return g

def jug(name, loc, parent=None, s=1.0):
    g = group(name, parent, loc)
    cyl(name+"_b", (0, 0, 0.17*s), 0.12*s, 0.34*s, "#8EC1DA", g)
    cyl(name+"_c", (0, 0, 0.37*s), 0.04*s, 0.06*s, "#2F6F7A", g)
    return g

def cart(name, loc):
    g = group(name, None, loc)
    for (x, y, z, sx, sy, sz) in ((0, 0, 0.55, 0.55, 0.85, 0.03), (0, 0.42, 0.75, 0.55, 0.03, 0.42), (0, -0.42, 0.75, 0.55, 0.03, 0.42),
                                   (0.27, 0, 0.75, 0.03, 0.85, 0.42), (-0.27, 0, 0.75, 0.03, 0.85, 0.42), (0, 0.55, 1.0, 0.6, 0.05, 0.05)):
        box(f"{name}_{x}{y}{z}", (x, y, z), (sx, sy, sz), "#AEB6BF", 0.008, g)
    for (x, y) in ((0.22, 0.35), (-0.22, 0.35), (0.22, -0.35), (-0.22, -0.35)):
        cyl(f"{name}_w{x}{y}", (x, y, 0.07), 0.07, 0.05, "#26252A", g, 12, (0, math.pi/2, 0))
        box(f"{name}_l{x}{y}", (x, y, 0.32), (0.03, 0.03, 0.46), "#AEB6BF", 0.005, g)
    return g

def build():
    W = {}
    reset((540, 960), 15); world_color("#1C2230")
    # --- interior del súper ---
    st = group("store"); W["store"] = st
    plane("floor", (0, 4, 0), (14, 20), "#CFC8BC", parent=st)
    for i in range(-6, 7):
        box(f"tile{i}", (i*1.0, 4, 0.001), (0.02, 20, 0.002), "#B9B2A6", 0, st)
    box("backwall", (0, 12, 2), (14, 0.2, 4), "#D9C7AA", 0.0, st)
    box("ceilbar", (0, 4, 3.6), (14, 20, 0.1), "#4A5060", 0.0, st)
    for i in range(5): box(f"lightp{i}", (0, -1+i*2.6, 3.52), (0.5, 1.6, 0.04), "#F2F0E6", 0.0, st)
    for i, x in enumerate((-2.6, 2.6)):
        s1 = shelf_unit(f"sh{i}", x, 4, 7.0, 4, i+1, math.radians(90 if x < 0 else -90)); s1.parent = st
    s3 = shelf_unit("sh_end", 0, 9.5, 4.0, 4, 7); s3.parent = st
    # pasillo de agua: estante con garrafas
    wq = group("waterrack", st, (1.7, 2.0, 0)); W["waterrack"] = wq
    box("wr_base", (0, 0, 0.6), (1.2, 0.6, 1.2), "#6F7781", 0.02, wq)
    W["jugs_rack"] = [jug(f"jr{i}", (-0.4+(i % 3)*0.4, 0, 1.2+0.0), wq, 0.9) for i in range(3)]
    # escaparate (frente de la tienda, en y=-3)
    fr = group("front", st, (0, -3, 0)); W["front"] = fr
    box("fr_top", (0, 0, 3.0), (8, 0.25, 1.2), "#2B2A2F", 0.02, fr)
    for x in (-4, -1.35, 1.35, 4): box(f"fr_post{x}", (x, 0, 1.3), (0.18, 0.25, 2.6), "#9AA3AD", 0.01, fr)
    W["shutter"] = box("shutter", (0, 0.1, 1.3), (8, 0.06, 2.6), "#7E868F", 0.0, fr)
    # calle (detrás del escaparate)
    street = group("street", None, (0, -9, 0)); W["street"] = street
    plane("road", (0, 0, 0.0), (30, 12), "#2A2E36", parent=street)
    for i in range(5):
        box(f"bld{i}", (-9+i*4.5, -5, 3), (4, 3, 6+i % 3*1.5), ["#3B4150", "#454B5A", "#353A47"][i % 3], 0.02, street)
    box("lamp", (3, -1, 2.2), (0.12, 0.12, 4.4), "#3A3940", 0.01, street)
    sphere("lampbulb", (3, -0.8, 4.4), 0.18, "#FFE9A8", (1, 1, 1), street)
    # zombis
    W["zs"] = []
    for i, L in enumerate(ZOMB):
        z = Person(f"z{i}", L, 0.98+0.04*(i % 2)); W["zs"].append(z)
    # congelados
    fz = group("freezers", None, (0, 20, 0)); W["freezers"] = fz
    plane("fz_floor", (0, 0, 0), (12, 16), "#BFC6CC", parent=fz)
    for i in range(4):
        box(f"fz{i}", (2.4, -4+i*2.1, 1.1), (1.0, 2.0, 2.2), "#9FC3D3", 0.03, fz)
        box(f"fzd{i}", (1.88, -4+i*2.1, 1.15), (0.04, 1.8, 1.9), "#D7ECF5", 0.01, fz)
        box(f"fzl{i}", (-2.4, -4+i*2.1, 1.1), (1.0, 2.0, 2.2), "#9FC3D3", 0.03, fz)
    box("fz_back", (0, 5, 2), (8, 0.2, 4), "#3A4250", 0, fz)
    W["cart"] = cart("cart", (0, 22, 0))
    W["stranger"] = Person("stranger", dict(skin="#3A3436", hair="#141216", top="#1E1D22", top2="#1E1D22", legs="#1E1D22", shoe="#141216", hair_style="bun"))
    # pedestal (escenas de datos)
    pd = group("pedestal", None, (0, 40, 0)); W["pedestal"] = pd
    plane("pd_floor", (0, 0, 0), (12, 12), "#2C3442", parent=pd)
    cyl("pd_top", (0, 0, 0.4), 0.9, 0.8, "#3E4757", pd, 32)
    W["jug_big"] = jug("jbig", (0, 0, 0.8), pd, 1.6)
    W["jug_row"] = [jug(f"jrow{i}", (-1.2+i*0.8, -2.2, 0.0), pd, 1.3) for i in range(4)]
    W["jug_stack"] = [jug(f"jst{i}", (-0.4+(i % 6)*0.32, 2.6+(i//6)*0.3, 0.0), pd, 0.85) for i in range(18)]
    W["teo"] = Person("teo", TEO)
    camera(32)
    return W

def hide_all(W):
    for k in ("store", "street", "freezers", "pedestal", "cart"): show(W[k], False)
    for z in W["zs"]: z.show(False)
    W["stranger"].show(False); W["teo"].show(True)

def zombies_outside(W, t, n=5, y=-6.0, spread=1.0, walk=True):
    for i, z in enumerate(W["zs"]):
        if i >= n: z.show(False); continue
        z.show(True)
        x = (-3.2+i*1.6*spread + (t*0.25 if walk else 0) + i*0.37) % 9 - 4.5
        z.place(x, y-(i % 2)*0.8, 180 if i % 2 else 160)
        z.pose("point", t+i, walk=t*0.45+i*0.3 if walk else 0, expr="neutral")
        z.sh[-1].rotation_euler = (-1.4, 0, -0.05); z.sh[1].rotation_euler = (-1.3, 0, 0.05)
        z.hips.rotation_euler = (0.12, 0, math.sin(t*1.3+i)*0.08)
        z.head.rotation_euler = (0.25, 0, math.sin(t*0.9+i)*0.3)

# ---------------- escenas (lt = tiempo local, d = duración, t = tiempo global) ----------------
def z1_0(W, lt, d, t):    # gancho: Teo escondido tras la estantería, zombis tras el cristal
    hide_all(W); show(W["store"]); show(W["street"]); W["shutter"].hide_render = True; world_color("#0E1320")
    teo = W["teo"]; teo.face_to(-1.25, 0.9, 0.3, -4); teo.pose("hide", t, expr="shock")
    zombies_outside(W, t)
    k = ease(lt/d)
    look(lerpv((-1.6, 4.2, 2.05), (-1.5, 3.4, 1.9), k), (-0.2, -4.5, 1.2), 26)

def z1_1(W, lt, d, t):    # el mejor sitio… si no haces ruido
    hide_all(W); show(W["store"]); show(W["street"]); W["shutter"].hide_render = True; world_color("#202634")
    zombies_outside(W, t, 3, -7.5)
    a = math.radians(-25+35*ease(lt/d)); cx, cy = math.sin(a)*4.2, 3.6-math.cos(a)*4.2
    teo = W["teo"]; teo.face_to(0, 3.6, cx, cy); teo.pose("stand" if lt < d*0.55 else "listen", t, expr="focus", look=(0.0, 0))
    look((cx, cy, 1.5), (0, 3.6, 1.05), 28)

def z1_2(W, lt, d, t):    # 22:00 reponiendo, gritos fuera
    hide_all(W); show(W["store"]); W["shutter"].hide_render = True; world_color("#262C3A")
    teo = W["teo"]
    if lt < d*0.55:
        teo.face_to(-1.6, 5.2, -2.6, 5.4); teo.pose("carry", t, expr="neutral")
    else:
        k = ease((lt-d*0.55)/0.6); teo.place(-1.6, 5.2, lerp(-90, 10, k)); teo.pose("listen", t, expr="shock")
    look((1.3, 2.6, 1.55), (-1.6, 5.3, 1.15), 32)

def z1_3(W, lt, d, t):    # baja la persiana y apaga el escaparate
    hide_all(W); show(W["store"]); show(W["street"]); world_color("#141A26")
    k = ease(clamp((lt/d-0.15)/0.6))
    sh = W["shutter"]; sh.hide_render = False; sh.scale = (1, 1, max(0.02, k)); sh.location.z = 2.6-1.3*k
    zombies_outside(W, t, 4, -6.5)
    teo = W["teo"]; teo.face_to(0.4, -2.2, 0.4, -4); teo.pose("alarm" if lt < d*0.75 else "stand", t, expr="focus")
    look((-1.4, 2.4, 1.8), (0.2, -3.2, 1.5), 28)

def z1_4(W, lt, d, t):    # desde la calle: tienda cerrada y en silencio
    hide_all(W); show(W["store"]); show(W["street"]); world_color("#0B0F18")
    sh = W["shutter"]; sh.hide_render = False; sh.scale = (1, 1, 1); sh.location.z = 1.3
    W["teo"].show(False)
    for i, z in enumerate(W["zs"]):
        z.show(True); x = ((i*2.1+t*0.35) % 11)-5.5; y = -5.2-(i % 3)*0.9
        z.place(x, y, 90); z.pose("stand", t+i, walk=t*0.45+i*0.3)
        z.sh[-1].rotation_euler = (-1.4, 0, -0.05); z.sh[1].rotation_euler = (-1.3, 0, 0.05); z.head.rotation_euler = (0.25, 0, math.sin(t+i)*0.3)
    k = ease(lt/d)
    look(lerpv((-2.4, -12.5, 2.5), (-1.2, -11.0, 2.1), k), (0, -3, 1.6), 30)

def z1_5(W, lt, d, t):    # el agua, no la comida
    hide_all(W); show(W["store"]); W["shutter"].hide_render = False; world_color("#1A1F2B")
    teo = W["teo"]; teo.face_to(0.5, 1.0, 1.7, 2.0); teo.pose("think", t, expr="focus")
    look((1.0, -2.6, 1.7), (1.1, 1.5, 1.05), 26)

def z1_6(W, lt, d, t):    # 3 días sin beber / semanas sin comer
    hide_all(W); W["teo"].show(False); show(W["pedestal"]); world_color("#141A26")
    for j in W["jug_row"] + W["jug_stack"]: show(j, False)
    show(W["jug_big"]); W["jug_big"].rotation_euler = (0, 0, t*0.6)
    a = t*0.25; look((math.sin(a)*3.8, 40-math.cos(a)*3.8, 2.3), (0, 40, 1.3), 34)

def z1_7(W, lt, d, t):    # 4 L por persona y día
    hide_all(W); W["teo"].show(False); show(W["pedestal"]); world_color("#141A26")
    show(W["jug_big"], False)
    for j in W["jug_stack"]: show(j, False)
    for i, j in enumerate(W["jug_row"]):
        k = clamp((lt-0.3-i*0.25)/0.35); show(j, k > 0); s = max(0.01, ease(k)); j.scale = (s, s, s)
    look((0, 33.6, 1.6), (0, 37.8, 0.45), 30)

def z1_8(W, lt, d, t):    # cuenta garrafas: meses… si está solo
    hide_all(W); show(W["pedestal"]); world_color("#141A26")
    show(W["jug_big"], False)
    for j in W["jug_row"]: show(j, False)
    n = int(18*ease(clamp(lt/(d*0.5))))
    for i, j in enumerate(W["jug_stack"]): show(j, i < n)
    teo = W["teo"]; teo.face_to(-1.4, 42.2, 1.0, 43.2); teo.pose("think" if lt < d*0.65 else "stand", t, expr="focus" if lt < d*0.65 else "worried")
    look((2.5, 38.2, 1.9), (-0.2, 42.6, 0.9), 20)

def z1_9(W, lt, d, t):    # un carrito rueda en congelados
    hide_all(W); show(W["freezers"]); show(W["cart"]); world_color("#0B0F18")
    c = W["cart"]; c.location = (0.3, lerp(24.0, 20.8, ease(lt/d)), 0); c.rotation_euler = (0, 0, math.radians(8))
    teo = W["teo"]; teo.face_to(-0.7, 17.0, 0.3, 22); teo.pose("listen", t, expr="shock")
    look((-0.2, 14.2, 1.8), (0.3, 22.0, 0.9), 24)

def z1_10(W, lt, d, t):   # alguien más se había quedado dentro
    hide_all(W); show(W["freezers"]); show(W["cart"]); world_color("#080B12")
    c = W["cart"]; c.location = (0.8, 20.8, 0)
    s = W["stranger"]; s.show(True); s.face_to(0.8, 21.9, -1.0, 17.2); s.pose("stand", t)
    teo = W["teo"]; teo.face_to(-1.0, 17.2, 0.8, 21.9); teo.pose("stand", t, expr="shock")
    k = ease(lt/d)
    look(lerpv((-1.5, 13.4, 2.0), (-1.4, 14.2, 1.95), k), lerpv((0.3, 21.0, 1.2), (0.6, 21.6, 1.3), k), lerp(26, 32, k))

SCENES3D = {"Z1": [z1_0, z1_1, z1_2, z1_3, z1_4, z1_5, z1_6, z1_7, z1_8, z1_9, z1_10]}
