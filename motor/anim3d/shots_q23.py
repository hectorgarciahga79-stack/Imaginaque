"""Q23 · Mini historia «El bebé que perdía mil euros por minuto» (3D de bloques, 76,19 s).
Reutiliza shots_q17.py (hospital, puerta del hospital, cumpleaños, Nil) y añade: oficina del banco con contador gigante (y=1200),
padres y empleado del banco, maletas, alquiler de bicis (y=1400), cuarto de adolescente con ordenador (y=1600),
planeta con transferencias (y=1800) y la multitud de los que recibieron el dinero (y=2000)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, tiles, planks, stripes, text3d, building, tree, asphalt
import shots_q17 as S17

FPS = 24
TOTAL = 76.19
RED = "#E0302A"; GOLD = "#F2C230"
O_BK = (0, 1200, 0); O_BI = (0, 1400, 0); O_TN = (0, 1600, 0); O_GL = (0, 1800, 0); O_CR = (0, 2000, 0)
fmt = S17.fmt; money = S17.money

class Env:
    def talk(self, who, T): return 0.0

def build():
    W = S17.build()
    r = random.Random(23)
    # banco
    W["bank"] = g = group("bank", O_BK)
    B = Batch("bk_b", g, 1.0)
    B.add((0, 0, -0.05), (30, 30, 0.1), tmat("bkfl", "#E8E4DA", 16, 0.04, 181, tiles)); B.add((0, 4, 3), (30, 0.2, 6), "#D8D0C0")
    B.add((0, 1.2, 0.55), (3.6, 1.0, 1.1), "#8A6A4A"); B.add((0, 1.2, 1.12), (3.7, 1.05, 0.06), "#D8C8A8")
    B.done()
    W["bigdebt"] = text3d("bigdebt", "-9.460.800.000 €", (O_BK[0], O_BK[1]+3.85, 3.4), 0.55, RED, None, extrude=0.05)
    W["clerk"] = Person("clerk", dict(npc_look(601), top="#2A3A5A", top2="#2A3A5A", stripe="#2A3A5A"), 1.0)
    W["mom"] = Person("mom", dict(npc_look(602), top="#C86A9A", top2="#C86A9A", stripe="#C86A9A", hstyle="long"), 1.0)
    W["dad"] = Person("dad", dict(npc_look(603), top="#4A7A5A", top2="#4A7A5A", stripe="#4A7A5A", hstyle="short"), 1.05)
    W["suitcases"] = [box(f"sc{q}", (0, 0, 0), (0.5, 0.25, 0.7), mat(["#C0302A", "#3A6AA8", "#E0A030"][q])) for q in range(3)]
    W["redctr"] = text3d("redctr", "", (0, 0, 0), 0.3, RED, None, extrude=0.03)
    # bicis
    W["bikes"] = g = group("bikes", O_BI)
    B = Batch("bi_b", g, 1.0)
    B.add((0, 0, -0.06), (200, 200, 0.1), tmat("grassb", "#5A9A44", 16, 0.10, 182)); B.add((0, 2, 0.02), (40, 4, 0.06), tmat("walkb", "#B8B0A0", 16, 0.05, 183, tiles))
    for k in range(5):
        x = -3+k*1.4
        B.add((x, 2.6, 0.35), (0.06, 0.5, 0.5), "#2A2A2E"); B.add((x, 1.8, 0.35), (0.06, 0.5, 0.5), "#2A2A2E"); B.add((x, 2.2, 0.6), (0.05, 1.0, 0.06), "#3AA0C8"); B.add((x, 2.5, 0.8), (0.05, 0.08, 0.35), "#3AA0C8")
    B.add((3.6, 2.6, 1.0), (0.8, 0.4, 2.0), "#E8ECF0"); B.add((3.6, 2.38, 1.4), (0.5, 0.05, 0.4), "#1E3A5A")
    B.done()
    W["nox"] = text3d("nox", "DENEGADO", (O_BI[0]+3.6, O_BI[1]+2.33, 1.35), 0.12, RED, None, extrude=0.01)
    W["letter"] = box("letter", (0, 0, 0), (0.5, 0.03, 0.34), mat("#F4F1EA"))
    W["lettert"] = text3d("lettert", "+520 M", (0, 0, 0), 0.1, RED, None, extrude=0.01)
    # cuarto de adolescente
    W["teen"] = g = group("teen", O_TN)
    B = Batch("tn_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("tfl", "#A87A50", 16, 0.07, 184, planks)); B.add((0, 3.2, 1.6), (14, 0.2, 3.2), tmat("twall", "#3A4A6A", 16, 0.04, 185))
    B.add((0, 1.6, 0.75), (2.2, 1.0, 0.08), "#2A2A2E"); B.add((0, 2.0, 1.25), (1.2, 0.08, 0.8), "#1C1C22")
    B.done()
    W["screen"] = box("screen", (O_TN[0], O_TN[1]+1.95, 1.25), (1.1, 0.02, 0.7), mat("#40A0E0"))
    W["lines"] = [box(f"ln{q}", (O_TN[0]-0.45+0.02*(q % 3), O_TN[1]+1.93, 1.5-q*0.07), (0.6+0.3*((q*7) % 3)/3, 0.01, 0.03), mat("#F4F1EA")) for q in range(8)]
    # planeta con transferencias
    W["gl"] = gl = group("gl", O_GL)
    Bg = Batch("gl_b", gl, 1.0)
    R = 3.0; st = 0.45; n = int(R/st)+1
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            for k in range(-n, n+1):
                p = Vector((i, j, k))*st; d = p.length
                if not (R-st*0.95 < d <= R): continue
                u = p.normalized()
                v = math.sin(u.x*2.3+1.3)*math.cos(u.y*1.9-0.4) + 0.7*math.sin(u.z*3.0+u.x*1.7+u.y*2.2) + 0.5*math.cos(u.y*3.3-u.z*1.1)
                Bg.add(tuple(p), (st, st, st), "#EEF4F8" if abs(u.z) > 0.88 else ("#5A9A44" if v > -0.05 else "#2E6EB8"))
    Bg.done()
    S = Batch("st2_b", None, 1.0)
    for q in range(160): S.add((O_GL[0]+r.uniform(-60, 60), O_GL[1]+r.uniform(25, 40), r.uniform(-60, 60)), (0.12, 0.12, 0.12), "#FFFFFF")
    W["stars"] = S.done()
    W["arcs"] = []
    targets = [Vector((0.3, -0.8, 0.5)), Vector((-0.9, -0.4, -0.2)), Vector((0.8, 0.2, 0.3)), Vector((-0.2, -0.9, -0.4)), Vector((0.5, -0.5, -0.7)), Vector((-0.6, -0.7, 0.4))]
    src = Vector((0.1, -0.85, 0.55)).normalized()
    for t in targets:
        t = t.normalized(); dots = []
        for s in range(14):
            f = (s+1)/15; v = (src*(1-f)+t*f).normalized()*(R+0.25+0.9*math.sin(f*math.pi))
            dots.append(box(f"arc{len(W['arcs'])}_{s}", tuple(v), (0.14, 0.14, 0.14), mat(GOLD), gl))
        W["arcs"].append(dots)
    # multitud
    W["crowdg"] = g = group("crowdg", O_CR)
    B = Batch("cr_b", g, 1.0)
    B.add((0, 0, -0.06), (400, 400, 0.1), tmat("plaza", "#C8B898", 16, 0.05, 186, tiles))
    skins = ["#F2C9A0", "#E0B08A", "#C68E62", "#8D5A3A", "#F5D6B8", "#B97A50"]; tops = ["#B5443A", "#3A6EA8", "#6A9A48", "#E0B040", "#7A4E8A", "#D0D0CC", "#C46A2E", "#2E7A6A"]
    for ix in range(-30, 31):
        for iy in range(2, 60):
            if r.random() < 0.25: continue
            x = ix*0.9+r.uniform(-0.2, 0.2); y = iy*0.9; h = r.uniform(1.5, 1.85)
            B.add((x, y, h*0.4), (0.45, 0.3, h*0.8), tops[(ix*7+iy) % 8]); B.add((x, y, h*0.85), (0.4, 0.4, 0.4), skins[(ix+iy*3) % 6])
            B.add((x+0.2, y-0.16, h*0.75), (0.25, 0.02, 0.16), "#F4F1EA")
    B.done()
    W["front"] = [Person(f"fr{q}", npc_look(700+q), 1.0) for q in range(5)]
    W["envs"] = [box(f"en{q}", (0, 0, 0), (0.3, 0.02, 0.2), mat("#F4F1EA")) for q in range(5)]
    W["teenNil"] = Person("teennil", S17.NIL, 1.0)
    return W

def hide_all(W):
    S17.hide_all(W)
    for k in ("bank", "bikes", "teen", "gl", "crowdg"): show(W[k], False)
    hid(W["stars"], True)
    for k in ("bigdebt", "redctr", "nox", "letter", "lettert", "screen"): hid(W[k], True)
    for o in W["suitcases"] + W["lines"] + W["envs"]: hid(o, True)
    for a in W["arcs"]:
        for d in a: hid(d, True)
    for p in [W["clerk"], W["mom"], W["dad"], W["teenNil"]] + W["front"]: p.show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

shake = S17.shake; settext = S17.settext; baby = S17.baby

def teen(W, x, y, face, T, expr="neutral", look_=(0, 0), s=1.0):
    H = W["teenNil"]; H.show(True); H.place(x, y, face); H.root.scale = (s, s, s); H.idle(T); H.face(T, expr, look_)
    return H

# ------------------------------------------------------------------ planos
@shot(0.0, 6.7)
def n1(W, T, M):
    show(W["bank"], True); world_color("#E8E4DA"); light_dir((0.4, -0.5, 0.75)); shadow(0.45)
    k = T/6.7
    hid(W["bigdebt"], False)
    H = teen(W, O_BK[0], O_BK[1]-0.5, 0, T, "worried" if T < 4.2 else "sad", (0, 0.3))
    if T > 4.2:
        for sx in (-1, 1): H.arm(sx, fwd=0.4, side=0.6, elbow=1.2); H.fingers(sx, 0.0, 0.0)
    C = W["clerk"]; C.show(True); C.place(O_BK[0]+0.4, O_BK[1]+1.9, 180); C.idle(T); C.face(T, "neutral", (0, 0))
    look(lerpv((O_BK[0]+0.6, O_BK[1]-6.0, 2.8), (O_BK[0]+0.4, O_BK[1]-3.4, 1.9), eio(k)), (O_BK[0], O_BK[1]+1.0, lerp(2.8, 1.6, eio(k))), 24)
    M["grade"] = "lab"

@shot(6.7, 13.78)
def n2(W, T, M):
    S17.m1(W, lerp(0.0, 4.98, (T-6.7)/7.08), M)

@shot(13.78, 21.62)
def n3(W, T, M):
    S17.m3(W, lerp(10.72, 17.28, (T-13.78)/7.84), M)

@shot(21.62, 30.64)
def n4(W, T, M):
    k = (T-21.62)/9.02
    if T < 26.9:
        show(W["bank"], True); world_color("#E8E4DA"); light_dir((0.4, -0.5, 0.75)); shadow(0.45)
        C = W["clerk"]; C.show(True); C.place(O_BK[0]+0.4, O_BK[1]+1.9, 180); C.idle(T); C.face(T, "neutral", (0, 0))
        C.arm(1, fwd=0.6, side=0.4, elbow=1.0)
        for q, (p, x) in enumerate(((W["mom"], -0.6), (W["dad"], 0.6))):
            p.show(True); p.place(O_BK[0]+x, O_BK[1]+0.2, 180); p.idle(T+q); p.face(T, "worried", (0, 0))
        Mo = W["mom"]; Mo.arm(-1, fwd=1.0, side=0.1, elbow=1.6)
        ctr = W["redctr"]; settext(ctr, fmt(money(1440+(T-21.62)*3000))); ctr.location = (O_BK[0]-0.6, O_BK[1]+0.1, 2.5)
        look(lerpv((O_BK[0]-2.4, O_BK[1]-3.4, 2.0), (O_BK[0]-1.8, O_BK[1]-2.6, 1.9), eio(clamp((T-21.62)/5.0))), (O_BK[0], O_BK[1]+0.8, 1.5), 24)
        M["grade"] = "lab"
    else:
        show(W["door"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
        o = S17.O_D; f = clamp((T-26.9)/3.7)
        for q, (p, x) in enumerate(((W["mom"], -0.7), (W["dad"], 0.7))):
            p.show(True); p.place(o[0]+x, o[1]-1.0-2.0*f, 0); p.walk(T*1.3+q*0.5); p.face(T, "worried", (0, 0))
        for q, s in enumerate(W["suitcases"]): hid(s, False); s.location = (o[0]+[-1.1, 1.1, 0.0][q], o[1]-1.2-2.0*f, 0.35)
        ctr = W["redctr"]; settext(ctr, fmt(money(1440*30+(T-26.9)*90000))); ctr.location = (o[0], o[1]-1.0-2.0*f, 2.6)
        look((o[0]+0.5, o[1]-8.5, 1.8), (o[0], o[1]-2.0, 1.6), 24)
        M["grade"] = "day_sad"

@shot(30.64, 41.0)
def n5(W, T, M):
    k = (T-30.64)/10.36
    if T < 35.2:
        show(W["bikes"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
        hid(W["nox"], T < 32.6)
        H = teen(W, O_BI[0]+2.6, O_BI[1]+1.2, 40, T, "happy" if T < 32.6 else "sad", (0.4, 0.2), s=0.7)
        H.arm(1, fwd=1.4, side=0.0, elbow=0.4)
        look(lerpv((O_BI[0]+0.5, O_BI[1]-3.2, 1.6), (O_BI[0]+1.4, O_BI[1]-2.2, 1.5), eio(clamp((T-30.64)/4.5))), (O_BI[0]+3.0, O_BI[1]+2.2, 1.0), 26)
        M["grade"] = "day"
    else:
        S17.m5(W, lerp(25.1, 28.16, (T-35.2)/5.8), M)
        o = S17.O_B
        H = W["nil"]; H.root.scale = (0.7, 0.7, 0.7)
        bpy.context.view_layer.update()
        hp = H.hand[1].matrix_world @ Vector((0, -0.1, -0.1))
        H.arm(1, fwd=1.4, side=0.0, elbow=0.5)
        bpy.context.view_layer.update()
        hp = H.hand[1].matrix_world @ Vector((0, -0.1, -0.05))
        lt = W["letter"]; hid(lt, False); lt.location = tuple(hp); lt.rotation_euler = (0, 0, 0.3)
        tx = W["lettert"]; hid(tx, False); tx.location = (hp.x-0.15, hp.y-0.03, hp.z-0.04); tx.rotation_euler = (math.pi/2, 0, 0.3)

@shot(41.0, 46.84)
def n6(W, T, M):
    show(W["teen"], True); world_color("#141A2C"); light_dir((0.3, -0.6, 0.75)); shadow(0.35)
    k = (T-41.0)/5.84
    hid(W["screen"], False)
    for q, l in enumerate(W["lines"]): hid(l, q/8 > clamp((T-41.5)/3.0))
    H = teen(W, O_TN[0]-0.2, O_TN[1]+0.6, 180, T, "worried" if T < 44.0 else "shock", (0, -0.2))
    for sx in (-1, 1): H.arm(sx, fwd=1.3, side=0.0, elbow=1.0)
    look(lerpv((O_TN[0]+1.6, O_TN[1]-1.4, 1.9), (O_TN[0]+1.1, O_TN[1]-0.6, 1.8), eio(k)), (O_TN[0], O_TN[1]+1.8, 1.4), 26)
    M["grade"] = "night"

@shot(46.84, 56.92)
def n7(W, T, M):
    show(W["gl"], True); hid(W["stars"], False); world_color("#04050A"); light_dir((0.6, -0.5, 0.6)); shadow(0.3)
    k = (T-46.84)/10.08
    W["gl"].rotation_euler = (0.2, 0, 0.3*math.sin(T*0.2))
    starts = [47.2, 52.4, 54.0, 55.4, 49.5, 50.8]
    for a, t0 in zip(W["arcs"], starts):
        f = clamp((T-t0)/1.0)
        for s, d in enumerate(a): hid(d, s/14 > f)
    look(lerpv((O_GL[0]+0.0, O_GL[1]-12.0, 3.0), (O_GL[0]+1.0, O_GL[1]-10.0, 2.0), eio(k)), (O_GL[0], O_GL[1], 0.0), 30)
    M["grade"] = "night"

@shot(56.92, 66.28)
def n8(W, T, M):
    show(W["crowdg"], True); world_color("#FFD9A0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-56.92)/9.36
    for q, p in enumerate(W["front"]):
        p.show(True); p.place(O_CR[0]-2.0+q*1.0, O_CR[1]+0.6, 0); p.idle(T+q); p.face(T+q, "happy", (0, 0.2))
        p.arm(1, fwd=2.6, side=0.2, elbow=0.3+0.2*math.sin(T*4+q))
        bpy.context.view_layer.update()
        hp = p.hand[1].matrix_world @ Vector((0, -0.06, -0.1)); e = W["envs"][q]; hid(e, False); e.location = tuple(hp)
    e_ = eio(k)
    look((O_CR[0]+lerp(0.0, 0.0, e_), O_CR[1]-lerp(4.5, 16.0, e_), lerp(1.6, 26.0, e_)), (O_CR[0], O_CR[1]+lerp(1.0, 20.0, e_), lerp(1.4, 0.0, e_)), lerp(26, 24, e_))
    M["grade"] = "dawn"

@shot(66.28, 71.66)
def n9(W, T, M):
    show(W["crowdg"], True); world_color("#FFD9A0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-66.28)/5.38
    for q, p in enumerate(W["front"]):
        p.show(True); p.place(O_CR[0]-2.0+q*1.0, O_CR[1]+0.6, 0); p.idle(T+q); p.face(T+q, "happy", (0, 0.2)); p.arm(1, fwd=0.3, side=2.6, elbow=0.4+0.4*math.sin(T*8+q))
    H = teen(W, O_CR[0], O_CR[1]-1.6, 180, T, "happy", (0, 0.2))
    look(lerpv((O_CR[0]+0.6, O_CR[1]-4.0, 1.7), (O_CR[0]+0.4, O_CR[1]-3.4, 1.65), eio(k)), (O_CR[0], O_CR[1]-1.0, 1.6), 26)
    if T > 68.4:
        H.place(O_CR[0], O_CR[1]-1.6, 0); H.face(T, "happy", (0, 0.1))
        look(lerpv((O_CR[0]+0.4, O_CR[1]-3.6, 1.65), (O_CR[0]+0.3, O_CR[1]-3.0, 1.62), eio(clamp((T-68.4)/3.2))), (O_CR[0], O_CR[1]-1.6, 1.5), 26)
    M["grade"] = "dawn"

@shot(71.66, TOTAL+0.1)
def n10(W, T, M):
    show(W["crowdg"], True); world_color("#FFD9A0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-71.66)/4.53
    for q, p in enumerate(W["front"]):
        p.show(True); p.place(O_CR[0]-2.0+q*1.0, O_CR[1]+0.6, 0); p.idle(T+q); p.face(T+q, "happy", (0, 0.2))
    H = teen(W, O_CR[0], O_CR[1]-1.6, 0, T, "smirk", (0, 0.1))
    H.arm(1, fwd=1.2, side=0.1, elbow=1.4); H.fingers(1, 0.6, 0.2)
    look(lerpv((O_CR[0]+0.4, O_CR[1]-4.4, 1.65), (O_CR[0]+0.3, O_CR[1]-3.6, 1.62), eio(k)), (O_CR[0], O_CR[1]-1.6, 1.5), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-75.7)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
