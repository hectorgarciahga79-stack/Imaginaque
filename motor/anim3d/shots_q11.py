"""Q11 · «¿Y si todos los volcanes del mundo entraran en erupción a la vez?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral). Tiempos de plano = timeline de align.py (63,31 s).
Decorados propios: planeta de vóxeles con 60 penachos (origen), pueblo con volcán que se parte (y=200),
sala de datos (y=400: Tambora, termómetro, barras de CO2), campo de cultivo y aeródromo (y=600).
Protagonista original: Lucas (chaqueta verde, pelo castaño)."""
import math, random
from vox import *
from mathutils import Vector
from person import Person
from world import Batch, tmat, building, tree, tiles, planks, brick, asphalt, car

FPS = 24
TOTAL = 63.31
LUCAS = dict(skin="#E8BE96", hair="#5A3A22", hair2="#6E4A2C", eye="#3A2A18", top="#2E8A5A", top2="#226A44", stripe="#F4D040",
             legs="#34405A", legs2="#28324A", shoe="#E8E4DA", shoe2="#2A2A2E", watch=False, hstyle="short")

class Env:
    def talk(self, who, T): return 0.0

O_T = (0, 200, 0); O_D = (0, 400, 0); O_F = (0, 600, 0)
LAVA = ["#FF5A14", "#FF8A20", "#FFC440"]
ROCK = "#5E524A"

def cone(B, cx, cy, base, h, n=7, col=ROCK, half=0):
    """volcán escalonado; half=-1/1 construye solo la mitad izquierda/derecha"""
    for l in range(n):
        s = base*(1-l/(n+0.6)); z = h*l/n + h/n/2
        c = tmat("rock"+col, col, 16, 0.12, 31) if l < n-1 else tmat("rock2"+col, "#3E3430" if col == ROCK else col, 16, 0.10, 32)
        if half == 0: B.add((cx, cy, z), (s, s, h/n), c)
        else: B.add((cx+half*s/4, cy, z), (s/2, s, h/n), c)
    return h

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(11)
    # ---------------- planeta ----------------
    W["globe"] = g = group("globe", (0, 0, 0))
    B = Batch("globe_b", g, 1.0)
    R = 5.0; st = 0.62; land = []
    n = int(R/st)+1
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            for k in range(-n, n+1):
                p = Vector((i, j, k))*st; d = p.length
                if not (R-st*0.95 < d <= R): continue
                u = p.normalized()
                v = math.sin(u.x*2.3+1.3)*math.cos(u.y*1.9-0.4) + 0.7*math.sin(u.z*3.0+u.x*1.7+u.y*2.2) + 0.5*math.cos(u.y*3.3-u.z*1.1)
                if abs(u.z) > 0.88: col = "#EEF4F8"
                elif v > -0.05: col = "#5A9A44" if v < 0.9 else "#8A7A5A"; land.append(p.copy())
                else: col = "#2E6EB8"
                B.add(tuple(p), (st, st, st), col)
    B.done()
    r.shuffle(land); W["plumes"] = []
    for q, p in enumerate(land[:60]):
        u = p.normalized()
        pl = box(f"pl{q}", tuple(p*1.0), (0.32, 0.32, 1.0), mat(LAVA[q % 3]), g, origin=(0, 0, -0.5))
        pl.rotation_euler = u.to_track_quat('Z', 'Y').to_euler()
        W["plumes"].append((pl, r.uniform(0, 1)))
    W["ash"] = []
    for q in range(140):
        u = Vector((r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1))).normalized()
        a = box(f"ash{q}", tuple(u*(R+0.9+r.uniform(0, 0.6))), (1.1, 1.1, 1.1), mat(["#3A3634", "#4A4644", "#2A2826"][q % 3]), g)
        W["ash"].append((a, r.uniform(0, 1)))
    W["stars"] = Batch("stars_b", None, 1.0)
    for q in range(160):
        W["stars"].add((r.uniform(-60, 60), r.uniform(25, 40), r.uniform(-60, 60)), (0.12, 0.12, 0.12), "#FFFFFF")
    W["stars"] = W["stars"].done()
    # ---------------- pueblo ----------------
    W["town"] = g = group("town", O_T)
    B = Batch("town_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("grass", "#5A9A44", 16, 0.10, 41))
    B.add((0, 0, 0.0), (6, 300, 0.06), tmat("road", "#4A4A50", 16, 0.05, 42, asphalt))
    cols = ["#E8D8B8", "#F0E6D0", "#D8C8A8", "#E0C8A8"]
    for k in range(-3, 6):
        building(B, -8.5, k*9.0, 8, 6, 2+abs(k) % 2, cols[k % 4], 400+k, 1)
        if k != 0: building(B, 9.0, k*9.0, 8, 6, 2+(k+1) % 2, cols[(k+1) % 4], 420+k, -1)
        tree(B, -4.2, k*9.0+4.5, 2.6, k)
    for q in range(10): cone(B, -60+q*13, 95+r.uniform(0, 20), 18, 6+r.uniform(0, 5), 5, "#6A7A5A")
    B.done()
    # casa con tejado (se hunde)
    W["house"] = hs = group("house", (O_T[0]+7.5, O_T[1]+0.5, 0))
    Bh = Batch("house_b", hs, 1.0)
    Bh.add((0, 0, 1.6), (5, 5, 3.2), tmat("hwall", "#F0E0C0", 16, 0.06, 43, brick))
    Bh.add((-2.52, 0, 1.0), (0.06, 1.1, 2.0), "#7A4A2A")
    for y in (-1.6, 1.6): Bh.add((-2.52, y, 2.0), (0.06, 1.0, 0.9), "#9FD0E8")
    Bh.done()
    W["roof"] = box("roof", (O_T[0]+7.5, O_T[1]+0.5, 3.4), (5.6, 5.6, 0.4), tmat("rooft", "#B8463A", 16, 0.08, 44, planks))
    W["ashroof"] = box("ashroof", (O_T[0]+7.5, O_T[1]+0.5, 3.6), (5.6, 5.6, 1.0), mat("#8A8682"), origin=(0, 0, -0.5))
    W["ashground"] = box("ashground", (O_T[0], O_T[1], 0.0), (60, 80, 1.0), mat("#8E8A86"), origin=(0, 0, -0.5))
    # volcán que se parte (detrás, en y+48)
    VY = O_T[1]+48
    W["vl"] = vl = group("vl", (0, VY, 0)); W["vr"] = vr = group("vr", (0, VY, 0))
    Bl = Batch("vl_b", vl, 1.0); cone(Bl, 0, 0, 30, 16, 8, ROCK, -1); Bl.done()
    Br = Batch("vr_b", vr, 1.0); cone(Br, 0, 0, 30, 16, 8, ROCK, 1); Br.done()
    W["lavacol"] = box("lavacol", (0, VY, 0), (3.0, 3.0, 1.0), mat("#FF7A1E"), origin=(0, 0, -0.5))
    W["lavacore"] = box("lavacore", (0, VY, 0), (1.6, 1.6, 1.0), mat("#FFD050"), origin=(0, 0, -0.5))
    W["bombs"] = [(box(f"bomb{q}", (0, 0, 0), (0.9, 0.9, 0.9), mat(LAVA[q % 3])), r.uniform(-1, 1), r.uniform(-0.5, 0.5), r.uniform(0.7, 1.3), r.uniform(0, 3)) for q in range(40)]
    W["smoke"] = [(box(f"smk{q}", (0, 0, 0), (4, 4, 4), mat(["#3A3634", "#55504C", "#2A2826"][q % 3])), r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(0, 1)) for q in range(36)]
    # río de lava (avanza despacio por la carretera)
    W["flow"] = [box(f"flow{q}", (0, 0, 0), (1.0, 1.0, 0.35), mat(LAVA[q % 3])) for q in range(60)]
    # ceniza que cae
    W["flakes"] = [(box(f"fl{q}", (0, 0, 0), (0.09, 0.09, 0.09), mat(["#9A9692", "#7A7672", "#B8B4B0"][q % 3])), r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(0, 1)) for q in range(220)]
    W["snow"] = [(box(f"sn{q}", (0, 0, 0), (0.08, 0.08, 0.08), mat("#FFFFFF")), r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(0, 1)) for q in range(160)]
    # ---------------- sala de datos ----------------
    W["data"] = g = group("data", O_D)
    B = Batch("data_b", g, 1.0)
    B.add((0, 0, -0.05), (120, 120, 0.1), tmat("dfl", "#2E3644", 16, 0.05, 51, tiles))
    B.add((0, 30, 30), (120, 0.2, 60), "#1C2230")
    B.done()
    W["tambora"] = tb = group("tambora", (O_D[0]-1.5, O_D[1], 0))
    Bt = Batch("tb_b", tb, 1.0); cone(Bt, 0, 0, 3.2, 1.8, 6); Bt.add((0, 0, 1.85), (0.45, 0.45, 0.1), "#FF7A1E"); Bt.done()
    W["tplume"] = box("tplume", (O_D[0]-1.5, O_D[1], 1.8), (0.5, 0.5, 1.0), mat("#4A4644"), origin=(0, 0, -0.5))
    W["thermo"] = th = group("thermo", (O_D[0]+1.5, O_D[1], 0))
    Bth = Batch("th_b", th, 1.0)
    Bth.add((0, 0.12, 2.0), (0.7, 0.1, 4.0), "#F4F1EA"); Bth.add((0, 0, 0.35), (0.7, 0.7, 0.7), "#C0302A")
    for k in range(9): Bth.add((0.42, 0.0, 0.8+k*0.4), (0.18, 0.05, 0.04), "#2A2A2E")
    Bth.done()
    W["merc"] = box("merc", (O_D[0]+1.5, O_D[1]-0.02, 0.7), (0.28, 0.12, 1.0), mat("#E0302A"), origin=(0, 0, -0.5))
    W["mercb"] = box("mercb", (O_D[0]+1.5, O_D[1]-0.02, 0.7), (0.28, 0.12, 1.0), mat("#5AB0E8"), origin=(0, 0, -0.5))
    # barras CO2
    W["barv"] = box("barv", (O_D[0]-1.6, O_D[1]+6, 0), (1.6, 1.6, 1.0), mat("#8A8682"), origin=(0, 0, -0.5))
    W["barh"] = box("barh", (O_D[0]+1.6, O_D[1]+6, 0), (1.6, 1.6, 1.0), mat("#C0302A"), origin=(0, 0, -0.5))
    W["co2ic"] = ic = group("co2ic", (0, 0, 0))
    Bi = Batch("ic_b", ic, 1.0)
    cone(Bi, O_D[0]-3.6, O_D[1]+5.0, 1.2, 0.8, 4)
    Bi.add((O_D[0]+3.9, O_D[1]+5.5, 0.9), (1.4, 1.2, 1.8), "#7A7A82"); Bi.add((O_D[0]+4.3, O_D[1]+5.5, 2.4), (0.35, 0.35, 1.4), "#9A9AA2")
    Bi.add((O_D[0]+3.5, O_D[1]+5.5, 2.1), (0.3, 0.3, 0.8), "#9A9AA2")
    Bi.done()
    W["car"] = car("carco2", "#2E78BC")
    W["fumes"] = [(box(f"fm{q}", (0, 0, 0), (0.5, 0.5, 0.5), mat("#5A5654")), r.uniform(0, 1)) for q in range(20)]
    # ---------------- campo y aeródromo ----------------
    W["field"] = g = group("field", O_F)
    B = Batch("field_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("soil", "#7A5A3A", 16, 0.10, 61))
    B.add((14, 0, 0.0), (8, 200, 0.06), tmat("runway", "#4A4A50", 16, 0.05, 62, asphalt))
    for y in range(-40, 41, 6): B.add((14, y, 0.04), (0.3, 3.0, 0.02), "#E8E4DA")
    B.add((24, 4, 2.5), (8, 6, 5), "#B8B0A0"); B.add((24, 4, 5.2), (8.4, 6.4, 0.4), "#5A5A62")
    B.done()
    W["cropg"] = Batch("cropg_b", None, 1.0); W["cropb"] = Batch("cropb_b", None, 1.0)
    for x in range(-8, 9):
        for y in range(-6, 12):
            h = 0.6+0.2*math.sin(x*1.7+y)
            W["cropg"].add((O_F[0]+x*0.7, O_F[1]+y*0.9, h/2), (0.3, 0.3, h), "#6AB040" if (x+y) % 3 else "#8AC850")
            W["cropb"].add((O_F[0]+x*0.7, O_F[1]+y*0.9, h*0.3/2), (0.34, 0.34, h*0.3), "#8A6A3A" if (x+y) % 3 else "#6A5030")
    W["cropg"] = W["cropg"].done(); W["cropb"] = W["cropb"].done()
    W["plane"] = pn = group("plane", (O_F[0]+14, O_F[1]+6, 0))
    Bp = Batch("plane_b", pn, 1.0)
    Bp.add((0, 0, 1.6), (1.6, 9, 1.6), "#F4F1EA"); Bp.add((0, -4.8, 1.6), (1.2, 0.8, 1.2), "#F4F1EA")
    Bp.add((0, 0.5, 1.4), (12, 2.0, 0.25), "#E0DCD2"); Bp.add((0, 4.3, 3.0), (0.25, 1.4, 2.0), "#C0302A")
    Bp.add((0, 4.3, 1.9), (4, 1.0, 0.2), "#E0DCD2")
    for y in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0):
        for sx in (-1, 1): Bp.add((sx*0.81, y, 1.9), (0.04, 0.4, 0.3), "#5A8AB8")
    for sx in (-1, 1): Bp.add((sx*3.2, 0.2, 1.1), (0.9, 1.6, 0.8), "#9A9AA2")
    for x, y in ((0, -3.2), (-1.5, 0.6), (1.5, 0.6)): Bp.add((x, y, 0.35), (0.4, 0.5, 0.7), "#1C1C20")
    Bp.done()
    W["planeash"] = box("planeash", (O_F[0]+14, O_F[1]+6, 2.4), (1.7, 9.2, 1.0), mat("#8E8A86"), origin=(0, 0, -0.5))
    W["snowground"] = box("snowground", (O_F[0], O_F[1], 0.0), (300, 300, 1.0), mat("#F4F6F8"), origin=(0, 0, -0.5))
    W["sun"] = box("sun", (0, 0, 0), (6, 6, 6), mat("#FFF2A8"))
    # ---------------- personaje ----------------
    W["lucas"] = Person("lucas", LUCAS)
    camera(28)
    return W

def hide_all(W):
    for k in ("globe", "stars", "town", "house", "vl", "vr", "data", "tambora", "thermo", "co2ic", "car", "field", "cropg", "cropb", "plane"): show(W[k], False)
    for k in ("roof", "ashroof", "ashground", "lavacol", "lavacore", "tplume", "merc", "mercb", "barv", "barh", "planeash", "snowground", "sun"): hid(W[k], True)
    for lst in ("bombs", "smoke", "flakes", "snow", "fumes"):
        for it in W[lst]: hid(it[0], True)
    for o in W["flow"]: hid(o, True)
    W["lucas"].show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

# ---------------- utilidades de plano ----------------
def globe(W, T, erupt=1.0, ashk=0.0, rot=0.25):
    show(W["globe"], True); show(W["stars"], True)
    W["globe"].rotation_euler = (0.35, 0, T*rot)
    for pl, ph in W["plumes"]:
        k = clamp((erupt-ph*0.6)/0.4) if erupt < 1.0 else 1.0
        hid(pl, k <= 0.01)
        s = max(0.01, k*(1.0+0.35*math.sin(T*9+ph*20)))
        pl.scale = (1, 1, s*1.6)
    for a, ph in W["ash"]:
        k = clamp((ashk-ph*0.7)/0.3)
        hid(a, k <= 0.01); s = max(0.01, k); a.scale = (s, s, s)

def erupt_mountain(W, T, t_open, split=1.0, bombs=True, smoke=0.0):
    VY = O_T[1]+48
    show(W["vl"], True); show(W["vr"], True)
    W["vl"].location = (-6.0*split, VY, 0); W["vr"].location = (6.0*split, VY, 0)
    if split > 0.05:
        hid(W["lavacol"], False); hid(W["lavacore"], False)
        h = 16+14*split+2.5*math.sin(T*11)
        W["lavacol"].scale = (0.6+0.6*split, 1, h); W["lavacore"].scale = (0.5+0.4*split, 1, h*1.05)
    if bombs and split > 0.05:
        for o, vx, vy, v, ph in W["bombs"]:
            tt = ((T-t_open)*0.9+ph) % 3.0
            hid(o, False)
            o.location = (vx*9*tt*v, VY+vy*6*tt, 28+22*v*tt-9.8*tt*tt*1.4)
            o.rotation_euler = (tt*3, tt*2, 0)
            if o.location.z < 0: hid(o, True)
    if smoke > 0:
        for o, a, b, ph in W["smoke"]:
            tt = (T*0.12+ph) % 1.0
            hid(o, False); s = (0.8+3.0*tt)*smoke
            o.scale = (s, s, s); o.location = (a*12*tt*2.2, VY+b*8*tt+4, 34+tt*30)

def fall(W, key, T, center, area=(9, 9, 7), speed=1.2, n=None, drift=0.3):
    lst = W[key] if n is None else W[key][:n]
    for o, a, b, ph in lst:
        z = area[2]*(1-((T*speed/area[2]+ph) % 1.0))
        hid(o, False)
        o.location = (center[0]+a*area[0]/2+math.sin(T*1.3+ph*9)*drift, center[1]+b*area[1]/2, center[2]+z)

def town(W, dusk=0.0):
    show(W["town"], True); show(W["house"], True); hid(W["roof"], False)
    world_color(lerpv(hexc("#9CC8E8"), hexc("#3A2A2A"), dusk)); light_dir((0.45, -0.55, 0.7)); shadow(0.5)

def lucas(W, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    H = W["lucas"]; H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_)
    return H

# ------------------------------------------------------------------ planos
@shot(0.0, 3.46)
def v1(W, T, M):
    world_color("#05060C"); light_dir((0.6, -0.5, 0.6)); shadow(0.3)
    k = T/3.46
    globe(W, T, erupt=clamp(0.15+k*1.1))
    look(lerpv((0, -22, 4), (0, -16.5, 2.5), eio(k)), (0, 0, 0), 30)
    M["grade"] = "night"

@shot(3.46, 7.44)
def v2(W, T, M):
    world_color("#05060C"); light_dir((0.6, -0.5, 0.6)); shadow(0.3)
    k = (T-3.46)/3.98
    globe(W, T, erupt=1.0, rot=0.25+0.5*clamp((T-5.7)/0.3))
    sx_, sy_, sz_ = shake(T, 0.12 if 5.76 < T < 6.6 else 0.0)
    look(lerpv((8, -18, 7), (4, -13.5, 3), eio(k)), (0.0+sx_, sy_, sz_), 32)
    if 5.76 < T < 5.86: M["flash"] = 1
    M["grade"] = "night"

@shot(7.44, 12.0)
def v3(W, T, M):
    town(W, 0.5); k = (T-7.44)/4.56
    split = eio(clamp((T-7.9)/1.3))
    erupt_mountain(W, T, 7.9, split, smoke=0.6*split)
    H = lucas(W, 1.0, O_T[1]-4.5, 180, T, "shock" if T > 8.3 else "neutral", (0, 0.5))
    H.arm(1, fwd=1.4*clamp((T-9.9)/0.4), side=0.1, elbow=0.1)
    sx_, sy_, sz_ = shake(T, 0.08 if 8.0 < T < 9.6 else 0.01)
    look(lerpv((2.4+sx_, O_T[1]-8.6+sy_, 1.2+sz_), (2.2, O_T[1]-7.8, 1.25), eio(k)), (0.0, O_T[1]+30, lerp(10, 15, k)), lerp(20, 24, k))
    if 7.95 < T < 8.05: M["flash"] = 1
    M["grade"] = "night"

@shot(12.0, 15.3)
def v4(W, T, M):
    town(W, 0.55); k = (T-12.0)/3.3
    erupt_mountain(W, T, 7.9, 1.0, bombs=False, smoke=0.8)
    front = O_T[1]+6.0-0.9*(T-12.0)
    for q, o in enumerate(W["flow"]):
        row, col_ = q//6, q % 6
        y = front+row*1.0+0.2*math.sin(q*1.7)
        hid(o, False); o.location = (-2.5+col_*1.0, y, 0.15+0.06*math.sin(T*3+q))
    wk = T*1.6
    H = W["lucas"]; H.show(True); H.place(0.6, O_T[1]-1.0-0.9*(T-12.0), 0); H.walk(wk); H.face(T, "worried", (0.6, 0))
    look(lerpv((2.6, O_T[1]-11.0, 1.4), (2.2, O_T[1]-12.5, 1.6), eio(k)), (0.0, O_T[1]+4.0, 2.2), 24)
    M["grade"] = "night"

@shot(15.3, 20.56)
def v5(W, T, M):
    town(W, 0.75); k = (T-15.3)/5.26
    erupt_mountain(W, T, 7.9, 1.0, bombs=False, smoke=1.0)
    c = (O_T[0]+4.0, O_T[1]-0.5, 0.0)
    fall(W, "flakes", T, c, (14, 12, 8), 1.0)
    acc = clamp((T-15.3)/4.0)
    ar = W["ashroof"]; hid(ar, False)
    col = 19.4
    if T < col:
        ar.scale = (1, 1, 0.05+0.9*acc); ar.location = (O_T[0]+7.5, O_T[1]+0.5, 3.6); W["roof"].location.z = 3.4; W["roof"].rotation_euler = (0, 0, 0)
    else:
        f = eio(clamp((T-col)/0.5))
        W["roof"].location.z = lerp(3.4, 1.0, f); W["roof"].rotation_euler = (0, 0.35*f, 0)
        ar.scale = (1, 1, 0.95); ar.location = (O_T[0]+7.5, O_T[1]+0.5, lerp(3.6, 1.2, f)); ar.rotation_euler = (0, 0.35*f, 0)
    ag = W["ashground"]; hid(ag, False); ag.scale = (1, 1, 0.02+0.12*acc)
    H = lucas(W, 3.0, O_T[1]-3.5, 180+40*clamp((T-19.2)/0.5), T, "worried" if T < 19.3 else "shock", (0.3, 0.6))
    for sx in (-1, 1): H.arm(sx, fwd=2.6, side=0.3, elbow=1.9)
    sx_, sy_, sz_ = shake(T, 0.06 if col < T < col+0.6 else 0.0)
    look((lerp(-0.5, 0.2, k)+sx_, O_T[1]-11.5+sy_, 2.0+sz_), (4.8, O_T[1]-0.5, 2.0), 26)
    if col+0.35 < T < col+0.42: M["flash"] = 1
    M["grade"] = "day_sad"

@shot(20.56, 26.9)
def v6(W, T, M):
    show(W["data"], True); show(W["tambora"], True); show(W["thermo"], True)
    world_color("#1C2230"); light_dir((0.4, -0.6, 0.7)); shadow(0.5); k = (T-20.56)/6.34
    tp = W["tplume"]; hid(tp, False); tp.scale = (1+1.5*clamp((T-21.0)/2), 1+1.5*clamp((T-21.0)/2), 0.1+3.5*eio(clamp((T-21.0)/2.5)))
    d = eio(clamp((T-24.6)/1.6))
    hid(W["merc"], False); W["merc"].scale = (1, 1, lerp(2.4, 0.01, d))
    hid(W["mercb"], d < 0.05); W["mercb"].scale = (1, 1, max(0.01, 1.2*d)); W["mercb"].location.z = 0.7
    W["merc"].location.z = 0.7+1.2*d
    look(lerpv((-0.2, O_D[1]-14.0, 3.4), (-0.2, O_D[1]-12.0, 2.9), eio(k)), (-0.2, O_D[1], 1.9), 26)
    M["grade"] = "lab"

@shot(26.9, 28.96)
def v7(W, T, M):
    show(W["field"], True); show(W["cropg"], True); world_color("#C8D8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-26.9)/2.06
    fall(W, "snow", T, (O_F[0], O_F[1]-1, 0), (10, 10, 6), 0.9)
    sg = W["snowground"]; hid(sg, False); sg.scale = (1, 1, 0.05+0.3*k)
    hid(W["sun"], False); W["sun"].location = (O_F[0]+8, O_F[1]+60, 26)
    H = lucas(W, 0.0, O_F[1]-3.0, 0, T, "shock", (0, 0.7))
    H.arm(1, fwd=1.6, side=0.3, elbow=0.3); H.fingers(1, 0.2, 0.1)
    look(lerpv((1.6, O_F[1]-7.5, 1.4), (1.1, O_F[1]-6.5, 1.5), eio(k)), (0.0, O_F[1]-2.0, 1.6), 26)
    M["grade"] = "cold"

@shot(28.96, 34.86)
def v8(W, T, M):
    k = (T-28.96)/5.9
    world_color(lerpv(hexc("#0A0C14"), hexc("#020203"), k)); light_dir((0.6, -0.5, 0.6)); shadow(0.3)
    globe(W, T, erupt=1.0, ashk=clamp((T-31.3)/2.6), rot=0.3)
    look(lerpv((0, -14, 2), (0, -20, 5), eio(k)), (0, 0, 0), 30)
    M["grade"] = "night"

@shot(34.86, 40.58)
def v9(W, T, M):
    show(W["field"], True); show(W["plane"], True)
    k = (T-34.86)/5.72
    world_color("#4A4440"); light_dir((0.3, -0.5, 0.8)); shadow(0.25)
    wilt = eio(clamp((T-35.0)/1.0))
    show(W["cropg"], wilt < 0.5); show(W["cropb"], wilt >= 0.5)
    fall(W, "flakes", T, (O_F[0]+4, O_F[1]-2, 0), (16, 14, 8), 1.0)
    pa = W["planeash"]; hid(pa, T < 36.4); pa.scale = (1, 1, 0.05+0.25*clamp((T-36.4)/1.5))
    sg = W["snowground"]; hid(sg, T < 38.2); sg.scale = (1, 1, 0.02+0.25*clamp((T-38.2)/2))
    if T < 36.45:
        look(lerpv((0.0, O_F[1]-9.0, 3.2), (0.5, O_F[1]-8.0, 2.6), eio(clamp((T-34.86)/1.6))), (0.0, O_F[1]+1.0, 0.3), 26)
    elif T < 38.3:
        look(lerpv((6.0, O_F[1]-10.0, 2.5), (7.0, O_F[1]-9.0, 2.8), eio(clamp((T-36.45)/1.9))), (O_F[0]+14, O_F[1]+4, 1.8), 24)
    else:
        H = lucas(W, 2.0, O_F[1]-3.0, 0, T, "scared", (0, 0.2))
        for sx in (-1, 1): H.arm(sx, fwd=0.9, side=-0.3, elbow=2.0)
        H.chest.rotation_euler = (0.05*math.sin(T*40), 0, 0)
        look(lerpv((3.2, O_F[1]-7.5, 1.5), (2.8, O_F[1]-6.5, 1.55), eio(clamp((T-38.3)/2.2))), (2.0, O_F[1]-3.0, 1.4), 26)
    M["grade"] = "cold"

def co2_room(W):
    show(W["data"], True); show(W["co2ic"], True)
    world_color("#1C2230"); light_dir((0.4, -0.6, 0.7)); shadow(0.5)

@shot(40.58, 47.96)
def v10(W, T, M):
    co2_room(W); k = (T-40.58)/7.38
    bv = W["barv"]; hid(bv, False); bv.scale = (1, 1, 0.02+0.23*eio(clamp((T-42.8)/1.0)))
    hid(W["barh"], False); W["barh"].scale = (1, 1, 0.02)
    for o, ph in W["fumes"][:8]:
        tt = (T*0.4+ph) % 1.0; hid(o, False); s = 0.4+0.8*tt; o.scale = (s, s, s)
        o.location = (O_D[0]-3.6+0.3*math.sin(ph*9), O_D[1]+5.0, 0.9+2.5*tt)
    if T < 42.6:
        look(lerpv((-1.0, O_D[1]-7.0, 3.0), (-1.6, O_D[1]-3.0, 1.8), eio(clamp((T-40.58)/2.0))), (-2.4, O_D[1]+5.5, 0.6), 28)
    else:
        look(lerpv((-1.6, O_D[1]-3.0, 1.8), (-1.2, O_D[1]-1.2, 1.2), eio(clamp((T-42.6)/5.3))), (-2.4, O_D[1]+5.4, 0.5), 30)
    M["grade"] = "lab"

@shot(47.96, 52.6)
def v11(W, T, M):
    co2_room(W); k = (T-47.96)/4.64
    hid(W["barv"], False); W["barv"].scale = (1, 1, 0.25)
    g = eio(clamp((T-48.4)/3.4))
    bh = W["barh"]; hid(bh, False); bh.scale = (1, 1, 0.02+14.98*g)
    cr = W["car"]; show(cr, True); cr.location = (O_D[0]+4.2, O_D[1]+2.8, 0); cr.rotation_euler = (0, 0, 0.3)
    for o, ph in W["fumes"]:
        tt = (T*0.5+ph) % 1.0; hid(o, False); s = 0.5+1.2*tt; o.scale = (s, s, s)
        o.location = (O_D[0]+4.3+0.4*math.sin(ph*7), O_D[1]+5.5, 3.1+5.0*tt)
    look(lerpv((0.0, O_D[1]-5.0, 1.0), (0.0, O_D[1]-14.0, 4.0+4.0*g), eio(k)), (0.6, O_D[1]+6.0, 0.6+7.0*g), lerp(26, 22, k))
    M["grade"] = "alarm" if T > 50.5 else "lab"

@shot(52.6, 57.5)
def v12(W, T, M):
    show(W["field"], True); show(W["cropb"], True)
    k = (T-52.6)/4.9
    clear = eio(clamp((T-52.8)/2.0))
    world_color(lerpv(hexc("#4A4440"), hexc("#F0B070"), clear)); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
    sg = W["snowground"]; hid(sg, clear > 0.9); sg.scale = (1, 1, max(0.01, 0.27*(1-clear)))
    if clear < 0.7: fall(W, "flakes", T, (O_F[0], O_F[1]-2, 0), (12, 12, 8), 1.0, n=int(220*(1-clear)))
    hid(W["sun"], False); W["sun"].location = (O_F[0]+6, O_F[1]+60, lerp(10, 22, clear)); W["sun"].scale = (1+0.6*clear,)*3
    H = lucas(W, 0.0, O_F[1]-3.0, 0, T, "worried" if T < 55.5 else "scared", (0, 0.6))
    H.arm(1, fwd=2.2, side=0.2, elbow=1.9); H.fingers(1, 0.2, 0.2)
    look(lerpv((0.8, O_F[1]-8.0, 1.1), (0.5, O_F[1]-6.4, 1.4), eio(k)), (0.0, O_F[1]-2.0, 1.9), 26)
    M["grade"] = "day_sad" if clear < 0.5 else "alarm"

@shot(57.5, TOTAL+0.1)
def v13(W, T, M):
    k = (T-57.5)/5.81
    world_color("#05060C"); light_dir((0.6, -0.5, 0.6)); shadow(0.3)
    globe(W, T, erupt=1.0, ashk=1.0-eio(clamp((T-58.0)/3.0)), rot=0.35)
    look(lerpv((0, -15, 6), (0, -19, 2), eio(k)), (0, 0, 0), 30)
    M["grade"] = "night"; M["fade"] = clamp((T-62.9)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
