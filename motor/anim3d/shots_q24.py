"""Q24 · Mini historia «Siete días antes del asteroide» (3D de bloques, 77,23 s).
Protagonista original: Marcos (camisa azul cielo, pelo castaño). Personajes: Clara, su padre, un comprador, el jefe.
Decorados: oficina (world.Office), ciudad (world.City), pueblo con meteoro (y=500), mirador al atardecer (y=700),
súper vacío y autopista atascada (y=900), casa del padre (y=1100), espacio con el asteroide y la nave (y=1300), colina nocturna (y=1500)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, City, Office, building, tree, tiles, planks, asphalt, stripes, text3d, car

FPS = 24
TOTAL = 77.23
MARCOS = dict(skin="#E0B08A", hair="#5A3820", hair2="#6A4428", eye="#2A1A10", top="#7AB8E8", top2="#5A98C8", stripe="#F4F1EA",
              legs="#3A3A44", legs2="#2C2C34", shoe="#6A4A30", shoe2="#2A2A2E", watch=True, hstyle="short")
CLARA = dict(skin="#C68E62", hair="#1C1410", hair2="#2A1E16", eye="#2A1A10", top="#E8A040", top2="#C88020", stripe="#F4F1EA",
             legs="#3A5A8A", legs2="#2E4A74", shoe="#F4F1EA", shoe2="#E8A040", watch=False, hstyle="long")
DAD = dict(skin="#E0B08A", hair="#B8B4AE", hair2="#A8A4A0", eye="#2A1A10", top="#6A5A4A", top2="#5A4A3A", stripe="#8A7A6A",
           legs="#3A3A40", legs2="#2C2C34", shoe="#3A2A20", shoe2="#3A2A20", watch=False, hstyle="bald")

class Env:
    def talk(self, who, T): return 0.0

O_OF = (0, 300, 0); O_V = (0, 500, 0); O_P = (0, 700, 0); O_X = (0, 900, 0); O_F = (0, 1100, 0); O_SP = (0, 1300, 0); O_HL = (0, 1500, 0)

def rockball(B, R, st, col, seed):
    rr = random.Random(seed)
    n = int(R/st)+1
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            for k in range(-n, n+1):
                p = Vector((i, j, k))*st
                if p.length <= R*(0.85+0.15*math.sin(i*1.3+j*0.7+k)) and p.length > R-2*st:
                    B.add(tuple(p), (st, st, st), col if rr.random() > 0.3 else "#4A3E36")

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(24)
    W["office"] = Office(O_OF)
    W["badge"] = box("badge", (0, 0, 0), (0.12, 0.02, 0.18), mat("#F4F1EA"))
    W["city"] = City()
    W["sky_ast"] = box("skyast", (0, 0, 0), (1.2, 1.2, 1.2), mat("#FF7A40"))
    W["tv"] = text3d("tvtxt", "ASTEROIDE · DOMINGO", (0, 0, 0), 0.35, "#E0302A", None, extrude=0.02)
    W["tvbox"] = box("tvbox", (0, 0, 0), (4.2, 0.1, 1.0), mat("#1C1C22"))
    # pueblo con meteoro
    W["vil"] = g = group("vil", O_V)
    B = Batch("vil_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("snowv", "#E8ECF0", 16, 0.05, 191))
    for k in range(-5, 6): building(B, k*9.0, 8.0, 8, 6, 3+k % 3, ["#C8B8A8", "#B8A898", "#D8C8B8"][k % 3], 1200+k, -1)
    B.done()
    W["meteor"] = box("meteor", (0, 0, 0), (1.0, 1.0, 1.0), mat("#FFE080"))
    W["trail"] = [box(f"tr{q}", (0, 0, 0), (0.8, 0.8, 0.8), mat("#FFF2C8" if q % 2 else "#E8E0D8")) for q in range(20)]
    W["shards"] = [(box(f"gs{q}", (0, 0, 0), (0.15, 0.03, 0.15), mat("#9FD0E8")), r.uniform(-1, 1), r.uniform(0, 1), r.uniform(-1, 1)) for q in range(40)]
    # mirador
    W["view"] = g = group("view", O_P)
    B = Batch("vw_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("grassp", "#6A9A44", 16, 0.10, 192))
    B.add((0, 40, -2), (300, 60, 0.5), tmat("seap", "#3A6AA8", 16, 0.06, 193))
    B.add((0, 2, 0.5), (3.0, 0.6, 0.15), "#8A6A4A"); B.add((-1.2, 2, 0.25), (0.15, 0.5, 0.5), "#6A4A30"); B.add((1.2, 2, 0.25), (0.15, 0.5, 0.5), "#6A4A30")
    B.done()
    W["sun"] = box("sunp", (0, 0, 0), (5, 5, 5), mat("#FFB060"))
    W["carkey"] = box("carkey", (0, 0, 0), (0.1, 0.03, 0.18), mat("#C8C8D0"))
    W["soldcar"] = car("soldcar", "#5A8AC8")
    W["buyer"] = Person("buyer", npc_look(801), 1.0)
    # caos: súper vacío + autopista
    W["chaos"] = g = group("chaos", O_X)
    B = Batch("ch_b", g, 1.0)
    B.add((0, 0, -0.06), (400, 400, 0.1), tmat("grassx", "#7A8A5A", 16, 0.10, 194))
    B.add((0, 0, 0.0), (8, 400, 0.06), tmat("hw", "#4A4A50", 16, 0.05, 195, asphalt))
    for y in range(-60, 61, 6): B.add((0, y, 0.04), (0.2, 3.0, 0.02), "#E8E4DA")
    B.done()
    W["jam"] = []
    for q in range(16):
        c = car(f"jam{q}", ["#C0302A", "#3A6AA8", "#E0C040", "#D8D8D0", "#3A3A44"][q % 5]); W["jam"].append((c, (-1.9 if q % 2 else 1.9), -4+q*5.2))
    W["smoke"] = [box(f"sk{q}", (0, 0, 0), (2.0, 2.0, 2.0), mat("#5A5654")) for q in range(6)]
    # casa del padre
    W["home"] = g = group("home", O_F)
    B = Batch("hm_b", g, 1.0)
    B.add((0, 0, -0.06), (100, 100, 0.1), tmat("grassh", "#5A9A44", 16, 0.10, 196))
    B.add((0, 5, 1.6), (6, 4, 3.2), tmat("hwall", "#E8D8B8", 16, 0.06, 197, stripes)); B.add((0, 5, 3.4), (6.4, 4.4, 0.4), "#A84A3A")
    B.add((0, 2.98, 1.0), (1.0, 0.06, 2.0), "#6A4A30"); B.add((-1.8, 2.98, 1.8), (1.0, 0.05, 0.8), "#FFE7A0"); B.add((1.8, 2.98, 1.8), (1.0, 0.05, 0.8), "#FFE7A0")
    B.done()
    # espacio
    W["sp"] = g = group("sp", O_SP)
    B = Batch("ast_b", g, 1.0); rockball(B, 3.2, 0.5, "#6A5A4A", 7); B.done()
    S = Batch("stars_b", None, 1.0)
    for q in range(200): S.add((O_SP[0]+r.uniform(-60, 60), O_SP[1]+r.uniform(25, 40), r.uniform(-60, 60)), (0.12, 0.12, 0.12), "#FFFFFF")
    W["stars"] = S.done()
    W["probe"] = pb = group("probe", (0, 0, 0))
    Pb = Batch("probe_b", pb, 1.0); Pb.add((0, 0, 0), (0.6, 0.6, 0.6), "#C8C8D0"); Pb.add((0, 0, 0), (2.4, 0.05, 0.5), "#2A4A8A"); Pb.add((-0.4, 0, 0), (0.3, 0.3, 0.3), "#FF8030"); Pb.done()
    W["frags"] = [(box(f"fg{q}", (0, 0, 0), (0.6, 0.6, 0.6), mat("#6A5A4A")), Vector((r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1))).normalized()) for q in range(30)]
    # colina nocturna
    W["hill"] = g = group("hill", O_HL)
    B = Batch("hl_b", g, 1.0)
    B.add((0, 0, -0.06), (300, 300, 0.1), tmat("grassn", "#2A4A2A", 16, 0.10, 198))
    for q in range(300): B.add((r.uniform(-80, 80), r.uniform(40, 60), r.uniform(10, 70)), (0.15, 0.15, 0.15), "#FFFFFF")
    B.done()
    W["streaks"] = [(box(f"ms{q}", (0, 0, 0), (0.08, 0.08, 2.5), mat("#FFF2C8")), r.uniform(-1, 1), r.uniform(0, 1), r.uniform(0, 1)) for q in range(40)]
    W["bigast"] = box("bigast", (0, 0, 0), (2.0, 2.0, 2.0), mat("#FFD080"))
    W["marcos"] = Person("marcos", MARCOS)
    W["clara"] = Person("clara", CLARA)
    W["dad"] = Person("dadp", DAD, 0.98)
    W["boss"] = Person("boss", dict(npc_look(805), top="#2A2A30", top2="#2A2A30", stripe="#C0302A"), 1.0)
    camera(28)
    return W

def hide_all(W):
    W["office"].show(False)
    c = W["city"]; show(c.g, False)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True)
    for k in ("vil", "view", "chaos", "home", "sp", "probe", "hill", "soldcar"): show(W[k], False)
    hid(W["stars"], True)
    for k in ("badge", "sky_ast", "tv", "tvbox", "meteor", "sun", "carkey", "bigast"): hid(W[k], True)
    for o in W["trail"] + W["smoke"]: hid(o, True)
    for lst in ("shards", "frags", "streaks"):
        for it in W[lst]: hid(it[0], True)
    for c_, x, y in W["jam"]: show(c_, False)
    for p in ("marcos", "clara", "dad", "boss", "buyer"): W[p].show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def person(W, key, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    H = W[key]; H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_)
    return H

def city(W, dusk=0.0):
    c = W["city"]; show(c.g, True)
    for d, a, b, cc in c.rain: hid(d, True)
    hid(c.glass, True); show(c.car, False)
    world_color(lerpv(hexc("#B8D0E0"), hexc("#E89060"), dusk)); light_dir((0.45, -0.55, 0.7)); shadow(0.5)

# ------------------------------------------------------------------ planos
@shot(0.0, 5.74)
def a1(W, T, M):
    of = W["office"]; of.show(True); world_color("#E8ECF0"); light_dir((0.4, -0.5, 0.75)); shadow(0.45)
    k = T/5.74; O = O_OF
    hid(W["sky_ast"], False); W["sky_ast"].location = (O[0]-1.0, O[1]+9.0, 3.2)
    B = W["boss"]; B.show(True); B.place(O[0]+0.4, O[1]+0.9, 180); B.idle(T); B.face(T, "shock" if T > 3.2 else "neutral", (0, 0))
    H = person(W, "marcos", O[0]+0.4, O[1]-0.9, 180, T, "smirk", (0, 0.2))
    bd = W["badge"]; hid(bd, False)
    if T < 3.1:
        H.arm(1, fwd=1.5, side=0.1, elbow=0.4)
        bpy.context.view_layer.update(); bd.location = tuple(H.hand[1].matrix_world @ Vector((0, -0.06, -0.12)))
    else:
        f = clamp((T-3.1)/0.35); bd.location = (O[0]+0.5, O[1]+lerp(-0.4, 0.4, f), lerp(1.4, 0.81, f)+0.3*math.sin(f*math.pi)); bd.rotation_euler = (math.pi/2*f, 0, 0)
    look(lerpv((O[0]+2.8, O[1]-0.8, 1.7), (O[0]+2.3, O[1]-0.3, 1.65), eio(k)), (O[0]+0.4, O[1]-0.1, 1.4), 26)
    M["grade"] = "office"

@shot(5.74, 12.86)
def a2(W, T, M):
    city(W, 0.2); k = (T-5.74)/7.12
    tb = W["tvbox"]; hid(tb, False); tb.location = (6.0, 5.95, 5.2)
    tv = W["tv"]; hid(tv, False); tv.location = (6.0, 5.88, 5.05)
    hid(W["sky_ast"], False); W["sky_ast"].location = (lerp(-20, -12, k), 30, 22)
    H = person(W, "marcos", 4.2, 3.6, 160, T, "shock", (0.6, 0.9))
    look(lerpv((2.0, -3.0, 1.4), (2.6, -2.0, 1.6), eio(k)), (5.0, 6.0, lerp(3.0, 5.0, eio(clamp((T-5.8)/2.0)))), 22)
    M["grade"] = "day_sad"

@shot(12.86, 20.8)
def a3(W, T, M):
    show(W["vil"], True); world_color("#C8D4E0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-12.86)/7.94; o = O_V
    f = clamp((T-13.0)/3.0)
    mx = lerp(-40, 30, f); mz = lerp(40, 18, f)
    hid(W["meteor"], f >= 1.0); W["meteor"].location = (o[0]+mx, o[1]+30, mz)
    for q, t in enumerate(W["trail"]):
        g = f-q*0.02
        if g <= 0: continue
        hid(t, False); t.location = (o[0]+lerp(-40, 30, g), o[1]+30, lerp(40, 18, g)); s = 1.0+q*0.12; t.scale = (s, s, s)
    if T > 16.3:
        for b, a, ph, c in W["shards"]:
            tt = (T-16.3)*1.5
            hid(b, tt > 2.5); b.location = (o[0]+a*6, o[1]+5.0-tt*3*ph, max(0.05, 3+c*2.0-4.9*tt*tt*0.5)); b.rotation_euler = (tt*5, tt*3, 0)
    sx_, sy_, sz_ = shake(T, 0.12 if 16.3 < T < 17.2 else 0.0)
    look((o[0]-2.0+sx_, o[1]-8.0+sy_, 1.8+sz_), (o[0]+2.0, o[1]+20, 14), 24)
    if 16.3 < T < 16.45: M["flash"] = 1
    M["grade"] = "cold"

@shot(20.8, 29.28)
def a4(W, T, M):
    k = (T-20.8)/8.48
    if T < 24.4:
        city(W, 0.1)
        c = W["soldcar"]; show(c, True); c.location = (1.5, 1.5, 0)
        H = person(W, "marcos", -0.4, -0.2, 70, T, "smirk", (0.3, 0)); H.arm(1, fwd=1.4, side=0.0, elbow=0.4)
        Bu = W["buyer"]; Bu.show(True); Bu.place(0.6, -0.2, -90); Bu.idle(T); Bu.face(T, "happy", (0, 0)); Bu.arm(1, fwd=1.3, side=0.0, elbow=0.5)
        bpy.context.view_layer.update(); kk = W["carkey"]; hid(kk, False); kk.location = tuple(H.hand[1].matrix_world @ Vector((0, -0.06, -0.12)))
        look((0.2, -4.2, 1.6), (0.2, 0.0, 1.3), 26)
        M["grade"] = "day"
    else:
        show(W["view"], True); world_color("#F0A070"); light_dir((0.3, -0.8, 0.4)); shadow(0.4); o = O_P
        hid(W["sun"], False); W["sun"].location = (o[0]+8, o[1]+60, 8)
        H = person(W, "marcos", o[0]-0.45, o[1]+1.2, -60 if T < 26.5 else 180, T, "worried" if T < 26.0 else "happy", (0.2, 0))
        Cl = W["clara"]; Cl.show(True); Cl.place(o[0]+0.45, o[1]+1.2, 60 if T < 26.5 else 180); Cl.idle(T); Cl.face(T, "shock" if T < 27.0 else "happy", (0, 0))
        if T > 27.0: H.arm(1, fwd=0.4, side=0.3, elbow=0.2); Cl.arm(-1, fwd=0.4, side=0.3, elbow=0.2)
        look(lerpv((o[0]+0.5, o[1]-3.4, 1.4), (o[0]+0.3, o[1]-2.6, 1.45), eio(clamp((T-24.4)/4.9))), (o[0], o[1]+1.2, 1.4), 26)
        M["grade"] = "dawn"

@shot(29.28, 39.58)
def a5(W, T, M):
    k = (T-29.28)/10.3
    show(W["chaos"], True); world_color("#B8B0A0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45); o = O_X
    for c_, x, y in W["jam"]: show(c_, True); c_.location = (o[0]+x, o[1]+y, 0); c_.rotation_euler = (0, 0, math.pi/2+0.15*math.sin(y))
    for q, s in enumerate(W["smoke"]):
        tt = (T*0.2+q/6) % 1.0; hid(s, False); sc = 1+2*tt; s.scale = (sc, sc, sc); s.location = (o[0]+15+q*3, o[1]+30+q*4, 3+tt*10)
    if T < 35.5:
        H = W["marcos"]; H.show(True); y = o[1]-6+0.9*(T-29.28); H.place(o[0]+4.6, y, 180); H.walk(T*1.3); H.face(T, "worried", (0.3, 0))
        look((o[0]+7.5, y-6.5, 2.6), (o[0]+2.5, y+6.0, 1.0), 24)
        M["grade"] = "day_sad"
    else:
        show(W["chaos"], False)
        for c_, x, y in W["jam"]: show(c_, False)
        for s in W["smoke"]: hid(s, True)
        show(W["home"], True); world_color("#E8A070"); o = O_F
        H = person(W, "marcos", o[0]-0.5, o[1]+1.6, 160, T, "worried", (0.2, 0))
        D = W["dad"]; D.show(True); D.place(o[0]+0.4, o[1]+2.4, 200); D.idle(T); D.face(T, "shock" if T < 37.5 else "sad", (0, 0))
        if T > 37.6:
            H.arm(1, fwd=1.3, side=0.0, elbow=0.4); D.arm(1, fwd=1.3, side=0.0, elbow=0.4)
        look(lerpv((o[0]+1.4, o[1]-2.4, 1.7), (o[0]+1.0, o[1]-1.6, 1.6), eio(clamp((T-35.5)/4.0))), (o[0], o[1]+2.0, 1.5), 26)
        M["grade"] = "dawn"

@shot(39.58, 50.78)
def a6(W, T, M):
    show(W["sp"], True); hid(W["stars"], False); world_color("#04050A"); light_dir((0.6, -0.5, 0.6)); shadow(0.3)
    k = (T-39.58)/11.2; o = O_SP
    W["sp"].rotation_euler = (0.2, T*0.1, T*0.15)
    f = clamp((T-40.0)/9.5)
    pb = W["probe"]; show(pb, True); pb.location = (o[0]-18+15*f, o[1]-4+3*f, 2-1.5*f); pb.rotation_euler = (0, 0, 0.2); pb.scale = (2.5, 2.5, 2.5)
    look(lerpv((o[0]-8, o[1]-14, 3), (o[0]-4, o[1]-10, 1.5), eio(k)), (o[0]-3+3*f, o[1], 0.5), 28)
    M["grade"] = "night"

@shot(50.78, 62.76)
def a7(W, T, M):
    show(W["hill"], True); world_color("#0A1028"); light_dir((0.3, -0.5, 0.8)); shadow(0.3); o = O_HL
    k = (T-50.78)/11.98
    boom = 55.0
    ba = W["bigast"]
    if T < boom:
        hid(ba, False); s = lerp(1.0, 1.6, clamp((T-50.8)/4.2)); ba.scale = (s, s, s); ba.location = (o[0]+4, o[1]+50, 30)
    else:
        for b, a, ph, c in W["streaks"]:
            tt = ((T-boom)*0.6+ph) % 1.0
            hid(b, False); b.location = (o[0]+a*40+tt*10, o[1]+48, 50-tt*45); b.rotation_euler = (0, 0.4, 0)
    for q, (key, x) in enumerate((("dad", -0.9), ("marcos", 0.0), ("clara", 0.9))):
        P = person(W, key, o[0]+x, o[1], 180, T, "shock" if T < boom+1 else "happy", (0, 0.9))
    if T < boom:
        look((o[0]+0.6, o[1]-5.0, 1.0), (o[0]+2.0, o[1]+50, lerp(16, 26, clamp((T-50.8)/3.0))), 24)
    else:
        look(lerpv((o[0]+0.6, o[1]-5.0, 1.0), (o[0]+1.0, o[1]-6.5, 0.8), eio(clamp((T-boom)/7.0))), (o[0]+1.0, o[1]+40, 22), 22)
    if boom < T < boom+0.12: M["flash"] = 1
    M["grade"] = "night"

@shot(62.76, 70.64)
def a8(W, T, M):
    city(W, 0.0); k = (T-62.76)/7.88
    H = person(W, "marcos", 3.0, 4.2, 0, T, "sad" if T < 67.7 else "smirk", (0, 0))
    if T > 67.7:
        for sx in (-1, 1): H.arm(sx, fwd=0.3, side=0.6, elbow=1.4); H.fingers(sx, 0.0, 0.0)
    look(lerpv((3.6, -0.5, 1.7), (3.4, 1.4, 1.65), eio(k)), (3.0, 4.2, 1.5), 26)
    M["grade"] = "day"

@shot(70.64, 74.06)
def a9(W, T, M):
    city(W, 0.6); k = (T-70.64)/3.42
    H = person(W, "marcos", 3.0, 4.2, 0, T, "happy", (0, 0))
    D = W["dad"]; D.show(True); D.place(2.2, 4.4, 10); D.idle(T); D.face(T, "happy", (0, 0)); D.arm(-1, fwd=0.2, side=-1.0, elbow=0.6)
    if T > 72.4:
        Cl = W["clara"]; Cl.show(True); Cl.place(3.8, 4.3, -10); Cl.idle(T); Cl.face(T, "happy", (0, 0)); Cl.arm(1, fwd=0.2, side=0.3, elbow=0.1); H.arm(-1, fwd=0.2, side=0.3, elbow=0.1)
    look(lerpv((3.4, -0.4, 1.6), (3.3, 0.6, 1.6), eio(k)), (3.0, 4.2, 1.4), 26)
    M["grade"] = "dawn"

@shot(74.06, TOTAL+0.1)
def a10(W, T, M):
    city(W, 0.6); k = (T-74.06)/3.17
    H = person(W, "marcos", 3.0, 4.2, 0, T, "smirk", (0, 0.1))
    H.arm(1, fwd=1.2, side=0.1, elbow=1.4); H.fingers(1, 0.6, 0.2)
    look(lerpv((3.4, 1.4, 1.65), (3.3, 2.1, 1.62), eio(k)), (3.0, 4.2, 1.5), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-76.8)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
