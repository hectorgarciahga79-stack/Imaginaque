"""Q10 · «¿Qué pasaría si mañana despertaras con superfuerza?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral). Tiempos de plano = timeline de align.py (65,79 s).
Decorados propios: dormitorio (origen), laboratorio de datos (y=200: fémur gigante y barras de fuerza),
calle (y=400: pared de ladrillo, coche, camión), vuelo sobre la ciudad (y=600).
Protagonista original: Iván (camiseta roja, pelo negro)."""
import math, random
from vox import *
from person import Person
from world import Batch, tmat, building, tree, tiles, planks, brick, asphalt, car

FPS = 24
TOTAL = 65.79
IVAN = dict(skin="#E2B48C", hair="#16120F", hair2="#2A221C", eye="#4A3020", top="#D8392E", top2="#A82A22", stripe="#F4F1EA",
            legs="#2E3A52", legs2="#243046", shoe="#F4F1EA", shoe2="#2A2A2E", watch=False, hstyle="short")

class Env:
    def talk(self, who, T): return 0.0

O_LAB = (0, 200, 0); O_ST = (0, 400, 0); O_FL = (0, 600, 0)

def build():
    reset((720, 1280))
    W = {}
    # ---------------- dormitorio ----------------
    W["room"] = g = group("room")
    B = Batch("room_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("floor", "#A87A50", 16, 0.07, 61, planks))
    B.add((0, 3.2, 1.6), (14, 0.2, 3.2), tmat("wall", "#9CB8D8", 16, 0.04, 62))
    B.add((-4.0, 0, 1.6), (0.2, 12, 3.2), tmat("wall2", "#8AA8C8", 16, 0.04, 63))
    B.add((1.8, 3.08, 1.9), (1.8, 0.06, 1.3), "#FFD9A0"); B.add((1.8, 3.06, 1.9), (1.9, 0.04, 0.08), "#F4F1EA")
    B.add((-2.2, 1.9, 0.25), (2.0, 2.4, 0.5), "#6A4A30")                         # cama
    B.add((-2.2, 1.9, 0.6), (1.9, 2.3, 0.2), "#F4F1EA"); B.add((-2.2, 2.7, 0.78), (1.4, 0.5, 0.2), "#FFFFFF")
    B.add((-2.2, 1.4, 0.72), (1.95, 1.4, 0.08), "#3A6EA8")
    B.add((-2.2, 3.1, 0.9), (2.0, 0.1, 1.0), "#6A4A30")
    B.add((-0.2, 0.2, 0.01), (2.6, 2.0, 0.02), "#C8A048")                         # alfombra
    B.add((2.6, 2.6, 0.9), (1.2, 0.6, 1.8), "#8A5A36"); B.add((2.6, 2.29, 1.2), (0.04, 0.02, 0.5), "#E0B040")  # armario
    B.done()
    # mesilla (se parte) + despertador
    W["ns_body"] = box("ns_body", (0.6, 1.9, 0.35), (0.6, 0.55, 0.7), mat("#8A5A36"), g)
    W["ns_l"] = box("ns_l", (0.45, 1.9, 0.74), (0.32, 0.6, 0.08), mat("#A06A40"), g)
    W["ns_r"] = box("ns_r", (0.75, 1.9, 0.74), (0.32, 0.6, 0.08), mat("#A06A40"), g)
    W["clock"] = ck = group("clock", (0.6, 1.9, 0.78), g)
    C = Batch("clock_b", ck, 1.0)
    C.add((0, 0, 0.11), (0.3, 0.14, 0.2), "#D8392E"); C.add((0, -0.075, 0.11), (0.22, 0.01, 0.14), "#F4F1EA")
    C.add((0, -0.08, 0.13), (0.02, 0.01, 0.07), "#16120F"); C.add((0.03, -0.08, 0.11), (0.06, 0.01, 0.02), "#16120F")
    for sx in (-1, 1): C.add((sx*0.09, 0, 0.25), (0.08, 0.08, 0.06), "#E0B040")
    C.done()
    # ---------------- laboratorio de datos ----------------
    W["lab"] = g = group("lab", O_LAB)
    B = Batch("lab_b", g, 1.0)
    B.add((0, 0, -0.05), (80, 80, 0.1), tmat("labfl", "#2E3644", 16, 0.05, 64, tiles))
    B.add((0, 14, 20), (80, 0.2, 40), "#1C2230")
    B.add((0, 0, 0.2), (3.0, 3.0, 0.4), "#4A5262")
    B.done()
    W["femur"] = fm = group("femur", (0, 0, 2.6), g)
    F = Batch("femur_b", fm, 1.0)
    for k in range(12): F.add((0.02*math.sin(k), 0, -1.5+k*0.27), (0.42, 0.42, 0.3), "#F2EAD8" if k % 2 else "#E8DEC8")
    F.add((0.25, 0, 1.75), (0.7, 0.55, 0.45), "#F2EAD8"); F.add((0.55, 0, 2.05), (0.55, 0.55, 0.55), "#F6F0E2")
    F.add((-0.2, 0, 1.6), (0.35, 0.4, 0.35), "#E8DEC8")
    F.add((0, 0, -1.85), (0.85, 0.6, 0.45), "#F2EAD8")
    for sx in (-1, 1): F.add((sx*0.28, 0, -2.1), (0.42, 0.55, 0.32), "#F6F0E2")
    F.done()
    W["cracks"] = []
    for k in range(7):
        W["cracks"].append(box(f"crk{k}", (0.0, -0.22, -0.6+k*0.18), (0.08+0.06*(k % 2), 0.03, 0.12), mat("#C0302A"), fm, rot=(0, 0.6*(-1)**k, 0)))
    W["bars"] = []
    for i, (x, c) in enumerate(((-1.6, "#C0302A"), (1.6, "#FFD040"))):
        b = box(f"bar{i}", (x, 0, 0.4), (1.6, 1.6, 1.0), mat(c), g, origin=(0, 0, -0.5))
        cap = box(f"barcap{i}", (x, 0, 0.4), (1.7, 1.7, 0.12), mat("#F4F1EA"), g)
        W["bars"].append((b, cap))
    W["boxer"] = Person("boxer", dict(skin="#B88A64", hair="#1C1612", hair2="#2A221C", eye="#2A1A10", top="#2E6A9A", top2="#245478", stripe="#F4F1EA",
                                       legs="#1C1C22", legs2="#141418", shoe="#C0302A", shoe2="#8A2020", watch=False, hstyle="short"), 0.9)
    # ---------------- calle ----------------
    W["street"] = g = group("street", O_ST)
    B = Batch("st_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("grass2", "#5A9A44", 16, 0.10, 65))
    B.add((0, 0, 0.0), (300, 8, 0.06), tmat("road", "#4A4A50", 16, 0.05, 66, asphalt))
    for x in range(-40, 41, 4): B.add((x, 0, 0.04), (2.0, 0.15, 0.02), "#E8E4DA")
    B.add((0, 5.2, 0.08), (300, 2.4, 0.16), tmat("walk", "#B8B0A0", 16, 0.05, 67, tiles))
    cols = ["#E8D8B8", "#F0E6D0", "#D8C8A8", "#C8D8E0", "#E0C8A8"]
    for k in range(-6, 7):
        building(B, k*11.0, 11.5, 10, 8, 3+k % 3, cols[k % 5], 600+k, -1)
        tree(B, k*11.0+5.5, 6.6, 3.0, k)
    B.done()
    W["wall"] = wl = group("wallg", (6.0, 1.6, 0), g)
    Bw = Batch("wall_b", wl, 1.0); Bw.add((0, 0, 1.25), (3.2, 0.5, 2.5), tmat("bricks", "#B8563A", 16, 0.08, 68, brick)); Bw.done()
    W["wcrack"] = [box(f"wc{k}", (6.0+0.1*math.sin(k*2), 1.34, 1.45+0.12*math.cos(k*3)), (0.18, 0.04, 0.05), mat("#2A1A14"), g, rot=(0, k*0.9, 0)) for k in range(6)]
    W["car"] = car("carq", "#2E78BC")
    W["bumper"] = box("bumper", (0, 0, 0), (0.18, 1.7, 0.26), mat("#2A2A2E"))
    W["truck"] = tr = group("truck", (0, 0, 0))
    T = Batch("truck_b", tr, 1.0)
    T.add((0, 0, 2.3), (12, 2.6, 3.4), "#E8E4DA"); T.add((0, -1.31, 2.3), (11.6, 0.02, 0.6), "#C0302A")
    T.add((7.3, 0, 1.7), (2.4, 2.5, 2.6), "#C0302A"); T.add((8.45, 0, 2.2), (0.08, 2.2, 1.0), "#9FD0E8")
    T.add((0, 0, 0.55), (14, 2.2, 0.3), "#2A2A2E")
    for x in (-4.6, -3.2, 3.0, 7.4):
        for y in (-1.15, 1.15): T.add((x, y, 0.5), (1.0, 0.4, 1.0), "#1C1C20")
    T.done()
    W["skid"] = [box(f"skid{k}", (0, 0, 0), (0.3, 0.18, 0.02), mat("#1C1C20"), None) for k in range(16)]
    # ---------------- vuelo ----------------
    W["fly"] = g = group("fly", O_FL)
    B = Batch("fl_b", g, 1.0)
    B.add((0, 0, -0.06), (900, 300, 0.1), tmat("grass3", "#5A9A44", 16, 0.10, 69))
    B.add((0, 0, 0.0), (900, 10, 0.06), tmat("road2", "#4A4A50", 16, 0.05, 70, asphalt))
    r = random.Random(9)
    for k in range(-30, 31):
        for side in (-1, 1):
            building(B, k*12.0, side*(14+r.uniform(0, 8)), 10, 8, 2+r.randint(0, 5), cols[(k+side) % 5], 700+k*3+side, -side)
    B.done()
    W["cone"] = cn = group("cone", (0, 0, 0))
    Cn = Batch("cone_b", cn, 1.0)
    for ring in range(4):
        R = 0.9+ring*0.75
        for a in range(28):
            an = a*2*math.pi/28
            Cn.add((ring*0.9, math.cos(an)*R, math.sin(an)*R), (0.25, 0.25, 0.25), "#F4FAFF")
    Cn.done()
    # ---------------- personaje ----------------
    W["ivan"] = Person("ivan", IVAN)
    camera(28)
    return W

def hide_all(W):
    for k in ("room", "lab", "street", "fly", "truck", "cone", "car", "femur"): show(W[k], False)
    for b, c in W["bars"]: hid(b, True); hid(c, True)
    for o in W["cracks"] + W["wcrack"] + W["skid"] + [W["bumper"]]: hid(o, True)
    W["ivan"].show(False); W["boxer"].show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def room(W):
    show(W["room"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    for k in ("ns_body", "ns_l", "ns_r"): hid(W[k], False)

def street(W):
    show(W["street"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
    for c in W["wcrack"]: hid(c, True)

def strong_pose(H, T, k=1.0):
    """pose de culturista: brazos en jarra arriba"""
    for sx in (-1, 1): H.arm(sx, fwd=0.2, side=1.45*k, elbow=2.2*k)
    for sx in (-1, 1): H.leg(sx, 0.0, 0.0); H.fingers(sx, 0.9, 1.2)
    H.hips.location.z = 0.78; H.hips.rotation_euler = (0, 0, 0)

def overhead(H, k=1.0):
    for sx in (-1, 1): H.arm(sx, fwd=lerp(0.2, 3.0, k), side=0.25, elbow=lerp(0.3, 0.15, k)); H.fingers(sx, 0.6, 0.9)

# ------------------------------------------------------------------ planos
@shot(0.0, 3.5)
def b1(W, T, M):
    room(W); k = T/3.5
    ck = W["clock"]; ck.location = (0.6, 1.9, 0.78+abs(math.sin(T*28))*0.02); ck.rotation_euler = (0, 0, 0.08*math.sin(T*30))
    H = W["ivan"]; H.show(True); H.place(-0.3, 1.9, 90); H.idle(T)
    H.face(T, "angry" if T > 1.2 else "sad", (0.3, -0.2))
    look(lerpv((2.2, -1.4, 1.9), (1.6, -0.6, 1.75), eio(k)), (-0.1, 1.9, 1.3), lerp(24, 28, k))
    M["grade"] = "dawn"

@shot(3.5, 6.62)
def b2(W, T, M):
    room(W); k = T-3.5
    H = W["ivan"]; H.show(True); H.place(-0.3, 1.9, 90)
    hit = 4.75
    if T < hit:
        kk = eio(clamp((T-3.6)/1.0))
        for sx in (-1, 1): H.arm(sx, fwd=lerp(0.3, 2.9, kk), side=0.15, elbow=0.4)
        H.hips.location.z = 0.78; H.hips.rotation_euler = (0, 0, 0)
    else:
        for sx in (-1, 1): H.arm(sx, fwd=0.75, side=0.12, elbow=0.1)
        H.hips.location.z = 0.74; H.hips.rotation_euler = (0.35, 0, 0)
    for sx in (-1, 1): H.leg(sx, 0.0, 0.0); H.fingers(sx, 0.9, 1.2)
    H.face(T, "angry" if T < hit else "shock", (0.4, -0.4))
    ck = W["clock"]
    if T < hit:
        ck.location = (0.6, 1.9, 0.78+abs(math.sin(T*28))*0.02); ck.scale = (1, 1, 1)
    else:
        f = eio(clamp((T-hit)/0.12)); ck.scale = (1.35, 1.35, lerp(1, 0.18, f)); ck.location = (0.6, 1.9, lerp(0.78, 0.5, f))
        d = ease(clamp((T-hit)/0.6))
        W["ns_l"].location = (0.45-0.3*d, 1.9, 0.74-0.5*d); W["ns_l"].rotation_euler = (0, -1.1*d, 0)
        W["ns_r"].location = (0.75+0.3*d, 1.9, 0.74-0.5*d); W["ns_r"].rotation_euler = (0, 1.1*d, 0)
        W["ns_body"].scale = (1, 1, lerp(1, 0.55, d)); W["ns_body"].location.z = lerp(0.35, 0.19, d)
    sx_, sy_, sz_ = shake(T, 0.05 if hit < T < hit+0.6 else 0.0)
    look((1.3+sx_, -0.9+sy_, 1.55+sz_), (0.2, 1.9, 1.0), 24, fstop=3.0)
    if hit < T < hit+0.08: M["flash"] = 1
    M["grade"] = "dawn"

def reset_room(W):
    W["ns_l"].location = (0.45, 1.9, 0.74); W["ns_l"].rotation_euler = (0, 0, 0)
    W["ns_r"].location = (0.75, 1.9, 0.74); W["ns_r"].rotation_euler = (0, 0, 0)
    W["ns_body"].scale = (1, 1, 1); W["ns_body"].location.z = 0.35
    W["clock"].location = (0.6, 1.9, 0.78); W["clock"].scale = (1, 1, 1); W["clock"].rotation_euler = (0, 0, 0)

@shot(6.62, 10.48)
def b3(W, T, M):
    room(W); reset_room(W); k = (T-6.62)/3.86
    hid(W["clock"], True)
    H = W["ivan"]; H.show(True); H.place(-0.4, 0.6, 15)
    strong_pose(H, T, eio(clamp((T-6.75)/0.5)))
    H.chest.rotation_euler = (0, 0, 0.12*math.sin(T*2.5))
    H.face(T, "happy" if T < 9.0 else "worried", (0.0, 0.1))
    an = -0.5+0.8*eio(k)
    look((-0.4+math.sin(an)*3.4, 0.6-math.cos(an)*3.4, lerp(0.5, 0.9, k)), (-0.4, 0.6, 1.35), 24)
    M["grade"] = "dawn"

@shot(10.48, 14.7)
def b4(W, T, M):
    world_color("#141A26"); light_dir((0.4, -0.6, 0.7)); shadow(0.5)
    show(W["lab"], True); show(W["femur"], True); k = (T-10.48)/4.22
    for b, c in W["bars"]: hid(b, True); hid(c, True)
    W["femur"].rotation_euler = (0.15, 0, T*0.5)
    for i, c in enumerate(W["cracks"]): hid(c, not (T > 12.8+i*0.12))
    H = W["ivan"]; H.show(True); H.place(O_LAB[0]-2.4, O_LAB[1]-0.6, 25, 0.4)
    strong_pose(H, T, 1.0); H.face(T, "neutral" if T < 12.7 else "worried", (0.5, 0.3))
    a = -0.3+0.25*eio(k)
    look((O_LAB[0]+math.sin(a)*9.5-0.8, O_LAB[1]-math.cos(a)*9.5, 2.0), (O_LAB[0]-0.9, O_LAB[1], 2.3), 30)
    M["grade"] = "lab"

@shot(14.7, 20.22)
def b5(W, T, M):
    world_color("#141A26"); light_dir((0.4, -0.6, 0.7)); shadow(0.5)
    show(W["lab"], True); show(W["femur"], False); k = (T-14.7)/5.52
    hs = (0.5*eio(clamp((T-15.3)/0.6)), 50.0*eio(clamp((T-18.2)/1.6)))
    for i, (b, cap) in enumerate(W["bars"]):
        h = max(0.02, hs[i]); hid(b, h < 0.03); hid(cap, h < 0.03)
        b.scale = (1, 1, h); cap.location.z = 0.4+h+0.06
    bx = W["boxer"]; bx.show(True); bx.place(O_LAB[0]-1.6, O_LAB[1]-1.6, 0); bx.idle(T)
    bx.arm(1, fwd=1.5, side=0.05, elbow=1.6); bx.arm(-1, fwd=1.3, side=0.1, elbow=2.2); bx.fingers(1, 1.2, 1.4); bx.fingers(-1, 1.2, 1.4)
    bx.face(T, "angry", (0, 0))
    H = W["ivan"]; H.show(True); H.place(O_LAB[0]+1.6, O_LAB[1]-1.6, 0); H.idle(T)
    if T > 18.2:
        H.arm(1, fwd=1.5, side=0.05, elbow=1.6); H.fingers(1, 1.2, 1.4)
    H.face(T, "smirk" if T > 18.2 else "neutral", (0, 0.2 if T > 18.5 else 0))
    up = eio(clamp((T-18.4)/1.8))
    look((O_LAB[0], O_LAB[1]-lerp(9.5, 13.0, up), lerp(1.6, 4.0, up)), (O_LAB[0], O_LAB[1], lerp(1.2, 9.0, up)), lerp(28, 22, up))
    M["grade"] = "lab"

@shot(20.22, 25.38)
def b6(W, T, M):
    street(W); show(W["wall"], True)
    H = W["ivan"]; H.show(True); H.place(O_ST[0]+6.0, O_ST[1]+0.55, 180)
    hit = 22.0
    if T < hit-0.35:
        H.idle(T); H.arm(1, fwd=1.0, side=0.1, elbow=2.0); H.arm(-1, fwd=1.2, side=0.1, elbow=2.2)
    else:
        kk = eio(clamp((T-(hit-0.35))/0.35))
        H.arm(1, fwd=lerp(1.0, 1.55, kk), side=0.05, elbow=lerp(2.0, 0.05, kk)); H.arm(-1, fwd=0.6, side=0.2, elbow=2.0)
        for sx in (-1, 1): H.leg(sx, 0.25*sx, 0.15)
    for sx in (-1, 1): H.fingers(sx, 1.2, 1.4)
    H.face(T, "angry" if T < hit else ("scared" if T > 22.5 else "shock"), (0, 0))
    for i, c in enumerate(W["wcrack"]): hid(c, not (T > hit+i*0.05))
    if T > 22.3: M["freeze"] = 1
    if hit < T < hit+0.1: M["flash"] = 1
    sx_, sy_, sz_ = shake(T, 0.04 if hit < T < hit+0.5 else 0.0)
    k = (T-20.22)/5.16
    look(lerpv((O_ST[0]+8.9+sx_, O_ST[1]-0.4+sy_, 1.8+sz_), (O_ST[0]+8.3, O_ST[1]+0.1, 1.7), eio(k)), (O_ST[0]+6.0, O_ST[1]+0.9, 1.5), lerp(24, 30, k), fstop=2.8)
    M["grade"] = "day" if T < 23.0 else "alarm"

def car_at(W, loc, rot=(0, 0, 0)):
    c = W["car"]; show(c, True); c.location = loc; c.rotation_euler = rot

@shot(25.38, 30.26)
def b7(W, T, M):
    street(W); k = (T-25.38)/4.88
    up = eio(clamp((T-26.4)/1.6))
    H = W["ivan"]; H.show(True); H.place(O_ST[0], O_ST[1], 0); overhead(H, up)
    for sx in (-1, 1): H.leg(sx, 0.08*sx, 0.15*(1-up))
    H.face(T, "angry" if up < 0.9 else "happy", (0, 0.4*up))
    car_at(W, (O_ST[0], O_ST[1]+lerp(0.9, 0.0, up), lerp(0.0, 1.95, up)), (0, 0, 0))
    a = 0.4-0.25*eio(k)
    look((O_ST[0]+math.sin(a)*7.5, O_ST[1]-math.cos(a)*7.5, 0.7), (O_ST[0], O_ST[1], lerp(1.2, 2.2, up)), 24)
    M["grade"] = "day"

@shot(30.26, 34.16)
def b8(W, T, M):
    street(W); k = (T-30.26)/3.9
    H = W["ivan"]; H.show(True); H.place(O_ST[0], O_ST[1], 0)
    fall = clamp((T-32.4)/0.5)
    if fall <= 0:
        overhead(H, 1.0); car_at(W, (O_ST[0], O_ST[1], 1.95))
    else:
        car_at(W, (O_ST[0]-0.3*fall, O_ST[1]+0.8*fall, max(0.0, 1.95-1.95*fall*fall)), (0.25*fall*(1-fall)*4, 0, 0.1*fall))
        H.arm(1, fwd=2.6, side=0.25, elbow=0.2); H.arm(-1, fwd=0.3, side=0.2, elbow=0.3)
        b = W["bumper"]; hid(b, False); b.location = (O_ST[0]+0.35, O_ST[1]-0.05, 2.25); b.rotation_euler = (0, 0, 0.3)
    for sx in (-1, 1): H.leg(sx, 0, 0); H.fingers(sx, 0.9, 1.1)
    H.face(T, "happy" if T < 32.4 else "shock", (0.0, 0.3))
    if 32.85 < T < 33.1: M["flash"] = 1
    sx_, sy_, sz_ = shake(T, 0.05 if 32.85 < T < 33.3 else 0.0)
    look(lerpv((O_ST[0]+2.6+sx_, O_ST[1]-6.0+sy_, 1.3+sz_), (O_ST[0]+1.6, O_ST[1]-5.0, 1.5), eio(k)), (O_ST[0]+0.1, O_ST[1], 1.6), 26)
    M["grade"] = "day"

@shot(34.16, 39.92)
def b9(W, T, M):
    street(W); k = (T-34.16)/5.76
    tr = W["truck"]; show(tr, True)
    up = eio(clamp((T-34.4)/1.4)); crush = eio(clamp((T-38.35)/0.5))
    hz = 1.95 - 0.55*crush
    tr.location = (O_ST[0]-1.0, O_ST[1], hz-0.4*(1-up)*0 if up > 0 else 0)
    tr.location = (O_ST[0]-1.0, O_ST[1]+lerp(3.0, 0, up), lerp(0.0, hz, up))
    H = W["ivan"]; H.show(True); H.place(O_ST[0], O_ST[1], 0)
    overhead(H, up*(1-0.3*crush))
    bend = clamp((T-35.9)/2.3)*0.35 + crush*1.2
    for sx in (-1, 1): H.leg(sx, bend*0.9, bend*1.6)
    H.hips.location.z = 0.78 - 0.32*min(1, bend/1.2)
    H.face(T, "angry" if T < 37.0 else "scared", (0, 0.4))
    sx_, sy_, sz_ = shake(T, 0.015+0.06*crush*(1-clamp((T-38.9)/0.6)))
    look((O_ST[0]+3.5+sx_, O_ST[1]-8.0+sy_, 0.8+sz_), (O_ST[0]-0.3, O_ST[1], lerp(2.6, 2.2, k)), lerp(18, 20, k))
    if 38.35 < T < 38.45: M["flash"] = 1
    M["grade"] = "day" if T < 37.5 else "alarm"

@shot(39.92, 43.7)
def b10(W, T, M):
    street(W); k = (T-39.92)/3.78
    H = W["ivan"]; H.show(True); H.place(O_ST[0], O_ST[1], 90)
    rel = 41.4
    if T < rel:
        w = eio(clamp((T-39.95)/1.2)); overhead(H, 1.0)
        H.chest.rotation_euler = (-0.35*w, 0, 0)
        car_at(W, (O_ST[0]-0.25*w, O_ST[1], 1.95+0.2*w), (0, 0, math.pi/2))
    else:
        f = T-rel
        for sx in (-1, 1): H.arm(sx, fwd=lerp(3.0, 1.4, eio(clamp(f/0.25))), side=0.15, elbow=0.1)
        H.chest.rotation_euler = (0.3*eio(clamp(f/0.25)), 0, 0)
        car_at(W, (O_ST[0]+20*f, O_ST[1], 2.1+3.0*f-2.0*f*f), (0, f*4, math.pi/2))
    for sx in (-1, 1): H.leg(sx, 0.3*sx, 0.15)
    H.face(T, "angry", (0.0, 0.2))
    look(lerpv((O_ST[0]-2.0, O_ST[1]-8.5, 1.5), (O_ST[0]+1.0, O_ST[1]-11.0, 2.2), eio(k)), (O_ST[0]+lerp(0.5, 2.5, eio(clamp((T-rel)/1.5))), O_ST[1], 2.0), 22)
    M["grade"] = "day"

def flyer(W, T, x, z):
    H = W["ivan"]; H.show(True); H.place(x, O_FL[1], -90, z)
    H.hips.rotation_euler = (-0.5, 0, 0); H.hips.location.z = 0.78
    for sx in (-1, 1): H.arm(sx, fwd=1.6+0.1*math.sin(T*20+sx), side=0.3, elbow=0.2); H.leg(sx, 0.4, 0.4); H.fingers(sx, 0.2, 0.2)
    H.face(T, "scared", (0, 0))
    return H

@shot(43.7, 49.0)
def b11(W, T, M):
    show(W["fly"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-43.7)/5.3
    x = 30*(T-43.7)**1.5; z = 4+1.5*(T-43.7)
    flyer(W, T, x, z)
    sx_, sy_, sz_ = shake(T, 0.03)
    if T < 45.6:
        look((x-3.2+sx_, O_FL[1]-3.0+sy_, z+0.6+sz_), (x, O_FL[1], z+0.7), 26)
    else:
        look((x+5.0+sx_, O_FL[1]-4.5+sy_, z+1.5+sz_), (x, O_FL[1], z+0.7), 30)
    M["grade"] = "day"

@shot(49.0, 54.38)
def b12(W, T, M):
    show(W["fly"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-49.0)/5.38
    x = O_FL[0]+60*(T-49.0); z = 14
    flyer(W, T, x, z)
    cn = W["cone"]; show(cn, True); cn.location = (x-0.6, O_FL[1], z+0.9)
    s = 1.0+0.15*math.sin(T*12); cn.scale = (1.0, s, s)
    look((x-14+8*eio(k), O_FL[1]-16, z+3.0), (x, O_FL[1], z+0.5), lerp(30, 36, k))
    if 52.6 < T < 52.72: M["flash"] = 1
    M["grade"] = "day"

@shot(54.38, 60.16)
def b13(W, T, M):
    street(W); k = (T-54.38)/5.78
    car_at(W, (O_ST[0]+1.6, O_ST[1], 0), (0, 0, 0))
    slide = (T-54.4)*0.55
    H = W["ivan"]; H.show(True); H.place(O_ST[0]-0.75-slide, O_ST[1], 90)
    H.hips.rotation_euler = (0.55, 0, 0); H.hips.location.z = 0.7
    for sx in (-1, 1): H.arm(sx, fwd=1.55, side=0.1, elbow=0.25); H.fingers(sx, 0.4, 0.4)
    ph = T*3.2
    for sx in (-1, 1): H.leg(sx, -0.55+0.25*math.sin(ph+sx*1.6), 0.4)
    H.face(T, "worried" if T < 58.6 else "sad", (0.2, 0))
    for i, s in enumerate(W["skid"]):
        d = i*0.18
        if d > slide: continue
        hid(s, False); s.location = (O_ST[0]-0.75-d, O_ST[1]+(0.1 if i % 2 else -0.1), 0.05)
    a = -0.6+0.3*eio(k)
    look((O_ST[0]-0.3+math.sin(a)*9.0, O_ST[1]-math.cos(a)*9.0, 1.6), (O_ST[0]-0.6-slide*0.5, O_ST[1], 1.0), 24)
    M["grade"] = "day"

@shot(60.16, TOTAL+0.1)
def b14(W, T, M):
    room(W); reset_room(W); k = (T-60.16)/5.63
    H = W["ivan"]; H.show(True); H.face_to(-0.3, 0.8, 0.1, -3.0); H.idle(T)
    H.face(T, "smirk", (0.0, 0.1))
    H.arm(1, fwd=0.2, side=1.45, elbow=2.2); H.fingers(1, 0.9, 1.2)
    H.arm(-1, fwd=1.1, side=0.15, elbow=0.9); H.fingers(-1, 0.0, 0.0)
    look(lerpv((0.2, -2.6, 1.7), (0.05, -1.9, 1.62), eio(k)), (-0.3, 0.8, 1.45), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-65.35)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
