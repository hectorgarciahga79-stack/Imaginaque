"""Generador procedural de ciudad costera nocturna (estilo 'Miami años 80',
diseño 100% original: nombres, rótulos y arquitectura inventados).

Distribución (metros, X = este, Y = norte, Z = arriba):
  * Avenida costera (4 carriles) en x ∈ [-8, 8] a lo largo de Y.
  * Paseo marítimo con palmeras y farolas x ∈ [8, 15]; playa hasta x = 70;
    océano al este.
  * Edificios art déco con neones en primera línea (x ≈ -13..-35) y torres
    de oficinas detrás. Calles transversales hacia el oeste cada ``block`` m.

Optimización: mallas compartidas (duplicados enlazados) para palmeras,
farolas y coches aparcados; materiales cacheados; geometría simple con
detalle en los shaders.
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

from . import materials as M
from .vehicles import box, cylinder, _link

NEON_COLORS = [(1.0, 0.08, 0.55), (0.05, 0.85, 1.0), (0.65, 0.15, 1.0), (1.0, 0.35, 0.05), (0.2, 1.0, 0.55), (1.0, 0.9, 0.2)]
PASTELS = [(0.85, 0.55, 0.62), (0.55, 0.78, 0.78), (0.9, 0.82, 0.65), (0.72, 0.62, 0.85), (0.92, 0.9, 0.86), (0.6, 0.82, 0.68)]
SIGNS = ["HOTEL MAREA", "CAFÉ LUNA", "NEÓN", "OCEAN CLUB", "MOTEL ROSA", "BAR 24H", "PALMERAS", "DISCO SOL",
         "FLAMENCO", "CASA AZUL", "TROPICAL", "MARINA", "HOTEL BRISA", "CORAL", "PARAÍSO", "SALSA"]


class CityBuilder:
    def __init__(self, seed=7, y_min=-1000.0, y_max=320.0, block=80.0, turn_y=0.0, west_extent=420.0,
                 quality="high", font_path=None):
        self.rng = random.Random(seed)
        self.seed = seed
        self.y_min, self.y_max = y_min, y_max
        self.block = block
        self.turn_y = turn_y
        self.west = west_extent
        self.quality = quality
        self.font = None
        if font_path:
            try:
                self.font = bpy.data.fonts.load(font_path, check_existing=True)
            except Exception:
                self.font = None
        self.coll = bpy.data.collections.new("Ciudad")
        bpy.context.scene.collection.children.link(self.coll)
        self.cross_ys = self._cross_streets()
        self.street_lights = []

    # ------------------------------------------------------------------ helpers
    def _sub(self, name):
        c = bpy.data.collections.new(name)
        self.coll.children.link(c)
        return c

    def _cross_streets(self):
        ys = []
        y = self.turn_y
        while y > self.y_min + 40:
            ys.append(y)
            y -= self.block
        y = self.turn_y + self.block
        while y < self.y_max - 40:
            ys.append(y)
            y += self.block
        return sorted(ys)

    def _plane(self, name, x0, x1, y0, y1, z, mat, coll):
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        vs = [bm.verts.new((x0, y0, z)), bm.verts.new((x1, y0, z)), bm.verts.new((x1, y1, z)), bm.verts.new((x0, y1, z))]
        bm.faces.new(vs)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        return _link(ob, coll)

    def _merged_boxes(self, name, boxes, mat, coll):
        """Muchas cajas en una sola malla (marcas viales, bordillos...)."""
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        for (cx, cy, cz, sx, sy, sz) in boxes:
            r = bmesh.ops.create_cube(bm, size=1.0)
            for v in r["verts"]:
                v.co = Vector((cx + v.co.x * sx, cy + v.co.y * sy, cz + v.co.z * sz))
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        return _link(ob, coll)

    # ------------------------------------------------------------------ build
    def build(self):
        self.build_ground()
        self.build_roads()
        self.build_waterfront()
        self.build_buildings()
        self.build_street_furniture()
        self.build_skyline_far()
        return self

    def build_ground(self):
        c = self._sub("Suelo")
        base = M.concrete("suelo_base", (0.03, 0.03, 0.032), 0.5)
        self._plane("suelo", -3000, 70, -3000, 3000, -0.05, base, c)
        self._plane("playa", 15, 72, -3000, 3000, -0.02, M.sand(), c)
        self._plane("oceano", 70, 4000, -4000, 4000, -0.35, M.ocean(), c)

    def build_roads(self):
        c = self._sub("Calles")
        asphalt = M.wet_asphalt()
        self._plane("avenida", -8, 8, self.y_min, self.y_max, 0.0, asphalt, c)
        for y in self.cross_ys:
            self._plane("calle_%d" % y, -self.west, -8, y - 6, y + 6, 0.0, asphalt, c)
        # aceras elevadas (bordillo 15 cm)
        side = M.concrete("acera", (0.22, 0.21, 0.2), 0.45)
        boxes = []
        ys = [self.y_min] + self.cross_ys + [self.y_max]
        for a, b in zip(ys, ys[1:]):
            y0 = a + (6 if a in self.cross_ys else 0)
            y1 = b - (6 if b in self.cross_ys else 0)
            if y1 - y0 < 2:
                continue
            boxes.append((-10.5, (y0 + y1) / 2, 0.075, 5, y1 - y0, 0.15))
        boxes.append((11.5, (self.y_min + self.y_max) / 2, 0.075, 7, self.y_max - self.y_min, 0.15))
        for y in self.cross_ys:  # aceras de las calles transversales
            for sy in (-1, 1):
                boxes.append((-(self.west + 13) / 2, y + sy * 8.5, 0.075, self.west - 13, 5, 0.15))
        self._merged_boxes("aceras", boxes, side, c)
        # marcas viales
        paint = M.principled("pintura_vial", (0.75, 0.75, 0.72), 0, 0.35)
        yellow = M.principled("pintura_amarilla", (0.8, 0.55, 0.05), 0, 0.35)
        marks, ymarks = [], []
        y = self.y_min
        while y < self.y_max:
            near_cross = any(abs(y - cy) < 9 for cy in self.cross_ys)
            if not near_cross:
                for x in (-4, 4):
                    marks.append((x, y, 0.003, 0.15, 3.0, 0.006))
                ymarks.append((-0.18, y + 3, 0.003, 0.12, 6.0, 0.006))
                ymarks.append((0.18, y + 3, 0.003, 0.12, 6.0, 0.006))
            y += 6
        for cy in self.cross_ys:  # pasos de cebra
            for k in range(8):
                marks.append((-6.5 + k * 1.85, cy - 8.5, 0.003, 0.9, 3.0, 0.006))
                marks.append((-6.5 + k * 1.85, cy + 8.5, 0.003, 0.9, 3.0, 0.006))
        self._merged_boxes("marcas", marks, paint, c)
        self._merged_boxes("lineas_amarillas", ymarks, yellow, c)

    # ------------------------------------------------------------------ palmeras
    def _palm_proto(self, c):
        rng = random.Random(3)
        me = bpy.data.meshes.new("palmera")
        bm = bmesh.new()
        h, segs, n = 9.0, 14, 10
        rings = []
        for i in range(segs + 1):
            t = i / segs
            z = h * t
            off = 0.9 * t * t
            r = 0.24 * (1 - 0.35 * t) * (1.08 if i % 2 else 1.0)
            ring = []
            for k in range(n):
                a = 2 * math.pi * k / n
                ring.append(bm.verts.new((off + r * math.cos(a), r * math.sin(a), z)))
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(n):
                bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
        trunk_faces = len(bm.faces)
        top = Vector((0.9, 0, h))
        for f in range(13):
            a = 2 * math.pi * f / 13 + rng.uniform(-0.15, 0.15)
            L = rng.uniform(3.6, 4.6)
            droop = rng.uniform(0.6, 1.0)
            pts = 9
            left, right = [], []
            for i in range(pts):
                t = i / (pts - 1)
                d = L * t
                z = 0.9 * math.sin(t * 2.2) * 1.0 - droop * 2.6 * t * t
                cx = top.x + math.cos(a) * d
                cy = top.y + math.sin(a) * d
                w = 0.55 * math.sin(math.pi * min(1, t * 1.15)) + 0.05
                px, py = -math.sin(a) * w, math.cos(a) * w
                left.append(bm.verts.new((cx + px, cy + py, top.z + z - 0.08 * w)))
                right.append(bm.verts.new((cx - px, cy - py, top.z + z - 0.08 * w)))
                mid = None
            for i in range(pts - 1):
                bm.faces.new((left[i], left[i + 1], right[i + 1], right[i]))
        bm.to_mesh(me)
        bm.free()
        me.materials.append(M.bark())
        me.materials.append(M.leaf())
        for i, p in enumerate(me.polygons):
            p.material_index = 0 if i < trunk_faces else 1
            p.use_smooth = True
        return me

    def build_waterfront(self):
        c = self._sub("PaseoMaritimo")
        palm = self._palm_proto(c)
        y = self.y_min + 6
        i = 0
        while y < self.y_max:
            for x, jitter in ((13.2, 1.0), (-11.6, 0.0)):
                if x < 0 and (i % 3 != 0 or any(abs(y - cy) < 10 for cy in self.cross_ys)):
                    continue
                ob = bpy.data.objects.new("palmera", palm)
                ob.location = (x + self.rng.uniform(-0.4, 0.4) * jitter, y + self.rng.uniform(-2, 2), 0.15)
                ob.rotation_euler = (0, 0, self.rng.uniform(0, 2 * math.pi))
                s = self.rng.uniform(0.85, 1.25)
                ob.scale = (s, s, s)
                _link(ob, c)
            # palmeras en la playa (densidad menor)
            if self.rng.random() < 0.55:
                ob = bpy.data.objects.new("palmera_playa", palm)
                ob.location = (self.rng.uniform(20, 55), y + self.rng.uniform(-5, 5), 0)
                ob.rotation_euler = (0, 0, self.rng.uniform(0, 6.28))
                s = self.rng.uniform(0.9, 1.4)
                ob.scale = (s, s, s)
                _link(ob, c)
            y += 12
            i += 1
        # murete del paseo con tira de neón cian
        wall = M.concrete("murete", (0.75, 0.72, 0.68), 0.5)
        self._merged_boxes("murete", [(15.0, (self.y_min + self.y_max) / 2, 0.45, 0.4, self.y_max - self.y_min, 0.9)], wall, c)
        self._merged_boxes("neon_murete", [(14.78, (self.y_min + self.y_max) / 2, 0.8, 0.04, self.y_max - self.y_min, 0.04)], M.neon("neon_cian", (0.05, 0.8, 1.0), 4.0), c)
        # socorristas (casetas de colores) en la playa
        for k in range(10):
            yy = self.y_min + 80 + k * (self.y_max - self.y_min - 160) / 9
            col = PASTELS[k % len(PASTELS)]
            hut = box("caseta", (3, 3, 2.4), (45, yy, 2.6), c, M.principled("caseta_%d" % (k % 6), col, 0, 0.6), 0.05)
            box("caseta_pata", (2.4, 2.4, 1.4), (45, yy, 0.7), c, M.concrete("pilar", (0.4, 0.38, 0.36)))
            roof = box("caseta_techo", (3.6, 3.6, 0.25), (45, yy, 3.9), c, M.neon("neon_caseta_%d" % (k % 6), NEON_COLORS[k % 6], 4.0))

    # ------------------------------------------------------------------ edificios
    def _neon_text(self, text, loc, rot, size, color, c, strength=30.0):
        cu = bpy.data.curves.new("rotulo", "FONT")
        cu.body = text
        cu.size = size
        cu.extrude = 0.04
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        if self.font:
            cu.font = self.font
        ob = bpy.data.objects.new("rotulo_" + text, cu)
        ob.location = loc
        ob.rotation_euler = rot
        mat = M.neon("neon_txt_%d" % NEON_COLORS.index(color), color, strength)
        cu.materials.append(mat)
        return _link(ob, c)

    def _deco_building(self, x_front, y0, y1, c, idx):
        """Edificio art déco: cuerpo pastel, cornisas, aleta central, neones."""
        rng = self.rng
        depth = rng.uniform(16, 24)
        floors = rng.randint(3, 6)
        h = floors * 3.3 + 1.2
        col = PASTELS[rng.randrange(len(PASTELS))]
        fac = M.facade("deco_%d" % (idx % 6), wall=col, lit_ratio=0.32, floor_h=3.3, win_w=2.2,
                       strength=1.1, seed=idx % 6, pastel=True)
        cx, cy = x_front - depth / 2, (y0 + y1) / 2
        w = y1 - y0
        b = box("deco", (depth, w, h), (cx, cy, h / 2), c, fac)
        # remate escalonado
        b2 = box("deco_remate", (depth * 0.6, w * 0.5, 2.6), (cx + depth * 0.15, cy, h + 1.3), c, fac)
        trim = M.concrete("cornisa_%d" % (idx % 3), (0.92, 0.9, 0.86), 0.5)
        ledges = []
        for f in range(1, floors + 1):
            ledges.append((x_front + 0.25, cy, f * 3.3 - 0.2, 0.5, w, 0.12))
        ledges.append((x_front + 0.15, cy, h, 0.6, w + 0.2, 0.35))
        self._merged_boxes("cornisas", ledges, trim, c)
        ncol = NEON_COLORS[rng.randrange(len(NEON_COLORS))]
        nm = M.neon("neon_%d" % NEON_COLORS.index(ncol), ncol, 6.0)
        # tiras de neón: borde del tejado y esquinas
        strips = [(x_front + 0.42, cy, h + 0.2, 0.06, w, 0.08),
                  (x_front + 0.42, y0 + 0.2, h / 2, 0.06, 0.08, h),
                  (x_front + 0.42, y1 - 0.2, h / 2, 0.06, 0.08, h),
                  (x_front + 0.42, cy, 3.6, 0.06, w * 0.95, 0.06)]
        self._merged_boxes("neon_borde", strips, nm, c)
        # aleta vertical con rótulo
        if rng.random() < 0.75:
            fin_h = h * 0.75
            fin = box("aleta", (1.6, 0.5, fin_h), (x_front + 0.8, cy + rng.uniform(-w * 0.25, w * 0.25), h - fin_h / 2 + 1.5), c, trim)
            word = SIGNS[idx % len(SIGNS)].split()[0]
            col2 = NEON_COLORS[(NEON_COLORS.index(ncol) + 2) % len(NEON_COLORS)]
            for k, ch in enumerate(word[:7]):
                self._neon_text(ch, (x_front + 1.65, fin.location.y, h + 0.6 - k * 1.45), (math.pi / 2, 0, math.pi / 2), 1.4, col2, c, 14)
        # rótulo horizontal sobre la planta baja
        text = SIGNS[(idx * 7 + 3) % len(SIGNS)]
        tsize = min(2.3, w * 0.85 / (len(text) * 0.62))
        box("panel_rotulo", (0.15, w * 0.9, tsize * 1.25), (x_front + 0.5, cy, 5.0 + tsize * 0.4), c, M.principled("panel_oscuro", (0.01, 0.01, 0.012), 0.3, 0.3))
        self._neon_text(text, (x_front + 0.62, cy, 5.0 + tsize * 0.4), (math.pi / 2, 0, math.pi / 2), tsize, ncol, c, 16)
        # toldo
        aw = M.principled("toldo_%d" % (idx % 4), NEON_COLORS[(idx + 1) % 6], 0, 0.6)
        a = box("toldo", (2.2, w * 0.7, 0.12), (x_front + 1.1, cy, 3.25), c, aw)
        a.rotation_euler = (0, math.radians(-12), 0)
        # luz real del rótulo hacia la calle (iluminación de neón sobre el asfalto)
        ld = bpy.data.lights.new("luz_neon", "AREA")
        ld.energy = 420
        ld.color = ncol
        ld.size = min(w * 0.7, 10)
        ld.size_y = 1.0
        ld.shape = "RECTANGLE"
        lo = bpy.data.objects.new("luz_neon", ld)
        lo.location = (x_front + 1.2, cy, 4.2)
        lo.rotation_euler = (0, math.radians(110), 0)  # mira hacia +X y abajo
        _link(lo, c)

    def _tower(self, cx, cy, sx, sy, h, c, idx):
        fac = M.facade("torre_%d" % (idx % 8), wall=(0.16, 0.17, 0.2) if idx % 3 else (0.35, 0.33, 0.32),
                       lit_ratio=0.18 + 0.1 * (idx % 3), floor_h=3.6, win_w=1.9, strength=1.6, seed=10 + idx % 8)
        box("torre", (sx, sy, h), (cx, cy, h / 2), c, fac)
        if h > 60 and self.rng.random() < 0.6:  # corona iluminada
            ncol = NEON_COLORS[idx % len(NEON_COLORS)]
            box("corona", (sx * 0.7, sy * 0.7, 6), (cx, cy, h + 3), c, M.facade("corona", wall=(0.1, 0.1, 0.12), lit_ratio=0.9, strength=8, seed=99))
            self._merged_boxes("neon_corona", [(cx, cy, h + 0.3, sx + 0.3, sy + 0.3, 0.3)], M.neon("neon_%d" % NEON_COLORS.index(ncol), ncol, 6.0), c)
        if h > 80:  # baliza roja de aviación
            box("baliza", (0.5, 0.5, 0.5), (cx, cy, h + 7), c, M.emission("baliza", (1, 0.05, 0.02), 80))

    def build_buildings(self):
        c = self._sub("Edificios")
        rng = self.rng
        ys = [self.y_min] + self.cross_ys + [self.y_max]
        idx = 0
        for a, b in zip(ys, ys[1:]):
            y0 = a + (8.5 if a in self.cross_ys else 0) + 2.5
            y1 = b - (8.5 if b in self.cross_ys else 0) - 2.5
            if y1 - y0 < 15:
                continue
            # primera línea art déco (fachada a la avenida en x = -13)
            y = y0
            while y < y1 - 8:
                w = min(rng.uniform(16, 28), y1 - y)
                if y1 - (y + w) < 8:
                    w = y1 - y
                self._deco_building(-13.2, y + 0.4, y + w - 0.4, c, idx)
                idx += 1
                y += w
            # torres detrás, en manzanas hasta el oeste
            x = -58
            row = 0
            while x > -self.west + 20:
                yy = y0
                while yy < y1 - 10:
                    sy = min(rng.uniform(18, 34), y1 - yy)
                    sx = rng.uniform(18, 30)
                    dist = abs(x)
                    hmax = 26 + min(170, (dist - 40) * 0.55) + (50 if abs((yy + a) / 2 - self.turn_y) < 260 and dist > 120 else 0)
                    h = rng.uniform(18, hmax)
                    self._tower(x - sx / 2, yy + sy / 2, sx - 2, sy - 2, h, c, idx)
                    idx += 1
                    yy += sy + rng.uniform(2, 6)
                x -= rng.uniform(34, 48)
                row += 1
        self.building_count = idx

    def build_street_furniture(self):
        c = self._sub("Mobiliario")
        pole_m = M.principled("metal_farola", (0.08, 0.08, 0.09), 0.8, 0.4)
        lamp_m = M.emission("lampara_led", (1.0, 0.82, 0.68), 25.0)
        # prototipo de farola (malla compartida)
        proto = bpy.data.meshes.new("farola")
        bm = bmesh.new()
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.12, radius2=0.08, depth=8.5)
        bmesh.ops.translate(bm, vec=(0, 0, 4.25), verts=r["verts"])
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((v.co.x * 2.6 - 1.2, v.co.y * 0.1, v.co.z * 0.1 + 8.4))
        nfaces_pole = len(bm.faces)
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((v.co.x * 0.9 - 2.4, v.co.y * 0.35, v.co.z * 0.12 + 8.3))
        bm.to_mesh(proto)
        bm.free()
        proto.materials.append(pole_m)
        proto.materials.append(lamp_m)
        for i, p in enumerate(proto.polygons):
            p.material_index = 0 if i < nfaces_pole else 1
        y = self.y_min + 10
        while y < self.y_max:
            for x, rot in ((9.4, 0.0), (-9.4, math.pi)):
                ob = bpy.data.objects.new("farola", proto)
                ob.location = (x, y + (0 if x > 0 else 17), 0.15)
                ob.rotation_euler = (0, 0, rot)
                _link(ob, c)
                ld = bpy.data.lights.new("farola_luz", "SPOT")
                ld.energy = 1300
                ld.color = (1.0, 0.8, 0.66)
                ld.spot_size = math.radians(115)
                ld.spot_blend = 0.8
                ld.shadow_soft_size = 0.3
                lo = bpy.data.objects.new("farola_luz", ld)
                lo.location = (x - 2.4 * (1 if x > 0 else -1), ob.location.y, 8.15)
                _link(lo, c)
                self.street_lights.append(lo)
            y += 34
        # semáforos en la intersección del giro
        sem_m = M.principled("semaforo", (0.05, 0.05, 0.05), 0.5, 0.4)
        for (sx, sy) in ((9, self.turn_y - 8), (-9, self.turn_y + 8)):
            box("semaforo_poste", (0.18, 0.18, 6), (sx, sy, 3), c, sem_m)
            box("semaforo_caja", (0.4, 0.4, 1.1), (sx, sy, 5.8), c, sem_m)
            box("semaforo_luz", (0.42, 0.2, 0.2), (sx, sy, 6.15), c, M.emission("ambar", (1.0, 0.45, 0.02), 60))

    def build_skyline_far(self):
        """Gran 'downtown' lejano al norte y bahía con islas iluminadas."""
        c = self._sub("SkylineLejano")
        rng = self.rng
        for k in range(70):
            cx = rng.uniform(-900, -60)
            cy = rng.uniform(self.y_max + 150, self.y_max + 1100)
            h = rng.uniform(60, 260) * (1.3 if abs(cx + 350) < 200 else 1.0)
            s = rng.uniform(25, 45)
            self._tower(cx, cy, s, s * rng.uniform(0.7, 1.3), h, c, 200 + k)
        # puente con luces sobre la bahía (norte)
        deck = M.concrete("puente", (0.3, 0.3, 0.32))
        self._merged_boxes("puente", [(300, self.y_max + 420, 18, 900, 14, 1.5)], deck, c)
        lights = [(-150 + i * 20, self.y_max + 420 + s * 6.8, 20.0, 0.4, 0.4, 0.4) for i in range(46) for s in (-1, 1)]
        self._merged_boxes("puente_luces", lights, M.emission("luz_puente", (1.0, 0.8, 0.55), 60), c)
        cables = [(-150 + i * 120, self.y_max + 420, 45, 2.5, 14, 55) for i in range(8)]
        self._merged_boxes("puente_pilonos", cables, M.facade("pilono", wall=(0.2, 0.2, 0.22), lit_ratio=0.0), c)
        # luces de barcos en el mar
        boats = [(rng.uniform(150, 900), rng.uniform(-1200, 600), 0.5, 0.5, 0.5, 0.5) for _ in range(40)]
        self._merged_boxes("barcos", boats, M.emission("luz_barco", (1.0, 0.9, 0.7), 200), c)

    # ------------------------------------------------------------------ cielo
    @staticmethod
    def build_world(moon=True, strength=1.0):
        w = bpy.data.worlds.new("NocheNeon")
        bpy.context.scene.world = w
        w.use_nodes = True
        nt = w.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        b = M.NB(nt)
        tc = b.n("ShaderNodeTexCoord")
        sep = b.n("ShaderNodeSeparateXYZ")
        b.link(tc.outputs["Generated"], sep.inputs[0])
        z = sep.outputs["Z"]
        grad = b.n("ShaderNodeValToRGB")
        cr = grad.color_ramp
        cr.elements[0].position = 0.0
        cr.elements[0].color = (0.11, 0.035, 0.12, 1)
        cr.elements[1].position = 0.22
        cr.elements[1].color = (0.004, 0.006, 0.025, 1)
        e = cr.elements.new(0.06)
        e.color = (0.06, 0.02, 0.09, 1)
        b.link(z, grad.inputs[0])
        # nubes iluminadas por la ciudad
        cl = b.n("ShaderNodeTexNoise", Scale=2.5, Detail=8.0, Roughness=0.62)
        b.link(tc.outputs["Generated"], cl.inputs["Vector"])
        cm = b.n("ShaderNodeMapRange", **{"From Min": 0.48, "From Max": 0.75})
        b.link(cl.outputs["Fac"], cm.inputs["Value"])
        low = b.math("SUBTRACT", 1.0, b.math("MULTIPLY", b.math("ABSOLUTE", z), 2.2), clamp=True)
        cloud_amt = b.math("MULTIPLY", cm.outputs[0], b.math("MULTIPLY", low, 0.55))
        col = b.mix_color(cloud_amt, grad.outputs[0], (0.16, 0.06, 0.13, 1))
        # estrellas
        st = b.n("ShaderNodeTexVoronoi", Scale=420.0)
        b.link(tc.outputs["Generated"], st.inputs["Vector"])
        stars = b.math("LESS_THAN", st.outputs["Distance"], 0.035)
        stars = b.math("MULTIPLY", stars, b.math("SUBTRACT", 1.0, cloud_amt, clamp=True))
        stars = b.math("MULTIPLY", stars, b.math("GREATER_THAN", z, 0.1))
        col2 = b.mix_color(b.math("MULTIPLY", stars, 0.8), col, (1, 1, 1, 1), "ADD")
        bg = b.n("ShaderNodeBackground", Strength=strength)
        b.link(col2, bg.inputs["Color"])
        o = b.n("ShaderNodeOutputWorld")
        b.link(bg.outputs[0], o.inputs["Surface"])
        if moon:
            ld = bpy.data.lights.new("luna", "SUN")
            ld.energy = 0.12
            ld.color = (0.55, 0.65, 1.0)
            ld.angle = math.radians(1.5)
            lo = bpy.data.objects.new("luna", ld)
            lo.rotation_euler = (math.radians(55), 0, math.radians(-120))
            bpy.context.scene.collection.objects.link(lo)
        return w
