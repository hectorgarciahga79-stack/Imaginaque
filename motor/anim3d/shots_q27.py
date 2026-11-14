"""Q27 · Mini historia «Sangre de oro» (3D de bloques, 75,0 s). Idea de Héctor: ¿y si tu cuerpo fabricara oro en lugar de sangre?
Protagonista original: Tomás (mecánico, mono azul). Su hija Alba. Joyero, médica, el hombre del traje negro.
Decorados: taller (y=100), joyería (y=300), escalera (y=500), hospital (y=700), baño (y=900), parque (y=1100), ciudad (world.City)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, City, building, tree, tiles, planks, asphalt, stripes, brick, text3d, car

FPS = 24
TOTAL = 75.0
GOLD = "#FFC830"
TOMAS = dict(skin="#D8A47A", hair="#2A2420", hair2="#3A3028", eye="#2A1A10", top="#2E5A9A", top2="#244A82", stripe="#E8A030",
             legs="#2E5A9A", legs2="#244A82", shoe="#3A2A20", shoe2="#3A2A20", watch=False, hstyle="short")
ALBA = dict(skin="#D8A47A", hair="#3A2618", hair2="#4A3020", eye="#2A1A10", top="#E86A8A", top2="#C85070", stripe="#F4F1EA",
            legs="#3A5A8A", legs2="#2E4A74", shoe="#F4F1EA", shoe2="#E86A8A", watch=False, hstyle="long")
DOC = dict(skin="#C68E62", hair="#1C1410", hair2="#2A1E16", eye="#2A1A10", top="#F4F4F0", top2="#E0E0DC", stripe="#3A8AA8",
           legs="#3A8AA8", legs2="#2E7A98", shoe="#F4F1EA", shoe2="#F4F1EA", watch=False, hstyle="long")
SUIT = dict(skin="#F2C9A0", hair="#141216", hair2="#141216", eye="#2A2A30", top="#18181C", top2="#101014", stripe="#F4F1EA",
            legs="#18181C", legs2="#101014", shoe="#0E0C10", shoe2="#0E0C10", watch=True, hstyle="short")

class Env:
    def talk(self, who, T): return 0.0

O_WS = (0, 100, 0); O_JW = (0, 300, 0); O_ST = (0, 500, 0); O_HS = (0, 700, 0); O_BT = (0, 900, 0); O_PK = (0, 1100, 0)

def longhair(P, L):
    hs = 0.56*P.s; t = hs/2; Hm = mat(L["hair"])
    for sx in (-1, 1):
        box(f"{P.n}_lock{sx}", (sx*(t+0.03*P.s), -0.02*P.s, hs*0.25), (0.07*P.s, hs*0.9, hs*1.0), Hm, P.head)
    box(f"{P.n}_lockb", (0, t+0.03*P.s, hs*0.1), (hs+0.1*P.s, 0.07*P.s, hs*1.2), Hm, P.head)

def room(name, O, floor, wall, seed):
    g = group(name, O); B = Batch(name+"_b", g, 1.0)
    B.add((0, 0, -0.05), (20, 20, 0.1), floor); B.add((0, 3.0, 2.0), (20, 0.2, 4.0), wall); B.add((-3.5, 0, 2.0), (0.2, 20, 4.0), wall)
    return g, B

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(27)
    # taller
    W["ws"], B = room("ws", O_WS, tmat("wsfl", "#6A6A6E", 16, 0.08, 271, tiles), tmat("wsw", "#9AA0A8", 16, 0.05, 272, brick), 1)
    B.add((0, 0.6, 0.45), (2.6, 0.9, 0.9), "#5A5A62"); B.add((0, 0.6, 0.92), (2.8, 1.0, 0.06), "#8A6A4A")
    B.add((-0.2, 0.5, 0.96), (0.9, 0.6, 0.02), "#B8BCC4")
    B.add((0, 2.85, 1.8), (3.0, 0.1, 1.4), "#4A4A50")
    for i in range(7): B.add((-1.2+i*0.4, 2.78, 1.9), (0.06, 0.05, 0.5+0.1*(i % 3)), "#C8C8D0")
    B.add((2.8, 1.0, 1.6), (0.2, 0.2, 3.2), "#E0C030"); B.add((-2.4, 1.4, 0.6), (1.0, 1.0, 1.2), "#C0302A")
    B.done()
    W["wscar"] = car("wscar", "#5A8AC8")
    # joyería
    W["jw"], B = room("jw", O_JW, tmat("jwfl", "#3A2A3A", 16, 0.05, 273, tiles), tmat("jww", "#5A3A4A", 16, 0.04, 274, stripes), 2)
    B.add((0, 0.8, 0.5), (3.0, 0.8, 1.0), "#2A1E24"); B.add((0, 0.8, 1.03), (3.1, 0.9, 0.06), "#BFE0F0")
    B.add((0.2, 0.7, 1.1), (0.5, 0.4, 0.06), "#C8C8D0"); B.add((0.2, 0.7, 1.16), (0.36, 0.3, 0.02), "#E8E8EC")
    B.add((-0.6, 0.6, 1.12), (0.3, 0.06, 0.12), "#1C1C22")
    for i in range(5): B.add((-2.4+i*1.2, 2.85, 2.0), (0.8, 0.1, 0.6), "#1C1418")
    B.done()
    # escalera
    W["st"] = g = group("st", O_ST); B = Batch("st_b", g, 1.0)
    for i in range(14): B.add((0, i*0.32, (i+1)*0.1), (1.6, 0.34, (i+1)*0.2), tmat("step", "#B8A890", 16, 0.05, 275, tiles))
    B.add((-0.9, 2.2, 3.0), (0.1, 6, 6), "#D8C8B0"); B.add((0.85, 2.2, 1.0), (0.05, 5.0, 0.06), "#6A4A30")
    B.done()
    # hospital
    W["hs"], B = room("hs", O_HS, tmat("hsfl", "#B8C0C4", 16, 0.04, 276, tiles), tmat("hsw", "#E8F0F0", 16, 0.03, 277, stripes), 3)
    B.add((0, 0.6, 0.35), (1.2, 2.2, 0.5), "#F4F4F0"); B.add((0, 1.6, 0.8), (1.2, 0.1, 0.9), "#A8B0B8")
    B.add((1.3, 1.2, 1.6), (0.7, 0.2, 0.5), "#1C1C22"); B.add((1.3, 1.2, 0.8), (0.06, 0.06, 1.6), "#A8B0B8")
    B.done()
    W["bar"] = box("mbar", (O_HS[0]+1.3, O_HS[1]+1.08, O_HS[2]+1.4), (0.12, 0.03, 0.4), mat(GOLD), None, origin=(0, 0, -0.2))
    W["bar2"] = box("mbar2", (O_HS[0]+1.1, O_HS[1]+1.08, O_HS[2]+1.6), (0.25, 0.03, 0.02), mat("#40E080"))
    # baño
    W["bt"], B = room("bt", O_BT, tmat("btfl", "#D8D8D0", 16, 0.04, 278, tiles), tmat("btw", "#B8D8E0", 16, 0.04, 279, tiles), 4)
    B.add((0, 2.6, 0.45), (1.4, 0.7, 0.9), "#F4F4F0"); B.add((0, 2.85, 1.7), (1.2, 0.05, 1.0), "#C8E0E8")
    B.done()
    # parque
    W["pk"] = g = group("pk", O_PK); B = Batch("pk_b", g, 1.0)
    B.add((0, 0, -0.05), (300, 300, 0.1), tmat("pkg", "#5A9A44", 16, 0.12, 280))
    for i in range(-4, 5): tree(B, i*4.0+1.5, 6.0+(i % 2)*2, 3.4, 270+i)
    B.add((0, 30, 4), (40, 1, 8), "#C8B8A8")
    B.done()
    W["sun"] = box("sunq", (0, 0, 0), (4, 4, 4), mat("#FFB060"))
    W["city"] = City()
    W["newcar"] = car("newcar", "#E0302A"); W["blackcar"] = car("blackcar", "#141418")
    W["cash"] = [box(f"cash{q}", (0, 0, 0), (0.3, 0.14, 0.06), mat("#5AA05A")) for q in range(6)]
    W["bags"] = [box(f"bag{q}", (0, 0, 0), (0.5, 0.25, 0.65), mat(["#C0302A", "#3A6AA8"][q])) for q in range(2)]
    W["case"] = box("brief", (0, 0, 0), (0.45, 0.12, 0.32), mat("#2A1E18"))
    W["phone"] = box("ph27", (0, 0, 0), (0.09, 0.02, 0.17), mat("#1C1C22"))
    W["drop"] = box("drop", (0, 0, 0), (0.05, 0.05, 0.06), mat(GOLD))
    W["dropr"] = box("dropr", (0, 0, 0), (0.05, 0.05, 0.06), mat("#C01818"))
    W["razor"] = box("razor", (0, 0, 0), (0.04, 0.04, 0.2), mat("#3A6AA8"))
    W["ring"] = box("ring", (0, 0, 0), (0.06, 0.06, 0.03), mat(GOLD))
    W["veins"] = []
    W["tomas"] = T_ = Person("tomas", TOMAS)
    for sx in (-1, 1):
        for q in range(3):
            v = box(f"vein{sx}{q}", (0, -0.075, -0.12-q*0.1), (0.025, 0.01, 0.09), mat(GOLD), T_.el[sx]); W["veins"].append(v)
    W["alba"] = A = Person("alba", ALBA, 0.65); longhair(A, ALBA)
    W["jew"] = Person("jew", npc_look(1301))
    W["doc"] = D = Person("doc", DOC); longhair(D, DOC)
    W["suit"] = Person("suit", SUIT)
    camera(28)
    return W

def hide_all(W):
    for k in ("ws", "jw", "st", "hs", "bt", "pk", "wscar", "newcar", "blackcar"): show(W[k], False)
    c = W["city"]; show(c.g, False)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    for o in W["cash"] + W["bags"] + W["veins"] + [W[k] for k in ("case", "phone", "drop", "dropr", "razor", "ring", "bar", "bar2", "sun")]: hid(o, True)
    for k in ("tomas", "alba", "jew", "doc", "suit"): W[k].show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def person(W, key, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0, talk=0.0):
    H = W[key]; H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_, talk=talk)
    return H

def sit(H, z=0.48):
    for sx in (-1, 1): H.leg(sx, 1.5, 1.5)
    H.hips.location.z = z

def indoor(col="#D8D8D0"):
    world_color(col); light_dir((0.45, -0.55, 0.7)); shadow(0.45)

def city(W, night=False):
    c = W["city"]; show(c.g, True)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    world_color("#2A3048" if night else "#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)

def handpos(H, sx=1):
    bpy.context.view_layer.update()
    return H.hand[sx].matrix_world @ Vector((0, 0, -0.08*H.s))

# ------------------------------------------------------------------ planos
@shot(0.0, 7.66)
def d1(W, T, M):
    show(W["ws"], True); indoor("#C8CCD0"); o = O_WS
    cr = W["wscar"]; show(cr, True); cr.location = (o[0]+1.0, o[1]+2.0, 0.9); cr.rotation_euler = (0, 0, 0)
    Tm = person(W, "tomas", o[0]-0.2, o[1]-0.15, 0, T, "neutral" if T < 0.8 else ("shock" if T > 3.0 else "worried"), (0.2, -0.8))
    Tm.chest.rotation_euler = (-0.25, 0, 0)
    Tm.arm(1, fwd=0.9, side=-0.15, elbow=0.9); Tm.arm(-1, fwd=0.9, side=-0.15, elbow=0.9)
    if T > 0.8:
        Tm.arm(1, fwd=1.1, side=-0.3, elbow=1.4)
    d = W["drop"]; hid(d, T < 2.9)
    p = handpos(Tm)
    if T < 3.5: d.location = (p.x, p.y, p.z)
    else:
        k = clamp((T-3.5)/0.9); d.location = (p.x, p.y, lerp(p.z, o[2]+0.98, k*k))
    if T < 2.9:
        look(lerpv((o[0]+0.9, o[1]-2.2, 1.6), (o[0]+0.7, o[1]-1.8, 1.5), eio(clamp(T/2.9))), (o[0]-0.2, o[1]-0.3, 1.2), 26)
    elif T < 5.0:
        look((p.x+0.35, p.y-0.55, p.z+0.05), (p.x, p.y, p.z-0.12), 32, fstop=2.0)
    else:
        look(lerpv((o[0]+0.0, o[1]-0.7, 1.25), (o[0]+0.05, o[1]-0.5, 1.2), eio(clamp((T-5.0)/2.6))), (d.location.x, d.location.y, d.location.z), 36, fstop=2.0)
    M["grade"] = "office"
    if 4.4 < T < 4.48: M["flash"] = 1

@shot(7.66, 14.38)
def d2(W, T, M):
    show(W["jw"], True); indoor("#3A2A34"); o = O_JW
    J = person(W, "jew", o[0], o[1]+1.6, 0, T, "neutral" if T < 10.1 else "shock", (0, -0.7))
    J.arm(1, fwd=1.0, side=-0.1, elbow=0.8)
    Tm = person(W, "tomas", o[0]+0.4, o[1]-0.3, 180, T, "worried", (0, -0.3))
    d = W["drop"]; hid(d, False); d.location = (o[0]+0.2, o[1]+0.7, 1.2)
    if T < 11.4:
        look(lerpv((o[0]-1.4, o[1]-1.2, 1.9), (o[0]-1.1, o[1]-0.7, 1.8), eio(clamp((T-7.66)/3.7))), (o[0]+0.0, o[1]+1.2, 1.4), 24)
    else:
        look(lerpv((o[0]-0.1, o[1]+0.2, 1.45), (o[0]-0.05, o[1]+0.35, 1.4), eio(clamp((T-11.4)/3.0))), (o[0]+0.2, o[1]+0.7, 1.18), 34, fstop=2.0)
    M["grade"] = "cafe"

@shot(14.38, 18.92)
def d3(W, T, M):
    show(W["ws"], True); indoor("#C8CCD0"); o = O_WS
    Tm = person(W, "tomas", o[0]-1.0, o[1]-1.0, 0, T, "shock", (0.4, -0.5))
    Tm.arm(1, fwd=1.3, side=-0.4, elbow=1.2, twist=1.2)
    n = int(clamp((T-15.0)/2.4)*7)
    for q, v in enumerate(W["veins"]):
        if (q // 3 == 1) and (q % 3) < n: hid(v, False)
    look(lerpv((o[0]-0.3, o[1]-3.2, 1.6), (o[0]-0.5, o[1]-2.7, 1.55), eio(clamp((T-14.38)/4.5))), (o[0]-0.9, o[1]-1.0, 1.4), 28, fstop=2.8)
    M["grade"] = "office"

@shot(18.92, 26.84)
def d4(W, T, M):
    if T < 22.0:
        show(W["jw"], True); indoor("#3A2A34"); o = O_JW
        J = person(W, "jew", o[0], o[1]+1.6, 0, T, "happy", (0, -0.4)); J.arm(1, fwd=1.2, side=-0.2, elbow=0.3)
        Tm = person(W, "tomas", o[0]+0.3, o[1]-0.2, 200, T, "smirk", (0, 0))
        n = int(clamp((T-19.4)/2.0)*6)
        for q, c_ in enumerate(W["cash"]):
            if q < n: hid(c_, False); c_.location = (o[0]-0.3+0.32*(q % 3), o[1]+0.75, 1.1+0.07*(q//3))
        look(lerpv((o[0]+1.6, o[1]-1.6, 1.8), (o[0]+1.3, o[1]-1.2, 1.7), eio(clamp((T-18.92)/3.0))), (o[0]+0.1, o[1]+0.8, 1.2), 24)
        M["grade"] = "cafe"
    else:
        city(W)
        nc = W["newcar"]; show(nc, True); nc.location = (3.0, 1.8, 0)
        A = W["alba"]; A.show(True); A.place(2.0, 3.8, 0); A.idle(T); A.face(T, "happy", (0, 0.4), talk=0.6*abs(math.sin(T*8)))
        jump = abs(math.sin((T-22.0)*7))*0.18; A.root.location.z = 0.2+jump
        for sx in (-1, 1): A.arm(sx, fwd=0.4, side=2.4, elbow=0.2)
        Tm = person(W, "tomas", 3.6, 4.0, 0, T, "happy", (-0.5, 0)); Tm.root.location.z = 0.2
        for q, b_ in enumerate(W["bags"]):
            if T > 24.4: hid(b_, False); b_.location = (4.3+q*0.6, 3.8, 0.55)
        look(lerpv((2.2, -1.6, 1.5), (2.6, -1.0, 1.45), eio(clamp((T-22.0)/4.8))), (3.0, 3.0, 1.0), 22)
        M["grade"] = "day"

@shot(26.84, 38.86)
def d5(W, T, M):
    show(W["st"], True); indoor("#D8D0C0"); o = O_ST
    k = clamp((T-26.84)/12.0)
    i = 2+5*k
    y = o[1]+i*0.32; z = o[2]+(int(i)+1)*0.2
    Tm = W["tomas"]; Tm.show(True); Tm.place(o[0]+0.2, y, 180, z); Tm.walk(T*0.45); Tm.face(T, "worried" if T < 33.0 else "sad", (0, -0.2))
    Tm.chest.rotation_euler = (-0.35, 0, 0); Tm.arm(1, fwd=0.6, side=0.6, elbow=0.4)
    sx_, sy_, sz_ = shake(T, 0.01)
    if T < 34.0:
        look((o[0]+0.6+sx_, y-2.6, z+1.6+sz_), (o[0]+0.2, y, z+1.1), 26)
    else:
        look(lerpv((o[0]+1.2, y+1.5, z+1.4), (o[0]+1.0, y+1.2, z+1.35), eio(clamp((T-34.0)/4.8))), (o[0]+0.2, y, z+1.3), 28)
    M["grade"] = "day_sad"

@shot(38.86, 47.92)
def d6(W, T, M):
    city(W, night=True)
    bc = W["blackcar"]; show(bc, True); bc.location = (7.0, 1.8, 0)
    Tm = person(W, "tomas", 3.0, 4.2, 0 if T < 41.3 else 40, T, "worried" if T < 44.8 else "scared", (0.6, 0)); Tm.root.location.z = 0.2
    if 42.8 < T < 44.6:
        Tm.arm(1, fwd=1.3, side=0.3, elbow=2.0); ph = W["phone"]; hid(ph, False); p = handpos(Tm); ph.location = (p.x, p.y, p.z+0.05)
    if T > 44.6:
        Sx = lerp(6.0, 4.2, clamp((T-44.6)/1.4))
        S = W["suit"]; S.show(True); S.place(Sx, 3.8, -80); S.root.location.z = 0.2
        if T < 46.0: S.walk(T*1.0)
        else: S.idle(T)
        S.face(T, "smirk", (-0.5, 0), talk=0.5*abs(math.sin(T*6)) if T > 45.4 else 0)
        S.arm(1, fwd=1.0, side=-0.2, elbow=0.4); c_ = W["case"]; hid(c_, False); p = handpos(S); c_.location = (p.x, p.y, p.z-0.1)
    if T < 41.3:
        look(lerpv((9.0, -3.0, 1.6), (8.4, -2.4, 1.6), eio(clamp((T-38.86)/2.4))), (6.0, 2.4, 1.0), 24)
    elif T < 44.6:
        look(lerpv((3.5, 1.6, 1.85), (3.4, 2.1, 1.8), eio(clamp((T-41.3)/3.3))), (3.0, 4.2, 1.85), 26)
    else:
        look((2.0, 1.2, 1.8), (3.8, 4.0, 1.7), 24)
    M["grade"] = "night"

@shot(47.92, 56.88)
def d7(W, T, M):
    show(W["hs"], True); indoor("#C8D4D8"); o = O_HS
    Tm = person(W, "tomas", o[0], o[1]+0.9, 0, T, "worried" if T < 52.7 else ("neutral" if T < 54.8 else "worried"), (0.6, 0)); sit(Tm, 0.72)
    Dc = person(W, "doc", o[0]+1.6, o[1]+0.0, -60, T, "shock" if T > 50.4 else "neutral", (0.3, 0.3), talk=0.4*abs(math.sin(T*6)) if T > 51.9 else 0)
    b = W["bar"]; hid(b, False); hid(W["bar2"], False)
    h = 1.0
    if T > 52.8: h = lerp(1.0, 0.25, clamp((T-52.8)/1.1))
    if T > 55.4: h = lerp(0.25, 1.1, clamp((T-55.4)/0.8))
    b.scale = (1, 1, h)
    if T < 51.0:
        look(lerpv((o[0]-1.4, o[1]-2.6, 1.9), (o[0]-1.1, o[1]-2.1, 1.85), eio(clamp((T-47.92)/3.1))), (o[0]+0.4, o[1]+0.8, 1.2), 24)
    else:
        look(lerpv((o[0]+0.4, o[1]-0.4, 1.6), (o[0]+0.5, o[1]-0.1, 1.55), eio(clamp((T-51.0)/5.9))), (o[0]+1.3, o[1]+1.2, 1.45), 30, fstop=2.8)
    M["grade"] = "lab"

@shot(56.88, 60.44)
def d8(W, T, M):
    show(W["pk"], True); world_color("#E8B890"); light_dir((0.2, -0.8, 0.35)); shadow(0.5); o = O_PK
    s_ = W["sun"]; hid(s_, False); s_.location = (o[0]-6, o[1]+28, 3.0)
    Tm = person(W, "tomas", o[0], o[1], 0, T, "neutral", (0, 0.3))
    for e in Tm.eyes: e.scale = (1, 1, 0.15)
    Tm.chest.rotation_euler = (0.08*math.sin(T*1.6), 0, 0)
    look(lerpv((o[0]+0.4, o[1]-2.2, 1.55), (o[0]+0.3, o[1]-1.6, 1.6), eio(clamp((T-56.88)/3.6))), (o[0], o[1], 1.55), 26)
    M["grade"] = "dawn"

@shot(60.44, 69.06)
def d9(W, T, M):
    show(W["bt"], True); indoor("#D8E0E0"); o = O_BT
    Tm = person(W, "tomas", o[0], o[1]+1.8, 180, T, "neutral" if T < 62.8 else ("shock" if T < 67.8 else "happy"), (0, 0.0))
    if T > 67.9: Tm.chest.rotation_euler = (0.1*math.sin(T*12), 0, 0)
    Tm.arm(1, fwd=1.4, side=-0.4, elbow=2.0 if T < 63.2 else 1.6)
    rz = W["razor"]
    if T < 63.2: hid(rz, False); p = handpos(Tm); rz.location = (p.x, p.y, p.z+0.1)
    d = W["dropr"]
    if T > 63.8:
        hid(d, False); k = clamp((T-63.8)/0.8); d.location = (o[0]+0.1, o[1]+2.35, lerp(1.4, 0.92, k*k))
    if T < 64.2:
        look(lerpv((o[0]+0.4, o[1]+2.78, 1.7), (o[0]+0.3, o[1]+2.78, 1.68), eio(clamp((T-60.44)/3.8))), (o[0], o[1]+1.8, 1.6), 18)
    elif T < 67.6:
        look((o[0]+0.9, o[1]+2.5, 1.2), (o[0]+0.1, o[1]+2.35, 0.95), 34, fstop=2.0)
    else:
        look((o[0]+0.4, o[1]+2.78, 1.7), (o[0], o[1]+1.8, 1.6), 18)
    M["grade"] = "lab"

@shot(69.06, TOTAL+0.1)
def d10(W, T, M):
    show(W["pk"], True); world_color("#E8B890"); light_dir((0.2, -0.8, 0.35)); shadow(0.5); o = O_PK
    s_ = W["sun"]; hid(s_, False); s_.location = (o[0]-6, o[1]+28, 3.0)
    A = person(W, "alba", o[0]+0.5, o[1], 0, T, "happy", (0, 0.6))
    A.arm(1, fwd=1.1, side=-0.3, elbow=0.6)
    rg = W["ring"]; hid(rg, False); p = handpos(A); rg.location = (p.x, p.y-0.03, p.z+0.03)
    Tm = person(W, "tomas", o[0]-0.4, o[1]+0.2, 20, T, "happy", (0.5, -0.4))
    if T < 72.6:
        look(lerpv((p.x+0.25, p.y-0.6, p.z+0.15), (p.x+0.2, p.y-0.45, p.z+0.12), eio(clamp((T-69.06)/3.5))), (p.x, p.y, p.z), 36, fstop=2.0)
    else:
        look(lerpv((o[0]+0.3, o[1]-2.6, 1.3), (o[0]+0.2, o[1]-2.2, 1.3), eio(clamp((T-72.6)/2.4))), (o[0]+0.05, o[1]+0.1, 1.15), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-74.6)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
