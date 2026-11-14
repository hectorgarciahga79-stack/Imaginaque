"""Q14 · «¿Y si cada hora fueras 10 veces más pequeño?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral). Tiempos de plano = timeline de align.py (58,35 s).
El protagonista mantiene su tamaño en cámara y el mundo crece a su alrededor: cuarto (origen), suelo con gato gigante (y=200),
baldosas con hormiga (y=400), borde de la mesa (y=600), polvo con ácaro y pelo (y=800), sangre con glóbulos y bacterias (y=1000),
onda de luz (y=1200), ADN y átomo (y=1400). Protagonista original: Hugo (sudadera azul)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person
from world import Batch, tmat, tiles, planks, brick, stripes

FPS = 24
TOTAL = 58.35
HUGO = dict(skin="#F0C8A0", hair="#C8782A", hair2="#A85E1E", eye="#2A4A6A", top="#2E6EC8", top2="#2456A0", stripe="#F4F1EA",
            legs="#3A3A44", legs2="#2C2C34", shoe="#C0302A", shoe2="#F4F1EA", watch=False, hstyle="short")

class Env:
    def talk(self, who, T): return 0.0

O = {k: (0, 200*i, 0) for i, k in enumerate(("room", "cat", "ant", "table", "dust", "blood", "light", "dna"))}

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(14)
    # ---------------- cuarto (tamaño normal) ----------------
    W["room"] = g = group("room", O["room"])
    B = Batch("room_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("floor", "#A87A50", 16, 0.07, 81, planks))
    B.add((0, 3.2, 1.6), (14, 0.2, 3.2), tmat("wall", "#6AA88A", 16, 0.04, 82))
    B.add((-2.4, 1.9, 0.25), (2.0, 2.4, 0.5), "#6A4A30"); B.add((-2.4, 1.9, 0.6), (1.9, 2.3, 0.2), "#F4F1EA")
    B.add((1.8, 3.08, 1.9), (1.6, 0.06, 1.2), "#9FD0E8")
    B.done()
    W["poof"] = [box(f"pf{q}", (0, 0, 0), (0.15, 0.15, 0.15), mat("#FFFFFF")) for q in range(16)]
    # ---------------- suelo gigante + gato ----------------
    W["catset"] = g = group("catset", O["cat"])
    B = Batch("cat_b", g, 1.0)
    B.add((0, 0, -0.05), (300, 300, 0.1), tmat("floorbig", "#A87A50", 16, 0.07, 83, planks))
    B.add((-14, 18, 3), (8, 6, 6), "#6A4A30")
    B.done()
    W["cat"] = ct = group("cat", (O["cat"][0]+1.0, O["cat"][1]+9.0, 0))
    C = Batch("catb", ct, 1.0); F = tmat("fur", "#E8A050", 16, 0.12, 84, stripes)
    C.add((0, 4, 4.5), (6, 9, 5), F)                       # cuerpo
    C.add((0, -1.5, 7.5), (6.5, 5.5, 5.5), F)              # cabeza
    for sx in (-1, 1):
        C.add((sx*2.2, -1.5, 11.0), (1.6, 1.4, 1.8), F)    # orejas
        C.add((sx*1.5, -4.26, 8.3), (1.3, 0.05, 1.5), "#F4F1EA"); C.add((sx*1.5, -4.3, 8.2), (0.45, 0.05, 1.2), "#141216")
        for y in (0.5, 7.5): C.add((sx*2.0, y, 1.0), (1.6, 1.6, 2.0), F)
        for k in range(3): C.add((sx*(2.4+k*0.3), -4.3, 6.6+k*0.3-0.3), (1.8, 0.05, 0.1), "#F4F1EA")
    C.add((0, -4.3, 6.9), (0.8, 0.1, 0.6), "#E07A8A"); C.add((0, 9, 7.5), (1.2, 1.2, 6), F)
    C.done()
    # ---------------- baldosas + hormiga ----------------
    W["antset"] = g = group("antset", O["ant"])
    B = Batch("ant_b", g, 1.0)
    B.add((0, 0, -0.05), (300, 300, 0.1), tmat("tilebig", "#D8D0C0", 16, 0.05, 85, tiles))
    for q in range(12): B.add((r.uniform(-12, 12), r.uniform(4, 30), 0.15), (0.8, 0.8, 0.3), "#E8D8A0")   # migas
    B.done()
    W["ant"] = an = group("ant", (O["ant"][0]+1.8, O["ant"][1]+3.0, 0))
    A = Batch("antb", an, 1.0)
    A.add((0, 0, 1.4), (1.4, 1.2, 1.2), "#3A1C14"); A.add((0, 1.4, 1.2), (1.0, 1.2, 0.9), "#4A2418"); A.add((0, 3.2, 1.6), (2.2, 2.6, 2.0), "#3A1C14")
    A.add((0, -1.2, 1.8), (1.4, 1.2, 1.2), "#4A2418")
    for sx in (-1, 1):
        A.add((sx*0.35, -1.86, 1.9), (0.3, 0.05, 0.3), "#141216")
        A.add((sx*0.4, -2.2, 2.7), (0.12, 0.12, 1.6), "#2A1410")
        for y in (0.2, 1.3, 2.2):
            A.add((sx*1.2, y, 1.2), (1.4, 0.15, 0.15), "#2A1410"); A.add((sx*1.9, y, 0.6), (0.15, 0.15, 1.2), "#2A1410")
    A.done()
    # ---------------- borde de la mesa ----------------
    W["tableset"] = g = group("tableset", O["table"])
    B = Batch("tb_b", g, 1.0)
    B.add((0, 0, -0.05), (400, 400, 0.1), tmat("floorbig2", "#A87A50", 16, 0.07, 86, planks))
    B.add((0, 30, 40), (80, 60, 4), tmat("tabletop", "#8A5A36", 16, 0.06, 87, planks))
    B.add((-30, 50, 19), (4, 4, 38), "#6A4A30")
    B.done()
    # ---------------- polvo: ácaro + pelo ----------------
    W["dustset"] = g = group("dustset", O["dust"])
    B = Batch("du_b", g, 1.0)
    B.add((0, 0, -0.05), (300, 300, 0.1), tmat("fiber", "#B8A890", 16, 0.18, 88))
    for q in range(40): B.add((r.uniform(-20, 20), r.uniform(-4, 30), r.uniform(0.1, 0.6)), (r.uniform(0.3, 1.2),)*3, "#C8BCA8")
    B.add((0, 2.5, 0.9), (60, 1.8, 1.8), tmat("hair", "#3A2414", 16, 0.10, 89, stripes))       # pelo tumbado
    B.done()
    W["mite"] = mt = group("mite", (O["dust"][0]-2.4, O["dust"][1]+6.0, 0))
    Mb = Batch("miteb", mt, 1.0)
    Mb.add((0, 0, 2.2), (3.0, 3.8, 2.6), tmat("mitet", "#D8A878", 8, 0.12, 92)); Mb.add((0, -2.2, 2.0), (1.2, 0.8, 0.8), "#8A5A3A")
    for sx in (-1, 1): Mb.add((sx*0.3, -2.62, 2.15), (0.2, 0.05, 0.2), "#141216")
    for sx in (-1, 1):
        for y in (-1.4, -0.5, 0.5, 1.4):
            Mb.add((sx*2.0, y, 1.6), (1.4, 0.25, 0.25), "#6A4A2A"); Mb.add((sx*2.6, y, 0.8), (0.25, 0.25, 1.6), "#6A4A2A")
        for k in range(4): Mb.add((sx*0.8, -0.8+k*0.6, 3.6), (0.1, 0.1, 0.8), "#B89878")
    Mb.done()
    # ---------------- sangre ----------------
    W["bloodset"] = g = group("bloodset", O["blood"])
    W["world_blood"] = None
    W["rbc"] = [(box(f"rbc{q}", (0, 0, 0), (0.85, 0.85, 0.28), tmat("rbct", "#C8302A", 8, 0.10, 90)), r.uniform(-1, 1), r.uniform(0, 1), r.uniform(-1, 1)) for q in range(26)]
    W["bact"] = [(box(f"bac{q}", (0, 0, 0), (0.9, 2.0, 0.9), tmat("bact", "#7AC850", 8, 0.12, 91)), r.uniform(-1, 1), r.uniform(0, 1), r.uniform(-1, 1)) for q in range(10)]
    # ---------------- onda de luz ----------------
    W["wave"] = [box(f"wv{q}", (0, 0, 0), (0.35, 0.35, 0.35), mat(["#C040FF", "#5080FF", "#40D0FF", "#50FF80", "#FFE040", "#FF8030", "#FF3040"][q % 7])) for q in range(70)]
    # ---------------- ADN + átomo ----------------
    W["dna"] = [box(f"dn{q}", (0, 0, 0), (0.5, 0.5, 0.5), mat("#40A0FF" if q % 2 else "#FF6080")) for q in range(48)]
    W["rungs"] = [box(f"rg{q}", (0, 0, 0), (1.0, 0.15, 0.15), mat(["#FFD040", "#60E080"][q % 2])) for q in range(24)]
    W["nucleus"] = [box(f"nu{q}", (0, 0, 0), (0.22, 0.22, 0.22), mat("#FF5040" if q % 2 else "#A0A0B0")) for q in range(14)]
    W["elec"] = [box(f"el{q}", (0, 0, 0), (0.14, 0.14, 0.14), mat("#60E0FF")) for q in range(3)]
    W["atoms"] = [box(f"at{q}", (0, 0, 0), (0.06, 0.06, 0.06), mat(["#60E0FF", "#FF6080", "#FFD040", "#F4F1EA"][q % 4])) for q in range(180)]
    W["hugo"] = Person("hugo", HUGO)
    camera(28)
    return W

def hide_all(W):
    for k in ("room", "catset", "cat", "antset", "ant", "tableset", "dustset", "mite"): show(W[k], False)
    for lst in ("rbc", "bact"):
        for it in W[lst]: hid(it[0], True)
    for o in W["poof"] + W["wave"] + W["dna"] + W["rungs"] + W["nucleus"] + W["elec"] + W["atoms"]: hid(o, True)
    W["hugo"].show(False); W["hugo"].root.scale = (1, 1, 1)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def hugo(W, o, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    H = W["hugo"]; H.show(True); H.place(o[0]+x, o[1]+y, face, z); H.idle(T); H.face(T, expr, look_)
    return H

def poof(W, c, T, t0):
    f = clamp((T-t0)/0.5)
    if 0 < f < 1:
        for q, p in enumerate(W["poof"]):
            a = q*2*math.pi/16; hid(p, False); s = (1-f)*1.2
            p.scale = (s, s, s); p.location = (c[0]+math.cos(a)*0.6*f*2, c[1]+math.sin(a)*0.3*f, c[2]+0.5+math.sin(a*3)*0.4*f)

# ------------------------------------------------------------------ planos
@shot(0.0, 3.4)
def w1(W, T, M):
    o = O["room"]; show(W["room"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    k = T/3.4
    s = lerp(1.0, 0.1, eio(clamp((T-1.6)/1.0)))
    H = hugo(W, o, 0.2, 0.6, 0, T, "shock" if T > 1.4 else "neutral", (0, 0.2*(1-s)))
    H.root.scale = (s, s, s)
    if T > 1.4: H.arm(-1, fwd=1.6, side=0.3, elbow=0.3); H.arm(1, fwd=1.6, side=0.3, elbow=0.3)
    poof(W, (o[0]+0.2, o[1]+0.6, 0.0), T, 1.6)
    cz = lerp(1.5, 0.35, eio(clamp((T-1.6)/1.2)))
    look((o[0]+0.5, o[1]-lerp(3.6, 1.6, eio(clamp((T-1.6)/1.2))), cz+0.2), (o[0]+0.2, o[1]+0.6, cz), lerp(26, 30, k))
    if 1.62 < T < 1.7: M["flash"] = 1
    M["grade"] = "dawn"

@shot(3.4, 8.62)
def w2(W, T, M):
    o = O["cat"]; show(W["catset"], True); show(W["cat"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    k = (T-3.4)/5.22
    W["cat"].location = (o[0]+1.0, o[1]+lerp(12.0, 8.0, eio(clamp((T-5.8)/1.5))), 0)
    H = hugo(W, o, -0.3, 0.0, 200, T, "shock" if T > 6.2 else "neutral", (0.2, 0.8))
    look(lerpv((o[0]+1.2, o[1]-5.6, 1.0), (o[0]+1.0, o[1]-4.8, 1.3), eio(k)), (o[0]+0.4, o[1]+4.0, lerp(3.0, 4.6, k)), lerp(20, 18, k))
    M["grade"] = "dawn"

@shot(8.62, 13.98)
def w3(W, T, M):
    o = O["ant"]; show(W["antset"], True); show(W["ant"], True); world_color("#E8E0D0"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
    k = (T-8.62)/5.36
    wk = clamp((T-9.0)/3.0)
    W["ant"].location = (o[0]+1.8, o[1]+lerp(7.0, 2.6, eio(wk)), 0.05*abs(math.sin(T*12)))
    W["ant"].rotation_euler = (0, 0, 0.1*math.sin(T*3))
    H = hugo(W, o, -0.9, -0.4, -30, T, "scared" if T > 11.7 else "worried", (0.5, 0.5))
    if T > 11.7: H.arm(1, fwd=1.4, side=0.2, elbow=0.4)
    look(lerpv((o[0]-3.5, o[1]-6.5, 1.3), (o[0]-2.8, o[1]-5.2, 1.6), eio(k)), (o[0]+0.4, o[1]+1.5, 1.6), 22)
    M["grade"] = "day"

@shot(13.98, 19.6)
def w4(W, T, M):
    o = O["table"]; show(W["tableset"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    jump = 16.3
    H = W["hugo"]; H.show(True); H.idle(T)
    if T < jump:
        H.place(o[0], o[1]+0.6, 0, 42.0); H.face(T, "smirk", (0, -0.3))
        look((o[0]+3.0, o[1]-6.5, 42.6), (o[0], o[1]+0.8, 42.3), 24)
    else:
        f = T-jump
        z = max(0.0, 42.0 - 14.0*f) if T < 19.1 else 0.0
        H.place(o[0], o[1]-0.5-0.4*f, 0, z)
        for sx in (-1, 1): H.arm(sx, fwd=0.4, side=2.4, elbow=0.2); H.leg(sx, 0.3, 0.4)
        H.face(T, "happy" if z > 0 else "smirk", (0, 0))
        if z <= 0.0:
            H.idle(T)
            for sx in (-1, 1): H.arm(sx, fwd=0.1, side=1.4, elbow=2.0)
        look((o[0]+3.0, o[1]-7.5, z+1.6), (o[0], o[1]-0.5, z+0.9), 24)
    M["grade"] = "dawn"

@shot(19.6, 26.2)
def w5(W, T, M):
    o = O["dust"]; show(W["dustset"], True); show(W["mite"], True); world_color("#D8C8B0"); light_dir((0.45, -0.55, 0.7)); shadow(0.45)
    k = (T-19.6)/6.6
    W["mite"].location = (o[0]-2.4+0.3*math.sin(T*1.3), o[1]+6.0-1.2*eio(clamp((T-19.8)/2.5)), 0)
    H = hugo(W, o, 0.8, -0.6, -15, T, "scared" if T < 23.5 else "shock", (-0.5, 0.6))
    if T < 23.5:
        look(lerpv((o[0]+4.0, o[1]-7.5, 1.6), (o[0]+3.2, o[1]-6.5, 2.0), eio(clamp((T-19.6)/3.9))), (o[0]-0.6, o[1]+3.0, 2.0), 22)
    else:
        look(lerpv((o[0]+5.0, o[1]-4.0, 1.0), (o[0]+4.0, o[1]-3.4, 1.4), eio(clamp((T-23.5)/2.7))), (o[0]+0.5, o[1]+1.5, 1.1), 24)
    M["grade"] = "day_sad"

def stream(W, key, T, o, n, spread=(5, 14, 3.5), speed=1.6):
    for q, (b, a, ph, c) in enumerate(W[key][:n]):
        y = (ph*spread[1] + T*speed) % spread[1] - spread[1]*0.35
        hid(b, False); b.location = (o[0]+a*spread[0], o[1]+y, 1.0+c*spread[2]*0.5+spread[2]*0.5)
        b.rotation_euler = (T*0.7+q, T*0.5+q*2, 0)

@shot(26.2, 34.54)
def w6(W, T, M):
    o = O["blood"]; k = (T-26.2)/8.34
    bact = T > 31.0
    world_color("#5A1418" if not bact else "#1C2A1C"); light_dir((0.4, -0.5, 0.75)); shadow(0.3)
    if not bact: stream(W, "rbc", T, o, 26)
    else: stream(W, "bact", T, o, 10, (5, 16, 3.5), 1.0)
    H = hugo(W, o, 0.0, 0.0, 0, T, "worried" if not bact else "shock", (0.5*math.sin(T), 0.2), z=1.6)
    for sx in (-1, 1): H.arm(sx, fwd=0.6+0.3*math.sin(T*3+sx), side=0.9, elbow=0.4); H.leg(sx, 0.3*math.sin(T*3+sx), 0.4)
    a = -0.4+0.8*eio(k)
    look((o[0]+math.sin(a)*6.0, o[1]-math.cos(a)*6.0, 2.6), (o[0], o[1], 2.4), 26)
    M["grade"] = "alarm" if not bact else "lab"

@shot(34.54, 44.14)
def w7(W, T, M):
    o = O["light"]; k = (T-34.54)/9.6
    dark = clamp((T-42.6)/1.2)
    world_color(lerpv(hexc("#141830"), hexc("#000000"), dark)); light_dir((0.4, -0.5, 0.75)); shadow(0.3)
    lam = 4.5   # 380–700 nm frente a 175 nm → onda 2–4 veces su altura
    for q, b in enumerate(W["wave"]):
        x = -14 + q*0.4 - ((T*3.0) % lam)
        hid(b, dark > 0.6); b.location = (o[0]+x, o[1]+2.0, 2.0+1.6*math.sin(2*math.pi*x/lam))
    H = hugo(W, o, 0.0, 0.0, 0, T, "shock" if T < 42.0 else "scared", (0.3*math.sin(T*2), 0.3))
    if dark > 0.9: H.show(False)
    look(lerpv((o[0]+1.2, o[1]-8.0, 1.6), (o[0]+0.4, o[1]-6.0, 1.5), eio(k)), (o[0], o[1]+1.0, 1.6), 24)
    M["grade"] = "night"
    if dark: M["fade"] = dark*0.92

@shot(44.14, 50.2)
def w8(W, T, M):
    o = O["dna"]; world_color("#0A0E1C"); light_dir((0.4, -0.5, 0.75)); shadow(0.3)
    atom = T > 47.3
    if not atom:
        for q, b in enumerate(W["dna"]):
            i = q//2; sx = 1 if q % 2 else -1
            z = -2.0+i*0.5; a = i*0.55+T*0.8
            hid(b, False); b.location = (o[0]+sx*1.0*math.cos(a), o[1]+2.0+sx*1.0*math.sin(a), z+1.0)
        for i, rg in enumerate(W["rungs"]):
            a = i*0.55+T*0.8; hid(rg, False)
            rg.location = (o[0], o[1]+2.0, -2.0+i*0.5+1.0); rg.rotation_euler = (0, 0, a); rg.scale = (1.8, 1, 1)
        H = hugo(W, o, -1.6, 0.5, 20, T, "shock", (0.6, 0.6))
        look((o[0]+0.0, o[1]-9.0, 3.0), (o[0]-0.3, o[1]+1.5, 3.2), 24)
    else:
        for q, b in enumerate(W["nucleus"]):
            u = Vector((math.sin(q*2.4), math.cos(q*1.7), math.sin(q*3.1))).normalized()*0.18
            hid(b, False); b.location = (o[0]+1.2+u.x, o[1]+u.y, 1.0+u.z)
        for q, e in enumerate(W["elec"]):
            a = T*5+q*2.1; hid(e, False)
            e.location = (o[0]+1.2+0.8*math.cos(a), o[1]+0.8*math.sin(a)*math.cos(q), 1.0+0.8*math.sin(a)*math.sin(q+0.5))
        H = hugo(W, o, -0.4, 0.0, 30, T, "worried", (0.8, 0.0))
        look((o[0]+0.6, o[1]-5.0, 1.3), (o[0]+0.5, o[1]+0.2, 1.0), 26)
    M["grade"] = "night"

@shot(50.2, 55.4)
def w9(W, T, M):
    o = O["dna"]; world_color("#0A0E1C"); light_dir((0.4, -0.5, 0.75)); shadow(0.3)
    f = eio(clamp((T-51.0)/3.0))
    H = hugo(W, o, 0.0, 0.0, 0, T, "shock", (0, 0.4))
    s = 1.0-0.85*f; H.root.scale = (s, s, s)
    rr = random.Random(5)
    for q, a in enumerate(W["atoms"]):
        p = Vector((rr.uniform(-0.3, 0.3), rr.uniform(-0.15, 0.15), rr.uniform(0.1, 1.9)))
        d = Vector((rr.gauss(0, 1), rr.gauss(0, 1), rr.gauss(0, 1))).normalized()
        hid(a, f < 0.02); a.location = (o[0]+p.x+d.x*3.5*f, o[1]+p.y+d.y*3.5*f, p.z+d.z*2.5*f)
    look((o[0]+0.4, o[1]-4.6, 1.3), (o[0], o[1], 1.1), 26)
    M["grade"] = "night"

@shot(55.4, TOTAL+0.1)
def w10(W, T, M):
    o = O["room"]; show(W["room"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    k = (T-55.4)/2.95
    H = hugo(W, o, 0.2, 0.6, 0, T, "smirk", (0, 0.1))
    H.arm(1, fwd=1.2, side=0.1, elbow=1.4); H.fingers(1, 0.6, 0.2)
    look(lerpv((o[0]+0.4, o[1]-2.8, 1.65), (o[0]+0.3, o[1]-2.0, 1.62), eio(k)), (o[0]+0.2, o[1]+0.6, 1.5), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-57.9)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
