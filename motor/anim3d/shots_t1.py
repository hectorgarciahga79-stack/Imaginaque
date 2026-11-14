"""Plano a plano de «¿Qué pasaría si despertaras con el poder de controlar el tiempo?» (prueba 3D).
frame(T) posa el mundo para el tiempo global T (s) y devuelve metadatos para la postproducción."""
import math, random, json
import numpy as np
from vox import *
from person import Person, LEO, FIG, npc_look
from world import City, Cafe, Field, Office, car, text3d, Batch, tmat
from bpy_extras.object_utils import world_to_camera_view

FPS = 24
TOTAL = 59.4
# ---------------------------------------------------------------- audio (inicio en el vídeo, recorte del archivo)
CLIPS = {  # id: (archivo, ini, fin, colocación)
    "P1": ("pro", 0.0, 0.775, 1.25), "N1": ("nar", 0.0, 3.225, 2.10), "P2": ("pro", 0.775, 2.505, 8.95),
    "N2": ("nar", 3.455, 7.78, 12.85), "P4": ("pro", 4.055, 5.305, 18.55),
    "P5": ("pro", 5.305, 6.905, 21.75), "N3": ("nar", 7.78, 15.345, 24.30), "N4": ("nar", 15.345, 19.86, 34.50),
    "P6": ("pro", 6.905, 8.32, 42.30), "F1": ("fig", 0.0, 3.52, 44.30), "N5": ("nar", 19.86, 24.32, 51.60)}
SPEAKER = {"P": "leo", "F": "fig", "N": None}

class Env:
    """envolvente de voz por personaje para la boca"""
    def __init__(self):
        import librosa
        self.tr = {}
        for who in ("leo", "fig"):
            self.tr[who] = np.zeros(int(TOTAL*100)+10)
        for cid, (f, a, b, at) in CLIPS.items():
            who = SPEAKER[cid[0]]
            if not who: continue
            y, sr = librosa.load(f"/home/claude/t3d/au/{f}.mp3", sr=16000)
            seg = y[int(a*sr):int(b*sr)]
            hop = sr//100
            r = np.array([np.sqrt(np.mean(seg[i:i+hop*2]**2)) for i in range(0, len(seg)-hop, hop)])
            r = r/(r.max()+1e-6)
            i0 = int(at*100); self.tr[who][i0:i0+len(r)] = np.maximum(self.tr[who][i0:i0+len(r)], r)
    def talk(self, who, T):
        a = self.tr[who]; i = int(T*100)
        if i < 0 or i >= len(a): return 0.0
        v = a[i]; return clamp((v-0.08)*1.6)

# ---------------------------------------------------------------- construcción
def build():
    reset((720, 1280))
    W = {}
    W["city"] = City()
    W["cafe"] = Cafe(); W["field"] = Field(); W["office"] = Office()
    W["leo"] = Person("leo", LEO)
    ph = box("phone", (0, -0.03, -0.12), (0.12, 0.03, 0.2), mat("#1E1E24"), W["leo"].hand[1]); W["phone"] = ph
    box("phone_s", (0, -0.017, 0), (0.1, 0.005, 0.17), mat("#7FB8E8"), ph)
    W["coffee_hand"] = box("cup", (0, -0.06, -0.13), (0.11, 0.11, 0.15), mat("#F0EEE8"), W["leo"].hand[-1])
    W["ref"] = Person("leoref", dict(LEO, hair2="#9A9890"))
    hid(W["ref"].grey, False)
    W["fig"] = Person("fig", FIG, 1.08)
    W["friend"] = Person("friend", dict(npc_look(4), hstyle="short", top="#C46A2E", top2="#A85A26", stripe="#C46A2E"))
    W["keeper"] = Person("keeper", dict(npc_look(8), top="#E0C040", top2="#C0A030", stripe="#2A2A2E", hstyle="short"))
    W["boss"] = Person("boss", dict(npc_look(15), top="#3A3A44", top2="#2A2A30", stripe="#B03030", hstyle="bald", hair="#8A8A88"))
    W["cow"] = [Person(f"cow{i}", npc_look(30+i)) for i in range(4)]
    W["npc"] = [Person(f"npc{i}", npc_look(100+i), 0.94+0.12*random.Random(i).random()) for i in range(64)]
    # coches nocturnos
    W["ncars"] = [car(f"ncar{i}", c) for i, c in enumerate(("#3A6AA8", "#E0E0D8", "#2A2A2E", "#5A8A5A"))]
    # set del escaparate (reflejo)
    O = (0, 400, 0); W["win"] = g = group("winset", O)
    B = Batch("win_b", g, 1.0)
    wall = tmat("winwall", "#C8A27A", 16, 0.07, 777)
    B.add((-2.6, 0.2, 2.0), (2.0, 0.4, 4.0), wall); B.add((2.6, 0.2, 2.0), (2.0, 0.4, 4.0), wall)
    B.add((0, 0.2, 3.3), (3.2, 0.4, 1.4), wall); B.add((0, 0.2, 0.15), (3.2, 0.4, 0.3), "#6A6A72")
    B.add((0, -0.02, 2.62), (3.4, 0.08, 0.1), "#3A3A40"); B.add((0, -0.02, 0.32), (3.4, 0.08, 0.06), "#3A3A40")
    for x in (-1.62, 1.62): B.add((x, -0.02, 1.45), (0.08, 0.08, 2.3), "#3A3A40")
    B.add((0, 6.0, 2.0), (12, 0.2, 6), "#5A6A7A")      # fondo del reflejo (la calle de enfrente, desenfocada)
    for i in range(5): B.add((-4+i*2.0, 5.8, 1.5+0.6*(i % 2)), (1.2, 0.2, 2.0+i % 3), ["#9AA8B8", "#B0786A", "#D8C8A8", "#A8B89A", "#C8B8D0"][i])
    B.add((1.8, 3.0, 2.0), (0.14, 0.14, 4.0), "#2E3036"); B.add((1.8, 3.0, 4.0), (0.45, 0.45, 0.25), "#FFF2B0")
    B.add((0, 2.5, -0.04), (12, 8, 0.08), "#B8B4AA")
    B.add((0, -3, -0.04), (12, 6, 0.08), tmat("walk2", "#B8B4AA", 16, 0.05, 12))
    B.add((0, -3.2, 2.0), (12, 0.2, 6), "#8A9AAA")
    W["winb"] = B.done()
    W["glass_corners"] = [(O[0]+x, O[1]-0.0, O[2]+z) for x, z in ((-1.58, 2.57), (1.58, 2.57), (1.58, 0.35), (-1.58, 0.35))]
    # charcos de luz bajo farolas (noche)
    LB = Batch("pools", None, 1.0)
    for (lx, ly, lz) in W["city"].lamps:
        LB.add((lx, ly, 0.21 if abs(ly) > 3 else 0.012), (2.4, 2.4, 0.01), "#C8B47A")
    W["pools"] = LB.done()
    # haces de faros
    W["beams"] = [box(f"beam{i}", (0, 0, 0), (6.0, 1.6, 0.01), mat("#D8D0A0"), None, origin=(-3.0, 0, 0)) for i in range(4)]
    camera(30)
    return W

def hide_all(W):
    show(W["city"].g, False); show(W["win"], False)
    W["cafe"].show(False); hid(W["field"].g, True); show(W["field"].g, False); W["office"].show(False)
    for p in [W["leo"], W["ref"], W["fig"], W["friend"], W["keeper"], W["boss"]] + W["cow"] + W["npc"]: p.show(False)
    for c in W["ncars"]: show(c, False)
    hid(W["pools"], True)
    for b in W["beams"]: hid(b, True)
    hid(W["leo"].mark, True)

def leo_on(W, phone=False, cup=False, grey=False, mark=False):
    L = W["leo"]; L.show(True)
    show(W["phone"], phone); hid(W["coffee_hand"], not cup)
    hid(L.grey, not grey); hid(L.mark, not mark)
    return L

# ---------------------------------------------------------------- utilidades de tiempo
def wtime(T, freezes):
    """tiempo del mundo con pausas: freezes = [(t0, t1), …] (t1 = None → sigue congelado)"""
    w = T
    for a, b in freezes:
        if T > a:
            w -= (min(T, b if b is not None else 1e9) - a)
    return w

def frozen(T, freezes):
    return any(T > a and (b is None or T < b) for a, b in freezes)

def snap_pose(P, sx, k):
    """k 0..1: levanta la mano, junta pulgar e índice y chasquea a k≈0.7"""
    up = ease(k/0.4)
    P.arm(sx, fwd=1.25*up, side=0.25*up, elbow=1.5*up, twist=0.0)
    if k < 0.7: P.fingers(sx, thumb=1.2*up, index=1.3*up)
    else: P.fingers(sx, thumb=0.2, index=0.4)

def pedestrians(W, T, wt, day=True, n=16, frozen_heads=None, center=0.0, span=60.0):
    city = W["city"]
    for i, p in enumerate(W["npc"]):
        if i >= n: p.show(False); continue
        p.show(True); r = random.Random(i)
        side = 1 if i % 2 == 0 else -1
        y = side*(3.7 + r.random()*1.8)
        dirx = 1 if r.random() < 0.5 else -1
        sp = 1.0+r.random()*0.5
        x = ((r.random()*span + dirx*sp*wt) % span) - span/2 + center
        p.place(x, y, 90 if dirx > 0 else -90)
        p.walk(wt*sp*0.9+r.random(), sp); p.face(wt, "neutral", (0, 0), blink=not frozen_heads)
    return

# ---------------------------------------------------------------- planos
SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

FZ1 = [(1.70, 11.45)]                     # S1–S2: primera congelación
CAR_V = 19.0
def car_x(wt): return 2.45 + CAR_V*(1.70 - wt)   # coche hacia −X, se para a 0,35 m de Leo

def city_day(W, T, wt, rain=True, n=16):
    show(W["city"].g, True); W["city"].rain_on = rain
    world_color("#8E9CAE" if rain else "#9CC8E8"); light_dir((0.5, -0.45, 0.75)); shadow(0.35 if rain else 0.5)
    pedestrians(W, T, wt, True, n)
    hid(W["city"].glass, True); W["city"].rain[0][0].scale = (1, 1, 1)
    c = W["city"].car; show(c, True); c.rotation_euler = (0, 0, math.pi)
    c.location = (car_x(wt), 1.3, 0)

def leo_cross(W, T, wt, L):
    y = 3.6 - 1.32*min(wt, 1.70)
    return y

@shot(0.0, 1.1)
def s1a(W, T, M):
    wt = wtime(T, FZ1); city_day(W, T, wt)
    L = leo_on(W, phone=True); y = leo_cross(W, T, wt, L)
    L.place(0, y, 0); L.walk(wt*0.85)
    L.arm(1, fwd=0.35, side=-0.35, elbow=1.25, twist=-0.4); L.fingers(1, 0.6, 0.8)
    L.face(T, "happy", (-0.4, -1.0)); L.head.rotation_euler = (0.3, 0, 0)
    W["city"].place_rain((0, 1.5, 0), T, None)
    k = T/1.1
    look(lerpv((-6.5, -2.5, 1.2), (-6.0, -2.2, 1.15), k), (2.67, 1.49, 1.3), 16, fstop=8)
    M["grade"] = "rain"

@shot(1.1, 1.95)
def s1b(W, T, M):
    wt = wtime(T, FZ1); city_day(W, T, wt)
    L = leo_on(W, phone=True); y = leo_cross(W, T, wt, L)
    L.place(0, y, 0)
    k = clamp((T-1.15)/0.25)
    if T < 1.3:
        L.walk(wt*0.85); L.arm(1, fwd=0.35, side=-0.35, elbow=1.25, twist=-0.4)
        L.face(T, "shock" if T > 1.18 else "happy", (1.0*k, -0.8+0.8*k))
    else:
        kk = ease((T-1.3)/0.25)
        L.idle(T); L.arm(1, fwd=0.4*kk, side=1.45*kk, elbow=0.1); L.fingers(1, 0, 0)
        L.arm(-1, fwd=0.6*kk, side=-0.2, elbow=1.2*kk)
        L.chest.rotation_euler = (0.08*kk, 0, 0.25*kk)
        L.face(T, "shock", (1.0, 0.0), talk=W["env"].talk("leo", T))
    W["city"].place_rain((0, 1.5, 0), T, 1.70 if T > 1.70 else None)
    look((-1.0, -0.4, 1.72), (0.25, y, 1.65), 34, fstop=2.2)
    M["grade"] = "rain"

@shot(1.95, 5.6)
def s1c(W, T, M):
    wt = wtime(T, FZ1); city_day(W, T, wt)
    L = leo_on(W, phone=True); L.place(0, 1.3, 0); L.idle(1.70, 0)
    L.arm(1, fwd=0.4, side=1.45, elbow=0.1); L.fingers(1, 0, 0); L.arm(-1, fwd=0.6, side=-0.2, elbow=1.2)
    L.chest.rotation_euler = (0.08, 0, 0.25)
    L.face(1.70, "shock", (1.0, 0.0), blink=False)
    W["city"].place_rain((0.8, 1.3, 0), T, 1.70)
    k = eio((T-1.95)/3.65)
    a = math.radians(lerp(-150, 25, k)); R = lerp(3.6, 4.4, k)
    look((0.9+math.sin(a)*R, 1.3-math.cos(a)*R, lerp(1.2, 2.4, k)), (0.7, 1.3, 1.25), 22, fstop=5)
    M["grade"] = "rain"; M["freeze"] = 1

@shot(5.6, 7.6)
def s2a(W, T, M):
    wt = wtime(T, FZ1); city_day(W, T, wt)
    L = leo_on(W, phone=False)
    k = (T-5.6)/2.0
    if k < 0.45:
        L.place(0, 1.3, 0); L.idle(T); kk = ease(k/0.2)
        L.arm(1, fwd=0.4*(1-kk), side=1.45*(1-kk)+0.08, elbow=0.1)
        L.face(T, "shock", (math.sin(T*5)*0.9, 0.2))
        L.head.rotation_euler = (0, 0, math.sin(T*3.2)*0.5)
    else:
        kk = ease((k-0.45)/0.35)
        L.place(lerp(0, 0.15, kk), 1.3, lerp(0, 90, kk)); L.walk((T-6.5)*0.9) if kk < 1 else L.idle(T)
        if k > 0.75:
            r = ease((k-0.75)/0.25); L.arm(1, fwd=1.0*r, elbow=0.5*r, side=-0.1*r); L.chest.rotation_euler = (-0.25*r, 0, 0)
        L.face(T, "shock" if k < 0.8 else "worried", (0.6, -0.5))
    W["city"].place_rain((0.8, 1.3, 0), T, 1.70)
    look(lerpv((-2.6, -1.4, 1.5), (-2.0, -1.0, 1.4), ease(k)), (0.5, 1.3, 1.15), 28, fstop=3)
    M["grade"] = "rain"; M["freeze"] = 1

DROP = (0.42, 0.62, 1.86)
@shot(7.6, 8.95)
def s2b(W, T, M):
    wt = wtime(T, FZ1); city_day(W, T, wt)
    L = leo_on(W); L.place(0.15, 1.3, 35); L.idle(T, 0.3)
    k = (T-7.6)/1.35
    L.face(T, "shock" if k < 0.4 else "happy", (0.0, 0.0), brow=(0.06, 0.0) if k < 0.4 else None)
    for i, sx in enumerate((-1, 1)): L.pup[i].location.x = sx*0.125*L.s - sx*0.025*L.s   # bizquea un poco: mira la gota
    r = ease((k-0.35)/0.35)
    L.arm(1, fwd=1.45*r, side=0.0, elbow=0.55*r, twist=0.0); L.fingers(1, 0.6, 1.4*(1-r)+0.0)
    W["city"].place_rain((0.8, 1.3, 0), T, 1.70)
    d, *_ = W["city"].rain[0]; d.location = (DROP[0], DROP[1]+(0.01*math.sin(T*30) if k > 0.7 else 0), DROP[2]); hid(d, False)
    d.scale = (2.2, 2.2, 0.55)
    look((0.75, -0.25, 1.9), (0.42, 0.62, 1.86), 30, fstop=1.4)
    M["grade"] = "rain"; M["freeze"] = 1

@shot(8.95, 10.8)
def s2c(W, T, M):
    wt = wtime(T, FZ1); city_day(W, T, wt)
    W["city"].rain[0][0].scale = (1, 1, 1)
    L = leo_on(W); k = (T-8.95)/1.85
    L.place(0.15, 1.3, lerp(90, 25, ease(k*3))); L.idle(T)
    tk = W["env"].talk("leo", T)
    L.face(T, "smirk" if k < 0.18 else "happy", (-0.3, 0.1), talk=tk)
    L.arm(1, fwd=0.5, side=0.5, elbow=1.3); L.arm(-1, fwd=0.5, side=0.5, elbow=1.3)
    L.chest.rotation_euler = (0.06*math.sin(T*9)*tk, 0, 0)
    W["city"].place_rain((0.8, 1.3, 0), T, 1.70)
    look(lerpv((1.3, -0.9, 1.78), (1.05, -0.55, 1.8), k), (0.15, 1.3, 1.72), 40, fstop=2.0)
    M["grade"] = "rain"; M["freeze"] = 1

@shot(10.8, 12.85)
def s2d(W, T, M):
    wt = wtime(T, FZ1); city_day(W, T, wt)
    L = leo_on(W); k = T-10.8
    if k < 0.45:
        kk = ease(k/0.45); L.place(lerp(0.15, -0.3, kk), lerp(1.3, 3.3, kk), 180); L.walk(k*1.6, run=True)
        L.face(T, "happy", (0, 0))
    else:
        L.place(-0.3, 3.3, 0); L.idle(T)
        sk = clamp((k-0.45)/0.25)
        if T < 11.6: snap_pose(L, 1, sk)
        else: L.arm(1, fwd=0.2, side=0.1, elbow=0.3)
        if T > 11.5:
            L.face(T, "shock", (1.0*clamp((T-11.5)/0.2)-2*clamp((T-11.7)/0.5), 0.0))
            L.head.rotation_euler = (0, 0, lerp(-0.6, 0.9, clamp((T-11.5)/0.6)))
            L.chest.rotation_euler = (0.12, 0, 0)
            L.tuft.rotation_euler = (0.2+0.4*math.sin(T*25)*math.exp(-(T-11.5)*3), 0, 0.3)
        else: L.face(T, "smirk", (0, 0))
    W["city"].place_rain((0, 2.0, 0), T, None if T > 11.45 else 1.70)
    look(lerpv((-3.4, -1.0, 0.55), (-3.0, -1.3, 0.6), k/2), (0.0, 2.6, 1.3), 20, fstop=6)
    M["grade"] = "rain"; M["freeze"] = 1 if T < 11.45 else 0
    if 11.45 <= T < 11.8: M["ripple"] = (T-11.45)/0.35

# ---------- cafetería
FZ_C = [(13.95, 14.85)]
@shot(12.85, 16.4)
def s3a(W, T, M):
    C = W["cafe"]; C.show(True); world_color("#E8D8B8"); light_dir((-0.3, -0.5, 0.8)); shadow(0.4)
    O = C.O; wt = wtime(T, FZ_C)
    L = leo_on(W); F = W["friend"]; F.show(True)
    sit(L, O[0]-1.15, O[1], 90); sit(F, O[0]+1.15, O[1], -90)
    # el amigo se lleva una patata a la boca (despacio)
    fk = clamp((wt-12.85)/1.6)
    F.arm(1, fwd=lerp(0.6, 1.5, ease(fk)), side=-0.2, elbow=lerp(0.6, 2.1, ease(fk))); F.fingers(1, 1.0, 1.0)
    F.arm(-1, fwd=0.5, elbow=0.9)
    st = W["cafe"].stolen
    hand = F.hand[1].matrix_world.translation
    if T < 14.3:
        bpy.context.view_layer.update(); hand = F.hand[1].matrix_world.translation
        st.location = (hand.x, hand.y, hand.z-0.12); st.rotation_euler = (0, 0.9, 0)
    tk = W["env"].talk("leo", T)
    if T < 13.85:
        L.arm(1, fwd=0.6, elbow=0.9); L.arm(-1, fwd=0.6, elbow=0.9)
        L.face(T, "neutral", (0.6, 0.0)); F.face(T, "happy", (-0.6, 0.0))
    elif T < 14.85:   # congelado: Leo se levanta un poco y roba la patata
        r = ease((T-13.95)/0.5)
        if T < 14.0: snap_pose(L, -1, (T-13.85)/0.15)
        L.chest.rotation_euler = (-0.35*r, 0, 0); L.arm(1, fwd=1.4*r+0.4, elbow=0.4, side=-0.1)
        L.face(T, "smirk", (1.0, 0.2)); F.face(13.95, "happy", (-0.6, 0.0), blink=False)
        if T > 14.6: snap_pose(L, -1, (T-14.6)/0.36)
        if T > 14.3:
            bpy.context.view_layer.update(); h = L.hand[1].matrix_world.translation
            st.location = (h.x, h.y, h.z-0.12)
    else:
        r = ease((T-14.85)/0.3)
        L.chest.rotation_euler = (-0.35*(1-r), 0, 0); L.arm(1, fwd=lerp(1.8, 1.6, r), elbow=lerp(0.4, 2.2, r), side=-0.2)
        bpy.context.view_layer.update(); h = L.hand[1].matrix_world.translation
        st.location = (h.x, h.y, h.z-0.06) if T < 15.25 else (0, 0, -50)
        L.face(T, "happy", (0.5, 0.0), talk=tk)
        bite = clamp((T-14.85)/0.25)
        F.face(T, "shock" if T > 15.15 else "happy", (-0.2, -0.6 if T > 15.15 else 0), talk=0.8*(1-bite) if T < 15.15 else 0.6)
    t = T-12.85
    if T < 13.95:
        look(lerpv((O[0]+0.2, O[1]-5.6, 1.5), (O[0]+0.1, O[1]-4.9, 1.45), t/1.1), (O[0], O[1], 1.15), 22, fstop=3)
    elif T < 14.85:
        a = lerp(-0.5, 0.25, (T-13.95)/0.9)
        look((O[0]-0.2+math.sin(a)*3.0, O[1]-math.cos(a)*3.0, 1.75), (O[0]-0.2, O[1], 1.2), 24, fstop=2.5)
    else:
        look((O[0]+0.1, O[1]-4.7, 1.55), (O[0], O[1], 1.2), 20, fstop=4)
    M["grade"] = "cafe"; M["freeze"] = 1 if frozen(T, FZ_C) else 0
    if 13.95 <= T < 14.3: M["ripple"] = (T-13.95)/0.35
    if 14.85 <= T < 15.2: M["ripple"] = (T-14.85)/0.35

def sit(P, x, y, face):
    P.place(x, y, face); P.idle(0)
    P.hips.location.z = 0.52*P.s
    for sx in (-1, 1): P.leg(sx, fwd=1.5, knee=1.5)

# ---------- fútbol
FZ_F = [(17.30, 18.45)]
@shot(16.4, 19.85)
def s3b(W, T, M):
    Fd = W["field"]; show(Fd.g, True); world_color("#8CC4F0"); light_dir((0.4, -0.3, 0.85)); shadow(0.55)
    O = Fd.O; wt = wtime(T, FZ_F)
    L = leo_on(W); K = W["keeper"]; K.show(True)
    b = Fd.ball
    # balón: patada a 16.6, hacia la escuadra izquierda; tras el cambio, a la derecha
    def ball_path(k, tx):
        return (O[0]+lerp(0, tx, k), O[1]+lerp(-1.0, 10.4, k), O[2]+0.16+1.25*math.sin(min(k, 1)*math.pi*0.8)+0.0*k)
    kk = clamp((wt-16.6)/1.0)   # vuelo: 1 s de mundo
    if T < 17.3:
        b.location = ball_path(kk, -1.7)
        L.place(O[0]+lerp(-0.8, -0.1, clamp((T-16.4)/0.2)), O[1]-1.8, 170)
        if T < 16.6: L.walk(T*2.2, run=True)
        else:
            L.idle(T); L.leg(1, fwd=1.3*ease((T-16.6)/0.15), knee=0.2); L.arm(-1, fwd=0.6, side=0.6, elbow=0.4)
            if T > 17.08: snap_pose(L, -1, (T-17.08)/0.3)
        L.face(T, "angry" if T < 16.7 else "happy", (0, 0.3))
    elif T < 18.45:   # congelado: Leo junto al balón en el aire, lo cambia de sitio
        k = (T-17.35)/1.1
        p0 = ball_path(clamp((17.30-16.6)/1.0), -1.7); p1 = (O[0]+1.9, O[1]+9.6, O[2]+1.6)
        m = ease((k-0.2)/0.6)
        b.location = lerpv(p0, p1, m)
        L.place(lerp(p0[0]-0.2, p1[0]-0.35, m), p0[1]-0.6, 90 if m < 1 else 30)
        L.walk(T*1.4) if 0.2 < k < 0.8 else L.idle(T)
        L.arm(1, fwd=1.6, side=0.2, elbow=0.3); L.arm(-1, fwd=1.6, side=0.2, elbow=0.3)
        L.face(T, "smirk", (0.4, 0.6))
        if T > 18.25: snap_pose(L, 1, (T-18.25)/0.2)
    else:
        k = clamp((T-18.45)/0.35)
        b.location = lerpv((O[0]+1.9, O[1]+9.6, O[2]+1.6), (O[0]+2.0, O[1]+10.8, O[2]+1.5), k)
        L.place(O[0]+1.55, O[1]+9.0, 200); L.idle(T)
        L.arm(1, fwd=3.0, side=0.3, elbow=0.2); L.arm(-1, fwd=3.0, side=0.3, elbow=0.2)
        L.face(T, "happy", (0, 0.5), talk=W["env"].talk("leo", T))
        L.hips.location.z = 0.78*L.s + 0.15*abs(math.sin(T*7))*L.s
    # portero: se lanza hacia la izquierda
    dk = clamp((wt-16.85)/0.5)
    K.place(O[0]+lerp(0, -1.3, ease(dk)), O[1]+9.6, 0, z=0.6*math.sin(min(dk, 1)*math.pi*0.6) if T < 18.45 else max(0, 0.6*math.sin(math.pi*0.6) - 2*(T-18.45))-0.0)
    K.root.rotation_euler = (0, lerp(0, 1.2, ease(dk)) if T < 18.45 else lerp(1.2, 1.5, clamp((T-18.45)/0.3)), 0)
    K.idle(T); K.arm(1, fwd=1.2*dk, side=2.6*dk, elbow=0.1); K.arm(-1, fwd=1.2*dk, side=2.6*dk, elbow=0.1)
    K.face(wt, "shock" if dk > 0.3 else "angry", (-0.6, 0.4), blink=not frozen(T, FZ_F))
    if T < 17.3:
        k = (T-16.4)/0.9
        look(lerpv((O[0]-0.8, O[1]-5.2, 1.1), (O[0]-0.6, O[1]-3.8, 1.5), k), (b.location.x*0.3+O[0]*0.7, O[1]+4, 1.3), 24, fstop=6)
    elif T < 18.45:
        k = (T-17.3)/1.15
        look(lerpv((O[0]+3.6, O[1]+3.2, 1.6), (O[0]+3.2, O[1]+3.9, 1.75), k), (O[0]-0.8, O[1]+7.0, 1.3), 24, fstop=5)
    else:
        look((O[0]+0.4, O[1]+13.8, 1.5), (O[0]+1.0, O[1]+8.6, 1.1), 26, fstop=5)
    M["grade"] = "field"; M["freeze"] = 1 if frozen(T, FZ_F) else 0
    if 17.30 <= T < 17.65: M["ripple"] = (T-17.3)/0.35
    if 18.45 <= T < 18.8: M["ripple"] = (T-18.45)/0.35
    if T > 18.5: M["cheer"] = 1

# ---------- oficina
FZ_O = [(20.35, 21.65)]
@shot(19.85, 23.25)
def s3c(W, T, M):
    Of = W["office"]; Of.show(True); world_color("#E4E6E8"); light_dir((0.2, -0.6, 0.8)); shadow(0.35)
    O = Of.O; wt = wtime(T, FZ_O)
    L = leo_on(W, cup=True); Bo = W["boss"]; Bo.show(True)
    dx, dy = Of.desks[1]; desk = (O[0]+dx, O[1]+dy)
    for i, c in enumerate(W["cow"]):
        c.show(True); x, y = Of.desks[[0, 2, 3, 5][i]]
        sit(c, O[0]+x, O[1]+y-0.9, 180)
        c.arm(1, fwd=1.1, elbow=0.5+0.15*math.sin(wt*14+i)); c.arm(-1, fwd=1.1, elbow=0.5+0.15*math.sin(wt*13+i*2))
        c.face(wt, "neutral", (0, -0.4), blink=not frozen(T, FZ_O))
    # jefe junto a la mesa vacía mirando el reloj
    Bo.place(desk[0]+1.3, desk[1]-1.9, -60 if T < 21.65 else lerp(-60, -100, clamp((T-21.65)/0.3)))
    Bo.idle(wt); Bo.arm(-1, fwd=1.2, elbow=1.6, side=0.3); Bo.arm(1, fwd=0.9, elbow=1.8, side=0.2)
    Bo.leg(1, fwd=0.15*abs(math.sin(wt*6)))
    Bo.face(wt, "angry" if T < 21.75 else "shock", (0.5 if T < 21.75 else -0.8, -0.6 if T < 21.75 else 0.0), blink=not frozen(T, FZ_O))
    # reloj de pared
    mins = 14 + clamp((wt-19.85)/3)*2
    Of.clock_m.rotation_euler = (0, math.radians(mins*6), 0); Of.clock_h.rotation_euler = (0, math.radians(270+mins*0.5), 0)
    if T < 20.35:
        k = (T-19.85)/0.5
        L.place(O[0]-5.0+3.0*k, desk[1]-2.6, 90); L.walk(T*2.4, run=True); L.face(T, "scared", (0.5, 0))
        if T > 20.15: snap_pose(L, 1, (T-20.15)/0.2)
    elif T < 21.65:
        k = (T-20.4)/1.25
        if k < 0.6:
            kk = ease(k/0.6); L.place(lerp(O[0]-2.0, desk[0], kk), lerp(desk[1]-2.6, desk[1]-0.9, kk), lerp(90, 150, kk)); L.walk(T*1.3)
            L.arm(-1, fwd=0.9, elbow=1.2)
        else:
            sit(L, desk[0], desk[1]-0.9, 180); L.arm(-1, fwd=0.9, elbow=1.2)
        L.face(T, "smirk", (0.6, 0))
        if T > 21.45: snap_pose(L, 1, (T-21.45)/0.2)
    else:
        sit(L, desk[0], desk[1]-0.9, lerp(180, 60, ease((T-21.65)/0.35)))
        L.arm(1, fwd=2.6, side=0.5, elbow=2.4); L.arm(-1, fwd=2.6, side=0.5, elbow=2.4)
        L.face(T, "happy", (1.0, 0.1), talk=W["env"].talk("leo", T))
        hid(W["coffee_hand"], True)
        Of.coffee.location = (desk[0]-0.4, desk[1]-0.2, 0.86); hid(Of.coffee, False)
    if T < 20.35:
        look((O[0]-1.5, desk[1]-7.0, 1.7), (O[0]-3.0, desk[1]-2.6, 1.1), 24, fstop=5)
    elif T < 21.65:
        k = (T-20.35)/1.3
        look(lerpv((desk[0]-3.5, desk[1]-5.5, 2.4), (desk[0]-1.5, desk[1]-5.0, 1.9), k), (desk[0]-0.3, desk[1]-1.6, 1.1), 26, fstop=4)
    else:
        look((desk[0]+0.1, desk[1]-4.6, 1.55), (desk[0]+0.6, desk[1]-1.5, 1.3), 26, fstop=3)
    M["grade"] = "office"; M["freeze"] = 1 if frozen(T, FZ_O) else 0
    if 20.35 <= T < 20.7: M["ripple"] = (T-20.35)/0.35
    if 21.65 <= T < 22.0: M["ripple"] = (T-21.65)/0.35

# ---------- el precio
@shot(23.25, 25.2)
def s4a(W, T, M):
    city_day(W, T, T, rain=False, n=16); show(W["city"].car, False)
    L = leo_on(W, mark=True); L.place(-4.0, 3.9, 0); L.idle(T)
    k = (T-23.25)/1.95
    L.arm(1, fwd=0.9, side=-0.2, elbow=0.95); L.fingers(1, 0.3, 0.3)
    L.face(T, "worried" if k > 0.4 else "neutral", (0.3, -0.6))
    pulse = 0.5+0.5*math.sin(T*9)
    L.mark.scale = (1+0.25*pulse*ease(k*3), 1, 1+0.25*pulse*ease(k*3)); hid(L.mark, k < 0.12)
    bpy.context.view_layer.update(); h = L.el[1].matrix_world @ Vector((0, -0.1, -0.25)); hd = L.head.matrix_world @ Vector((0, 0, 0.28))
    tg = tuple(h)
    look(lerpv((hd.x+0.75, hd.y+0.55, hd.z+0.7), (hd.x+0.65, hd.y+0.45, hd.z+0.6), k), tg, 36, fstop=2.0)
    M["grade"] = "day"; M["glow_mark"] = 1

@shot(25.2, 27.4)
def s4b(W, T, M):
    city_day(W, T, T, rain=False); show(W["city"].car, False)
    L = leo_on(W, mark=True, grey=T > 26.6); L.place(-4.0, 3.9, 0); L.idle(T)
    k = (T-25.2)/2.2
    L.arm(-1, fwd=0.9, side=-0.2, elbow=0.95)
    L.arm(1, fwd=0.3, elbow=0.4)
    L.watchhand.rotation_euler = (0, T*T*1.6, 0)
    L.face(T, "worried", (-0.4, -0.7))
    bpy.context.view_layer.update(); h = L.el[-1].matrix_world @ Vector((0, -0.12, -0.255))
    hd = L.head.matrix_world @ Vector((0, 0, 0.28))
    look(lerpv((hd.x-0.75, hd.y+0.5, hd.z+0.65), (hd.x-0.62, hd.y+0.4, hd.z+0.55), k), tuple(h), 40, fstop=1.6)
    M["grade"] = "day"

@shot(27.4, 30.9)
def s4c(W, T, M):
    show(W["win"], True); world_color("#9CC8E8"); light_dir((0.3, -0.6, 0.7)); shadow(0.45)
    O = (0, 400, 0); k = (T-27.4)/3.5
    L = leo_on(W, grey=True); L.place(O[0]-0.25+0.0, O[1]-0.9, 180); L.idle(T)
    R = W["ref"]; R.show(True); hid(R.mark, True); R.place(O[0]-0.25, O[1]+0.9, 0); R.idle(T)
    for P in (L, R):
        P.arm(-1, fwd=0.3, elbow=0.5); P.arm(1, fwd=0.3, elbow=0.5)
    L.face(T, "neutral" if k < 0.4 else "worried", (0, 0.1))
    R.face(T, "neutral" if k < 0.4 else "worried", (0, 0.1))
    R.brows[0].location.z -= 0.01; R.mouth.scale = (0.9, 1, 1)
    look(lerpv((O[0]+1.25, O[1]-2.9, 1.85), (O[0]+1.0, O[1]-2.5, 1.85), k), (O[0]-0.35, O[1]+0.9, 1.65), 32, fstop=2.8)
    M["grade"] = "day"; M["glass"] = W["glass_corners"]

@shot(30.9, 34.4)
def s4d(W, T, M):
    show(W["win"], True); world_color("#9CC8E8"); shadow(0.45)
    O = (0, 400, 0); k = (T-30.9)/3.5
    L = leo_on(W, grey=True); L.place(O[0]-0.25, O[1]-0.9, 180); L.idle(T)
    L.face(T, "happy" if k < 0.15 else ("worried" if k < 0.55 else "sad"), (0.0, -0.1 if k > 0.6 else 0.1))
    look(lerpv((O[0]-0.1, O[1]+0.9, 1.84), (O[0]-0.15, O[1]+0.55, 1.83), k), (O[0]-0.25, O[1]-0.9, 1.78), 28, fstop=2.0)
    M["grade"] = "day_sad"; M["glass_full"] = 1

# ---------- la noche
FZ_N = [(36.0, None)]
def city_night(W, T, wt, n=64):
    show(W["city"].g, True); W["city"].rain_on = True; hid(W["pools"], False); hid(W["city"].glass, True)
    world_color("#0A0F1E"); light_dir((-0.2, -0.3, 0.9)); shadow(0.7)
    show(W["city"].car, False)
    pedestrians(W, T, wt, False, n, frozen_heads=frozen(T, FZ_N), center=-8.5, span=30.0)
    for i, c in enumerate(W["ncars"]):
        show(c, True); lane = 1.3 if i % 2 == 0 else -1.3; d = -1 if i % 2 == 0 else 1
        x = ((i*17 + d*14*wt) % 70) - 35
        c.location = (x, lane, 0); c.rotation_euler = (0, 0, 0 if d > 0 else math.pi)
        b = W["beams"][i]; hid(b, False); b.location = (x+d*1.8, lane, 0.02); b.rotation_euler = (0, 0, 0 if d > 0 else math.pi)

def leo_night_x(T):
    return -13.25 + 1.25*clamp(T-34.4, 0, 3.4) if T < 38.0 else -13.25+1.25*3.4
@shot(34.4, 36.1)
def s5a(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    L = leo_on(W, grey=True); x = leo_night_x(T)
    L.place(x, 4.6, 90); L.walk((T-34.4)*0.95)
    if T > 35.75: snap_pose(L, 1, (T-35.75)/0.25)
    L.face(T, "neutral", (0, -0.3))
    W["city"].place_rain((x, 3.0, 0), T, 36.0 if T > 36.0 else None, (12, 10, 7))
    k = eio((T-34.4)/1.7)
    look(lerpv((x-7, -6.0, 9.0), (x-3.2, 0.5, 2.6), k), (x+0.5, 4.4, 1.1), 24, fstop=6)
    M["grade"] = "night"

@shot(36.1, 37.7)
def s5b(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    L = leo_on(W, grey=True); x = leo_night_x(T)
    L.place(x, 4.6, 90); L.walk((T-34.4)*0.95)
    L.arm(1, fwd=0.1, elbow=0.9, side=0.15); L.arm(-1, fwd=0.1, elbow=0.9, side=0.15)
    L.face(T, "happy", (-0.6, 0))
    W["city"].place_rain((x, 3.0, 0), T, 36.0, (12, 10, 7))
    look((x-0.3, 1.0, 1.35), (x+0.2, 4.6, 1.45), 30, fstop=3.5)
    M["grade"] = "night"; M["freeze"] = 1
    if T < 36.45: M["ripple"] = (T-36.0)/0.35

@shot(37.7, 39.1)
def s5c(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    L = leo_on(W, grey=True); x = leo_night_x(T)
    L.place(x, 4.6, 90); L.idle(T)
    k = (T-37.7)/1.4
    L.face(T, "neutral" if T < 38.1 else "shock", (0.0 if T < 38.1 else -0.9, 0.0), blink=T < 38.1)
    W["city"].place_rain((x, 3.0, 0), T, 36.0, (12, 10, 7))
    look(lerpv((x+2.1, 3.6, 1.85), (x+1.8, 3.75, 1.84), k), (x, 4.6, 1.78), 34, fstop=1.8)
    M["grade"] = "night"; M["freeze"] = 1

FIGX = lambda T: -16.5 + 1.0*clamp(T-39.1, 0, 5.2)
@shot(39.1, 40.7)
def s5d(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    L = leo_on(W, grey=True); x = leo_night_x(T)
    k = ease((T-39.1)/1.5)
    L.place(x, 4.6, lerp(90, 270, k)); L.idle(T)
    L.head.rotation_euler = (0, 0, 0.6*(1-k))
    L.face(T, "scared", (0, 0))
    F = W["fig"]; F.show(True); fx = FIGX(T); F.place(fx, 4.4, 90); F.walk(T*0.7); F.face(T, "neutral", (0, 0))
    W["city"].place_rain((x, 3.0, 0), T, 36.0, (12, 10, 7))
    look((x+2.2, 2.6, 1.7), (x-1.0, 4.5, 1.55), 30, fstop=2.5)
    M["grade"] = "night"; M["freeze"] = 1

@shot(40.7, 42.3)
def s5e(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    L = leo_on(W, grey=True); x = leo_night_x(T); L.place(x, 4.6, 270); L.idle(T); L.face(T, "scared", (0, 0))
    F = W["fig"]; F.show(True); fx = FIGX(T); F.place(fx, 4.4, 90); F.walk(T*0.7); F.face(T, "neutral", (0, 0), blink=False)
    W["city"].place_rain((x-3, 3.0, 0), T, 36.0, (14, 10, 7))
    k = (T-40.7)/1.6
    look(lerpv((x+0.4, 3.9, 0.55), (x+0.2, 4.0, 0.6), k), (fx, 4.4, 1.55), 30, fstop=4)
    M["grade"] = "night"; M["freeze"] = 1

@shot(42.3, 44.3)
def s5f(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    L = leo_on(W, grey=True); k = (T-42.3)/2.0
    x = leo_night_x(T) + 0.6*ease(k)
    L.place(x, 4.6, 270); L.walk(-k*1.2) if k < 0.8 else L.idle(T)
    L.arm(1, fwd=0.9, side=0.3, elbow=0.6); L.arm(-1, fwd=0.9, side=0.3, elbow=0.6)
    L.face(T, "scared", (0, 0), talk=W["env"].talk("leo", T))
    F = W["fig"]; F.show(True); fx = FIGX(T); F.place(fx, 4.4, 90); F.walk(T*0.7)
    W["city"].place_rain((x, 3.0, 0), T, 36.0, (12, 10, 7))
    look(lerpv((x-1.6, 0.5, 1.5), (x-1.6, 0.8, 1.5), k), (x-1.6, 4.5, 1.45), 16, fstop=5)
    M["grade"] = "night"; M["freeze"] = 1

@shot(44.3, 47.85)
def s5g(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    xl = leo_night_x(T)+0.6
    L = leo_on(W, grey=True); L.place(xl, 4.6, 270); L.idle(T); L.face(T, "scared", (0, 0))
    F = W["fig"]; F.show(True); fx = min(FIGX(T), xl-2.0); F.place(fx, 4.4, 90)
    F.walk(T*0.7) if FIGX(T) < xl-2.0 else F.idle(T)
    F.face(T, "smirk", (0, 0), talk=W["env"].talk("fig", T), blink=False)
    W["city"].place_rain((fx, 3.0, 0), T, 36.0, (12, 10, 7))
    k = eio((T-44.3)/3.4)
    hz = 0.78*1.08+0.74*1.08+0.3*1.08
    look(lerpv((fx+3.4, 3.3, 1.9), (fx+1.9, 4.0, hz+0.02), k), (fx, 4.4, hz-0.05), lerp(30, 40, k), fstop=lerp(4, 2.0, k))
    M["grade"] = "night"; M["freeze"] = 1; M["drone"] = 1

@shot(47.85, 49.2)
def s6a(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    xl = leo_night_x(T)+0.6
    F = W["fig"]; F.show(True); fx = xl-2.0; F.place(fx, 4.4, 90); F.idle(T)
    k = (T-47.85)/1.35
    snap_pose(F, 1, clamp(k/0.6)); F.face(T, "smirk", (0, 0), blink=False)
    L = leo_on(W, grey=True); L.place(xl, 4.6, 270); L.idle(T); L.face(T, "scared", (0, 0))
    W["city"].place_rain((fx, 3.0, 0), T, 36.0, (12, 10, 7))
    bpy.context.view_layer.update(); h = F.hand[1].matrix_world.translation
    look((h.x+1.7, h.y-1.3, h.z-0.1), (h.x-0.2, h.y, h.z-0.15), 32, fstop=2.2)
    M["grade"] = "night"; M["freeze"] = 1
    if k > 0.45: M["ripple_v"] = clamp((k-0.45)/0.4)

def crowd_awake(W, T, xl):
    """los peatones congelados se despiertan: giran la cabeza y caminan hacia Leo"""
    ka = clamp((T-48.4)/0.6)
    for i, p in enumerate(W["npc"]):
        r = random.Random(i)
        if r.random() < 0.65 and ka > 0:
            st = 48.4 + r.random()*1.6
            if T > st:
                loc = p.root.location
                tx, ty = xl, 4.6
                walk_k = clamp((T-st-0.3)/5.0)
                nx = lerp(loc.x, tx, walk_k*0.72); ny = lerp(loc.y, ty, walk_k*0.72)
                p.face_to(nx, ny, tx, ty); p.walk((T-st)*0.8) if T-st > 0.4 else p.idle(T)
                p.face(T, "neutral", (0, 0))

@shot(49.2, 51.7)
def s6b(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    xl = leo_night_x(T)+0.6
    crowd_awake(W, T, xl)
    L = leo_on(W, grey=True); L.place(xl, 4.6, lerp(270, 200, ease((T-49.2)/1.5))); L.idle(T); L.face(T, "scared", (math.sin(T*2.5), 0))
    F = W["fig"]; F.show(True); F.place(xl-2.0, 4.4, 90); F.idle(T); F.face(T, "smirk", (0, 0))
    W["city"].place_rain((xl, 3.0, 0), T, 36.0, (14, 12, 7))
    k = (T-49.2)/2.5
    look(lerpv((xl-1.2, 2.4, 1.0), (xl-0.9, 2.8, 1.15), k), (xl+3.0, 4.6, 1.3), 22, fstop=5)
    M["grade"] = "night"; M["freeze"] = 1; M["crowd"] = 1

@shot(51.7, 56.4)
def s6c(W, T, M):
    wt = wtime(T, FZ_N); city_night(W, T, wt)
    xl = leo_night_x(T)+0.6
    crowd_awake(W, T, xl)
    L = leo_on(W, grey=True); L.place(xl, 4.6, 200); L.idle(T); L.face(T, "scared", (0, 0.5))
    F = W["fig"]; F.show(True); F.place(xl-2.0, 4.4, 90); F.idle(T)
    W["city"].place_rain((xl, 3.0, 0), T, 36.0, (20, 14, 9))
    k = eio((T-51.7)/4.7)
    look(lerpv((xl+1.5, 1.0, 2.0), (xl+11.0, -1.2, 13.0), k), (xl, 4.4, lerp(1.4, 0.6, k)), lerp(26, 22, k), fstop=None)
    M["grade"] = "night"; M["freeze"] = 1; M["crowd"] = 1
    M["fade"] = clamp((T-55.9)/0.5)

@shot(56.4, TOTAL+0.1)
def s7(W, T, M):
    M["black"] = 1

def _segd(p, a, b):
    ax, ay, bx, by = a.x, a.y, b.x, b.y; dx, dy = bx-ax, by-ay; L2 = dx*dx+dy*dy+1e-9
    u = ((p.x-ax)*dx+(p.y-ay)*dy)/L2
    if u <= 0.05 or u >= 0.95: return 9.0
    return math.hypot(p.x-(ax+u*dx), p.y-(ay+u*dy))

def DES_NAMES():
    return [k for k, v in DES.items() if not v[1]]

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    if "glass" in M or "glass_full" in M:
        sc = bpy.context.scene; bpy.context.view_layer.update()
        if "glass" in M:
            M["glass"] = [tuple(world_to_camera_view(sc, sc.camera, Vector(p)))[:2] for p in M["glass"]]
    # nadie se cruza delante de la cámara ni se mete dentro de Leo o de la figura
    cam = bpy.context.scene.camera.location
    keep = [W["leo"].root.location.copy()]
    if not W["fig"].root.hide_render or ("fig" in DES_NAMES()): keep.append(W["fig"].root.location.copy())
    keep.append(bpy.data.objects[bpy.context.scene.camera["tgt"]].location.copy())
    for p in W["npc"]:
        if DES.get(p.root.name, (None, True))[1]: continue
        l = p.root.location
        if math.hypot(l.x-cam.x, l.y-cam.y) < 1.4 or any(math.hypot(l.x-k.x, l.y-k.y) < 0.85 for k in keep) \
                or (not M.get("crowd") and any(_segd(l, cam, k) < 1.05 for k in keep)):
            p.show(False)
    apply_vis()
    return M
