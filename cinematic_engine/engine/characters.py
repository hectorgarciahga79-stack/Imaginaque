"""Personajes secundarios (peatones) con ciclo de andar/correr procedural.

Figuras estilizadas de baja poligonización (cápsulas) con jerarquía de
articulaciones (cadera, hombros, rodillas). El ciclo se calcula en tiempo de
simulación, por lo que también se ralentiza en cámara lenta.
"""
import math
import random

import bpy

from . import materials as M
from .vehicles import _link, _empty, cylinder
from .fx import _sphere_mesh, _coll

CLOTHES = [(0.8, 0.15, 0.3), (0.1, 0.5, 0.7), (0.9, 0.85, 0.8), (0.15, 0.15, 0.18), (0.95, 0.6, 0.1), (0.3, 0.7, 0.4)]
SKIN = [(0.75, 0.55, 0.42), (0.55, 0.38, 0.27), (0.35, 0.22, 0.15), (0.9, 0.72, 0.6)]


def _limb(name, r, length, mat, coll, parent):
    ob = cylinder(name, r, length, (0, 0, -length / 2), coll, mat, 10)
    sub = ob.modifiers.new("s", "SUBSURF")
    sub.levels = sub.render_levels = 1
    ob.parent = parent
    return ob


def build_pedestrian(name, seed=0, coll=None):
    rng = random.Random(seed)
    coll = coll or _coll("Personajes")
    shirt = M.principled("ropa_%d" % (seed % 6), CLOTHES[seed % 6], 0, 0.7)
    pants = M.principled("pantalon_%d" % (seed % 3), CLOTHES[(seed + 3) % 6], 0, 0.8)
    skin = M.principled("piel_%d" % (seed % 4), SKIN[seed % 4], 0, 0.5)
    h = rng.uniform(0.92, 1.08)
    root = _empty(name, coll)
    hips = _empty(name + "_cadera", coll, root, (0, 0, 0.95 * h))
    torso = cylinder(name + "_torso", 0.19, 0.62 * h, (0, 0, 0.3 * h), coll, shirt, 12)
    torso.scale = (1.0, 0.65, 1.0)
    torso.parent = hips
    s = torso.modifiers.new("s", "SUBSURF")
    s.levels = s.render_levels = 2
    head = bpy.data.objects.new(name + "_cabeza", _sphere_mesh("cabeza", 0.12, 2))
    head.data.materials.clear() if False else None
    head.location = (0, 0, 0.78 * h)
    head.parent = hips
    head.active_material = skin
    _link(head, coll)
    joints = {}
    for side in (-1, 1):
        hipj = _empty(name + "_pierna%d" % side, coll, hips, (0, side * 0.1, 0))
        thigh = _limb(name + "_muslo", 0.075, 0.45 * h, pants, coll, hipj)
        knee = _empty(name + "_rodilla%d" % side, coll, hipj, (0, 0, -0.45 * h))
        _limb(name + "_gemelo", 0.06, 0.45 * h, pants, coll, knee)
        sh = _empty(name + "_hombro%d" % side, coll, hips, (0, side * 0.25, 0.55 * h))
        _limb(name + "_brazo", 0.05, 0.6 * h, shirt if rng.random() < 0.5 else skin, coll, sh)
        joints[side] = (hipj, knee, sh)
    return {"root": root, "hips": hips, "joints": joints, "height": h}


def animate_pedestrian(p, start, direction, speed, frame_times, frame_start, phase=0.0, run_from=None):
    """Anima el desplazamiento lineal + ciclo de piernas/brazos.

    run_from: (t, nueva_dirección, nueva_velocidad) para reaccionar (huir).
    """
    root, hips = p["root"], p["hips"]
    x, y = start
    prev_t = None
    cyc = phase
    d, v = direction, speed
    for i, t in enumerate(frame_times):
        f = frame_start + i
        if prev_t is not None:
            dt = t - prev_t
            if run_from and t >= run_from[0]:
                d, v = run_from[1], run_from[2]
            x += math.cos(d) * v * dt
            y += math.sin(d) * v * dt
            cyc += dt * v * 1.15 * math.pi
        prev_t = t
        root.location = (x, y, 0.15)
        root.rotation_euler = (0, 0, d)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
        amp = 0.45 if v < 2 else 0.85
        hips.location = (0, 0, 0.95 * p["height"] + 0.03 * abs(math.sin(cyc)))
        hips.rotation_euler = (0, 0.08 if v > 2 else 0.0, 0)
        hips.keyframe_insert("location", frame=f)
        hips.keyframe_insert("rotation_euler", frame=f)
        for side in (-1, 1):
            hipj, knee, sh = p["joints"][side]
            ph = cyc + (0 if side > 0 else math.pi)
            hipj.rotation_euler = (0, -amp * math.sin(ph), 0)
            knee.rotation_euler = (0, amp * 1.2 * max(0.0, math.sin(ph + 1.4)), 0)
            sh.rotation_euler = (0, amp * 0.9 * math.sin(ph), 0)
            for j in (hipj, knee, sh):
                j.keyframe_insert("rotation_euler", frame=f)
