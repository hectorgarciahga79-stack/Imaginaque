"""Q12 · «¿Qué pasaría si mañana la Tierra fuera un cubo?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral). Tiempos de plano = palabras del ASR (68,2 s).
Decorados propios: planeta-cubo de vóxeles (seco / con 6 océanos redondos / agrietado de lava), Tierra esférica,
cubo en alambre con distancias, llanura con lago (y=200), esquina fuera de la atmósfera (y=400),
escala Everest vs esquina (y=600), mini planeta-cubo final (y=800). Protagonista original: Mateo (sudadera naranja)."""
import math, random
from vox import *
from mathutils import Vector
from person import Person
from world import Batch, tmat, tree

FPS = 24
TOTAL = 68.2
MATEO = dict(skin="#F0C8A0", hair="#2A1E18", hair2="#3A2A20", eye="#2A1A10", top="#E8762A", top2="#C05A1A", stripe="#F4F1EA",
             legs="#2E3A52", legs2="#242E42", shoe="#F4F1EA", shoe2="#2A2A2E", watch=False, hstyle="short")

class Env:
    def talk(self, who, T): return 0.0

O_G = (0, 200, 0); O_C = (0, 400, 0); O_D = (0, 600, 0); O_E = (0, 800, 0)
LAVA = ["#FF5A14", "#FF8A20", "#FFC440"]

def noise(u):
    return math.sin(u.x*2.3+1.3)*math.cos(u.y*1.9-0.4) + 0.7*math.sin(u.z*3.0+u.x*1.7+u.y*2.2) + 0.5*math.cos(u.y*3.3-u.z*1.1)

def cube_planet(name, half, st, mode, parent=None, dry_top=False):
    B = Batch(name, parent, 1.0)
    n = int(round(2*half/st))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if not (i in (0, n-1) or j in (0, n-1) or k in (0, n-1)): continue
                p = Vector(((i+0.5)*st-half, (j+0.5)*st-half, (k+0.5)*st-half))
                ax = max(range(3), key=lambda q: abs(p[q]))
                a, b = [p[q]/half for q in range(3) if q != ax]
                r = max(abs(a), abs(b)); d = math.hypot(a, b)
                u = p.normalized(); v = noise(u)
                if mode == "earth" or (dry_top and ax == 2 and p.z > 0):
                    if dry_top and ax == 2 and p.z > 0: col = "#6AA048" if v > -0.6 else "#8A7A5A"
                    elif abs(u.z) > 0.9: col = "#EEF4F8"
                    elif v > -0.05: col = "#5A9A44" if v < 0.9 else "#8A7A5A"
                    else: col = "#2E6EB8"
                elif mode == "ocean":
                    if d < 0.24: col = "#245EA8"
                    elif d < 0.42: col = "#2E6EB8" if (i+j+k) % 5 else "#3A7EC8"
                    elif d < 0.5: col = "#E8D8A0"
                    elif r < 0.7: col = "#5A9A44" if v > -0.4 else "#6AA84E"
                    elif r < 0.84: col = "#8A7A5A"
                    elif abs(a) > 0.86 and abs(b) > 0.86: col = "#5E5A56"
                    else: col = "#9A968E"
                else:  # lava
                    crack = abs(a) < 0.07 or abs(b) < 0.07 or abs(abs(a)-abs(b)) < 0.06 or r > 0.93
                    col = LAVA[(i+j+k) % 3] if crack else ("#3A3230" if (i*3+j+k) % 4 else "#4A3E3A")
                B.add(tuple(p), (st, st, st), col)
    return B.done()

def sphere_planet(name, R, st, mode, parent=None):
    B = Batch(name, parent, 1.0)
    n = int(R/st)+1
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            for k in range(-n, n+1):
                p = Vector((i, j, k))*st; d = p.length
                if not (R-st*0.95 < d <= R): continue
                u = p.normalized(); v = noise(u)
                if mode == "earth":
                    if abs(u.z) > 0.88: col = "#EEF4F8"
                    elif v > -0.05: col = "#5A9A44" if v < 0.9 else "#8A7A5A"
                    else: col = "#2E6EB8"
                else:
                    col = LAVA[(i+j+k) % 3] if v > 0.3 or abs(v) < 0.12 else "#3A3230"
                B.add(tuple(p), (st, st, st), col)
    return B.done()

def arrow(name, col="#E8402A", L=2.4, w=0.22):
    g = group(name, (0, 0, 0))
    B = Batch(name+"_b", g, 1.0)
    B.add((0, 0, -L/2), (w, w, L), col)
    for q, s in enumerate((0.8, 0.6, 0.4, 0.2)):
        B.add((0, 0, -L-0.12-q*0.16), (s, s, 0.16), col)
    B.done()
    return g   # apunta hacia -Z

def orient(o, d):
    """orienta un objeto que apunta a -Z hacia la dirección d"""
    o.rotation_euler = (-Vector(d)).normalized().to_track_quat('Z', 'Y').to_euler()

def cone(B, cx, cy, base, h, n=7, cols=("#7A7672", "#6A6662"), cap=None):
    for l in range(n):
        s = base*(1-l/(n+0.6)); z = h*l/n + h/n/2
        c = cap if (cap and l >= n-2) else cols[l % 2]
        B.add((cx, cy, z), (s, s, h/n), c)

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(12)
    # ---------------- espacio ----------------
    W["stars"] = Batch("stars_b", None, 1.0)
    for q in range(220):
        W["stars"].add((r.uniform(-80, 80), r.uniform(30, 50), r.uniform(-80, 80)), (0.14, 0.14, 0.14), "#FFFFFF")
    W["stars"] = W["stars"].done()
    W["sp_earth"] = g = group("sp_earth"); sphere_planet("sph_e", 6.2, 0.5, "earth", g)
    W["sp_lava"] = g = group("sp_lava"); sphere_planet("sph_l", 6.2, 0.5, "lava", g)
    W["c_earth"] = g = group("c_earth"); cube_planet("cub_e", 5.0, 0.5, "earth", g)
    W["c_dry"] = g = group("c_dry"); cube_planet("cub_d", 5.0, 0.5, "earth", g, dry_top=True)
    W["c_ocean"] = g = group("c_ocean"); cube_planet("cub_o", 5.0, 0.5, "ocean", g)
    W["c_lava"] = g = group("c_lava"); cube_planet("cub_l", 5.0, 0.5, "lava", g)
    W["corners"] = [box(f"cor{q}", (sx*5.1, sy*5.1, sz*5.1), (0.9, 0.9, 0.9), mat("#FF3A2A"))
                    for q, (sx, sy, sz) in enumerate([(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)])]
    W["cbase"] = [tuple(o.location) for o in W["corners"]]
    # agua que corre al centro de la cara de arriba
    cells = [(x, y) for x in range(-6, 6) for y in range(-6, 6) if math.hypot(x+0.5, y+0.5) < 5.2]
    W["water"] = []
    used = set()
    for q, (x, y) in enumerate(cells):
        while True:
            sx_, sy_ = r.randint(-9, 8), r.randint(-9, 8)
            if (sx_, sy_) not in used and math.hypot(sx_+0.5, sy_+0.5) > 4.5: used.add((sx_, sy_)); break
        o = box(f"wat{q}", (0, 0, 0), (0.5, 0.5, 0.5), mat("#2E6EB8" if q % 4 else "#3A7EC8"))
        W["water"].append((o, ((sx_+0.5)*0.5, (sy_+0.5)*0.5), ((x+0.5)*0.5, (y+0.5)*0.5), math.hypot(sx_, sy_)))
    W["garrows"] = []
    for q, (x, y) in enumerate(((-3.6, 0), (3.6, 0), (0, -3.6), (0, 3.6))):
        a = arrow(f"ga{q}", "#FFD040", 1.6, 0.16); a.location = (x, y, 8.2); orient(a, (-x, -y, -8.2)); W["garrows"].append(a)
    # cubo de alambre + distancias
    W["wire"] = g = group("wire")
    Bw = Batch("wire_b", g, 1.0)
    for ax in range(3):
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                c = [0, 0, 0]; sz = [0.12, 0.12, 0.12]; c[ax] = 0; sz[ax] = 10.12
                o1, o2 = [q for q in range(3) if q != ax]; c[o1] = s1*5; c[o2] = s2*5
                Bw.add(tuple(c), tuple(sz), "#DDE6F0")
    Bw.add((0, 0, 0), (0.5, 0.5, 0.5), "#FFD040")
    Bw.done()
    W["wface"] = box("wface", (0, 0, -5.0), (10, 10, 0.06), mat("#2E6EB8"))
    W["bar_f"] = box("bar_f", (0, 0, 0), (0.32, 0.32, 1.0), mat("#4AD06A"), origin=(0, 0, -0.5))
    W["bar_f"].rotation_euler = (math.pi, 0, 0)
    W["bar_c"] = box("bar_c", (0, 0, 0), (0.32, 0.32, 1.0), mat("#FF3A2A"), origin=(0, 0, -0.5))
    W["bar_c"].rotation_euler = Vector((1, -1, 1)).normalized().to_track_quat('Z', 'Y').to_euler()
    W["dot_f"] = box("dot_f", (0, 0, -5.0), (0.6, 0.6, 0.6), mat("#4AD06A"))
    W["dot_c"] = box("dot_c", (5, -5, 5), (0.7, 0.7, 0.7), mat("#FF3A2A"))
    # ---------------- llanura con lago (cara) ----------------
    W["plain"] = g = group("plain", O_G)
    B = Batch("plain_b", g, 1.0)
    B.add((0, 0, -0.06), (400, 400, 0.1), tmat("grass12", "#5A9A44", 16, 0.10, 121))
    for x in range(-14, 15):
        for y in range(-4, 30):
            d = math.hypot(x, y-12)
            if d < 9: B.add((x*1.0, y*1.0, -0.02), (1.0, 1.0, 0.06), "#2E6EB8" if (x+y) % 5 else "#3A7EC8")
            elif d < 10.5: B.add((x*1.0, y*1.0, -0.01), (1.0, 1.0, 0.06), "#E8D8A0")
    for q in range(14): tree(B, r.uniform(-30, 30), r.uniform(25, 60), r.uniform(2.2, 3.4), q)
    for q in range(16): tree(B, r.choice((-1, 1))*r.uniform(12, 30), r.uniform(-10, 20), r.uniform(2.2, 3.2), q+20)
    for q in range(8):  # rocas camino al borde (derecha)
        B.add((14+q*6+r.uniform(-1, 1), r.uniform(-6, 6), 0.3), (r.uniform(0.6, 1.4),)*2+(0.6,), "#8A7A5A")
    B.done()
    W["garrow"] = arrow("garrow", "#FFD040", 1.4, 0.14)
    # ---------------- esquina sin aire ----------------
    W["corner"] = g = group("corner", O_C)
    B = Batch("corner_b", g, 1.0)
    cone(B, 0, 0, 30, 16, 10, ("#7A7672", "#6A6662"))
    B.add((0, 0, -0.5), (300, 300, 1.0), "#5E5A56")
    B.done()
    W["c_stars"] = Batch("cstars_b", None, 1.0)
    for q in range(200):
        W["c_stars"].add((r.uniform(-90, 90), O_C[1]+r.uniform(40, 70), r.uniform(-10, 90)), (0.16, 0.16, 0.16), "#FFFFFF")
    W["c_stars"] = W["c_stars"].done()
    W["c_globe"] = box("c_glow", (-30, O_C[1]+60, -6), (40, 4, 14), mat("#5A8ACC"))
    # ---------------- escala: Everest vs esquina ----------------
    W["scale"] = g = group("scale", O_D)
    B = Batch("scale_b", g, 1.0)
    B.add((0, 0, -0.05), (900, 900, 0.1), tmat("dfl12", "#2E3644", 16, 0.05, 125))
    cone(B, 0, 0, 0.7, 0.32, 6, ("#8A8682", "#7A7672"), "#F4F6F8")
    B.add((0, 0, 0.42), (0.01, 0.01, 0.16), "#2A2A2E"); B.add((0.025, 0, 0.47), (0.05, 0.005, 0.035), "#E8402A")
    cone(B, 0, 140, 260, 138, 14, ("#7A7672", "#6A6662"), "#5E5A56")
    B.done()
    # ---------------- mini planeta final ----------------
    W["mini"] = g = group("mini", O_E); cube_planet("cub_m", 1.6, 0.2, "ocean", g)
    W["m_stars"] = Batch("mstars_b", None, 1.0)
    for q in range(200):
        W["m_stars"].add((r.uniform(-60, 60), O_E[1]+r.uniform(25, 45), r.uniform(-60, 60)), (0.12, 0.12, 0.12), "#FFFFFF")
    W["m_stars"] = W["m_stars"].done()
    # ---------------- personaje ----------------
    W["mateo"] = Person("mateo", MATEO)
    camera(28)
    return W

GROUPS = ("stars", "sp_earth", "sp_lava", "c_earth", "c_dry", "c_ocean", "c_lava", "wire", "plain", "garrow", "corner", "c_stars",
          "scale", "mini", "m_stars")
def hide_all(W):
    for k in GROUPS: show(W[k], False)
    W["plain"].rotation_euler = (0, 0, 0); W["garrow"].scale = (1, 1, 1)
    for o in W["corners"]: hid(o, True)
    for o, *_ in W["water"]: hid(o, True)
    for a in W["garrows"]: show(a, False)
    for k in ("wface", "bar_f", "bar_c", "dot_f", "dot_c", "c_globe"): hid(W[k], True)
    W["mateo"].show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def space(M):
    world_color("#05060C"); light_dir((0.6, -0.5, 0.6)); shadow(0.3); M["grade"] = "night"

def planet(W, key, T, rot=(0.45, 0.0, 0.3), scale=1.0, base=0.0):
    g = W[key]; show(g, True); show(W["stars"], True)
    g.rotation_euler = (rot[0], rot[1], base+T*rot[2]); g.scale = (scale,)*3

def mateo(W, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    H = W["mateo"]; H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_)
    return H

# ------------------------------------------------------------------ planos
@shot(0.0, 3.0)
def v1(W, T, M):
    space(M); k = T/3.0
    planet(W, "c_earth", T, (0.62, 0.0, 0.5), base=0.6)
    look(lerpv((0, -48, 9), (0, -36, 5), eio(k)), (0, 0, 0), 30)

@shot(3.0, 8.1)
def v2(W, T, M):
    space(M); k = (T-3.0)/5.1
    m = eio(clamp((T-4.5)/1.2))
    if m < 1: planet(W, "sp_earth", T, (0.62, 0.0, 0.4), scale=max(0.01, 1-m*0.25), base=0.6)
    if m > 0: planet(W, "c_earth", T, (0.62, 0.0, 0.4), scale=max(0.01, m), base=0.6)
    if 4.95 < T < 5.05: M["flash"] = 1
    if T > 6.9:
        for q, o in enumerate(W["corners"]):
            if T > 6.9+q*0.08:
                hid(o, False); s = 1+0.25*math.sin(T*10+q); o.scale = (s, s, s)
                o.location = W["c_earth"].rotation_euler.to_matrix() @ Vector(W["cbase"][q])
                o.rotation_euler = W["c_earth"].rotation_euler
    look(lerpv((0, -36, 5), (5, -35, 10), eio(k)), (0, 0, 0), 30)

@shot(8.1, 16.5)
def v3(W, T, M):
    space(M); k = (T-8.1)/8.4
    planet(W, "c_dry", 0, (0, 0, 0), base=0.0)
    for a in W["garrows"]:
        show(a, T > 10.7)
    for o, s_, e_, dd in W["water"]:
        f = eio(clamp((T-13.0-dd*0.04)/2.6))
        hid(o, False)
        o.location = (lerp(s_[0], e_[0], f), lerp(s_[1], e_[1], f), 5.25+0.06*math.sin(T*6+dd))
    look(lerpv((-3, -17, 19), (0, -13.5, 18), eio(k)), (0, 0.8, 4.6), 30)

@shot(16.5, 19.2)
def v4(W, T, M):
    space(M); k = (T-16.5)/2.7
    planet(W, "c_ocean", T, (0.62, 0.0, 0.7), base=0.3)
    look(lerpv((0, -32, 4), (0, -38, 8), eio(k)), (0, 0, 0), 30)

def plain(W, M, sky="#9CC8E8"):
    show(W["plain"], True); world_color(sky); light_dir((0.45, -0.55, 0.7)); shadow(0.5); M["grade"] = "day"

@shot(19.2, 24.3)
def v5(W, T, M):
    plain(W, M); k = (T-19.2)/5.1
    breathe = eio(clamp((T-20.9)/0.8))
    H = mateo(W, 0, O_G[1]+1.5, 0, T, "happy" if T > 21.0 else "neutral", (0, 0.3))
    for sx in (-1, 1): H.arm(sx, fwd=0.4*breathe, side=0.15+1.2*breathe, elbow=0.2)
    H.chest.rotation_euler = (0.12*breathe, 0, 0)
    look(lerpv((2.5, O_G[1]-6.5, 1.3), (1.4, O_G[1]-4.8, 1.6), eio(k)), (0.0, O_G[1]+3.0, 2.0), 26)

def ramp(W, M, T, u, roll, lean, walk_ph, expr, arms=None, cam_off=(0, 0)):
    """mundo inclinado: el suelo gira roll rad alrededor de Y (sube hacia +X); la gravedad sentida sigue hacia abajo"""
    plain(W, M); g = W["plain"]; g.rotation_euler = (0, -roll, 0)
    wx, wz = u*math.cos(roll), u*math.sin(roll)
    H = W["mateo"]; H.show(True); H.place(wx, O_G[1]-2.0, 90, wz); H.walk(walk_ph)
    if arms:
        for sx in (-1, 1): H.arm(sx, fwd=arms+0.15*math.sin(T*3.5+sx), side=0.1, elbow=0.7)
    H.face(T, expr, (0, 0.3))
    H.chest.rotation_euler = (lean, 0, 0)
    a = W["garrow"]; show(a, True); a.location = (wx+0.6, O_G[1]-3.6, wz+4.6); a.rotation_euler = (0, 0, 0)
    s_ = 1+0.12*math.sin(T*6); a.scale = (s_, s_, s_)
    look((wx-0.5+cam_off[0], O_G[1]-11.5, wz+2.4+cam_off[1]), (wx+1.0, O_G[1]-2.0, wz+1.8), 26)

@shot(24.3, 31.1)
def v6(W, T, M):
    k = (T-24.3)/6.8
    roll = math.radians(22*eio(clamp((T-27.4)/3.4)))
    ramp(W, M, T, 2.0+0.9*(T-24.3), roll, 0.35*roll/math.radians(22), (T-24.3)*1.3,
         "neutral" if T < 28.0 else "worried", cam_off=(lerp(0, 1.0, k), 0))

@shot(31.1, 35.8)
def v7(W, T, M):
    k = (T-31.1)/4.7
    roll = math.radians(lerp(22, 42, eio(clamp((T-31.1)/2.6))))
    ramp(W, M, T, 8.1+0.4*(T-31.1), roll, 0.6, (T-31.1)*0.6, "scared", arms=1.1, cam_off=(lerp(0, 0.6, k), 0.3))

@shot(35.8, 43.2)
def v8(W, T, M):
    space(M); k = (T-35.8)/7.4
    g = W["wire"]; show(g, True); show(W["stars"], True)
    hid(W["wface"], False)
    gf = eio(clamp((T-36.3)/1.2)); gc = eio(clamp((T-37.2)/1.6))
    hid(W["bar_f"], gf < 0.02); W["bar_f"].scale = (1, 1, max(0.01, 5.0*gf))
    hid(W["dot_f"], gf < 0.95)
    hid(W["bar_c"], gc < 0.02); W["bar_c"].scale = (1, 1, max(0.01, 8.66*gc))
    hid(W["dot_c"], gc < 0.95)
    if T > 39.4:
        p = 1+0.25*max(0, math.sin((T-39.4)*8)); W["dot_c"].scale = (p, p, p)
    a = 0.6+0.25*k
    look((math.sin(a)*28, -math.cos(a)*28, 10+2*k), (0.6, 0, 0.0), 30)

@shot(43.2, 48.4)
def v9(W, T, M):
    show(W["corner"], True); show(W["c_stars"], True); hid(W["c_globe"], False)
    world_color("#020306"); light_dir((0.8, -0.4, 0.45)); shadow(0.55); M["grade"] = "night"
    k = (T-43.2)/5.2
    H = mateo(W, 0, O_C[1]-1.0, 0, T, "scared" if T > 45.8 else "worried", (0, 0.5), z=16.0)
    if T > 45.8:
        for sx in (-1, 1): H.arm(sx, fwd=2.4, side=0.35, elbow=2.2)
    if k < 0.5:
        look(lerpv((0, O_C[1]-36, 4), (0, O_C[1]-26, 10), eio(k*2)), (0, O_C[1], lerp(10, 15, eio(k*2))), 30)
    else:
        look(lerpv((1.8, O_C[1]-7.5, 17.6), (1.3, O_C[1]-6.3, 17.6), eio((k-0.5)*2)), (0, O_C[1]-1.0, 17.7), 26)

@shot(48.4, 53.9)
def v10(W, T, M):
    show(W["scale"], True); world_color("#1C2230"); light_dir((0.4, -0.6, 0.7)); shadow(0.5); M["grade"] = "lab"
    k = eio(clamp((T-50.6)/3.1))
    pos = lerpv((0.25, O_D[1]-1.3, 0.35), (60, O_D[1]-230, 70), k)
    tgt = lerpv((0, O_D[1], 0.18), (0, O_D[1]+100, 50), k)
    look(pos, tgt, lerp(32, 26, k))

@shot(53.9, 56.0)
def v11(W, T, M):
    space(M); k = (T-53.9)/2.1
    planet(W, "c_ocean", T, (0.62, 0.0, 0.15), base=1.2)
    sx_, sy_, sz_ = shake(T, 0.03*k)
    look(lerpv((0, -40, 6), (0, -34, 5), eio(k)), (sx_, sy_, sz_), 30)
    M["grade"] = "night"

@shot(56.0, 64.0)
def v12(W, T, M):
    space(M); k = (T-56.0)/8.0
    m = eio(clamp((T-58.6)/3.6))
    if T < 63.1:
        planet(W, "c_lava", T, (0.62, 0.0, 0.3), scale=lerp(1.0, 0.72, m), base=1.2)
        if m > 0: planet(W, "sp_lava", T, (0.62, 0.0, 0.3), scale=max(0.01, lerp(0.55, 1.0, m)), base=1.2)
    else:
        planet(W, "sp_earth", T, (0.62, 0.0, 0.3), base=1.2)
    if 58.6 < T < 58.7 or 63.1 < T < 63.2: M["flash"] = 1
    amp = 0.25 if T < 61.5 else 0.08 if T < 63.1 else 0.0
    sx_, sy_, sz_ = shake(T, amp)
    look(lerpv((0, -40, 7), (0, -35, 4), eio(k)), (sx_, sy_, sz_), 30)
    M["grade"] = "alarm" if T < 63.1 else "night"

@shot(64.0, TOTAL+0.1)
def v13(W, T, M):
    space(M); k = (T-64.0)/4.2
    show(W["mini"], True); show(W["m_stars"], True)
    W["mini"].rotation_euler = (0, 0, 0)
    turn = eio(clamp((T-64.3)/0.8))
    H = mateo(W, 0.15, O_E[1]-0.2, lerp(140, 0, turn), T, "happy" if T < 65.8 else "smirk", (0, 0.1), z=1.6)
    if T > 65.8: H.arm(1, fwd=1.3, side=0.4, elbow=0.2); H.fingers(1, 0.2, 0.0)
    a = lerp(-0.35, 0.15, eio(k))
    look((math.sin(a)*9.5, O_E[1]-math.cos(a)*9.5, lerp(3.6, 2.9, k)), (0, O_E[1], 2.3), 30)
    M["fade"] = clamp((T-67.85)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
