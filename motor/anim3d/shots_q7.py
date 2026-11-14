"""Q7 · «¿Qué pasaría si un tiranosaurio apareciera en tu calle?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral) colocada en 0,15 s. Tiempos de plano = timeline de align.py."""
import math, random
import numpy as np
from vox import *
from person import Person, npc_look
from world import City, car, Batch, tmat
from dino import TRex, Chicken, Bike

FPS = 24
TOTAL = 56.6
HUGO = dict(skin="#E0B08A", hair="#2A1E18", hair2="#3A2A20", eye="#3A5A2A", top="#D8452E", top2="#B03A26", stripe="#F4F1EA",
            legs="#2F3A52", legs2="#273046", shoe="#F4F1EA", shoe2="#2E8BD0", watch=False, hstyle="short")
REXC = ["#5E7A3A", "#6E6A3A", "#4E6E4A", "#7A5E3A", "#5A6A4A", "#6A7A3A"]

class Env:
    def talk(self, who, T): return 0.0

def build():
    reset((720, 1280))
    W = {}
    W["city"] = City()
    W["city"].car.location = (-60, 1.3, 0)
    W["hugo"] = Person("hugo", HUGO)
    W["npc"] = [Person(f"npc{i}", npc_look(300+i), 0.94+0.12*random.Random(i).random()) for i in range(26)]
    W["rex"] = [TRex(f"rex{i}", REXC[i % len(REXC)], s=1.0 if i == 0 else 0.92+0.1*random.Random(i).random()) for i in range(12)]
    W["bike"] = Bike("bike")
    W["bus"] = g = group("bus")
    B = Batch("bus_b", g, 0.5)
    B.add((0, 0, 1.85), (14.0, 3.0, 3.1), "#D23A2E"); B.add((0, 0, 3.45), (13.8, 2.9, 0.12), "#E8E4DA")
    for i in range(9): B.add((-5.8+i*1.4, -1.52, 2.35), (1.1, 0.04, 1.0), "#9FD0E8")
    B.add((6.98, 0, 2.3), (0.06, 2.6, 1.4), "#9FD0E8")
    for x in (-4.5, 4.5):
        for y in (-1.45, 1.45): B.add((x, y, 0.5), (1.0, 0.3, 1.0), "#1C1C20")
    B.add((0, -1.52, 1.15), (14, 0.04, 0.3), "#F4F1EA"); B.done()
    # coches del atasco
    W["jam"] = [car(f"jam{i}", c) for i, c in enumerate(("#3A6AA8", "#E0E0D8", "#2A2A2E", "#5A8A5A", "#E0C040", "#7A4E8A"))]
    # ventana (primer plano del plano 1)
    W["win"] = g = group("winfg")
    B = Batch("win_b", g, 1.0)
    wood = tmat("wood", "#F2EEE6", 8, 0.04, 9)
    B.add((-1.05, 0, 4.6), (0.16, 0.16, 3.4), wood); B.add((1.05, 0, 4.6), (0.16, 0.16, 3.4), wood)
    B.add((0, 0, 3.0), (2.3, 0.3, 0.18), wood); B.add((0, 0, 6.2), (2.3, 0.16, 0.18), wood)
    B.add((0, 0.02, 4.6), (0.08, 0.1, 3.2), wood)
    B.add((-1.5, -0.1, 4.6), (0.6, 0.2, 3.4), "#C04848"); B.add((1.5, -0.1, 4.6), (0.6, 0.2, 3.4), "#C04848")
    B.add((0.4, 0.05, 3.15), (0.3, 0.3, 0.2), "#6A4A30"); B.add((0.4, 0.05, 3.42), (0.36, 0.36, 0.36), "#4E8A3A")
    B.done()
    # azotea (plano del pánico)
    W["roof"] = g = group("roofset")
    B = Batch("roof_b", g, 1.0)
    B.add((0, 0, 4.5), (9.0, 4.4, 9.0), tmat("roofwall", "#C8A27A", 16, 0.07, 41))
    B.add((0, 0, 9.04), (9.0, 4.4, 0.08), tmat("rooftop", "#8A8A90", 16, 0.08, 42))
    for x in (-4.45, 4.45): B.add((x, 0, 9.3), (0.12, 4.4, 0.5), "#6A6A72")
    B.add((0, -2.17, 9.3), (9.0, 0.12, 0.5), "#6A6A72")
    B.add((3.0, 1.2, 9.6), (1.0, 1.0, 1.1), "#9AA0A8"); B.add((-3.2, 1.4, 9.5), (0.5, 0.5, 0.9), "#4A4A52")
    B.done(); g.location = (-1.0, 8.4, 0)
    # manada lejana (siluetas fijas de bloques)
    W["horde"] = g = group("horde")
    B = Batch("horde_b", g, 1.0)
    r = random.Random(5)
    for i in range(170):
        x = r.uniform(14, 70); y = r.uniform(-2.6, 2.6)
        s = r.uniform(0.75, 1.0); c = r.choice(REXC); h = 3.6*s
        B.add((x, y, h), (4.0*s, 1.8*s, 2.0*s), c)                       # cuerpo
        B.add((x+3.4*s, y, h+0.4*s), (2.4*s, 1.2*s, 1.0*s), c)            # cabeza (mira a −X: cola hacia +X)
        B.add((x-2.9*s, y, h), (3.5*s, 1.1*s, 0.9*s), c)
        for sy in (-0.6, 0.6): B.add((x+0.2*s, y+sy*s, h/2-0.4*s), (0.7*s, 0.6*s, h-0.4*s), c)
    B.done()
    g.rotation_euler = (0, 0, math.pi); g.location = (0, 0, 0)
    # laboratorio (proteínas)
    O = (0, 500, 0); W["lab"] = g = group("lab", O)
    B = Batch("lab_b", g, 1.0)
    B.add((0, 6, 6), (60, 0.4, 14), tmat("labwall", "#E8ECF0", 16, 0.03, 61, None))
    B.add((0, 0, -0.1), (60, 20, 0.2), tmat("labfloor", "#D8DCE2", 16, 0.04, 62, None))
    B.add((6.5, 0.5, 0.6), (2.4, 2.4, 1.2), "#3A6EA8")
    B.done()
    W["helix"] = []
    for i in range(22):
        a = box(f"hx{i}a", (0, 0, 0), (0.42, 0.42, 0.42), mat("#2E8BD0" if i % 2 else "#E0A030"))
        b = box(f"hx{i}b", (0, 0, 0), (0.42, 0.42, 0.42), mat("#D8452E" if i % 2 else "#5BC08A"))
        c = box(f"hx{i}c", (0, 0, 0), (0.12, 0.12, 0.12), mat("#B8BCC4"))
        W["helix"].append((a, b, c))
    W["hen"] = Chicken("hen", 1.9)
    W["hen2"] = Chicken("hen2", 0.55)
    W["corn"] = [box(f"corn{i}", (0, 0, 0), (0.09, 0.09, 0.09), mat("#F4C430")) for i in range(30)]
    camera(28)
    return W

def hide_all(W):
    show(W["city"].g, False); W["city"].rain_on = False
    for k in ("bus", "win", "roof", "horde", "lab"): show(W[k], False)
    for a, b, c in W["helix"]: hid(a, True); hid(b, True); hid(c, True)
    for p in [W["hugo"]] + W["npc"]: p.show(False)
    for r in W["rex"]: r.show(False)
    W["bike"].show(False); W["hen"].show(False); W["hen2"].show(False)
    for c in W["jam"]: show(c, False)
    for c in W["corn"]: hid(c, True)
    show(W["city"].car, False)

def day(W, rain=False):
    show(W["city"].g, True)
    for d, *_ in W["city"].rain: hid(d, True)
    hid(W["city"].glass, True)
    show(W["city"].car, False)
    world_color("#9CC8E8"); light_dir((0.5, -0.45, 0.75)); shadow(0.5)

def fleeing(W, T, n=14, x0=-6, dirx=-1, seed=0, center=0.0):
    for i, p in enumerate(W["npc"]):
        if i >= n: continue
        r = random.Random(i+seed); p.show(True)
        side = 1 if i % 2 else -1
        y = side*(3.8+r.random()*1.6) if i % 3 else r.uniform(-2.4, 2.4)
        sp = 3.2+r.random()*1.4
        x = center + x0 + r.uniform(-9, 9) + dirx*sp*(T % 40)*0.25
        p.place(x, y, 90 if dirx > 0 else -90)
        p.walk(T*1.6+r.random(), 1.0, run=True)
        p.face(T, "scared", (0, 0.3))
        if i % 4 == 0: p.arm(1, fwd=2.6, side=0.2, elbow=0.3)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

# ------------------------------------------------------------------ planos
@shot(0.0, 2.4)
def a1(W, T, M):
    day(W); W["win"].location = (-0.15, 4.4, 2.99); W["win"].scale = (0.42, 1, 0.35)
    R = W["rex"][0]; R.show(True); R.place(lerp(12.0, 10.5, T/2.4), -0.6, 168)
    rr = clamp((T-0.55)/0.5) if T < 1.9 else clamp(1-(T-1.9)/0.4)
    R.pose(T, walk=None if T > 0.5 else T*0.6, roar=ease(rr), head_yaw=-0.5)
    fleeing(W, T, 10, 2, -1)
    k = eio(T/2.4)
    sx, sy, sz = shake(T, 0.03 if 0.8 < T < 1.9 else 0)
    look((lerp(1.6, 1.4, k)+sx, lerp(5.3, 2.2, k)+sy, lerp(5.2, 3.4, k)+sz), (7.0, -0.6, lerp(5.4, 5.0, k)), 18)
    M["grade"] = "day"

@shot(2.4, 5.08)
def a2(W, T, M):
    day(W); k = (T-2.4)/2.68
    R = W["rex"][0]; R.show(True); x = lerp(4.0, -0.5, k); R.place(x, -0.2, 180); R.pose(T, walk=(T-2.4)*0.55, jaw=0.25+0.2*math.sin(T*3))
    H = W["hugo"]; H.show(True); H.place(-7.0, -2.7, 0); H.face_to(-7.0, -2.7, x+4, -0.2); H.idle(T)
    H.arm(1, fwd=0.9, side=0.3, elbow=1.6); H.arm(-1, fwd=0.9, side=0.3, elbow=1.6); H.face(T, "shock", (0.6, 0.6))
    fleeing(W, T, 12, -4, -1, 7)
    st = 0.04*max(0, math.sin((T-2.4)*0.55*2*math.pi))**8
    sx, sy, sz = shake(T, st)
    look((lerp(-10.0, -10.4, k)+sx, -4.4+sy, 1.35+sz), (-2.5, -0.6, lerp(3.2, 3.6, k)), 19)
    M["grade"] = "day"

@shot(5.08, 9.94)
def a3(W, T, M):
    day(W); k = (T-5.08)/4.86
    show(W["bus"], True); W["bus"].location = (0.6, -1.6, 0)
    R = W["rex"][0]; R.show(True); R.place(-0.4, 1.5, 180); R.pose(T, head_yaw=0.15*math.sin(T*0.8), jaw=0.15)
    H = W["hugo"]; H.show(True); H.place(-9.6, -4.0, -40); H.idle(T); H.face(T, "shock", (0.5, 0.8))
    look((lerp(-17.0, -15.0, eio(k)), -0.1, lerp(13.5, 12.5, k)), (lerp(1.0, 1.5, k), 0.0, 2.2), 22)
    M["grade"] = "day"

@shot(9.94, 13.72)
def a4(W, T, M):
    day(W); k = (T-9.94)/3.78
    R = W["rex"][0]; R.show(True); R.place(0.3, 1.6, 0)
    R.pose(T, jaw=ease(clamp((k-0.1)/0.4))*0.9, roar=0.0, head_yaw=-0.35, head_pitch=0.15)
    look(lerpv((8.4, -4.2, 6.2), (7.4, -3.2, 6.0), eio(k)), (5.2, 0.9, 5.9), 26, fstop=3.0)
    M["grade"] = "day"

@shot(13.72, 16.68)
def a5(W, T, M):
    day(W); k = T-13.72
    c = W["city"].car; show(c, True); c.location = (6.9, 1.0, 0); c.rotation_euler = (0, 0, math.pi/2)
    bite = 15.45
    R = W["rex"][0]; R.show(True); R.place(0.6, 1.0, 0)
    dn = ease(clamp(k/1.0)) if T < bite+0.45 else lerp(1, 0.5, ease((T-bite-0.45)/0.8))
    jaw = ease(clamp((k-0.3)/0.6)) if T < bite else max(0, 0.12*math.sin((T-bite)*18)*(1-(T-bite)))
    R.pose(T, peck=dn*1.05, crouch=dn*0.8, jaw=jaw)
    crush = clamp((T-bite)/0.12)
    c.scale = (1, 1, lerp(1, 0.42, crush)); c.location.z = 0
    sx, sy, sz = shake(T, 0.12*clamp(1-(T-bite)/0.6) if T > bite else 0)
    look((0.6+sx, -5.3+sy, 2.0+sz), (5.6, 1.0, 1.6), 20)
    M["grade"] = "day"
    if bite < T < bite+0.15: M["flash"] = 1

@shot(16.68, 22.2)
def a6(W, T, M):
    day(W); k = T-16.68
    hx = 12.0 - 3.3*k
    H = W["hugo"]; H.show(True); H.place(hx, -4.4, -90); H.walk(k*1.7, 1.0, run=True)
    look_back = 1.8 < k < 3.6
    H.face(T, "scared", (0.9 if look_back else 0, 0.2))
    if look_back: H.head.rotation_euler = (0, 0, -1.2)
    R = W["rex"][0]; R.show(True); rx = hx + 10.5 + 0.3*k; R.place(rx, -0.6, 180); R.pose(T, walk=k*0.42, jaw=0.4)
    fleeing(W, T, 6, -6, -1, 3, center=hx)
    look((hx-6.4, -2.2, 1.7), (hx+3.0, -2.8, 2.6), 21)
    M["grade"] = "day"

@shot(22.2, 23.6)
def a7(W, T, M):
    day(W); k = T-22.2
    bx = 2.0 - 7.5*k
    B = W["bike"]; B.show(True); B.place(bx, -1.8, 180); B.spin(-k*14)
    H = W["hugo"]; H.show(True); H.place(bx-0.2, -1.8, -90, 0.32)
    for sx in (-1, 1):
        ph = k*9 + (0 if sx > 0 else math.pi)
        H.leg(sx, fwd=1.25+0.35*math.sin(ph), knee=1.35+0.35*math.cos(ph))
    H.arm(-1, fwd=1.2, side=0.1, elbow=0.4); H.arm(1, fwd=1.2, side=0.1, elbow=0.4)
    H.chest.rotation_euler = (-0.35, 0, 0); H.hips.location.z = 0.78
    H.face(T, "happy", (-0.6, 0))
    R = W["rex"][0]; R.show(True); R.place(14.0, -0.6, 180); R.pose(T, walk=None, head_yaw=0.2*math.sin(T*2), crouch=0.0)
    look((bx-4.6, -2.9, 1.3), (bx+2.0, -1.6, 1.5), 20)
    M["grade"] = "day"

@shot(23.6, 31.3)
def a8(W, T, M):
    day(W); k = T-23.6
    n = 1 if T < 26.3 else (5 if T < 27.05 else 12)
    for i, R in enumerate(W["rex"]):
        if i >= n: continue
        r = random.Random(i*7)
        R.show(True)
        x = (0 if i == 0 else 4 + (i % 4)*5.5 + r.uniform(-1, 1)) - 1.4*k
        y = 0 if i == 0 else [-1.6, 1.6, 0.0, -0.8, 0.8][i % 5]
        z = 0
        if i in (6, 9):   # dos sobre los tejados de enfrente
            y = 9.0 if i == 6 else -9.6; z = 8.0 if i == 6 else 9.0
        R.place(x, y, 180, z); R.pose(T+i, walk=k*0.38+i*0.21, jaw=0.3+0.3*math.sin(T*2+i))
    show(W["horde"], T > 27.8)
    W["horde"].location = (-1.4*k, 0, 0)
    fleeing(W, T, 14, -10, -1, 11)
    kk = eio(clamp((T-23.6)/7.2))
    if T < 27.8:
        look(lerpv((-11, -1.5, 3.0), (-16, -4.0, 12), eio(k/4.2)), (4.0, 0, 3.0), 22)
    else:
        kk = eio((T-27.8)/3.5)
        look(lerpv((-16, -4.0, 12), (-26, -16, 34), kk), lerpv((4.0, 0, 3.0), (22, 0, 0), kk), lerp(22, 20, kk))
    M["grade"] = "day"
    M["chip"] = 1

@shot(31.3, 36.72)
def a9(W, T, M):
    day(W); k = T-31.3
    show(W["roof"], True)
    for i, p in enumerate(W["npc"]):
        r = random.Random(i+50)
        if i < 7:
            p.show(True); p.place(-4.9+i*0.75+r.uniform(-0.2, 0.2), 7.6+r.uniform(-0.3, 1.0), r.uniform(-30, 30), 9.08)
            p.idle(T); p.face(T, "scared", (0, 0.5))
            if i % 2: p.arm(1, fwd=2.8+0.3*math.sin(T*9+i), side=0.3, elbow=0.2)
            if i % 3 == 0: p.arm(-1, fwd=2.8+0.3*math.sin(T*8+i), side=0.3, elbow=0.2)
        elif i < 20:
            p.show(True); x = -12+(i-7)*2.2+r.uniform(-0.5, 0.5) - 3.5*k*(0.7+r.random()*0.6)
            p.place(x, r.choice([-4.6, -4.0, 4.0, 4.8]), -90); p.walk(T*1.7+i, 1, run=True); p.face(T, "scared", (0, 0))
    for i, c in enumerate(W["jam"]):
        show(c, True); c.location = (-9+i*4.4, -1.4 if i % 2 else 1.4, 0); c.rotation_euler = (0, 0, 0 if i % 2 else math.pi)
    H = W["hugo"]; H.show(True); H.place(-1.2, 6.6, 20, 9.08); H.idle(T); H.face(T, "worried", (0.3, 0.6))
    for i in range(3):
        R = W["rex"][i]; R.show(True); R.place(14 + i*7 - 2.6*k, [0.4, -1.8, 1.6][i], 180); R.pose(T+i, walk=k*0.4+i*0.3, jaw=0.4)
    a = lerp(-0.25, 0.2, eio(k/5.4))
    look((-7.0+2*a, 11.6, 16.0), (6.0, -1.0, 0.0), 20)
    M["grade"] = "alarm"; M["alarm"] = 1

@shot(36.72, 39.66)
def a10(W, T, M):
    day(W); world_color("#202838"); shadow(0.7); light_dir((0.2, -0.7, 0.4))
    k = (T-36.72)/2.94
    R = W["rex"][0]; R.show(True); R.place(0.3, 1.6, 0); R.pose(T, head_yaw=-0.5, jaw=0.05)
    # el ojo derecho (lado −Y) queda hacia la cámara
    look(lerpv((7.4, -5.0, 6.8), (6.2, -3.4, 6.6), eio(k)), (4.85, 0.6, 6.3), 30, fstop=2.2)
    M["grade"] = "night"

@shot(39.66, 47.3)
def a11(W, T, M):
    k = T-39.66
    world_color("#E8ECF0"); light_dir((0.3, -0.6, 0.8)); shadow(0.35)
    show(W["lab"], True)
    R = W["rex"][0]; R.show(True); R.place(-7.5, 501.0, 0); R.pose(T, head_yaw=-0.3, jaw=0.2*math.sin(T*2)**2)
    for i, (a, b, c) in enumerate(W["helix"]):
        hid(a, False); hid(b, False); hid(c, False)
        z = 1.0 + i*0.42; ang = i*0.55 + T*1.4
        a.location = (0.0+math.cos(ang)*0.9, 501.0+math.sin(ang)*0.9, z); b.location = (0.0-math.cos(ang)*0.9, 501.0-math.sin(ang)*0.9, z)
        c.location = (0, 501.0, z); c.scale = (abs(math.cos(ang))*14+1, abs(math.sin(ang))*14+1, 1)
        a.rotation_euler = b.rotation_euler = (0, 0, ang)
    pop = ease(clamp((T-44.3)/0.35))
    Hn = W["hen"]; Hn.show(pop > 0.01); Hn.place(6.5, 500.5, 180, 1.2); Hn.root.scale = (pop, pop, pop)
    Hn.pose(T, peck=max(0, math.sin((T-45.4)*7))*0.8 if T > 45.4 else 0)
    if T < 43.0:
        kk = eio(k/3.34); look(lerpv((-3.5, 487.0, 6.5), (-1.0, 487.5, 5.5), kk), lerpv((-3.0, 501, 5.0), (0.0, 501, 4.6), kk), 26)
    else:
        kk = eio((T-43.0)/2.4); look(lerpv((-1.0, 487.5, 5.5), (4.2, 493.0, 3.4), kk), lerpv((0.0, 501, 4.6), (5.6, 500.6, 2.4), kk), lerp(26, 24, kk))
    M["grade"] = "lab"

@shot(47.3, 52.16)
def a12(W, T, M):
    day(W); k = T-47.3
    H = W["hugo"]; H.show(True); H.place(-1.9, -2.2, 60); H.idle(T)
    thr = clamp((k-1.4)/0.5)
    H.arm(1, fwd=lerp(0.3, 2.2, ease(thr)) if k < 2.4 else 0.6, side=0.2, elbow=lerp(1.6, 0.2, ease(thr)) if k < 2.4 else 0.4)
    H.face(T, "happy" if k > 2.6 else "worried", (0.8, 0.3))
    R = W["rex"][0]; R.show(True); R.place(5.4, -0.4, 200)
    pk = max(0, math.sin((k-2.9)*6.0)) if k > 2.9 else 0
    R.pose(T, peck=0.8+0.3*pk if k > 2.6 else 0.15*ease(k/2.6), crouch=0.9 if k > 2.6 else 0.2, jaw=0.3*pk)
    for i, c in enumerate(W["corn"]):
        r = random.Random(i)
        t0 = 1.75+r.random()*0.15
        if k < t0: continue
        hid(c, False); u = clamp((k-t0)/0.75)
        tx, ty = 2.2+r.uniform(-0.8, 0.8), -1.7+r.uniform(-0.7, 0.7)
        c.location = (lerp(-1.4, tx, u), lerp(-1.9, ty, u), 1.9+2.2*u*(1-u)*2 - 1.7*u)
        if k > 2.9 and r.random() < clamp((k-2.9)/2.0): hid(c, True)
    Hn = W["hen2"]; Hn.show(True); Hn.place(-0.6, -2.9, 0); Hn.pose(T, peck=max(0, math.sin(T*7))*0.8 if k > 2.0 else 0)
    look(lerpv((-7.6, -2.2, 2.5), (-7.0, -2.4, 2.4), eio(k/4.86)), (2.5, -1.2, 3.0), 20)
    M["grade"] = "day"

@shot(52.16, TOTAL+0.1)
def a13(W, T, M):
    day(W); k = T-52.16
    H = W["hugo"]; H.show(True); H.place(-4.0, -1.8, -60); H.idle(T); H.face(T, "smirk", (0, 0.2))
    H.arm(1, fwd=0.3, side=0.9, elbow=1.8)
    R = W["rex"][0]; R.show(True); R.place(3.0, 0.6, 195); R.pose(T, head_yaw=0.3, head_pitch=0.35, jaw=0.15)
    Hn = W["hen2"]; Hn.show(True); Hn.place(-4.8, -2.6, 120); Hn.pose(T)
    look(lerpv((-11.0, -1.2, 2.4), (-10.0, -1.4, 2.6), eio(k/4.4)), (0.0, -0.6, lerp(3.0, 3.6, k/4.4)), 18)
    M["grade"] = "day"; M["fade"] = clamp((T-56.15)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    cam = bpy.context.scene.camera.location
    keep = [W["hugo"].root.location.copy()]
    for p in W["npc"]:
        if DES.get(p.root.name, (None, True))[1]: continue
        l = p.root.location
        if math.hypot(l.x-cam.x, l.y-cam.y) < 1.6 and abs(l.z-cam.z) < 3 or any(math.hypot(l.x-q.x, l.y-q.y) < 0.8 and abs(l.z-q.z) < 1 for q in keep):
            p.show(False)
    apply_vis()
    return M
