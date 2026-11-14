"""Q30 · Mini historia «La radio de Lucía» (3D de bloques, 77,3 s). Idea de Héctor: ¿y si fueras la única mujer de la Tierra?
Protagonista original: Lucía (científica polar, parka roja, pelo castaño largo). Hombres del aeropuerto, un camionero, un anciano, una voz desde Groenlandia.
Decorados: terminal del aeropuerto (y=100), casa (y=300), sala de prensa (y=500), estudio de radio (y=700), cabina de camión (y=900), base polar nevada (y=1100)."""
import math, random
import bpy
from vox import *
from mathutils import Vector
from person import Person, npc_look
from world import Batch, tmat, City, building, tree, tiles, planks, asphalt, stripes, brick, text3d, car

FPS = 24
TOTAL = 77.3
LUCIA = dict(skin="#E8BE96", hair="#5A3820", hair2="#6A4428", eye="#2A3A2A", top="#C8302A", top2="#A82420", stripe="#F4F1EA",
             legs="#2A2A34", legs2="#20202A", shoe="#5A3A20", shoe2="#5A3A20", watch=True, hstyle="long")
INUK = dict(skin="#C69068", hair="#141216", hair2="#1C1A1E", eye="#2A1A10", top="#E0A030", top2="#C08020", stripe="#F4F1EA",
            legs="#2A2A34", legs2="#20202A", shoe="#3A2A20", shoe2="#3A2A20", watch=False, hstyle="long")

class Env:
    def talk(self, who, T): return 0.0

O_AP = (0, 100, 0); O_HM = (0, 300, 0); O_PR = (0, 500, 0); O_RD = (0, 700, 0); O_TK = (0, 900, 0); O_GR = (0, 1100, 0)

def longhair(P, L):
    hs = 0.56*P.s; t = hs/2; Hm = mat(L["hair"])
    for sx in (-1, 1):
        box(f"{P.n}_lock{sx}", (sx*(t+0.03*P.s), -0.02*P.s, hs*0.25), (0.07*P.s, hs*0.9, hs*1.0), Hm, P.head)
    box(f"{P.n}_lockb", (0, t+0.03*P.s, hs*0.1), (hs+0.1*P.s, 0.07*P.s, hs*1.2), Hm, P.head)

def man(name, seed, h=1.0):
    L = npc_look(seed)
    if L["hstyle"] == "long": L["hstyle"] = "short"
    return Person(name, L, h)

def build():
    reset((720, 1280))
    W = {}
    r = random.Random(30)
    # terminal
    W["ap"] = g = group("ap", O_AP); B = Batch("ap_b", g, 1.0)
    B.add((0, 0, -0.05), (40, 40, 0.1), tmat("apfl", "#C8C8C4", 16, 0.04, 301, tiles)); B.add((0, 12, 4), (40, 0.2, 8), "#9FB8C8")
    for x in range(-18, 19, 3): B.add((x, 11.8, 4), (0.2, 0.1, 8), "#6A7A88")
    B.add((0, 0, 8.0), (40, 40, 0.1), "#E8E8E4"); B.add((-6, 6, 3.5), (4, 0.2, 1.2), "#1C1C22")
    B.done()
    W["plane"] = pl = group("plane30", (0, 0, 0)); P_ = Batch("pl30_b", pl, 1.0)
    P_.add((0, 0, 0), (14, 2.2, 2.2), "#F4F4F6"); P_.add((-0.5, 0, -0.3), (3, 18, 0.3), "#E8E8EC"); P_.add((-6.5, 0, 1.8), (1.6, 0.3, 2.6), "#3A6AA8")
    P_.done()
    # casa
    W["hm"] = g = group("hm", O_HM); B = Batch("hm_b", g, 1.0)
    B.add((0, 0, -0.05), (12, 12, 0.1), tmat("hmfl", "#A07A50", 16, 0.1, 302, planks)); B.add((0, 3, 2), (12, 0.2, 4), tmat("hmw", "#D8C8A8", 16, 0.04, 303, stripes))
    B.add((0, 0.6, 0.75), (1.6, 1.0, 0.07), "#7A5A3A"); B.add((0, 0.6, 0.37), (0.12, 0.12, 0.74), "#3A3A40")
    for x in (-1.1, 1.1): B.add((x, 0.6, 0.45), (0.5, 0.5, 0.08), "#7A4A2A"); B.add((x, 0.6+0.25*(1 if x < 0 else 1), 0.75), (0.5, 0.08, 0.6), "#7A4A2A")
    for x in (-0.45, 0.45): B.add((x, 0.6, 0.8), (0.4, 0.4, 0.03), "#F4F1EA")
    B.add((-2.4, 2.9, 2.0), (0.8, 0.05, 0.6), "#C8A060")
    B.done()
    # prensa
    W["pr"] = g = group("pr", O_PR); B = Batch("pr_b", g, 1.0)
    B.add((0, 0, -0.05), (20, 20, 0.1), "#2A2A34"); B.add((0, 3, 2.5), (14, 0.2, 5), "#2A4A7A")
    B.add((0, 1.4, 0.6), (1.0, 0.6, 1.2), "#5A3A22"); B.add((0, 1.05, 1.28), (0.06, 0.06, 0.4), "#1C1C20")
    for q in range(9): B.add((-3+q*0.75, -3.2, 1.6), (0.4, 0.6, 0.4), "#1C1C20"); B.add((-3+q*0.75, -3.2, 0.7), (0.06, 0.06, 1.4), "#3A3A40")
    B.done()
    # radio
    W["rd"] = g = group("rd", O_RD); B = Batch("rd_b", g, 1.0)
    B.add((0, 0, -0.05), (12, 12, 0.1), "#3A2E2A"); B.add((0, 2.6, 2), (12, 0.2, 4), tmat("rdw", "#5A4A6A", 16, 0.06, 304, tiles))
    B.add((0, 0.6, 0.75), (2.4, 1.0, 0.07), "#2A2A30"); B.add((0, 0.6, 0.37), (2.2, 0.8, 0.74), "#1C1C22")
    B.add((0.3, 0.3, 0.88), (0.9, 0.4, 0.15), "#3A3A44")
    for q in range(8): B.add((0.0+q*0.1, 0.12, 0.97), (0.04, 0.04, 0.06), ["#E03030", "#40E080", "#F0C030"][q % 3])
    B.add((-0.4, 0.3, 1.05), (0.06, 0.06, 0.5), "#2A2A2E")
    B.add((-0.4, 0.15, 1.35), (0.14, 0.16, 0.2), "#4A4A52")
    B.done()
    W["onair"] = box("onair", (O_RD[0]+1.6, O_RD[1]+2.48, O_RD[2]+2.6), (1.6, 0.05, 0.45), mat("#E03030"))
    W["onairt"] = text3d("onairt", "EN EL AIRE", (O_RD[0]+1.6, O_RD[1]+2.44, O_RD[2]+2.52), 0.2, "#F4F1EA", None, extrude=0.01)
    W["wave"] = [box(f"wv{q}", (O_RD[0]-1.6+q*0.12, O_RD[1]+2.48, O_RD[2]+1.6), (0.08, 0.05, 0.1), mat("#40E0FF")) for q in range(16)]
    # cabina de camión
    W["tk"] = g = group("tk", O_TK); B = Batch("tk_b", g, 1.0)
    B.add((0, 0, 0.3), (3, 3, 0.6), "#2A2A30"); B.add((0, -1.2, 1.6), (3, 0.06, 1.4), "#9FC8E0"); B.add((0, -0.9, 0.95), (2.8, 0.5, 0.4), "#3A3A44")
    B.add((-0.5, -0.65, 1.2), (0.6, 0.06, 0.6), "#1C1C20"); B.add((0, 1.4, 1.6), (3, 0.1, 2.6), "#5A5A60")
    B.add((0, 0, 2.95), (3, 3, 0.1), "#4A4A50")
    B.done()
    # base polar
    W["gr"] = g = group("gr", O_GR); B = Batch("gr_b", g, 1.0)
    B.add((0, 0, -0.05), (400, 400, 0.1), "#EEF2F6"); B.add((0, 6, 1.5), (6, 3, 3), "#C8302A"); B.add((0, 4.45, 1.0), (1.0, 0.05, 2.0), "#2A2A30")
    B.add((3.4, 6, 4), (0.15, 0.15, 8), "#8A8A90")
    for q in range(10): B.add((r.uniform(-60, 60), r.uniform(30, 80), r.uniform(2, 10)), (r.uniform(8, 20), 4, r.uniform(4, 14)), "#D8E0E8")
    B.done()
    W["flakes"] = [box(f"fk{q}", (0, 0, 0), (0.06, 0.06, 0.06), mat("#FFFFFF")) for q in range(50)]
    W["lucia"] = L = Person("lucia", LUCIA); longhair(L, LUCIA)
    W["inuk"] = I = Person("inuk", INUK); longhair(I, INUK)
    W["men"] = [man(f"mn{q}", 1700+q) for q in range(12)]
    W["boy"] = man("boy", 1790, 0.65)
    W["radio"] = box("radio", (0, 0, 0), (0.5, 0.3, 0.3), mat("#3A3A44"))
    camera(28)
    return W

def hide_all(W):
    for k in ("ap", "plane", "hm", "pr", "rd", "tk", "gr"): show(W[k], False)
    for o in W["wave"] + W["flakes"] + [W[k] for k in ("onair", "onairt", "radio")]: hid(o, True)
    for p in W["men"] + [W["lucia"], W["inuk"], W["boy"]]: p.show(False)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

def person(W, H, x, y, face, T, expr="neutral", look_=(0, 0), z=0.0, talk=0.0):
    H = W[H] if isinstance(H, str) else H
    H.show(True); H.place(x, y, face, z); H.idle(T); H.face(T, expr, look_, talk=talk)
    return H

def sit(H, z=0.48):
    for sx in (-1, 1): H.leg(sx, 1.5, 1.5)
    H.hips.location.z = z

def indoor(W, k, col):
    show(W[k], True); world_color(col); light_dir((0.45, -0.55, 0.7)); shadow(0.45)

# ------------------------------------------------------------------ planos
@shot(0.0, 9.8)
def g1(W, T, M):
    indoor(W, "ap", "#C8D0D8"); o = O_AP
    pl = W["plane"]; show(pl, True); pl.location = (o[0]+4, o[1]+20, o[2]+1.6)
    Lc = W["lucia"]; Lc.show(True)
    f = clamp(T/3.0)
    Lc.place(o[0]+lerp(-2.0, 0.0, f), o[1]+1.0, 0); (Lc.walk(T*1.1) if T < 3.0 else Lc.idle(T))
    Lc.face(T, "neutral" if T < 3.4 else "worried", (0.8*math.sin(T*1.3), 0) if T > 3.4 else (0, 0))
    if T > 3.4: Lc.head.rotation_euler = (0, 0, 0.6*math.sin((T-3.4)*1.1))
    for q in range(8):
        P = W["men"][q]; P.show(True); P.place(o[0]-4+q*1.2, o[1]+4.0+(q % 3)*1.4, 180+20*math.sin(q)); P.walk(T*0.9+q); P.face(T, "neutral", (0, 0))
    if T < 5.4:
        look(lerpv((o[0]-1.0, o[1]-4.6, 1.8), (o[0]-0.4, o[1]-3.6, 1.75), eio(clamp(T/5.4))), (o[0]-0.4, o[1]+1.5, 1.5), 24)
    else:
        look(lerpv((o[0]+0.4, o[1]-0.9, 1.65), (o[0]+0.3, o[1]-0.5, 1.65), eio(clamp((T-5.4)/4.4))), (o[0], o[1]+1.0, 1.65), 28)
    M["grade"] = "office"

@shot(9.8, 18.94)
def g2(W, T, M):
    show(W["gr"], True); world_color("#B8C8D8"); light_dir((0.3, -0.6, 0.5)); shadow(0.3); o = O_GR
    for q, fl in enumerate(W["flakes"]):
        hid(fl, False); fl.location = (o[0]+((q*1.37) % 8)-4, o[1]+((q*0.73) % 6)-1, 3.5-((T*0.9+q*0.11) % 3.5))
    Lc = person(W, "lucia", o[0]-0.6, o[1]+3.6, 0, T, "happy", (0, 0.3))
    Lc.arm(1, fwd=1.2, side=0.1, elbow=1.4)
    look(lerpv((o[0]+1.5, o[1]-3.0, 1.9), (o[0]+0.8, o[1]-1.0, 1.7), eio(clamp((T-9.8)/9.1))), (o[0]-0.3, o[1]+4.4, 1.6), 24)
    M["grade"] = "cold"

@shot(18.94, 24.9)
def g3(W, T, M):
    indoor(W, "ap", "#C8D0D8"); o = O_AP
    Lc = person(W, "lucia", o[0], o[1]+1.0, 180, T, "worried", (0, 0))
    for q in range(12):
        P = W["men"][q]; ring = q % 6; row = q // 6
        a = math.radians(-60+ring*24); R = 3.0+row*1.4
        x = o[0]+R*math.sin(a); y = o[1]+1.0+R*math.cos(a)
        P.show(True); P.face_to(x, y, o[0], o[1]+1.0); P.idle(T+q); P.face(T, "shock" if q % 3 == 0 else "sad", (0, 0))
    look(lerpv((o[0]+0.6, o[1]+7.0, 6.0), (o[0]+0.5, o[1]+6.0, 5.2), eio(clamp((T-18.94)/6.0))), (o[0], o[1]+0.8, 1.2), 22)
    M["grade"] = "office"

@shot(24.9, 35.32)
def g4(W, T, M):
    indoor(W, "hm", "#6A5A50"); o = O_HM
    if T < 30.6:
        P = W["men"][0]; person(W, P, o[0]-1.1, o[1]+0.6, 0, T, "sad", (0.6, -0.2)); sit(P)
        P.arm(1, fwd=1.3, side=0.3, elbow=2.0)
        look(lerpv((o[0]-0.6, o[1]-2.0, 1.4), (o[0]-0.8, o[1]-1.6, 1.4), eio(clamp((T-24.9)/5.7))), (o[0]-1.1, o[1]+0.6, 1.3), 26)
    else:
        P = W["men"][1]; person(W, P, o[0]-1.1, o[1]+0.6, 0, T, "sad", (0.8, 0)); sit(P)
        Bq = W["boy"]; person(W, Bq, o[0]+1.0, o[1]+0.6, 0, T, "sad", (-0.6, 0)); sit(Bq, 0.48)
        look(lerpv((o[0], o[1]-3.9, 1.5), (o[0], o[1]-3.5, 1.45), eio(clamp((T-30.6)/4.7))), (o[0], o[1]+0.7, 0.95), 22)
    M["grade"] = "day_sad"

@shot(35.32, 44.96)
def g5(W, T, M):
    if T < 41.0:
        indoor(W, "pr", "#141420"); o = O_PR
        Lc = person(W, "lucia", o[0], o[1]+1.9, 0, T, "worried", (0, 0))
        for q in range(4):
            P = W["men"][q+2]; person(W, P, o[0]-2.1+q*1.4+(0.7 if q > 1 else 0), o[1]+2.6, 0, T, "happy" if q % 2 else "neutral", (0, 0), talk=0.5*abs(math.sin(T*6+q)))
        look(lerpv((o[0]+0.4, o[1]-2.6, 2.0), (o[0]+0.3, o[1]-2.0, 1.9), eio(clamp((T-35.32)/5.7))), (o[0], o[1]+1.9, 1.7), 26)
        M["grade"] = "night"; M["flash"] = 1 if (T % 1.3) < 0.05 else 0
    else:
        indoor(W, "rd", "#2A2430"); o = O_RD
        Lc = person(W, "lucia", o[0]-0.4, o[1]-0.25, 180, T, "smirk", (0, 0)); sit(Lc)
        Lc.arm(1, fwd=1.3, side=-0.2, elbow=0.4)
        look(lerpv((o[0]+1.6, o[1]-2.6, 1.6), (o[0]+1.2, o[1]-2.0, 1.55), eio(clamp((T-41.0)/4.0))), (o[0]-0.2, o[1]+0.4, 1.1), 24)
        M["grade"] = "cafe"

@shot(44.96, 58.06)
def g6(W, T, M):
    if T < 49.8 or T > 53.8:
        indoor(W, "rd", "#2A2430"); o = O_RD
        hid(W["onair"], False); hid(W["onairt"], False)
        Lc = person(W, "lucia", o[0]-0.4, o[1]-0.25, 0, T, "happy" if T < 49.8 else "sad", (0, 0), talk=0.6*abs(math.sin(T*7)) if 45.1 < T < 48.2 else 0); sit(Lc)
        Lc.arm(1, fwd=1.0, side=-0.2, elbow=1.0)
        for q, w in enumerate(W["wave"]):
            hid(w, False); w.scale = (1, 1, 1+6*abs(math.sin(T*8+q*0.7)))
        if T < 49.8:
            look(lerpv((o[0]-0.2, o[1]-2.4, 1.5), (o[0]-0.3, o[1]-1.9, 1.45), eio(clamp((T-44.96)/4.8))), (o[0]-0.4, o[1]-0.25, 1.35), 28)
        else:
            look(lerpv((o[0]+1.4, o[1]-3.2, 1.9), (o[0]+1.0, o[1]-2.6, 1.8), eio(clamp((T-53.8)/4.3))), (o[0], o[1]+1.0, 1.5), 24)
        M["grade"] = "cafe"
    elif T < 51.9:
        indoor(W, "tk", "#1A2030"); o = O_TK
        P = W["men"][6]; person(W, P, o[0]-0.5, o[1]+0.0, 0, T, "sad", (0, 0.2), talk=0.5*abs(math.sin(T*6))); sit(P)
        P.arm(1, fwd=1.2, side=0, elbow=0.6); P.arm(-1, fwd=1.2, side=0, elbow=0.6)
        look(lerpv((o[0]+0.4, o[1]-1.0, 1.5), (o[0]+0.3, o[1]-0.9, 1.5), eio(clamp((T-49.8)/2.1))), (o[0]-0.5, o[1]+0.1, 1.35), 22)
        M["grade"] = "night"
    else:
        indoor(W, "hm", "#4A3A34"); o = O_HM
        P = W["men"][7]; person(W, P, o[0]-1.1, o[1]+0.6, 0, T, "sad", (0.4, 0), talk=0.4*abs(math.sin(T*5))); sit(P)
        rd = W["radio"]; hid(rd, False); rd.location = (o[0]-0.2, o[1]+0.4, 0.95)
        look(lerpv((o[0]-0.5, o[1]-1.8, 1.4), (o[0]-0.6, o[1]-1.5, 1.4), eio(clamp((T-51.9)/1.9))), (o[0]-0.8, o[1]+0.6, 1.2), 26)
        M["grade"] = "night"

@shot(58.06, 67.78)
def g7(W, T, M):
    if T < 64.2:
        indoor(W, "rd", "#2A2430"); o = O_RD
        hid(W["onair"], False); hid(W["onairt"], False)
        Lc = person(W, "lucia", o[0]-0.4, o[1]-0.25, 0, T, "neutral" if T < 61.0 else "shock", (0.3, 0.1)); sit(Lc)
        Lc.arm(1, fwd=1.3, side=0.3, elbow=2.0)
        for q, w in enumerate(W["wave"]):
            hid(w, False); amp = 6 if T < 60.8 else 2+3*abs(math.sin(T*3))
            w.scale = (1, 1, 1+amp*abs(math.sin(T*8+q*0.7)))
            if T > 60.8: w.data.materials[0] = mat("#FF70C0")
            else: w.data.materials[0] = mat("#40E0FF")
        look(lerpv((o[0]-0.25, o[1]-1.9, 1.48), (o[0]-0.3, o[1]-1.5, 1.45), eio(clamp((T-58.06)/6.1))), (o[0]-0.4, o[1]-0.25, 1.4), 30, fstop=2.8)
        M["grade"] = "cafe"
    else:
        show(W["gr"], True); world_color("#20283A"); light_dir((0.3, -0.6, 0.5)); shadow(0.3); o = O_GR
        for q, fl in enumerate(W["flakes"]):
            hid(fl, False); fl.location = (o[0]+((q*1.37) % 8)-4, o[1]+((q*0.73) % 6)-1, 3.5-((T*0.9+q*0.11) % 3.5))
        I = person(W, "inuk", o[0]+0.6, o[1]+3.6, 0, T, "worried", (0, 0.1), talk=0.5*abs(math.sin(T*6)))
        I.arm(1, fwd=1.3, side=0.3, elbow=2.0)
        look(lerpv((o[0]+1.2, o[1]-1.6, 1.7), (o[0]+1.0, o[1]+0.0, 1.7), eio(clamp((T-64.2)/3.6))), (o[0]+0.6, o[1]+3.6, 1.6), 24)
        M["grade"] = "cold"

@shot(67.78, 73.62)
def g8(W, T, M):
    indoor(W, "rd", "#2A2430"); o = O_RD
    hid(W["onair"], False); hid(W["onairt"], False)
    Lc = person(W, "lucia", o[0]-0.4, o[1]-0.25, 0, T, "shock" if T < 69.8 else "happy", (0, 0), talk=0.5*abs(math.sin(T*6)) if T > 71.0 else 0); sit(Lc)
    Lc.arm(1, fwd=1.3, side=0.3, elbow=2.0)
    look(lerpv((o[0]-0.3, o[1]-2.3, 1.45), (o[0]-0.35, o[1]-1.9, 1.43), eio(clamp((T-67.78)/5.8))), (o[0]-0.4, o[1]-0.25, 1.42), 30, fstop=2.8)
    M["grade"] = "dawn"

@shot(73.62, TOTAL+0.1)
def g9(W, T, M):
    indoor(W, "rd", "#E8C0A0"); o = O_RD
    hid(W["onair"], False); hid(W["onairt"], False)
    Lc = person(W, "lucia", o[0]+1.6, o[1]+1.2, 0, T, "smirk", (0, 0.1))
    look(lerpv((o[0]+1.95, o[1]-0.9, 1.75), (o[0]+1.9, o[1]-0.4, 1.72), eio(clamp((T-73.62)/3.7))), (o[0]+1.6, o[1]+1.2, 1.7), 26)
    M["grade"] = "dawn"; M["fade"] = clamp((T-76.9)/0.35)

def frame(W, T):
    hide_all(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    apply_vis()
    return M
