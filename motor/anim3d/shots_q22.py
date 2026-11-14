"""Q22 · Mini historia «El chico que encogía cada hora» (3D de bloques, 79,87 s).
Reutiliza los decorados de shots_q14.py (Hugo, cuarto, suelo con gato, borde de la mesa, polvo con ácaro, bacterias) y añade:
cama y móvil gigantes, migas que escriben AYUDA, Lucía (hermana, original), microscopio y vista a través de la lente (máscara en post_q22)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person
from world import Batch, tmat, tiles, planks, stripes, text3d
import shots_q14 as S14

FPS = 24
TOTAL = 79.87
O = S14.O
LUCIA = dict(skin="#F0C8A0", hair="#C8782A", hair2="#A85E1E", eye="#2A4A6A", top="#E86A8A", top2="#C8506E", stripe="#F4F1EA",
             legs="#3A3A54", legs2="#2C2C44", shoe="#F4F1EA", shoe2="#E86A8A", watch=False, hstyle="long")

class Env:
    def talk(self, who, T): return 0.0

def build():
    W = S14.build()
    r = random.Random(22)
    oc = O["cat"]
    W["bigbed"] = bb = group("bigbed", (oc[0]-14, oc[1]+4, 0))
    B = Batch("bigbed_b", bb, 1.0)
    B.add((0, 0, 2.5), (20, 24, 5), "#6A4A30"); B.add((0, 0, 6.0), (19, 23, 2.0), "#F4F1EA"); B.add((0, 8, 7.8), (14, 5, 2.0), "#FFFFFF"); B.add((0, -3, 7.2), (19.5, 14, 0.8), "#3A6EA8")
    B.done()
    W["phone"] = ph = group("phone", (oc[0]+1.0, oc[1]+2.0, 0))
    P = Batch("phone_b", ph, 1.0)
    P.add((0, 0, 0.12), (3.6, 7.4, 0.24), "#1C1C22"); P.add((0, 0, 0.25), (3.3, 6.9, 0.03), "#1E3A5A")
    for i in range(3):
        for j in range(4): P.add((-1.1+i*1.1, 1.6-j*1.1, 0.28), (0.9, 0.9, 0.04), "#2E5A8A")
    P.done()
    W["digits"] = [text3d(f"dg{q}", d, (oc[0]+1.0-1.1+[0, 0, 1.1][q], oc[1]+2.0+1.6+[0, 0, -1.1][q]-0.3, 0.32), 0.7, "#F4F1EA", None, rot=(0, 0, 0), extrude=0.02) for q, d in enumerate("112")]
    W["press"] = [box(f"pr{q}", (0, 0, 0), (0.95, 0.95, 0.05), mat("#40E0FF")) for q in range(3)]
    ot = O["table"]
    W["crumbs"] = []
    CR = {"A": ["01110", "10001", "11111", "10001", "10001"], "Y": ["10001", "01010", "00100", "00100", "00100"], "U": ["10001", "10001", "10001", "10001", "01110"],
          "D": ["11110", "10001", "10001", "10001", "11110"]}
    x0 = -6.0
    for li, ch in enumerate("AYUDA"):
        for rI, row in enumerate(CR[ch]):
            for cI, v in enumerate(row):
                if v == "1": W["crumbs"].append(box(f"cr{li}_{rI}_{cI}", (ot[0]+x0+li*2.6+cI*0.42, ot[1]+5.0-rI*0.42, 42.1), (0.36, 0.36, 0.2), mat("#E8C890")))
    W["onecrumb"] = box("onecrumb", (0, 0, 0), (0.36, 0.36, 0.2), mat("#E8C890"))
    orr = O["room"]
    W["desk"] = dk = group("desk", (orr[0]+2.4, orr[1]+2.2, 0))
    D = Batch("desk_b", dk, 1.0)
    D.add((0, 0, 0.75), (1.8, 0.9, 0.08), "#8A5A36")
    for x in (-0.8, 0.8):
        for y in (-0.35, 0.35): D.add((x, y, 0.37), (0.08, 0.08, 0.74), "#6A4A30")
    D.add((0.3, 0, 0.82), (0.3, 0.3, 0.06), "#2A2A2E"); D.add((0.3, 0.1, 1.05), (0.08, 0.08, 0.45), "#2A2A2E"); D.add((0.3, -0.02, 1.25), (0.08, 0.3, 0.08), "#2A2A2E")
    D.add((0.3, -0.12, 1.05), (0.06, 0.06, 0.28), "#C8C8D0"); D.add((0.3, -0.1, 0.9), (0.2, 0.2, 0.03), "#C8C8D0")
    D.add((-0.5, 0, 0.8), (0.5, 0.35, 0.02), "#F4F1EA")
    D.done()
    W["smallcrumbs"] = [box(f"scr{q}", (orr[0]+2.0+(q % 9)*0.03, orr[1]+2.1+(q//9)*0.03, 0.8), (0.015, 0.015, 0.01), mat("#E8C890")) for q in range(18)]
    W["lucia"] = Person("lucia", LUCIA)
    W["glowcell"] = [box(f"gc{q}", (0, 0, 0), (0.6, 1.4, 0.6), mat("#7AC850")) for q in range(8)]
    return W

def hide_all(W):
    S14.hide_all(W)
    for k in ("bigbed", "phone", "desk"): show(W[k], False)
    for o in W["digits"] + W["press"] + W["crumbs"] + W["smallcrumbs"] + W["glowcell"] + [W["onecrumb"]]: hid(o, True)
    W["lucia"].show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

shake = S14.shake
def hugo(W, o, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0):
    return S14.hugo(W, o, x, y, face, T, expr, look_, z)

def bigfloor(W):
    show(W["catset"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)

# ------------------------------------------------------------------ planos
@shot(0.0, 5.08)
def k1(W, T, M):
    bigfloor(W); o = O["cat"]; show(W["cat"], True)
    k = T/5.08
    W["cat"].location = (o[0]+1.0, o[1]+lerp(9.0, 5.5, eio(k)), 0)
    H = W["hugo"]; H.show(True); x = 0.4-0.3*k
    H.place(o[0]+x, o[1]+0.5-1.2*k, 10); H.walk(T*2.0, run=True); H.face(T, "scared", (0.6, 0.6))
    sx_, sy_, sz_ = shake(T, 0.03)
    look((o[0]+1.6+sx_, o[1]-5.0+sy_, 0.9+sz_), (o[0]+0.2, o[1]+3.5, lerp(3.0, 5.0, k)), 20)
    M["grade"] = "dawn"

@shot(5.08, 11.02)
def k2(W, T, M):
    bigfloor(W); show(W["bigbed"], True); o = O["cat"]; k = (T-5.08)/5.94
    bx, by = o[0]-14, o[1]+4
    H = hugo(W, (bx, by, 0), 0.0, 5.0, 0, T, "shock" if T > 7.0 else "neutral", (0.3, 0.6), z=8.8)
    if T < 7.0: H.hips.rotation_euler = (math.pi/2*(1-eio(clamp((T-5.5)/1.2))), 0, 0)
    look(lerpv((bx+3.0, by+0.0, 10.5), (bx+1.4, by+2.4, 9.8), eio(k)), (bx, by+5.0, 9.4), 26)
    M["grade"] = "dawn"

@shot(11.02, 21.42)
def k3(W, T, M):
    bigfloor(W); show(W["phone"], True); o = O["cat"]; k = (T-11.02)/10.4
    for d in W["digits"]: hid(d, T < 13.0)
    hits = [14.72, 15.1, 15.5]
    pos = [(o[0]+1.0-1.1+0.45, o[1]+2.0+1.6), (o[0]+1.0-1.1+0.45, o[1]+2.0+1.6), (o[0]+1.0+0.45, o[1]+2.0+0.5)]
    for q, p in enumerate(W["press"]):
        if hits[q] < T < hits[q]+0.3: hid(p, False); p.location = (pos[q][0]-0.45, pos[q][1]-0.3, 0.31)
    if T < 13.0:
        H = W["hugo"]; H.show(True); f = (T-11.02)/2.0; H.place(o[0]+lerp(-3.0, 0.3, f), o[1]+lerp(-3.0, 0.5, f), 30); H.walk(T*2.0, run=True); H.face(T, "worried", (0.3, 0))
    else:
        jt = (T % 0.4)/0.4
        z = 0.3+(0.6*math.sin(jt*math.pi) if 14.5 < T < 15.9 else 0)
        i = 0 if T < 15.1 else (1 if T < 15.5 else 2)
        H = hugo(W, (pos[i][0]-0.4, pos[i][1]-0.4, 0), 0, 0, 0, T, "focus" if False else ("happy" if T < 17.3 else "sad"), (0, -0.4), z=z)
        if T > 17.3:
            for sx in (-1, 1): H.arm(sx, fwd=0.3, side=0.5, elbow=1.4)
    look(lerpv((o[0]+3.0, o[1]-4.0, 4.0), (o[0]+2.4, o[1]-3.0, 4.5), eio(k)), (o[0]+0.6, o[1]+2.2, 0.6), 24)
    M["grade"] = "dawn"

@shot(21.42, 27.96)
def k4(W, T, M):
    ot = O["table"]; show(W["tableset"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    k = (T-21.42)/6.54
    H = hugo(W, ot, 0.0, 3.0, 20, T, "worried" if T < 25 else "focus" if False else "neutral", (0.4, 0.3), z=42.0)
    H.arm(1, fwd=0.9, side=0.1, elbow=1.8); H.fingers(1, 0.6, 0.6)
    look(lerpv((ot[0]+2.4, ot[1]-2.0, 43.2), (ot[0]+1.6, ot[1]-1.0, 43.0), eio(k)), (ot[0], ot[1]+3.0, 42.9), 26)
    M["grade"] = "dawn"

@shot(27.96, 39.08)
def k5(W, T, M):
    ot = O["table"]; show(W["tableset"], True); world_color("#FFD9A0"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    n = len(W["crumbs"]); m = int(n*clamp((T-28.1)/4.2))
    for q, c in enumerate(W["crumbs"]): hid(c, q >= m)
    jump = 35.86
    H = W["hugo"]; H.show(True); H.idle(T)
    if T < 33.0:
        tgt = W["crumbs"][max(0, min(n-1, m))].location
        H.place(tgt.x-0.6, tgt.y-0.5, 90, 42.0); H.walk(T*1.6); H.face(T, "focus" if False else "worried", (0.3, -0.5))
        for sx in (-1, 1): H.arm(sx, fwd=1.4, side=0.0, elbow=0.4)
        oc_ = W["onecrumb"]; hid(oc_, False); oc_.location = (tgt.x-0.15, tgt.y-0.5, 42.6)
        look((ot[0], ot[1]-6.5, 48.0), (ot[0], ot[1]+3.6, 42.0), 18)
    elif T < jump:
        H.place(ot[0], ot[1]+0.6, 0, 42.0); H.face(T, "smirk", (0, -0.3))
        look((ot[0]+3.0, ot[1]-6.5, 42.6), (ot[0], ot[1]+0.8, 42.3), 24)
    else:
        f = T-jump; z = max(0.0, 42.0-14.0*f)
        H.place(ot[0], ot[1]-0.5-0.4*f, 0, z)
        for sx in (-1, 1): H.arm(sx, fwd=0.4, side=2.4, elbow=0.2); H.leg(sx, 0.3, 0.4)
        H.face(T, "happy" if z > 0 else "smirk", (0, 0))
        look((ot[0]+3.0, ot[1]-7.5, z+1.6), (ot[0], ot[1]-0.5, z+0.9), 24)
    M["grade"] = "dawn"

@shot(39.08, 48.34)
def k6(W, T, M):
    S14.w5(W, lerp(19.6, 26.2, (T-39.08)/9.26), M)
    H = W["hugo"]
    if T > 44.6:
        o = O["dust"]; H.place(o[0]+0.8, o[1]+1.4, 160); H.face(T, "scared", (0, 0.2))
        for sx in (-1, 1): H.arm(sx, fwd=0.9, side=-0.3, elbow=2.0)
        look(lerpv((o[0]+3.0, o[1]-2.0, 1.4), (o[0]+2.5, o[1]-1.5, 1.4), eio(clamp((T-44.6)/3.7))), (o[0]+0.6, o[1]+2.0, 1.2), 24)

@shot(48.34, 55.36)
def k7(W, T, M):
    o = O["room"]; show(W["room"], True); show(W["desk"], True); world_color("#FFC890"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
    k = (T-48.34)/7.02
    for c in W["smallcrumbs"]: hid(c, False)
    L = W["lucia"]; L.show(True)
    if T < 50.4:
        f = clamp((T-48.4)/2.0); L.place(o[0]-3.0+3.6*f, o[1]-1.0+1.8*f, 60); L.walk(T*1.3); L.face(T, "neutral", (0.3, 0))
        look((o[0]+3.6, o[1]-3.2, 1.7), (o[0]+0.4, o[1]+0.8, 1.3), 24)
    elif T < 53.9:
        L.place(o[0]+1.6, o[1]+1.4, 40); L.idle(T); L.face(T, "worried" if T < 51.6 else "shock", (0.4, -0.6))
        look(lerpv((o[0]+1.0, o[1]+0.3, 1.5), (o[0]+1.4, o[1]+0.9, 1.3), eio(clamp((T-50.4)/3.0))), (o[0]+2.1, o[1]+2.1, 0.82), 30, fstop=2.8)
    else:
        L.place(o[0]+2.0, o[1]+1.2, 10); L.idle(T); L.face(T, "shock", (0.0, 0.2))
        look((o[0]+2.4, o[1]-1.4, 1.5), (o[0]+2.1, o[1]+1.2, 1.4), 26)
    M["grade"] = "dawn"

def scope_view(W, T, M, hug_s=1.0, blur=0.0, wave=True):
    o = O["blood"]; world_color("#1C2A1C"); light_dir((0.4, -0.5, 0.75)); shadow(0.3)
    S14.stream(W, "bact", T, o, 10, (5, 16, 3.5), 0.5)
    H = hugo(W, o, 0.0, 0.0, 0, T, "happy", (0, 0.1), z=1.6)
    H.root.scale = (hug_s,)*3
    if wave: H.arm(1, fwd=0.3, side=2.6, elbow=0.4+0.5*math.sin(T*9))
    for sx in (-1, 1): H.leg(sx, 0.3*math.sin(T*3+sx), 0.4)
    look((o[0]+0.3, o[1]-6.0, 2.4), (o[0], o[1], 2.3), 26)
    M["grade"] = "lab"; M["scope"] = 1; M["blur"] = blur

@shot(55.36, 65.72)
def k8(W, T, M):
    if T < 59.6:
        o = O["room"]; show(W["room"], True); show(W["desk"], True); world_color("#FFC890"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
        L = W["lucia"]; L.show(True); L.place(o[0]+2.7, o[1]+1.4, -60); L.idle(T); L.face(T, "focus" if False else "worried", (0.0, -0.5))
        L.chest.rotation_euler = (0.35, 0, 0)
        for sx in (-1, 1): L.arm(sx, fwd=1.4, side=0.1, elbow=1.2)
        look(lerpv((o[0]+0.4, o[1]-2.0, 1.6), (o[0]+0.9, o[1]-1.4, 1.5), eio(clamp((T-55.36)/4.2))), (o[0]+2.6, o[1]+1.9, 1.2), 26)
        M["grade"] = "dawn"
    else:
        scope_view(W, T, M, 1.0, 0.0, T > 63.7)

@shot(65.72, 73.56)
def k9(W, T, M):
    f = clamp((T-70.5)/2.5)
    scope_view(W, T, M, lerp(1.0, 0.35, eio(f)), f*1.0, True)

@shot(73.56, TOTAL+0.1)
def k10(W, T, M):
    if T < 77.4:
        f = clamp((T-73.56)/3.0)
        scope_view(W, T, M, lerp(0.35, 0.08, eio(f)), 1.0+2.0*f, True)
        if f > 0.95: W["hugo"].show(False)
    else:
        o = O["room"]; show(W["room"], True); show(W["desk"], True); world_color("#FFC890"); light_dir((0.5, -0.4, 0.75)); shadow(0.5)
        L = W["lucia"]; L.show(True); L.place(o[0]+2.4, o[1]+1.0, 0); L.idle(T); L.face(T, "sad", (0, 0.1))
        look(lerpv((o[0]+2.6, o[1]-1.4, 1.62), (o[0]+2.5, o[1]-0.9, 1.6), eio(clamp((T-77.4)/2.4))), (o[0]+2.4, o[1]+1.0, 1.5), 28)
        M["grade"] = "dawn"
    M["fade"] = clamp((T-79.4)/0.4)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
