"""Planos detalle ('insertos') rápidos para historias cortas.

Un inserto es un plano macro barato de renderizar (pocos objetos, 540x960)
que muestra el objeto clave de una historia: una placa en el asfalto, un
mensaje, una llave... Sirven para los 'reveals' que el metraje de la
persecución no tiene. Todo es procedural y original.

Uso:  python run.py inserto --tipo placa --texto "R. VEGA" -o projects/x/renders/insertos/placa
"""
import math
import os

import bpy

from . import materials as M
from . import render as R


def _clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    w = bpy.data.worlds.new("mundo")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.012, 0.006, 0.02, 1)
    bg.inputs["Strength"].default_value = 1.0
    return sc


def _asphalt_macro():
    """Asfalto mojado a escala de centímetros (grano, gravilla y charco)."""
    m, nt = M._new("asfalto_macro")
    b = M.NB(nt)
    geo = b.n("ShaderNodeNewGeometry")
    vor = b.n("ShaderNodeTexVoronoi", Scale=150.0, Randomness=1.0)
    b.link(geo.outputs["Position"], vor.inputs["Vector"])
    fine = b.n("ShaderNodeTexNoise", Scale=180.0, Detail=8.0, Roughness=0.7)
    b.link(geo.outputs["Position"], fine.inputs["Vector"])
    puddle = b.n("ShaderNodeTexNoise", Scale=2.2, Detail=4.0)
    b.link(geo.outputs["Position"], puddle.inputs["Vector"])
    pm = b.n("ShaderNodeMapRange", **{"From Min": 0.47, "From Max": 0.53})
    b.link(puddle.outputs["Fac"], pm.inputs["Value"])
    stones = b.mix_color(vor.outputs["Distance"], (0.035, 0.034, 0.037, 1), (0.01, 0.01, 0.012, 1))
    col = b.mix_color(pm.outputs[0], stones, (0.004, 0.004, 0.006, 1))
    rough = b.n("ShaderNodeMapRange", **{"To Min": 0.38, "To Max": 0.02})
    b.link(pm.outputs[0], rough.inputs["Value"])
    bump = b.n("ShaderNodeBump", Strength=0.18, Distance=0.0015)
    b.link(b.math("ADD", vor.outputs["Distance"], b.math("MULTIPLY", fine.outputs["Fac"], 0.4)), bump.inputs["Height"])
    p = b.n("ShaderNodeBsdfPrincipled")
    b.link(col, p.inputs["Base Color"])
    b.link(rough.outputs[0], p.inputs["Roughness"])
    b.link(bump.outputs[0], p.inputs["Normal"])
    b.out(p)
    return m


def _star(name, r_out=0.032, r_in=0.017, points=6, depth=0.004):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = []
    for i in range(points * 2):
        a = math.pi / 2 + i * math.pi / points
        r = r_out if i % 2 == 0 else r_in
        verts.append(bm.verts.new((r * math.cos(a), r * math.sin(a), 0)))
    f = bm.faces.new(verts)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += depth
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bev = ob.modifiers.new("bisel", "BEVEL")
    bev.width = 0.0012
    bev.segments = 3
    for p in me.polygons:
        p.use_smooth = True
    return ob


def _text(body, size, loc, mat, extrude=0.0006, font=None, rot=0.0):
    cu = bpy.data.curves.new("txt_" + body[:8], "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = extrude
    if font and os.path.exists(font):
        cu.font = bpy.data.fonts.load(font)
    ob = bpy.data.objects.new("txt_" + body[:8], cu)
    ob.location = loc
    ob.rotation_euler = (0, 0, rot)
    ob.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build_badge(name_text="R. VEGA", number="4471", city="COSTA NEON", font=None):
    """Placa de policía ficticia (estrella de 6 puntas + chapa con nombre)."""
    gold = M.principled("oro", color=(1.0, 0.77, 0.4), metallic=1.0, roughness=0.17)
    dark = M.principled("esmalte", color=(0.02, 0.03, 0.08), metallic=0.2, roughness=0.35)
    root = bpy.data.objects.new("placa", None)
    bpy.context.scene.collection.objects.link(root)
    star = _star("estrella")
    star.data.materials.append(gold)
    star.parent = root
    # disco central esmaltado
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.0115, depth=0.0016, location=(0, 0, 0.0046))
    disc = bpy.context.object
    disc.data.materials.append(dark)
    disc.parent = root
    for tx, sz, y in ((city, 0.0034, 0.0035), ("POLICIA", 0.0040, -0.0005), (number, 0.0034, -0.0048)):
        t = _text(tx, sz, (0, y, 0.0055), gold, extrude=0.0002, font=font)
        t.parent = root
    # chapa con el nombre
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.047, 0.0018))
    plate = bpy.context.object
    plate.scale = (0.046, 0.011, 0.0018)
    bev = plate.modifiers.new("bisel", "BEVEL")
    bev.width = 0.001
    bev.segments = 2
    plate.data.materials.append(gold)
    plate.parent = root
    t = _text(name_text, 0.0078, (0, -0.0472, 0.0029), dark, extrude=0.0003, font=font)
    t.parent = root
    root["chapa"] = plate.name
    root.rotation_euler = (math.radians(2.5), math.radians(-1.5), math.radians(-17))
    root.location = (0, 0.01, 0.0005)
    return root


def render_badge(out_dir, name_text="R. VEGA", frames=72, res=(540, 960), samples=16, font=None):
    """Plano de la placa en el asfalto mojado: 'push-in' lento (1-48) y
    acercamiento rápido al nombre (49-72), con luces de sirena alternas."""
    sc = _clear()
    bpy.ops.mesh.primitive_plane_add(size=3)
    ground = bpy.context.object
    ground.data.materials.append(_asphalt_macro())
    build_badge(name_text, font=font)
    # agua: lámina fina para reflejos en el charco
    # luces: neón rosa y cian de fondo, sirenas roja/azul alternas
    def area(name, loc, color, energy, size=0.6):
        bpy.ops.object.light_add(type="AREA", location=loc)
        L = bpy.context.object
        L.name = name
        L.data.color = color
        L.data.energy = energy
        L.data.size = size
        try:
            L.visible_camera = False
        except Exception:
            pass
        tr = L.constraints.new("TRACK_TO")
        tr.target = bpy.data.objects["placa"]
        return L

    area("neon_rosa", (-1.2, 1.4, 1.3), (1.0, 0.16, 0.75), 22)
    area("neon_cian", (1.2, 1.4, 0.4), (0.1, 0.85, 1.0), 30)
    area("farola", (0.2, -0.4, 1.6), (1.0, 0.8, 0.55), 28, 0.4)
    red = area("sirena_roja", (-0.7, 0.9, 0.25), (1.0, 0.05, 0.03), 0, 0.25)
    blue = area("sirena_azul", (0.7, 0.9, 0.25), (0.05, 0.2, 1.0), 0, 0.25)
    for f in range(1, frames + 1):
        ph = (f // 4) % 2
        red.data.energy = 140 if ph == 0 else 6
        blue.data.energy = 6 if ph == 0 else 160
        red.data.keyframe_insert("energy", frame=f)
        blue.data.keyframe_insert("energy", frame=f)
    # cámara
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam_data.lens = 40
    cam_data.clip_start = 0.002
    cam_data.sensor_width = 36
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 2.2
    tgt = bpy.data.objects.new("objetivo", None)
    sc.collection.objects.link(tgt)
    tr = cam.constraints.new("TRACK_TO")
    tr.target = tgt
    cam_data.dof.focus_object = tgt
    bpy.context.view_layer.update()
    pl = bpy.data.objects[bpy.data.objects["placa"]["chapa"]].matrix_world.translation
    px, py = pl.x, pl.y
    keys = [  # (frame, cam_loc, target)
        (1, (0.05, -0.25, 0.16), (-0.004, -0.008, 0.0)),
        (48, (0.03, -0.18, 0.115), (-0.006, -0.012, 0.0)),
        (56, (px + 0.012, py - 0.075, 0.05), (px, py, 0.002)),
        (72, (px + 0.008, py - 0.064, 0.043), (px, py, 0.002)),
    ]
    for f, loc, t in keys:
        cam.location = loc
        tgt.location = t
        cam.keyframe_insert("location", frame=f)
        tgt.keyframe_insert("location", frame=f)
    for ob in (cam, tgt):
        if ob.animation_data and ob.animation_data.action:
            try:
                for fc in ob.animation_data.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = "BEZIER"
            except Exception:
                pass
    sc.frame_start, sc.frame_end = 1, frames
    R.configure(sc, {"samples": samples, "resolution": res, "motion_blur": True, "look": "AgX - Punchy"})
    R.compositor(sc, fog=0.0, bloom=0.8, mist_start=5, mist_depth=10)
    os.makedirs(out_dir, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "inserto_placa.blend"))
    R.render_animation(sc, out_dir, 1, frames)
    return out_dir
