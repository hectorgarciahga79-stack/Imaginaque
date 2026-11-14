"""Q9 · «¿Y si un día apareciera un agujero negro en tu salón?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral) colocada en 0,15 s. Tiempos de plano = timeline de align.py (52,83 s).
Decorados propios: salón (origen), balanza (y=200), espacio (y=400), Tierra en corte (y=600),
mesa de ping-pong (y=800). Protagonista original: Nico (sudadera verde)."""
import math, random
import numpy as np
from vox import *
from person import Person, npc_look
from world import Batch, tmat, building, tree, tiles, planks

FPS = 24
TOTAL = 52.83
NICO = dict(skin="#EBC29C", hair="#2C1E16", hair2="#3C2A1E", eye="#3A6A3A", top="#3FA45A", top2="#2E8046", stripe="#F2D23A",
            legs="#34405A", legs2="#2A3448", shoe="#F4F1EA", shoe2="#D8453A", watch=False, hstyle="short")

class Env:
    def talk(self, who, T): return 0.0

O_SC = (0, 200, 0); O_SP = (0, 400, 0); O_CUT = (0, 600, 0); O_PP = (0, 800, 0)
DISK = ["#FFF4C0", "#FFD040", "#FF9A20", "#FF6A10", "#FFB830"]

def vsphere(B, c, R, step, colf, shell=1.6, cut=None):
    n = int(R/step)+1
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            for k in range(-n, n+1):
                x, y, z = i*step, j*step, k*step; d = math.sqrt(x*x+y*y+z*z)
                if d > R or d < R-shell*step: continue
                if cut and cut(x, y, z): continue
                B.add((c[0]+x, c[1]+y, c[2]+z), (step, step, step), colf(x, y, z, d))

def earthcol(x, y, z, d):
    r = random.Random(int(x*7+y*13+z*31))
    if abs(z) > d*0.86: return "#F4F6F8"
    n = math.sin(x*0.45)+math.cos(y*0.38)+math.sin(z*0.5+x*0.2)
    if n > 0.9: return r.choice(["#4E9A3A", "#5AA844", "#C8A860"])
    return r.choice(["#2A6EB0", "#2E78BC", "#2766A8"])

def blackhole(name, parent, s=1.0, rings=True):
    g = group(name, (0, 0, 0), parent)
    B = Batch(name+"_core", g, 1.0)
    vsphere(B, (0, 0, 0), 0.5*s, 0.1*s, lambda *a: "#050508", shell=6)
    B.done()
    ring = None
    if rings:
        ring = group(name+"_ring", (0, 0, 0), g)
        R = Batch(name+"_rb", ring, 1.0); r = random.Random(5)
        for a in range(90):
            an = a*2*math.pi/90
            for rr in (0.72, 0.86, 1.0, 1.14):
                if r.random() < 0.18: continue
                R.add((math.cos(an)*rr*s, math.sin(an)*rr*s, r.uniform(-0.02, 0.02)*s), (0.11*s, 0.11*s, 0.04*s), DISK[int(rr*7) % 5])
        R.done()
        halo = group(name+"_halo", (0, 0, 0), g)
        H = Batch(name+"_hb", halo, 1.0)
        for a in range(60):
            an = a*2*math.pi/60
            H.add((math.cos(an)*0.62*s, 0, math.sin(an)*0.62*s), (0.08*s, 0.03*s, 0.08*s), "#FFE680")
        H.done()
    return g, ring

def build():
    reset((720, 1280))
    W = {}
    # ---------------- salón ----------------
    W["room"] = g = group("room")
    B = Batch("room_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("floor", "#B8875A", 16, 0.07, 41, planks))
    B.add((0, 5.0, 1.6), (14, 0.2, 3.2), tmat("wall", "#E8DCC4", 16, 0.04, 42))
    B.add((-6.0, 0, 1.6), (0.2, 12, 3.2), tmat("wall2", "#DCCDB0", 16, 0.04, 43))
    B.add((2.6, 4.88, 1.8), (2.6, 0.06, 1.6), "#9CC8E8"); B.add((2.6, 4.86, 1.8), (2.7, 0.04, 0.08), "#F4F1EA")
    B.add((-1.0, 0.5, 0.01), (4, 3, 0.02), "#5A7AA8")                       # alfombra
    B.done()
    W["sofa"] = so = group("sofa", (-1.2, 3.4, 0), g)
    S = Batch("sofa_b", so, 1.0)
    S.add((0, 0, 0.25), (2.8, 1.0, 0.5), "#C8462E"); S.add((0, 0.42, 0.75), (2.8, 0.26, 0.9), "#A8382A")
    S.add((-1.32, 0, 0.5), (0.26, 1.0, 0.6), "#A8382A"); S.add((1.32, 0, 0.5), (0.26, 1.0, 0.6), "#A8382A")
    S.add((-0.6, 0.1, 0.6), (0.5, 0.25, 0.4), "#F2D23A"); S.done()
    W["tv"] = tv = group("tv", (-1.2, -3.2, 0), g)
    T = Batch("tv_b", tv, 1.0)
    T.add((0, 0, 0.3), (2.2, 0.6, 0.6), "#6A4A30"); T.add((0, 0, 1.15), (1.9, 0.12, 1.1), "#1C1C22")
    T.add((0, 0.07, 1.15), (1.75, 0.02, 0.95), "#3A6EA8"); T.done()
    W["lamp"] = lp = group("lamp", (-4.8, 3.8, 0), g)
    L = Batch("lamp_b", lp, 1.0); L.add((0, 0, 0.9), (0.1, 0.1, 1.8), "#2A2A2E"); L.add((0, 0, 1.9), (0.6, 0.6, 0.45), "#FFE6A0"); L.done()
    W["plant"] = pl = group("plant", (3.6, 3.8, 0), g)
    P = Batch("plant_b", pl, 1.0); P.add((0, 0, 0.25), (0.5, 0.5, 0.5), "#C46A2E")
    for a in range(6): P.add((math.cos(a)*0.25, math.sin(a)*0.25, 0.75+0.1*(a % 2)), (0.3, 0.3, 0.5), "#4E9A3A")
    P.done()
    W["table"] = tb = group("tablet", (1.4, 0.4, 0), g)
    T = Batch("table_b", tb, 1.0); T.add((0, 0, 0.42), (1.4, 0.8, 0.08), "#8A5A36")
    for sx in (-1, 1):
        for sy in (-1, 1): T.add((sx*0.6, sy*0.32, 0.2), (0.08, 0.08, 0.4), "#6A4428")
    T.add((-0.3, 0, 0.52), (0.14, 0.14, 0.16), "#F4F1EA"); T.add((0.25, 0.1, 0.5), (0.4, 0.3, 0.1), "#3A6EA8"); T.done()
    W["books"] = [box(f"book{i}", (0, 0, 0), (0.3, 0.22, 0.06), mat(c), g) for i, c in enumerate(["#C0302A", "#3A6EA8", "#E0B040", "#6A9A48", "#7A4E8A", "#F4F1EA"])]
    # barrio (exterior)
    W["hood"] = g = group("hoodg")
    B2 = Batch("hood_b", g, 1.0)
    B2.add((0, 0, -0.06), (200, 200, 0.1), tmat("grass", "#5A9A44", 16, 0.10, 44))
    B2.add((0, -9, 0.0), (200, 6, 0.06), tmat("road", "#4A4A50", 16, 0.05, 45))
    cols = ["#E8D8B8", "#F0E6D0", "#D8C8A8", "#C8D8E0", "#E0C8A8"]
    for k in range(-5, 6):
        building(B2, k*13.0, 22, 9, 8, 2+k % 3, cols[k % 5], 500+k, -1)
        tree(B2, k*13.0+6.2, 14, 3.0, k)
    B2.done()
    W["house"] = []
    r = random.Random(3)
    for ix in range(-5, 6):
        for iz in range(0, 7):
            for side in (0, 1):
                c = "#F0E6D0" if iz < 5 else "#B8483A"
                W["house"].append((box(f"hb{ix}_{iz}_{side}", (0, 0, 0), (1.0, 1.0, 1.0), mat(c), None), (ix*1.0, -6.0+side*12, 0.5+iz*1.0), r.random()))
    for iy in range(-6, 7):
        for iz in range(0, 7):
            for side in (-1, 1):
                c = "#E8DCC4" if iz < 5 else "#B8483A"
                W["house"].append((box(f"hs{iy}_{iz}_{side}", (0, 0, 0), (1.0, 1.0, 1.0), mat(c), None), (side*6.0, iy*1.0, 0.5+iz*1.0), r.random()))
    # ---------------- balanza ----------------
    W["scale"] = g = group("scaleg", O_SC)
    B = Batch("sc_b", g, 1.0)
    B.add((0, 0, -0.05), (60, 60, 0.1), tmat("labfl", "#3A4250", 16, 0.05, 46, tiles))
    B.add((0, 0, 0.15), (2.4, 1.4, 0.3), "#5A6270"); B.add((0, 0, 2.2), (0.4, 0.4, 4.0), "#8A929E")
    B.add((0, 6, 3), (60, 0.2, 6), "#2A3040"); B.done()
    W["beam"] = bm_ = group("beam", (0, 0, 4.25), g)
    Bb = Batch("beam_b", bm_, 1.0); Bb.add((0, 0, 0), (9.0, 0.3, 0.3), "#C8CCD2"); Bb.add((0, 0, 0.1), (0.5, 0.5, 0.5), "#E0B040"); Bb.done()
    W["pans"] = []
    for sx in (-1, 1):
        pg = group(f"pan{sx}", (0, 0, 0), g)
        Pb = Batch(f"pan_b{sx}", pg, 1.0)
        for a in range(3): Pb.add((math.cos(a*2.1)*0.9, math.sin(a*2.1)*0.9, 1.4), (0.04, 0.04, 2.8), "#9AA0A8")
        Pb.add((0, 0, 0), (2.6, 2.6, 0.16), "#C8CCD2"); Pb.done()
        W["pans"].append((sx, pg))
    W["mini_earth"] = me = group("mini_earth", (0, 0, 0), g)
    Bm = Batch("me_b", me, 1.0); vsphere(Bm, (0, 0, 0), 1.2, 0.2, earthcol, 2.0); Bm.done()
    W["bh_sc"], W["ring_sc"] = blackhole("bh_sc", g, 0.32)
    # ---------------- espacio ----------------
    W["space"] = g = group("space", O_SP)
    B = Batch("stars_b", g, 1.0); r = random.Random(11)
    for i in range(500):
        th, ph = r.uniform(0, 2*math.pi), r.uniform(-1.2, 1.2)
        R = r.uniform(140, 180)
        B.add((math.cos(th)*math.cos(ph)*R, math.sin(th)*math.cos(ph)*R, math.sin(ph)*R), (0.5, 0.5, 0.5), r.choice(["#FFFFFF", "#DDE6FF", "#FFF0C8"]))
    B.done()
    W["earth"] = eg = group("earth", O_SP)
    Be = Batch("earth_b", eg, 1.0); vsphere(Be, (0, 0, 0), 10, 0.5, earthcol, 2.2); Be.done()
    W["bh_sp"], W["ring_sp"] = blackhole("bh_sp", None, 0.6)
    W["arrows"] = []
    for k in range(2):
        a = group(f"arrow{k}", (0, 0, 0))
        Ba = Batch(f"arrow_b{k}", a, 1.0)
        for j in range(5): Ba.add((0, 0, j*0.55), (0.35, 0.35, 0.45), "#FFD040")
        Ba.add((0, 0, 2.9), (0.9, 0.35, 0.35), "#FFD040"); Ba.add((0, 0, 3.2), (0.5, 0.35, 0.3), "#FFD040"); Ba.done()
        W["arrows"].append(a)
    # chunks de Tierra (para el final)
    W["chunks"] = []; r = random.Random(17)
    for i in range(220):
        th, ph = r.uniform(0, 2*math.pi), math.asin(r.uniform(-1, 1))
        c = r.choice(["#2A6EB0", "#2E78BC", "#4E9A3A", "#C8A860", "#8A6A4A", "#F4F6F8"])
        s = r.uniform(0.9, 2.2)
        W["chunks"].append((box(f"ch{i}", (0, 0, 0), (s, s, s), mat(c), None), th, ph, r.random()))
    # ---------------- Tierra en corte ----------------
    W["cut"] = g = group("cutg", O_CUT)
    def cutcol(x, y, z, d):
        if d > 9.2: return earthcol(x, y, z, d)
        if d > 5.8: return random.Random(int(x*5+z*9)).choice(["#C8642A", "#D8742E", "#B85A26"])
        if d > 3.4: return random.Random(int(x*5+z*9)).choice(["#E89A30", "#F0A838"])
        return random.Random(int(x*5+z*9)).choice(["#FFE070", "#FFD050"])
    Bc = Batch("cut_b", g, 1.0); vsphere(Bc, (0, 0, 0), 10, 0.5, cutcol, 30, cut=lambda x, y, z: y < 0 or (y > 0.6 and math.sqrt(x*x+y*y+z*z) < 8.8)); Bc.done()
    W["bh_cut"], W["ring_cut"] = blackhole("bh_cut", None, 0.55)
    W["trail"] = [box(f"tr{i}", (0, 0, 0), (0.45, 0.45, 0.45), mat(["#FFF4C0", "#FFD040", "#FF9A20"][i % 3]), None) for i in range(30)]
    # disco (primer plano en la roca)
    W["rock"] = g = group("rockg", (0, 1000, 0))
    Br = Batch("rock_b", g, 1.0); r = random.Random(21)
    for i in range(900):
        th = r.uniform(0, 2*math.pi); R = r.uniform(4, 16)
        Br.add((math.cos(th)*R, math.sin(th)*R*0.3+6, math.sin(th)*R*0.9), (r.uniform(0.6, 1.6),)*3, r.choice(["#8A5A3A", "#6A4A30", "#A86A3A", "#C8642A"]))
    Br.done()
    W["bh_big"], W["ring_big"] = blackhole("bh_big", None, 2.2)
    W["debris"] = [box(f"db{i}", (0, 0, 0), (0.3, 0.3, 0.3), mat(["#8A5A3A", "#C8642A", "#FFD040", "#FFF4C0"][i % 4]), None) for i in range(70)]
    # ---------------- ping-pong ----------------
    W["pp"] = g = group("ppg", O_PP)
    B = Batch("pp_b", g, 1.0)
    B.add((0, 0, -0.05), (40, 40, 0.1), tmat("ppfl", "#C8B898", 16, 0.05, 47, planks))
    B.add((0, 0, 0.76), (2.74, 1.52, 0.04), "#2E6A4A"); B.add((0, 0, 0.785), (2.74, 0.02, 0.005), "#F4F1EA")
    B.add((0, 0, 0.87), (0.02, 1.7, 0.15), "#E8E8E8")
    for sx in (-1, 1):
        for sy in (-1, 1): B.add((sx*1.2, sy*0.6, 0.37), (0.06, 0.06, 0.74), "#2A2A2E")
    B.add((0, 8, 2), (40, 0.2, 4), "#D8CCB4"); B.done()
    W["ppball"] = Batch("ppball_b", g, 1.0); vsphere(W["ppball"], (0.0, 0, 0), 0.02, 0.004, lambda *a: "#FBFBF6", 6); W["ppball"] = W["ppball"].done((0.62, -0.1, 0.8))
    W["bh_pp"], W["ring_pp"] = blackhole("bh_pp", g, 0.036, rings=True)
    W["paddle"] = pd = group("paddle", (0, 0, 0), g)
    Bp = Batch("pad_b", pd, 1.0); Bp.add((0, 0, 0), (0.16, 0.17, 0.012), "#C0302A"); Bp.add((0, -0.13, 0), (0.035, 0.1, 0.025), "#8A5A36"); Bp.done()
    # ---------------- personaje ----------------
    W["nico"] = Person("nico", NICO)
    camera(28)
    return W

def hide_all(W):
    for k in ("room", "hood", "scale", "space", "earth", "bh_sp", "cut", "bh_cut", "rock", "bh_big", "pp"): show(W[k], False)
    for a in W["arrows"]: show(a, False)
    for o, *_ in W["house"]: hid(o, True)
    for o, *_ in W["chunks"]: hid(o, True)
    for o in W["trail"] + W["debris"]: hid(o, True)
    W["nico"].show(False)

def space(W):
    world_color("#04050C"); light_dir((0.6, -0.5, 0.45)); shadow(0.6); show(W["space"], True)

def room(W):
    show(W["room"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)

def bh_at(W, key, ringkey, loc, T, s=1.0, tilt=0.35):
    g = W[key]; show(g, True); g.location = loc; g.scale = (s, s, s)
    if W[ringkey] is not None:
        W[ringkey].rotation_euler = (tilt, 0.1, T*2.2)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

BHR = (0.6, 0.6, 1.25)   # canica en el salón

def room_items(W, T, pull=0.0):
    """pull 0..1: los objetos del salón caen en espiral hacia la canica"""
    for i, b in enumerate(W["books"]):
        base = (1.2+(i % 3)*0.3, 0.3+(i//3)*0.25, 0.53+0.06*(i % 2))
        k = clamp(pull*1.4-i*0.08)
        an = k*6+i
        p = lerpv(base, (BHR[0]+math.cos(an)*0.2*(1-k), BHR[1]+math.sin(an)*0.2*(1-k), BHR[2]), ease(k))
        b.location = p; b.rotation_euler = (k*5+i, k*3, k*7); b.scale = (1-0.95*k,)*3; hid(b, k > 0.97)
    for key, home, d0 in (("sofa", (-1.2, 3.4, 0), 0.0), ("tv", (-1.2, -3.2, 0), 0.15), ("lamp", (-4.8, 3.8, 0), 0.3), ("plant", (3.6, 3.8, 0), 0.1), ("table", (1.4, 0.4, 0), 0.05)):
        o = W[key]; k = ease(clamp((pull-d0)/0.75))
        an = k*4.5
        cx, cy = BHR[0]+(home[0]-BHR[0])*(1-k), BHR[1]+(home[1]-BHR[1])*(1-k)
        o.location = (BHR[0]+(cx-BHR[0])*math.cos(an)-(cy-BHR[1])*math.sin(an), BHR[1]+(cx-BHR[0])*math.sin(an)+(cy-BHR[1])*math.cos(an), home[2]+(BHR[2]-0.4-home[2])*k)
        o.rotation_euler = (k*2.5, k*1.5, an); sc = max(0.02, 1-0.98*k**1.5); o.scale = (sc, sc, sc)
        show(o, sc > 0.03)

# ------------------------------------------------------------------ planos
@shot(0.0, 4.68)
def a1(W, T, M):
    room(W); room_items(W, T, 0)
    bh_at(W, "bh_sp", "ring_sp", BHR, T, 0.3*(0.4+0.6*ease(clamp(T/0.5))))
    H = W["nico"]; H.show(True); H.place(-0.9, 1.4, 35); H.idle(T)
    H.face(T, "shock" if T > 0.7 else "neutral", (0.6, -0.3))
    if T > 0.7: H.arm(1, fwd=0.7, side=0.3, elbow=1.9); H.arm(-1, fwd=0.6, side=0.3, elbow=1.9)
    k = eio(T/4.68)
    look(lerpv((-0.4, -2.8, 1.7), (0.35, -0.9, 1.35), k), lerpv((-0.2, 0.9, 1.35), BHR, k), lerp(24, 30, k))
    M["grade"] = "day"

@shot(4.68, 7.8)
def a2(W, T, M):
    room(W); room_items(W, T, 0); k = (T-4.68)/3.12
    bh_at(W, "bh_sp", "ring_sp", BHR, T, 0.22)
    ruler = W["books"][5]
    look(lerpv((BHR[0]+0.9, BHR[1]-1.5, BHR[2]+0.2), (BHR[0]+0.45, BHR[1]-0.9, BHR[2]+0.05), eio(k)), BHR, 34, fstop=2.0)
    M["grade"] = "day"

@shot(7.8, 10.88)
def a3(W, T, M):
    world_color("#1C2230"); light_dir((0.4, -0.6, 0.7)); shadow(0.5)
    show(W["scale"], True); k = T-7.8
    tilt = 0.18*math.cos(k*3.2)*math.exp(-k*1.1)
    bm_ = W["beam"]; bm_.rotation_euler = (0, tilt, 0)
    for sx, pg in W["pans"]:
        x = sx*4.3*math.cos(tilt); z = 4.25 - sx*4.3*math.sin(tilt) - 2.95
        pg.location = (x, 0, z)
        if sx == 1:
            W["mini_earth"].location = (x, 0, z+1.3); W["mini_earth"].rotation_euler = (0, 0, T*0.5)
        else:
            bh_at(W, "bh_sc", "ring_sc", (O_SC[0]+x, O_SC[1], z+0.4), T, 1.0)
            W["bh_sc"].location = (x, 0, z+0.4)
    a = -0.5+0.35*eio(k/3.08)
    look((math.sin(a)*17, O_SC[1]-math.cos(a)*17, 3.8), (0, O_SC[1], 2.6), 22)
    M["grade"] = "lab"

@shot(10.88, 16.22)
def a4(W, T, M):
    room(W); k = T-10.88
    room_items(W, T, 0.12*clamp(k/5))
    bh_at(W, "bh_sp", "ring_sp", BHR, T, 0.22)
    H = W["nico"]; H.show(True)
    lean = 0.25+0.05*math.sin(T*9)
    H.place(-0.4+0.15*clamp(k/5), -0.4, 135, 0)
    H.hips.rotation_euler = (lean, 0, 0)
    H.arm(1, fwd=1.7, side=0.1, elbow=0.2); H.arm(-1, fwd=1.6, side=0.15, elbow=0.25)
    H.leg(1, fwd=0.4, knee=0.2); H.leg(-1, fwd=-0.3, knee=0.3)
    H.face(T, "scared", (0.6, 0.0))
    sx, sy, sz = shake(T, 0.02)
    cams = (((0.2, -2.4, 1.9), (-0.35, -0.35, 1.6), 30), ((1.8, -2.4, 1.3), (0.0, 0.0, 1.4), 26))
    part = 0 if k < 2.7 else 1; kk = eio((k-part*2.7)/2.7)
    cp, tg, ln = cams[part]
    look((cp[0]+sx+0.4*kk, cp[1]+sy+0.4*kk, cp[2]+sz), tg, ln, fstop=3.0)
    M["grade"] = "alarm"

@shot(16.22, 18.7)
def a5(W, T, M):
    room(W); k = (T-16.22)/2.48
    room_items(W, T, 0.12+0.88*k)
    bh_at(W, "bh_sp", "ring_sp", BHR, T, 0.22)
    sx, sy, sz = shake(T, 0.04)
    look((2.6+sx, -3.0+sy, 2.6+sz), (0.4, 0.7, 1.0), 24)
    M["grade"] = "alarm"

@shot(18.7, 21.24)
def a6(W, T, M):
    show(W["hood"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
    k = (T-18.7)/2.54
    for o, home, rr in W["house"]:
        hid(o, False); kk = ease(clamp((k*1.5-rr*0.5)))
        an = kk*5+rr*6
        dx, dy = home[0]-BHR[0], home[1]-BHR[1]
        o.location = (BHR[0]+(dx*math.cos(an)-dy*math.sin(an))*(1-kk), BHR[1]+(dx*math.sin(an)+dy*math.cos(an))*(1-kk), home[2]+(BHR[2]-home[2])*kk)
        sc = max(0.02, 1-kk); o.scale = (sc, sc, sc); o.rotation_euler = (kk*4, kk*3, an)
        if kk > 0.98: hid(o, True)
    bh_at(W, "bh_sp", "ring_sp", BHR, T, 0.5+1.2*k)
    sx, sy, sz = shake(T, 0.08)
    look(lerpv((14+sx, -22+sy, 11+sz), (18, -28, 15), eio(k)), (0, 0, 2.5), 24)
    M["grade"] = "alarm"

@shot(21.24, 25.42)
def a7(W, T, M):
    space(W); show(W["earth"], True); k = (T-21.24)/4.18
    W["earth"].rotation_euler = (0.3, 0, T*0.15)
    p = (O_SP[0]+7.6, O_SP[1]-5.2, 4.6)
    bh_at(W, "bh_sp", "ring_sp", p, T, 1.2)
    for i, a in enumerate(W["arrows"]):
        show(a, True)
        if i == 0:   # de la Tierra hacia el agujero
            a.location = (O_SP[0]+4.4, O_SP[1]-3.0, 2.7); a.rotation_euler = (math.radians(-60), 0, math.radians(-125))
        else:
            a.location = (O_SP[0]+10.4, O_SP[1]-7.1, 6.3); a.rotation_euler = (math.radians(-120), 0, math.radians(55))
        pul = 1+0.12*math.sin(T*6+i*3); a.scale = (pul, pul, pul)
    an = -0.9+0.35*eio(k)
    look((O_SP[0]+math.sin(an)*36, O_SP[1]-math.cos(an)*36, 9), (O_SP[0]+3.5, O_SP[1]-2.5, 2.0), 26)
    M["grade"] = "night"

@shot(25.42, 30.48)
def a8(W, T, M):
    space(W); show(W["cut"], True); k = (T-25.42)/5.06
    dz = lerp(9.6, 0.4, eio(k))
    bh_at(W, "bh_cut", "ring_cut", (O_CUT[0], O_CUT[1]-0.6, dz), T, 1.0)
    for i, o in enumerate(W["trail"]):
        z = dz + i*0.33
        if z > 9.8: continue
        hid(o, False); o.location = (O_CUT[0]+0.15*math.sin(i+T*8), O_CUT[1]-0.5, z); s = max(0.1, 1-i/30); o.scale = (s, s, s)
    an = 0.25*math.sin(T*0.4)
    look((O_CUT[0]+math.sin(an)*30, O_CUT[1]-math.cos(an)*30, 4), (O_CUT[0], O_CUT[1], lerp(5, 1.5, k)), 30)
    M["grade"] = "night"

@shot(30.48, 34.82)
def a9(W, T, M):
    world_color("#120804"); light_dir((0.2, -0.4, 0.9)); shadow(0.4)
    show(W["rock"], True); k = (T-30.48)/4.34
    c = (0, 1000+6, 0)
    bh_at(W, "bh_big", "ring_big", c, T*1.8, 1.0, 0.45)
    r = random.Random(4)
    for i, o in enumerate(W["debris"]):
        ph = (T*0.35+r.random()) % 1; R = lerp(9, 1.0, ph**1.5); an = r.random()*6.28+ph*9
        hid(o, False); o.location = (c[0]+math.cos(an)*R, c[1]+math.sin(an)*R*0.35, c[2]+math.sin(an)*R*0.28+r.uniform(-0.4, 0.4))
        o.rotation_euler = (ph*9, ph*5, 0)
    a = 0.3*eio(k)
    look((c[0]+math.sin(a)*14, c[1]-math.cos(a)*14, lerp(2.5, 4.0, k)), c, 28)
    M["grade"] = "night"

@shot(34.82, 40.58)
def a10(W, T, M):
    space(W); k = (T-34.82)/5.76
    p = (O_SP[0], O_SP[1], 0)
    bh_at(W, "bh_sp", "ring_sp", p, T, lerp(1.6, 2.6, eio(clamp((k-0.55)/0.45))))
    look(lerpv((p[0]+2.0, p[1]-9.0, 1.6), (p[0]+1.2, p[1]-6.4, 1.0), eio(k)), p, 30)
    M["grade"] = "night"
    if k < 0.55: M["freeze"] = 1

@shot(40.58, 47.1)
def a11(W, T, M):
    space(W); k = (T-40.58)/6.52
    show(W["earth"], True)
    es = max(0.05, 1-eio(clamp((k-0.15)/0.75))); W["earth"].scale = (es, es, es); W["earth"].rotation_euler = (0.3, 0, T*0.3)
    if es < 0.08: show(W["earth"], False)
    bh_at(W, "bh_sp", "ring_sp", (O_SP[0], O_SP[1], 0), T*1.5, lerp(1.4, 2.2, k))
    for o, th, ph, rr in W["chunks"]:
        kk = clamp((k-0.05-rr*0.35)/0.55)
        if kk <= 0 or kk >= 1: continue
        hid(o, False); R = lerp(10.5, 0.6, eio(kk)); an = th+kk*7
        o.location = (O_SP[0]+math.cos(an)*math.cos(ph)*R, O_SP[1]+math.sin(an)*math.cos(ph)*R, math.sin(ph)*R*(1-kk*0.85))
        o.rotation_euler = (kk*8, kk*5, an); s = 1-0.8*kk; o.scale = (s, s, s)
    d = lerp(44, 14, eio(k))
    look((O_SP[0]+d*0.35, O_SP[1]-d, d*0.22), (O_SP[0], O_SP[1], 0), 26)
    M["grade"] = "night"

@shot(47.1, 49.94)
def a12(W, T, M):
    show(W["pp"], True); world_color("#E8D8C0"); light_dir((0.4, -0.5, 0.8)); shadow(0.45)
    k = (T-47.1)/2.84
    bh_at(W, "bh_pp", "ring_pp", (0.48, -0.1, 0.8), T, 1.0)
    W["bh_pp"].location = (0.48, -0.1, 0.8)
    W["ppball"].location = (0.62, -0.1, 0.8)
    pd = W["paddle"]; pd.location = (0.9, -0.3, 0.79); pd.rotation_euler = (0, 0, 0.5)
    look(lerpv((O_PP[0]+0.7, O_PP[1]-0.75, 1.0), (O_PP[0]+0.6, O_PP[1]-0.45, 0.92), eio(k)), (O_PP[0]+0.55, O_PP[1]-0.1, 0.8), 34, fstop=2.2)
    M["grade"] = "day"

@shot(49.94, TOTAL+0.1)
def a13(W, T, M):
    room(W); room_items(W, T, 0); k = (T-49.94)/2.89
    bh_at(W, "bh_sp", "ring_sp", BHR, T, 0.22)
    H = W["nico"]; H.show(True); H.face_to(-0.6, -0.5, 0.7, -3.3); H.idle(T)
    H.face(T, "smirk", (0.5, 0.2))
    H.arm(1, fwd=1.3, side=0.2, elbow=0.6); H.fingers(1, 0.6, 0.0)
    H.arm(-1, fwd=0.4, side=0.2, elbow=2.0)
    look(lerpv((0.7, -3.3, 1.65), (0.5, -2.7, 1.55), eio(k)), (-0.15, -0.1, 1.35), 24)
    M["grade"] = "day"; M["fade"] = clamp((T-52.45)/0.38)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
