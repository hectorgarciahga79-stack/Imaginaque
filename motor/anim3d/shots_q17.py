"""Q17 · «¿Y si nacieras con un millón de euros pero perdieras 1.000 € cada minuto?» (3D de bloques, formato B).
Voz única del narrador (Juanjo Viral). Tiempos de plano = timeline de align.py (49,39 s).
Decorados propios: habitación de hospital con cuna y contador gigante (origen), puerta del hospital (y=200), cocina con biberón (y=400),
salón con tarta de cumpleaños (y=600), «carretera de sueldos» (y=800), gráfica del interés (y=1000).
Protagonista original: Nil (bebé con pijama verde menta; de mayor, sudadera menta)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person
from world import Batch, tmat, tiles, planks, brick, asphalt, stripes, text3d, building, tree

FPS = 24
TOTAL = 49.39
NIL = dict(skin="#F2CCA8", hair="#8A5A2A", hair2="#6A4420", eye="#2A4A6A", top="#7ED8B8", top2="#5AB898", stripe="#F4F1EA",
           legs="#7ED8B8", legs2="#5AB898", shoe="#F4F1EA", shoe2="#F4F1EA", watch=False, hstyle="short")
GOLD = "#F2C230"; RED = "#E0302A"

class Env:
    def talk(self, who, T): return 0.0

O_H = (0, 0, 0); O_D = (0, 200, 0); O_K = (0, 400, 0); O_B = (0, 600, 0); O_R = (0, 800, 0); O_I = (0, 1000, 0)

def fmt(n):
    s = f"{abs(int(n)):,}".replace(",", ".") + " €"
    return ("-" if n < 0 else "") + s

def money(min_):
    return 1_000_000 - 1000*min_

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(17)
    # ---------------- hospital ----------------
    W["hosp"] = g = group("hosp", O_H)
    B = Batch("hp_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("hfl", "#D8E0E0", 16, 0.04, 131, tiles))
    B.add((0, 3.2, 1.6), (14, 0.2, 3.2), tmat("hwall", "#B8D8E8", 16, 0.03, 132))
    B.add((0, 1.2, 0.45), (1.6, 1.0, 0.1), "#F4F1EA")
    for x in (-0.78, 0.78):
        for y in (0.72, 1.68): B.add((x, y, 0.25), (0.08, 0.08, 0.5), "#C8C8D0")
    for x in range(-7, 8): B.add((x*0.2, 0.7, 0.8), (0.04, 0.04, 0.6), "#C8C8D0")
    B.add((0, 0.7, 1.1), (1.6, 0.06, 0.06), "#C8C8D0"); B.add((0, 1.7, 0.9), (1.6, 0.06, 0.9), "#C8C8D0")
    B.add((0, 1.2, 0.55), (1.5, 0.9, 0.12), "#F4F8FC")
    B.add((2.6, 3.05, 1.8), (1.4, 0.1, 1.0), "#9FD0E8")
    B.done()
    W["counter"] = text3d("counter", fmt(1_000_000), (0, 3.05, 2.35), 0.42, GOLD, None, extrude=0.05)
    W["clock"] = text3d("clockt", "0 H 0 MIN", (0, 3.05, 1.85), 0.22, "#2A2A2E", None, extrude=0.02)
    W["pile"] = box("pile", (0.9, 1.2, 0.62), (0.5, 0.5, 1.0), tmat("bills", "#5AA860", 16, 0.12, 133, stripes), origin=(0, 0, -0.5))
    # ---------------- puerta del hospital ----------------
    W["door"] = g = group("door", O_D)
    B = Batch("dr_b", g, 1.0)
    B.add((0, 0, -0.06), (200, 200, 0.1), tmat("grassd", "#5A9A44", 16, 0.10, 134))
    B.add((0, -2, 0.0), (200, 5, 0.06), tmat("roadd", "#4A4A50", 16, 0.05, 135, asphalt))
    B.add((0, 6, 4), (14, 6, 8), tmat("hospb", "#F0F0F4", 16, 0.04, 136, tiles)); B.add((0, 2.95, 1.2), (2.4, 0.1, 2.4), "#9FD0E8")
    B.add((0, 2.9, 6.5), (3.0, 0.1, 1.0), "#E0302A"); B.add((0, 2.85, 6.5), (0.3, 0.05, 0.8), "#F4F1EA"); B.add((0, 2.85, 6.5), (0.8, 0.05, 0.3), "#F4F1EA")
    B.done()
    W["pram"] = pm = group("pram", (0, 0, 0))
    P = Batch("pram_b", pm, 1.0)
    P.add((0, 0, 0.6), (0.6, 1.0, 0.4), "#5A6AB8"); P.add((0, 0.35, 0.9), (0.62, 0.35, 0.5), "#4A5AA8")
    for x in (-0.3, 0.3):
        for y in (-0.35, 0.35): P.add((x, y, 0.15), (0.06, 0.3, 0.3), "#2A2A2E")
    P.add((0, -0.75, 1.0), (0.6, 0.06, 0.06), "#2A2A2E"); P.add((0, -0.6, 0.8), (0.05, 0.3, 0.5), "#2A2A2E")
    P.done()
    W["counter2"] = text3d("counter2", "", (0, 0, 0), 0.5, GOLD, None, extrude=0.05)
    # ---------------- cocina + biberón ----------------
    W["kitchen"] = g = group("kitchen", O_K)
    B = Batch("kt_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("kfl", "#E8D8B8", 16, 0.05, 137, tiles)); B.add((0, 3.2, 1.6), (14, 0.2, 3.2), tmat("kwall", "#F0E0A0", 16, 0.04, 138, tiles))
    B.add((0, 1.2, 0.5), (3.0, 1.2, 1.0), "#C8A878"); B.add((0, 1.2, 1.03), (3.1, 1.25, 0.06), "#F4F1EA")
    B.done()
    W["bottle"] = bt = group("bottle", (O_K[0]+0.2, O_K[1]+1.0, 1.06))
    Bb = Batch("bot_b", bt, 1.0)
    Bb.add((0, 0, 0.25), (0.24, 0.24, 0.5), "#F4F8FC"); Bb.add((0, 0, 0.2), (0.22, 0.22, 0.36), "#FFFFFF"); Bb.add((0, 0, 0.53), (0.26, 0.26, 0.08), "#7ED8B8"); Bb.add((0, 0, 0.62), (0.1, 0.1, 0.12), "#E8C898")
    Bb.done()
    W["tag"] = box("tag", (O_K[0]+0.75, O_K[1]+0.95, 1.55), (0.9, 0.04, 0.4), mat("#F4F1EA"))
    W["price"] = text3d("price", "440.000 €", (O_K[0]+0.75, O_K[1]+0.92, 1.47), 0.17, RED, None, extrude=0.02)
    # ---------------- cumpleaños ----------------
    W["bday"] = g = group("bday", O_B)
    B = Batch("bd_b", g, 1.0)
    B.add((0, 0, -0.05), (14, 12, 0.1), tmat("bfl", "#A87A50", 16, 0.07, 139, planks)); B.add((0, 3.2, 1.6), (14, 0.2, 3.2), tmat("bwall", "#E8A0B8", 16, 0.04, 140))
    B.add((0, 1.0, 0.4), (1.6, 1.0, 0.8), "#8A5A36")
    B.add((0, 1.0, 0.95), (0.7, 0.7, 0.3), "#F4E0C0"); B.add((0, 1.0, 1.12), (0.72, 0.72, 0.05), "#E86A8A")
    B.add((0, 1.0, 1.3), (0.05, 0.05, 0.3), "#7AB8F0")
    for k in range(8): B.add((-3+k*0.85, 3.08, 2.6-0.2*(k % 2)), (0.3, 0.05, 0.4), ["#E86A4A", "#F2C230", "#5AB898", "#7A8AE8"][k % 4])
    B.done()
    W["flame"] = box("flame", (O_B[0], O_B[1]+1.0, 1.5), (0.06, 0.06, 0.1), mat("#FFC040"))
    W["counter3"] = text3d("counter3", "", (O_B[0], O_B[1]+3.05, 2.1), 0.32, RED, None, extrude=0.04)
    # ---------------- carretera de sueldos ----------------
    W["road"] = g = group("roadset", O_R)
    B = Batch("rd_b", g, 1.0)
    B.add((0, 0, -0.06), (400, 400, 0.1), tmat("grassr", "#5A9A44", 16, 0.10, 141))
    B.add((0, 100, 0.0), (3.0, 400, 0.06), tmat("roadr", "#4A4A50", 16, 0.05, 142, asphalt))
    B.done()
    W["bricks"] = [box(f"sb{q}", (O_R[0], O_R[1]+2.0+q*1.0, 0.3), (0.8, 0.6, 0.6), tmat("salary", "#5AA860", 16, 0.10, 143, stripes)) for q in range(140)]
    W["debt"] = box("debt", (O_R[0]+4.0, O_R[1]+6.0, 0), (2.0, 2.0, 1.0), mat(RED), origin=(0, 0, -0.5))
    # ---------------- gráfica del interés ----------------
    W["chart"] = g = group("chart", O_I)
    B = Batch("ch_b", g, 1.0)
    B.add((0, 0, -0.05), (200, 200, 0.1), tmat("cfl", "#2E3644", 16, 0.05, 144, tiles)); B.add((0, 20, 20), (200, 0.2, 40), "#1C2230")
    B.add((-3.5, 2, 3), (0.1, 0.1, 6), "#F4F1EA"); B.add((0, 2, 0.05), (7, 0.1, 0.1), "#F4F1EA")
    B.done()
    W["cbars"] = [box(f"cb{q}", (O_I[0]-3.0+q*0.5, O_I[1]+2, 0), (0.36, 0.36, 1.0), mat("#5AB898"), origin=(0, 0, -0.5)) for q in range(13)]
    W["lossbar"] = box("lossbar", (O_I[0]+3.0, O_I[1]+2, 0), (0.6, 0.6, 1.0), mat(RED), origin=(0, 0, -0.5))
    W["nil"] = Person("nil", NIL)
    camera(28)
    return W

def hide_all(W):
    for k in ("hosp", "door", "pram", "kitchen", "bottle", "bday", "road", "chart"): show(W[k], False)
    for k in ("counter", "clock", "pile", "counter2", "tag", "price", "flame", "counter3", "debt", "lossbar"): hid(W[k], True)
    for o in W["bricks"] + W["cbars"]: hid(o, True)
    W["nil"].show(False); W["nil"].root.scale = (1, 1, 1)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def shake(T, amp):
    return (amp*math.sin(T*47), amp*math.sin(T*53+1), amp*math.sin(T*41+2))

def settext(o, s, col=None):
    if o.data.body != s: o.data.body = s
    if col: o.data.materials[0] = mat(col)
    hid(o, False)

def baby(W, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0, s=0.42):
    H = W["nil"]; H.show(True); H.place(x, y, face, z); H.root.scale = (s, s, s); H.idle(T); H.face(T, expr, look_)
    return H

def hosp(W):
    show(W["hosp"], True); world_color("#E8F0F4"); light_dir((0.5, -0.4, 0.75)); shadow(0.45)

# ------------------------------------------------------------------ planos
@shot(0.0, 4.98)
def m1(W, T, M):
    hosp(W); k = T/4.98
    mins = 0 if T < 2.4 else (T-2.4)*20
    settext(W["counter"], fmt(money(mins)), GOLD)
    settext(W["clock"], f"{int(mins//60)} H {int(mins % 60)} MIN")
    pl = W["pile"]; hid(pl, False); pl.scale = (1, 1, max(0.02, money(mins)/1e6*0.8))
    H = baby(W, -0.1, 1.2, 0, T, "happy" if T < 2.6 else "shock", (0, 0.5), z=0.6)
    H.leg(-1, 1.5, 1.4); H.leg(1, 1.5, 1.4); H.hips.location.z = 0.35
    for sx in (-1, 1): H.arm(sx, fwd=1.0+0.6*math.sin(T*8+sx), side=0.4, elbow=0.6)
    look(lerpv((0.4, -2.4, 1.7), (0.2, -1.5, 1.6), eio(k)), (0.0, 1.6, 1.55), 24)
    M["grade"] = "lab"

@shot(4.98, 10.72)
def m2(W, T, M):
    show(W["door"], True); show(W["pram"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
    k = (T-4.98)/5.74
    y = O_D[1]+2.4-1.5*(T-4.98)
    W["pram"].location = (O_D[0]+0.2, y, 0.05*abs(math.sin(T*9))); W["pram"].rotation_euler = (0, 0, 0)
    H = baby(W, O_D[0]+0.2, y+0.05, 0, T, "happy", (0.3*math.sin(T), 0.2), z=0.75)
    H.leg(-1, 1.5, 1.4); H.leg(1, 1.5, 1.4); H.hips.location.z = 0.35
    mins = 2.4*20 + (T-4.98)*14 if T < 7.5 else 120
    c = W["counter2"]; settext(c, fmt(money(min(mins, 120))), GOLD); c.location = (O_D[0]+0.2, y+0.2, 1.9); c.scale = (1, 1, 1)
    look(lerpv((O_D[0]+2.5, O_D[1]-7.0, 1.5), (O_D[0]+1.8, y-3.6, 1.4), eio(k)), (O_D[0]+0.2, y, 1.3), 26)
    M["grade"] = "day"

@shot(10.72, 17.28)
def m3(W, T, M):
    hosp(W); k = (T-10.72)/6.56
    mins = 120 + (1000-120)*eio(clamp((T-10.8)/2.6))
    zero = mins >= 999.5
    settext(W["counter"], fmt(money(mins)), RED if zero else GOLD)
    settext(W["clock"], f"{int(mins//60)} H {int(mins % 60)} MIN")
    pl = W["pile"]; hid(pl, zero); pl.scale = (1, 1, max(0.02, money(mins)/1e6*0.8))
    H = baby(W, -0.1, 1.2, 0, T, "shock" if zero else "worried", (0.4, 0.4), z=0.6)
    H.leg(-1, 1.5, 1.4); H.leg(1, 1.5, 1.4); H.hips.location.z = 0.35
    if zero:
        for sx in (-1, 1): H.arm(sx, fwd=2.8, side=0.3, elbow=0.6)
    sx_, sy_, sz_ = shake(T, 0.03 if 13.4 < T < 13.9 else 0.0)
    look(lerpv((-1.6+sx_, -2.6+sy_, 1.9+sz_), (-0.4, -1.8, 1.8), eio(k)), (0.3, 2.0, 1.6), 24)
    if 13.46 < T < 13.54: M["flash"] = 1
    M["grade"] = "lab" if not zero else "alarm"

@shot(17.28, 25.1)
def m4(W, T, M):
    show(W["kitchen"], True); show(W["bottle"], True); world_color("#FFE8C0"); light_dir((0.5, -0.4, 0.75)); shadow(0.45)
    k = (T-17.28)/7.82
    mins = 1000 + 440*eio(clamp((T-17.4)/4.5))
    if T < 23.0:
        c = W["counter2"]; settext(c, fmt(money(mins)), RED); c.location = (O_K[0], O_K[1]+3.05, 2.3); c.scale = (0.8, 0.8, 0.8)
    H = baby(W, O_K[0]-0.6, O_K[1]+1.0, 30, T, "worried" if T < 23.0 else "shock", (0.6, 0.2), z=1.06)
    H.leg(-1, 1.5, 1.4); H.leg(1, 1.5, 1.4); H.hips.location.z = 0.35
    H.arm(1, fwd=1.4, side=0.0, elbow=0.4)
    if T > 23.0:
        hid(W["tag"], False); settext(W["price"], "440.000 €")
        look(lerpv((O_K[0]+0.9, O_K[1]-1.2, 1.6), (O_K[0]+0.7, O_K[1]-0.8, 1.55), eio(clamp((T-23.0)/2.0))), (O_K[0]+0.4, O_K[1]+1.0, 1.4), 28, fstop=3.5)
    else:
        look(lerpv((O_K[0]+0.6, O_K[1]-3.0, 1.9), (O_K[0]+0.3, O_K[1]-2.4, 1.8), eio(clamp((T-17.28)/5.7))), (O_K[0]-0.1, O_K[1]+1.5, 1.7), 26)
    M["grade"] = "cafe"

@shot(25.1, 28.16)
def m5(W, T, M):
    show(W["bday"], True); world_color("#FFE0E8"); light_dir((0.5, -0.4, 0.75)); shadow(0.45)
    k = (T-25.1)/3.06
    hid(W["flame"], False); W["flame"].scale = (1, 1, 1+0.3*math.sin(T*20))
    settext(W["counter3"], fmt(money(525600)), RED)
    H = baby(W, O_B[0]-0.8, O_B[1]+0.6, 20, T, "happy" if T < 26.5 else "shock", (0.4, 0.3), s=0.55)
    for sx in (-1, 1): H.arm(sx, fwd=1.2, side=0.5, elbow=0.4)
    look(lerpv((O_B[0]+0.6, O_B[1]-3.0, 1.5), (O_B[0]+0.3, O_B[1]-2.4, 1.6), eio(k)), (O_B[0]-0.2, O_B[1]+1.4, 1.5), 24)
    M["grade"] = "dawn"

@shot(28.16, 39.46)
def m6(W, T, M):
    show(W["road"], True); world_color("#9CC8E8"); light_dir((0.45, -0.55, 0.7)); shadow(0.5)
    k = (T-28.16)/11.3
    yrs18 = 18*525600
    c = W["counter2"]; settext(c, fmt(money(yrs18*eio(clamp((T-30.6)/2.5)) + 525600)), RED); c.location = (O_R[0]+0.6, O_R[1]+2.0, 2.5); c.scale = (0.55, 0.55, 0.55)
    db = W["debt"]; hid(db, False); db.scale = (1, 1, 0.2+8.0*eio(clamp((T-30.6)/3.0)))
    n = int(140*clamp((T-34.8)/3.5))
    for q, b in enumerate(W["bricks"]): hid(b, q >= n)
    H = W["nil"]; H.show(True); H.place(O_R[0]-0.6, O_R[1]+0.5, 10); H.idle(T); H.face(T, "shock" if T > 31.0 else "worried", (0.3, 0.6))
    if T < 34.8:
        look(lerpv((O_R[0]-1.0, O_R[1]-6.0, 1.8), (O_R[0]-0.5, O_R[1]-7.5, 3.0), eio(clamp((T-28.16)/6.6))), (O_R[0]+1.6, O_R[1]+4.0, lerp(1.8, 4.0, eio(clamp((T-30.6)/3.0)))), 24)
    else:
        e = eio(clamp((T-34.8)/4.6))
        look((O_R[0]+lerp(-2.0, -4.0, e), O_R[1]+lerp(-4.0, -6.0, e), lerp(2.0, 9.0, e)), (O_R[0], O_R[1]+lerp(10, 60, e), 0.5), lerp(26, 22, e))
    M["grade"] = "day"

@shot(39.46, 46.0)
def m7(W, T, M):
    show(W["chart"], True); world_color("#1C2230"); light_dir((0.4, -0.6, 0.7)); shadow(0.5)
    k = (T-39.46)/6.54
    lb = W["lossbar"]; hid(lb, False); lb.scale = (1, 1, 5.2)
    g = eio(clamp((T-40.0)/4.2))
    for q, b in enumerate(W["cbars"]):
        hid(b, q > g*12.5); b.scale = (1, 1, 0.1+0.4*q*(1+0.3*math.sin(T*3+q)*0))
    look(lerpv((O_I[0], O_I[1]-11.0, 3.0), (O_I[0]+0.4, O_I[1]-9.0, 3.2), eio(k)), (O_I[0], O_I[1]+2, 2.8), 26)
    if 44.48 < T < 44.56: M["flash"] = 1
    M["grade"] = "lab"

@shot(46.0, TOTAL+0.1)
def m8(W, T, M):
    hosp(W); k = (T-46.0)/3.39
    settext(W["counter"], fmt(1_000_000), GOLD); settext(W["clock"], "0 H 0 MIN")
    pl = W["pile"]; hid(pl, False); pl.scale = (1, 1, 0.8)
    H = baby(W, -0.1, 1.2, 0, T, "smirk", (0, 0.3), z=0.6)
    H.leg(-1, 1.5, 1.4); H.leg(1, 1.5, 1.4); H.hips.location.z = 0.35
    H.arm(1, fwd=1.3, side=0.1, elbow=1.4); H.fingers(1, 0.6, 0.2)
    look(lerpv((0.3, -1.9, 1.55), (0.2, -1.4, 1.5), eio(k)), (0.0, 1.5, 1.45), 26)
    M["grade"] = "lab"; M["fade"] = clamp((T-49.0)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
