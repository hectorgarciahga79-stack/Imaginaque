"""Q25 · Mini historia «Nueve minutos» (3D de bloques, 78,19 s). Idea de Héctor: cada persona puede ver cuánto tiempo le queda de vida.
Protagonista original: Irene (chaqueta verde oliva, pelo negro largo). La mujer del autobús: Rosa. Contadores flotantes sobre las cabezas.
Decorados: autobús por dentro (origen), ciudad de world.City (y=200 desplazada), hospital (y=400), cielo de paracaidismo (y=600),
rocódromo (y=800), circuito de motos (y=1000)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, City, building, tree, tiles, planks, asphalt, stripes, text3d

FPS = 24
TOTAL = 78.19
IRENE = dict(skin="#E8BE96", hair="#141216", hair2="#1C1A1E", eye="#2A1A10", top="#7A8A3A", top2="#5E6E2A", stripe="#F4F1EA",
             legs="#2E3A52", legs2="#243046", shoe="#F4F1EA", shoe2="#C0302A", watch=False, hstyle="long")
ROSA = dict(skin="#C68E62", hair="#8A6A5A", hair2="#7A5A4A", eye="#2A1A10", top="#A84A6A", top2="#8A3A56", stripe="#F4F1EA",
            legs="#3A3A44", legs2="#2C2C34", shoe="#2A2A2E", shoe2="#2A2A2E", watch=False, hstyle="short")
CYAN = "#40E0FF"; RED = "#FF4040"

class Env:
    def talk(self, who, T): return 0.0

O_BUS = (0, 0, 0); O_HS = (0, 400, 0); O_SK = (0, 600, 0); O_RK = (0, 800, 0); O_MT = (0, 1000, 0)

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(25)
    # autobús
    W["bus"] = g = group("bus", O_BUS)
    B = Batch("bus_b", g, 1.0)
    B.add((0, 0, -0.05), (3.0, 12, 0.1), "#4A4A52"); B.add((0, 0, 2.6), (3.0, 12, 0.1), "#D8DCE0")
    for sx in (-1, 1):
        B.add((sx*1.5, 0, 0.5), (0.1, 12, 1.0), "#E8C030"); B.add((sx*1.5, 0, 2.4), (0.1, 12, 0.4), "#E8C030")
        for y in range(-5, 6, 2): B.add((sx*1.5, y, 1.6), (0.05, 1.6, 1.2), "#9FD0E8")
        for y in range(-4, 6, 2): B.add((sx*1.05, y, 0.45), (0.8, 0.8, 0.12), "#3A5AA0"); B.add((sx*1.05, y+0.38, 0.85), (0.8, 0.1, 0.8), "#3A5AA0")
    B.add((0.0, 0, 2.3), (0.05, 12, 0.05), "#C8C8D0")
    B.done()
    W["outside"] = [box(f"os{q}", (0, 0, 0), (0.2, 3.0, 2.5), mat(["#C8B8A8", "#9AA8B8", "#B8A898"][q % 3])) for q in range(12)]
    W["city"] = City()
    W["npcs"] = [Person(f"np{q}", npc_look(900+q), 1.0) for q in range(6)]
    W["truck"] = tr = group("truck", (0, 0, 0))
    T_ = Batch("truck_b", tr, 1.0)
    T_.add((0, 0, 2.0), (7.0, 2.6, 2.8), "#E8E4DA"); T_.add((4.6, 0, 1.6), (2.2, 2.5, 2.4), "#C0302A"); T_.add((5.72, 0, 2.1), (0.06, 2.2, 0.9), "#9FD0E8")
    T_.add((0, 0, 0.5), (9.0, 2.2, 0.3), "#2A2A2E")
    for x in (-2.4, 1.0, 4.4):
        for y in (-1.15, 1.15): T_.add((x, y, 0.5), (1.0, 0.4, 1.0), "#1C1C20")
    T_.add((5.75, -0.8, 1.0), (0.05, 0.4, 0.2), "#FFF6C8"); T_.add((5.75, 0.8, 1.0), (0.05, 0.4, 0.2), "#FFF6C8")
    T_.done()
    # hospital
    W["hosp"] = g = group("hosp", O_HS)
    B = Batch("hs_b", g, 1.0)
    B.add((0, 0, -0.06), (200, 200, 0.1), tmat("hsfl", "#B8B0A0", 16, 0.05, 201, tiles))
    B.add((0, 10, 6), (20, 8, 12), tmat("hsw", "#F0F0F4", 16, 0.03, 202, tiles)); B.add((0, 5.95, 1.4), (4, 0.1, 2.8), "#9FD0E8")
    B.add((0, 5.9, 9.0), (3.0, 0.1, 1.0), "#E0302A"); B.add((0, 5.85, 9.0), (0.3, 0.05, 0.8), "#F4F1EA"); B.add((0, 5.85, 9.0), (0.8, 0.05, 0.3), "#F4F1EA")
    B.add((-14, 6, 3), (6, 4, 6), "#C8C0B0"); B.add((-14, 3.95, 4.6), (4.0, 0.1, 0.8), "#2A3A5A")
    B.done()
    W["closed"] = text3d("closed", "SEGUROS · CERRADO", (O_HS[0]-14, O_HS[1]+3.85, 4.45), 0.32, "#F4F1EA", None, extrude=0.02)
    W["crowd"] = [Person(f"cw{q}", npc_look(950+q), 1.0) for q in range(8)]
    # cielo
    W["sky"] = g = group("sky", O_SK)
    B = Batch("sk_b", g, 1.0)
    for q in range(30): B.add((r.uniform(-30, 30), r.uniform(-30, 30), r.uniform(-60, -10)), (r.uniform(4, 9), r.uniform(4, 9), 2.0), "#FFFFFF")
    B.add((0, 0, -200), (400, 400, 1), tmat("land", "#5A9A44", 16, 0.15, 203))
    B.done()
    # rocódromo
    W["rock"] = g = group("rock", O_RK)
    B = Batch("rk_b", g, 1.0)
    B.add((0, 0, -0.06), (100, 100, 0.1), "#8A7A6A"); B.add((0, 2, 8), (12, 1.0, 16), tmat("rockw", "#9A8A7A", 16, 0.15, 204))
    for q in range(40): B.add((r.uniform(-5, 5), 1.45, r.uniform(0.5, 15)), (0.25, 0.15, 0.2), ["#E0302A", "#3A8A5A", "#E0C040", "#3A6AA8"][q % 4])
    B.done()
    # circuito
    W["track"] = g = group("track", O_MT)
    B = Batch("mt_b", g, 1.0)
    B.add((0, 0, -0.06), (400, 400, 0.1), tmat("grassm", "#5A9A44", 16, 0.10, 205)); B.add((0, 0, 0.0), (400, 8, 0.06), tmat("tarmac", "#4A4A50", 16, 0.05, 206, asphalt))
    for x in range(-100, 100, 4): B.add((x, 4.2, 0.08), (2.0, 0.4, 0.1), "#E0302A" if (x//4) % 2 else "#F4F1EA")
    B.done()
    W["moto"] = mo = group("moto", (0, 0, 0))
    Mo = Batch("moto_b", mo, 1.0)
    Mo.add((0, 0, 0.55), (1.4, 0.35, 0.4), "#E0302A"); Mo.add((0.55, 0, 0.85), (0.4, 0.3, 0.3), "#E0302A")
    for x in (-0.6, 0.6): Mo.add((x, 0, 0.32), (0.6, 0.15, 0.6), "#1C1C20")
    Mo.add((0.7, 0, 1.05), (0.06, 0.6, 0.06), "#2A2A2E")
    Mo.done()
    W["chute"] = box("chute", (0, 0, 0), (3.0, 1.6, 0.25), mat("#E86A2A"))
    W["counters"] = [text3d(f"ct{q}", "", (0, 0, 0), 0.16, CYAN, None, extrude=0.01) for q in range(10)]
    W["irene"] = I = Person("irene", IRENE)
    hs = 0.56*I.s; t = hs/2; Hm = mat(IRENE["hair"])
    for sx in (-1, 1):   # melena larga hasta los hombros, visible de frente
        box(f"irene_lock{sx}", (sx*(t+0.03*I.s), -0.02*I.s, hs*0.25), (0.07*I.s, hs*0.9, hs*1.0), Hm, I.head)
    box("irene_lockb", (0, t+0.03*I.s, hs*0.1), (hs+0.1*I.s, 0.07*I.s, hs*1.2), Hm, I.head)
    W["rosa"] = Person("rosa", ROSA)
    camera(28)
    return W

def hide_all(W):
    for k in ("bus", "hosp", "sky", "rock", "track", "moto", "truck"): show(W[k], False)
    c = W["city"]; show(c.g, False)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True)
    for o in W["outside"] + W["counters"] + [W["closed"], W["chute"]]: hid(o, True)
    for p in W["npcs"] + W["crowd"] + [W["irene"], W["rosa"]]: p.show(False)
    W["_ci"] = 0

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def person(W, key, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    H = W[key]; H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_)
    return H

def counter(W, H, txt, col=CYAN, size=1.0):
    """contador flotante sobre la cabeza, orientado a la cámara"""
    i = W["_ci"]; W["_ci"] += 1
    if i >= len(W["counters"]): return
    o = W["counters"][i]
    if o.data.body != txt: o.data.body = txt
    o.data.materials[0] = mat(col)
    bpy.context.view_layer.update()
    p = H.head.matrix_world @ Vector((0, 0, 0.85*H.s))
    cam = bpy.context.scene.camera.location
    p = p + (cam-p).normalized()*0.35
    o.location = tuple(p); o.scale = (size, size, size)
    yaw = math.atan2(cam.x-p.x, -(cam.y-p.y))
    o.rotation_euler = (math.pi/2, 0, yaw); hid(o, False)

def sit(H):
    for sx in (-1, 1): H.leg(sx, 1.5, 1.5)
    H.hips.location.z = 0.48

def bus(W, T, move=True):
    show(W["bus"], True); world_color("#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.4)
    for q, o in enumerate(W["outside"]):
        hid(o, False); y = ((q*3.5 - T*6) % 42) - 21
        o.location = (O_BUS[0]+(2.6 if q % 2 else -2.6), O_BUS[1]+y, 1.4)

def city(W):
    c = W["city"]; show(c.g, True)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    world_color("#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)

def fmt_min(m):
    return f"{int(m)} MIN" if m >= 1 else f"{int(m*60)} S"

# ------------------------------------------------------------------ planos
@shot(0.0, 8.62)
def b1(W, T, M):
    bus(W, T)
    I = person(W, "irene", -1.05, 0.1, 0, T, "neutral" if T < 5.0 else "shock", (0.0 if T < 4.4 else 0.9, 0.6 if T < 4.4 else 0.0)); sit(I)
    R = person(W, "rosa", 1.05, 0.1, 0, T, "sad", (0, -0.3)); sit(R)
    if T < 4.6:
        look(lerpv((-1.0, -2.4, 1.6), (-1.0, -1.7, 1.55), eio(clamp(T/4.6))), (-1.05, 0.1, 1.6), 26)
    else:
        look(lerpv((0.2, -2.0, 1.4), (0.5, -1.5, 1.45), eio(clamp((T-4.6)/4.0))), (1.05, 0.1, 1.5), 28)
    counter(W, I, "61 AÑOS"); counter(W, R, "9 MIN", RED, 1.2)
    M["grade"] = "day"

@shot(8.62, 17.2)
def b2(W, T, M):
    city(W); k = (T-8.62)/8.58
    I = person(W, "irene", 3.0, 3.7, 0, T, "shock", (0.6*math.sin(T*1.2), 0.5))
    look(lerpv((4.4, -1.2, 2.2), (3.9, 0.2, 2.0), eio(k)), (3.0, 3.6, 1.9), 24)
    counter(W, I, "61 AÑOS")
    vals = ["52 AÑOS", "3 AÑOS", "18 AÑOS", "70 AÑOS", "4 DÍAS", "33 AÑOS"]
    for q, p in enumerate(W["npcs"]):
        p.show(True); x = -1+q*1.6 + ((T*0.6+q) % 2.0 if q % 2 else 0); y = 4.6 if q % 2 else -4.6
        p.place(x, y, 90 if q % 2 else -90); p.walk(T*1.2+q*0.3); p.face(T, "worried", (0, 0.5))
        counter(W, p, vals[q], RED if "DÍAS" in vals[q] else CYAN, 2.2)
    M["grade"] = "day"

@shot(17.2, 23.94)
def b3(W, T, M):
    show(W["hosp"], True); world_color("#C8D4E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-17.2)/6.74; o = O_HS
    hid(W["closed"], T < 19.0)
    vals = ["2 DÍAS", "11 H", "5 DÍAS", "40 MIN", "3 DÍAS", "1 DÍA", "9 H", "6 DÍAS"]
    for q, p in enumerate(W["crowd"]):
        p.show(True); p.place(o[0]-3+(q % 4)*2.0, o[1]+2.0+(q//4)*1.4, 0); p.idle(T+q); p.face(T, "worried" if q % 2 else "scared", (0, 0.4))
        if q < 6: counter(W, p, vals[q], RED, 2.4)
    if T < 19.0:
        look(lerpv((o[0]-12, o[1]-8.0, 3.0), (o[0]-12.5, o[1]-6.0, 3.6), eio(clamp((T-17.2)/1.8))), (o[0]-14, o[1]+4, 4.4), 26)
    else:
        look(lerpv((o[0]+0.8, o[1]-3.6, 2.3), (o[0]+0.2, o[1]-2.4, 2.5), eio(clamp((T-19.0)/4.9))), (o[0], o[1]+4, 2.0), 24)
    M["grade"] = "day_sad"

@shot(23.94, 35.66)
def b4(W, T, M):
    k = (T-23.94)/11.72
    if T < 32.4:
        city(W)
        I = person(W, "irene", 3.0, 4.0, 0, T, "smirk", (0, 0.2))
        I.arm(1, fwd=1.2, side=0.1, elbow=1.4); I.fingers(1, 0.6, 0.2)
        look(lerpv((3.4, 0.8, 1.9), (3.3, 1.8, 1.8), eio(clamp((T-23.94)/6.8))), (3.0, 4.0, 1.8), 26)
        counter(W, I, "61 AÑOS")
        M["grade"] = "day"
    elif T < 33.6:
        show(W["sky"], True); world_color("#8AC8F0"); light_dir((0.45, -0.55, 0.7)); shadow(0.3); o = O_SK
        I = person(W, "irene", o[0], o[1], 0, T, "happy", (0, -0.5))
        I.hips.rotation_euler = (-1.2, 0, 0)
        for sx in (-1, 1): I.arm(sx, fwd=0.3, side=2.4, elbow=0.2); I.leg(sx, -0.3, 0.6)
        W["sky"].location = (O_SK[0], O_SK[1], 30*(T-32.4))
        look((o[0]+1.5, o[1]-3.0, -1.0), (o[0], o[1], 0.4), 26)
        M["grade"] = "day"
    elif T < 34.4:
        show(W["rock"], True); world_color("#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45); o = O_RK
        z = 6+2.0*(T-33.6)
        I = person(W, "irene", o[0], o[1]+1.2, 180, T, "focus" if False else "happy", (0, 0.5), z=z)
        I.arm(1, fwd=2.8, side=0.3, elbow=0.4+0.3*math.sin(T*6)); I.arm(-1, fwd=2.6, side=0.4, elbow=0.6); I.leg(1, 0.8, 1.2)
        look((o[0]+1.6, o[1]-2.2, z+1.1), (o[0], o[1]+1.2, z+1.0), 24)
        M["grade"] = "day"
    else:
        show(W["track"], True); world_color("#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45); o = O_MT
        x = o[0]-20+30*(T-34.4)
        mo = W["moto"]; show(mo, True); mo.location = (x, o[1], 0); mo.rotation_euler = (0.35, 0, 0)
        I = person(W, "irene", x, o[1], -90, T, "happy", (0, 0), z=0.25)
        I.hips.rotation_euler = (0.9, 0, 0); I.hips.location.z = 0.85
        for sx in (-1, 1): I.leg(sx, 1.3, 1.6); I.arm(sx, fwd=1.4, side=0.1, elbow=0.4)
        I.root.rotation_euler = (0.35, 0, math.radians(90))
        look((x-6.0, o[1]-6.0, 1.2), (x, o[1], 1.0), 22)
        M["grade"] = "day"

@shot(35.66, 44.06)
def b5(W, T, M):
    bus(W, T); k = (T-35.66)/8.4
    I = person(W, "irene", -1.05, 0.1, 0, T, "worried", (0.9, 0.0)); sit(I)
    R = person(W, "rosa", 1.05, 0.1, 0, T, "sad", (0, -0.3)); sit(R)
    for sx in (-1, 1): R.arm(sx, fwd=1.6, side=0.0, elbow=2.2)
    R.head.rotation_euler = (0.35, 0, 0)
    m = 9.0
    if T > 41.9: m = 8.0
    if T > 43.0: m = 7.0
    look(lerpv((0.0, -1.9, 1.5), (0.3, -1.3, 1.45), eio(k)), (1.05, 0.1, 1.35), 28, fstop=3.0)
    counter(W, R, fmt_min(m), RED, 1.2)
    M["grade"] = "day_sad"

@shot(44.06, 49.26)
def b6(W, T, M):
    city(W); k = (T-44.06)/5.2
    f = clamp((T-44.1)/4.0)
    I = W["irene"]; I.show(True); I.place(1.0+3.0*f, 4.4, 90); I.walk(T*1.2); I.face(T, "worried", (0.4, 0))
    R = W["rosa"]; R.show(True); R.place(1.8+3.0*f, 4.2, 90); R.walk(T*1.2+0.3); R.face(T, "sad", (0, 0))
    look((2.4+3.0*f, -1.0, 1.9), (1.6+3.0*f, 4.3, 1.5), 24)
    counter(W, R, fmt_min(6.0-(T-44.06)/5.2*4), RED, 1.1); counter(W, I, "61 AÑOS")
    M["grade"] = "day"

@shot(49.26, 59.34)
def b7(W, T, M):
    city(W)
    pull = 55.3
    tr = W["truck"]; tx = -5.75+20*(T-55.6)
    show(tr, -60 < tx < 60); tr.location = (tx, 0.6, 0)
    I = W["irene"]; R = W["rosa"]
    if T < pull:
        I.show(True); I.place(0.9, 3.7, 180 if T < 53.2 else 200); I.idle(T); I.face(T, "worried" if T < 53.2 else "shock", (0.8, 0.0))
        R.show(True); y = 3.4-2.0*clamp((T-50.0)/3.0); R.place(1.7, y, 180); R.walk(T*0.8) if T < 53.0 else R.idle(T); R.face(T, "sad", (0, -0.3))
        if T > 54.4: I.arm(1, fwd=1.6, side=-0.3, elbow=0.2)
        secs = max(1, int(10-(T-51.8)*2.4)) if T > 51.8 else None
        counter(W, R, f"{secs} S" if secs else "1 MIN", RED, 1.2)
        if T < 53.2:
            look(lerpv((5.0, 0.0, 1.8), (4.5, 0.6, 1.7), eio(clamp((T-49.26)/3.9))), (1.3, 2.6, 1.3), 22)
        else:
            look(lerpv((6.0, -2.5, 2.2), (5.0, -2.0, 2.0), eio(clamp((T-53.2)/2.1))), (0.8, 1.6, 1.2), 22)
    else:
        f = eio(clamp((T-pull)/1.4))
        R.show(True); R.place(1.7, lerp(1.4, 4.2, f), 180); R.idle(T); R.face(T, "shock", (0, 0))
        R.hips.rotation_euler = (-1.2*f, 0, 0); R.hips.location.z = lerp(0.78, 0.45, f)
        I.show(True); I.place(0.9, lerp(3.7, 4.8, f), 180); I.idle(T); I.face(T, "shock", (0, 0))
        I.hips.rotation_euler = (-1.2*f, 0, 0); I.hips.location.z = lerp(0.78, 0.45, f)
        sx_, sy_, sz_ = shake(T, 0.08 if T < pull+1.4 else 0.0)
        look((3.8+sx_, 0.8+sy_, 1.5+sz_), (1.3, 4.1, 0.7), 24)
        if T > 57.0: counter(W, R, "1 S", RED, 1.2)
    if 55.55 < T < 55.63: M["flash"] = 1
    M["grade"] = "day"

@shot(59.34, 65.9)
def b8(W, T, M):
    city(W); k = (T-59.34)/6.56
    I = person(W, "irene", 2.4, 4.4, 0, T, "shock", (0, 0.7)); I.leg(-1, 1.5, 1.5); I.leg(1, 1.5, 1.5); I.hips.location.z = 0.35
    R = person(W, "rosa", 3.6, 4.4, 0, T, "shock" if T < 61.8 else "happy", (0, 0.7)); R.leg(-1, 1.5, 1.5); R.leg(1, 1.5, 1.5); R.hips.location.z = 0.35
    rv = "1 S" if T < 61.6 else "40 AÑOS"
    iv = "61 AÑOS" if T < 64.6 else "21 AÑOS"
    if T < 63.2:
        counter(W, R, rv, RED if T < 61.6 else CYAN, 1.3)
        look(lerpv((3.9, 2.0, 1.5), (3.8, 2.4, 1.45), eio(clamp((T-59.34)/3.8))), (3.6, 4.4, 1.7), 28)
    else:
        counter(W, I, iv, CYAN if T < 64.6 else RED, 1.3)
        look(lerpv((2.1, 2.0, 1.5), (2.2, 2.4, 1.45), eio(clamp((T-63.2)/2.7))), (2.4, 4.4, 1.7), 28)
    if 64.6 < T < 64.68 or 61.6 < T < 61.68: M["flash"] = 1
    M["grade"] = "day"

@shot(65.9, 74.8)
def b9(W, T, M):
    city(W); k = (T-65.9)/8.9
    I = person(W, "irene", 2.4, 4.4, 0, T, "sad" if T < 72.0 else "happy", (0, 0.2)); I.leg(-1, 1.5, 1.5); I.leg(1, 1.5, 1.5); I.hips.location.z = 0.35
    R = person(W, "rosa", 3.6, 4.4, -20, T, "happy", (-0.5, 0)); R.leg(-1, 1.5, 1.5); R.leg(1, 1.5, 1.5); R.hips.location.z = 0.35
    R.arm(-1, fwd=0.8, side=-0.6, elbow=0.6)
    look(lerpv((2.8, 1.6, 1.1), (2.6, 2.6, 1.05), eio(k)), (2.5, 4.4, 1.1), 28, fstop=3.0)
    counter(W, I, "21 AÑOS", CYAN, 1.0)
    M["grade"] = "dawn"

@shot(74.8, TOTAL+0.1)
def b10(W, T, M):
    city(W); k = (T-74.8)/3.39
    I = person(W, "irene", 3.0, 4.2, 0, T, "smirk", (0, 0.1))
    I.arm(1, fwd=1.2, side=0.1, elbow=1.4); I.fingers(1, 0.6, 0.2)
    look(lerpv((3.4, 1.4, 1.65), (3.3, 2.1, 1.62), eio(k)), (3.0, 4.2, 1.6), 26)
    counter(W, I, "21 AÑOS", CYAN, 0.8)
    M["grade"] = "dawn"; M["fade"] = clamp((T-77.8)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
