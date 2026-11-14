"""Decorados de bloques (originales): ciudad (día/lluvia/noche), cafetería, campo de fútbol, oficina."""
import math, random
from vox import *
from person import Person, npc_look, LEO, FIG

FONT = None
def text3d(name, s, loc, size, col, parent=None, rot=(math.pi/2, 0, 0), extrude=0.02, align='CENTER'):
    global FONT
    if FONT is None: FONT = bpy.data.fonts.load("/home/claude/tiktok/fonts/Anton.ttf")
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = s; cu.font = FONT; cu.size = size; cu.extrude = extrude; cu.align_x = align
    o = link(bpy.data.objects.new(name, cu)); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(mat(col))
    if parent: o.parent = parent
    return o

def brick(p, r):  # patrón de ladrillo en una textura 16×16
    for y in range(16):
        if y % 4 == 3: p[y, :, :] *= 0.72
        off = 0 if (y//4) % 2 else 4
        for x in range(16):
            if (x+off) % 8 == 7: p[y, x, :] *= 0.75
    return p
def tiles(p, r):
    for y in range(16):
        for x in range(16):
            if x % 8 == 0 or y % 8 == 0: p[y, x, :] *= 0.82
    return p
def planks(p, r):
    for y in range(16):
        if y % 4 == 0: p[y, :, :] *= 0.75
    return p
def asphalt(p, r):
    p *= r.uniform(0.85, 1.1, (16, 16, 1)); return p
def stripes(p, r):
    for x in range(16):
        if (x//2) % 2: p[:, x, :] *= 0.86
    return p

def car(name, col="#C8342C", parent=None):
    g = group(name, (0, 0, 0), parent)
    B = Batch(name+"_b", g, 0.25)
    B.add((0, 0, 0.55), (3.6, 1.7, 0.6), col)
    B.add((-0.25, 0, 1.12), (2.0, 1.55, 0.56), col)
    B.add((0.78, 0, 1.12), (0.08, 1.45, 0.48), "#9FD0E8")       # parabrisas
    B.add((-1.27, 0, 1.12), (0.06, 1.4, 0.44), "#9FD0E8")
    for x in (-0.75, 0.25):
        for y in (-0.79, 0.79): B.add((x, y, 1.12), (0.8, 0.02, 0.42), "#9FD0E8")
    B.add((1.81, 0, 0.5), (0.04, 1.6, 0.22), "#2A2A2E")       # rejilla
    for y in (-0.55, 0.55):
        B.add((1.81, y, 0.68), (0.05, 0.36, 0.16), "#FFF6C8")   # faros
        B.add((-1.81, y, 0.68), (0.05, 0.3, 0.14), "#E03030")
    B.add((0, 0, 0.27), (3.62, 1.72, 0.08), "#2A2A2E")
    for x in (-1.15, 1.15):
        for y in (-0.82, 0.82):
            B.add((x, y, 0.32), (0.62, 0.22, 0.62), "#1C1C20"); B.add((x, y*1.02, 0.32), (0.3, 0.2, 0.3), "#9AA0A8")
    B.done()
    return g

def tree(B, x, y, h=3.0, seed=0):
    r = random.Random(seed)
    B.add((x, y, h/2), (0.4, 0.4, h), tmat("bark", "#6A4A30", 8, 0.15, 5))
    for i in range(5):
        dx, dy, dz = r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6), r.uniform(0, 0.8)
        B.add((x+dx, y+dy, h+dz), (1.3, 1.3, 1.0), tmat("leaf", "#4E8A3A", 8, 0.22, 6))

def building(B, x0, y0, w, d, floors, col, seed, face=-1, shop=None):
    """bloque de edificio con ventanas en la fachada que mira a y·face"""
    r = random.Random(seed); fh = 1.6; H = floors*fh+0.4
    wall = tmat(f"wall{seed % 5}", col, 16, 0.07, seed, brick if seed % 2 else tiles)
    B.add((x0, y0, H/2), (w, d, H), wall)
    B.add((x0, y0, H+0.15), (w+0.2, d+0.2, 0.3), "#4A4A52")
    fy = y0 + face*d/2
    nx = max(1, int(w/1.6))
    for f in range(1 if shop else 0, floors):
        for i in range(nx):
            wx = x0 - w/2 + (i+0.5)*w/nx
            lit = r.random() < 0.5
            B.add((wx, fy+face*0.02, f*fh+1.0), (0.8, 0.06, 0.9), "#FFE7A0" if lit else "#4A6A8A")
            B.add((wx, fy+face*0.05, f*fh+0.52), (1.0, 0.12, 0.08), "#E8E4DA")
            if r.random() < 0.3: B.add((wx, fy+face*0.35, f*fh+0.45), (1.1, 0.6, 0.06), "#6A6A72")
    return fy

class City:
    """calle a lo largo de X. Calzada y∈[-3,3]; acera norte y∈[3,6] (tiendas), acera sur y∈[-6,-3]."""
    def __init__(s):
        s.g = group("city")
        B = Batch("city_static", s.g, 1.0)
        A = tmat("asph", "#45474E", 16, 0.12, 11, asphalt)
        B.add((0, 0, -0.05), (120, 6, 0.1), A)
        for sy in (1, -1):
            B.add((0, sy*4.5, 0.075), (120, 3, 0.25), tmat("walk", "#B8B4AA", 16, 0.05, 12, tiles))
            B.add((0, sy*3.05, 0.1), (120, 0.12, 0.3), "#8A8880")
        for i in range(-30, 30):
            B.add((i*2.0, 0, 0.005), (1.0, 0.12, 0.02), "#E8E4D8")      # línea central
        for j in range(7):                                             # paso de cebra en x≈0
            B.add((0.0, -2.6+j*0.86, 0.006), (2.6, 0.45, 0.02), "#EDEAE0")
        cols = ["#C8A27A", "#9AA8B8", "#D8C8A8", "#B0786A", "#A8B89A", "#C8B8D0", "#D0A070"]
        # fachada norte (tiendas en planta baja)
        s.shops = []
        x = -40
        k = 0
        while x < 40:
            w = random.Random(k).choice([6, 7, 8, 9])
            fy = building(B, x+w/2, 9.5, w, 7, 4+k % 4, cols[k % len(cols)], 100+k, -1, shop=True)
            # escaparate y toldo
            B.add((x+w/2, fy-0.02, 1.25), (w-1.2, 0.05, 1.9), "#7FA8C0")
            B.add((x+w/2, fy-0.6, 2.45), (w-0.8, 1.2, 0.1), ["#C0392B", "#2E7D6A", "#E0A030", "#3A5AA0"][k % 4])
            B.add((x+0.6, fy-0.05, 1.3), (0.2, 0.1, 2.6), "#4A4A52")
            s.shops.append((x+w/2, fy, w))
            x += w; k += 1
        x = -40; k = 0
        while x < 40:
            w = random.Random(50+k).choice([7, 8, 10])
            building(B, x+w/2, -9.5, w, 7, 5+k % 3, cols[(k+3) % len(cols)], 200+k, 1)
            x += w; k += 1
        # farolas, árboles, bancos, papeleras, semáforo
        s.lamps = []
        for i in range(-6, 7):
            for sy in (1, -1):
                lx = i*6.0+(1.5 if sy < 0 else 0); ly = sy*3.4
                B.add((lx, ly, 2.0), (0.14, 0.14, 4.0), "#2E3036")
                B.add((lx, ly-sy*0.45, 4.0), (0.1, 1.0, 0.1), "#2E3036")
                B.add((lx, ly-sy*0.85, 3.85), (0.42, 0.42, 0.22), "#FFF2B0")
                s.lamps.append((lx, ly-sy*0.85, 3.85))
        for i in range(-5, 6):
            tree(B, i*6.0+3, -5.2, 3.2, i)
        for i in (-14, 10, 22):
            B.add((i, 5.2, 0.55), (1.6, 0.5, 0.12), "#7A5A3A"); B.add((i, 5.42, 0.85), (1.6, 0.08, 0.5), "#7A5A3A")
        for i in (-21, 15):
            B.add((i, 3.6, 0.6), (0.5, 0.5, 0.9), "#3E6A4A")
        B.add((-1.8, 3.3, 1.6), (0.14, 0.14, 3.2), "#2E3036"); B.add((-1.8, 3.3, 3.3), (0.35, 0.3, 0.8), "#1E1E22")
        s.tl = [B.add((-1.8, 3.13, 3.55-i*0.25), (0.18, 0.04, 0.18), c) for i, c in enumerate(("#E03030", "#E0A030", "#30C060"))]
        s.static = B.done()
        # coches aparcados (estáticos)
        P = Batch("parked", s.g, 0.25)
        s.static2 = P.done()
        s.parked = []
        for i, (px, c) in enumerate(((-12, "#3A6AA8"), (-22, "#E0C040"), (9, "#5A8A5A"), (18, "#D8D8D0"), (28, "#6A3A7A"))):
            cg = car(f"park{i}", c, s.g); cg.location = (px, -2.0, 0); s.parked.append(cg)
        # coche protagonista
        s.car = car("hero_car", "#D23A2E", s.g)
        # rótulos
        names = ["PANADERÍA", "LIBROS", "MODA", "FARMACIA", "BAZAR", "ÓPTICA", "FLORES", "ZAPATOS", "CAFÉ"]
        for i, (sx, fy, w) in enumerate(s.shops):
            text3d(f"sign{i}", names[i % len(names)], (sx, fy-1.22, 2.62), 0.42, "#FBF6E8", s.g)
        # lluvia
        s.rain = []
        rng = random.Random(7)
        for i in range(520):
            d = box(f"drop{i}", (0, 0, 0), (0.012, 0.012, 0.15), mat("#CFE8FF"), s.g)
            s.rain.append((d, rng.random(), rng.random(), rng.random()))
        s.rain_on = True
        # escaparate para el reflejo (plano de cristal delante de la tienda 6)
        s.glass = box("glass", (0, 0, 0), (3.2, 0.03, 1.9), mat("#89AFC8"), s.g)
        hid(s.glass, True)

    def place_rain(s, center, t, frozen_t=None, area=(9, 9, 6)):
        tt = t if frozen_t is None else frozen_t
        cx, cy, cz = center
        for d, a, b, c in s.rain:
            z = (c*area[2] - tt*9.0) % area[2]
            d.location = (cx+(a-0.5)*area[0], cy+(b-0.5)*area[1], z+0.05)
            hid(d, not s.rain_on)

    def lights(s, on_traffic=0):
        for i, o in enumerate(s.tl): pass

class Cafe:
    def __init__(s, O=(0, 100, 0)):
        s.O = O; s.g = group("cafe", O)
        B = Batch("cafe_b", s.g, 1.0)
        B.add((0, 0, -0.05), (14, 14, 0.1), tmat("cafe_floor", "#B07A50", 16, 0.1, 21, planks))
        B.add((0, 4.0, 2.0), (14, 0.2, 4.0), tmat("cafe_wall", "#E8D8B8", 16, 0.04, 22, stripes))
        B.add((-5.0, 0, 2.0), (0.2, 14, 4.0), tmat("cafe_wall2", "#D8C098", 16, 0.04, 23, brick))
        B.add((0, 3.85, 1.2), (14, 0.12, 0.08), "#7A4A2A")
        # barra
        B.add((3.5, 2.4, 0.55), (4.0, 1.0, 1.1), tmat("bar", "#6A3E22", 16, 0.08, 24, planks))
        B.add((3.5, 2.4, 1.13), (4.2, 1.1, 0.06), "#D8D0C0")
        for i in range(5): B.add((2.0+i*0.7, 3.7, 1.8+0.1*(i % 2)), (0.3, 0.3, 0.45), ["#C0392B", "#E0A030", "#3A5AA0", "#6A9A48", "#F0EEE8"][i])
        B.add((3.5, 3.85, 2.6), (3.0, 0.1, 0.9), "#2A2A2E")
        # ventana a la calle con luz
        B.add((-4.88, 0, 2.0), (0.05, 4.0, 2.2), "#BFE0F0")
        # mesas del fondo
        for i, (x, y) in enumerate(((-2.8, 2.2), (0.5, 2.6), (-3.0, -2.0))):
            B.add((x, y, 0.75), (1.1, 1.1, 0.06), "#E8E0D0"); B.add((x, y, 0.37), (0.12, 0.12, 0.74), "#3A3A40")
        # lámparas colgantes
        for x in (-2.5, 0.2, 3.0):
            B.add((x, 0.5, 3.5), (0.04, 0.04, 1.0), "#2A2A2E"); B.add((x, 0.5, 2.95), (0.5, 0.5, 0.25), "#F0C060")
        # mesa principal
        B.add((0, 0, 0.78), (1.4, 1.0, 0.07), "#F4EEE3"); B.add((0, 0, 0.38), (0.14, 0.14, 0.76), "#3A3A40")
        for x in (-1.15, 1.15):
            B.add((x, 0, 0.45), (0.55, 0.55, 0.08), "#7A4A2A"); B.add((x, 0.25, 0.75), (0.55, 0.08, 0.6), "#7A4A2A")
            B.add((x, 0, 0.22), (0.08, 0.08, 0.44), "#3A3A40")
        # plato y vasos
        B.add((0.35, 0, 0.83), (0.5, 0.5, 0.03), "#FBFBF6")
        B.add((-0.35, 0.2, 0.92), (0.14, 0.14, 0.22), "#D8E8F0"); B.add((-0.35, 0.2, 0.87), (0.12, 0.12, 0.1), "#E0A030")
        s.b = B.done()
        # patatas del amigo (cajas sueltas para poder robar una)
        s.fries = []
        r = random.Random(3)
        for i in range(9):
            f = box(f"fry{i}", (O[0]+0.35+r.uniform(-0.14, 0.14), O[1]+r.uniform(-0.14, 0.14), O[2]+0.88), (0.05, 0.05, 0.24), mat("#F2C040"), s.g, rot=(r.uniform(-0.5, 0.5), r.uniform(-0.5, 0.5), r.uniform(0, 3)))
            f.parent = None; f.location = (O[0]+0.35+r.uniform(-0.14, 0.14), O[1]+r.uniform(-0.14, 0.14), O[2]+0.9)
            s.fries.append(f)
        s.stolen = box("fry_stolen", (0, 0, 0), (0.05, 0.05, 0.24), mat("#F2C040"))
        s.cup_drop = box("coffee_splash", (0, 0, 0), (0.06, 0.06, 0.06), mat("#6A3E22"))
    def show(s, v=True):
        show(s.g, v)
        for f in s.fries: hid(f, not v)
        hid(s.stolen, not v); hid(s.cup_drop, not v)

class Field:
    def __init__(s, O=(0, 200, 0)):
        s.O = O; s.g = group("field", O)
        B = Batch("field_b", s.g, 1.0)
        def stripe_grass(p, r):
            for x in range(16):
                if (x//8) % 2: p[:, x, :] *= 0.86
            return p
        B.add((0, 0, -0.05), (60, 60, 0.1), tmat("pitch", "#4E9A3E", 16, 0.08, 31, stripe_grass))
        for x in (-8, 8): B.add((x, 0, 0.005), (0.12, 40, 0.02), "#F0F0E8")
        B.add((0, -9, 0.005), (16, 0.12, 0.02), "#F0F0E8")
        B.add((0, 10, 0.005), (8.2, 0.12, 0.02), "#F0F0E8"); B.add((0, 6, 0.005), (8.2, 0.12, 0.02), "#F0F0E8")
        for x in (-4.1, 4.1): B.add((x, 8, 0.005), (0.12, 4, 0.02), "#F0F0E8")
        # portería
        for x in (-2.6, 2.6): B.add((x, 10, 1.15), (0.14, 0.14, 2.3), "#FBFBF6")
        B.add((0, 10, 2.3), (5.34, 0.14, 0.14), "#FBFBF6")
        for i in range(12): B.add((-2.6+i*0.47, 11.0, 1.15), (0.03, 0.03, 2.3), "#E8E8E8")
        for i in range(6): B.add((0, 11.0, 0.2+i*0.4), (5.2, 0.03, 0.03), "#E8E8E8")
        B.add((0, 10.5, 2.3), (5.2, 1.0, 0.03), "#E0E0E0")
        # gradas con público
        r = random.Random(9)
        for row in range(6):
            B.add((0, 18+row*1.0, 0.4+row*0.5), (40, 1.0, 0.8+row), "#8A8C94")
            for i in range(60):
                c = r.choice(["#C0392B", "#3A5AA0", "#F0EEE8", "#E0A030", "#2A2A2E", "#6A9A48"])
                B.add((-20+i*0.66+r.uniform(-0.1, 0.1), 18+row*1.0, 1.0+row*1.0), (0.4, 0.4, 0.5), c)
                B.add((-20+i*0.66, 18+row*1.0, 1.42+row*1.0), (0.3, 0.3, 0.3), r.choice(["#F2C9A0", "#C68E62", "#8D5A3A"]))
        B.add((-14, 16.5, 3.0), (6.0, 0.2, 2.0), "#1E1E24")
        s.b = B.done()
        s.score = text3d("score", "1 - 1", (O[0]-14, O[1]+16.38, O[2]+2.75), 0.9, "#FFD040", s.g)
        s.ball = box("ball", (0, 0, 0), (0.32, 0.32, 0.32), tmat("ballt", "#F4F4F0", 4, 0.0, 1, lambda p, r: _ballpat(p)), s.g)

def _ballpat(p):
    for (x, y) in ((0, 0), (2, 1), (1, 3), (3, 2)): p[y, x, :] = 0.1
    return p

class Office:
    def __init__(s, O=(0, 300, 0)):
        s.O = O; s.g = group("office", O)
        B = Batch("office_b", s.g, 1.0)
        B.add((0, 0, -0.05), (20, 20, 0.1), tmat("carpet", "#6A7A8A", 16, 0.06, 41))
        B.add((0, 6.0, 2.0), (20, 0.2, 4.0), tmat("owall", "#E4E6E8", 16, 0.02, 42, tiles))
        B.add((-6.0, 0, 2.0), (0.2, 20, 4.0), tmat("owall2", "#D8DCE0", 16, 0.02, 43))
        for i in range(4): B.add((-3+i*2.6, 5.88, 2.3), (2.0, 0.05, 1.6), "#9FC8E0")   # ventanas
        B.add((4.6, 5.86, 3.2), (0.8, 0.05, 0.8), "#FBFBF6")                          # reloj de pared
        s.clock_h = box("oclock_h", (O[0]+4.6, O[1]+5.82, O[2]+3.2), (0.05, 0.02, 0.28), mat("#1E1E24"), None, origin=(0, 0, -0.12))
        s.clock_m = box("oclock_m", (O[0]+4.6, O[1]+5.81, O[2]+3.2), (0.04, 0.02, 0.36), mat("#C0302A"), None, origin=(0, 0, -0.16))
        s.desks = []
        for row in range(2):
            for col in range(3):
                x, y = -3.5+col*3.4, -1.5+row*3.2
                B.add((x, y, 0.75), (2.2, 1.1, 0.07), "#E8E0D0")
                for dx in (-1.0, 1.0): B.add((x+dx, y, 0.37), (0.07, 1.0, 0.74), "#5A5A62")
                B.add((x, y+0.35, 1.1), (0.9, 0.06, 0.55), "#1E1E24"); B.add((x, y+0.33, 1.1), (0.82, 0.02, 0.47), "#5AA0D8")
                B.add((x, y+0.4, 0.82), (0.1, 0.1, 0.1), "#2A2A2E")
                B.add((x, y-0.1, 0.8), (0.6, 0.2, 0.03), "#2A2A2E")
                B.add((x, y-0.9, 0.5), (0.55, 0.55, 0.08), "#2A2A2E"); B.add((x, y-1.15, 0.85), (0.55, 0.08, 0.6), "#2A2A2E")
                s.desks.append((x, y))
        for i in range(3): B.add((5.0, -3+i*1.2, 0.6), (0.6, 0.6, 1.2), "#4E8A3A")
        B.add((-5.5, 2.0, 1.1), (0.8, 2.5, 2.2), "#8A8C94")
        s.b = B.done()
        s.papers = [box(f"paper{i}", (0, 0, 0), (0.3, 0.4, 0.01), mat("#FBFBF6"), None) for i in range(6)]
        s.coffee = box("ocoffee", (0, 0, 0), (0.12, 0.12, 0.16), mat("#F0EEE8"))
    def show(s, v=True):
        show(s.g, v); hid(s.clock_h, not v); hid(s.clock_m, not v)
        for p in s.papers: hid(p, not v)
        hid(s.coffee, not v)
