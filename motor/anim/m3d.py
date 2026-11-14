"""m3d — motor 3D propio de ImaginaQue (Blender bpy, render Workbench «plastilina»).
Se ejecuta en un proceso aparte (render3d.py). Construye decorados y personajes con primitivas,
y cada fotograma se posa desde Python (como el motor cairo) y se renderiza a PNG.
Sin modelos descargados, sin personajes ni marcas de terceros."""
import bpy, bmesh, math, random
from mathutils import Vector, Euler

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

def srgb2lin(c):
    return tuple(((x+0.055)/1.055)**2.4 if x > 0.04045 else x/12.92 for x in c)

# ---------------------------------------------------------------- escena
def reset(res=(540, 960), fps=15):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
    try: sh.studio_light = 'paint.sl'
    except Exception: pass
    sh.show_shadows = True; sh.shadow_intensity = 0.32
    sh.show_cavity = False; sh.cavity_type = 'BOTH'; sh.cavity_ridge_factor = 0.6; sh.cavity_valley_factor = 1.0
    sh.curvature_ridge_factor = 0.5; sh.curvature_valley_factor = 0.7
    sh.show_object_outline = True; sh.object_outline_color = (0.07, 0.06, 0.08)
    sh.show_specular_highlight = False
    sc.display.light_direction = (0.45, -0.35, 0.82)
    sc.display.shadow_shift = 0.08; sc.display.shadow_focus = 0.6
    sc.display.render_aa = 'FXAA'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.fps = fps
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0.45
    w = bpy.data.worlds.new("w"); sc.world = w; w.color = srgb2lin(hexc("#1E2230"))
    return sc

def world_color(col):
    bpy.context.scene.world.color = srgb2lin(col if isinstance(col, tuple) else hexc(col))

_MATS = {}
def mat(col):
    col = col if isinstance(col, tuple) else hexc(col)
    key = tuple(round(x, 3) for x in col)
    if key not in _MATS:
        m = bpy.data.materials.new(f"m{len(_MATS)}"); m.diffuse_color = (*srgb2lin(col), 1); m.roughness = 0.6; m.metallic = 0.0
        _MATS[key] = m
    return _MATS[key]

def _finish(o, col, smooth=True, parent=None):
    if col is not None:
        o.data.materials.clear(); o.data.materials.append(mat(col))
    if smooth and o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
    if parent: o.parent = parent
    return o

def link(o):
    bpy.context.scene.collection.objects.link(o); return o

def empty(name="e", loc=(0, 0, 0), parent=None):
    o = link(bpy.data.objects.new(name, None)); o.location = loc
    if parent: o.parent = parent
    return o

def _mesh_obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return link(bpy.data.objects.new(name, me))

def box(name, loc, size, col, bevel=0.04, parent=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x*size[0], v.co.y*size[1], v.co.z*size[2]))
    o = _mesh_obj(name, bm); o.location = loc; o.rotation_euler = rot
    if bevel:
        m = o.modifiers.new("b", 'BEVEL'); m.width = bevel; m.segments = 3; m.limit_method = 'NONE'
    return _finish(o, col, smooth=bool(bevel), parent=parent)

def sphere(name, loc, r, col, scale=(1, 1, 1), parent=None, seg=24):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg//2, radius=r)
    o = _mesh_obj(name, bm); o.location = loc; o.scale = scale
    return _finish(o, col, parent=parent)

def cyl(name, loc, r, h, col, parent=None, seg=24, rot=(0, 0, 0), r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = _mesh_obj(name, bm); o.location = loc; o.rotation_euler = rot
    m = o.modifiers.new("b", 'BEVEL'); m.width = min(r, h)*0.12; m.segments = 2; m.limit_method = 'ANGLE'
    return _finish(o, col, parent=parent)

def capsule(name, r, L, col, parent=None, loc=(0, 0, 0), seg=18):
    """cápsula colgando hacia -Z desde el origen (pivote arriba): para brazos y piernas"""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg//2+1, radius=r)
    for v in bm.verts:
        if v.co.z < 0: v.co.z -= L
    for v in bm.verts: v.co.z -= r*0.4
    o = _mesh_obj(name, bm); o.location = loc
    return _finish(o, col, parent=parent)

def plane(name, loc, size, col, rot=(0, 0, 0), parent=None):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    for v in bm.verts: v.co = Vector((v.co.x*size[0], v.co.y*size[1], 0))
    o = _mesh_obj(name, bm); o.location = loc; o.rotation_euler = rot
    return _finish(o, col, smooth=False, parent=parent)

def group(name, parent=None, loc=(0, 0, 0)):
    return empty(name, loc, parent)

def show(o, v=True):
    o.hide_render = not v
    for ch in o.children: show(ch, v)

# ---------------------------------------------------------------- cámara
CAM = None
def camera(lens=32):
    global CAM
    cd = bpy.data.cameras.new("cam"); cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24
    CAM = link(bpy.data.objects.new("cam", cd)); bpy.context.scene.camera = CAM
    tgt = empty("cam_tgt"); c = CAM.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    CAM["tgt"] = tgt.name
    return CAM

def look(pos, target, lens=None):
    CAM.location = pos; bpy.data.objects[CAM["tgt"]].location = target
    if lens: CAM.data.lens = lens

# ---------------------------------------------------------------- personaje
class Person:
    """muñeco «plastilina»: cabeza grande, cuerpo de cápsula, miembros articulados.
    look = dict(skin, hair, top, top2, legs, shoe, hair_style)"""
    def __init__(self, name, look, h=1.0):
        self.n = name; L = look; s = h
        self.root = group(name)
        self.hips = group(name+"_hips", self.root, (0, 0, 0.92*s))
        self.torso = capsule(name+"_torso", 0.16*s, 0.36*s, L['top'], self.hips, (0, 0, 0.64*s))
        self.torso.scale = (1.12, 0.62, 1.0)
        box(name+"_belt", (0, 0, 0.02*s), (0.24*s, 0.16*s, 0.08*s), L['legs'], 0.03, self.hips)
        cyl(name+"_neckc", (0, 0, 0.7*s), 0.035*s, 0.12*s, L['skin'], self.hips, 12)
        self.neck = group(name+"_neck", self.hips, (0, 0, 0.72*s))
        self.head = group(name+"_head", self.neck, (0, 0, 0.0))
        sphere(name+"_skull", (0, 0, 0.24*s), 0.22*s, L['skin'], (1, 1, 1), self.head, 32)
        # pelo
        hs = L.get('hair_style', 'messy')
        if hs == 'messy':
            sphere(name+"_hair", (0, 0.03*s, 0.3*s), 0.232*s, L['hair'], (1.04, 1.04, 0.8), self.head)
            for i, (x, y, z, r) in enumerate(((-0.1, -0.14, 0.4, 0.08), (0.0, -0.165, 0.42, 0.09), (0.1, -0.13, 0.4, 0.08), (-0.16, -0.04, 0.37, 0.075), (0.17, -0.03, 0.37, 0.075))):
                sphere(f"{name}_tuft{i}", (x*s, y*s, z*s), r*s, L['hair'], (1, 0.8, 0.7), self.head, 12)
        elif hs == 'bun':
            sphere(name+"_hair", (0, 0.04*s, 0.3*s), 0.228*s, L['hair'], (1.05, 1.05, 0.8), self.head)
            sphere(name+"_bun", (0, 0.17*s, 0.43*s), 0.1*s, L['hair'], (1, 1, 1), self.head, 16)
        elif hs == 'buzz':
            sphere(name+"_hair", (0, 0.025*s, 0.29*s), 0.226*s, L['hair'], (1.01, 1.0, 0.78), self.head)
        # cara (mira hacia -Y = hacia la cámara por defecto)
        self.eyes = []
        for sx in (-1, 1):
            self.eyes.append(sphere(f"{name}_eye{sx}", (sx*0.075*s, -0.2*s, 0.26*s), 0.022*s, "#141216", (1, 0.6, 1.25), self.head, 12))
            box(f"{name}_brow{sx}", (sx*0.075*s, -0.205*s, 0.32*s), (0.06*s, 0.015*s, 0.014*s), L['hair'], 0.005, self.head)
        self.brows = [bpy.data.objects[f"{name}_brow-1"], bpy.data.objects[f"{name}_brow1"]]
        self.mouth = box(name+"_mouth", (0, -0.21*s, 0.16*s), (0.05*s, 0.015*s, 0.01*s), "#5A2E2A", 0.004, self.head)
        if L.get('hood'):
            sphere(name+"_hood", (0, 0.1*s, 0.0), 0.15*s, L['top2'], (1.4, 0.8, 0.45), self.head, 16)
        # brazos
        self.sh = {}; self.el = {}
        for sx in (-1, 1):
            shp = group(f"{name}_sh{sx}", self.hips, (sx*0.2*s, 0, 0.66*s))
            capsule(f"{name}_ua{sx}", 0.045*s, 0.24*s, L['top'], shp)
            elb = group(f"{name}_el{sx}", shp, (0, 0, -0.29*s))
            capsule(f"{name}_fa{sx}", 0.04*s, 0.22*s, L['top'], elb)
            sphere(f"{name}_hand{sx}", (0, 0, -0.29*s), 0.048*s, L['skin'], (1, 1, 1), elb, 14)
            self.sh[sx] = shp; self.el[sx] = elb
        # piernas
        self.hp = {}; self.kn = {}
        for sx in (-1, 1):
            hpp = group(f"{name}_hp{sx}", self.hips, (sx*0.07*s, 0, -0.02*s))
            capsule(f"{name}_th{sx}", 0.055*s, 0.34*s, L['legs'], hpp)
            kn = group(f"{name}_kn{sx}", hpp, (0, 0, -0.42*s))
            capsule(f"{name}_sn{sx}", 0.05*s, 0.34*s, L['legs'], kn)
            box(f"{name}_shoe{sx}", (0, -0.05*s, -0.45*s), (0.1*s, 0.2*s, 0.08*s), L['shoe'], 0.03, kn)
            self.hp[sx] = hpp; self.kn[sx] = kn
        self.s = s

    # --- posado ---
    def face_to(self, x, y, tx, ty, z=0.0):
        self.place(x, y, math.degrees(math.atan2(tx-x, -(ty-y))), z)

    def place(self, x, y, face=0.0, z=0.0):
        """face en grados: 0 = mira a cámara (-Y), 90 = mira a +X"""
        self.root.location = (x, y, z); self.root.rotation_euler = (0, 0, math.radians(face))

    def pose(self, name="stand", t=0.0, walk=0.0, run=False, expr="neutral", look=(0, 0), lean=0.0):
        P = dict(stand=(0, 0, 0.08, 0.1, 0.08, 0.1), reach=(0, 0, 0.08, 0.1, 1.35, 0.15),
                 carry=(0, 0, 0.9, 1.0, 0.9, 1.0), think=(0, 0, 0.08, 0.1, 0.5, 2.3),
                 phone=(0, 0, 0.08, 0.1, 0.9, 1.6), alarm=(0, 0, -2.6, 0.3, -2.6, 0.3),
                 listen=(0, 0, 0.08, 0.1, 0.3, 2.5), hide=(0, 0.5, 0.6, 1.4, 0.6, 1.4),
                 sit=(1.5, 1.5, 0.3, 0.6, 0.3, 0.6), crouch=(1.1, 2.0, 0.5, 0.9, 0.5, 0.9),
                 point=(0, 0, 0.08, 0.1, 1.5, 0.0))[name]
        th, kn, la, le, ra, re = P
        s = self.s; sw = math.sin(walk*2*math.pi) if walk else 0.0
        amp = 0.9 if run else 0.5
        for sx in (-1, 1):
            k = sx*sw
            self.hp[sx].rotation_euler = (-(th + amp*k) if not walk else -amp*k, 0, 0)
            self.kn[sx].rotation_euler = (kn + (max(0, -k)*0.9 if walk else 0), 0, 0)
        arm = {-1: (la, le), 1: (ra, re)}
        for sx in (-1, 1):
            a, e = arm[sx]
            if walk and name == "stand": a = 0.08 - sx*sw*amp*0.8; e = 0.25 if not run else 1.2
            spread = 0.06 if name != "alarm" else 0.3
            self.sh[sx].rotation_euler = (-a, sx*spread*0, sx*spread)
            self.el[sx].rotation_euler = (-e, 0, 0)
        bob = abs(sw)*0.04*s if walk else math.sin(t*2.2)*0.006*s
        hz = {"sit": 0.55, "crouch": 0.6}.get(name, 0.92)*s
        self.hips.location = (0, 0, hz + bob)
        self.hips.rotation_euler = ((0.25 if run else 0.06 if walk else 0) + lean + (0.35 if name == "hide" else 0) + (0.3 if name == "crouch" else 0), 0, 0)
        self.head.rotation_euler = (-look[1]*0.4, 0, -look[0]*0.7)
        b = {"worried": (0.35, 0.01), "angry": (-0.35, -0.01), "shock": (0.0, 0.03), "focus": (-0.15, -0.005)}.get(expr, (0, 0))
        for i, sx in enumerate((-1, 1)):
            br = self.brows[i]; br.rotation_euler = (0, sx*b[0]*-1 if expr != "shock" else 0, 0); br.location.z = 0.37*s + b[1]*s
        self.mouth.scale = (0.6, 1, 3.5) if expr == "shock" else (1, 1, 1)
        blink = 1.0 < (t % 3.7) < 1.12
        for e in self.eyes: e.scale = (1, 0.6, 0.15 if blink else 1.25 if expr != "shock" else 1.5)

    def show(self, v=True): show(self.root, v)

# ---------------------------------------------------------------- utilidades
def ease(x): x = max(0, min(1, x)); return 4*x*x*x if x < .5 else 1-((-2*x+2)**3)/2
def lerp(a, b, k): return a+(b-a)*k
def lerpv(a, b, k): return tuple(lerp(x, y, k) for x, y in zip(a, b))
def clamp(x, a=0, b=1): return max(a, min(b, x))

def render_to(path):
    sc = bpy.context.scene; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
