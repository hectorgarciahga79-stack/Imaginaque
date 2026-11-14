"""vox — motor 3D de bloques (original) para la prueba «El control del tiempo».
Blender bpy + Workbench (texturas pixeladas con filtro Closest, sombras, contorno, DOF).
Todo se construye por código: sin modelos, texturas ni personajes de terceros."""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))
def s2l(c): return tuple(((x+0.055)/1.055)**2.4 if x > 0.04045 else x/12.92 for x in c)
def ease(x): x = max(0.0, min(1.0, x)); return x*x*(3-2*x)
def eio(x): x = max(0.0, min(1.0, x)); return 4*x**3 if x < .5 else 1-((-2*x+2)**3)/2
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, k): return a+(b-a)*k
def lerpv(a, b, k): return tuple(lerp(x, y, k) for x, y in zip(a, b))

# ------------------------------------------------------------------ escena
def reset(res=(720, 1280)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'
    try: sh.studio_light = 'outdoor.sl'
    except Exception: pass
    sh.color_type = 'TEXTURE'
    sh.show_shadows = True; sh.shadow_intensity = 0.45
    sh.show_cavity = True; sh.cavity_type = 'WORLD'
    sh.cavity_ridge_factor = 0.4; sh.cavity_valley_factor = 0.9
    sh.show_object_outline = False
    sh.show_specular_highlight = True
    sc.display.light_direction = (0.5, -0.45, 0.75)
    sc.display.shadow_shift = 0.05; sc.display.shadow_focus = 0.4
    sc.display.render_aa = '5'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new("w"); sc.world = w
    return sc

def world_color(col):
    bpy.context.scene.world.color = s2l(hexc(col) if isinstance(col, str) else col)

def light_dir(v): bpy.context.scene.display.light_direction = v
def shadow(k): bpy.context.scene.display.shading.shadow_intensity = k

# ------------------------------------------------------------------ materiales
_M = {}
def mat(col):
    col = hexc(col) if isinstance(col, str) else col
    key = ('c',)+tuple(round(x, 3) for x in col)
    if key not in _M:
        m = bpy.data.materials.new(f"m{len(_M)}"); m.diffuse_color = (*s2l(col), 1); m.roughness = 0.7
        _M[key] = m
    return _M[key]

def pix_image(name, base, n=16, var=0.10, seed=1, pattern=None):
    """textura pixelada n×n: color base con variación por píxel (o un patrón propio)"""
    if ('i', name) in _M: return _M[('i', name)]
    r = np.random.default_rng(seed)
    b = np.array(hexc(base) if isinstance(base, str) else base)
    px = np.clip(b[None, None, :]*(1+r.uniform(-var, var, (n, n, 1))), 0, 1)
    if pattern is not None: px = pattern(px, r)
    img = bpy.data.images.new(name, n, n)
    rgba = np.concatenate([px, np.ones((n, n, 1))], 2).astype(np.float32)
    img.pixels = rgba.ravel()
    _M[('i', name)] = img
    return img

def tmat(name, base, n=16, var=0.10, seed=1, pattern=None):
    key = ('t', name)
    if key in _M: return _M[key]
    img = pix_image(name, base, n, var, seed, pattern)
    m = bpy.data.materials.new("t_"+name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.interpolation = 'Closest'
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    m.diffuse_color = (*s2l(hexc(base) if isinstance(base, str) else base), 1)
    _M[key] = m
    return m

# ------------------------------------------------------------------ geometría
def link(o): bpy.context.scene.collection.objects.link(o); return o
def empty(name, loc=(0, 0, 0), parent=None):
    o = link(bpy.data.objects.new(name, None)); o.location = loc
    if parent: o.parent = parent
    return o
group = empty

def _cube_bm(bm, c, s, uvs=True, tile=1.0):
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r['verts']
    for v in vs: v.co = Vector((c[0]+v.co.x*s[0], c[1]+v.co.y*s[1], c[2]+v.co.z*s[2]))
    return vs

def _uv_box(bm, tile):
    """UV por cara proporcional al tamaño (texel constante): `tile` unidades = 1 textura"""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for l in f.loops:
            l[uv].uv = (l.vert.co[a]/tile, l.vert.co[b]/tile)

def box(name, loc, size, m, parent=None, rot=(0, 0, 0), tile=1.0, origin=None):
    """caja de tamaño `size` centrada en loc. origin=(ox,oy,oz) desplaza el pivote dentro de la caja"""
    bm = bmesh.new(); off = origin or (0, 0, 0)
    _cube_bm(bm, (-off[0], -off[1], -off[2]), size)
    bm.normal_update(); _uv_box(bm, tile)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me)); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(m if not isinstance(m, str) else mat(m))
    if parent: o.parent = parent
    return o

class Batch:
    """muchas cajas en un solo objeto (decorados estáticos rápidos). add(c, s, mat)"""
    def __init__(self, name, parent=None, tile=1.0):
        self.name = name; self.parent = parent; self.tile = tile
        self.bm = bmesh.new(); self.mats = []; self.idx = {}
    def add(self, c, s, m):
        m = m if not isinstance(m, str) else mat(m)
        if m.name not in self.idx: self.idx[m.name] = len(self.mats); self.mats.append(m)
        vs = _cube_bm(self.bm, c, s)
        fs = {f for v in vs for f in v.link_faces}
        for f in fs: f.material_index = self.idx[m.name]
    def done(self, loc=(0, 0, 0)):
        self.bm.normal_update(); _uv_box(self.bm, self.tile)
        me = bpy.data.meshes.new(self.name); self.bm.to_mesh(me); self.bm.free()
        for m in self.mats: me.materials.append(m)
        o = link(bpy.data.objects.new(self.name, me)); o.location = loc
        if self.parent: o.parent = self.parent
        return o

_KIDS = {}; DES = {}
def show(o, v=True):
    DES[o.name] = (o, not v)
    k = _KIDS.get(o.name)
    if k is None: k = _KIDS[o.name] = list(o.children)
    for ch in k: show(ch, v)
def hid(o, h):
    DES[o.name] = (o, bool(h))
def apply_vis():
    for o, h in DES.values():
        if o.hide_render != h: o.hide_render = h
    DES.clear()

# ------------------------------------------------------------------ cámara
CAM = None
def camera(lens=30):
    global CAM
    cd = bpy.data.cameras.new("cam"); cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24
    cd.clip_start = 0.05; cd.clip_end = 400
    CAM = link(bpy.data.objects.new("cam", cd)); bpy.context.scene.camera = CAM
    tgt = empty("cam_tgt")
    c = CAM.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    CAM["tgt"] = tgt.name
    return CAM

def look(pos, target, lens=None, fstop=None, roll=0.0):
    CAM.location = pos; t = bpy.data.objects[CAM["tgt"]]; t.location = target
    if lens: CAM.data.lens = lens
    d = CAM.data.dof
    if fstop:
        d.use_dof = True; d.aperture_fstop = fstop
        d.focus_distance = (Vector(pos)-Vector(target)).length
    else:
        d.use_dof = False

def render_to(path):
    sc = bpy.context.scene; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
