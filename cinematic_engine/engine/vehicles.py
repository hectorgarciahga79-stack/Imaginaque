"""Generador procedural de vehículos (diseños originales) y su animación.

Carrocería por 'loft' de secciones superelípticas + subdivisión + pasos de
rueda por booleana. Jerarquía:

  root (sigue la trayectoria, yaw)
   ├─ body_pivot (balanceo / cabeceo de la suspensión)
   │   ├─ carrocería, habitáculo, faros, pilotos, alerón, luces reales
   │   └─ puente de luces (policía) + luces roja/azul parpadeantes
   └─ wheel_pivot_XX (giro de dirección) └─ wheel_XX (rotación)
"""
import math

import bmesh
import bpy
from mathutils import Vector

from . import materials as M
from .kinematics import sample_states

SPORTS = {
    "length": 4.56, "wheelbase": 2.66, "track": 0.84, "wheel_r": 0.345, "exp": 3.2,
    "body": [  # x, half_width, z_bottom, z_top, top_ratio
        (-2.28, 0.80, 0.38, 0.86, 0.80), (-2.15, 0.93, 0.31, 0.93, 0.85), (-1.7, 0.99, 0.27, 0.96, 0.86),
        (-0.9, 1.0, 0.26, 0.93, 0.86), (0.0, 0.99, 0.26, 0.84, 0.86), (0.9, 0.98, 0.26, 0.76, 0.86),
        (1.6, 0.95, 0.27, 0.68, 0.86), (2.05, 0.88, 0.29, 0.58, 0.84), (2.28, 0.72, 0.33, 0.48, 0.8),
    ],
    "cabin": [
        (-1.62, 0.60, 0.78, 0.86, 0.8), (-1.15, 0.74, 0.78, 1.08, 0.72), (-0.45, 0.78, 0.76, 1.17, 0.7),
        (0.2, 0.78, 0.74, 1.13, 0.7), (0.78, 0.74, 0.7, 0.84, 0.75), (0.92, 0.62, 0.68, 0.74, 0.8),
    ],
    "roof_z": 1.05, "roof_x": (-1.0, 0.25),
    "head": (2.16, 0.64, 0.6), "tail": (-2.25, 0.82), "spoiler": True,
}

POLICE = {
    "length": 5.0, "wheelbase": 2.9, "track": 0.84, "wheel_r": 0.36, "exp": 2.8,
    "body": [
        (-2.5, 0.86, 0.44, 0.95, 0.85), (-2.32, 0.94, 0.36, 1.0, 0.88), (-1.4, 0.96, 0.33, 1.0, 0.9),
        (0.0, 0.96, 0.33, 0.97, 0.9), (1.3, 0.95, 0.33, 0.93, 0.9), (2.2, 0.9, 0.35, 0.86, 0.88),
        (2.5, 0.78, 0.40, 0.72, 0.85),
    ],
    "cabin": [
        (-1.55, 0.72, 0.9, 0.99, 0.8), (-1.2, 0.82, 0.9, 1.42, 0.78), (-0.2, 0.84, 0.9, 1.5, 0.78),
        (0.6, 0.82, 0.88, 1.46, 0.78), (1.1, 0.74, 0.86, 1.0, 0.82),
    ],
    "roof_z": 1.36, "roof_x": (-1.1, 0.55),
    "head": (2.38, 0.66, 0.68), "tail": (-2.47, 0.86), "spoiler": False,
}


def _link(obj, coll):
    coll.objects.link(obj)
    return obj


def _ring(x, w, zb, zt, top_ratio, e, n=28):
    pts = []
    zc, h = (zb + zt) / 2, (zt - zb) / 2
    for i in range(n):
        th = 2 * math.pi * i / n
        c, s = math.cos(th), math.sin(th)
        ww = w * (1 + (top_ratio - 1) * max(0.0, s))
        y = ww * math.copysign(abs(c) ** (2 / e), c)
        z = zc + h * math.copysign(abs(s) ** (2 / e), s)
        pts.append((x, y, z))
    return pts


def loft(name, sections, e, coll, n=28):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for sec in sections:
        rings.append([bm.verts.new(p) for p in _ring(*sec, e, n=n)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    return _link(ob, coll)


def box(name, size, loc, coll, mat=None, bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    if mat:
        me.materials.append(mat)
    if bevel:
        md = ob.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = 2
    return _link(ob, coll)


def cylinder(name, r, depth, loc, coll, mat=None, verts=32, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=depth)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = len(p.vertices) == 4
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    return _link(ob, coll)


_WHEEL_MESH = {}


def wheel_mesh(r, coll, style="sport"):
    """Malla de rueda (neumático + llanta de radios) compartida por instancias."""
    key = (round(r, 3), style)
    if key in _WHEEL_MESH:
        return _WHEEL_MESH[key]
    tire_m = M.rubber()
    rim_m = M.chrome() if style == "sport" else M.principled("llanta_acero", (0.25, 0.25, 0.27), 1.0, 0.35)
    width = 0.27
    parts = []
    t = cylinder("tmp_tire", r, width, (0, 0, 0), coll, tire_m, 40, (math.pi / 2, 0, 0))
    bv = t.modifiers.new("b", "BEVEL")
    bv.width = 0.06
    bv.segments = 4
    parts.append(t)
    rim = cylinder("tmp_rim", r * 0.68, width + 0.012, (0, 0, 0), coll, M.principled("hueco_llanta", (0.01, 0.01, 0.01), 0, 0.6), 32, (math.pi / 2, 0, 0))
    parts.append(rim)
    nsp = 5 if style == "sport" else 6
    for i in range(nsp):
        a = 2 * math.pi * i / nsp
        sp = box("tmp_spoke", (0.07, 0.03, r * 1.3), (0, 0, 0), coll, rim_m)
        sp.location = (0, width / 2 + 0.008, 0)
        sp.rotation_euler = (0, a, 0)
        parts.append(sp)
    hub = cylinder("tmp_hub", 0.06, width + 0.03, (0, 0, 0), coll, rim_m, 16, (math.pi / 2, 0, 0))
    parts += [hub]
    # aplicar modificadores, unir en una sola malla con índices de material
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new("rueda_%s" % style)
    mats = []
    bm_all = bmesh.new()
    for p in parts:
        ev = p.evaluated_get(dg)
        tmp_me = bpy.data.meshes.new_from_object(ev)
        tmp_me.transform(p.matrix_basis)
        mname = p.data.materials[0].name
        if mname not in mats:
            mats.append(mname)
        for poly in tmp_me.polygons:
            poly.material_index = mats.index(mname)
        bm_all.from_mesh(tmp_me)
        bpy.data.meshes.remove(tmp_me)
        bpy.data.objects.remove(p, do_unlink=True)
    bm_all.to_mesh(me)
    bm_all.free()
    for mn in mats:
        me.materials.append(bpy.data.materials[mn])
    _WHEEL_MESH[key] = me
    return me


def _empty(name, coll, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.5
    e.location = loc
    e.parent = parent
    return _link(e, coll)


def build_vehicle(name, kind="sports", paint=(0.55, 0.01, 0.03), coll=None, headlights=True,
                  underglow=None, siren=False, real_lights=True):
    """Construye un vehículo completo y devuelve un dict con sus partes."""
    spec = SPORTS if kind == "sports" else POLICE
    coll = coll or bpy.context.scene.collection
    vc = bpy.data.collections.new(name)
    coll.children.link(vc)
    root = _empty(name + "_root", vc)
    piv = _empty(name + "_body", vc, root, (0, 0, 0))

    paint_m = M.car_paint("pintura_" + name, paint) if kind == "sports" else M.police_livery("librea_" + name)
    body = loft(name + "_carroceria", spec["body"], spec["exp"], vc)
    body.data.materials.append(paint_m)
    # pasos de rueda (booleana)
    wb, tr, wr = spec["wheelbase"], spec["track"], spec["wheel_r"]
    cutter_parts = []
    for sx in (-1, 1):
        c = cylinder(name + "_cut", wr + 0.07, 0.6, (sx * wb / 2, 0, wr), vc, None, 32, (math.pi / 2, 0, 0))
        c.scale = (1, 1, 4)
        cutter_parts.append(c)
    sub = body.modifiers.new("subsurf", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    for c in cutter_parts:
        bo = body.modifiers.new("arch", "BOOLEAN")
        bo.object = c
        bo.operation = "DIFFERENCE"
        bo.solver = "EXACT" if "EXACT" in [i.identifier for i in bo.bl_rna.properties["solver"].enum_items] else bo.solver
        c.hide_render = True
        c.hide_viewport = True
        c.parent = piv
    body.parent = piv

    cab = loft(name + "_cabina", spec["cabin"], spec["exp"] + 0.6, vc)
    glass_m = M.glass()
    roof_m = paint_m
    cab.data.materials.append(glass_m)
    cab.data.materials.append(roof_m)
    for p in cab.data.polygons:
        c = p.center
        if c.z > spec["roof_z"] and spec["roof_x"][0] < c.x < spec["roof_x"][1]:
            p.material_index = 1
    s2 = cab.modifiers.new("subsurf", "SUBSURF")
    s2.levels = 2
    s2.render_levels = 2
    cab.parent = piv

    # parrilla / difusor oscuro
    dark = M.principled("plastico_negro", (0.01, 0.01, 0.012), 0.0, 0.45)
    hx = spec["head"][0]
    g = box(name + "_parrilla", (0.12, 1.3, 0.12), (hx + 0.02, 0, spec["body"][-1][2] + 0.06), vc, dark, 0.03)
    g.parent = piv
    d = box(name + "_difusor", (0.2, 1.5, 0.12), (spec["tail"][0] + 0.05, 0, 0.36), vc, dark, 0.03)
    d.parent = piv

    # faros
    head_m = M.emission("faro_" + name, (0.85, 0.92, 1.0), 60.0)
    parts = {"root": root, "pivot": piv, "body": body, "cabin": cab, "coll": vc, "kind": kind}
    for sy in (-1, 1):
        h = box(name + "_faro", (0.06, 0.34, 0.06), (hx, sy * spec["head"][1], spec["head"][2]), vc, head_m, 0.02)
        h.rotation_euler = (0, 0, sy * -0.35)
        h.parent = piv
    # pilotos traseros (tira continua)
    tail_m = M.emission("piloto_" + name, (1.0, 0.02, 0.03), 18.0)
    tx, tz = spec["tail"]
    t = box(name + "_piloto", (0.04, 1.62, 0.05), (tx - 0.01, 0, tz), vc, tail_m, 0.015)
    t.parent = piv
    parts["tail_mat"] = tail_m
    # retrovisores
    for sy in (-1, 1):
        mrr = box(name + "_retrovisor", (0.16, 0.14, 0.09), (spec["cabin"][-2][0] - 0.05, sy * (spec["body"][3][1] + 0.05), spec["cabin"][-2][2] + 0.08), vc, paint_m, 0.03)
        mrr.parent = piv
    if spec["spoiler"]:
        w = box(name + "_aleron", (0.32, 1.7, 0.025), (-2.05, 0, 1.08), vc, M.principled("carbono", (0.02, 0.02, 0.022), 0.4, 0.25, coat=1.0), 0.01)
        w.parent = piv
        for sy in (-1, 1):
            st = box(name + "_soporte", (0.12, 0.03, 0.15), (-2.02, sy * 0.55, 0.99), vc, dark)
            st.parent = piv

    # luces reales: faros (spots) y luz trasera
    if real_lights and headlights:
        for sy in (-1, 1):
            ld = bpy.data.lights.new(name + "_haz", "SPOT")
            ld.energy = 900 if kind == "sports" else 700
            ld.color = (0.88, 0.93, 1.0)
            ld.spot_size = math.radians(62)
            ld.spot_blend = 0.6
            ld.shadow_soft_size = 0.05
            lo = bpy.data.objects.new(name + "_haz", ld)
            lo.location = (hx + 0.1, sy * 0.62, 0.62)
            lo.rotation_euler = (0, math.radians(90 + 7), 0)  # spot mira -Z -> girar hacia +X y un poco abajo
            lo.parent = piv
            _link(lo, vc)
        lt = bpy.data.lights.new(name + "_rojo", "AREA")
        lt.energy = 25
        lt.color = (1.0, 0.05, 0.05)
        lt.size = 1.5
        lo = bpy.data.objects.new(name + "_rojo", lt)
        lo.location = (tx - 0.15, 0, tz)
        lo.rotation_euler = (0, math.radians(-90), 0)
        lo.parent = piv
        _link(lo, vc)
        parts["tail_light"] = lt
    if underglow:
        lu = bpy.data.lights.new(name + "_neon_bajo", "AREA")
        lu.energy = 120
        lu.color = underglow
        lu.shape = "RECTANGLE"
        lu.size, lu.size_y = 3.6, 1.5
        lo = bpy.data.objects.new(name + "_neon_bajo", lu)
        lo.location = (0, 0, 0.2)
        lo.parent = piv
        _link(lo, vc)

    # puente de luces de policía
    if siren:
        base = box(name + "_puente", (0.3, 1.3, 0.08), (-0.25, 0, spec["cabin"][2][3] + 0.03), vc, dark, 0.02)
        base.parent = piv
        red_m = M.emission("sirena_roja_" + name, (1.0, 0.02, 0.02), 0.0)
        blue_m = M.emission("sirena_azul_" + name, (0.05, 0.15, 1.0), 0.0)
        for sy, mat in ((1, red_m), (-1, blue_m)):
            seg = box(name + "_sirena", (0.24, 0.55, 0.09), (-0.25, sy * 0.33, spec["cabin"][2][3] + 0.1), vc, mat, 0.02)
            seg.parent = piv
        parts["siren_mats"] = (red_m, blue_m)
        sl = []
        for sy, col in ((1, (1.0, 0.03, 0.03)), (-1, (0.05, 0.2, 1.0))):
            ld = bpy.data.lights.new(name + "_destello", "POINT")
            ld.energy = 0
            ld.color = col
            ld.shadow_soft_size = 0.15
            lo = bpy.data.objects.new(name + "_destello", ld)
            lo.location = (-0.25, sy * 0.4, spec["cabin"][2][3] + 0.35)
            lo.parent = piv
            _link(lo, vc)
            sl.append(ld)
        parts["siren_lights"] = sl

    # ruedas
    wm = wheel_mesh(wr, vc, "sport" if kind == "sports" else "steel")
    wheels = []
    for sx, front in ((1, True), (-1, False)):
        for sy in (-1, 1):
            wp = _empty("%s_pivote_%s%s" % (name, "D" if front else "T", "I" if sy > 0 else "D"), vc, root, (sx * wb / 2, sy * tr, wr))
            w = bpy.data.objects.new(name + "_rueda", wm)
            w.parent = wp
            if sy < 0:
                w.rotation_euler = (0, 0, math.pi)  # cara exterior hacia fuera
            _link(w, vc)
            wheels.append((wp, w, front, sy))
    parts["wheels"] = wheels
    parts["spec"] = spec
    return parts


def animate_vehicle(parts, states, frame_times, frame_start=1, siren_phase=0.0):
    """Inserta fotogramas clave a partir de los estados simulados.

    frame_times: lista de tiempos de simulación, uno por fotograma.
    """
    root, piv = parts["root"], parts["pivot"]
    prev_yaw = None
    for i, t in enumerate(frame_times):
        f = frame_start + i
        st = sample_states(states, t)
        yaw = st.yaw
        if prev_yaw is not None:  # continuidad del ángulo (evita saltos de 2*pi)
            while yaw - prev_yaw > math.pi:
                yaw -= 2 * math.pi
            while yaw - prev_yaw < -math.pi:
                yaw += 2 * math.pi
        prev_yaw = yaw
        root.location = (st.x, st.y, st.z)
        root.rotation_euler = (0, 0, yaw)
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
        # vibración de alta frecuencia por velocidad (asfalto)
        vib = 0.004 * min(1.0, st.speed / 30) * math.sin(t * 61.0)
        piv.location = (0, 0, vib)
        piv.rotation_euler = (st.roll, st.pitch, 0)
        piv.keyframe_insert("location", frame=f)
        piv.keyframe_insert("rotation_euler", frame=f)
        for wp, w, front, sy in parts["wheels"]:
            if front:
                wp.rotation_euler = (0, 0, st.steer)
                wp.keyframe_insert("rotation_euler", frame=f)
            spin = st.wheel_rot if sy > 0 else -st.wheel_rot
            w.rotation_euler = (0, spin, 0 if sy > 0 else math.pi)
            w.keyframe_insert("rotation_euler", frame=f)
        # luces de freno
        tm = parts.get("tail_mat")
        if tm:
            node = tm.node_tree.nodes.get("Emission")
            node.inputs["Strength"].default_value = 18.0 if st.lon_acc > -4 else 70.0
            node.inputs["Strength"].keyframe_insert("default_value", frame=f)
        if "siren_mats" in parts:
            # patrón de destellos rojo/azul en tiempo de simulación
            ph = (t + siren_phase) * 7.5
            red_on = 1.0 if (int(ph) % 2 == 0 and (ph % 1) < 0.7) else 0.0
            blue_on = 1.0 if (int(ph) % 2 == 1 and (ph % 1) < 0.7) else 0.0
            for mat, on in zip(parts["siren_mats"], (red_on, blue_on)):
                node = mat.node_tree.nodes.get("Emission")
                node.inputs["Strength"].default_value = 3.0 + 90.0 * on
                node.inputs["Strength"].keyframe_insert("default_value", frame=f)
            for ld, on in zip(parts["siren_lights"], (red_on, blue_on)):
                ld.energy = 15 + 2600 * on
                ld.keyframe_insert("energy", frame=f)
