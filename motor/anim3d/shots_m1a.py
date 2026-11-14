"""M1A · «Caída al Cielo» · Parte 1 (mini-historia 3D de bloques, formato A, serie GRAVEDAD).
Voz única del narrador (Juanjo Viral) colocada en 0,15 s. Protagonista: Nora (pelo castaño recogido,
chaqueta mostaza, vaqueros oscuros). Decorados: calle nocturna (City), habitación de Nora, nubes."""
import math, random
from vox import *
from person import Person, npc_look
from world import City, car, Batch, tmat, text3d

FPS = 24
TOTAL = 75.0
OFF = 0.15
NORA = dict(skin="#F0C8A4", hair="#6A4228", hair2="#7E5232", eye="#3A5A2A", top="#D8A23A", top2="#B8842A", stripe="#F4EAD0",
            legs="#2E3A5A", legs2="#26304A", shoe="#F4F1EA", shoe2="#C0392B", watch=False, hstyle="short")
G = 9.8
CEIL = 3.2          # techo de la habitación
RO = (0, 200, 0)     # origen de la habitación
WIN = (4.0, 5.93, 5.0)   # ventana de Nora en la fachada norte (centro)

import vox as _vox
from mathutils import Vector as _V, Quaternion as _Q
def look(pos, target, lens=None, fstop=None, roll=0.0):
    """como vox.look pero sin TRACK_TO: orientación calculada aquí para poder girar (roll)"""
    cam = bpy.context.scene.camera
    for c in cam.constraints: c.mute = True
    cam.location = pos
    d = _V(target) - _V(pos)
    q = d.to_track_quat('-Z', 'Y')
    if roll: q = q @ _Q((0, 0, 1), roll)
    cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    if lens: cam.data.lens = lens
    dof = cam.data.dof
    if fstop:
        dof.use_dof = True; dof.aperture_fstop = fstop; dof.focus_distance = d.length
    else:
        dof.use_dof = False

class Env:
    def talk(self, who, T): return 0.0

def build():
    reset((720, 1280))
    W = {}
    C = W["city"] = City()
    for d, *_ in C.rain: hid(d, True)
    apply_vis()
    W["nora"] = N = Person("nora", NORA, 0.85)
    # moño (pelo recogido)
    box("nora_bun", (0, 0.22*0.85, 0.62*0.85), (0.2*0.85, 0.16*0.85, 0.18*0.85), mat(NORA["hair"]), N.head)
    W["npc"] = [Person(f"npc{i}", npc_look(700+i), 0.9+0.12*random.Random(i).random()) for i in range(10)]
    W["cars"] = [car(f"fc{i}", c) for i, c in enumerate(("#3A6AA8", "#E0C040", "#D23A2E", "#5A8A5A", "#E0E0D8", "#7A4E8A"))]
    # nubes (muy arriba: es hacia donde se cae)
    W["clouds"] = g = group("clouds")
    B = Batch("clouds_b", g, 2.0)
    r = random.Random(11)
    for i in range(70):
        cx, cy, cz = r.uniform(-60, 60), r.uniform(-40, 40), r.uniform(48, 62)
        for j in range(4):
            B.add((cx+r.uniform(-4, 4), cy+r.uniform(-3, 3), cz+r.uniform(-1, 1)), (r.uniform(5, 10), r.uniform(4, 8), r.uniform(1.5, 3)),
                  tmat("cloud", "#A8B4D0", 8, 0.06, 3))
    B.done()
    # ventana de Nora en la fachada (marco grande + cristal iluminado)
    W["win"] = g = group("winout", WIN)
    B = Batch("winout_b", g, 1.0)
    wood = tmat("frame", "#EDE6D8", 8, 0.05, 21)
    B.add((0, 0, 0), (1.9, 0.05, 2.2), "#FFE0A0")
    B.done()
    W["frame"] = f = group("frame_g", (0, -0.12, 0), g)
    B = Batch("frame_b", f, 1.0)
    B.add((-1.0, 0, 0), (0.16, 0.22, 2.4), wood); B.add((1.0, 0, 0), (0.16, 0.22, 2.4), wood)
    B.add((0, 0, 1.15), (2.16, 0.22, 0.16), wood); B.add((0, 0, -1.15), (2.16, 0.3, 0.16), wood)
    B.add((0, 0, 0), (0.08, 0.14, 2.2), wood)
    B.done()
    W["screws"] = [box(f"screw{i}", (0, 0, 0), (0.07, 0.07, 0.14), mat("#B8BCC4")) for i in range(4)]
    # habitación de Nora
    W["room"] = g = group("room", RO)
    B = Batch("room_b", g, 1.0)
    B.add((0, 0, -0.05), (7, 7, 0.1), tmat("rfloor", "#9A7050", 16, 0.08, 31))
    B.add((0, 0, CEIL+0.05), (7, 7, 0.1), tmat("rceil", "#E8E2D6", 16, 0.03, 32))
    B.add((0, 3.5, CEIL/2), (7, 0.2, CEIL), tmat("rwall", "#7A9AB8", 16, 0.05, 33))
    B.add((-3.5, 0, CEIL/2), (0.2, 7, CEIL), tmat("rwall2", "#6E8EAC", 16, 0.05, 34))
    B.add((3.5, 0, CEIL/2), (0.2, 7, CEIL), tmat("rwall2", "#6E8EAC", 16, 0.05, 34))
    # ventana del cuarto (pared del fondo): cielo nocturno + edificios de enfrente
    B.add((1.2, 3.38, 1.7), (1.8, 0.05, 1.6), "#1E2A4A")
    for i, (x, h) in enumerate(((0.6, 0.5), (1.1, 0.8), (1.6, 0.4), (2.0, 0.7))):
        B.add((x, 3.36, 0.9+h/2), (0.38, 0.03, h), "#2A3048")
        B.add((x, 3.35, 0.95+h*0.6), (0.1, 0.02, 0.1), "#FFE7A0")
    B.add((1.2, 3.3, 2.55), (2.0, 0.16, 0.12), "#EDE6D8"); B.add((1.2, 3.3, 0.85), (2.0, 0.22, 0.12), "#EDE6D8")
    B.add((0.2, 3.3, 1.7), (0.12, 0.16, 1.8), "#EDE6D8"); B.add((2.2, 3.3, 1.7), (0.12, 0.16, 1.8), "#EDE6D8")
    B.add((1.2, 3.3, 1.7), (0.06, 0.12, 1.6), "#EDE6D8")
    B.add((-1.0, 3.38, 2.0), (0.9, 0.04, 0.7), "#C04848")   # póster
    B.done()
    W["roomwin"] = (RO[0]+1.2, RO[1]+3.3, 1.7)
    def prop(name, parts):
        g = group(name, (0, 0, 0), W["room"])
        B = Batch(name+"_b", g, 1.0)
        for c, s, m in parts: B.add(c, s, m)
        B.done(); return g
    W["bed"] = prop("bed", [((0, 0, 0.25), (1.5, 2.4, 0.5), "#6A4A30"), ((0, 0, 0.6), (1.4, 2.3, 0.25), "#F0F0F0"),
                            ((0, 0.85, 0.8), (1.0, 0.45, 0.18), "#FFFFFF"), ((0, -0.35, 0.76), (1.42, 1.5, 0.1), "#4A7AB8"),
                            ((0, 1.25, 0.75), (1.5, 0.1, 1.5), "#6A4A30")])
    W["desk"] = prop("desk", [((0, 0, 0.78), (1.4, 0.7, 0.08), "#C8A070"), ((-0.62, 0, 0.38), (0.08, 0.6, 0.76), "#C8A070"),
                              ((0.62, 0, 0.38), (0.08, 0.6, 0.76), "#C8A070"), ((0.3, 0.1, 0.92), (0.5, 0.06, 0.32), "#2A2A30"),
                              ((-0.35, 0, 0.86), (0.25, 0.3, 0.08), "#C0392B")])
    W["lamp"] = prop("lamp", [((0, 0, 0.3), (0.3, 0.3, 0.6), "#3A3A44"), ((0, 0, 0.72), (0.5, 0.5, 0.3), "#FFE9A0")])
    W["phone"] = prop("phone", [((0, 0, 0.02), (0.18, 0.34, 0.03), "#1E1E24"), ((0, 0, 0.037), (0.15, 0.3, 0.005), "#7FD0FF")])
    W["clock"] = prop("clock", [((0, 0, 0.18), (0.5, 0.22, 0.36), "#2A2A30")])
    W["clock_t"] = text3d("clock_txt", "3:07", (0, -0.115, 0.1), 0.2, "#FF5040", W["clock"])
    W["books"] = [prop(f"book{i}", [((0, 0, 0.05), (0.3, 0.42, 0.1), c)]) for i, c in enumerate(("#3A6AA8", "#E0A030", "#5A8A5A"))]
    camera(26)
    return W

PROPS = ("bed", "desk", "lamp", "phone", "clock", "books")

def hide_all(W):
    C = W["city"]; show(C.g, False)
    for d, *_ in C.rain: hid(d, True)
    hid(C.glass, True)
    for k in ("clouds", "win", "room"): show(W[k], False)
    for c in W["cars"]: show(c, False)
    for s in W["screws"]: hid(s, True)
    for p in [W["nora"]] + W["npc"]: p.show(False)

def night(W):
    C = W["city"]; show(C.g, True)
    for d, *_ in C.rain: hid(d, True)
    hid(C.glass, True); show(C.car, False)
    show(W["clouds"], True); show(W["win"], True)
    for s in W["screws"]: hid(s, True)
    world_color("#1C2848"); light_dir((0.35, -0.5, 0.8)); shadow(0.55)

def room(W, inverted):
    """habitación; inverted: muebles en el techo (boca abajo)"""
    show(W["room"], True); world_color("#2A3450"); light_dir((0.3, -0.6, 0.75)); shadow(0.45)
    for k in ("bed", "desk", "lamp", "phone", "clock"): show(W[k], True)
    for b in W["books"]: show(b, True)
    place_props(W, 1.0 if inverted else 0.0)

HOME = {"bed": (-1.6, 0.6, 0), "desk": (1.9, 1.9, 0), "lamp": (-2.9, 2.6, 0), "phone": (-0.9, -0.5, 0.0), "clock": (1.5, 1.9, 0.82),
        "book0": (2.2, 1.8, 0.82), "book1": (-0.2, -1.4, 0), "book2": (0.7, 0.2, 0)}
def place_props(W, k, T=0.0):
    """k: 0 = suelo · 1 = techo. Cada objeto con su retardo y giro al caer"""
    items = [("bed", W["bed"]), ("desk", W["desk"]), ("lamp", W["lamp"]), ("phone", W["phone"]), ("clock", W["clock"])] + \
            [(f"book{i}", b) for i, b in enumerate(W["books"])]
    for j, (n, g) in enumerate(items):
        x, y, z0 = HOME[n]
        kk = clamp((k - 0.04*j)/0.85)
        u = kk*kk                                   # cae acelerando
        h = {"bed": 0.9, "desk": 0.95, "lamp": 1.0, "clock": 0.36, "phone": 0.05}.get(n, 0.1)
        zt = CEIL - z0 if n not in ("clock", "book0") else CEIL
        z = lerp(z0, zt, u)
        g.location = (x, y, z if kk < 1 else CEIL)
        fl = clamp((u-0.55)/0.45)
        g.rotation_euler = (0.25*math.sin(j)*u*(1-u)*4, math.pi*ease(fl), 0.3*math.sin(j*2)*u)

def nora_bed(N, k):
    """k=0 tumbada en la cama boca arriba; k=1 de espaldas al techo (boca abajo)"""
    N.show(True)
    u = clamp(k)**2
    z = lerp(0.89+0.0, CEIL-0.13, u)
    N.root.location = (RO[0]+lerp(-1.6, 0.1, ease(clamp((k-0.1)/0.8))), RO[1]-0.3, z)
    N.root.rotation_euler = (-math.pi/2, math.pi*ease(clamp((k-0.2)/0.6)), 0)

def flipped(N, x, y, face, z):
    """de pie en el techo / colgando: cuerpo invertido (pies arriba)"""
    N.show(True); N.root.location = (x, y, z); N.root.rotation_euler = (math.pi, 0, math.radians(face))

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def fall(T, t0):
    """altura de caída libre hacia arriba desde t0 (m)"""
    d = max(0.0, T-t0); return 0.5*G*d*d

def rising_cars(W, T, n=6, base=0.0, seed=0, xc=0.0):
    for i, c in enumerate(W["cars"][:n]):
        r = random.Random(i+seed); show(c, True)
        t0 = base + r.uniform(-2.5, 1.0)
        x = xc + (-14 + i*5.5 + r.uniform(-1, 1)); y = r.choice([-1.5, 1.5])
        c.location = (x, y, 0.0 + fall(T, t0)*0.6)
        sp = max(0, T-t0)
        c.rotation_euler = (0.15*sp*math.sin(i), 0.2*sp*math.cos(i*1.7), (0 if y < 0 else math.pi) + 0.1*sp)

def rising_people(W, T, n=6, base=0.0, seed=0, xc=0.0):
    for i, p in enumerate(W["npc"][:n]):
        r = random.Random(i*3+seed); t0 = base + r.uniform(-2.0, 2.0)
        x = xc + r.uniform(-12, 12); y = r.choice([-4.6, 4.4, -3.8])
        z = fall(T, t0)*0.5
        p.show(True); p.place(x, y, r.uniform(0, 360), z)
        if z > 0.05:
            p.root.rotation_euler = (0.6*math.sin(T*1.3+i), 0.5*math.cos(T*1.1+i), p.root.rotation_euler.z + 0.4*(T-t0))
            for sx in (-1, 1):
                p.arm(sx, fwd=2.4+0.4*math.sin(T*9+i+sx), side=0.6, elbow=0.4); p.leg(sx, fwd=0.4*math.sin(T*8+i*sx), knee=0.6)
            p.face(T, "scared", (0, -0.6))
        else:
            p.idle(T); p.face(T, "shock", (0, 0.8))

# ------------------------------------------------------------------ planos
@shot(0.0, 3.25)
def s1(W, T, M):        # gancho: los coches caen hacia el cielo
    night(W); k = T/3.25
    rising_cars(W, T+1.6, 6, 0.0, 1)
    rising_people(W, T+1.2, 6, 0.0, 2)
    N = W["nora"]; N.show(False)
    look(lerpv((-9.0, -2.0, 1.2), (-8.6, -2.4, 1.0), eio(k)), (2.0, 0.6, lerp(5.5, 8.5, eio(k))), 17)
    M["grade"] = "night"

@shot(3.25, 6.99)
def s2(W, T, M):        # no te caes de la cama: caes hacia el techo
    room(W, False); k = (T-3.25)
    fk = clamp((k-1.5)/1.4)
    place_props(W, fk)
    N = W["nora"]; nora_bed(N, fk)
    N.face(T, "neutral" if fk < 0.05 else "shock", (0, 0.4), blink=fk > 0.0)
    if fk < 0.05:
        for e in N.eyes: e.scale = (1, 1, 0.12)
        for p in N.pup: p.scale = (1, 1, 0.12)
    for sx in (-1, 1): N.arm(sx, fwd=0.2+2.0*fk, side=0.3+0.5*fk, elbow=0.3); N.leg(sx, fwd=0.4*fk*sx, knee=0.5*fk)
    sx_, sy_, sz_ = shake(T, 0.03 if fk > 0.95 and fk < 1 else 0)
    look((RO[0]+2.4+sx_, RO[1]-3.6+sy_, lerp(2.0, 1.4, eio(k/3.7))+sz_), (RO[0]-1.5, RO[1]+0.4, lerp(0.9, 2.0, ease(fk))), 20)
    M["grade"] = "room"

@shot(6.99, 9.31)
def s3(W, T, M):        # 3:07 de la madrugada (reloj pegado al techo, cámara invertida)
    room(W, True); k = (T-6.99)/2.32
    N = W["nora"]; nora_bed(N, 1.0); N.face(T, "worried", (0, -0.3))
    c = W["clock"]; cx, cy = RO[0]+HOME["clock"][0], RO[1]+HOME["clock"][1]
    look(lerpv((cx+0.35, cy-1.5, CEIL-0.6), (cx+0.15, cy-1.0, CEIL-0.45), eio(k)), (cx, cy, CEIL-0.22), 30, fstop=2.0, roll=math.pi)
    M["grade"] = "room"

@shot(9.31, 13.11)
def s4(W, T, M):        # Nora despierta de espaldas al techo
    room(W, True); k = (T-9.31)/3.8
    N = W["nora"]; nora_bed(N, 1.0)
    N.face(T, "scared" if k > 0.35 else "worried", (0.3*math.sin(T*2), 0.4))
    for sx in (-1, 1): N.arm(sx, fwd=0.3, side=0.5+0.15*math.sin(T*3+sx), elbow=0.5); N.leg(sx, 0.1*sx, 0.2)
    hx, hy = RO[0]+0.1, RO[1]-0.3+1.5
    look(lerpv((hx+0.9, hy+1.6, 0.9), (hx+0.5, hy+1.1, 1.3), eio(k)), (hx, hy, CEIL-0.25), 24)
    M["grade"] = "room"

@shot(13.11, 17.81)
def s5(W, T, M):        # cama, mesa, móvil… todo arriba con ella (cámara boca abajo: ella «de pie» en el techo)
    room(W, True); k = (T-13.11)/4.7
    N = W["nora"]
    up = clamp((k-0.15)/0.3)
    flipped(N, RO[0]-0.4, RO[1]-0.8, lerp(200, 160, eio(k)), CEIL)
    N.idle(T); N.face(T, "shock", (math.sin(T*1.7)*0.8, 0.2))
    N.arm(1, fwd=0.6, side=0.4, elbow=0.8); N.arm(-1, fwd=0.4, side=0.5, elbow=0.6)
    a = lerp(-0.6, 0.5, eio(k))
    cx, cy = RO[0]-0.2, RO[1]+0.3
    look((cx+math.sin(a)*5.2, cy-math.cos(a)*5.2, 1.0), (cx, cy, 2.2), 20, roll=math.pi)
    M["grade"] = "room"

@shot(17.81, 22.93)
def s6(W, T, M):        # se asoma a la ventana: los coches caen hacia las nubes
    night(W); k = T-17.81
    rising_cars(W, T-17.81+0.4, 6, 0.0, 7, xc=4.0)
    rising_people(W, T-17.81, 4, 0.5, 9, xc=4.0)
    N = W["nora"]; wx, wy, wz = WIN
    flipped(N, wx, wy+0.15, 180, wz+1.1)
    N.idle(T); N.face(T, "shock", (0.4*math.sin(T*1.2), -0.6))
    N.arm(-1, fwd=1.3, side=0.5, elbow=0.3); N.arm(1, fwd=1.3, side=0.5, elbow=0.3)
    if k < 2.4:
        look(lerpv((wx+2.2, wy-3.4, wz-0.6), (wx+1.4, wy-2.6, wz-0.3), eio(k/2.4)), (wx, wy, wz+0.2), 24)
    else:
        kk = eio((k-2.4)/2.7)
        look(lerpv((wx-0.2, wy-0.6, wz+0.3), (wx-0.4, wy-1.0, wz+0.6), kk), (wx-3.0, -1.0, lerp(3.0, 10.0, kk)), 20)
    M["grade"] = "night"

@shot(22.93, 32.75)
def s7(W, T, M):        # no flotan: caen. 9,8 m/s² · ≈200 km/h
    night(W); k = T-22.93
    c = W["cars"][2]; show(c, True)
    z = 0.6 + fall(T, 22.93+0.9)*0.55
    c.location = (2.0, -1.5, z); sp = max(0, k-0.9)
    c.rotation_euler = (0.06*sp, 0.12*sp, 0.04*sp)
    for i, cc in enumerate(W["cars"]):
        if i == 2: continue
        show(cc, True); r = random.Random(i+40)
        cc.location = (-16+i*7, r.choice([-1.5, 1.5]), 0.6 + fall(T, 22.93+r.uniform(-1.5, 2.5))*0.5)
        cc.rotation_euler = (0.1*math.sin(T+i), 0.1*math.cos(T+i), i)
    cz = min(z, 52.0)
    look((lerp(-7.0, -10.0, eio(k/9.8)), 2.2, max(1.2, cz+lerp(-1.5, -5.0, clamp(k/6)))), (2.0, -1.5, cz+0.8), lerp(22, 18, eio(k/9.8)))
    M["grade"] = "night"; M["chip"] = 1

@shot(32.75, 41.55)
def s8(W, T, M):        # REGLA #1: tres puntos de apoyo (dentro, invertida: pies en el techo, manos en la ventana)
    room(W, True); k = T-32.75
    N = W["nora"]; wx, wy, wz = W["roomwin"]
    flipped(N, wx-0.1, wy-0.75, 180, CEIL)
    N.face(T, "worried", (0, 0.6))
    hold = clamp(k/1.2)
    N.arm(-1, fwd=lerp(0.3, 2.2, ease(hold)), side=0.25, elbow=0.25)
    N.arm(1, fwd=lerp(0.3, 2.2, ease(clamp((k-1.6)/1.0))) if k < 5.0 else 0.6, side=0.25, elbow=0.25 if k < 5.0 else 1.0)
    N.leg(-1, 0.0, 0.0); N.leg(1, 0.35 if 4.0 < k < 6.4 else 0.0, 0.5 if 4.0 < k < 6.4 else 0.0)
    N.chest.rotation_euler = (-0.35*hold, 0, 0)
    a = lerp(-0.5, 0.35, eio(k/8.8))
    look((wx+math.sin(a)*3.4, wy-1.0-math.cos(a)*3.0, 1.2), (wx-0.1, wy-0.6, 2.1), 22, roll=math.pi)
    M["grade"] = "room"; M["chip"] = 1

@shot(41.55, 44.67)
def s9(W, T, M):        # su calle es una pared al revés (cámara girada)
    night(W); k = (T-41.55)/3.12
    rising_people(W, T, 5, 41.5, 13, xc=0)
    rl = lerp(0.0, math.pi*0.5, eio(k))
    look((-16.0, -0.5, 3.0), (10.0, 0.5, 8.0), 18, roll=rl)
    M["grade"] = "night"

@shot(44.67, 48.69)
def s10(W, T, M):       # un hombre se suelta de una farola y se pierde entre las nubes
    night(W); k = T-44.67
    p = W["npc"][0]; lx, ly = 6.0, 3.4
    rel = 44.67+1.3
    z = 4.15 + fall(T, rel)
    p.show(True); p.place(lx, ly, 180, z); p.root.rotation_euler = (math.pi+0.2*math.sin(T*2), 0.1*max(0, T-rel), math.radians(180))
    for sx in (-1, 1):
        p.arm(sx, fwd=math.pi if T < rel else 2.6+0.5*math.sin(T*8+sx), side=0.15 if T < rel else 0.7, elbow=0.1)
        p.leg(sx, 0.3*math.sin(T*6+sx), 0.4)
    p.face(T, "scared", (0, 0.8))
    rising_cars(W, T-44.67, 3, 1.0, 21, xc=8)
    if T < rel:
        look((lx-2.0, ly-3.6, 1.6), (lx, ly, 5.0), 22)
    else:
        kk = eio((T-rel)/2.7)
        look((lx-2.0, ly-3.6, lerp(1.6, 2.2, kk)), (lx, ly, min(z, 60)), lerp(22, 30, kk))
    M["grade"] = "night"

@shot(48.69, 53.65)
def s11(W, T, M):       # REGLA #2: no mires hacia donde caes, mira a qué te agarras
    room(W, True); k = T-48.69
    N = W["nora"]; wx, wy, wz = W["roomwin"]
    flipped(N, wx-0.1, wy-0.75, 180, CEIL)
    N.arm(-1, fwd=2.2, side=0.25, elbow=0.25); N.arm(1, fwd=2.2, side=0.25, elbow=0.25)
    N.chest.rotation_euler = (-0.35, 0, 0)
    lk = (0, -0.9) if k < 1.9 else (0, 0.9)
    N.face(T, "scared" if k < 1.9 else "angry", lk)
    hx, hy, hz = wx-0.1, wy-0.75-0.35, CEIL-1.75
    look(lerpv((hx+0.9, hy-1.5, hz-0.3), (hx+0.6, hy-1.1, hz-0.2), eio(k/4.96)), (hx, hy, hz), 26, fstop=2.4, roll=math.pi)
    M["grade"] = "room"; M["chip"] = 1

@shot(53.65, 60.93)
def s12(W, T, M):       # allí arriba: 8.000 m sin oxígeno, −37 °C
    night(W); k = T-53.65
    rising_cars(W, T-53.65+3.0, 4, 0.0, 31, xc=4)
    kk = eio(k/7.28)
    look(lerpv((4.0, 1.0, 9.0), (4.0, 1.0, 30.0), kk), (4.5, 1.6, lerp(30.0, 60.0, kk)), lerp(20, 16, kk))
    M["grade"] = "night"; M["chip"] = 1

@shot(60.93, 65.43)
def s13(W, T, M):       # Nora sale por la ventana, pie a pie por la fachada
    night(W); k = T-60.93
    N = W["nora"]; wx, wy, wz = WIN
    gz = wz-1.15   # alféizar
    flipped(N, wx+lerp(0.0, 0.5, eio(k/4.5)), wy-0.38, 0, gz+1.85)
    for sx in (-1, 1):
        N.arm(sx, fwd=math.pi-0.15+0.12*math.sin(T*3+sx), side=0.25, elbow=0.15)
    N.leg(-1, 0.5+0.2*math.sin(T*2), 0.7); N.leg(1, 0.1, 0.1)
    N.face(T, "worried", (0, 0.7))
    look(lerpv((wx-2.6, wy-4.8, gz+0.4), (wx-1.8, wy-4.0, gz+0.8), eio(k/4.5)), (wx+0.3, wy-0.3, gz+1.2), 22)
    M["grade"] = "night"

@shot(65.43, 67.41)
def s14(W, T, M):       # el marco cruje
    night(W); k = T-65.43
    N = W["nora"]; wx, wy, wz = WIN
    gz = wz-1.15
    flipped(N, wx+0.5, wy-0.38, 0, gz+1.85)
    for sx in (-1, 1): N.arm(sx, fwd=math.pi-0.15, side=0.25, elbow=0.15)
    N.leg(-1, 0.6, 0.7); N.leg(1, 0.1, 0.1)
    N.face(T, "shock" if k > 0.9 else "worried", (0, 0.9))
    cr = 0.02 if k > 0.9 else 0.0
    W["frame"].location = (cr*math.sin(T*60), -0.12, cr*math.sin(T*70))
    sx_, sy_, sz_ = shake(T, 0.015 if k > 0.9 else 0)
    look((wx+1.9+sx_, wy-1.5+sy_, gz-0.15+sz_), (wx+1.0, wy-0.15, gz), 30, fstop=2.0)
    M["grade"] = "night"

@shot(67.41, 72.85)
def s15(W, T, M):       # un tornillo cae hacia el cielo… la ventana empieza a soltarse
    night(W); k = T-67.41
    N = W["nora"]; wx, wy, wz = WIN
    gz = wz-1.15
    lift = 0.0 if k < 3.1 else 0.06*(k-3.1)**2
    W["frame"].location = (0.02*math.sin(T*50), -0.12, lift)
    for i, s in enumerate(W["screws"]):
        t0 = [0.2, 2.0, 3.3, 3.6][i]
        if k < t0: continue
        hid(s, False); sx0 = [-1.0, 1.0, -1.0, 1.0][i]; sz0 = [-1.15, -1.15, 1.15, 1.15][i]
        s.location = (wx+sx0, wy-0.25, wz+sz0+0.12+fall(T, 67.41+t0)*0.6)
        s.rotation_euler = (T*7, T*5, 0)
    flipped(N, wx+0.5, wy-0.38, 0, gz+1.85+lift)
    for sx in (-1, 1): N.arm(sx, fwd=math.pi-0.15, side=0.25, elbow=0.15)
    N.leg(-1, 0.6, 0.7); N.leg(1, 0.1, 0.1)
    N.face(T, "scared", (0, 0.9) if k < 3.0 else (0, -0.9))
    if k < 2.9:
        sz = W["screws"][0].location.z if k > 0.2 else gz
        look((wx-1.6, wy-2.2, gz-0.5), (wx-1.0, wy-0.25, min(max(gz, sz), gz+6)), 26)
    else:
        kk = eio((k-2.9)/2.5)
        sx_, sy_, sz_ = shake(T, 0.02)
        look(lerpv((wx+1.6, wy-3.2, gz+0.6), (wx+2.6, wy-5.4, gz+0.2), kk)+(0,)*0, (wx+0.3, wy-0.3, gz+0.9+lift), 24)
    M["grade"] = "night"

@shot(72.85, TOTAL+0.1)
def s16(W, T, M):       # CONTINUARÁ (negro)
    M["black"] = 1

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    if "black" not in M:
        cam = bpy.context.scene.camera.location
        for p in W["npc"]:
            if DES.get(p.root.name, (None, True))[1]: continue
            l = p.root.location
            if (l - cam).length < 1.6: p.show(False)
    apply_vis()
    return M
