"""Q29 · Mini historia «Un bombero más» (3D de bloques, 76,6 s). Idea de Héctor: ¿y si fueras el único hombre de la Tierra?
Protagonista original: Iván (bombero, uniforme azul marino con bandas amarillas). Su jefa Carmen y la dotación.
Decorados: parque de bomberos (y=100), ciudad (world.City), plató de TV (y=300), pista de aterrizaje y puente (y=500), piso (y=700)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, City, building, tree, tiles, planks, asphalt, stripes, brick, text3d, car

FPS = 24
TOTAL = 76.6
IVAN = dict(skin="#D8A47A", hair="#2A1E18", hair2="#3A2A20", eye="#2A1A10", top="#1E2A44", top2="#18223A", stripe="#F0C030",
            legs="#1E2A44", legs2="#18223A", shoe="#1C1C20", shoe2="#1C1C20", watch=True, hstyle="short")
CARMEN = dict(skin="#C68E62", hair="#2A1E16", hair2="#1C1410", eye="#2A1A10", top="#1E2A44", top2="#18223A", stripe="#F0C030",
              legs="#1E2A44", legs2="#18223A", shoe="#1C1C20", shoe2="#1C1C20", watch=False, hstyle="long")

class Env:
    def talk(self, who, T): return 0.0

O_FS = (0, 100, 0); O_TV = (0, 300, 0); O_RW = (0, 500, 0); O_AP = (0, 700, 0)

def longhair(P, L):
    hs = 0.56*P.s; t = hs/2; Hm = mat(L["hair"])
    for sx in (-1, 1):
        box(f"{P.n}_lock{sx}", (sx*(t+0.03*P.s), -0.02*P.s, hs*0.25), (0.07*P.s, hs*0.9, hs*1.0), Hm, P.head)
    box(f"{P.n}_lockb", (0, t+0.03*P.s, hs*0.1), (hs+0.1*P.s, 0.07*P.s, hs*1.2), Hm, P.head)

def woman(name, seed, uniform=False):
    L = npc_look(seed); L["hstyle"] = "short"
    if uniform: L.update(top="#1E2A44", top2="#18223A", stripe="#F0C030", legs="#1E2A44", legs2="#18223A")
    P = Person(name, L); longhair(P, L); return P

def firetruck(name):
    g = group(name, (0, 0, 0)); B = Batch(name+"_b", g, 1.0)
    B.add((0, 0, 1.3), (6.0, 2.3, 1.9), "#C8201C"); B.add((2.4, 0, 2.5), (1.4, 2.2, 0.6), "#C8201C"); B.add((3.12, 0, 2.0), (0.05, 2.0, 0.8), "#9FD0E8")
    B.add((-0.5, 0, 2.35), (4.5, 1.2, 0.2), "#C8C8D0"); B.add((0, 0, 1.0), (6.05, 2.35, 0.12), "#F4F1EA")
    for x in (-2.0, 2.0):
        for y in (-1.1, 1.1): B.add((x, y, 0.45), (0.9, 0.3, 0.9), "#1C1C20")
    B.add((2.4, -0.6, 2.85), (0.3, 0.3, 0.15), "#3A7AE0"); B.add((2.4, 0.6, 2.85), (0.3, 0.3, 0.15), "#E03030")
    B.done(); return g

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(29)
    # parque de bomberos
    W["fs"] = g = group("fs", O_FS); B = Batch("fs_b", g, 1.0)
    B.add((0, 0, -0.05), (24, 24, 0.1), tmat("fsfl", "#8A8A8A", 16, 0.05, 291, tiles)); B.add((0, 6, 3), (24, 0.2, 6), tmat("fsw", "#B8A898", 16, 0.05, 292, brick))
    B.add((-6, 0, 3), (0.2, 24, 6), "#B8A898")
    for i in range(7):
        x = -5.5+i*0.9; B.add((x, 5.6, 1.0), (0.8, 0.6, 2.0), "#5A6A7A"); B.add((x, 5.25, 2.15), (0.5, 0.4, 0.3), "#E0C030")
        B.add((x, 5.25, 1.2), (0.6, 0.15, 1.0), "#1E2A44")
    B.add((3.0, 5.85, 4.2), (2.0, 0.05, 0.6), "#C8201C")
    B.done()
    W["truck"] = firetruck("ftruck")
    W["alarm"] = box("alarm", (O_FS[0]+3.0, O_FS[1]+5.8, O_FS[2]+4.2), (2.0, 0.05, 0.6), mat("#FF4030"))
    # ciudad
    W["city"] = City()
    W["drones"] = []
    for q in range(5):
        d = group(f"dr{q}", (0, 0, 0)); box(f"drb{q}", (0, 0, 0), (0.4, 0.4, 0.12), mat("#2A2A2E"), d)
        for sx in (-1, 1):
            for sy in (-1, 1): box(f"drr{q}{sx}{sy}", (sx*0.3, sy*0.3, 0.08), (0.25, 0.25, 0.02), mat("#8A8A90"), d)
        box(f"drl{q}", (0, -0.21, 0), (0.06, 0.02, 0.06), mat("#E03030"), d)
        W["drones"].append(d)
    W["fire"] = [box(f"fl{q}", (0, 0, 0), (0.8, 0.5, 0.8), mat(["#FF8A20", "#FFC030", "#E04010"][q % 3])) for q in range(18)]
    W["smoke"] = [box(f"sm{q}", (0, 0, 0), (1.6, 1.6, 1.6), mat("#4A4644")) for q in range(8)]
    # plató
    W["tv"] = g = group("tv", O_TV); B = Batch("tv_b", g, 1.0)
    B.add((0, 0, -0.05), (20, 20, 0.1), "#1C1C24"); B.add((0, 4, 2.5), (12, 0.2, 5), "#2A3A6A")
    B.add((0, 3.85, 2.6), (6, 0.05, 2.8), "#3A6AC8")
    B.add((0, 1.0, 0.4), (2.4, 1.0, 0.8), "#E8E4DA")
    for x in (-1.6, 1.6): B.add((x, 1.0, 0.45), (0.55, 0.55, 0.9), "#C8201C")
    for x in (-3.0, 0.0, 3.0): B.add((x, -4.0, 1.4), (0.5, 0.9, 0.6), "#1C1C20"); B.add((x, -4.0, 0.6), (0.08, 0.08, 1.2), "#3A3A40")
    B.done()
    W["tvtxt"] = text3d("tvtxt", "EL ÚLTIMO HOMBRE", (O_TV[0], O_TV[1]+3.8, O_TV[2]+3.4), 0.42, "#F4F1EA", None, extrude=0.02)
    W["contract"] = box("contract", (O_TV[0]+0.4, O_TV[1]+0.9, O_TV[2]+0.82), (0.3, 0.4, 0.02), mat("#FBFBF6"))
    # pista y puente
    W["rw"] = g = group("rw", O_RW); B = Batch("rw_b", g, 1.0)
    B.add((0, 0, -0.05), (400, 400, 0.1), tmat("grrw", "#6A9A54", 16, 0.10, 293)); B.add((0, 0, 0.0), (300, 14, 0.06), "#4A4A50")
    for x in range(-140, 140, 10): B.add((x, 0, 0.04), (5, 0.4, 0.02), "#F4F1EA")
    for q in range(6): B.add((-30+q*12, 40, 6), (2, 2, 12), "#9A9A9C")
    B.add((0, 40, 12.5), (80, 3, 1), "#A8A8AA")
    B.done()
    W["plane"] = pl = group("plane", (0, 0, 0)); P_ = Batch("pl_b", pl, 1.0)
    P_.add((0, 0, 0), (14, 2.2, 2.2), "#F4F4F6"); P_.add((-0.5, 0, -0.3), (3, 18, 0.3), "#E8E8EC"); P_.add((-6.5, 0, 1.8), (1.6, 0.3, 2.6), "#C8201C")
    P_.add((6.9, 0, 0.3), (0.3, 1.6, 0.6), "#3A4A6A")
    for x in range(-5, 6, 1): P_.add((x, -1.11, 0.3), (0.3, 0.02, 0.3), "#3A4A6A")
    P_.done()
    # piso
    W["ap"] = g = group("ap", O_AP); B = Batch("ap_b", g, 1.0)
    B.add((0, 0, -0.05), (12, 12, 0.1), tmat("apfl", "#A07A50", 16, 0.1, 294, planks)); B.add((0, 3, 2), (12, 0.2, 4), "#D8C8B0")
    B.add((0, 2.92, 1.8), (2.4, 0.05, 1.8), "#2A3450"); B.add((-1.8, 1.8, 0.4), (2.0, 0.9, 0.8), "#6A4A6A")
    B.add((2.0, 2.6, 0.8), (0.9, 0.5, 1.6), "#8A6A4A"); B.add((2.0, 2.33, 1.7), (0.4, 0.05, 0.3), "#F4F1EA")
    B.done()
    W["ivan"] = Person("ivan", IVAN)
    W["carmen"] = C = Person("carmen", CARMEN); longhair(C, CARMEN)
    W["crew"] = [woman(f"crew{q}", 1500+q, uniform=True) for q in range(3)]
    W["women"] = [woman(f"wm{q}", 1600+q) for q in range(8)]
    W["helmet"] = box("helmet", (0, 0, 0), (0.42, 0.45, 0.25), mat("#F0C030"))
    W["ihelm"] = box("ihelm", (0, 0, 0.62), (0.62, 0.62, 0.14), mat("#F0C030"), W["ivan"].head)
    W["chelm"] = box("chelm", (0, 0, 0.62), (0.62, 0.62, 0.14), mat("#F4F1EA"), W["carmen"].head)
    W["mhelm"] = [box(f"mh{q}", (0, 0, 0.62), (0.62, 0.62, 0.14), mat("#F0C030"), W["crew"][q].head) for q in range(3)]
    camera(28)
    return W

def hide_all(W):
    for k in ("fs", "truck", "tv", "rw", "plane", "ap"): show(W[k], False)
    c = W["city"]; show(c.g, False)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    for d in W["drones"]: show(d, False)
    for o in W["fire"] + W["smoke"] + W["mhelm"] + [W[k] for k in ("alarm", "tvtxt", "contract", "helmet", "ihelm", "chelm")]: hid(o, True)
    for p in W["crew"] + W["women"] + [W["ivan"], W["carmen"]]: p.show(False)
    W["_helm"] = set()

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def person(W, H, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0, talk=0.0):
    H = W[H] if isinstance(H, str) else H
    H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_, talk=talk)
    return H

def sit(H, z=0.48):
    for sx in (-1, 1): H.leg(sx, 1.5, 1.5)
    H.hips.location.z = z

def station(W, night=False, alarm=False, T=0.0):
    show(W["fs"], True); world_color("#1A1A28" if night else "#C8C8C8"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    tr = W["truck"]; show(tr, True); tr.location = (O_FS[0]+1.0, O_FS[1]+1.5, 0); tr.rotation_euler = (0, 0, 0)
    if alarm: hid(W["alarm"], (T*3) % 1 > 0.5)

def city(W, night=False):
    c = W["city"]; show(c.g, True)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    world_color("#141828" if night else "#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)

# ------------------------------------------------------------------ planos
@shot(0.0, 8.64)
def f1(W, T, M):
    station(W, alarm=True, T=T); o = O_FS
    I = W["ivan"]; I.show(True)
    if T < 3.4:
        f = clamp(T/3.0); I.place(o[0]-3.0+2.0*f, o[1]-2.0, 90); I.walk(T*2.0, run=True); I.face(T, "worried", (0.5, 0))
        look(lerpv((o[0]+1.5, o[1]-6.0, 1.8), (o[0]+1.0, o[1]-5.0, 1.7), eio(f)), (o[0]-1.6, o[1]-2.0, 1.4), 24)
    else:
        I.place(o[0]-1.0, o[1]-2.0, 160); I.idle(T); I.face(T, "shock" if T > 5.5 else "worried", (0.7*math.sin(T*1.4), 0.2))
        I.head.rotation_euler = (0, 0, 0.5*math.sin(T*1.2))
        if T < 6.8:
            look(lerpv((o[0]-1.4, o[1]-4.2, 1.7), (o[0]-1.2, o[1]-3.6, 1.7), eio(clamp((T-3.4)/3.4))), (o[0]-1.0, o[1]-2.0, 1.65), 26)
        else:
            look(lerpv((o[0]-3.6, o[1]+1.4, 1.8), (o[0]-3.4, o[1]+2.0, 1.75), eio(clamp((T-6.8)/1.8))), (o[0]-3.4, o[1]+5.6, 1.6), 26)
    M["grade"] = "alarm"

@shot(8.64, 14.96)
def f2(W, T, M):
    city(W)
    I = person(W, "ivan", 3.0, 4.0, 0, T, "shock", (0.8*math.sin(T), 0.1)); I.root.location.z = 0.2
    for q in range(6):
        P = W["women"][q]; P.show(True); x = -2+q*1.8+((T*0.5) % 1.0 if q % 2 else 0); P.place(x, 4.6 if q % 2 else -4.6, 90 if q % 2 else -90, 0.2)
        P.walk(T*1.1+q); P.face(T, "worried", (0, 0))
    look(lerpv((3.8, -3.0, 2.6), (3.4, -1.2, 2.0), eio(clamp((T-8.64)/6.3))), (3.0, 3.4, 1.6), 24)
    M["grade"] = "day_sad"

@shot(14.96, 22.76)
def f3(W, T, M):
    city(W)
    I = person(W, "ivan", 3.0, 4.0, 0, T, "worried" if T < 20.0 else "shock", (0, 0.6 if T > 20 else -0.4)); I.root.location.z = 0.2
    I.arm(1, fwd=1.2, side=0.1, elbow=1.4)
    for q in range(5):
        P = W["women"][q]; P.show(True); P.place(1.0+q*1.0, 1.6+0.3*(q % 2), 0, 0.0); P.idle(T+q); P.face(T, "neutral", (0, 0.2))
        P.arm(1, fwd=1.4, side=0.0, elbow=0.6)
    for q, d in enumerate(W["drones"]):
        on = T > 20.0
        show(d, on); d.location = (1.6+q*0.8, 3.0+0.3*math.sin(T+q), 3.2+0.3*math.sin(T*2+q)); d.rotation_euler = (0, 0, T*0.2)
    if T < 20.0:
        look(lerpv((3.8, -1.4, 1.8), (3.5, -0.6, 1.8), eio(clamp((T-14.96)/5.0))), (3.0, 4.0, 1.6), 24)
    else:
        look(lerpv((6.0, -0.4, 1.5), (5.6, 0.0, 1.6), eio(clamp((T-20.0)/2.8))), (2.8, 3.4, 2.8), 24)
    M["grade"] = "day"

@shot(22.76, 30.5)
def f4(W, T, M):
    show(W["tv"], True); world_color("#141420"); light_dir((0.3, -0.7, 0.6)); shadow(0.4); o = O_TV
    hid(W["tvtxt"], False); hid(W["contract"], T < 25.2)
    I = person(W, "ivan", o[0]-1.6, o[1]+1.0, 0, T, "worried", (0.6, 0)); sit(I, 0.9)
    H = W["women"][6]; person(W, H, o[0]+1.6, o[1]+1.0, 0, T, "happy", (-0.6, 0), talk=0.6*abs(math.sin(T*7))); sit(H, 0.9)
    H.arm(-1, fwd=1.0, side=-0.4, elbow=0.4)
    if T < 27.4:
        look(lerpv((o[0], o[1]-5.6, 2.0), (o[0], o[1]-4.6, 1.9), eio(clamp((T-22.76)/4.6))), (o[0], o[1]+1.6, 1.6), 24)
    else:
        look(lerpv((o[0]-1.2, o[1]-1.4, 1.6), (o[0]-1.3, o[1]-1.0, 1.6), eio(clamp((T-27.4)/3.1))), (o[0]-1.6, o[1]+1.0, 1.55), 28)
    M["grade"] = "night"; M["flash"] = 1 if (T % 1.7) < 0.05 else 0

@shot(30.5, 39.8)
def f5(W, T, M):
    show(W["rw"], True); world_color("#B8D0E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.4); o = O_RW
    if T < 34.8:
        k = clamp((T-30.5)/4.3)
        pl = W["plane"]; show(pl, True); pl.location = (o[0]+lerp(-60, 10, k), o[1], o[2]+max(1.4, lerp(12, 1.4, k*1.4))); pl.rotation_euler = (0, -0.08*(1-k), 0)
        look(lerpv((o[0]-4, o[1]-22, 3.0), (o[0]-2, o[1]-20, 2.4), eio(k)), (o[0]+lerp(-40, 8, k), o[1], o[2]+3), 24)
    else:
        for q in range(3):
            P = W["women"][q+3]; P.show(True); P.place(o[0]-4+q*2.2, o[1]+38.4, 180*0+0, o[2]+13.0); P.idle(T+q); P.face(T, "happy", (0, 0))
            P.arm(1, fwd=1.2, side=0, elbow=0.8+0.6*math.sin(T*6+q))
        look(lerpv((o[0]-1, o[1]+33, 14.0), (o[0]-1.5, o[1]+34, 14.2), eio(clamp((T-34.8)/5.0))), (o[0]-2, o[1]+38.4, 14.0), 24)
    M["grade"] = "day"

@shot(39.8, 50.58)
def f6(W, T, M):
    show(W["ap"], True); world_color("#2A2A3A"); light_dir((0.45, -0.55, 0.7)); shadow(0.4); o = O_AP
    I = person(W, "ivan", o[0]-1.8, o[1]+1.6, 0, T, "sad", (0.2, -0.2)); sit(I, 0.8)
    I.arm(1, fwd=0.6, side=0.1, elbow=1.2); I.arm(-1, fwd=0.6, side=0.1, elbow=1.2)
    I.chest.rotation_euler = (-0.25, 0, 0)
    for q in range(2):
        G = W["women"][q+6]; G.show(True); G.place(o[0]+2.6+q*0.7, o[1]-1.0, -30, 0); G.idle(T); G.face(T, "neutral", (0, 0))
    if T < 44.0:
        look(lerpv((o[0]+3.4, o[1]-3.0, 1.8), (o[0]+3.0, o[1]-2.4, 1.8), eio(clamp((T-39.8)/4.2))), (o[0]-1.0, o[1]+1.4, 1.2), 24)
    else:
        look(lerpv((o[0]-1.4, o[1]-0.6, 1.4), (o[0]-1.5, o[1]-0.2, 1.4), eio(clamp((T-44.0)/6.6))), (o[0]-1.8, o[1]+1.6, 1.3), 28, fstop=2.8)
    M["grade"] = "night"

def burning(W, T, x0=12.0):
    for q, f in enumerate(W["fire"]):
        hid(f, False); fl = 0.8+0.3*math.sin(T*9+q*1.7)
        f.location = (x0-2.0+(q % 6)*0.8, 6.2, 2.0+(q//6)*2.6+0.2*math.sin(T*7+q)); f.scale = (fl, 1, fl)
    for q, s in enumerate(W["smoke"]):
        hid(s, False); z = 8+((T*1.2+q*1.3) % 9); s.location = (x0-1+0.6*math.sin(q+T*0.4), 6.4, z); s.scale = (1+z*0.05,)*3

@shot(50.58, 60.94)
def f7(W, T, M):
    if T < 53.6:
        station(W, night=True, alarm=True, T=T); o = O_FS
        I = person(W, "ivan", o[0]-2.2, o[1]-2.0, 160 if T < 52.0 else 90, T, "shock", (0, 0.4))
        look(lerpv((o[0]-1.4, o[1]-5.0, 1.8), (o[0]-1.6, o[1]-4.2, 1.8), eio(clamp((T-50.58)/3.0))), (o[0]-2.2, o[1]-2.0, 1.6), 26)
        M["grade"] = "alarm"
    elif T < 56.5:
        city(W, night=True); burning(W, T)
        look(lerpv((10.0, -2.2, 1.8), (10.4, -1.6, 2.4), eio(clamp((T-53.6)/2.9))), (12.0, 6.0, 4.5), 24)
        M["grade"] = "night"
    else:
        station(W, night=True, alarm=True, T=T); o = O_FS
        I = person(W, "ivan", o[0]-2.2, o[1]-2.0, 90, T, "worried", (0.8, 0))
        C = person(W, "carmen", o[0]-0.4, o[1]-2.2, -90, T, "angry", (-0.8, 0), talk=0.6*abs(math.sin(T*8)) if T > 58.9 else 0); W["_helm"].add("chelm")
        hm = W["helmet"]; hid(hm, False)
        k = clamp((T-57.9)/0.6)
        if T < 57.9: C.arm(1, fwd=1.2, side=0.3, elbow=0.8); p = (o[0]-0.6, o[1]-2.5, 1.35)
        else: C.arm(1, fwd=1.4, side=0.0, elbow=0.1); p = lerpv((o[0]-0.6, o[1]-2.5, 1.35), (o[0]-1.9, o[1]-2.25, 1.25), k)
        hm.location = p; hm.rotation_euler = (k*6, 0, 0)
        if T > 58.5: I.arm(-1, fwd=1.3, side=0.2, elbow=0.9); I.arm(1, fwd=1.3, side=0.2, elbow=0.9)
        look(lerpv((o[0]-1.3, o[1]-5.6, 1.7), (o[0]-1.3, o[1]-4.8, 1.7), eio(clamp((T-56.5)/4.4))), (o[0]-1.3, o[1]-2.1, 1.5), 24)
        M["grade"] = "alarm"

@shot(60.94, 67.78)
def f8(W, T, M):
    city(W, night=True); burning(W, T, 16.0)
    tr = W["truck"]; show(tr, True); tr.location = (lerp(-10, 9.0, eio(clamp((T-60.94)/2.0))), 1.4, 0); tr.rotation_euler = (0, 0, 0)
    if T < 63.4:
        look(lerpv((2.0, -4.6, 1.6), (3.0, -4.0, 1.7), eio(clamp((T-60.94)/2.4))), (tr.location.x, 1.4, 1.4), 24)
    else:
        I = person(W, "ivan", 15.2, 3.6, 0, T, "angry" if T < 66.0 else "happy", (0, 0.5)); I.root.location.z = 0.2; W["_helm"].add("ihelm")
        I.arm(1, fwd=1.4, side=0.1, elbow=0.4); I.arm(-1, fwd=1.4, side=-0.1, elbow=0.6)
        for q in range(3):
            P = W["crew"][q]; person(W, P, 16.2+q*0.8, 3.4, 0, T, "angry", (0, 0.5)); P.root.location.z = 0.2; W["_helm"].add(q)
            P.arm(1, fwd=1.4, side=0.1, elbow=0.4)
        C = person(W, "carmen", 14.3, 3.4, 0, T, "happy" if T > 66.0 else "angry", (0.4, 0)); C.root.location.z = 0.2; W["_helm"].add("chelm")
        sx_, sy_, sz_ = shake(T, 0.02)
        look(lerpv((15.8, -0.8+sx_, 1.5), (15.7, -0.2, 1.55+sz_), eio(clamp((T-63.4)/4.4))), (15.8, 4.0, 1.9), 22)
    M["grade"] = "night"

@shot(67.78, 72.28)
def f9(W, T, M):
    station(W); o = O_FS
    world_color("#E8B890")
    I = person(W, "ivan", o[0]-2.0, o[1]-2.6, 0, T, "happy", (0, 0.1))
    I.arm(1, fwd=1.2, side=-0.1, elbow=1.0)
    hm = W["helmet"]; hid(hm, False); bpy.context.view_layer.update(); p = I.hand[1].matrix_world @ Vector((0, 0, -0.1)); hm.location = p
    for q in range(3):
        P = W["crew"][q]; person(W, P, o[0]-0.6+q*0.8, o[1]-2.0, -20, T, "happy", (-0.5, 0), talk=0.5*abs(math.sin(T*6+q)) if q == 1 else 0)
    look(lerpv((o[0]-0.6, o[1]-6.4, 1.6), (o[0]-0.7, o[1]-5.6, 1.6), eio(clamp((T-67.78)/4.5))), (o[0]-0.8, o[1]-2.2, 1.45), 24)
    M["grade"] = "dawn"

@shot(72.28, TOTAL+0.1)
def f10(W, T, M):
    station(W); o = O_FS; world_color("#E8B890")
    I = person(W, "ivan", o[0]-2.0, o[1]-2.6, 0, T, "smirk", (0, 0.1))
    look(lerpv((o[0]-1.65, o[1]-4.6, 1.75), (o[0]-1.7, o[1]-4.0, 1.72), eio(clamp((T-72.28)/4.3))), (o[0]-2.0, o[1]-2.6, 1.7), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-76.2)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    hid(W["ihelm"], "ihelm" not in W["_helm"]); hid(W["chelm"], "chelm" not in W["_helm"])
    for q in range(3): hid(W["mhelm"][q], q not in W["_helm"])
    apply_vis()
    return M
