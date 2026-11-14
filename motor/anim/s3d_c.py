"""3D · «Ocho Plantas a Oscuras» (serie APAGON). Decorados (fachada, piso, rellano, corte del edificio) + poses."""
import math, random
from m3d import *

MARTA = dict(skin="#E8C3A0", skin2="#D2A884", hair="#6B4A32", top="#D59A2A", top2="#B07A1A", legs="#3C4658", shoe="#FBF8F1", hair_style="bun")

def windows_grid(name, parent, x0, z0, cols, rows, dx, dz, y, lit_fn):
    out = []
    for r in range(rows):
        for c in range(cols):
            o = box(f"{name}_{r}_{c}", (x0+c*dx, y, z0+r*dz), (dx*0.6, 0.05, dz*0.55), "#FFD98A" if lit_fn(r, c) else "#1B2030", 0.0, parent)
            out.append((r, c, o))
    return out

def build():
    W = {}
    reset((540, 960), 15); world_color("#2A3550")
    # ---- exterior: fachada con 10 plantas ----
    ex = group("ext", None, (0, 0, 0)); W["ext"] = ex
    plane("ex_ground", (0, -4, 0), (40, 20), "#2A2E36", parent=ex)
    box("ex_bld", (0, 1, 5.2), (5.2, 3, 10.4), "#B7A893", 0.02, ex)
    box("ex_roof", (0, 1, 10.5), (5.6, 3.4, 0.2), "#5E4535", 0.02, ex)
    W["ex_win"] = windows_grid("exw", ex, -1.8, 0.8, 4, 10, 1.2, 1.0, -0.52, lambda r, c: True)
    for i, (x, h) in enumerate(((-7, 7), (-4.6, 5), (5, 8), (7.6, 6), (10, 9))):
        box(f"ex_n{i}", (x, 3+i % 2, h/2), (2.2, 2.5, h), "#3B4150", 0.02, ex)
        W.setdefault("ex_nwin", []).extend(windows_grid(f"exn{i}", ex, x-0.6, 0.8, 2, int(h)-1, 1.0, 1.0, 1.72+i % 2, lambda r, c: True))
    # ---- piso de Marta ----
    ap = group("apt", None, (0, 30, 0)); W["apt"] = ap
    plane("ap_floor", (0, 0, 0), (12, 12), "#8A6A4E", parent=ap)
    box("ap_wallb", (0, 3, 1.5), (12, 0.2, 3), "#E6D8C1", 0.0, ap)
    box("ap_walll", (-4, 0, 1.5), (0.2, 12, 3), "#D9C7AA", 0.0, ap)
    box("ap_win_frame", (1.6, 2.88, 1.7), (2.0, 0.1, 1.6), "#F4EEE3", 0.02, ap)
    W["ap_win"] = box("ap_win", (1.6, 2.83, 1.7), (1.8, 0.05, 1.4), "#5B6F9A", 0.0, ap)
    box("ap_winbar", (1.6, 2.8, 1.7), (0.06, 0.06, 1.4), "#F4EEE3", 0.0, ap)
    box("sofa_seat", (-2.0, 1.6, 0.25), (2.2, 0.9, 0.5), "#C8372D", 0.08, ap)
    box("sofa_back", (-2.0, 2.05, 0.65), (2.2, 0.3, 0.8), "#A82E25", 0.08, ap)
    box("rug", (-0.8, 0.6, 0.01), (3, 2, 0.02), "#6F8F5A", 0.0, ap)
    cyl("lamp_cord", (0.2, 0.8, 2.6), 0.01, 0.8, "#26252A", ap)
    W["lamp"] = cyl("lamp_shade", (0.2, 0.8, 2.15), 0.35, 0.3, "#FFE9A8", ap, 24, r2=0.15)
    # cocina (al fondo derecha)
    box("kt_counter", (3.2, 2.4, 0.45), (2.6, 0.7, 0.9), "#8C6A4E", 0.02, ap)
    box("kt_top", (3.2, 2.4, 0.92), (2.7, 0.75, 0.06), "#DCD6CB", 0.01, ap)
    box("kt_sink", (3.4, 2.35, 0.94), (0.7, 0.45, 0.04), "#6F7781", 0.01, ap)
    cyl("kt_tap", (3.4, 2.6, 1.15), 0.03, 0.4, "#9AA3AD", ap)
    box("kt_spout", (3.4, 2.5, 1.33), (0.05, 0.25, 0.05), "#9AA3AD", 0.01, ap)
    W["drop"] = sphere("drop", (3.4, 2.38, 1.2), 0.035, "#6FA8C7", (1, 1, 1.3), ap, 12)
    W["fridge"] = box("fridge", (4.3, 1.0, 0.95), (0.8, 0.75, 1.9), "#F4EEE3", 0.05, ap)
    box("fridge_h", (3.87, 0.9, 1.2), (0.04, 0.05, 0.4), "#9AA3AD", 0.01, ap)
    W["bottles"] = [cyl(f"bt{i}", (2.4+i*0.18, 2.3, 1.07), 0.06, 0.26, "#9ED0E6", ap) for i in range(5)]
    W["pot"] = cyl("pot", (2.9, 2.3, 1.03), 0.18, 0.18, "#AEB6BF", ap)
    W["candle"] = cyl("candle", (-1.1, 0.9, 0.62), 0.05, 0.22, "#F4EEE3", ap)
    box("table", (-1.1, 0.9, 0.25), (0.9, 0.6, 0.5), "#6F5240", 0.03, ap)
    W["flame"] = sphere("flame", (-1.1, 0.9, 0.78), 0.04, "#FFC845", (1, 1, 1.8), ap, 12)
    # baño (bañera) en otra zona del piso
    bt = group("bath", ap, (-2.5, -3.5, 0)); W["bath"] = bt
    plane("bt_floor", (0, 0, 0.005), (4, 3), "#DCD6CB", parent=bt)
    box("bt_wall", (0, 1.4, 1.5), (4, 0.15, 3), "#CFE0E3", 0.0, bt)
    box("tub_b", (0, 0.7, 0.06), (1.8, 0.8, 0.12), "#FBF8F1", 0.03, bt)
    for nm, lc, sz in (("tub_f", (0, 0.33, 0.32), (1.8, 0.08, 0.62)), ("tub_k", (0, 1.07, 0.32), (1.8, 0.08, 0.62)), ("tub_l", (-0.86, 0.7, 0.32), (0.08, 0.8, 0.62)), ("tub_r", (0.86, 0.7, 0.32), (0.08, 0.8, 0.62))):
        box(nm, lc, sz, "#FBF8F1", 0.03, bt)
    W["tubwater"] = box("tubwater", (0, 0.7, 0.35), (1.64, 0.66, 0.5), "#6FA8C7", 0.0, bt)
    # puerta de entrada
    W["door"] = box("door", (-3.88, -1.0, 1.05), (0.08, 0.95, 2.1), "#7A5640", 0.02, ap)
    W["doorlight"] = box("doorlight", (-3.7, -1.0, 0.005), (0.5, 0.95, 0.01), "#FFE3A0", 0.0, ap)
    # ---- rellano con ascensor ----
    hl = group("hall", None, (0, 60, 0)); W["hall"] = hl
    plane("hl_floor", (0, 0, 0), (10, 8), "#9A8F80", parent=hl)
    box("hl_wall", (0, 2, 1.5), (10, 0.2, 3), "#CFC2AA", 0.0, hl)
    box("el_frame", (1.0, 1.88, 1.15), (1.6, 0.08, 2.3), "#6F7781", 0.01, hl)
    W["el_doors"] = [box(f"el_d{i}", (1.0+sx*0.36, 1.82, 1.1), (0.7, 0.05, 2.1), "#AEB6BF", 0.0, hl) for i, sx in enumerate((-1, 1))]
    W["el_btn"] = sphere("el_btn", (2.05, 1.85, 1.15), 0.05, "#C8372D", (1, 0.5, 1), hl, 12)
    box("exit_sign", (-2.6, 1.86, 2.5), (0.6, 0.04, 0.22), "#5BD38A", 0.0, hl)
    # ---- corte del edificio (agua) ----
    sc_ = group("section", None, (0, 90, 0)); W["section"] = sc_
    plane("sec_bg", (0, 2, 0), (20, 4), "#1A1F2B", parent=sc_)
    for f in range(10):
        box(f"fl{f}", (0, 0, 0.45+f*0.9), (3.2, 2.0, 0.82), "#B7A893" if f != 7 else "#E2A63B", 0.02, sc_)
    box("sec_base", (0, 0, -0.3), (3.4, 2.2, 0.6), "#474B55", 0.02, sc_)
    W["pump"] = box("pump", (1.2, -0.6, -0.3), (0.5, 0.4, 0.4), "#C8372D", 0.04, sc_)
    cyl("pipe", (1.95, -0.4, 4.4), 0.1, 9.4, "#6F7781", sc_)
    W["water"] = cyl("water", (1.95, -0.52, 0), 0.07, 1.0, "#6FA8C7", sc_)
    W["marta"] = Person("marta", MARTA, 0.97)
    camera(30)
    return W

def hide_all(W):
    for k in ("ext", "apt", "hall", "section"): show(W[k], False)
    W["marta"].show(True)

def set_city_lights(W, k):
    for i, (r, c, o) in enumerate(W["ex_win"] + W["ex_nwin"]):
        off = k > ((i*37) % 100)/100*0.85+0.1
        o.data.materials[0] = mat("#1B2030" if off else "#FFD98A")

# ---------------- escenas C1 ----------------
def c1_0(W, lt, d, t):
    hide_all(W); show(W["ext"]); W["marta"].show(False); world_color("#2E3A55")
    set_city_lights(W, clamp((lt/d-0.15)/0.6))
    k = ease(lt/d); look(lerpv((0, -16, 3.0), (0, -12.5, 5.5), k), (0, 1, lerp(4.5, 7.2, k)), 28)

def c1_1(W, lt, d, t):
    hide_all(W); show(W["apt"]); show(W["bath"], False); world_color("#2E3A55")
    on = lt < d*0.4 or (lt < d*0.55 and math.sin(lt*40) > 0.2)
    W["lamp"].data.materials[0] = mat("#FFE9A8" if on else "#55524A")
    m = W["marta"]; m.face_to(0.2, 31.2, 0.2, 25); m.pose("stand" if on else "think", t, expr="neutral" if on else "worried", look=(0, 0.4 if not on else 0))
    look((0.9, 26.6, 1.5), (0.2, 31.2, 1.3), 28)

def c1_2(W, lt, d, t):
    hide_all(W); show(W["apt"]); show(W["bath"], False); world_color("#1A2135"); W["lamp"].data.materials[0] = mat("#55524A")
    m = W["marta"]; m.face_to(-0.4, 31.0, 0.5, 26); m.pose("phone", t, expr="focus", look=(0.2, 0.5))
    look((0.4, 27.6, 1.45), (-0.4, 31.0, 1.35), 30)

def c1_3(W, lt, d, t):
    hide_all(W); show(W["hall"]); world_color("#151A26")
    for dd in W["el_doors"]: dd.location.y = 1.82
    x = lerp(-2.6, 0.6, ease(clamp(lt/(d*0.5))))
    m = W["marta"]; m.face_to(x, 59.4+0.0, 1.0, 62); m.pose("reach" if lt > d*0.5 else "stand", t, walk=0 if lt > d*0.5 else lt*1.5, expr="focus")
    m.root.location.y = 60.4
    W["el_btn"].data.materials[0] = mat("#C8372D" if (lt > d*0.5 and math.sin(t*6) > 0) else "#3A2A2A")
    look((-1.2, 56.4, 1.7), (0.6, 61.2, 1.2), 26)

def c1_4(W, lt, d, t):
    hide_all(W); show(W["hall"]); W["marta"].show(False); world_color("#0E121C")
    W["el_btn"].data.materials[0] = mat("#C8372D" if math.sin(t*6) > 0 else "#3A2A2A")
    look((1.0, 57.0, 1.3), (1.0, 61.9, 1.4), 28)

def c1_5(W, lt, d, t):
    hide_all(W); show(W["apt"]); show(W["bath"], False); world_color("#1A2135")
    x = lerp(0.8, 2.85, ease(clamp(lt/(d*0.45))))
    m = W["marta"]; m.face_to(x, 31.9, 3.4, 32.4); m.pose("reach" if lt > d*0.45 else "stand", t, walk=0 if lt > d*0.45 else lt*1.5, expr="worried" if lt > d*0.7 else "focus")
    W["drop"].location.z = 1.2 - ((t*1.3) % 1)**2*0.25; W["drop"].hide_render = lt < d*0.5
    look((1.2, 28.4, 1.6), (3.0, 32.2, 1.1), 26)

def c1_6(W, lt, d, t):
    hide_all(W); show(W["section"]); W["marta"].show(False); world_color("#11151F")
    pw = lt < d*0.35; lvl = 1.0 if pw else lerp(1.0, 0.27, ease(clamp((lt/d-0.35)/0.3)))
    W["water"].scale = (1, 1, max(0.02, 9.2*lvl)); W["water"].location.z = 9.2*lvl/2 - 0.3
    W["pump"].data.materials[0] = mat("#C8372D" if pw else "#474B55")
    a = 0.25*math.sin(t*0.3); look((math.sin(a)*14.5, 90-math.cos(a)*14.5, 4.6), (0.6, 90, 4.2), 24)

def c1_7(W, lt, d, t):
    hide_all(W); show(W["apt"]); world_color("#1A2135")
    k = 0.15+0.75*clamp(lt/d); tw = W["tubwater"]; tw.scale = (1, 1, k); tw.location.z = 0.1+0.25*k
    m = W["marta"]; m.face_to(-1.2, 26.9, -2.5, 27.2); m.pose("carry", t, expr="focus")
    look((0.6, 23.6, 1.9), (-2.1, 27.1, 0.5), 26)

def c1_8(W, lt, d, t):
    hide_all(W); show(W["apt"]); show(W["bath"], False); world_color("#1A2135")
    m = W["marta"]; m.face_to(2.9, 30.4, 4.3, 31.0); m.pose("think", t, expr="focus")
    look((1.6, 27.6, 1.6), (3.7, 31.0, 1.2), 26)

def c1_9(W, lt, d, t):
    hide_all(W); show(W["apt"]); show(W["bath"], False); world_color("#151B2C")
    pull = math.sin(clamp(lt/(d*0.5))*math.pi)
    m = W["marta"]; m.face_to(3.0+0.3*pull, 30.5, 4.3, 31.0); m.pose("reach" if pull > 0.3 else "stand", t, expr="focus")
    look((1.4, 27.2, 1.6), (3.7, 30.8, 1.2), 24)

def c1_10(W, lt, d, t):
    hide_all(W); show(W["apt"]); show(W["bath"], False); world_color("#0E1220")
    W["flame"].scale = (1, 1, 1.6+0.3*math.sin(t*13))
    m = W["marta"]; m.face_to(-2.0, 31.6, -1.1, 30.9); m.pose("sit", t, expr="neutral")
    m.root.location.z = 0.05
    look((-0.2, 28.0, 1.3), (-1.6, 31.2, 0.9), 26)

def c1_11(W, lt, d, t):
    hide_all(W); show(W["apt"]); show(W["bath"], False); world_color("#06080F")
    kn = lt > d*0.25
    W["door"].location.x = -3.88 + (math.sin(t*60)*0.006 if kn and (t % 1.4) < 0.5 else 0)
    m = W["marta"]; m.face_to(-1.6, 29.6, -3.9, 29.0); m.pose("listen" if lt > d*0.3 else "stand", t, expr="shock" if lt > d*0.3 else "neutral")
    look((0.6, 25.9, 1.6), (-2.2, 29.4, 1.1), 24)

SCENES3D = {"C1": [c1_0, c1_1, c1_2, c1_3, c1_4, c1_5, c1_6, c1_7, c1_8, c1_9, c1_10, c1_11]}
