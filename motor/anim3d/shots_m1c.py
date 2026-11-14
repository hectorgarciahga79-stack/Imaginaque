"""M1C · «Caída al Cielo» · Parte 3 (FINAL) (mini-historia 3D de bloques, formato A, serie GRAVEDAD).
Continúa M1B: misma Nora, misma calle (City de noche), farola LAMP=(18,3.4) y borde de la zona invertida en x≈37.
Nuevo: barandilla de la fachada norte (x 24,5–35,5), farola final x=36, borde que se frena en x=38,5, caída al lado
normal con aterrizaje y rodada (REGLA #5), torre alta (azotea) en x=50 y ciudades lejanas perdiendo coches."""
import math, random
import shots_m1b as B
import shots_m1a as A
from vox import *
from shots_m1a import bpy, NORA, G, look, Env, fall, shake
from shots_m1b import hang, falling_people, night2, hide2
from person import Person, npc_look
from world import Batch, tmat, building, car

FPS = 24
OFF = 0.15
END = 71.9
TOTAL = 74.1

LAMPX = [18.0, 24.0, 30.0, 36.0]
LY = 3.4
RAIL = (24.5, 35.5, 5.72, 1.2)     # x0, x1, y, z de la barandilla
EDGE_STOP = 38.5
PARK = [(43.0, -2.0), (55.0, 2.0), (52.5, -2.0), (60.0, 2.0)]
TOWER = (50.0, 9.5, 8.0, 7.0, 14)  # x0, y0, w, d, plantas
TH = 14*1.6+0.4                    # altura de la azotea
ROOF = (47.2, 6.9, TH+0.3)

def edge_x(T):
    return lerp(37.0, EDGE_STOP, eio(clamp(T/22.0)))

def build():
    W = B.build()
    # barandilla metálica en la fachada norte
    W["rail"] = g = group("rail_g")
    R = Batch("rail_b", g, 1.0)
    x0, x1, ry, rz = RAIL
    R.add(((x0+x1)/2, ry, rz), (x1-x0, 0.08, 0.08), "#3A3A44")
    for i in range(12):
        x = x0 + i*(x1-x0)/11
        R.add((x, ry+0.14, rz), (0.06, 0.28, 0.06), "#3A3A44")
    R.done()
    W["wall"] = g = group("wall_g")
    Wb = Batch("wall_b", g, 1.0); Wb.add((45.0, 5.0, 0.5), (1.6, 1.4, 1.0), tmat("lwall", "#B8B0A0", 8, 0.08, 61)); Wb.done()
    # torre alta al final de la calle (la azotea)
    W["tower"] = g = group("tower_g")
    T = Batch("tower_b", g, 1.0)
    x0, y0, w, d, fl = TOWER
    building(T, x0, y0, w, d, fl, "#9AA8B8", 307, -1)
    T.add((x0, y0-d/2+0.1, TH+0.6), (w, 0.12, 0.6), "#5A5E66")      # pretil delantero
    T.add((x0-w/2+0.1, y0, TH+0.6), (0.12, d, 0.6), "#5A5E66")
    T.add((x0+1.5, y0+1.0, TH+1.0), (1.6, 1.6, 1.4), "#7A7E86")       # caseta
    T.done()
    # ciudades lejanas (horizonte) y sus coches que caen hacia las nubes
    W["far"] = g = group("far_g")
    F = Batch("far_b", g, 4.0)
    r = random.Random(77)
    W["far_c"] = [(-150.0, 30.0), (-175.0, -60.0), (-120.0, 115.0)]
    for (cx, cy) in W["far_c"]:
        for i in range(26):
            bx, by = cx + r.uniform(-28, 28), cy + r.uniform(-16, 16)
            h = r.uniform(6, 30)
            F.add((bx, by, h/2), (r.uniform(5, 10), r.uniform(5, 10), h), r.choice(("#2E3650", "#343C58", "#28304A")))
            for j in range(int(h/4)):
                if r.random() < 0.55: F.add((bx + r.uniform(-2, 2), by-0.1 + r.uniform(-1, 1)*0, 2+j*3.6), (1.6, 11, 1.0), "#FFE7A0")
    F.done()
    W["far_cars"] = []
    for i in range(18):
        cg = box(f"farcar{i}", (0, 0, 0), (3.6, 1.7, 1.3), mat(r.choice(("#D23A2E", "#E0C040", "#3A6AA8", "#E0E0D8", "#5A8A5A"))))
        W["far_cars"].append((cg, r.random(), r.random()))
    return W

def hide3(W):
    hide2(W)
    for k in ("rail", "tower", "far", "wall"): show(W[k], False)
    for c, *_ in W["far_cars"]: hid(c, True)

def night3(W):
    night2(W)
    for k in ("rail", "tower", "far", "wall"): show(W[k], True)

def parked(W, T, tremble=0.0):
    for i, c in enumerate(W["cars"][:4]):
        x, y = PARK[i]; show(c, True)
        c.location = (x, y, 0.0); c.rotation_euler = (0, 0, 0 if y < 0 else math.pi)
        if i == 0 and tremble:
            c.location = (x + 0.03*tremble*math.sin(T*63), y, 0.04*tremble*abs(math.sin(T*47)))
            c.rotation_euler = (0.02*tremble*math.sin(T*31), 0, 0)

def edge_dust(W, T, ex=None):
    ex = edge_x(T) if ex is None else ex
    for d, a, b, c in W["dust"]:
        hid(d, False)
        x = ex + (a-0.5)*1.2 + 0.3*math.sin(T*1.3+b*9)
        d.location = (x, -6 + b*12, ((c*6.0 + T*(0.6+0.8*a)) % 6.0)); d.rotation_euler = (T*3*a, T*2*b, T*c)

def far_cars(W, T):
    for i, (c, a, b) in enumerate(W["far_cars"]):
        cx, cy = W["far_c"][i % 3]
        ph = (a + T*0.08) % 1.0
        hid(c, False)
        c.location = (cx + (b-0.5)*40, cy + (a-0.5)*24, 4 + 70*ph**1.7)
        c.rotation_euler = (T*0.7*a, T*0.5*b, i)

def rail_hang(N, x, T, step=0.0):
    """colgada de la barandilla (gravedad hacia arriba), mira a la pared; step 0..1 = brazo que avanza"""
    hang(N, x, RAIL[2]-0.15, RAIL[3], 0, True, 0.02*math.sin(T*2), T)
    s = math.sin(math.pi*step)
    N.arm(1, fwd=math.pi-0.15, side=0.22+0.55*s, elbow=0.12+0.3*s)

def lamp_hang(N, x, T, face=270):
    hang(N, x, LY+0.18, 1.5, face, True, 0.02*math.sin(T), T)

def arc(N, p0, p1, u, face, T, h=0.5):
    hx, hy, hz = lerpv(p0, p1, u); hz += h*math.sin(math.pi*u)
    hang(N, hx, hy, hz, face, True, -0.4*math.sin(math.pi*u), T)

L = 1.62   # pies (raíz) → manos, colgada con los brazos estirados (escala 0,85)

SH = []
def shot(t0, t1):
    def deco(f): SH.append((t0, t1, f)); return f
    return deco

# ------------------------------------------------------------------ planos
@shot(0.0, 4.8)
def s1(W, T, M):        # gancho: colgada de la farola, el borde se aleja al fondo
    night3(W); k = T/4.8
    N = W["nora"]; lx = LAMPX[0]
    lamp_hang(N, lx, T); N.face(T, "worried", (-0.8, 0.2))
    parked(W, T); edge_dust(W, T)
    falling_people(W, T, 4, 31, xc=lx+4, yc=0, z0=8, z1=40)
    look(lerpv((lx-2.6, LY-2.9, 2.0), (lx-2.0, LY-2.3, 2.2), eio(k)), (lx+lerp(0.8, 2.0, eio(k)), LY-0.3, 2.4), lerp(22, 24, eio(k)), roll=math.pi)
    M["grade"] = "night"

@shot(4.8, 6.6)
def s2(W, T, M):        # cada agarre cuenta (primer plano de las manos en la farola)
    night3(W); k = (T-4.8)/1.8
    N = W["nora"]; lx = LAMPX[0]
    lamp_hang(N, lx, T); N.face(T, "angry", (0, 0.6))
    for sx in (-1, 1): N.fingers(sx, 1.0, 1.4)
    look(lerpv((lx-1.9, LY-1.7, 1.1), (lx-1.6, LY-1.4, 1.15), eio(k)), (lx, LY+0.18, 1.75), 28, fstop=2.8, roll=math.pi)
    M["grade"] = "night"

@shot(6.6, 9.6)
def s3(W, T, M):        # suelta la farola y se lanza a por la siguiente
    night3(W); k = T-6.6
    N = W["nora"]
    p0 = (LAMPX[0], LY+0.18, 1.5); p1 = (LAMPX[1], LY+0.18, 1.5)
    u = eio(clamp((k-0.6)/1.6))
    arc(N, p0, p1, u, 270, T, 0.9)
    N.face(T, "angry" if u < 0.95 else "worried", (0.6, 0.2))
    falling_people(W, T, 3, 41, xc=22, yc=-2, z0=8, z1=40)
    x = lerp(p0[0], p1[0], u)
    look((x-1.2, 0.2, 1.2), (x+0.6, LY+0.2, 2.5), 22, roll=math.pi)
    M["grade"] = "night"

@shot(9.6, 12.4)
def s4(W, T, M):        # una mano… otra… otra más (barandilla)
    night3(W); k = T-9.6
    N = W["nora"]
    st = k/0.9; i = min(2, int(st)); u = st - int(st) if st < 3 else 1.0
    x = RAIL[0] + 0.4 + (i + eio(clamp(u*1.4)))*0.55
    rail_hang(N, x, T, clamp(u*1.4))
    N.face(T, "angry", (0.5, 0.4))
    look((x+2.2, RAIL[2]-1.8, 0.8), (x+0.2, RAIL[2]-0.1, 2.0), 22, roll=math.pi)
    M["grade"] = "night"

@shot(12.4, 18.8)
def s5(W, T, M):        # lo que cae hacia arriba no vuelve: ≈200 km/h en unos 15 s (POV hacia el cielo)
    night3(W); k = T-12.4
    N = W["nora"]; x = RAIL[0]+2.3
    rail_hang(N, x, T); N.face(T, "worried", (0, -0.9))
    c = W["cars"][4]; show(c, True)
    z = 1.0 + fall(T, 12.4-0.6)*0.5
    c.location = (x+1.0, 0.5, z); sp = k; c.rotation_euler = (0.12*sp, 0.18*sp, 0.05*sp)
    falling_people(W, T, 5, 51, xc=x, yc=-1, z0=6, z1=45, speed=0.6)
    look((x+0.6, RAIL[2]-1.4, 3.6), (x+0.8, 0.6, min(z, 52.0)+0.5), lerp(20, 26, eio(k/6.4)))
    M["grade"] = "night"; M["chip"] = 1

@shot(18.8, 23.6)
def s6(W, T, M):        # el borde está a una manzana; los coches de delante tiemblan
    night3(W); k = (T-18.8)/4.8
    N = W["nora"]
    x = lerp(RAIL[0]+3.0, RAIL[1]-0.4, eio(k))
    rail_hang(N, x, T, (k*6) % 1.0); N.face(T, "worried", (0.8, 0.2))
    parked(W, T, tremble=clamp((k-0.4)*3)); edge_dust(W, T)
    if k < 0.5:
        look((x-2.8, 2.0, 1.6), (x+0.8, RAIL[2]-0.2, 2.2), 22, roll=math.pi)
    else:
        kk = eio((k-0.5)*2)
        look(lerpv((40.8, -4.3, 0.9), (41.2, -4.5, 0.85), kk), (43.0, -2.0, 0.7), 18)
    M["grade"] = "night"

@shot(23.6, 27.4)
def s7(W, T, M):        # última farola; al otro lado del borde, el asfalto
    night3(W); k = T-23.6
    N = W["nora"]; lx = LAMPX[3]
    u = eio(clamp(k/0.9))
    arc(N, (RAIL[1]-0.2, RAIL[2]-0.15, RAIL[3]), (lx, LY+0.18, 1.5), u, lerp(0, 270, u), T, 0.4)
    N.face(T, "worried", (0.9, 0.0))
    parked(W, T, 0.6); edge_dust(W, T)
    kk = eio(clamp((k-0.8)/3.0))
    look(lerpv((lx-2.4, LY-2.2, 3.4), (lx-1.8, LY-1.0, 3.6), kk), (lerp(lx, 44.0, kk), lerp(LY, 0.0, kk), lerp(2.4, 0.6, kk)), lerp(22, 26, kk))
    M["grade"] = "night"

@shot(27.4, 29.3)
def s8(W, T, M):        # detrás de ella, el vacío (contrapicado hacia las nubes)
    night3(W); k = (T-27.4)/1.9
    N = W["nora"]; lx = LAMPX[3]
    lamp_hang(N, lx, T); N.face(T, "scared", (0, -0.9))
    falling_people(W, T, 8, 61, xc=30, yc=0, z0=7, z1=50, speed=0.7)
    look((lx-0.4, LY-0.9, lerp(3.4, 3.9, eio(k))), (lx-6.0, LY-3.0, 45.0), 16)
    M["grade"] = "night"

@shot(29.3, 34.2)
def s9(W, T, M):        # REGLA #5: pies y rodillas juntos, un poco dobladas (Nora se prepara)
    night3(W); k = T-29.3
    N = W["nora"]; lx = LAMPX[3]
    lamp_hang(N, lx, T)
    kb = eio(clamp((k-2.2)/1.0))
    for sx in (-1, 1): N.leg(sx, 0.35*kb, 0.75*kb)
    N.face(T, "angry", (0.4, 0.3))
    parked(W, T, 0.3); edge_dust(W, T)
    a = lerp(-0.8, 0.6, eio(k/4.9))
    cx, cy, cz = lx, LY+0.18, 2.4
    look((cx+math.sin(a)*4.0, cy-math.cos(a)*4.0, 1.6), (cx, cy, cz), 22, roll=math.pi)
    M["grade"] = "night"; M["chip"] = 1

@shot(34.2, 39.3)
def s10(W, T, M):       # …y rueda de lado: así el golpe se reparte (demostración en el lado normal)
    night3(W); k = T-34.2
    parked(W, T); edge_dust(W, T)
    p = W["npc"][2]; p.show(True)
    p.root.rotation_mode = 'ZYX'
    wall = (45.0, 5.0)
    if k < 1.2:                                    # en el muro bajo
        p.place(wall[0], wall[1], 90, 1.0); p.idle(T)
        for sx in (-1, 1): p.leg(sx, 0.25, 0.5)
    elif k < 1.7:                                  # cae con pies juntos
        u = (k-1.2)/0.5
        p.place(wall[0]+0.6*u, wall[1], 90, 1.0*(1-u*u)); p.idle(T)
        for sx in (-1, 1): p.leg(sx, 0.4, 0.8); p.arm(sx, fwd=0.6, side=0.3, elbow=0.8)
    else:                                          # toca, flexiona y rueda de lado
        u = clamp((k-1.7)/1.6)
        tip = math.pi/2*eio(clamp(u*2.2)); spin = 2*math.pi*eio(clamp((u-0.35)/0.65))
        p.root.location = (wall[0]+0.6+1.8*eio(u), wall[1], 0.22*clamp(u*3))
        p.root.rotation_euler = (0, tip, math.radians(90)+spin)
        for sx in (-1, 1): p.leg(sx, 0.9*(1-u*0.5), 1.4*(1-u*0.5)); p.arm(sx, fwd=1.2, side=0.2, elbow=1.4)
        if k > 3.6:
            p.root.rotation_mode = 'XYZ'; p.place(wall[0]+2.4, wall[1], 200, 0); p.idle(T)
    p.face(T, "angry", (0, -0.2))
    look((wall[0]+1.4, wall[1]-5.4, 1.3), (wall[0]+1.3, wall[1], 0.6), 26)
    M["grade"] = "night"; M["chip"] = 1

SW0, REL = 39.3, 42.6
def swing_b(T):
    return 0.55*math.sin((T-SW0)*2*math.pi/1.6)*clamp((T-SW0)/1.2)

def nora_free(N, T):
    """tras soltarse: vuela hacia +x, cruza el borde y cae al asfalto (pies primero)"""
    lx = LAMPX[3]; b = swing_b(REL)
    px, pz = lx + L*math.sin(b), 1.5 + L*math.cos(b)
    vx = 3.2; t = T-REL
    tc = (EDGE_STOP - px)/vx
    if t < tc:
        z = pz + 1.2*t + 0.5*G*t*t                       # aún en la zona invertida: sube
    else:
        zc = pz + 1.2*tc + 0.5*G*tc*tc; vc = 1.2 + G*tc
        tt = t-tc; z = zc + vc*tt - 0.5*G*tt*tt          # zona normal: frena y cae
    x = px + vx*t
    flip = eio(clamp((t-tc+0.1)/0.7))                     # pasa de boca abajo a de pie
    return x, z, flip, tc

def land_t():
    lx = LAMPX[3]; b = swing_b(REL); px, pz = lx + L*math.sin(b), 1.5 + L*math.cos(b)
    for j in range(1, 400):
        t = j*0.01; x, z, f, tc = nora_free(None, REL+t)
        if t > tc and z <= 0.0: return REL+t, x
    return REL+1.5, px+4
TL, XL = None, None

def nora_air(N, T):
    x, z, flip, tc = nora_free(N, T)
    N.show(True)
    # cuerpo: raíz en los pies; boca abajo (pi) → de pie (0)
    rx = math.pi*(1-flip)
    zz = z if flip < 0.5 else max(0.0, z - L*0.0)
    N.root.rotation_mode = 'XYZ'
    N.root.location = (x, LY+0.18, max(0.0, zz))
    N.root.rotation_euler = (rx, 0, math.radians(270))
    for sx in (-1, 1):
        N.arm(sx, fwd=2.4+0.3*math.sin(T*9+sx), side=0.6, elbow=0.4); N.leg(sx, 0.35, 0.75)
    return x, z, flip

@shot(39.3, 43.2)
def s11(W, T, M):       # se balancea una vez… dos… y se suelta
    night3(W); k = T-39.3
    N = W["nora"]; lx = LAMPX[3]
    parked(W, T, 0.3); edge_dust(W, T)
    if T < REL:
        b = swing_b(T)
        N.show(True); N.root.rotation_mode = 'XYZ'
        N.root.location = (lx + L*math.sin(b), LY+0.18, 1.5 + L*math.cos(b))
        N.root.rotation_euler = (math.pi, b, math.radians(270))
        for sx in (-1, 1): N.arm(sx, fwd=math.pi-0.15, side=0.22, elbow=0.12); N.leg(sx, 0.35, 0.75)
        N.face(T, "angry", (0.6, 0.2))
    else:
        nora_air(N, T); N.face(T, "scared", (0.6, 0.0))
    look((lx-0.6, -1.6, 1.5), (lx+0.4, LY, 2.6), 22)
    M["grade"] = "night"

@shot(43.2, 45.2)
def s12(W, T, M):       # cruza el borde… y cae. Hacia abajo, por fin
    night3(W)
    N = W["nora"]
    parked(W, T); edge_dust(W, T)
    tl, xl = land_t()
    if T < tl:
        x, z, flip = nora_air(N, T); N.face(T, "shock", (0.6, -0.4))
    else:
        x = xl; landing(N, T, tl, xl)
    nx, nz = (x, z) if T < tl else (xl, 0.5)
    look((EDGE_STOP-1.0, -2.6, 1.2), (nx, LY, max(0.8, min(nz+0.6, 6.0))), 20)
    M["grade"] = "night"

def landing(N, T, tl, xl):
    """toca con pies juntos, flexiona y rueda de lado por el asfalto"""
    u = T - tl
    N.show(True)
    if u < 0.25:
        N.root.rotation_mode = 'XYZ'; N.place(xl, LY+0.18, 270, 0)
        N.idle(T); N.hips.location.z = 0.78*N.s - 0.25*eio(u/0.25)
        for sx in (-1, 1): N.leg(sx, 0.9*eio(u/0.25), 1.6*eio(u/0.25)); N.arm(sx, fwd=0.8, side=0.4, elbow=0.8)
        N.face(T, "scared", (0.5, -0.3))
    else:
        r = clamp((u-0.25)/1.6)
        N.idle(T); N.root.rotation_mode = 'ZYX'
        tip = math.pi/2*eio(clamp(r*2.5)); spin = 2*math.pi*eio(clamp((r-0.25)/0.75))
        N.root.location = (xl + 1.8*eio(r), LY+0.18 - 0.4*r, 0.22*clamp(r*3))
        N.root.rotation_euler = (0, tip, math.radians(270)+spin)
        for sx in (-1, 1): N.leg(sx, 0.7*(1-r), 1.2*(1-r)); N.arm(sx, fwd=1.3, side=0.2, elbow=1.5)
        N.face(T, "scared" if r < 0.8 else "worried", (0, 0))

@shot(45.2, 48.55)
def s13(W, T, M):       # rueda por el asfalto (plano bajo)
    night3(W); k = (T-45.2)/3.35
    N = W["nora"]
    parked(W, T); edge_dust(W, T)
    tl, xl = land_t()
    landing(N, max(T, tl), tl, xl)
    look(lerpv((xl+0.8, LY-3.6, 0.7), (xl+1.8, LY-3.2, 0.55), eio(k)), (xl+lerp(0.6, 1.9, eio(k)), LY, 0.35), 24)
    M["grade"] = "night"

@shot(48.55, 51.05)
def s14(W, T, M):       # ¡lo ha conseguido! suelo de verdad (en cuclillas, la mano en el asfalto)
    night3(W); k = (T-48.55)/2.5
    N = W["nora"]; tl, xl = land_t(); x = xl+1.8
    parked(W, T); edge_dust(W, T)
    N.show(True); N.root.rotation_mode = 'XYZ'; N.place(x, LY-0.22, 340, 0)
    N.idle(T); N.hips.location.z = 0.78*N.s - 0.32
    for sx in (-1, 1): N.leg(sx, 1.2, 2.0)
    N.arm(-1, fwd=0.7, side=0.15, elbow=0.2); N.arm(1, fwd=0.3+0.7*eio(clamp((k-0.5)*2)), side=0.6, elbow=0.4)
    N.face(T, "happy", (0.0, 0.3*math.sin(T*2)))
    look(lerpv((x-1.0, LY-2.5, 0.8), (x-0.7, LY-2.0, 0.75), eio(k)), (x, LY-0.22, 0.75), 26, fstop=2.2)
    M["grade"] = "night"

@shot(51.05, 55.25)
def s15(W, T, M):       # sube a la azotea más alta (grúa por la fachada de la torre)
    night3(W); k = (T-51.05)/4.2
    N = W["nora"]; rx, ry, rz = ROOF
    parked(W, T); edge_dust(W, T)
    N.show(True); N.root.rotation_mode = 'XYZ'; N.place(rx, ry, 270, rz-0.3); N.idle(T); N.face(T, "angry", (0.6, 0))
    z = lerp(2.0, rz+1.2, eio(k))
    look((rx-7.5, ry-9.0, z), (rx+0.5, ry+0.5, lerp(z+1.5, rz+0.6, eio(k))), lerp(18, 26, eio(k)))
    M["grade"] = "night"

@shot(55.25, 58.0)
def s16(W, T, M):       # y entonces lo ve (primer plano, se le cae el alma)
    night3(W); k = (T-55.25)/2.75
    N = W["nora"]; rx, ry, rz = ROOF
    N.show(True); N.root.rotation_mode = 'XYZ'; N.place(rx, ry, 270, rz-0.3); N.idle(T)
    N.face(T, "shock" if k > 0.35 else "worried", (-0.6, 0.1))
    far_cars(W, T)
    hz = rz-0.3+1.45
    look(lerpv((rx-1.4, ry-1.3, hz), (rx-1.1, ry-1.0, hz+0.05), eio(k)), (rx, ry, hz+0.05), 30, fstop=2.0)
    M["grade"] = "night"

@shot(58.0, 61.9)
def s17(W, T, M):       # en el horizonte, otras ciudades pierden sus coches hacia las nubes
    night3(W); k = (T-58.0)/3.9
    N = W["nora"]; rx, ry, rz = ROOF
    N.show(True); N.root.rotation_mode = 'XYZ'; N.place(rx, ry, 270, rz-0.3); N.idle(T); N.face(T, "shock", (0, 0.1))
    far_cars(W, T)
    falling_people(W, T, 4, 71, xc=20, yc=0, z0=10, z1=45)
    c = W["far_c"][0]
    look((rx+1.6, ry+0.6, rz+1.6), (lerp(c[0], c[0]+10, k), lerp(c[1]-10, c[1]+5, eio(k)), 22.0), lerp(32, 40, eio(k)))
    M["grade"] = "night"

@shot(61.9, 67.0)
def s18(W, T, M):       # no era su calle: el planeta entero, girándose poco a poco (grúa altísima + giro)
    night3(W); k = (T-61.9)/5.1
    N = W["nora"]; rx, ry, rz = ROOF
    N.show(True); N.root.rotation_mode = 'XYZ'; N.place(rx, ry, 270, rz-0.3); N.idle(T); N.face(T, "worried", (0, 0.3))
    far_cars(W, T); edge_dust(W, T, EDGE_STOP)
    falling_people(W, T, 6, 81, xc=10, yc=0, z0=8, z1=45)
    kk = eio(k)
    look((lerp(rx+6, rx+40, kk), lerp(ry-14, ry-70, kk), lerp(rz+4, rz+70, kk)), (lerp(rx, 10.0, kk), lerp(ry, 0.0, kk), lerp(rz, 0.0, kk)), lerp(24, 20, kk), roll=lerp(0.0, 0.9, kk))
    M["grade"] = "night"

@shot(67.0, END)
def s19(W, T, M):       # y tú… ¿a qué te agarrarías? (Nora mira a cámara desde la azotea)
    night3(W); k = (T-67.0)/(END-67.0)
    N = W["nora"]; rx, ry, rz = ROOF
    N.show(True); N.root.rotation_mode = 'XYZ'; N.place(rx, ry, lerp(270, 330, eio(clamp(k*2))), rz-0.3); N.idle(T)
    N.arm(-1, fwd=0.9, side=0.1, elbow=0.6)
    N.face(T, "worried" if k < 0.6 else "smirk", (0.0, 0.0))
    far_cars(W, T)
    hz = rz-0.3+1.3
    look(lerpv((rx-0.6, ry-4.2, hz+0.6), (rx-0.3, ry-2.3, hz+0.2), eio(k)), (rx, ry, hz), 26)
    M["grade"] = "night"

@shot(END, TOTAL+0.1)
def s20(W, T, M):       # FIN (negro)
    M["black"] = 1

def frame(W, T):
    hide3(W)
    for p in [W["nora"]] + W["npc"]: p.root.rotation_mode = 'XYZ'
    W["nora"].hips.location.z = 0.78*W["nora"].s
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
