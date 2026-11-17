"""Configuración de render (Cycles) y composición en Blender.

* Perfiles de calidad adaptados al hardware (ver hardware.py / profiles).
* Motion blur real (obturador 180º), profundidad de campo física.
* Composición: niebla atmosférica por pase 'Mist', bloom (Glare), destellos
  en luces intensas, aberración cromática y viñeteado suave.
* Render por lotes con reanudación (no sobreescribe fotogramas existentes).
"""
import os

import bpy


def configure(scene, profile, device_cfg=None):
    r = scene.render
    r.engine = "CYCLES"
    c = scene.cycles
    c.samples = profile["samples"]
    c.use_adaptive_sampling = True
    c.adaptive_threshold = profile.get("adaptive_threshold", 0.03)
    c.use_denoising = True
    try:
        c.denoiser = "OPENIMAGEDENOISE"
        c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
        c.denoising_prefilter = "ACCURATE"
    except Exception:
        pass
    c.max_bounces = 6
    c.diffuse_bounces = profile.get("diffuse_bounces", 2)
    c.glossy_bounces = profile.get("glossy_bounces", 3)
    c.transmission_bounces = 4
    c.volume_bounces = 0
    c.transparent_max_bounces = 12
    c.caustics_reflective = False
    c.caustics_refractive = False
    c.sample_clamp_indirect = 6.0
    c.sample_clamp_direct = 0.0
    c.blur_glossy = 1.0
    c.use_light_tree = True
    c.volume_step_rate = profile.get("volume_step_rate", 2.0)
    c.volume_max_steps = 256
    c.light_sampling_threshold = 0.01
    c.texture_limit_render = profile.get("texture_limit", "OFF")
    c.seed = 0
    c.use_animated_seed = True  # ruido distinto por fotograma -> grano natural tras denoise
    # dispositivo
    dev = (device_cfg or {}).get("device", "CPU")
    c.device = "GPU" if dev == "GPU" else "CPU"
    if dev == "GPU":
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = device_cfg["backend"]
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.name in device_cfg.get("devices", []) or (d.type == "CPU" and device_cfg.get("hybrid", False))
    r.threads_mode = "AUTO"
    try:  # compositor en CPU salvo que haya GPU (evita contexto gráfico en servidores)
        r.compositor_device = "GPU" if dev == "GPU" else "CPU"
    except Exception:
        pass
    r.use_persistent_data = True  # reutiliza BVH/escena entre fotogramas
    # salida
    r.resolution_x, r.resolution_y = profile["resolution"]
    r.resolution_percentage = 100
    r.fps = profile.get("fps", 24)
    r.use_motion_blur = profile.get("motion_blur", True)
    r.motion_blur_shutter = 0.5
    r.film_transparent = False
    r.image_settings.file_format = "PNG"
    r.image_settings.color_depth = "16" if profile.get("png16", False) else "8"
    r.image_settings.compression = 15
    r.use_overwrite = False
    r.use_placeholder = True
    # gestión de color
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = profile.get("look", "AgX - Punchy")
    scene.view_settings.exposure = profile.get("exposure", 0.0)
    scene.view_settings.gamma = 1.0


def compositor(scene, fog=0.5, fog_color=(0.13, 0.07, 0.16), bloom=0.6, mist_start=25.0, mist_depth=420.0,
               dispersion=0.012, streaks=0.0):
    """Árbol de composición (API de nodos de Blender 5.x con fallback)."""
    vl = scene.view_layers[0]
    vl.use_pass_mist = True
    w = scene.world
    if w is not None:
        w.mist_settings.start = mist_start
        w.mist_settings.depth = mist_depth
        w.mist_settings.falloff = "QUADRATIC"
    ng = bpy.data.node_groups.new("Composicion", "CompositorNodeTree")
    try:
        scene.compositing_node_group = ng
    except Exception:
        scene.use_nodes = True
    nodes, links = ng.nodes, ng.links
    rl = nodes.new("CompositorNodeRLayers")
    rl.scene = scene
    img = rl.outputs["Image"]
    # niebla atmosférica: mezcla hacia el color de niebla según el pase Mist
    if fog > 0:
        mul = nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        links.new(rl.outputs["Mist"], mul.inputs[0])
        mul.inputs[1].default_value = fog
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MIX"
        links.new(mul.outputs[0], mix.inputs[0])
        links.new(img, mix.inputs[6])
        mix.inputs[7].default_value = (*fog_color, 1.0)
        img = mix.outputs[2]
    # bloom
    if bloom > 0:
        g = nodes.new("CompositorNodeGlare")
        _set(g, "Type", "Bloom", "glare_type", "BLOOM")
        _set(g, "Quality", "High", "quality", "HIGH")
        _set(g, "Threshold", 0.9, "threshold", 0.9)
        _set(g, "Strength", bloom, "mix", bloom - 1)
        _set(g, "Size", 0.75, "size", 8)
        links.new(img, g.inputs["Image"])
        img = g.outputs[0]
    if streaks > 0:
        g2 = nodes.new("CompositorNodeGlare")
        _set(g2, "Type", "Streaks", "glare_type", "STREAKS")
        _set(g2, "Threshold", 6.0, "threshold", 6.0)
        _set(g2, "Strength", streaks, "mix", streaks - 1)
        _set(g2, "Streaks", 2, "streaks", 2)
        _set(g2, "Fade", 0.85, "fade", 0.85)
        links.new(img, g2.inputs["Image"])
        img = g2.outputs[0]
    if dispersion > 0:
        ld = nodes.new("CompositorNodeLensdist")
        ld.inputs["Dispersion"].default_value = dispersion
        try:
            ld.inputs["Distortion"].default_value = -0.01
        except Exception:
            pass
        links.new(img, ld.inputs["Image"])
        img = ld.outputs[0]
    out = _group_output(ng)
    links.new(img, out)
    return ng


def _set(node, sock, val, attr=None, attr_val=None):
    if sock in node.inputs:
        s = node.inputs[sock]
        try:
            s.default_value = val
            return
        except Exception:
            pass
    if attr and hasattr(node, attr):
        setattr(node, attr, attr_val)


def _group_output(ng):
    try:
        ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        o = ng.nodes.new("NodeGroupOutput")
        return o.inputs[0]
    except Exception:
        o = ng.nodes.new("CompositorNodeComposite")
        return o.inputs[0]


def render_animation(scene, out_dir, frame_start, frame_end, step=1):
    os.makedirs(out_dir, exist_ok=True)
    # reanudación: borrar marcadores vacíos de renders interrumpidos
    for fn in os.listdir(out_dir):
        fp = os.path.join(out_dir, fn)
        if fn.endswith(".png") and os.path.getsize(fp) == 0:
            os.remove(fp)
    scene.render.filepath = os.path.join(out_dir, "")
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    scene.frame_step = step
    bpy.ops.render.render(animation=True)
