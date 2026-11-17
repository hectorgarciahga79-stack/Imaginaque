"""Efectos visuales: lluvia, niebla volumétrica, humo de neumáticos, marcas de
derrape, explosiones (bola de fuego, metralla con física balística, chispas,
destello) y columna de humo.

Los efectos ligados a la acción usan un sistema de partículas propio,
determinista y evaluado en TIEMPO DE SIMULACIÓN: así la cámara lenta afecta
por igual a coches, humo, fuego y metralla (los sistemas de partículas de
Blender trabajan en fotogramas y no siguen un 'speed ramp').
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

from . import materials as M
from .kinematics import sample_states, smoothstep, clamp
from .vehicles import _link

G = 9.81
# 'soft': partículas de superficie con alfa (rápido en CPU)
# 'volume': volúmenes reales de Cycles (más realista; recomendado con GPU)
FX_MODE = "soft"


def _smoke_mat(name, density=1.0, color=(0.6, 0.6, 0.62), noise_scale=2.5):
    if FX_MODE == "volume":
        return _color_density_material(M.smoke_volume, name, density=density, color=color, noise_scale=noise_scale)
    return M.smoke_soft(name + "_soft", density=density * 1.1, color=color, noise_scale=noise_scale * 0.9)


def _fire_mat(name, density=2.0, temperature=1500, intensity=12):
    if FX_MODE == "volume":
        return _color_density_material(M.fire_volume, name, density=density, temperature=temperature, intensity=intensity)
    return M.fire_soft(name + "_soft", density=density * 0.7, intensity=intensity * 0.8)


def _coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def _sphere_mesh(name, r=1.0, sub=2):
    if name in bpy.data.meshes:
        return bpy.data.meshes[name]
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def _color_density_material(base_fn, name, **kw):
    """Envuelve un material de volumen para que la densidad/emisión se
    multipliquen por el alfa del color de objeto (animable por objeto)."""
    m = base_fn(name, **kw)
    nt = m.node_tree
    vol = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeVolumePrincipled")
    if "obj_alpha" in nt.nodes:
        return m
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    oi.name = "obj_alpha"
    for sock_name in ("Density", "Blackbody Intensity"):
        sock = vol.inputs[sock_name]
        if not sock.is_linked:
            continue
        src = sock.links[0].from_socket
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(src, mul.inputs[0])
        nt.links.new(oi.outputs["Alpha"], mul.inputs[1])
        nt.links.new(mul.outputs[0], sock)
    return m


# =========================================================================== lluvia
def add_rain(camera, frame_start, frame_end, time_scale=1.0, density=1.0, area=46.0, height=22.0, preroll=40):
    """Lluvia con partículas de Blender que siguen a la cámara (en XY)."""
    c = _coll("FX_Lluvia")
    me = bpy.data.meshes.new("gota")
    bm = bmesh.new()
    r = bmesh.ops.create_cone(bm, cap_ends=False, segments=4, radius1=0.0032, radius2=0.0018, depth=0.42)
    bmesh.ops.rotate(bm, verts=r["verts"], cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "Y"))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.rain_streak())
    drop = bpy.data.objects.new("gota", me)
    _link(drop, c)
    drop.hide_render = True
    drop.hide_viewport = True
    drop.visible_shadow = False
    drop.location = (0, 0, -500)

    em_me = bpy.data.meshes.new("emisor_lluvia")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=area / 2)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)  # normal hacia abajo
    bm.to_mesh(em_me)
    bm.free()
    em = bpy.data.objects.new("emisor_lluvia", em_me)
    _link(em, c)
    em.location = (0, 0, height)
    con = em.constraints.new("COPY_LOCATION")
    con.target = camera
    con.use_z = False
    em.hide_render = False
    n_frames = frame_end - frame_start + preroll
    ps_mod = em.modifiers.new("lluvia", "PARTICLE_SYSTEM")
    ps = ps_mod.particle_system.settings
    ps.count = int(220 * density * n_frames)
    ps.frame_start = frame_start - preroll
    ps.frame_end = frame_end
    ps.lifetime = 70
    ps.emit_from = "FACE"
    ps.use_emit_random = True
    ps.normal_factor = 11.0
    ps.factor_random = 1.0
    ps.object_align_factor = (0.6, 0.0, 0.0)  # viento
    ps.timestep = 0.04 * time_scale
    ps.render_type = "OBJECT"
    ps.instance_object = drop
    ps.particle_size = 1.0
    ps.size_random = 0.5
    ps.use_rotations = True
    ps.rotation_mode = "VEL"
    ps.effector_weights.gravity = 1.0
    ps_mod.particle_system.point_cache.frame_start = frame_start - preroll
    ps_mod.particle_system.point_cache.frame_end = frame_end
    ps_mod.particle_system.seed = 11
    em.show_instancer_for_render = False
    return em


# =========================================================================== niebla
def add_fog_volume(center, size, density=0.004, color=(0.75, 0.7, 0.9), anisotropy=0.35):
    """Volumen de dispersión: haces de faros y halos de neón."""
    c = _coll("FX_Niebla")
    me = bpy.data.meshes.new("niebla")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    m, nt = None, None
    m = bpy.data.materials.new("niebla_vol")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    b = M.NB(nt)
    geo = b.n("ShaderNodeNewGeometry")
    nz = b.n("ShaderNodeTexNoise", Scale=0.03, Detail=3.0)
    b.link(geo.outputs["Position"], nz.inputs["Vector"])
    sep = b.n("ShaderNodeSeparateXYZ")
    b.link(geo.outputs["Position"], sep.inputs[0])
    hfall = b.math("SUBTRACT", 1.0, b.math("DIVIDE", sep.outputs["Z"], size[2]), clamp=True)
    dens = b.math("MULTIPLY", b.math("MULTIPLY", b.math("ADD", nz.outputs["Fac"], 0.3), hfall), density)
    vol = b.n("ShaderNodeVolumeScatter")
    vol.inputs["Color"].default_value = M.rgba(color)
    vol.inputs["Anisotropy"].default_value = anisotropy
    b.link(dens, vol.inputs["Density"])
    b.out(None, vol)
    me.materials.append(m)
    ob = bpy.data.objects.new("niebla", me)
    ob.location = center
    ob.scale = size
    ob.visible_shadow = False
    return _link(ob, c)


# ====================================================== partículas en tiempo de simulación
class SimParticle:
    __slots__ = ("t0", "life", "p0", "v0", "drag", "buoy", "s0", "s1", "a0", "a1", "spin", "kind", "seed", "bounce")

    def __init__(self, t0, life, p0, v0, s0=0.3, s1=2.0, a0=1.0, a1=0.0, drag=1.5, buoy=0.0, kind="smoke",
                 spin=0.0, seed=0, bounce=False):
        self.t0, self.life, self.p0, self.v0 = t0, life, Vector(p0), Vector(v0)
        self.s0, self.s1, self.a0, self.a1 = s0, s1, a0, a1
        self.drag, self.buoy, self.kind, self.spin, self.seed, self.bounce = drag, buoy, kind, spin, seed, bounce

    def state(self, t):
        """Posición, escala, alfa en el instante t (o None si no existe)."""
        age = t - self.t0
        if age < 0 or age > self.life:
            return None
        k = self.drag
        if k > 0:
            f = (1 - math.exp(-k * age)) / k
        else:
            f = age
        acc = Vector((0, 0, self.buoy - (G if self.kind in ("debris", "spark") else 0)))
        if k > 0:
            disp = self.v0 * f + acc * ((age - f) / k)
        else:
            disp = self.v0 * age + acc * (0.5 * age * age)
        p = self.p0 + disp
        if self.bounce and p.z < 0.05:  # rebote simple contra el suelo
            p.z = 0.05 + abs(p.z - 0.05) * 0.25
        u = age / self.life
        scale = self.s0 + (self.s1 - self.s0) * (1 - (1 - u) ** 2.2)
        alpha = self.a0 + (self.a1 - self.a0) * smoothstep(0.0, 1.0, u)
        if u < 0.08:
            alpha *= u / 0.08
        return p, scale, alpha, age


class SimParticleSystem:
    """Instancia cada partícula como objeto (malla compartida) y anima
    ubicación/escala/rotación y color de objeto (densidad) por fotograma."""

    def __init__(self, name, mesh, material, coll_name="FX_Particulas"):
        self.name = name
        self.mesh = mesh
        if material and not mesh.materials:
            mesh.materials.append(material)
        self.particles = []
        self.coll = _coll(coll_name)

    def add(self, p):
        self.particles.append(p)

    def bake(self, frame_times, frame_start):
        t_first, t_last = frame_times[0], frame_times[-1]
        objs = 0
        for i, prt in enumerate(self.particles):
            if prt.t0 > t_last or prt.t0 + prt.life < t_first:
                continue
            ob = bpy.data.objects.new("%s_%d" % (self.name, i), self.mesh)
            _link(ob, self.coll)
            if prt.kind in ("smoke", "fire"):
                ob.visible_shadow = False
            objs += 1
            visible_prev = None
            for fi, t in enumerate(frame_times):
                f = frame_start + fi
                stt = prt.state(t)
                vis = stt is not None
                if vis:
                    p, s, a, age = stt
                    ob.location = p
                    ob.scale = (s, s, s * (0.75 if prt.kind == "smoke" else 1.0))
                    ob.rotation_euler = (prt.seed * 1.3 + age * prt.spin, prt.seed * 0.7, prt.seed * 2.1 + age * prt.spin * 0.5)
                    ob.color = (1, 1, 1, max(0.0, a))
                else:
                    ob.color = (1, 1, 1, 0.0)
                    ob.scale = (0.001, 0.001, 0.001)
                ob.keyframe_insert("location", frame=f) if vis else None
                ob.keyframe_insert("scale", frame=f)
                ob.keyframe_insert("rotation_euler", frame=f) if vis else None
                ob.keyframe_insert("color", frame=f)
                if visible_prev is not None and vis != visible_prev:
                    pass
                visible_prev = vis
        return objs


# =========================================================================== humo
def tire_smoke(states, wheel_offsets, t0, t1, rate=26.0, seed=1, color=(0.62, 0.6, 0.66), min_drift=0.35):
    """Genera partículas de humo en las ruedas traseras mientras derrapa."""
    rng = random.Random(seed)
    mesh = _sphere_mesh("puff", 1.0, 2)
    mat = _smoke_mat("humo_ruedas", density=0.9, color=color)
    sys = SimParticleSystem("humo", mesh.copy(), mat)
    t = t0
    dt = 1.0 / rate
    n = 0
    while t < t1:
        st = sample_states(states, t)
        if st.drifting > min_drift:
            c, s = math.cos(st.yaw), math.sin(st.yaw)
            for (ox, oy) in wheel_offsets:
                wx = st.x + c * ox - s * oy
                wy = st.y + s * ox + c * oy
                vel = Vector((math.cos(st.yaw - st.slip) * st.speed * 0.18 + rng.uniform(-1, 1),
                              math.sin(st.yaw - st.slip) * st.speed * 0.18 + rng.uniform(-1, 1),
                              rng.uniform(0.4, 1.2)))
                sys.add(SimParticle(t + rng.uniform(0, dt), rng.uniform(1.8, 2.8), (wx, wy, 0.35), vel,
                                    s0=0.35, s1=rng.uniform(2.2, 3.4), a0=st.drifting, a1=0.0, drag=1.6,
                                    buoy=0.5, kind="smoke", spin=rng.uniform(-0.6, 0.6), seed=rng.random() * 6))
                n += 1
        t += dt
    return sys


# =========================================================================== marcas
def skid_marks(states, wheel_offsets, t0, t1, frame_times, frame_start, min_drift=0.25, width=0.26):
    """Tiras de goma sobre el asfalto; cada tramo aparece cuando la rueda
    pasa (atributo 'spawn' + valor de tiempo animado en el material)."""
    c = _coll("FX_Marcas")
    m = bpy.data.materials.new("marcas_derrape")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    b = M.NB(nt)
    attr = b.n("ShaderNodeAttribute", p_attribute_name="spawn")
    tval = b.n("ShaderNodeValue")
    tval.name = "sim_time"
    vis = b.math("LESS_THAN", attr.outputs["Fac"], tval.outputs[0])
    ia = b.n("ShaderNodeAttribute", p_attribute_name="intens")
    alpha = b.math("MULTIPLY", vis, b.math("MULTIPLY", ia.outputs["Fac"], 0.85))
    p = b.n("ShaderNodeBsdfPrincipled", Roughness=0.55)
    p.inputs["Base Color"].default_value = (0.004, 0.004, 0.004, 1)
    b.link(alpha, p.inputs["Alpha"])
    b.out(p)
    me = bpy.data.meshes.new("marcas")
    bm = bmesh.new()
    spawn_l = bm.verts.layers.float.new("spawn")
    int_l = bm.verts.layers.float.new("intens")
    for (ox, oy) in wheel_offsets:
        prev = None
        t = t0
        while t < t1:
            st = sample_states(states, t)
            c_, s_ = math.cos(st.yaw), math.sin(st.yaw)
            wx = st.x + c_ * ox - s_ * oy
            wy = st.y + s_ * ox + c_ * oy
            # perpendicular a la velocidad
            vh = st.yaw - st.slip
            px, py = -math.sin(vh) * width / 2, math.cos(vh) * width / 2
            inten = clamp((st.drifting - min_drift) / 0.4, 0, 1)
            a = bm.verts.new((wx + px, wy + py, 0.006))
            bb = bm.verts.new((wx - px, wy - py, 0.006))
            for v in (a, bb):
                v[spawn_l] = t
                v[int_l] = inten
            if prev is not None:
                bm.faces.new((prev[0], prev[1], bb, a))
            prev = (a, bb)
            t += 0.02
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    ob = bpy.data.objects.new("marcas_derrape", me)
    _link(ob, c)
    for i, t in enumerate(frame_times):
        tval.outputs[0].default_value = t
        tval.outputs[0].keyframe_insert("default_value", frame=frame_start + i)
    return ob


# =========================================================================== explosión
def explosion(center, t_boom, seed=5, scale=1.0, frame_times=None, frame_start=1):
    """Explosión completa: bola de fuego volumétrica, humo negro, metralla
    balística con rebote, chispas incandescentes y destello de luz."""
    rng = random.Random(seed)
    cx, cy, cz = center
    out = {}
    fire_mat = _fire_mat("fuego_explosion", density=2.2, temperature=1500, intensity=14)
    smoke_mat = _smoke_mat("humo_negro", density=1.6, color=(0.05, 0.045, 0.045), noise_scale=1.8)
    fire = SimParticleSystem("fuego", _sphere_mesh("puff_fire", 1.0, 3).copy(), fire_mat)
    for i in range(22):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.1, 1.2))).normalized()
        sp = rng.uniform(5, 13) * scale
        fire.add(SimParticle(t_boom + rng.uniform(0, 0.12), rng.uniform(0.9, 1.6),
                             (cx + d.x * 0.5, cy + d.y * 0.5, cz + 0.6), d * sp,
                             s0=0.6 * scale, s1=rng.uniform(2.6, 4.2) * scale, a0=1.0, a1=0.0, drag=3.2,
                             buoy=3.5, kind="fire", spin=rng.uniform(-1, 1), seed=rng.random() * 6))
    smoke = SimParticleSystem("humo_neg", _sphere_mesh("puff_smoke", 1.0, 2).copy(), smoke_mat)
    for i in range(26):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.3, 1.0))).normalized()
        smoke.add(SimParticle(t_boom + 0.15 + i * 0.06, rng.uniform(3.0, 5.0),
                              (cx + d.x, cy + d.y, cz + 1.0), d * rng.uniform(2, 5) * scale,
                              s0=1.0 * scale, s1=rng.uniform(4, 7) * scale, a0=0.9, a1=0.0, drag=1.2,
                              buoy=2.5, kind="smoke", spin=rng.uniform(-0.3, 0.3), seed=rng.random() * 6))
    deb_me = bpy.data.meshes.new("metralla")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.25, v.co.y * 0.12, v.co.z * 0.05))
    bm.to_mesh(deb_me)
    bm.free()
    debris = SimParticleSystem("metralla", deb_me, M.debris())
    for i in range(36):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.4, 1.6))).normalized()
        sz = rng.uniform(0.5, 1.6)
        debris.add(SimParticle(t_boom, rng.uniform(2.0, 3.0), (cx, cy, cz + 0.6), d * rng.uniform(8, 20) * scale,
                               s0=sz, s1=sz, a0=1, a1=1, drag=0.25, kind="debris", spin=rng.uniform(4, 14),
                               seed=rng.random() * 6, bounce=True))
    sp_me = bpy.data.meshes.new("chispa")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.02, v.co.y * 0.02, v.co.z * 0.02))
    bm.to_mesh(sp_me)
    bm.free()
    sparks = SimParticleSystem("chispas", sp_me, M.emission("chispa", (1.0, 0.55, 0.12), 400))
    for i in range(70):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.2, 1.5))).normalized()
        sparks.add(SimParticle(t_boom + rng.uniform(0, 0.25), rng.uniform(0.6, 1.4), (cx, cy, cz + 0.7),
                               d * rng.uniform(10, 26) * scale, s0=1.0, s1=0.4, a0=1, a1=1, drag=0.6,
                               kind="spark", seed=rng.random() * 6, bounce=True))
    # destello: luz puntual animada
    ld = bpy.data.lights.new("destello_explosion", "POINT")
    ld.color = (1.0, 0.5, 0.15)
    ld.shadow_soft_size = 2.5
    lo = bpy.data.objects.new("destello_explosion", ld)
    lo.location = (cx, cy, cz + 2.5)
    _link(lo, _coll("FX_Particulas"))
    out.update(fire=fire, smoke=smoke, debris=debris, sparks=sparks, light=ld)
    if frame_times is not None:
        for s in (fire, smoke, debris, sparks):
            s.bake(frame_times, frame_start)
        for i, t in enumerate(frame_times):
            age = t - t_boom
            if age < 0:
                e = 0.0
            else:
                e = 6.0e4 * scale * math.exp(-age * 2.6) * (1 + 0.25 * math.sin(age * 40))
            ld.energy = e
            ld.keyframe_insert("energy", frame=frame_start + i)
    return out


def burning_wreck(center, t_start, t_end, seed=9, frame_times=None, frame_start=1):
    """Fuego persistente + humo continuo sobre un vehículo siniestrado."""
    rng = random.Random(seed)
    fire_mat = _fire_mat("fuego_restos", density=1.8, temperature=1400, intensity=10)
    smoke_mat = _smoke_mat("humo_restos", density=1.2, color=(0.07, 0.065, 0.065), noise_scale=1.6)
    fire = SimParticleSystem("llamas", _sphere_mesh("puff_fire2", 1.0, 2).copy(), fire_mat)
    smoke = SimParticleSystem("humo_col", _sphere_mesh("puff_smoke2", 1.0, 2).copy(), smoke_mat)
    cx, cy, cz = center
    t = t_start
    while t < t_end:
        fire.add(SimParticle(t, rng.uniform(0.5, 0.9), (cx + rng.uniform(-1, 1), cy + rng.uniform(-1, 1), cz + 0.8),
                             (rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(1.5, 3)),
                             s0=0.4, s1=1.3, a0=1, a1=0, drag=1.0, buoy=2.0, kind="fire", seed=rng.random() * 6))
        if rng.random() < 0.5:
            smoke.add(SimParticle(t, rng.uniform(3, 5), (cx, cy, cz + 2.0), (rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(2, 3.5)),
                                  s0=1.0, s1=4.5, a0=0.8, a1=0, drag=0.6, buoy=0.6, kind="smoke", seed=rng.random() * 6))
        t += 0.08
    if frame_times is not None:
        fire.bake(frame_times, frame_start)
        smoke.bake(frame_times, frame_start)
    return fire, smoke
