"""Q28 · Mini historia «El invernadero de Nora» (3D de bloques, 76,7 s). Idea de Héctor: ¿y si el Sol se apagara lentamente?
Protagonista original: Nora (agricultora, chaleco naranja, pelo rubio oscuro). Vecinos del pueblo.
Decorados: campo con invernaderos y molinos (origen), interior del invernadero (y=300), espacio (y=600), calle nevada (world.City, y=0 desplazada x=+200),
súper vacío (y=900)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, City, building, tree, tiles, planks, asphalt, stripes, brick, text3d, car

FPS = 24
TOTAL = 76.7
NORA = dict(skin="#E0B08A", hair="#B08A4A", hair2="#9A7A3A", eye="#2A3A2A", top="#E07A30", top2="#C06020", stripe="#F4F1EA",
            legs="#3A4A3A", legs2="#2E3E2E", shoe="#5A3A20", shoe2="#5A3A20", watch=False, hstyle="long")

class Env:
    def talk(self, who, T): return 0.0

O_IN = (0, 300, 0); O_SP = (0, 600, 0); O_SM = (0, 900, 0)

def longhair(P, L):
    hs = 0.56*P.s; t = hs/2; Hm = mat(L["hair"])
    for sx in (-1, 1):
        box(f"{P.n}_lock{sx}", (sx*(t+0.03*P.s), -0.02*P.s, hs*0.25), (0.07*P.s, hs*0.9, hs*1.0), Hm, P.head)
    box(f"{P.n}_lockb", (0, t+0.03*P.s, hs*0.1), (hs+0.1*P.s, 0.07*P.s, hs*1.2), Hm, P.head)

def plants(B, x0, y0, n, col, seed, tom=True):
    r = random.Random(seed)
    for i in range(n):
        y = y0+i*0.9
        B.add((x0, y, 0.5), (0.5, 0.5, 1.0), col)
        if tom:
            for k in range(3): B.add((x0+r.uniform(-0.28, 0.28), y-0.27, r.uniform(0.3, 0.9)), (0.12, 0.08, 0.12), "#D83A2A")

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(28)
    # campo exterior
    W["farm"] = g = group("farm", (0, 0, 0)); B = Batch("farm_b", g, 1.0)
    B.add((0, 0, -0.05), (400, 400, 0.1), tmat("dirt", "#B89A70", 16, 0.12, 281))
    for k in range(-3, 4):
        x = k*7.0
        B.add((x, 12, 1.4), (6.0, 14, 2.8), "#D8E4E8"); B.add((x, 12, 2.85), (6.2, 14.2, 0.1), "#C8D4D8")
        for y in range(6, 19, 2): B.add((x, y, 1.4), (6.1, 0.06, 2.9), "#A8B4B8")
    B.add((0, 60, 6), (300, 2, 12), "#A89A80")
    B.done()
    W["snowg"] = box("snowg", (0, 0, 0.0), (400, 400, 0.08), mat("#F0F4F8"))
    W["turb"] = []
    for q in range(4):
        x = -18+q*12; tw = box(f"tw{q}", (x, 45, 9), (0.6, 0.6, 18), mat("#E8ECEE"))
        hub = empty(f"hub{q}", (x, 44.6, 18))
        for b_ in range(3):
            bl = box(f"bl{q}{b_}", (0, 0, 3.2), (0.3, 0.1, 6.4), mat("#F4F6F8"), hub, origin=(0, 0, -3.2)); bl.rotation_euler = (0, b_*2.094, 0)
        W["turb"].append((tw, hub))
    W["sun"] = box("sun28", (0, 0, 0), (6, 6, 6), mat("#FFE070"))
    W["sundim"] = box("sun28d", (0, 0, 0), (6, 6, 6), mat("#E07A30"))
    W["sundk"] = box("sun28k", (0, 0, 0), (6, 6, 6), mat("#8A3A20"))
    # tractor
    W["tractor"] = tr = group("tractor", (0, 0, 0)); T_ = Batch("tr_b", tr, 1.0)
    T_.add((0, 0, 1.0), (2.4, 1.4, 1.0), "#2E7A3A"); T_.add((-0.5, 0, 1.9), (1.2, 1.3, 1.0), "#9FD0E8"); T_.add((-0.5, 0, 2.45), (1.3, 1.4, 0.1), "#2E7A3A")
    for x, rr in ((-0.8, 0.75), (0.9, 0.5)):
        for y in (-0.8, 0.8): T_.add((x, y, rr), (rr*2, 0.4, rr*2), "#1C1C20")
    T_.done()
    W["beams"] = [box(f"beam{sx}", (0, 0, 0), (0.25, 0.25, 0.25), mat("#FFF2B0")) for sx in (-1, 1)]
    W["cone"] = [box(f"cone{q}", (0, 0, 0), (0.6+q*0.3, 0.5+q*0.25, 0.3+q*0.1), mat("#FFF6D0")) for q in range(5)]
    # interior invernadero
    W["in"] = g = group("in", O_IN); B = Batch("in_b", g, 1.0)
    B.add((0, 0, -0.05), (12, 30, 0.1), tmat("infl", "#8A6A4A", 16, 0.12, 282))
    B.add((0, 14, 1.6), (12, 0.1, 3.2), "#C8D8DC"); B.add((-5.9, 0, 1.6), (0.1, 30, 3.2), "#C8D8DC"); B.add((5.9, 0, 1.6), (0.1, 30, 3.2), "#C8D8DC")
    B.add((0, 0, 3.25), (12, 30, 0.08), "#D8E4E8")
    B.done()
    W["live"] = g3 = group("live", O_IN); B = Batch("live_b", g3, 1.0)
    for x in (-4.5, -2.0, 2.0, 4.5): plants(B, x, -6, 14, "#3A8A3A", 283+int(x))
    B.done()
    W["dead"] = g2 = group("dead", O_IN); B = Batch("dead_b", g2, 1.0)
    for x in (-4.5, -2.0, 2.0, 4.5): plants(B, x, -6, 14, "#8A6A30", 290+int(x), tom=False)
    B.done()
    W["lamps"] = [box(f"lamp{q}", (O_IN[0]+(-4.5, -2.0, 2.0, 4.5)[q % 4], O_IN[1]-6+(q//4)*3.0, O_IN[2]+2.6), (0.7, 0.4, 0.1), mat("#F070F0")) for q in range(20)]
    W["table"] = box("ltable", (O_IN[0], O_IN[1]+1.0, O_IN[2]+0.75), (1.2, 9.0, 0.08), mat("#8A6A4A"))
    W["plates"] = [box(f"pl{q}", (O_IN[0]+(-0.35 if q % 2 else 0.35), O_IN[1]-2.6+(q//2)*1.4, O_IN[2]+0.81), (0.3, 0.3, 0.03), mat("#F4F1EA")) for q in range(12)]
    # espacio
    W["sp"] = g = group("sp", O_SP); B = Batch("sp_b", g, 1.0)
    for q in range(140): B.add((r.uniform(-60, 60), r.uniform(30, 60), r.uniform(-40, 40)), (0.15, 0.15, 0.15), "#FFFFFF")
    B.done()
    W["earth"] = box("earth28", (0, 0, 0), (1.0, 1.0, 1.0), mat("#3A6AC8"))
    W["pulse"] = box("pulse28", (0, 0, 0), (1.2, 0.3, 0.3), mat("#FFF6D0"))
    # ciudad nevada / súper
    W["city"] = City()
    W["flakes"] = [box(f"fk{q}", (0, 0, 0), (0.06, 0.06, 0.06), mat("#FFFFFF")) for q in range(60)]
    W["sm"] = g = group("sm", O_SM); B = Batch("sm_b", g, 1.0)
    B.add((0, 0, -0.05), (20, 20, 0.1), tmat("smfl", "#D8D8D0", 16, 0.04, 284, tiles)); B.add((0, 6, 2), (20, 0.2, 4), "#E8E8E4")
    for x in (-3, 0, 3):
        B.add((x, 2, 1.0), (1.6, 6, 2.0), "#C8C8C4")
        for z in (0.5, 1.1, 1.7): B.add((x, 2, z), (1.7, 6.1, 0.05), "#A8A8A4")
    B.add((2.85, -0.4, 1.15), (0.2, 0.3, 0.2), "#E0C030")
    B.done()
    W["sign"] = text3d("sign28", "SIN FRUTA", (O_SM[0], O_SM[1]+5.85, O_SM[2]+3.0), 0.5, "#E03030", None, extrude=0.02)
    W["nora"] = N = Person("nora", NORA); longhair(N, NORA)
    W["npcs"] = [Person(f"vn{q}", npc_look(1400+q), 1.0 if q < 7 else 0.65) for q in range(10)]
    camera(28)
    return W

def hide_all(W):
    for k in ("farm", "tractor", "in", "live", "dead", "sp", "sm"): show(W[k], False)
    c = W["city"]; show(c.g, False)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    for tw, hub in W["turb"]: hid(tw, True); show(hub, False)
    for o in W["beams"] + W["cone"] + W["lamps"] + W["plates"] + W["flakes"] + [W[k] for k in ("snowg", "sun", "sundim", "sundk", "table", "earth", "pulse", "sign")]: hid(o, True)
    for p in W["npcs"] + [W["nora"]]: p.show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def person(W, key, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0, talk=0.0):
    H = W[key] if isinstance(key, str) else key
    H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_, talk=talk)
    return H

def sun(W, pos, level):
    k = "sun" if level > 0.66 else ("sundim" if level > 0.33 else "sundk")
    s = W[k]; hid(s, False); s.location = pos

def farm(W, sky, level=0.5, snow=False, turb=False, T=0.0):
    show(W["farm"], True); world_color(sky); light_dir((0.3, -0.6, 0.45)); shadow(0.35+0.3*level)
    hid(W["snowg"], not snow)
    if turb:
        for q, (tw, hub) in enumerate(W["turb"]):
            hid(tw, False); show(hub, True); hub.rotation_euler = (0, T*1.6+q, 0)

def snowfall(W, T, c, area=(6, 6)):
    for q, f in enumerate(W["flakes"]):
        hid(f, False)
        x = c[0]+((q*1.37) % area[0])-area[0]/2+0.2*math.sin(T*2+q)
        y = c[1]+((q*0.73) % area[1])-area[1]/2
        z = c[2]+3.5-((T*0.8+q*0.11) % 3.5)
        f.location = (x, y, z)

# ------------------------------------------------------------------ planos
@shot(0.0, 8.46)
def e1(W, T, M):
    farm(W, "#6A5040", 0.4)
    sun(W, (-10, 70, 22), 0.5)
    tr = W["tractor"]; show(tr, True); tr.location = (1.0, 2.0, 0); tr.rotation_euler = (0, 0, math.radians(-90))
    on = T > 2.2
    for q, c_ in enumerate(W["cone"]):
        hid(c_, not on); c_.location = (1.0, 2.0-1.6-q*0.7, 0.9-q*0.12)
    N = person(W, "nora", 1.0, 2.1, 0, T, "worried" if T < 4.1 else "shock", (0, 0.8 if T > 4.1 else 0), z=1.25)
    for sx in (-1, 1): N.leg(sx, 1.5, 1.5)
    N.hips.location.z = 0.48
    N.arm(1, fwd=1.1, side=0, elbow=0.6); N.arm(-1, fwd=1.1, side=0, elbow=0.6)
    if T < 4.1:
        look(lerpv((3.0, -4.5, 2.2), (2.4, -3.6, 2.4), eio(clamp(T/4.1))), (1.0, 2.0, 1.8), 24)
    else:
        look(lerpv((2.8, -1.8, 3.4), (2.6, -1.2, 3.3), eio(clamp((T-4.1)/4.4))), (-10, 70, 22), 22)
    M["grade"] = "dawn"

@shot(8.46, 15.52)
def e2(W, T, M):
    farm(W, "#3A3040", 0.3)
    k = clamp((T-8.46)/7.0)
    sun(W, (-10, 70, 22), 0.6-0.4*k)
    N = person(W, "nora", 0.0, 0.0, 0, T, "worried", (0, 0.4))
    N.arm(1, fwd=1.3, side=0.1, elbow=2.0)
    for q in range(3):
        P = W["npcs"][q]; person(W, P, -1.4+q*1.4 if q != 1 else 1.4, 1.2+q*0.5, 10*q, T, "worried", (0, 0.5))
    look(lerpv((0.6, -3.4, 1.6), (0.4, -2.6, 1.6), eio(k)), (0.0, 1.0, 1.4), 24)
    M["grade"] = "night"

@shot(15.52, 21.86)
def e3(W, T, M):
    show(W["sp"], True); world_color("#04040A"); light_dir((0.3, -0.6, 0.45)); shadow(0.2); o = O_SP
    s = W["sundim"]; hid(s, False); s.location = (o[0], o[1]+20, o[2]+7); s.scale = (1.0, 1.0, 1.0)
    e = W["earth"]; hid(e, False); e.location = (o[0], o[1]+20, o[2]-6); e.scale = (1.4, 1.4, 1.4); e.rotation_euler = (0, 0, T*0.5)
    k = clamp((T-16.8)/4.0)
    p = W["pulse"]; hid(p, False); p.location = (o[0], o[1]+20, o[2]+3.5-8.5*k); p.rotation_euler = (0, math.pi/2, 0)
    look(lerpv((o[0]-3, o[1]+1, 1.0), (o[0]-1.5, o[1]+4, 0.5), eio(clamp((T-15.52)/6.3))), (o[0], o[1]+20, o[2]+0.5), 22)
    M["grade"] = "deep"

@shot(21.86, 29.22)
def e4(W, T, M):
    if T < 24.0:
        city(W, T)
        N = person(W, "nora", 3.0, 4.0, 0, T, "shock", (0, 0.8)); N.root.location.z = 0.2
        look(lerpv((3.6, 0.6, 1.3), (3.4, 1.4, 1.3), eio(clamp((T-21.86)/2.1))), (3.0, 4.0, 2.2), 22)
        M["grade"] = "cold"
    elif T < 26.4:
        show(W["sm"], True); world_color("#D8D8D0"); light_dir((0.3, -0.6, 0.6)); shadow(0.4); o = O_SM
        hid(W["sign"], False)
        P = W["npcs"][3]; person(W, P, o[0]+1.5, o[1]-0.4, 180, T, "sad", (0, 0))
        look(lerpv((o[0]+1.8, o[1]-5.0, 2.0), (o[0]+1.4, o[1]-4.2, 2.0), eio(clamp((T-24.0)/2.4))), (o[0], o[1]+3, 1.6), 24)
        M["grade"] = "day_sad"
    else:
        show(W["dead"], True); show(W["in"], True); world_color("#5A5048"); light_dir((0.3, -0.6, 0.45)); shadow(0.3); o = O_IN
        Bx = Batch  # noqa
        N = person(W, "nora", o[0], o[1]-3.5, 0, T, "sad", (0, -0.5))
        N.chest.rotation_euler = (-0.2, 0, 0)
        look(lerpv((o[0]+0.2, o[1]-6.0, 1.7), (o[0]+0.1, o[1]-5.4, 1.6), eio(clamp((T-26.4)/2.8))), (o[0], o[1]-3.5, 1.4), 24)
        M["grade"] = "day_sad"
    # el decorado del invernadero vivo y el muerto comparten sitio

def city(W, T):
    c = W["city"]; show(c.g, True)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    world_color("#8A94A8"); light_dir((0.3, -0.6, 0.45)); shadow(0.3)
    snowfall(W, T, (3.0, 2.0, 0.0), (7, 7))

def inside(W, lit=True, night=False):
    show(W["in"], True); show(W["live"], True); o = O_IN
    for l in W["lamps"]: hid(l, not lit)
    world_color("#2A1E30" if night else "#C8B8C8"); light_dir((0.3, -0.6, 0.6)); shadow(0.4)

@shot(29.22, 39.18)
def e5(W, T, M):
    if T < 34.4:
        show(W["dead"], True); show(W["in"], True); world_color("#5A5048"); light_dir((0.3, -0.6, 0.45)); shadow(0.3); o = O_IN
        N = person(W, "nora", o[0], o[1]-3.5, 0, T, "sad" if T < 30.4 else "smirk", (0.3 if T < 31.5 else 0, 0.6 if T > 31.5 else 0))
        look(lerpv((o[0]+0.3, o[1]-6.0, 1.75), (o[0]+0.2, o[1]-5.5, 1.7), eio(clamp((T-29.22)/5.2))), (o[0], o[1]-3.5, 1.55), 26)
        M["grade"] = "day_sad"
    elif T < 36.6:
        o = O_IN; inside(W, True, night=False)
        n = int(clamp((T-34.4)/2.0)*20)
        for q, l in enumerate(W["lamps"]): hid(l, q >= n)
        N = person(W, "nora", o[0]-3.2, o[1]-4.0, 30, T, "happy", (0, 0.8)); N.arm(1, fwd=2.6, side=0.2, elbow=0.4)
        look(lerpv((o[0]-1.0, o[1]-9.0, 2.0), (o[0]-0.6, o[1]-8.0, 2.2), eio(clamp((T-34.4)/2.2))), (o[0], o[1]-2.0, 1.6), 22)
        M["grade"] = "lab"
    else:
        farm(W, "#5A4A48", 0.4, turb=True, T=T)
        sun(W, (-10, 70, 22), 0.3)
        N = person(W, "nora", 2.0, 2.0, 160, T, "happy", (0, 0.6))
        look(lerpv((3.5, -4.0, 1.8), (3.2, -3.2, 2.2), eio(clamp((T-36.6)/2.6))), (-2.0, 40, 12), 22)
        M["grade"] = "dawn"

@shot(39.18, 45.1)
def e6(W, T, M):
    o = O_IN; inside(W, True)
    N = person(W, "nora", o[0]-0.6, o[1]-4.0, 0, T, "smirk" if T < 41.0 else "happy", (0, 0)); N.arm(1, fwd=1.1, side=-0.2, elbow=1.2)
    for q in range(3):
        P = W["npcs"][q]; laugh = T < 40.9
        person(W, P, o[0]+0.6+q*0.8, o[1]-5.6, 30-q*15, T, "happy" if laugh else "shock", (-0.6, 0.3 if not laugh else 0), talk=0.8*abs(math.sin(T*10+q)) if laugh else 0)
        if laugh: P.chest.rotation_euler = (0.12*math.sin(T*14+q), 0, 0)
    if T < 41.0:
        look(lerpv((o[0]+1.5, o[1]-8.5, 1.8), (o[0]+1.2, o[1]-7.8, 1.75), eio(clamp((T-39.18)/1.8))), (o[0]+0.8, o[1]-5.0, 1.4), 24)
    else:
        look(lerpv((o[0]-1.6, o[1]-8.0, 1.6), (o[0]-1.4, o[1]-7.0, 1.55), eio(clamp((T-41.0)/4.1))), (o[0]-0.5, o[1]-2.5, 1.0), 24)
    M["grade"] = "lab"

@shot(45.1, 58.46)
def e7(W, T, M):
    o = O_IN
    if T < 50.2:
        farm(W, "#0A0A18", 0.1, snow=True)
        snowfall(W, T, (0.0, 3.0, 0.0), (8, 8))
        N = person(W, "nora", 0.0, 5.0, 0, T, "worried", (0, 0.2)); N.arm(1, fwd=1.4, side=0.2, elbow=2.0)
        look(lerpv((0.8, 1.6, 1.7), (0.6, 2.4, 1.7), eio(clamp((T-45.1)/5.1))), (0.0, 5.0, 1.6), 26)
        M["grade"] = "night"
    elif T < 54.2:
        inside(W, False, night=True)
        N = person(W, "nora", o[0]-1.2, o[1]-6.0, 0, T, "worried", (0, 0)); N.arm(1, fwd=0.6, side=1.4, elbow=0.2)
        f = clamp((T-52.6)/1.6)
        for q in range(8):
            P = W["npcs"][q]; P.show(True)
            y = lerp(o[1]-15.0, o[1]-7.5+0.0*q, f)-q*0.7
            P.place(o[0]+0.2+(q % 3)*0.7, y, 180); P.walk(T*1.2+q); P.face(T, "worried", (0, 0))
        look(lerpv((o[0]+1.5, o[1]-2.0, 1.8), (o[0]+1.2, o[1]-2.6, 1.8), eio(clamp((T-50.2)/4.0))), (o[0]-0.2, o[1]-8.0, 1.3), 24)
        M["grade"] = "night"
    else:
        inside(W, False, night=True)
        for q in range(10):
            P = W["npcs"][q]; P.show(True)
            x = (-3.25, -0.6, 0.6, 3.25)[q % 4]; y = o[1]-4.0+(q//4)*2.2
            P.place(o[0]+x, y, 90 if q % 2 else -90, 0.0); P.idle(T, 0.3); P.face(T, "neutral", (0, 0), blink=False)
            for e in P.eyes: e.scale = (1, 1, 0.12)
            P.hips.rotation_euler = (1.5, 0, 0); P.hips.location.z = 0.22
        N = person(W, "nora", o[0]+0.0, o[1]-6.0, 0, T, "happy", (0, 0))
        look(lerpv((o[0]+0.4, o[1]-9.0, 2.6), (o[0]+0.2, o[1]-8.4, 2.9), eio(clamp((T-54.2)/4.3))), (o[0], o[1]-2.5, 0.4), 24)
        M["grade"] = "night"

@shot(58.46, 64.42)
def e8(W, T, M):
    k = clamp((T-60.8)/3.4)
    farm(W, "#6A6070" if T < 60.8 else "#C8A090", 0.5, snow=True)
    sun(W, (-10, 70, lerp(22, 28, k)), 0.4 if T < 61.5 else 0.7)
    N = person(W, "nora", 0.0, 3.0, 180, T, "shock" if T < 61.5 else "happy", (0, 0.4))
    for q in range(3):
        P = W["npcs"][q]; person(W, P, -1.4+q*1.4, 3.9, 180, T, "shock" if T < 60.5 else "happy", (0, 0.5))
    if q == 2 and 59.5 < T < 60.4: P.arm(1, fwd=2.6, side=0.2, elbow=0.2)
    if T < 60.8:
        look(lerpv((3.8, 3.0, 1.7), (3.4, 3.2, 1.7), eio(clamp((T-58.46)/2.3))), (0.0, 3.4, 1.5), 24)
    else:
        look(lerpv((0.6, -2.4, 1.2), (0.5, -1.8, 1.3), eio(clamp((T-60.8)/3.6))), (-10, 70, 22), 22)
    M["grade"] = "dawn"

@shot(64.42, 72.54)
def e9(W, T, M):
    o = O_IN; inside(W, True, night=True)
    hid(W["table"], False)
    for p_ in W["plates"]: hid(p_, False)
    for q in range(10):
        P = W["npcs"][q]; P.show(True)
        sx = -1 if q % 2 else 1; y = o[1]-2.6+(q//2)*1.4
        P.place(o[0]+sx*0.95, y, 90 if sx < 0 else -90); P.idle(T+q); P.face(T, "happy", (0, 0), talk=0.6*abs(math.sin(T*6+q)) if q % 3 == 0 else 0)
        for s2 in (-1, 1): P.leg(s2, 1.5, 1.5)
        P.hips.location.z = 0.48*P.s/1.0 if P.s > 0.9 else 0.5
    N = person(W, "nora", o[0], o[1]-4.0, 0, T, "happy", (0, 0.2))
    look(lerpv((o[0]+0.3, o[1]-7.5, 2.4), (o[0]+0.2, o[1]-6.6, 2.2), eio(clamp((T-64.42)/8.1))), (o[0], o[1]+0.5, 1.0), 22)
    M["grade"] = "cafe"

@shot(72.54, TOTAL+0.1)
def e10(W, T, M):
    o = O_IN; inside(W, True, night=True)
    N = person(W, "nora", o[0], o[1]-4.0, 0, T, "smirk", (0, 0.1))
    look(lerpv((o[0]+0.35, o[1]-6.2, 1.75), (o[0]+0.3, o[1]-5.5, 1.72), eio(clamp((T-72.54)/4.2))), (o[0], o[1]-4.0, 1.7), 26)
    M["grade"] = "cafe"; M["fade"] = clamp((T-76.3)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
