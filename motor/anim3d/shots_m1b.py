"""M1B · «Caída al Cielo» · Parte 2 (mini-historia 3D de bloques, formato A, serie GRAVEDAD).
Continúa M1A: misma Nora, misma calle (City de noche), misma ventana WIN. Voz única (Juanjo Viral) en 0,15 s.
Nuevos elementos: balcones de la fachada norte, toldo que se rasga, bajante que se suelta, borde de la zona
invertida (partículas) que avanza por la calle, coches aparcados que se levantan al pasar el borde."""
import math, random
import shots_m1a as A
from shots_m1a import (bpy, NORA, G, WIN, look, Env, hide_all, night, fall, shake, rising_cars)
from vox import *
from person import Person, npc_look
from world import Batch, tmat

FPS = 24
TOTAL = 77.8
OFF = 0.15
END = 75.62

# balcones (centro de la losa) en la fachada norte (fachada en y=6.0)
BAL = [(6.3, 5.45, 2.7), (9.5, 5.45, 2.7), (12.7, 5.45, 2.7)]
LAMP = (18.0, 3.4)          # farola de la esquina (fuste)
AWN = (-5.0, 2.3)           # toldo de la mujer (x, z)
PIPE_X = 15.2
EDGE0, EDGE1 = 23.0, 37.0   # borde de la zona invertida (x)
PARK = [(26.0, -2.0), (31.5, 2.0), (36.5, -2.0), (42.0, 2.0), (47.0, -2.0), (52.0, 2.0)]

def build():
    W = A.build()
    C = W["city"]
    # balcones
    W["bal"] = g = group("balcs")
    B = Batch("bal_b", g, 1.0)
    stone = tmat("bslab", "#D8D0C0", 8, 0.06, 41)
    for (x, y, z) in BAL:
        B.add((x, y, z), (1.9, 1.1, 0.14), stone)
        B.add((x, y-0.53, z+0.48), (1.9, 0.06, 0.07), "#3A3A44")
        for i in range(7): B.add((x-0.9+i*0.3, y-0.53, z+0.25), (0.04, 0.04, 0.48), "#3A3A44")
        for sx in (-1, 1): B.add((x+sx*0.93, y, z+0.25), (0.05, 1.05, 0.5), "#3A3A44")
        B.add((x, 5.97, z+1.3), (1.1, 0.05, 1.7), "#4A6A8A")   # puerta acristalada del balcón
    B.done()
    # toldo que se rasga (dos mitades con bisagra en la pared)
    W["awn"] = []
    for i, sx in enumerate((-1, 1)):
        h = group(f"awn{i}", (AWN[0]+sx*0.8, 6.0, AWN[1]+0.1))
        box(f"awn_p{i}", (0, -0.65, 0), (1.6, 1.3, 0.07), mat(["#2E7D6A", "#2E7D6A"][i]), h)
        for k in range(4): box(f"awn_s{i}{k}", (-0.6+k*0.4, -0.65, 0.04), (0.18, 1.3, 0.01), mat("#F0EADA"), h)
        W["awn"].append(h)
    # bajante (canalón) que se suelta
    W["pipe"] = []
    for k in range(5):
        h = group(f"pipe{k}", (PIPE_X, 5.85, k*1.4))
        box(f"pipe_s{k}", (0, 0, 0.7), (0.26, 0.26, 1.4), mat("#C07A40"), h)
        box(f"pipe_c{k}", (0, 0.05, 1.3), (0.24, 0.12, 0.08), mat("#5A5E66"), h)
        W["pipe"].append(h)
    # partículas del borde (hojas y papeles)
    W["dust"] = []
    r = random.Random(5)
    for i in range(60):
        c = r.choice(("#E0A040", "#F0EADA", "#C86A30", "#A8C060"))
        d = box(f"dust{i}", (0, 0, 0), (0.12, 0.09, 0.02), mat(c))
        W["dust"].append((d, r.random(), r.random(), r.random()))
    # coches aparcados más allá del borde
    W["park"] = [car_ for car_ in W["cars"]]
    return W

def hide2(W):
    hide_all(W)
    for k in ("bal",): show(W[k], False)
    for h in W["awn"] + W["pipe"]: show(h, False)
    for d, *_ in W["dust"]: hid(d, True)

def night2(W):
    night(W)
    show(W["bal"], True)
    for h in W["awn"] + W["pipe"]: show(h, True)
    C = W["city"]
    for i, p in enumerate(C.parked): show(p, False)     # en la zona invertida ya no queda ningún coche aparcado
    for h in W["awn"]: h.rotation_euler = (0, 0, 0)
    for k, h in enumerate(W["pipe"]): h.location = (PIPE_X, 5.85, k*1.4); h.rotation_euler = (0, 0, 0)
    W["frame"].location = (0, -0.12, 0)

def edge_x(T):
    return lerp(EDGE0, EDGE1, eio(clamp((T-62.0)/9.0)))

def parked_cars(W, T):
    """coches aparcados normales más allá del borde; cuando el borde los alcanza, caen hacia el cielo"""
    ex = edge_x(T)
    for i, c in enumerate(W["cars"]):
        x, y = PARK[i]; show(c, True)
        # momento en que el borde pasa por x
        if x <= EDGE0: tp = -99
        elif x >= EDGE1: tp = 1e9
        else:
            tp = 1e9
            for j in range(200):
                tt = 62.0 + j*0.05
                if edge_x(tt) >= x: tp = tt; break
        z = fall(T, tp+0.15)*0.45 if T > tp else 0.0
        sp = max(0, T-tp)
        c.location = (x, y, z)
        c.rotation_euler = (0.08*sp*math.sin(i+1), 0.1*sp*math.cos(i), (0 if y < 0 else math.pi) + 0.05*sp)
        if T > tp and sp < 0.5:
            c.location = (x + 0.02*math.sin(T*70), y, z + 0.03*abs(math.sin(T*50)))

def edge_dust(W, T):
    ex = edge_x(T)
    for d, a, b, c in W["dust"]:
        hid(d, False)
        x = ex + (a-0.5)*1.2 + 0.3*math.sin(T*1.3+b*9)
        y = -6 + b*12
        z = ((c*6.0 + T*(0.6+0.8*a)) % 6.0)
        d.location = (x, y, z); d.rotation_euler = (T*3*a, T*2*b, T*c)

def hang(N, hx, hy, hz, face=0.0, straight=True, sway=0.0, T=0.0):
    """Nora colgada (gravedad hacia arriba): manos en (hx,hy,hz), cuerpo hacia el cielo. face 0 = mira a la pared (+Y)"""
    N.show(True)
    el = 0.12 if straight else 1.35
    z = hz + (1.85 if straight else 1.58)
    N.root.location = (hx, hy, z)
    N.root.rotation_euler = (math.pi + sway, 0, math.radians(face))
    for sx in (-1, 1):
        N.arm(sx, fwd=math.pi-0.15 - (0.55 if not straight else 0.0), side=0.22, elbow=el)
        N.fingers(sx, 0.9, 1.2)
    N.leg(-1, 0.25+0.15*math.sin(T*1.7), 0.35); N.leg(1, 0.05+0.1*math.sin(T*1.9+1), 0.15)

def falling_people(W, T, n=8, seed=0, xc=0.0, yc=0.0, z0=6.0, z1=45.0, speed=1.0):
    for i, p in enumerate(W["npc"][:n]):
        r = random.Random(i*7+seed)
        ph = (r.random() + T*0.04*speed*(0.7+0.6*r.random())) % 1.0
        z = lerp(z0, z1, ph**1.6)
        p.show(True)
        p.place(xc + r.uniform(-9, 9), yc + r.uniform(-5, 5), r.uniform(0, 360), z)
        p.root.rotation_euler = (0.9*math.sin(T*0.7+i), 0.7*math.cos(T*0.6+i), r.uniform(0, 6) + 0.3*T)
        for sx in (-1, 1):
            p.arm(sx, fwd=2.3+0.4*math.sin(T*7+i+sx), side=0.7, elbow=0.4); p.leg(sx, fwd=0.4*math.sin(T*6+i*sx), knee=0.6)
        p.face(T, "scared", (0, -0.6))

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

wx, wy, wz = WIN
GZ = wz - 1.15          # alféizar (donde se agarra al empezar)
NX = wx + 0.5           # x de Nora en la ventana (como al final de M1A)

# ------------------------------------------------------------------ planos
@shot(0.0, 3.95)
def s1(W, T, M):        # gancho: colgada del marco, mirando hacia el cielo (contrapicado desde la calle)
    night2(W); k = T/3.95
    N = W["nora"]
    W["frame"].location = (0.02*math.sin(T*50), -0.12, 0.02*abs(math.sin(T*9)))
    hang(N, NX, wy-0.38, GZ, 0, True, 0.03*math.sin(T*2.2), T)
    N.face(T, "scared", (0, 0.9))
    rising_cars(W, T+6.0, 4, 0.0, 51, xc=4.0)
    sx_, sy_, sz_ = shake(T, 0.012)
    look(lerpv((wx-1.2+sx_, wy-3.6+sy_, GZ-1.6), (wx-0.4+sx_, wy-2.6+sy_, GZ-1.2), eio(k)), (NX, wy-0.4, lerp(GZ+1.2, GZ+2.2, eio(k))), 20)
    M["grade"] = "night"

@shot(3.95, 6.6)
def s2(W, T, M):        # plano general: la ventana, el balcón de abajo… y las nubes «abajo» (cámara girada)
    night2(W); k = (T-3.95)/2.65
    N = W["nora"]
    W["frame"].location = (0.025*math.sin(T*50), -0.12, 0.03*abs(math.sin(T*7)))
    hang(N, NX, wy-0.38, GZ, 0, True, 0.04*math.sin(T*2), T)
    N.face(T, "worried", (0.6, -0.5))
    falling_people(W, T, 4, 3, xc=4, yc=-2, z0=9, z1=40)
    b = BAL[0]
    look(lerpv((8.6, 0.2, 2.2), (9.4, -0.6, 2.6), eio(k)), ((wx+b[0])/2, 5.5, (GZ+b[2])/2+0.4), 20, roll=math.pi)
    M["grade"] = "night"

@shot(6.6, 8.3)
def s3(W, T, M):        # el marco se suelta
    night2(W); k = T-6.6
    N = W["nora"]
    lift = 0.0 if k < 0.5 else fall(T, 6.6+0.5)*0.6
    W["frame"].location = (0.03*math.sin(T*60), -0.12-0.15*clamp((k-0.5)*2), lift)
    W["frame"].rotation_euler = (0.25*clamp(k-0.5), 0, 0.1*clamp(k-0.5))
    if k < 0.9:
        hang(N, NX, wy-0.38, GZ+lift, 0, True, 0.05, T)
    else:   # se impulsa hacia el balcón de abajo
        u = eio(clamp((k-0.9)/0.8)); b = BAL[0]
        hang(N, lerp(NX, b[0]-0.3, u), lerp(wy-0.38, b[1]-0.75, u), lerp(GZ, b[2]-0.07, u) + 0.5*math.sin(math.pi*u), 0, True, -0.4*math.sin(math.pi*u), T)
    N.face(T, "shock" if k > 0.4 else "scared", (0, 0.9))
    sx_, sy_, sz_ = shake(T, 0.03 if k > 0.4 else 0.01)
    look((wx+0.6+sx_, 1.4+sy_, GZ-0.3+sz_), (wx+0.8, wy-0.3, GZ+0.8), 22)
    M["grade"] = "night"

@shot(8.3, 12.4)
def s4(W, T, M):        # se lanza hacia el balcón de abajo (que ahora está encima)
    night2(W); k = (T-8.3)/4.1
    N = W["nora"]; b = BAL[0]
    W["frame"].location = (0, -0.4, 1.0 + fall(T, 7.0)*0.6); W["frame"].rotation_euler = (0.5, 0, 0.2)
    u = eio(clamp(k/0.55))
    hx = lerp(NX, b[0]-0.3, u); hy = lerp(wy-0.38, b[1]-0.75, u); hz = lerp(GZ, b[2]-0.07, u) + 0.6*math.sin(math.pi*u)
    hang(N, hx, hy, hz, 0, True, -0.6*math.sin(math.pi*u), T)
    if k < 0.55:
        for sx in (-1, 1): N.arm(sx, fwd=math.pi-0.2-0.4*math.sin(math.pi*u), side=0.4, elbow=0.2)
    N.face(T, "scared" if k < 0.55 else "worried", (0.3, 0.8))
    look(lerpv((b[0]+2.6, b[1]-4.6, b[2]-1.4), (b[0]+1.8, b[1]-4.2, b[2]-1.0), eio(k)), (lerp(wx, b[0], u), 5.0, lerp(GZ+0.6, b[2]+0.7, u)), 22)
    M["grade"] = "night"

@shot(12.4, 16.6)
def s5(W, T, M):        # lo atrapa con una mano… el marco sale disparado hacia las nubes
    night2(W); k = T-12.4
    N = W["nora"]; b = BAL[0]
    hang(N, b[0]-0.3, b[1]-0.75, b[2]-0.07, 0, True, 0.12*math.sin(T*2.5)*math.exp(-k*0.4), T)
    N.arm(1, fwd=1.4+0.3*math.sin(T*3), side=0.9, elbow=0.4)          # la otra mano suelta (una sola mano)
    N.face(T, "scared", (0, -0.9) if k > 1.4 else (0, 0.9))
    fz = 1.0 + fall(T, 7.0)*0.6
    W["frame"].location = (0, -0.4, fz); W["frame"].rotation_euler = (0.5+0.4*(T-7), 0.2*(T-7), 0.2)
    if k < 1.4:
        look((b[0]+1.4, b[1]-2.0, b[2]-0.5), (b[0]-0.3, b[1]-0.75, b[2]+0.3), 26, fstop=2.2)
    else:
        kk = eio((k-1.4)/2.8)
        fwz = WIN[2] + min(fz, 55)
        look((b[0]+1.8, b[1]-3.2, b[2]-0.4), (wx, wy-0.4, lerp(b[2]+2.0, min(fwz, 50.0), kk)), lerp(24, 30, kk))
    M["grade"] = "night"

@shot(16.6, 26.4)
def s6(W, T, M):        # REGLA #3: brazos estirados (primero doblados, temblando; luego estirados)
    night2(W); k = T-16.6
    N = W["nora"]; b = BAL[0]
    straight = k > 4.0 or k < 1.6
    tremble = 0.02*math.sin(T*40) if (1.6 <= k <= 4.0) else 0.0
    hang(N, b[0]-0.3, b[1]-0.75, b[2]-0.07+tremble, 0, straight, 0.03*math.sin(T*1.5), T)
    N.face(T, "angry" if not straight else "worried", (0, 0.4))
    a = lerp(-0.7, 0.5, eio(k/9.8))
    cx, cy, cz = b[0]-0.3, b[1]-0.75, b[2]+0.9
    look((cx+math.sin(a)*3.0, cy-math.cos(a)*3.0, cz-0.4), (cx, cy, cz), 24, roll=math.pi)
    M["grade"] = "night"; M["chip"] = 1

@shot(26.4, 32.0)
def s7(W, T, M):        # de balcón en balcón… hasta la farola de la esquina
    night2(W); k = T-26.4
    N = W["nora"]
    # 0–3.6 s: balcones 0→1→2 (saltos cortos), 3.6–5.6: cruza a la farola
    segs = [(BAL[0][0]-0.3, BAL[0][1]-0.75, BAL[0][2]-0.07), (BAL[1][0]-0.3, BAL[1][1]-0.75, BAL[1][2]-0.07),
            (BAL[2][0]-0.3, BAL[2][1]-0.75, BAL[2][2]-0.07), (LAMP[0]-6.0, LAMP[1]+0.15, 1.1)]
    s = min(2, int(k/1.6)); u = eio(clamp((k - s*1.6)/1.0))
    p0, p1 = segs[s], segs[s+1]
    hx, hy, hz = lerpv(p0, p1, u); hz += 0.4*math.sin(math.pi*u)
    hang(N, hx, hy, hz, 0 if s < 2 else lerp(0, 180, u), True, -0.4*math.sin(math.pi*u), T)
    N.face(T, "angry", (0.6, 0.3))
    falling_people(W, T, 3, 9, xc=10, yc=-2, z0=8, z1=40)
    look((lerp(4.0, 12.0, eio(k/5.6)), -4.6, 1.2), (lerp(7.0, 12.0, eio(k/5.6)), 4.6, 3.6), 18)
    M["grade"] = "night"

@shot(32.0, 37.4)
def s8(W, T, M):        # bajo sus pies, en el cielo, la gente sigue cayendo hacia arriba (POV desde la farola)
    night2(W); k = (T-32.0)/5.4
    N = W["nora"]; lx, ly = LAMP[0]-6.0, LAMP[1]
    hang(N, lx, ly+0.15, 1.1, 180, True, 0.03*math.sin(T), T)
    N.face(T, "worried", (0, -0.9))
    falling_people(W, T, 10, 17, xc=lx, yc=0, z0=7, z1=50, speed=0.7)
    rising_cars(W, T-28.0, 3, 0.0, 61, xc=lx)
    look((lx+0.5, ly-0.8, lerp(4.6, 5.4, eio(k))), (lx+lerp(-2, 2, k), ly-2.0, 40.0), 16)
    M["grade"] = "night"

@shot(37.4, 40.9)
def s9(W, T, M):        # una mujer se agarra a un toldo… y el toldo se rasga
    night2(W); k = T-37.4
    p = W["npc"][1]; ax, az = AWN
    tear = clamp((k-2.0)/0.4)
    for i, h in enumerate(W["awn"]):
        sx = (-1, 1)[i]
        h.rotation_euler = (-1.2*eio(tear), 0.25*sx*tear, 0)
    hz = az - 0.03 if tear < 0.3 else az + fall(T, 37.4+2.25)*0.7
    p.show(True)
    p.root.location = (ax+0.4, 4.55, hz+1.7); p.root.rotation_euler = (math.pi+0.05*math.sin(T*2), 0, 0)
    for sx in (-1, 1):
        p.arm(sx, fwd=math.pi-0.15 if tear < 0.3 else 2.4+0.5*math.sin(T*9+sx), side=0.2 if tear < 0.3 else 0.8, elbow=0.1)
        p.leg(sx, 0.3*math.sin(T*3+sx), 0.4)
    p.face(T, "scared", (0, 0.9) if tear < 0.3 else (0, -0.9))
    sx_, sy_, sz_ = shake(T, 0.02 if 2.0 < k < 2.6 else 0)
    if k < 2.4:
        look((ax+2.6+sx_, 1.2+sy_, 1.2+sz_), (ax+0.2, 5.0, az+0.6), 24)
    else:
        kk = eio((k-2.4)/1.1)
        look((ax+2.6, 1.2, 1.2), (ax+0.4, 4.6, lerp(az+1.0, min(hz+1.0, 20), kk)), lerp(24, 28, kk))
    M["grade"] = "night"

@shot(40.9, 45.9)
def s10(W, T, M):       # REGLA #4: prueba el agarre con un tirón
    night2(W); k = T-40.9
    N = W["nora"]; lx, ly = LAMP
    hang(N, lx, ly+0.18, 1.5, 180, True, 0.02*math.sin(T), T)
    tug = k > 2.6 and k < 4.0
    if tug:
        jj = 0.12*abs(math.sin((k-2.6)*9))
        N.root.location.z += jj
        N.arm(1, fwd=math.pi-0.3, side=0.15, elbow=0.6*abs(math.sin((k-2.6)*9)))
    else:
        N.arm(1, fwd=math.pi-0.25, side=0.15, elbow=0.1)
    N.face(T, "angry" if tug else "worried", (0.3, 0.6))
    look(lerpv((lx-1.6, ly-2.2, 1.0), (lx-1.1, ly-1.6, 1.3), eio(k/5.0)), (lx, ly+0.1, 2.1), 24, fstop=2.4, roll=math.pi)
    M["grade"] = "night"; M["chip"] = 1

@shot(45.9, 49.55)
def s11(W, T, M):       # toldos, canalones y antenas no aguantan: la bajante se suelta
    night2(W); k = T-45.9
    for j, h in enumerate(W["pipe"]):
        tj = 0.6 + (4-j)*0.35
        if k > tj:
            u = k - tj
            h.location = (PIPE_X, 5.85 - 0.3*u, j*1.4 + fall(T, 45.9+tj)*0.5)
            h.rotation_euler = (-0.5*u, 0.3*u*math.sin(j), 0)
    for i, h in enumerate(W["awn"]): h.rotation_euler = (-1.2, 0.25*(-1, 1)[i], 0)
    look((PIPE_X-3.2, 1.0, 1.0), (PIPE_X, 5.8, lerp(3.0, 7.0, eio(k/3.6))), 22)
    M["grade"] = "night"; M["chip"] = 1

@shot(49.55, 52.0)
def s12(W, T, M):       # farolas y barandillas ancladas, sí (Nora firme en la farola)
    night2(W); k = (T-49.55)/2.45
    N = W["nora"]; lx, ly = LAMP
    hang(N, lx, ly+0.18, 1.5, 180, True, 0.02*math.sin(T), T)
    N.face(T, "angry", (0, 0.6))
    a = lerp(0.6, -0.2, eio(k))
    look((lx+math.sin(a)*4.4, ly-math.cos(a)*4.4, 0.8), (lx, ly, 2.6), 20, roll=math.pi)
    M["grade"] = "night"; M["chip"] = 1

@shot(52.0, 58.35)
def s13(W, T, M):       # final de la calle: en la manzana siguiente, coches aparcados. Normales.
    night2(W); k = T-52.0
    N = W["nora"]; lx, ly = LAMP
    hang(N, lx, ly+0.18, 1.5, 180 if k < 1.5 else lerp(180, 270, eio((k-1.5)/1.2)), True, 0.02*math.sin(T), T)
    N.face(T, "shock" if k > 3.4 else "worried", (0.0, 0.5))
    parked_cars(W, T); edge_dust(W, T)
    if k < 3.0:
        look(lerpv((lx-3.0, ly-3.6, 2.2), (lx-3.4, ly-2.6, 2.8), eio(k/3.0)), (lx+4.0, 0.5, 1.6), 24)
    else:
        kk = eio((k-3.0)/3.35)
        look(lerpv((lx-1.0, ly-1.0, 3.1), (lx+0.5, ly-1.0, 2.6), kk), (lx+12.0, 0.0, lerp(1.4, 0.8, kk)), lerp(24, 34, kk))
    M["grade"] = "night"

@shot(58.35, 61.35)
def s14(W, T, M):       # ¡hay un borde! (primer plano de Nora, cámara girada para verla «derecha»)
    night2(W); k = (T-58.35)/3.0
    N = W["nora"]; lx, ly = LAMP
    hang(N, lx, ly+0.18, 1.5, 270, True, 0.02*math.sin(T), T)
    N.face(T, "happy", (-0.8, 0.3))
    parked_cars(W, T); edge_dust(W, T)
    hz = 1.5 + 1.85 - 1.45
    look(lerpv((lx+1.9, ly-0.8, hz-0.1), (lx+1.6, ly-0.6, hz-0.05), eio(k)), (lx, ly+0.18, hz+0.1), 24, fstop=2.0, roll=math.pi)
    M["grade"] = "night"

@shot(61.35, 66.75)
def s15(W, T, M):       # el borde se mueve: un coche empieza a levantarse, luego otro
    night2(W); k = (T-61.35)/5.4
    parked_cars(W, T); edge_dust(W, T)
    ex = edge_x(T)
    look(lerpv((ex-7.0, -4.4, 1.3), (ex-5.0, -4.6, 2.2), eio(k)), (ex+3.0, 0.0, lerp(0.8, 2.0, eio(k))), 20)
    M["grade"] = "night"

@shot(66.75, 71.3)
def s16(W, T, M):       # la zona invertida avanza, calle a calle (grúa alta)
    night2(W); k = (T-66.75)/4.55
    parked_cars(W, T); edge_dust(W, T)
    N = W["nora"]; lx, ly = LAMP
    hang(N, lx, ly+0.18, 1.5, 270, True, 0.02*math.sin(T), T); N.face(T, "worried", (-0.8, 0.0))
    falling_people(W, T, 5, 23, xc=20, yc=0, z0=8, z1=40)
    ex = edge_x(T)
    look(lerpv((lx-6.0, -1.0, 12.0), (lx-8.0, -1.0, 20.0), eio(k)), (lerp(lx+8.0, ex+4.0, eio(k)), 0.0, 0.0), lerp(22, 18, eio(k)))
    M["grade"] = "night"

@shot(71.3, END)
def s17(W, T, M):       # Nora tendrá que correr colgada del mundo… más rápido que ella
    night2(W); k = (T-71.3)/(END-71.3)
    parked_cars(W, T); edge_dust(W, T)
    N = W["nora"]; lx, ly = LAMP
    hang(N, lx, ly+0.18, 1.5, 270, True, 0.02*math.sin(T), T)
    N.face(T, "angry", (-0.9, 0.2))
    N.arm(1, fwd=math.pi-0.25+0.6*eio(clamp((k-0.6)/0.4)), side=0.3, elbow=0.2)   # suelta una mano para ir a por la siguiente
    hz = 1.5 + 0.4
    look(lerpv((lx-2.2, ly-2.4, hz+0.3), (lx-5.0, ly-4.2, hz+1.2), eio(k)), (lx+lerp(0.0, 3.0, eio(k)), ly-0.2, hz+0.6), lerp(26, 20, eio(k)), roll=math.pi)
    M["grade"] = "night"

@shot(END, TOTAL+0.1)
def s18(W, T, M):       # CONTINUARÁ (negro)
    M["black"] = 1

def frame(W, T):
    hide2(W)
    M = {"T": T}
    for t0, t1, f in SH:
        if t0 <= T < t1:
            f(W, T, M); M["shot"] = f.__name__; break
    if "black" not in M:
        cam = bpy.context.scene.camera.location
        for p in W["npc"]:
            if DES.get(p.root.name, (None, True))[1]: continue
            l = p.root.location
            if (l - cam).length < 1.6: p.show(False)
    apply_vis()
    return M
