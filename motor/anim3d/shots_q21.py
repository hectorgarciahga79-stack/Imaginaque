"""Q21 · Mini historia «El euro que se duplicaba cada hora» (3D de bloques, 76,99 s).
Voz única del narrador (Juanjo Viral). Tiempos de plano = timeline de align.py.
Protagonista: Álex (sudadera amarilla, el mismo diseño original de Q13). Decorados propios: piso de Álex (origen), nave industrial
(y=200, dentro y fuera), calle con concesionario y ático (y=400), espacio con la Tierra (y=600)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, building, tree, tiles, planks, brick, asphalt, stripes, text3d, car

FPS = 24
TOTAL = 76.99
ALEX = dict(skin="#D9A57A", hair="#2A1C14", hair2="#3A2A1E", eye="#2A1A10", top="#F2B820", top2="#C8901A", stripe="#2A2A2E",
            legs="#2E3A52", legs2="#243046", shoe="#F4F1EA", shoe2="#C0302A", watch=False, hstyle="short")
COP = dict(skin="#C8946A", hair="#1C1410", hair2="#1C1410", eye="#2A1A10", top="#1E2A4A", top2="#16203A", stripe="#F4D040",
           legs="#1E2A4A", legs2="#16203A", shoe="#141216", shoe2="#141216", watch=False, hstyle="cap")
GOLD = "#F2C230"

class Env:
    def talk(self, who, T): return 0.0

O_A = (0, 0, 0); O_N = (0, 200, 0); O_S = (0, 400, 0); O_E = (0, 600, 0)

def fmt(n):
    return f"{int(n):,}".replace(",", ".") + " €"

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(21)
    coin = tmat("coins", GOLD, 16, 0.18, 71, stripes)
    W["coinmat"] = coin
    # ---------------- piso ----------------
    W["flat"] = g = group("flat", O_A)
    B = Batch("fl_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("floor", "#A87A50", 16, 0.07, 72, planks))
    B.add((0, 3.2, 1.6), (14, 0.2, 3.2), tmat("wall", "#7A6AA8", 16, 0.04, 73)); B.add((-4.0, 0, 1.6), (0.2, 12, 3.2), tmat("wall2", "#6A5A98", 16, 0.04, 74))
    B.add((0.4, 1.2, 0.75), (2.4, 1.2, 0.08), "#8A5A36")
    for x in (-0.7, 1.5):
        for y in (0.7, 1.7): B.add((x, y, 0.36), (0.1, 0.1, 0.72), "#6A4A30")
    B.add((-2.4, 1.6, 0.4), (2.0, 0.9, 0.8), "#C0503A"); B.add((-2.4, 2.0, 0.9), (2.0, 0.3, 0.8), "#A8402E")
    B.add((2.6, 3.08, 1.9), (1.6, 0.06, 1.3), "#2A3A5A")
    B.done()
    W["curtain"] = box("curtain", (2.6, 3.0, 1.9), (0.1, 0.06, 1.4), mat("#C8B898"), origin=(-0.5, 0, 0))
    W["c1"] = box("coinA", (0.4, 1.2, 0.81), (0.16, 0.16, 0.04), mat(GOLD))
    W["c2"] = box("coinB", (0.65, 1.2, 0.81), (0.16, 0.16, 0.04), mat(GOLD))
    W["floorcoins"] = [box(f"fc{q}", (r.uniform(-3, 3), r.uniform(-2.5, 2.8), 0.02), (0.16, 0.16, 0.04), mat(GOLD), rot=(0, 0, r.uniform(0, 3))) for q in range(90)]
    W["pile"] = box("pile", (0.9, 0.3, 0), (1.0, 1.0, 1.0), coin, origin=(0, 0, -0.5))
    W["sea"] = box("seaflat", (0, 0, 0), (7.8, 6.2, 1.0), coin, origin=(0, 0, -0.5))
    W["cracks"] = [box(f"ck{q}", (0, 0, 0), (0.9, 0.06, 0.03), mat("#2A1A10")) for q in range(10)]
    W["lamp"] = lp = group("lamp", (0.2, 0.8, 3.2))
    L = Batch("lamp_b", lp, 1.0); L.add((0, 0, -0.4), (0.02, 0.02, 0.8), "#2A2A2E"); L.add((0, 0, -0.85), (0.4, 0.4, 0.2), "#FFE7A0"); L.done()
    W["phones"] = [box(f"ph{q}", (0, 0, 0), (0.2, 0.36, 0.04), mat("#1C1C22")) for q in range(2)]
    W["phlab"] = [text3d(f"phl{q}", t, (0, 0, 0), 0.12, "#40E0FF", None, rot=(0, 0, 0), extrude=0.01) for q, t in enumerate(("BANCO", "HACIENDA"))]
    W["counter"] = text3d("counter", "1 €", (0, 3.05, 2.4), 0.36, GOLD, None, extrude=0.05)
    # ---------------- nave ----------------
    W["nave"] = g = group("nave", O_N)
    B = Batch("nv_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("asphn", "#4A4A50", 16, 0.05, 75, asphalt))
    B.add((0, 14, 5.0), (24, 0.3, 10), tmat("navew", "#8A9AA8", 16, 0.05, 76, stripes)); B.add((-12, 4, 5.0), (0.3, 20, 10), tmat("navew", "#8A9AA8", 16, 0.05, 76, stripes)); B.add((12, 4, 5.0), (0.3, 20, 10), tmat("navew", "#8A9AA8", 16, 0.05, 76, stripes))
    B.add((-7.5, -6, 5.0), (9, 0.3, 10), tmat("navew", "#8A9AA8", 16, 0.05, 76, stripes)); B.add((7.5, -6, 5.0), (9, 0.3, 10), tmat("navew", "#8A9AA8", 16, 0.05, 76, stripes)); B.add((0, -6, 8.0), (6, 0.3, 4), tmat("navew", "#8A9AA8", 16, 0.05, 76, stripes))
    for k in range(-3, 4): building(B, k*14.0, -26, 12, 8, 2+k % 2, ["#C8C0B0", "#B8B0A0"][k % 2], 980+k, 1)
    B.done()
    W["roof"] = box("roof", (O_N[0], O_N[1]+4, 10.15), (24.4, 20.4, 0.3), mat("#6A7A88"))
    W["door"] = box("door", (O_N[0], O_N[1]-6.0, 3.0), (6.0, 0.2, 6.0), mat("#5A6A78"))
    W["mount"] = box("mount", (O_N[0], O_N[1]+5, 0), (1.0, 1.0, 1.0), coin, origin=(0, 0, -0.5))
    W["spill"] = [box(f"sp{q}", (0, 0, 0), (0.5, 0.5, 0.5), coin) for q in range(30)]
    W["truck"] = tr = group("truck", (0, 0, 0))
    T_ = Batch("truck_b", tr, 1.0)
    T_.add((0, 0, 2.0), (2.6, 7.0, 2.8), "#E8E4DA"); T_.add((0, -4.6, 1.6), (2.5, 2.2, 2.4), "#3A6AA8"); T_.add((0, -5.72, 2.1), (2.2, 0.06, 0.9), "#9FD0E8")
    T_.add((0, 0, 0.5), (2.2, 9.0, 0.3), "#2A2A2E")
    for y in (-4.4, 1.5, 3.0):
        for x in (-1.15, 1.15): T_.add((x, y, 0.5), (0.4, 1.0, 1.0), "#1C1C20")
    T_.done()
    W["lights"] = [box(f"pl{q}", (0, 0, 0), (0.7, 0.3, 0.4), mat("#E0302A" if q % 2 else "#3060FF")) for q in range(2)]
    # ---------------- calle de los caprichos ----------------
    W["street"] = g = group("street", O_S)
    B = Batch("st_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("grass", "#5A9A44", 16, 0.10, 77))
    B.add((0, 0, 0.0), (300, 8, 0.06), tmat("road", "#4A4A50", 16, 0.05, 78, asphalt))
    cols = ["#E8D8B8", "#F0E6D0", "#D8C8A8", "#C8D8E0"]
    for k in range(-6, 7): building(B, k*11.0, 11.5, 10, 8, 3+k % 4, cols[k % 4], 990+k, -1); tree(B, k*11.0+5.5, 6.6, 3.0, k)
    B.add((22, 9, 15), (10, 8, 30), "#E8ECF0")
    for k in range(9): B.add((22, 4.96, 2+k*3.2), (10.2, 0.05, 0.4), "#9FD0E8")
    B.add((22, 6.5, 30.3), (10.4, 5, 0.4), "#C8C0B0"); B.add((22, 4.2, 30.9), (10.4, 0.1, 1.0), "#9FD0E8")
    B.done()
    W["car1"] = car("supercar", "#D8302A"); W["car2"] = car("supercar2", "#2A2A30")
    W["bow"] = box("bow", (0, 0, 0), (0.6, 0.2, 0.4), mat("#F2C230"))
    # ---------------- espacio ----------------
    W["space"] = g = group("space", O_E)
    W["globe"] = gl = group("globe", (2.2, 0, 0), g)
    B = Batch("globe_b", gl, 1.0)
    R = 3.0; st = 0.45; n = int(R/st)+1
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            for k in range(-n, n+1):
                p = Vector((i, j, k))*st; d = p.length
                if not (R-st*0.95 < d <= R): continue
                u = p.normalized()
                v = math.sin(u.x*2.3+1.3)*math.cos(u.y*1.9-0.4) + 0.7*math.sin(u.z*3.0+u.x*1.7+u.y*2.2) + 0.5*math.cos(u.y*3.3-u.z*1.1)
                col = "#EEF4F8" if abs(u.z) > 0.88 else ("#5A9A44" if v > -0.05 else "#2E6EB8")
                B.add(tuple(p), (st, st, st), col)
    B.done()
    S = Batch("stars_b", g, 1.0)
    for q in range(160): S.add((r.uniform(-60, 60), r.uniform(25, 40), r.uniform(-60, 60)), (0.12, 0.12, 0.12), "#FFFFFF")
    S.done()
    W["scube"] = box("scube", (O_E[0]-2.2, O_E[1], 0), (1.0, 1.0, 1.0), coin)
    W["alex"] = Person("alex", ALEX)
    W["cops"] = [Person(f"cop{q}", COP, 1.02) for q in range(2)]
    camera(28)
    return W

def hide_all(W):
    for k in ("flat", "lamp", "nave", "truck", "street", "space"): show(W[k], False)
    for k in ("curtain", "c1", "c2", "pile", "sea", "counter", "roof", "door", "mount", "bow", "scube"): hid(W[k], True)
    for lst in ("floorcoins", "cracks", "phones", "phlab", "spill", "lights"):
        for o in W[lst]: hid(o, True)
    for k in ("car1", "car2"): show(W[k], False)
    W["alex"].show(False)
    for c in W["cops"]: c.show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def settext(o, s):
    if o.data.body != s: o.data.body = s
    hid(o, False)

def flat(W, night=False):
    show(W["flat"], True); show(W["lamp"], True)
    world_color("#1C2238" if night else "#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    W["counter"].location = (0, 3.05, 2.4); W["counter"].scale = (1, 1, 1)

def alex(W, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    H = W["alex"]; H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_)
    return H

def hand_pos(H, sx=1, off=(0, -0.06, -0.12)):
    bpy.context.view_layer.update()
    return H.hand[sx].matrix_world @ Vector(off)

def police(W, T, base):
    for q, l in enumerate(W["lights"]):
        on = (math.sin(T*9) > 0) == (q == 0)
        hid(l, not on); l.location = base[q]

# ------------------------------------------------------------------ planos
@shot(0.0, 7.46)
def c1(W, T, M):
    show(W["nave"], True); hid(W["roof"], False); hid(W["door"], False)
    world_color("#0A0E18"); light_dir((0.3, -0.6, 0.75)); shadow(0.35)
    k = T/7.46
    mt = W["mount"]; hid(mt, False); mt.scale = (12, 8, 6); mt.location = (O_N[0], O_N[1]+7, 0)
    knock = (T % 0.8) < 0.12 and T > 4.5
    W["door"].location = (O_N[0], O_N[1]-6.0+(0.05 if knock else 0), 3.0)
    police(W, T, [(O_N[0]-1.5, O_N[1]-6.3, 6.4), (O_N[0]+1.5, O_N[1]-6.3, 6.4)])
    H = alex(W, O_N[0]+0.6, O_N[1]-1.5, 180 if T < 4.6 else 160, T, "smirk" if T < 4.5 else "shock", (0, 0.5 if T < 4.5 else -0.2))
    if T > 4.6: H.place(O_N[0]+0.6, O_N[1]-1.5, 10); H.face(T, "shock", (0, 0))
    sx_, sy_, sz_ = shake(T, 0.04 if knock else 0.0)
    if T < 4.5:
        look(lerpv((O_N[0]+2.2, O_N[1]-5.5, 1.3), (O_N[0]+1.6, O_N[1]-5.0, 1.6), eio(clamp(T/4.5))), (O_N[0]+0.3, O_N[1]+5.0, lerp(2.5, 4.5, eio(clamp(T/4.5)))), 24)
    else:
        look((O_N[0]+1.3+sx_, O_N[1]-4.0+sy_, 1.7+sz_), (O_N[0]+0.6, O_N[1]-1.5, 1.6), 30, fstop=3.0)
    M["grade"] = "night"; M["alarm"] = 1 if T > 4.5 else 0

@shot(7.46, 13.9)
def c2(W, T, M):
    flat(W); k = (T-7.46)/6.44
    H = alex(W, -0.5, 0.6, 15, T, "neutral" if T < 11.0 else "shock", (0.5, -0.4))
    hid(W["c1"], False)
    if T < 9.6:
        H.arm(1, fwd=0.4, side=0.2, elbow=1.6); c = W["c1"]; c.location = tuple(hand_pos(H)); c.rotation_euler = (0.3, 0, 0)
    else:
        W["c1"].location = (0.4, 1.2, 0.81); W["c1"].rotation_euler = (0, 0, 0)
    if T > 11.0:
        f = eio(clamp((T-11.0)/0.3)); hid(W["c2"], False); W["c2"].location = (lerp(0.4, 0.65, f), 1.2, 0.81+0.12*math.sin(f*math.pi))
    if 11.0 < T < 11.06: M["flash"] = 1
    look(lerpv((1.2, -1.2, 1.6), (0.9, -0.4, 1.45), eio(k)), (0.4, 1.2, 0.95), lerp(26, 34, k), fstop=2.8)
    M["grade"] = "dawn"

@shot(13.9, 20.54)
def c3(W, T, M):
    flat(W, night=T > 17.0); k = (T-13.9)/6.64
    n = int(90*clamp((T-14.0)/5.5))
    for q, c in enumerate(W["floorcoins"]): hid(c, q >= n)
    settext(W["counter"], fmt(2**int(lerp(2, 10, clamp((T-14.0)/5.5)))))
    H = W["alex"]; H.show(True); H.place(0.0, 0.0, 0); H.idle(T); H.face(T, "worried" if T < 16 else "shock", (0.0, -0.6))
    H.leg(-1, 1.5, 1.5); H.leg(1, 1.5, 1.5); H.hips.location.z = 0.32
    H.arm(1, fwd=1.2, side=0.1, elbow=0.6+0.4*math.sin(T*6)); H.arm(-1, fwd=0.9, side=0.3, elbow=0.4)
    look(lerpv((0.4, -3.6, 2.6), (0.2, -2.6, 2.0), eio(k)), (0.0, 0.4, 0.6), 24)
    M["grade"] = "dawn" if T < 17.0 else "night"

@shot(20.54, 27.02)
def c4(W, T, M):
    flat(W, night=True); k = (T-20.54)/6.48
    for c in W["floorcoins"]: hid(c, False)
    pl = W["pile"]; hid(pl, False)
    step = int((T-20.54)/1.2); f = clamp(((T-20.54) % 1.2)/0.25)
    s = 0.35*2**((step+f)/3); pl.scale = (s, s, s*0.6)
    cu = W["curtain"]; hid(cu, False); cl = eio(clamp((T-24.6)/1.0)); cu.scale = (lerp(0.1, 18.0, cl), 1, 1)
    H = alex(W, 1.8, 1.6, 40 if T < 24.4 else -30, T, "shock" if T < 24.4 else "smirk", (0.4, -0.3))
    if T > 24.4: H.arm(1, fwd=1.8, side=0.3, elbow=0.2)
    if (T-20.54) % 1.2 < 0.06: M["flash"] = 1
    look(lerpv((-2.0, -2.6, 1.9), (-1.4, -2.0, 1.8), eio(k)), (1.4, 1.4, 1.3), 24)
    M["grade"] = "night"

@shot(27.02, 34.62)
def c5(W, T, M):
    flat(W, night=True); k = (T-27.02)/7.6
    sea = W["sea"]; hid(sea, False); sea.location = (0, 0.2, 0); sea.scale = (1, 1, lerp(0.2, 1.05, eio(clamp((T-27.1)/3.0))))
    settext(W["counter"], fmt(2**20))
    W["lamp"].rotation_euler = (0.25*math.sin(T*2.2)*clamp((T-32.0)/1.0), 0, 0)
    for q, c in enumerate(W["cracks"]):
        if q/10 > clamp((T-32.1)/1.4): continue
        hid(c, False); c.location = (-3.9+0.02, -2.0+q*0.5, 0.4+0.25*math.sin(q*1.7)); c.rotation_euler = (0.6*math.sin(q), 0, 0); c.scale = (0.05, 1, 1)
    H = alex(W, 0.6, -0.6, 0, T, "happy" if T < 31.8 else "scared", (0.2, -0.5 if T > 32 else 0.4), z=lerp(0.0, 0.5, eio(clamp((T-27.1)/3.0))))
    if T < 31.8:
        for sx in (-1, 1): H.arm(sx, fwd=2.6, side=0.4, elbow=0.4)
    sx_, sy_, sz_ = shake(T, 0.03 if T > 32.1 else 0.0)
    look(lerpv((1.8+sx_, -3.8+sy_, 2.4+sz_), (1.4, -3.0, 2.2), eio(k)), (0.4, 0.6, 1.4), 24)
    M["grade"] = "night"

@shot(34.62, 42.14)
def c6(W, T, M):
    if T < 39.2:
        show(W["nave"], True); hid(W["roof"], False); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
        tr = W["truck"]; show(tr, True); f = eio(clamp((T-34.7)/2.0))
        tr.location = (O_N[0]+0.0, O_N[1]-16+7*f, 0); tr.rotation_euler = (0, 0, math.pi)
        H = alex(W, O_N[0]-4.0, O_N[1]-9.0, -30, T, "smirk", (0.4, 0)); H.arm(1, fwd=0.4, side=2.4, elbow=0.4+0.3*math.sin(T*8))
        look(lerpv((O_N[0]-9.0, O_N[1]-20.0, 4.5), (O_N[0]-7.0, O_N[1]-18.0, 3.5), eio(clamp((T-34.62)/2.4))), (O_N[0], O_N[1]-6.0, 3.0), 24)
        M["grade"] = "day"
    else:
        show(W["street"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
        c1_ = W["car1"]; show(c1_, True); c1_.location = (O_S[0]+1.0, O_S[1]+0.0, 0); c1_.rotation_euler = (0, 0, 0.3)
        hid(W["bow"], False); W["bow"].location = (O_S[0]+1.0, O_S[1], 1.45)
        if T > 40.9:
            c2_ = W["car2"]; show(c2_, True); c2_.location = (O_S[0]+5.0, O_S[1]+1.5, 0); c2_.rotation_euler = (0, 0, -0.3)
        H = alex(W, O_S[0]-1.4, O_S[1]-1.0, 30, T, "happy", (0.4, 0.2)); H.arm(-1, fwd=2.8, side=0.3, elbow=0.2)
        if T < 40.2:
            look(lerpv((O_S[0]-2.0, O_S[1]-7.0, 1.6), (O_S[0]-1.2, O_S[1]-6.0, 1.7), eio(clamp((T-39.2)/1.0))), (O_S[0]+0.6, O_S[1], 1.1), 24)
        else:
            e = eio(clamp((T-40.2)/1.9))
            look((O_S[0]+lerp(-2.0, 8.0, e), O_S[1]-lerp(7.0, 14.0, e), lerp(1.8, 22.0, e)), (O_S[0]+lerp(1.0, 22.0, e), O_S[1]+lerp(0, 6.0, e), lerp(1.0, 30.0, e)), 24)
        M["grade"] = "day"

@shot(42.14, 50.8)
def c7(W, T, M):
    show(W["nave"], True); k = (T-42.14)/8.66
    burst = T > 48.4
    hid(W["roof"], burst); hid(W["door"], False)
    mt = W["mount"]; hid(mt, False); mt.location = (O_N[0], O_N[1]+5, 0); g = eio(clamp((T-46.0)/2.4)); mt.scale = (lerp(10, 23.5, g), lerp(8, 19.5, g), lerp(3.0, 11.5, g))
    if burst:
        for q, s in enumerate(W["spill"]):
            tt = (T-48.4)*1.2; a = q*2*math.pi/30
            hid(s, False); s.location = (O_N[0]+math.cos(a)*(6+tt*6), O_N[1]+4+math.sin(a)*(5+tt*5), max(0.3, 11+6*tt-9.8*tt*tt*0.5))
    if T < 46.0:
        world_color("#1C2230"); light_dir((0.3, -0.6, 0.75)); shadow(0.4)
        H = alex(W, O_N[0]-1.8, O_N[1]-3.6, 170, T, "worried", (0, 0.8))
        look(lerpv((O_N[0]+0.2, O_N[1]-5.6, 1.2), (O_N[0]+0.0, O_N[1]-5.3, 1.3), eio(clamp((T-42.14)/3.8))), (O_N[0]-0.8, O_N[1]+4.0, 3.0), 20)
        M["grade"] = "night"
    else:
        world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
        sx_, sy_, sz_ = shake(T, 0.12 if burst and T < 49.2 else 0.0)
        look((O_N[0]-24+sx_, O_N[1]-30+sy_, 10+sz_), (O_N[0], O_N[1]+4, 7.0), 26)
        if 48.4 < T < 48.48: M["flash"] = 1
        M["grade"] = "day"

@shot(50.8, 60.98)
def c8(W, T, M):
    flat(W, night=True); k = (T-50.8)/10.18
    sea = W["sea"]; hid(sea, False); sea.location = (0, 0.2, 0); sea.scale = (1, 1, 0.5)
    v = 2**lerp(30, 41, eio(clamp((T-50.9)/4.5)))
    settext(W["counter"], fmt(v)); W["counter"].scale = (0.62, 0.62, 0.62)
    H = alex(W, 0.2, -0.4, 0, T, "worried" if T < 57.0 else "scared", (0.5*math.sin(T*2), -0.3), z=0.5)
    for q, p in enumerate(W["phones"]):
        ring = (T > 56.1 and q == 0) or (T > 57.6 and q == 1)
        hid(p, False); bz = 0.03*math.sin(T*60) if ring else 0
        p.location = (-0.6+q*1.4+bz, -1.2, 0.52); p.rotation_euler = (0, 0, 0.2*q)
        lb = W["phlab"][q]; hid(lb, not ring); lb.location = (-0.75+q*1.4, -1.3, 0.56)
    for sx in (-1, 1): H.arm(sx, fwd=1.0, side=0.5, elbow=2.4)
    look(lerpv((0.6, -3.6, 2.6), (0.4, -2.8, 2.3), eio(k)), (0.2, 0.4, 1.5), 24)
    M["grade"] = "night"

@shot(60.98, 68.92)
def c9(W, T, M):
    show(W["space"], True); world_color("#04050A"); light_dir((0.6, -0.5, 0.6)); shadow(0.3)
    k = (T-60.98)/7.94
    W["globe"].rotation_euler = (0.35, 0, T*0.2)
    g = eio(clamp((T-63.0)/5.0)); s = lerp(0.3, 8.0, g)
    sc = W["scube"]; hid(sc, False); sc.scale = (s, s, s); sc.location = (O_E[0]-2.2-s*0.45, O_E[1], 0); sc.rotation_euler = (0.2, 0.3, T*0.15)
    look(lerpv((0.0, O_E[1]-14.0, 2.0), (0.0, O_E[1]-28.0, 6.0), eio(k)), (lerp(1.5, -3.0, eio(k)), O_E[1], 0.0), 30)
    M["grade"] = "night"

@shot(68.92, TOTAL+0.1)
def c10(W, T, M):
    show(W["nave"], True); hid(W["roof"], False); world_color("#0A0E18"); light_dir((0.3, -0.6, 0.75)); shadow(0.35)
    k = (T-68.92)/8.07
    mt = W["mount"]; hid(mt, False); mt.scale = (12, 8, 6); mt.location = (O_N[0], O_N[1]+7, 0)
    op = eio(clamp((T-69.0)/1.2)); W["door"].location = (O_N[0]+5.8*op, O_N[1]-6.0, 3.0); hid(W["door"], False)
    police(W, T, [(O_N[0]-1.2, O_N[1]-9.5, 1.4), (O_N[0]+1.2, O_N[1]-9.5, 1.4)])
    for q, c in enumerate(W["cops"]):
        c.show(True); c.place(O_N[0]-0.8+1.6*q, O_N[1]-7.6, 0); c.idle(T+q); c.face(T, "angry", (0, 0))
    H = alex(W, O_N[0], O_N[1]-5.2, 0, T, "neutral" if T < 72.0 else "smirk", (0, 0.1))
    H.arm(1, fwd=1.5, side=0.05, elbow=0.4); H.fingers(1, 0.2, 0.1)
    hp = hand_pos(H)
    c = W["c1"]; hid(c, False); c.location = tuple(hp); c.rotation_euler = (math.pi/2, 0, 0)
    if T < 72.0:
        look(lerpv((O_N[0]+2.4, O_N[1]-2.4, 1.8), (O_N[0]+1.6, O_N[1]-3.2, 1.7), eio(clamp((T-68.92)/3.0))), (O_N[0], O_N[1]-7.0, 1.5), 24)
    else:
        look(lerpv((hp.x+0.7, hp.y-1.1, hp.z+0.25), (hp.x+0.45, hp.y-0.75, hp.z+0.18), eio(clamp((T-72.0)/4.5))), (hp.x, hp.y, hp.z+0.1), 30, fstop=2.5)
    M["grade"] = "night"; M["alarm"] = 1; M["fade"] = clamp((T-76.5)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
