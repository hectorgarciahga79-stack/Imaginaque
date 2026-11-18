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


# ------------------------------------------------------------------ inserto genérico
def _setup_cam(sc, keys, lens=40, fstop=2.0, frames=48):
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam_data.lens = lens
    cam_data.sensor_width = 36
    cam_data.clip_start = 0.002
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = fstop
    tgt = bpy.data.objects.new("objetivo", None)
    sc.collection.objects.link(tgt)
    tr = cam.constraints.new("TRACK_TO")
    tr.target = tgt
    cam_data.dof.focus_object = tgt
    for f, loc, t in keys:
        cam.location = loc
        tgt.location = t
        cam.keyframe_insert("location", frame=f)
        tgt.keyframe_insert("location", frame=f)
    sc.frame_start, sc.frame_end = 1, frames
    return cam


def _area(name, loc, color, energy, size=0.5, target=None):
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
    if target is not None:
        tr = L.constraints.new("TRACK_TO")
        tr.target = target
    return L


def _sirens(red, blue, frames, hi=120, lo=4, period=4):
    for f in range(1, frames + 1):
        ph = (f // period) % 2
        red.data.energy = hi if ph == 0 else lo
        blue.data.energy = lo if ph == 0 else hi * 1.15
        red.data.keyframe_insert("energy", frame=f)
        blue.data.keyframe_insert("energy", frame=f)


def _finish(sc, out_dir, name, frames, res, samples, bloom=0.8):
    R.configure(sc, {"samples": samples, "resolution": res, "motion_blur": True, "look": "AgX - Punchy"})
    R.compositor(sc, fog=0.0, bloom=bloom, mist_start=5, mist_depth=10)
    os.makedirs(out_dir, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, name + ".blend"))
    R.render_animation(sc, out_dir, 1, frames)
    return out_dir


def render_phone(out_dir, sender="Número desconocido", message="Yo también me acuerdo de vosotros.",
                 frames=60, res=(540, 960), samples=16, font=None):
    """Móvil vibrando en el asiento de cuero con un mensaje en pantalla."""
    sc = _clear()
    leather = M.principled("cuero", color=(0.035, 0.02, 0.018), roughness=0.45, coat=0.3)
    bpy.ops.mesh.primitive_plane_add(size=2)
    seat = bpy.context.object
    seat.data.materials.append(leather)
    # costuras del asiento
    stitch = M.principled("costura", color=(0.35, 0.05, 0.04), roughness=0.6)
    for x in (-0.16, 0.16):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.001))
        c = bpy.context.object
        c.scale = (0.004, 1.5, 0.002)
        c.data.materials.append(stitch)
    root = bpy.data.objects.new("movil", None)
    sc.collection.objects.link(root)
    body_m = M.principled("carcasa", color=(0.01, 0.01, 0.012), metallic=0.6, roughness=0.25)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.0045))
    body = bpy.context.object
    body.scale = (0.072, 0.152, 0.008)
    bev = body.modifiers.new("b", "BEVEL")
    bev.width = 0.006
    bev.segments = 6
    body.data.materials.append(body_m)
    body.parent = root
    screen_m = M.emission("pantalla", (0.03, 0.035, 0.05), 1.2)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0087))
    scr = bpy.context.object
    scr.scale = (0.066, 0.145, 1)
    scr.data.materials.append(screen_m)
    scr.parent = root
    bubble_m = M.emission("burbuja", (0.16, 0.17, 0.2), 1.6)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.004, -0.005, 0.0089))
    bub = bpy.context.object
    bub.scale = (0.054, 0.03, 0.0002)
    b2 = bub.modifiers.new("b", "BEVEL")
    b2.width = 0.004
    b2.segments = 4
    bub.data.materials.append(bubble_m)
    bub.parent = root
    white = M.emission("texto_blanco", (1, 1, 1), 3.0)
    grey = M.emission("texto_gris", (0.6, 0.62, 0.7), 2.0)
    red = M.emission("texto_rojo", (1.0, 0.15, 0.12), 4.0)
    words = message.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) > 16:
            lines.append(cur.strip())
            cur = ""
        cur += w + " "
    lines.append(cur.strip())
    for i, ln in enumerate(lines):
        t = _text(ln, 0.0062, (-0.004, 0.003 - i * 0.0085, 0.0092), white, extrude=0.0, font=font)
        t.parent = root
    t = _text(sender, 0.0055, (0, 0.05, 0.0092), grey, extrude=0.0, font=font)
    t.parent = root
    t = _text("03:12", 0.016, (0, 0.105, 0.0092), white, extrude=0.0, font=font)
    t.parent = root
    t = _text("1 mensaje nuevo", 0.005, (0, -0.045, 0.0092), red, extrude=0.0, font=font)
    t.parent = root
    root.rotation_euler = (0, 0, math.radians(14))
    # vibración: dos ráfagas
    for f in range(1, frames + 1):
        buzz = (8 <= f % 30 <= 16)
        root.location = ((0.0012 * math.sin(f * 2.9)) if buzz else 0.0, (0.0009 * math.cos(f * 3.7)) if buzz else 0.0, 0)
        root.rotation_euler = (0, 0, math.radians(14 + (0.8 * math.sin(f * 3.1) if buzz else 0)))
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_euler", frame=f)
    _area("luz_pantalla", (0, -0.1, 0.5), (0.7, 0.75, 1.0), 4, 0.3, root)
    _area("neon", (-0.8, 0.9, 0.6), (1.0, 0.15, 0.7), 6, 0.8, root)
    r = _area("sirena_roja", (-0.6, -0.6, 0.4), (1.0, 0.05, 0.03), 0, 0.4, root)
    b = _area("sirena_azul", (0.6, -0.6, 0.4), (0.05, 0.2, 1.0), 0, 0.4, root)
    _sirens(r, b, frames, hi=40, lo=2, period=5)
    _setup_cam(sc, [(1, (0.05, -0.32, 0.30), (0, 0.0, 0.0)), (40, (0.02, -0.17, 0.21), (-0.003, -0.002, 0.008)),
                    (frames, (0.012, -0.11, 0.165), (-0.004, -0.004, 0.009))], lens=40, fstop=2.8, frames=frames)
    return _finish(sc, out_dir, "inserto_movil", frames, res, samples)


def render_traffic_cam(out_dir, frames=48, res=(540, 960), samples=14, font=None):
    """Cámara de tráfico en un poste: LED rojo parpadeando y un flash al final."""
    sc = _clear()
    metal = M.principled("metal_gris", color=(0.18, 0.19, 0.2), metallic=0.8, roughness=0.35)
    white = M.principled("carcasa_blanca", color=(0.7, 0.72, 0.74), roughness=0.3)
    glass = M.principled("lente", color=(0.01, 0.01, 0.015), metallic=0.0, roughness=0.02, coat=1.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=3.0, location=(0, 0, 0))
    pole = bpy.context.object
    pole.rotation_euler = (0, math.radians(90), 0)
    pole.location = (-1.4, 0, 0)
    pole.data.materials.append(metal)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.05, 0, -0.16))
    box = bpy.context.object
    box.scale = (0.42, 0.16, 0.16)
    bev = box.modifiers.new("b", "BEVEL")
    bev.width = 0.02
    bev.segments = 4
    box.data.materials.append(white)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.07, 0, -0.05))
    hood = bpy.context.object
    hood.scale = (0.5, 0.2, 0.015)
    hood.data.materials.append(white)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.058, depth=0.04, location=(0.27, 0, -0.16))
    lens = bpy.context.object
    lens.rotation_euler = (0, math.radians(90), 0)
    lens.data.materials.append(glass)
    led_m = M.emission("led", (1.0, 0.02, 0.02), 30)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, location=(0.27, -0.09, -0.08))
    led = bpy.context.object
    led.data.materials.append(led_m)
    led_l = bpy.data.lights.new("led_luz", "POINT")
    led_l.color = (1, 0.05, 0.03)
    led_o = bpy.data.objects.new("led_luz", led_l)
    led_o.location = (0.3, -0.12, -0.08)
    sc.collection.objects.link(led_o)
    flash = bpy.data.lights.new("flash", "POINT")
    flash.color = (0.85, 0.9, 1.0)
    fo = bpy.data.objects.new("flash", flash)
    fo.location = (0.4, 0, -0.2)
    sc.collection.objects.link(fo)
    for f in range(1, frames + 1):
        on = (f // 6) % 2 == 0
        led_l.energy = 2.5 if on else 0.0
        led_l.keyframe_insert("energy", frame=f)
        em = led_m.node_tree.nodes.get("Emission")
        if em:
            em.inputs["Strength"].default_value = 30 if on else 0.5
            em.inputs["Strength"].keyframe_insert("default_value", frame=f)
        flash.energy = 900 if f in (frames - 9, frames - 8) else 0.0
        flash.keyframe_insert("energy", frame=f)
    # fondo: bokeh de neones y farolas lejanas
    rng = __import__("random").Random(3)
    cols = [(1.0, 0.15, 0.7), (0.1, 0.85, 1.0), (1.0, 0.75, 0.4), (0.6, 0.2, 1.0)]
    for i in range(26):
        m = M.emission("bokeh%d" % i, cols[i % 4], rng.uniform(4, 12))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rng.uniform(0.2, 0.6),
                                             location=(rng.uniform(-14, 14), rng.uniform(14, 30), rng.uniform(-6, 5)))
        bpy.context.object.data.materials.append(m)
    sky = bpy.data.worlds["mundo"].node_tree.nodes["Background"]
    sky.inputs["Color"].default_value = (0.03, 0.012, 0.05, 1)
    _area("relleno_rosa", (-1.5, -1.8, 0.6), (1.0, 0.2, 0.75), 30, 1.0, box)
    _area("relleno_cian", (1.8, -1.2, -0.8), (0.1, 0.8, 1.0), 22, 1.0, box)
    # cámara: desde abajo, acercándose a la lente (la cámara 'te mira')
    _setup_cam(sc, [(1, (1.5, -2.2, -1.0), (0.15, 0, -0.14)), (frames - 10, (0.95, -0.42, -0.25), (0.27, 0, -0.15)),
                    (frames, (0.85, -0.3, -0.2), (0.27, 0, -0.16))], lens=45, fstop=2.0, frames=frames)
    return _finish(sc, out_dir, "inserto_camara", frames, res, samples, bloom=1.0)
