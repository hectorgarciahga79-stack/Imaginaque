"""Q8 · «¿Qué pasa si mil millones de zombis salen del mar?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral, atempo 1,06) colocada en 0,15 s. Tiempos de plano = timeline de align.py.
Decorados propios: playa con paseo marítimo (origen), fondo marino (y=600), cabina de sonar (y=900)."""
import math, random
import numpy as np
from vox import *
from person import Person, npc_look
from world import Batch, tmat, building, tree, text3d, tiles

FPS = 24
TOTAL = 62.64
BRUNO = dict(skin="#E8BC94", hair="#3A2618", hair2="#4A3020", eye="#2B4A8A", top="#E23A2E", top2="#B82E24", stripe="#FBF6E8",
             legs="#F2C230", legs2="#D8A820", shoe="#2A2A2E", shoe2="#F4F1EA", watch=False, hstyle="short")
ZSKIN = ["#8FAE7A", "#9AB88A", "#7E9C70", "#A4B890", "#88A07A"]
ZTOP = ["#5A6A72", "#6E5A4E", "#4E5E6E", "#7A6A50", "#56604A", "#6A4E5A", "#4A5A50"]

def zlook(i):
    L = npc_look(700+i); r = random.Random(i)
    L.update(skin=r.choice(ZSKIN), eye="#D8E070", top=r.choice(ZTOP), legs=r.choice(["#3A3A44", "#4A4038", "#2E3440"]))
    L["top2"] = L["stripe"] = L["top"]
    return L

class Env:
    def talk(self, who, T): return 0.0

O_DEEP = (0, 600, 0); O_SON = (0, 900, 0)

def wavepat(p, r):
    for y in range(16):
        if y % 5 == 0: p[y, :, :] = np.clip(p[y, :, :]*1.18, 0, 1)
    return p

def build():
    reset((720, 1280))
    W = {}
    # ---------------- playa ----------------
    W["beach"] = g = group("beach")
    B = Batch("beach_b", g, 1.0)
    B.add((0, -110, -0.05), (400, 220, 0.1), tmat("sea", "#2A78A0", 16, 0.10, 21, wavepat))
    B.add((0, 0.6, 0.0), (400, 1.2, 0.06), "#E8F2F4")                                   # espuma
    B.add((0, 16, 0.02), (400, 31, 0.1), tmat("sand", "#E2C990", 16, 0.08, 22))
    B.add((0, 33, 0.6), (400, 4, 1.2), tmat("prom", "#C8C0B0", 16, 0.05, 23, tiles))      # paseo
    B.add((0, 31.1, 1.35), (400, 0.2, 0.3), "#F4F1EA")
    cols = ["#E8D8B8", "#F0E6D0", "#D8C8A8", "#F4EEE2", "#E0C8A8", "#C8D8E0"]
    x = -90; k = 0; W["roofs"] = []
    while x < 90:
        w = random.Random(k).choice([8, 9, 10, 12]); fl = 4+k % 5
        building(B, x+w/2, 40.5, w, 9, fl, cols[k % len(cols)], 400+k, -1)
        W["roofs"].append((x+w/2, fl*1.6+0.4+0.3, w))
        x += w+0.4; k += 1
    for i in range(-14, 15):
        B.add((i*6.0, 34.6, 2.2), (0.3, 0.3, 4.4), "#7A5A3A")                               # palmeras de bloques
        for a in range(5):
            ang = a*2*math.pi/5
            B.add((i*6.0+math.cos(ang)*0.9, 34.6+math.sin(ang)*0.9, 4.4), (1.8, 0.5, 0.18), "#4E9A3A")
    for i in range(-6, 7):                                                                  # sombrillas
        xx = i*11+3; yy = 12+(i % 3)*4
        B.add((xx, yy, 1.1), (0.1, 0.1, 2.2), "#F4F1EA"); B.add((xx, yy, 2.25), (2.4, 2.4, 0.2), ["#E23A2E", "#2E8BD0", "#F2C230"][i % 3])
        B.add((xx+1.2, yy-0.5, 0.12), (1.8, 0.9, 0.06), ["#F4F1EA", "#E8A040", "#40A8C8"][i % 3])
    B.done()
    W["moon"] = box("moon", (-30, -150, 45), (9, 9, 9), mat("#F4F0D8"))
    # regla de nivel del mar (plano del pelo)
    W["ruler"] = g = group("rulerg", (2.0, -0.6, 0))
    B = Batch("ruler_b", g, 1.0)
    B.add((0, 0, 0.4), (0.5, 0.12, 3.4), "#F4F1EA")
    for j in range(17):
        B.add((-0.12 if j % 4 else -0.05, -0.065, -1.2+j*0.2), (0.26 if j % 4 else 0.4, 0.01, 0.025), "#1C1C20")
    B.done()
    W["hair"] = box("hair", (0, 0, 0), (2.4, 0.045, 0.045), mat("#2A1A10"))
    W["waterline"] = box("wline", (0, 0, 0), (8, 6, 0.04), tmat("sea2", "#2A78A0", 16, 0.10, 24, wavepat))
    # ---------------- fondo marino ----------------
    W["deep"] = g = group("deep", O_DEEP)
    B = Batch("deep_b", g, 1.0)
    B.add((0, 0, -0.1), (420, 420, 0.2), tmat("seabed", "#6E7A72", 16, 0.14, 31))
    r = random.Random(9)
    for i in range(140):
        x, y = r.uniform(-120, 120), r.uniform(-60, 160); s = r.uniform(0.6, 3.2)
        B.add((x, y, s*0.4), (s, s*r.uniform(0.7, 1.3), s*0.8), r.choice(["#4E5A56", "#5E6A62", "#3E4A48"]))
    for i in range(70):                                                                       # algas
        x, y = r.uniform(-60, 60), r.uniform(-20, 120); h = r.uniform(1.5, 4)
        B.add((x, y, h/2), (0.25, 0.25, h), "#3E6A4A")
    # profundímetro (columna con marcas)
    for j in range(60):
        B.add((-5.0, 4.0, j*1.0+0.5), (0.6, 0.6, 0.95), "#E8E4DA" if j % 2 else "#D84A30")
    B.done()
    W["horde"] = g = group("hordeg", O_DEEP)
    B = Batch("horde_b", g, 1.0)
    r = random.Random(4)
    for i in range(900):
        x, y = r.uniform(-70, 70), r.uniform(18, 160); c = r.choice(ZTOP); sk = r.choice(ZSKIN)
        B.add((x, y, 0.75), (0.5, 0.3, 0.75), c); B.add((x, y, 1.4), (0.5, 0.5, 0.5), sk)
        B.add((x, y-0.35, 1.05), (0.42, 0.6, 0.16), c)
    B.done()
    W["carpet"] = g = group("carpetg", O_DEEP)
    B = Batch("carpet_b", g, 1.0)
    r = random.Random(6)
    for ix in range(-75, 76):
        for iy in range(0, 110):
            if r.random() < 0.12: continue
            x = ix*1.05+r.uniform(-0.2, 0.2); y = 20+iy*1.05+r.uniform(-0.2, 0.2)
            B.add((x, y, 1.4), (0.5, 0.5, 0.5), r.choice(ZSKIN))
    B.done()
    # lata (presión)
    W["can"] = g = group("can", (0, 0, 0))
    B = Batch("can_b", g, 1.0)
    B.add((0, 0, 0.6), (0.7, 0.7, 1.2), "#D8452E"); B.add((0, 0, 1.22), (0.66, 0.66, 0.06), "#C8CCD2")
    B.add((0, -0.36, 0.6), (0.72, 0.02, 0.3), "#F4F1EA"); B.done()
    # ballena (original, de bloques)
    W["whale"] = g = group("whale")
    B = Batch("whale_b", g, 1.0)
    B.add((0, 0, 0), (14, 4.2, 4.0), "#3A4E66"); B.add((7.6, 0, -0.2), (3.0, 3.6, 3.2), "#3A4E66")
    B.add((2, 0, -1.9), (12, 3.6, 0.6), "#C8D0D8")
    for sy in (-1, 1): B.add((2.5, sy*2.6, -1.2), (2.2, 1.6, 0.4), "#34465C")
    B.add((-8.5, 0, 0.3), (4, 1.4, 1.4), "#3A4E66"); B.add((-11.2, 0, 0.6), (1.6, 6.0, 0.4), "#34465C")
    for sy in (-1, 1): B.add((8.4, sy*1.82, 0.5), (0.4, 0.06, 0.4), "#141218")
    B.done()
    # ---------------- cabina de sonar ----------------
    W["sonar"] = g = group("sonar", O_SON)
    B = Batch("sonar_b", g, 1.0)
    B.add((0, 2.0, 2.5), (14, 0.3, 7), "#3A4048"); B.add((0, 0, -0.1), (14, 10, 0.2), "#4A4E56")
    B.add((0, 1.2, 0.8), (5.0, 1.4, 1.6), "#5A6068")
    B.add((0, 1.75, 3.0), (4.2, 0.4, 3.6), "#2A2E34")
    for i in range(9):
        B.add((-2.0+i*0.5, 0.55, 1.62), (0.25, 0.25, 0.08), ["#E0A030", "#30C060", "#E03030"][i % 3])
    B.done()
    W["screen"] = []
    for i in range(41):
        for j in range(41):
            dx, dy = (i-20)/20, (j-20)/20
            if dx*dx+dy*dy > 1: continue
            W["screen"].append(((i-20)*0.08, (j-20)*0.08))
    S = Batch("screen_b", g, 1.0)
    for (x, z) in W["screen"]: S.add((x, 1.53, 3.0+z), (0.082, 0.02, 0.082), "#0E3A24")
    for rr in (0.55, 1.1, 1.6):
        for a in range(48):
            an = a*2*math.pi/48; S.add((math.cos(an)*rr, 1.52, 3.0+math.sin(an)*rr), (0.05, 0.02, 0.05), "#2E8A54")
    S.done()
    W["sweep"] = box("sweep", (0, 0, 0), (1.6, 0.03, 0.06), mat("#7CFFB0"), g, origin=(-0.8, 0, 0))
    W["dots"] = [box(f"dot{i}", (0, 0, 0), (0.07, 0.03, 0.07), mat("#B8FFD0"), g) for i in range(160)]
    # ---------------- personajes ----------------
    W["bruno"] = Person("bruno", BRUNO)
    W["z"] = [Person(f"z{i}", zlook(i), 0.92+0.14*random.Random(i).random()) for i in range(24)]
    W["npc"] = [Person(f"npc{i}", npc_look(900+i), 0.94+0.12*random.Random(i).random()) for i in range(12)]
    camera(28)
    return W

def hide_all(W):
    for k in ("beach", "deep", "horde", "carpet", "can", "whale", "sonar", "ruler"): show(W[k], False)
    for k in ("moon", "hair", "waterline", "sweep"): hid(W[k], True)
    for d in W["dots"]: hid(d, True)
    for p in [W["bruno"]] + W["z"] + W["npc"]: p.show(False)

def day(W):
    show(W["beach"], True); world_color("#9CC8E8"); light_dir((0.5, -0.45, 0.75)); shadow(0.5)

def night(W):
    show(W["beach"], True); hid(W["moon"], False); world_color("#18203A"); light_dir((0.3, -0.8, 0.5)); shadow(0.7)

def deep(W, dark=0.0):
    show(W["deep"], True)
    c = [int(lerp(a, b, dark)) for a, b in ((0x1E, 0x04), (0x5A, 0x0A), (0x7A, 0x16))]
    world_color("#%02X%02X%02X" % tuple(c)); light_dir((0.1, -0.2, 1.0)); shadow(0.25)

def zpose(p, T, ph, i=0, arms=True):
    p.walk(ph*0.55, 0.6)
    if arms:
        for sx in (-1, 1):
            p.arm(sx, fwd=1.45+0.12*math.sin(T*2+i+sx), side=0.04, elbow=0.12, wrist=-0.2)
    p.head.rotation_euler = (0.2, 0.15*math.sin(T*1.3+i), 0.25*math.sin(T*0.7+i))
    p.chest.rotation_euler = (0.18, 0, 0.08*math.sin(T+i))
    p.face(T, "angry", (0, -0.3), talk=0.35+0.15*math.sin(T*3+i), blink=False)

def zrow(W, T, n, x0, y0, dx, dy, face, ph_speed=1.0, rows=1, ox=0, oy=0, z=0.0, seed=0, start=0):
    for i in range(n):
        p = W["z"][start+i]; r = random.Random(i+seed); p.show(True)
        rr = i % rows; cc = i // rows
        x = x0 + cc*dx + r.uniform(-0.4, 0.4) + ox; y = y0 + rr*dy + r.uniform(-0.5, 0.5) + oy
        p.place(x, y, face + r.uniform(-12, 12), z)
        zpose(p, T, T*ph_speed+r.random(), i)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

# ------------------------------------------------------------------ planos
@shot(0.0, 4.98)
def a1(W, T, M):
    day(W)
    H = W["bruno"]; H.show(True); H.place(1.6, 3.2, 200); H.idle(T)
    up = ease(clamp((T-0.2)/1.4))
    Z = W["z"][0]; Z.show(True); Z.place(0.0, -4.0, 0, lerp(-2.4, -1.15, up))
    Z.arm(1, fwd=2.9, side=0.15, elbow=0.1+0.2*math.sin(T*4)); Z.arm(-1, fwd=0.2, side=0.1, elbow=0.2)
    Z.face(T, "angry", (0, 0.4), talk=0.5, blink=False)
    H.face(T, "shock" if T > 1.3 else "neutral", (-0.3, -0.2))
    if T > 1.3: H.arm(1, fwd=0.6, side=0.3, elbow=1.8); H.arm(-1, fwd=0.6, side=0.3, elbow=1.8)
    # detrás: cabezas que asoman
    for i in range(1, 16):
        if T < 2.6+i*0.08: continue
        p = W["z"][i]; r = random.Random(i); p.show(True)
        k = ease(clamp((T-2.6-i*0.08)/0.9))
        p.place(-14+i*1.9+r.uniform(-0.6, 0.6), -9-r.uniform(0, 9), r.uniform(-15, 15), lerp(-1.9, -0.9, k))
        zpose(p, T, 0, i)
    k = eio(T/4.98)
    look(lerpv((3.6, 8.6, 1.7), (2.2, 6.2, 1.25), k), lerpv((0.0, -4.0, 0.8), (-1.0, -8.0, 0.9), k), lerp(24, 22, k))
    M["grade"] = "day"

@shot(4.98, 10.6)
def a2(W, T, M):
    deep(W, 0.1); show(W["horde"], True); k = T-4.98
    zrow(W, T, 18, -9, 600+10.0 - 1.2*k, 1.9, 2.8, 0, 1.0, rows=3, seed=3)
    for p in W["z"][:18]: p.root.location.y -= 0
    look((10.0, 600+1.0-1.2*k, 1.4), (-1.0, 600+14.0-1.2*k, 1.9), 22)
    M["grade"] = "deep"

@shot(10.6, 15.24)
def a3(W, T, M):
    k = (T-10.6)/4.64; deep(W, lerp(0.35, 0.95, k)); show(W["horde"], True)
    zrow(W, T, 12, -6, 612, 2.2, 2.6, 0, 1.0, rows=2, seed=8)
    look(lerpv((2.0, 600+2.0, 9.0), (1.5, 600+3.5, 1.6), eio(k)), lerpv((0.0, 616, 0.5), (0.0, 616, 1.7), eio(k)), 22)
    M["grade"] = "abyss"; M["dark"] = lerp(0.2, 0.75, k)

@shot(15.24, 19.1)
def a4(W, T, M):
    deep(W, 0.6); k = (T-15.24)/3.86
    Z = W["z"][2]; Z.show(True); Z.place(0, 610-0.8*k, 0); zpose(Z, T, T, 2)
    for i, p in enumerate(W["z"][3:8]):
        p.show(True); p.place(-2.5+i*1.5, 614-0.8*k+i % 2, 0); zpose(p, T, T+i*0.3, i+3)
    look(lerpv((1.4, 607.0, 2.0), (0.9, 607.6, 2.0), eio(k)), (0.0, 610-0.8*k, 1.65), 32, fstop=2.4)
    M["grade"] = "cold"; M["frost"] = 1

@shot(19.1, 25.94)
def a5(W, T, M):
    deep(W, 0.45); k = T-19.1
    # grúa hacia abajo junto al profundímetro (54 → 1)
    cz = lerp(52, 1.8, eio(clamp(k/5.2)))
    can = W["can"]; show(can, True); can.location = (-3.6, 600+4.0, max(0.0, cz-1.6))
    sq = clamp((52-cz)/50); can.scale = (1+0.35*sq, 1+0.35*sq, max(0.18, 1-0.82*sq)); can.rotation_euler = (0, 0, 0.3*sq)
    if k > 5.3:
        can.location.z = 0
        for i, p in enumerate(W["z"][:5]):
            p.show(True); p.place(-1.0+i*1.3, 600+7.0-0.9*(k-5.3)+(i % 2), 0); zpose(p, T, T+i*0.3, i)
    look((1.6, 600-3.5, cz+0.6), (-4.6, 600+4.0, cz-0.3), 24)
    M["grade"] = "deep"

@shot(25.94, 28.0)
def a6(W, T, M):
    deep(W, 0.25); show(W["horde"], True); k = (T-25.94)/2.06
    wh = W["whale"]; show(wh, True); wh.location = (lerp(-26, 6, k), 600+26-6*ease(k), 12+3*ease(k)); wh.rotation_euler = (0, -0.15*ease(k), 0.5*ease(k))
    zrow(W, T, 14, -8, 618, 2.2, 2.6, 0, 1.0, rows=2, seed=11)
    look((-3.0, 600+2.0, 3.0), (0.0, 600+24, 10.0), 20)
    M["grade"] = "deep"

@shot(28.0, 31.56)
def a7(W, T, M):
    world_color("#0E1418"); light_dir((0.2, -0.6, 0.7)); shadow(0.4)
    show(W["sonar"], True); k = T-28.0
    sw = W["sweep"]; hid(sw, False); sw.location = (0, 900+1.5, 3.0); ang = T*2.4; sw.rotation_euler = (0, -ang, 0)
    n = int(lerp(6, 160, eio(clamp(k/3.2))))
    r = random.Random(3)
    for i, d in enumerate(W["dots"]):
        a = r.uniform(0, 2*math.pi); rr = math.sqrt(r.random())*1.45
        if i >= n: continue
        x = math.cos(a)*rr; z = math.sin(a)*rr - 0.12*k
        if x*x+z*z > 2.1: continue
        hid(d, False); d.location = (x, 900+1.5, 3.0+z)
        d.scale = (1.3, 1, 1.3) if (ang+a) % (2*math.pi) < 0.6 else (1, 1, 1)
    H = W["bruno"]; H.show(True); H.place(1.9, 900-1.0, 200); H.idle(T); H.face(T, "shock", (-0.6, 0.2))
    look(lerpv((1.2, 900-5.2, 2.9), (0.6, 900-3.6, 3.0), eio(k/3.56)), (0.0, 900+1.5, 3.0), 26, fstop=4.0)
    M["grade"] = "sonar"

@shot(31.56, 37.16)
def a8(W, T, M):
    deep(W, 0.3); show(W["carpet"], True); k = (T-31.56)/5.6
    zrow(W, T, 10, -5, 600+22, 1.05, 1.05, 180, 1.0, rows=2, seed=13)
    h = lerp(6, 120, eio(k))
    look((0.0, 600+lerp(16, 30, eio(k)), h), (0.0, 600+lerp(30, 70, eio(k)), 0.0), lerp(22, 18, k))
    M["grade"] = "deep"; M["chip"] = 1

@shot(37.16, 41.28)
def a9(W, T, M):
    night(W); k = T-37.16
    pop = 39.95
    for i in range(24):
        p = W["z"][i]; r = random.Random(i+30)
        tt = clamp((T-pop-r.random()*0.25)/0.35)
        if tt <= 0: continue
        p.show(True); p.place(-16+i*1.4+r.uniform(-0.3, 0.3), -2.5-r.uniform(0, 7), r.uniform(-10, 10), lerp(-1.9, -0.75, ease(tt)))
        zpose(p, T, 0, i, arms=False); p.face(T, "angry", (0, 0.2), talk=0.2, blink=False)
    sx, sy, sz = shake(T, 0.03 if T > pop else 0)
    look(lerpv((0.0, 9.0, 1.4), (0.0, 7.2, 1.2), eio(k/4.1)) if True else None, (0.0, -6.0, 0.6), 24)
    W_ = bpy.context.scene.camera.location; W_.x += sx; W_.y += sy; W_.z += sz
    M["grade"] = "night"
    if pop < T < pop+0.12: M["flash"] = 1

@shot(41.28, 45.46)
def a10(W, T, M):
    day(W); world_color("#E8B890"); light_dir((-0.6, -0.5, 0.35)); shadow(0.6)
    k = T-41.28; part = 0 if k < 1.4 else (1 if k < 2.8 else 2)
    zrow(W, T, 24, -8, -6.0+1.4*k, 1.4, 2.0, 180, 1.0, rows=3, seed=17+part)
    for p in W["z"]:
        if p.root.location.y < -1.5: p.root.location.z = max(-1.0, (p.root.location.y+1.5)*0.35)
    cams = [((6, 9, 2.2), (-1, -3, 1.0), 24), ((-4, 5.5, 1.0), (1, -4, 1.6), 22), ((0, 22, 12), (-1, -3, 0), 22)]
    (cp, tg, ln) = cams[part]; kk = (k - part*1.4)/1.4
    look((cp[0]+kk*1.5, cp[1]-kk*1.0, cp[2]), tg, ln)
    M["grade"] = "dawn"

@shot(45.46, 47.78)
def a11(W, T, M):
    day(W); k = T-45.46
    for i, p in enumerate(W["npc"]):
        r = random.Random(i+70); p.show(True)
        yy = 24+k*3.6+r.uniform(-2, 2)
        p.place(-9+i*1.6+r.uniform(-0.3, 0.3), yy, 180+r.uniform(-15, 15), 0.05 if yy < 31 else 1.2)
        p.walk(T*1.7+r.random(), 1.0, run=True); p.face(T, "scared", (0, 0.3))
        if i % 3 == 0: p.arm(1, fwd=2.7, side=0.2, elbow=0.3)
    H = W["bruno"]; H.show(True); H.place(1.0, 22+k*3.6, 180); H.walk(T*1.8, 1, run=True); H.face(T, "scared", (0, 0.2))
    zrow(W, T, 12, -10, 9+k*0.8, 1.8, 2.2, 0, 1.0, rows=2, seed=21)
    look((6.0, 33+1.0*k, 6.5), (0.0, 18+3.0*k, 0.8), 20)
    M["grade"] = "alarm"; M["alarm"] = 1

ROOF = None
def roof_of(W):
    best = min(W["roofs"], key=lambda r: abs(r[0]-0.5))
    return best

@shot(47.78, 50.22)
def a12(W, T, M):
    day(W); k = T-47.78
    rx, rz, rw = roof_of(W)
    H = W["bruno"]; H.show(True); H.place(rx, 37.6, 0, rz); H.idle(T); H.face(T, "worried", (0.2, -0.5))
    H.arm(1, fwd=0.4, side=0.2, elbow=2.2); H.fingers(1, 0.3, 1.0)
    look(lerpv((rx-2.2, 33.6, rz+1.9), (rx-1.8, 34.4, rz+1.6), eio(k/2.44)), (rx, 37.6, rz+1.25), 30, fstop=3.0)
    M["grade"] = "day"

@shot(50.22, 56.94)
def a13(W, T, M):
    day(W); k = T-50.22
    show(W["ruler"], True); hid(W["waterline"], False)
    wl = W["waterline"]; wl.location = (2.0, -0.6, 0.0 - 0.0000002*clamp(k/3))
    hd = W["hair"]; hid(hd, k < 2.6); hd.location = (2.0, -0.72, 0.07)
    hd.rotation_euler = (0, 0.05*math.sin(T*2), 0)
    if k < 2.6:
        look(lerpv((2.7, -3.6, 0.45), (2.5, -3.0, 0.35), eio(k/2.6)), (2.0, -0.6, 0.25), 30)
    else:
        kk = eio((k-2.6)/4.1)
        look(lerpv((2.2, -1.9, 0.12), (2.1, -1.55, 0.08), kk), (2.0, -0.66, 0.03), lerp(40, 50, kk), fstop=3.5)
    M["grade"] = "day"; M["chip"] = 1

@shot(56.94, TOTAL+0.1)
def a14(W, T, M):
    day(W); k = T-56.94
    rx, rz, rw = roof_of(W)
    H = W["bruno"]; H.show(True); H.place(rx, 37.4, -15, rz); H.idle(T)
    H.face(T, "smirk" if k > 1.6 else "worried", (0, 0.2))
    if k > 1.6: H.arm(1, fwd=0.3, side=0.9, elbow=1.8)
    zrow(W, T, 24, rx-12, 22+0.6*k, 1.4, 2.0, 180, 0.6, rows=3, seed=25)
    for p in W["z"]:
        p.root.location.z = 0.05 if p.root.location.y < 31 else 1.2
    look(lerpv((rx-1.6, 33.6, rz+1.7), (rx-1.0, 34.8, rz+1.5), eio(k/5.7)), (rx, 37.4, rz+1.2), 28)
    M["grade"] = "day"; M["fade"] = clamp((T-62.2)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    cam = bpy.context.scene.camera.location
    for p in W["z"] + W["npc"]:
        if DES.get(p.root.name, (None, True))[1]: continue
        l = p.root.location
        if math.hypot(l.x-cam.x, l.y-cam.y) < 1.2 and abs(l.z-cam.z) < 3:
            p.show(False)
    apply_vis()
    return M
