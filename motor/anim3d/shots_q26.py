"""Q26 · Mini historia «Diez segundos» (3D de bloques, 80,5 s). Idea de Héctor: poder retroceder 10 segundos en el tiempo.
Protagonista original: Dani (sudadera mostaza, pelo castaño oscuro). Marta, su novia. Un niño con mochila.
Decorados: cafetería (world.Cafe, y=100), sala de entrevista (y=300), ciudad (world.City), quiosco de lotería en la ciudad."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, City, Cafe, building, tree, tiles, planks, asphalt, stripes, brick, text3d, car

FPS = 24
TOTAL = 80.5
DANI = dict(skin="#E0B08A", hair="#3A2618", hair2="#4A3020", eye="#2A1A10", top="#D8A030", top2="#B88420", stripe="#F4F1EA",
            legs="#2E3A52", legs2="#243046", shoe="#F4F1EA", shoe2="#2A2A2E", watch=True, hstyle="short")
MARTA = dict(skin="#E8BE96", hair="#7A3A22", hair2="#8A4A2A", eye="#2A1A10", top="#2A8A8A", top2="#1E6E6E", stripe="#F4F1EA",
             legs="#3A3A44", legs2="#2C2C34", shoe="#2A2A2E", shoe2="#2A2A2E", watch=False, hstyle="long")
KID = dict(skin="#C68E62", hair="#1C1410", hair2="#2A1E16", eye="#2A1A10", top="#E0302A", top2="#C02020", stripe="#F4F1EA",
           legs="#3A5A8A", legs2="#2E4A74", shoe="#F4F1EA", shoe2="#E0302A", watch=False, hstyle="short")

class Env:
    def talk(self, who, T): return 0.0

O_CF = (0, 100, 0); O_IV = (0, 300, 0)

def longhair(P, L):
    hs = 0.56*P.s; t = hs/2; Hm = mat(L["hair"])
    for sx in (-1, 1):
        box(f"{P.n}_lock{sx}", (sx*(t+0.03*P.s), -0.02*P.s, hs*0.25), (0.07*P.s, hs*0.9, hs*1.0), Hm, P.head)
    box(f"{P.n}_lockb", (0, t+0.03*P.s, hs*0.1), (hs+0.1*P.s, 0.07*P.s, hs*1.2), Hm, P.head)

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(26)
    W["cafe"] = Cafe(O_CF)
    W["cup"] = box("cup26", (0, 0, 0), (0.13, 0.13, 0.15), mat("#F4F1EA"))
    W["shards"] = [(box(f"cs{q}", (0, 0, 0), (0.06, 0.06, 0.03), mat("#F4F1EA")), r.uniform(-1, 1), r.uniform(-1, 1)) for q in range(10)]
    W["phone"] = box("phone26", (0, 0, 0), (0.09, 0.02, 0.17), mat("#1C1C22"))
    # sala de entrevista
    W["iv"] = g = group("iv", O_IV)
    B = Batch("iv_b", g, 1.0)
    B.add((0, 0, -0.05), (16, 16, 0.1), tmat("ivfl", "#8A8A90", 16, 0.04, 261, tiles))
    B.add((0, 3.5, 2.0), (16, 0.2, 4.0), tmat("ivw", "#D8DCE0", 16, 0.03, 262, stripes))
    B.add((-4.0, 0, 2.0), (0.2, 16, 4.0), "#C8CCD2"); B.add((-3.88, 0.5, 2.0), (0.05, 3.0, 1.8), "#BFE0F0")
    B.add((0, 0.2, 0.75), (2.4, 1.1, 0.07), "#6A4A30"); B.add((0, 0.2, 0.37), (2.2, 0.9, 0.7), "#5A3A22")
    B.add((0.6, 0.3, 0.82), (0.5, 0.35, 0.03), "#FBFBF6"); B.add((-0.5, 0.45, 0.95), (0.6, 0.05, 0.4), "#1C1C22")
    for y, by in ((1.3, 0.25), (-0.9, -0.25)):
        B.add((0, y, 0.45), (0.55, 0.55, 0.08), "#2A2A2E"); B.add((0, y+by, 0.75), (0.55, 0.08, 0.6), "#2A2A2E")
    B.add((2.5, 3.3, 1.2), (0.5, 0.5, 2.4), "#3A6A3A"); B.add((-2.4, 3.3, 2.4), (1.6, 0.05, 1.0), "#3A5AA0")
    B.done()
    W["city"] = c = City()
    W["kiosk"] = g = group("kiosk", (3.0, 5.3, 0))
    B = Batch("ki_b", g, 1.0)
    B.add((0, 0, 1.3), (2.0, 1.4, 2.6), "#2A6A9A"); B.add((0, -0.72, 1.4), (1.4, 0.05, 0.8), "#1C1C22"); B.add((0, -0.72, 2.35), (1.9, 0.06, 0.4), "#F0C040")
    B.done()
    W["ktxt"] = text3d("ktxt", "LOTERÍA", (3.0, 4.54, 2.27), 0.24, "#1C1C22", None, extrude=0.02)
    W["kclosed"] = text3d("kclosed", "CERRADO", (3.0, 4.54, 1.38), 0.26, "#E03030", None, extrude=0.02)
    W["ball"] = box("ball26", (0, 0, 0), (0.34, 0.34, 0.34), mat("#F07A20"))
    W["car"] = car("car26", "#3A6AA8")
    W["npcs"] = [Person(f"cn{q}", npc_look(1100+q), 1.0) for q in range(5)]
    W["boss"] = Person("boss", npc_look(1201), 1.0)
    W["dani"] = Person("dani", DANI)
    W["marta"] = Person("marta", MARTA); longhair(W["marta"], MARTA)
    W["kid"] = k = Person("kid", KID, 0.62)
    W["bag"] = box("kidbag", (0, 0.2*0.62, 0.15), (0.32, 0.16, 0.36), mat("#3A8A5A"), k.chest)
    camera(28)
    return W

def hide_all(W):
    W["cafe"].show(False); show(W["iv"], False)
    c = W["city"]; show(c.g, False)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    for k in ("kiosk", "car"): show(W[k], False)
    for k in ("cup", "phone", "ktxt", "kclosed", "ball"): hid(W[k], True)
    for o, a, b in W["shards"]: hid(o, True)
    for p in W["npcs"] + [W["boss"], W["dani"], W["marta"], W["kid"]]: p.show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def person(W, key, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    H = W[key]; H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_)
    return H

def sit(H, z=0.48):
    for sx in (-1, 1): H.leg(sx, 1.5, 1.5)
    H.hips.location.z = z

def snap(H, T, t0):
    """chasquido con la mano derecha a la altura de la cara"""
    H.arm(1, fwd=1.3, side=0.25, elbow=1.7)
    on = (T-t0) % 0.5 < 0.25
    H.fingers(1, 0.9 if on else 0.1, 0.2 if on else 0.9)

def cafe(W, night=False):
    W["cafe"].show(True)
    world_color("#3A3A50" if night else "#E8D8C0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)

def city(W):
    c = W["city"]; show(c.g, True)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    world_color("#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)

def rewind(M, T, t0, t1):
    if t0 <= T < t1:
        M["grade"] = "cold"; M["blur"] = 0.25
        if T < t0+0.08: M["flash"] = 1

# --------------------------------------------------------------- taza
def cup_at(W, tau):
    o = O_CF; base = (o[0]-0.55, o[1]-0.3, o[2]+0.89)
    cup = W["cup"]
    if tau < 0.8:
        hid(cup, False); cup.location = base; cup.rotation_euler = (0, 0, 0)
    elif tau < 2.3:
        k = (tau-0.8)/1.5; hid(cup, False)
        cup.location = (base[0]-0.35*k, base[1]-0.5*k, base[2]-0.83*k*k); cup.rotation_euler = (2.2*k, 0.8*k, 0)
    else:
        k = eio(clamp((tau-2.3)/0.4))
        for o_, a, b in W["shards"]:
            hid(o_, False); o_.location = (base[0]-0.35+a*0.7*k, base[1]-0.5+b*0.7*k, o[2]+0.03+0.25*math.sin(k*math.pi)*abs(a))
            o_.rotation_euler = (a*3*k, b*3*k, a*b*3)

@shot(0.0, 10.22)
def c1(W, T, M):
    cafe(W); o = O_CF
    if T < 4.8: tau = T
    elif T < 7.6: tau = 4.8-(T-4.8)*(4.8/2.8)
    else: tau = 0.0
    cup_at(W, tau)
    D = person(W, "dani", o[0]-1.15, o[1]+0.05, 0, T, "shock" if 1.0 < T < 7.8 else ("neutral" if T < 1.0 else "shock"), (0.3, -0.6) if T < 4.0 else (0.4, 0.0)); sit(D)
    if tau < 0.9: D.arm(1, fwd=0.9, side=-0.2, elbow=1.0)
    if 3.4 < T < 4.8: snap(D, T, 3.4)
    if T < 4.0:
        look(lerpv((o[0]-0.4, o[1]-2.8, 1.2), (o[0]-0.5, o[1]-2.4, 1.15), eio(clamp(T/4.0))), (o[0]-0.9, o[1]-0.3, 0.9), 24)
    elif T < 7.6:
        look((o[0]-0.3, o[1]-3.1, 1.3), (o[0]-0.9, o[1]-0.3, 0.9), 24)
    else:
        look(lerpv((o[0]-0.95, o[1]-2.0, 1.45), (o[0]-1.0, o[1]-1.6, 1.45), eio(clamp((T-7.6)/2.6))), (o[0]-1.15, o[1]+0.05, 1.35), 30)
    M["grade"] = "cafe"; rewind(M, T, 4.8, 7.6)
    if 2.3 < T < 2.38: M["flash"] = 1

@shot(10.22, 14.38)
def c2(W, T, M):
    cafe(W); o = O_CF; cup_at(W, 0.0)
    D = person(W, "dani", o[0]-1.15, o[1]+0.05, 0, T, "worried", (math.sin(T*1.5), 0.1)); sit(D)
    D.head.rotation_euler = (0, 0, 0.5*math.sin(T*1.3))
    pos = [(-2.8, 1.6, 0), (-2.2, 2.2, 180), (0.5, 2.0, 0), (3.0, 1.6, 0), (3.8, 1.6, 0)]
    for q, (x, y, f) in enumerate(pos):
        p = W["npcs"][q]; p.show(True); p.place(o[0]+x, o[1]+y, f); p.idle(T+q); p.face(T, "happy" if q % 2 else "neutral", (0, 0), talk=0.5*abs(math.sin(T*6+q)))
    look(lerpv((o[0]+0.5, o[1]-3.4, 1.7), (o[0]+0.2, o[1]-2.8, 1.6), eio(clamp((T-10.22)/4.16))), (o[0]-0.6, o[1]+0.6, 1.2), 26)
    M["grade"] = "cafe"

@shot(14.38, 23.7)
def c3(W, T, M):
    if T < 18.6:   # el móvil: cae, retrocede, lo atrapa
        city(W)
        D = person(W, "dani", 3.0, 4.0, 0, T, "smirk" if T > 17.2 else "shock", (0, -0.6))
        ph = W["phone"]; hid(ph, False)
        if T < 16.6:
            D.arm(1, fwd=0.9, side=0.0, elbow=0.6)
            k = clamp((T-15.4)/0.7); ph.location = (3.28, 3.6, 1.15-1.0*k*k); ph.rotation_euler = (3*k, 0, 1*k)
            if T > 16.0: snap(D, T, 16.0)
        else:
            k = clamp((T-16.6)/0.6); D.arm(1, fwd=0.9, side=0.0, elbow=0.6)
            ph.location = (3.28, 3.6, lerp(0.55, 1.05, eio(k))); ph.rotation_euler = (0, 0, 0)
        look(lerpv((3.9, 1.8, 1.5), (3.8, 2.3, 1.45), eio(clamp((T-14.38)/4.2))), (3.0, 4.0, 1.2), 26)
        M["grade"] = "day"; rewind(M, T, 16.6, 17.0)
    elif T < 21.1:  # piedra, papel o tijera
        cafe(W); o = O_CF
        D = person(W, "dani", o[0]-1.15, o[1]+0.05, 90, T, "smirk", (0, 0)); sit(D)
        F = W["npcs"][0]; F.show(True); F.place(o[0]+1.15, o[1]+0.05, -90); F.idle(T); F.face(T, "angry" if T > 20.2 else "neutral", (0, 0)); sit(F)
        for P in (D, F):
            P.arm(1, fwd=1.4+0.25*math.sin(T*12) if T < 19.8 else 1.4, side=0.0, elbow=0.4)
        D.fingers(1, 0.0, 0.0); F.fingers(1, 0.9, 0.9)
        look((o[0], o[1]-3.3, 1.5), (o[0], o[1]+0.05, 1.1), 22)
        M["grade"] = "cafe"; rewind(M, T, 19.4, 19.6)
    else:           # el chiste repetido
        cafe(W); o = O_CF
        D = person(W, "dani", o[0]-1.15, o[1]+0.05, 0, T, "happy", (0.6, 0), ); sit(D)
        D.face(T, "happy", (0.6, 0), talk=0.6*abs(math.sin(T*8)))
        laugh = T > 22.6
        for q, (x, y) in enumerate(((1.15, 0.05), (0.0, 1.1))):
            p = W["npcs"][q+1]; p.show(True); p.place(o[0]+x, o[1]+y, -60 if q == 0 else 0); p.idle(T); sit(p)
            p.face(T, "happy" if laugh else "neutral", (-0.5, 0), talk=0.8*abs(math.sin(T*10)) if laugh else 0)
            if laugh: p.chest.rotation_euler = (0.12*math.sin(T*14), 0, 0)
        look(lerpv((o[0]-0.2, o[1]-3.6, 1.5), (o[0]-0.1, o[1]-3.2, 1.45), eio(clamp((T-21.1)/2.6))), (o[0], o[1]+0.3, 1.1), 22)
        M["grade"] = "cafe"; rewind(M, T, 22.2, 22.5)

@shot(23.7, 33.8)
def c4(W, T, M):
    show(W["iv"], True); world_color("#D8DCE0"); light_dir((0.45, -0.55, 0.7)); shadow(0.4); o = O_IV
    D = person(W, "dani", o[0], o[1]-0.65, 180, T, "worried" if T < 28.9 else ("smirk" if T < 32.6 else "happy"), (0, 0.2)); sit(D)
    D.face(T, D and ("worried" if T < 28.9 else "smirk"), (0, 0.2), talk=0.6*abs(math.sin(T*7)) if (26.1 < T < 28.6 or 29.6 < T < 32.4) else 0)
    Bo = person(W, "boss", o[0], o[1]+1.05, 0, T, "neutral" if T < 30.6 else "happy", (0, 0)); sit(Bo)
    if T > 32.6:
        D.hips.location.z = 0.78; D.leg(1, 0, 0); D.leg(-1, 0, 0); Bo.hips.location.z = 0.78; Bo.leg(1, 0, 0); Bo.leg(-1, 0, 0)
        D.arm(1, fwd=1.2, side=-0.1, elbow=0.2); Bo.arm(-1, fwd=1.2, side=-0.1, elbow=0.2)
    if T < 28.6:
        look(lerpv((o[0]+1.2, o[1]-2.8, 1.75), (o[0]+1.0, o[1]-2.4, 1.7), eio(clamp((T-23.7)/4.9))), (o[0], o[1]+1.05, 1.2), 26)
    elif T < 32.6:
        look(lerpv((o[0]-1.2, o[1]+3.0, 1.75), (o[0]-1.0, o[1]+2.6, 1.7), eio(clamp((T-28.6)/4.0))), (o[0], o[1]-0.65, 1.2), 26)
    else:
        look((o[0]+3.0, o[1]+0.2, 1.6), (o[0], o[1]+0.2, 1.3), 26)
    M["grade"] = "office"; rewind(M, T, 28.9, 29.3)

@shot(33.8, 39.3)
def c5(W, T, M):
    city(W); show(W["kiosk"], True); hid(W["ktxt"], False); hid(W["kclosed"], T < 37.4)
    D = person(W, "dani", 3.0, 3.9, 180 if T < 38.0 else 160, T, "smirk" if T < 35.0 else ("worried" if T < 37.4 else "sad"), (0, 0.2))
    if 34.6 < T < 35.8: snap(D, T, 34.6)
    if T > 38.0:
        for sx in (-1, 1): D.arm(sx, fwd=0.4, side=0.6, elbow=1.4)
    look(lerpv((5.4, 1.6, 1.9), (5.0, 2.0, 1.8), eio(clamp((T-33.8)/5.5))), (3.0, 4.6, 1.6), 24)
    M["grade"] = "day"; rewind(M, T, 35.3, 35.7)

@shot(39.3, 51.06)
def c6(W, T, M):
    cafe(W); o = O_CF; cup_at(W, 0.0)
    D = person(W, "dani", o[0]-1.15, o[1]+0.05, 0, T, "happy" if T < 42.0 else ("worried" if T < 46.4 else "neutral"), (0.7, 0)); sit(D)
    Ma = person(W, "marta", o[0]+1.15, o[1]+0.05, 0, T, "happy" if T < 42.0 else ("worried" if T < 47.6 else "sad"), (-0.7, 0)); sit(Ma)
    Ma.face(T, "happy" if T < 42.0 else ("worried" if T < 47.6 else "sad"), (-0.7, 0), talk=0.6*abs(math.sin(T*7)) if 42.0 < T < 45.6 else 0)
    D.face(T, "happy" if T < 42.0 else ("worried" if T < 46.4 else "neutral"), (0.7, 0), talk=0.6*abs(math.sin(T*7)) if (39.4 < T < 41.6 or T > 48.0) else 0)
    if 47.6 < T < 50.5 and (T-47.6) % 1.0 < 0.45: snap(D, T, 47.6)
    if T < 42.0:
        look(lerpv((o[0], o[1]-4.8, 1.7), (o[0], o[1]-4.3, 1.65), eio(clamp((T-39.3)/2.7))), (o[0], o[1]+0.1, 1.15), 22)
    elif T < 46.4:
        look(lerpv((o[0]+0.3, o[1]-2.0, 1.45), (o[0]+0.5, o[1]-1.7, 1.45), eio(clamp((T-42.0)/4.4))), (o[0]+1.15, o[1]+0.05, 1.3), 28)
    else:
        look(lerpv((o[0]-0.3, o[1]-2.0, 1.45), (o[0]-0.5, o[1]-1.7, 1.45), eio(clamp((T-46.4)/4.7))), (o[0]-1.15, o[1]+0.05, 1.3), 28)
    M["grade"] = "cafe"
    for t0 in (48.0, 49.0, 50.0): rewind(M, T, t0, t0+0.25)

# ------------------------------------------------------- calle: pelota, niño, coche
def street(W, tau, T, dani):
    """tau: tiempo de la acción (52.9 = la pelota sale). dani: 'late' o 'early' (con tiempo de reloj T para animar)"""
    city(W)
    b = W["ball"]; hid(b, False)
    kb = clamp((tau-53.1)/1.9)
    b.location = (2.6, lerp(3.6, -3.8, kb), 0.17+0.25*abs(math.sin(kb*9))); b.rotation_euler = (-kb*20, 0, 0)
    K = W["kid"]; K.show(True)
    kk = clamp((tau-54.9)/1.6)
    if kk <= 0: K.place(2.2, 4.6, 180); K.idle(tau); K.face(tau, "happy", (0, -0.4))
    else: K.place(2.2, lerp(4.6, -0.9, kk), 180+180*0); K.walk(tau*1.8, run=True); K.face(tau, "happy", (0, -0.4)); K.root.rotation_euler = (0, 0, math.radians(180))
    if kk >= 1: K.idle(tau); K.face(tau, "shock", (-1, 0)); K.root.rotation_euler = (0, 0, math.radians(120))
    cx = lerp(-45, 9, clamp((tau-54.8)/3.9))
    C = W["car"]; show(C, True); C.location = (cx, -1.4, 0)
    return K, cx

@shot(51.06, 59.42)
def c7(W, T, M):
    tau = min(T, 58.4)
    K, cx = street(W, tau, T, "late")
    D = W["dani"]; D.show(True)
    if T < 57.8: D.place(5.6, 4.2, 180); D.idle(T); D.face(T, "neutral" if T < 54.9 else "shock", (-0.8, -0.3))
    else:
        f = clamp((T-57.8)/0.6); D.place(lerp(5.6, 4.6, f), lerp(4.2, 3.0, f), 220); D.walk(T*2, run=True); D.face(T, "scared", (0, 0))
    if T < 54.9:
        look(lerpv((6.6, 0.4, 1.6), (6.2, 0.8, 1.5), eio(clamp((T-51.06)/3.8))), (2.6, 3.0, 0.6), 24)
    elif T < 57.0:
        look((7.0, -4.5, 1.4), (2.2, 0.5, 0.6), 24)
    else:
        sx_, sy_, sz_ = shake(T, 0.05)
        look((0.2+sx_, -3.6+sy_, 1.0+sz_), (2.2, -0.9, 0.5), 22)
    M["grade"] = "day"
    if T > 58.4: M["flash"] = 1; M["fade"] = 0.0

@shot(59.42, 67.34)
def c8(W, T, M):
    if T < 61.2:
        tau = 58.4-(T-59.42)*(5.5/1.78)
        K, cx = street(W, tau, T, "late")
        D = W["dani"]; D.show(True); D.place(5.6, 4.2, 180); D.idle(T); D.face(T, "shock", (0, 0)); snap(D, T, 59.42)
        look((7.0, -4.5, 1.4), (3.0, 1.5, 0.8), 24)
        M["grade"] = "day"; rewind(M, T, 59.42, 61.2)
        return
    tau = 52.9+(T-61.2)
    K, cx = street(W, tau, T, "early")
    D = W["dani"]; D.show(True)
    cx = lerp(-45, 9, clamp((T-62.2)/3.9)); W["car"].location = (cx, -1.4, 0)
    if T < 62.4:
        D.place(5.6, 4.2, 180); D.idle(T); D.face(T, "angry", (-0.8, -0.3))
    elif T < 65.2:
        f = clamp((T-62.4)/2.6); D.place(lerp(5.6, 2.6, f), lerp(4.2, 0.9, f), 225); D.walk(T*2.2, run=True); D.face(T, "angry", (0, 0))
        K.place(2.2, min(K.root.location.y, 4.6), 180)
    else:
        f = eio(clamp((T-65.2)/1.0))
        D.place(lerp(2.6, 2.8, f), lerp(0.9, 3.8, f), 180+150*f); D.idle(T); D.face(T, "shock" if T < 66.4 else "happy", (0, 0))
        D.arm(1, fwd=1.3, side=-0.2, elbow=0.4)
        K.show(True); K.place(lerp(2.2, 2.4, f), lerp(0.6, 3.3, f), 180*(1-f)); K.idle(T); K.face(T, "shock", (0, 0))
    if T < 64.4:
        look(lerpv((7.5, -1.5, 1.6), (6.5, -0.8, 1.5), eio(clamp((T-61.2)/3.2))), (3.4, 2.2, 0.9), 24)
    else:
        sx_, sy_, sz_ = shake(T, 0.05 if 65.6 < T < 66.6 else 0.0)
        look((-1.2+sx_, -3.8+sy_, 1.3+sz_), (2.6, 2.0, 0.6), 22)
    M["grade"] = "day"
    if 65.40 < T < 65.48: M["flash"] = 1

@shot(67.34, 77.34)
def c9(W, T, M):
    cafe(W, night=True); o = O_CF; cup_at(W, 0.0)
    exD = "worried" if T < 71.9 else ("happy" if T > 73.8 else "smirk")
    D = person(W, "dani", o[0]-1.15, o[1]+0.05, 0, T, exD, (0.7, 0)); sit(D)
    D.face(T, exD, (0.7, 0), talk=0.6*abs(math.sin(T*7)) if 71.9 < T < 73.2 else 0)
    if T > 73.9: D.chest.rotation_euler = (0.1*math.sin(T*12), 0, 0)
    exM = "worried" if T < 72.6 else "happy"
    Ma = person(W, "marta", o[0]+1.15, o[1]+0.05, 0, T, exM, (-0.7, 0)); sit(Ma)
    Ma.face(T, exM, (-0.7, 0), talk=0.5*abs(math.sin(T*7)) if 68.6 < T < 69.8 else 0)
    if T > 75.4:
        D.arm(1, fwd=0.9, side=-0.4, elbow=0.6); D.fingers(1, 0.3, 0.4)
    if T < 70.4:
        look(lerpv((o[0], o[1]-4.8, 1.7), (o[0], o[1]-4.3, 1.65), eio(clamp((T-67.34)/3.0))), (o[0], o[1]+0.1, 1.15), 22)
    elif T < 75.4:
        look(lerpv((o[0]-0.3, o[1]-2.0, 1.45), (o[0]-0.6, o[1]-1.6, 1.45), eio(clamp((T-70.4)/5.0))), (o[0]-1.15, o[1]+0.05, 1.3), 28, fstop=3.0)
    else:
        look(lerpv((o[0]-0.8, o[1]-1.7, 1.2), (o[0]-0.85, o[1]-1.4, 1.15), eio(clamp((T-75.4)/1.9))), (o[0]-1.0, o[1]+0.0, 1.0), 28, fstop=3.0)
    M["grade"] = "night"

@shot(77.34, TOTAL+0.1)
def c10(W, T, M):
    city(W)
    D = person(W, "dani", 3.0, 4.0, 0, T, "smirk", (0, 0.1))
    D.arm(1, fwd=1.3, side=0.25, elbow=1.7); D.fingers(1, 0.1, 0.9)
    look(lerpv((3.4, 1.4, 1.75), (3.3, 2.1, 1.72), eio(clamp((T-77.34)/3.16))), (3.0, 4.0, 1.7), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-80.1)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
