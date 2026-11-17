"""Biblioteca de materiales PBR procedurales (sin texturas externas con licencia).

Todos los materiales se generan con nodos de Blender: pintura de coche con capa
de barniz, asfalto mojado con charcos, fachadas con ventanas iluminadas al azar,
neón, agua del océano, cristal, cromo, humo/fuego volumétrico...
Se cachean por nombre para reutilizarlos entre objetos (menos memoria).
"""
import bpy

_CACHE = {}


def _new(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name], None
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return m, nt


class NB:
    """Pequeño ayudante para construir árboles de nodos de forma legible."""

    def __init__(self, nt):
        self.nt = nt
        self.x = 0

    def n(self, kind, **inputs):
        node = self.nt.nodes.new(kind)
        node.location = (self.x, 0)
        self.x += 200
        for k, v in inputs.items():
            self.set(node, k, v)
        return node

    def set(self, node, key, val):
        if isinstance(key, str) and key.startswith("p_"):
            setattr(node, key[2:], val)
            return
        sock = node.inputs[key] if not isinstance(key, int) else node.inputs[key]
        if hasattr(val, "bl_idname") or isinstance(val, bpy.types.NodeSocket):
            out = val if isinstance(val, bpy.types.NodeSocket) else val.outputs[0]
            self.nt.links.new(out, sock)
        else:
            sock.default_value = val

    def link(self, a, b):
        self.nt.links.new(a, b)

    def math(self, op, a, b=0.0, clamp=False):
        m = self.n("ShaderNodeMath", p_operation=op, p_use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                self.link(v if isinstance(v, bpy.types.NodeSocket) else v.outputs[0], m.inputs[i])
        return m.outputs[0]

    def mix_color(self, fac, a, b, blend="MIX"):
        m = self.n("ShaderNodeMix", p_data_type="RGBA", p_blend_type=blend)
        for sock, v in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            elif isinstance(v, (tuple, list)):
                sock.default_value = v
            else:
                self.link(v if isinstance(v, bpy.types.NodeSocket) else v.outputs[0], sock)
        return m.outputs[2]

    def out(self, shader, volume=None):
        o = self.n("ShaderNodeOutputMaterial")
        if shader is not None:
            self.link(shader.outputs[0] if not isinstance(shader, bpy.types.NodeSocket) else shader, o.inputs["Surface"])
        if volume is not None:
            self.link(volume.outputs[0] if not isinstance(volume, bpy.types.NodeSocket) else volume, o.inputs["Volume"])
        return o


def rgba(c, a=1.0):
    return (c[0], c[1], c[2], a)


def principled(name, color=(0.8, 0.8, 0.8), metallic=0.0, roughness=0.5, coat=0.0,
               coat_rough=0.03, emission=None, strength=0.0, alpha=1.0, transmission=0.0,
               ior=1.45, specular=0.5):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    p = b.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = rgba(color)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = coat_rough
    p.inputs["IOR"].default_value = ior
    p.inputs["Specular IOR Level"].default_value = specular
    p.inputs["Transmission Weight"].default_value = transmission
    p.inputs["Alpha"].default_value = alpha
    if emission is not None:
        p.inputs["Emission Color"].default_value = rgba(emission)
        p.inputs["Emission Strength"].default_value = strength
    b.out(p)
    return m


def emission(name, color, strength=10.0):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    e = b.n("ShaderNodeEmission")
    e.inputs["Color"].default_value = rgba(color)
    e.inputs["Strength"].default_value = strength
    b.out(e)
    return m


def car_paint(name, color, flake=0.35, rough=0.32):
    """Pintura metalizada con escamas (ruido) + barniz brillante."""
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    tc = b.n("ShaderNodeTexCoord")
    noise = b.n("ShaderNodeTexNoise", Scale=900.0, Detail=1.0)
    b.link(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = b.math("MULTIPLY", noise.outputs["Fac"], flake)
    p = b.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = rgba(color)
    p.inputs["Metallic"].default_value = 0.75
    b.link(b.math("ADD", ramp, rough - flake / 2), p.inputs["Roughness"])
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.02
    p.inputs["Coat IOR"].default_value = 1.5
    b.out(p)
    return m


def police_livery(name):
    """Librea bicolor (negro/blanco) por coordenadas de objeto: puertas blancas."""
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ")
    b.link(tc.outputs["Object"], sep.inputs[0])
    # banda blanca central (puertas) y parte inferior negra
    y = sep.outputs["Y"]
    z = sep.outputs["Z"]
    band = b.math("LESS_THAN", b.math("ABSOLUTE", b.math("SUBTRACT", y, -0.15)), 1.05)
    low = b.math("GREATER_THAN", z, 0.42)
    white = b.math("MULTIPLY", band, low)
    col = b.mix_color(white, (0.012, 0.012, 0.014, 1), (0.85, 0.86, 0.88, 1))
    p = b.n("ShaderNodeBsdfPrincipled")
    b.link(col, p.inputs["Base Color"])
    p.inputs["Metallic"].default_value = 0.3
    p.inputs["Roughness"].default_value = 0.28
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.03
    b.out(p)
    return m


def wet_asphalt(name="asfalto_mojado", wetness=0.85):
    """Asfalto con charcos: rugosidad baja en charcos, microrelieve y marcas."""
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    geo = b.n("ShaderNodeNewGeometry")
    puddle = b.n("ShaderNodeTexNoise", Scale=0.06, Detail=6.0, Roughness=0.62)
    b.link(geo.outputs["Position"], puddle.inputs["Vector"])
    pmask = b.n("ShaderNodeMapRange", **{"From Min": 0.5 - 0.06 * wetness, "From Max": 0.56 - 0.06 * wetness})
    b.link(puddle.outputs["Fac"], pmask.inputs["Value"])
    grain = b.n("ShaderNodeTexNoise", Scale=9.0, Detail=12.0, Roughness=0.7)
    b.link(geo.outputs["Position"], grain.inputs["Vector"])
    base = b.mix_color(grain.outputs["Fac"], (0.018, 0.018, 0.02, 1), (0.05, 0.048, 0.05, 1))
    wet_col = b.mix_color(pmask.outputs[0], base, (0.006, 0.006, 0.008, 1))
    rough = b.n("ShaderNodeMapRange", **{"To Min": 0.42, "To Max": 0.035})
    b.link(pmask.outputs[0], rough.inputs["Value"])
    rough2 = b.math("ADD", rough.outputs[0], b.math("MULTIPLY", grain.outputs["Fac"], 0.08))
    bump = b.n("ShaderNodeBump", Strength=0.25, Distance=0.02)
    b.link(grain.outputs["Fac"], bump.inputs["Height"])
    # gotas de lluvia en los charcos (ondas): voronoi animable por la escala
    p = b.n("ShaderNodeBsdfPrincipled")
    b.link(wet_col, p.inputs["Base Color"])
    b.link(rough2, p.inputs["Roughness"])
    b.link(bump.outputs[0], p.inputs["Normal"])
    p.inputs["Specular IOR Level"].default_value = 0.6
    b.out(p)
    return m


def facade(name, wall=(0.6, 0.55, 0.5), lit_ratio=0.3, floor_h=3.3, win_w=2.4,
           warm=(1.0, 0.55, 0.22), cool=(0.45, 0.7, 1.0), strength=2.5, seed=0.0,
           pastel=False):
    """Fachada con rejilla de ventanas; cada ventana se enciende al azar.

    Usa la posición en el mundo (metros) -> sirve para cualquier edificio
    alineado con los ejes sin necesidad de UVs.
    """
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    geo = b.n("ShaderNodeNewGeometry")
    sep = b.n("ShaderNodeSeparateXYZ")
    b.link(geo.outputs["Position"], sep.inputs[0])
    nsep = b.n("ShaderNodeSeparateXYZ")
    b.link(geo.outputs["Normal"], nsep.inputs[0])
    # coordenada horizontal: x en caras +-Y, y en caras +-X
    nx = b.math("ABSOLUTE", nsep.outputs["X"])
    selx = b.math("GREATER_THAN", nx, 0.5)
    u_val = b.n("ShaderNodeMix", p_data_type="FLOAT")
    b.link(selx, u_val.inputs[0])
    b.link(sep.outputs["X"], u_val.inputs[2])
    b.link(sep.outputs["Y"], u_val.inputs[3])
    uu = b.math("DIVIDE", u_val.outputs[0], win_w)
    vv = b.math("DIVIDE", sep.outputs["Z"], floor_h)
    fu = b.math("FRACT", uu)
    fv = b.math("FRACT", vv)
    wu = b.math("MULTIPLY", b.math("GREATER_THAN", fu, 0.24), b.math("LESS_THAN", fu, 0.76))
    wv = b.math("MULTIPLY", b.math("GREATER_THAN", fv, 0.3), b.math("LESS_THAN", fv, 0.78))
    # parteluz central
    wu = b.math("MULTIPLY", wu, b.math("GREATER_THAN", b.math("ABSOLUTE", b.math("SUBTRACT", fu, 0.5)), 0.025))
    win = b.math("MULTIPLY", wu, wv)
    # no ventanas en planta baja muy cerca del suelo ni en cubiertas
    nz = b.math("ABSOLUTE", nsep.outputs["Z"])
    vertical = b.math("LESS_THAN", nz, 0.5)
    win = b.math("MULTIPLY", win, vertical)
    # aleatorio por celda
    cell = b.n("ShaderNodeCombineXYZ")
    b.link(b.math("FLOOR", uu), cell.inputs[0])
    b.link(b.math("FLOOR", vv), cell.inputs[1])
    cell.inputs[2].default_value = seed
    wn = b.n("ShaderNodeTexWhiteNoise", p_noise_dimensions="3D")
    b.link(cell.outputs[0], wn.inputs["Vector"])
    oi = b.n("ShaderNodeObjectInfo")
    rnd = b.math("FRACT", b.math("ADD", wn.outputs["Value"], oi.outputs["Random"]))
    lit = b.math("LESS_THAN", rnd, lit_ratio)
    rnd2 = b.math("FRACT", b.math("MULTIPLY", rnd, 7.31))
    wcol = b.mix_color(b.math("GREATER_THAN", rnd2, 0.72), warm + (1,), cool + (1,))
    bright = b.math("MULTIPLY", b.math("ADD", b.math("MULTIPLY", rnd2, 0.8), 0.4), strength)
    # interior: cortinas / degradado vertical / variación por ruido
    inter = b.n("ShaderNodeTexNoise", Scale=0.9, Detail=2.0)
    b.link(geo.outputs["Position"], inter.inputs["Vector"])
    shade = b.math("ADD", b.math("MULTIPLY", inter.outputs["Fac"], 0.9), b.math("MULTIPLY", fv, 0.5))
    em_strength = b.math("MULTIPLY", b.math("MULTIPLY", b.math("MULTIPLY", lit, win), bright), shade)
    # pared
    grime = b.n("ShaderNodeTexNoise", Scale=0.35, Detail=4.0)
    b.link(geo.outputs["Position"], grime.inputs["Vector"])
    wallc = b.mix_color(b.math("MULTIPLY", grime.outputs["Fac"], 0.6), wall + (1,), (wall[0] * 0.55, wall[1] * 0.55, wall[2] * 0.55, 1))
    glass = (0.02, 0.025, 0.035, 1)
    col = b.mix_color(win, wallc, glass)
    rough = b.n("ShaderNodeMix", p_data_type="FLOAT")
    b.link(win, rough.inputs[0])
    rough.inputs[2].default_value = 0.75 if not pastel else 0.6
    rough.inputs[3].default_value = 0.08
    p = b.n("ShaderNodeBsdfPrincipled")
    b.link(col, p.inputs["Base Color"])
    b.link(rough.outputs[0], p.inputs["Roughness"])
    b.link(wcol, p.inputs["Emission Color"])
    b.link(em_strength, p.inputs["Emission Strength"])
    b.out(p)
    return m


def neon(name, color, strength=25.0, flicker=False):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    e = b.n("ShaderNodeEmission")
    e.inputs["Color"].default_value = rgba(color)
    e.inputs["Strength"].default_value = strength
    b.out(e)
    return m


def ocean(name="oceano"):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    geo = b.n("ShaderNodeNewGeometry")
    mapn = b.n("ShaderNodeMapping")
    mapn.inputs["Scale"].default_value = (0.08, 0.25, 1)
    b.link(geo.outputs["Position"], mapn.inputs["Vector"])
    wave = b.n("ShaderNodeTexNoise", Scale=1.2, Detail=8.0, Roughness=0.55)
    b.link(mapn.outputs[0], wave.inputs["Vector"])
    bump = b.n("ShaderNodeBump", Strength=0.35, Distance=0.6)
    b.link(wave.outputs["Fac"], bump.inputs["Height"])
    p = b.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (0.003, 0.012, 0.02, 1)
    p.inputs["Roughness"].default_value = 0.04
    p.inputs["Specular IOR Level"].default_value = 0.6
    b.link(bump.outputs[0], p.inputs["Normal"])
    b.out(p)
    return m


def sand(name="arena"):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    geo = b.n("ShaderNodeNewGeometry")
    nz = b.n("ShaderNodeTexNoise", Scale=3.0, Detail=10.0)
    b.link(geo.outputs["Position"], nz.inputs["Vector"])
    col = b.mix_color(nz.outputs["Fac"], (0.32, 0.27, 0.2, 1), (0.42, 0.36, 0.27, 1))
    bump = b.n("ShaderNodeBump", Strength=0.3)
    b.link(nz.outputs["Fac"], bump.inputs["Height"])
    p = b.n("ShaderNodeBsdfPrincipled", Roughness=0.9)
    b.link(col, p.inputs["Base Color"])
    b.link(bump.outputs[0], p.inputs["Normal"])
    b.out(p)
    return m


def concrete(name="hormigon", color=(0.25, 0.25, 0.26), rough=0.55, wet=True):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    geo = b.n("ShaderNodeNewGeometry")
    nz = b.n("ShaderNodeTexNoise", Scale=2.5, Detail=8.0)
    b.link(geo.outputs["Position"], nz.inputs["Vector"])
    col = b.mix_color(nz.outputs["Fac"], rgba(color), rgba(tuple(c * 0.6 for c in color)))
    p = b.n("ShaderNodeBsdfPrincipled")
    b.link(col, p.inputs["Base Color"])
    r = b.math("ADD", b.math("MULTIPLY", nz.outputs["Fac"], 0.3), rough - (0.3 if wet else 0))
    b.link(r, p.inputs["Roughness"])
    b.out(p)
    return m


def glass(name="cristal_coche", tint=(0.02, 0.025, 0.03)):
    return principled(name, color=tint, metallic=0.0, roughness=0.02, coat=1.0, specular=0.8)


def chrome(name="cromo"):
    return principled(name, color=(0.9, 0.9, 0.92), metallic=1.0, roughness=0.12)


def rubber(name="neumatico"):
    return principled(name, color=(0.018, 0.018, 0.018), roughness=0.62)


def leaf(name="hoja_palmera"):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    p = b.n("ShaderNodeBsdfPrincipled", Roughness=0.55)
    p.inputs["Base Color"].default_value = (0.03, 0.09, 0.035, 1)
    p.inputs["Subsurface Weight"].default_value = 0.0
    tr = b.n("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = (0.05, 0.15, 0.04, 1)
    mix = b.n("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.3
    b.link(p.outputs[0], mix.inputs[1])
    b.link(tr.outputs[0], mix.inputs[2])
    b.out(mix)
    return m


def bark(name="tronco"):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    tc = b.n("ShaderNodeTexCoord")
    wave = b.n("ShaderNodeTexWave", Scale=18.0, Distortion=3.0, p_wave_type="BANDS", p_bands_direction="Z")
    b.link(tc.outputs["Object"], wave.inputs["Vector"])
    col = b.mix_color(wave.outputs["Fac"], (0.09, 0.07, 0.05, 1), (0.2, 0.16, 0.11, 1))
    bump = b.n("ShaderNodeBump", Strength=0.6)
    b.link(wave.outputs["Fac"], bump.inputs["Height"])
    p = b.n("ShaderNodeBsdfPrincipled", Roughness=0.85)
    b.link(col, p.inputs["Base Color"])
    b.link(bump.outputs[0], p.inputs["Normal"])
    b.out(p)
    return m


def smoke_volume(name="humo", density=1.2, color=(0.6, 0.6, 0.62), noise_scale=2.5):
    """Volumen de humo con densidad por ruido y caída radial (esferas instanciadas)."""
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    tc = b.n("ShaderNodeTexCoord")
    oi = b.n("ShaderNodeObjectInfo")
    vadd = b.n("ShaderNodeVectorMath", p_operation="ADD")
    b.link(tc.outputs["Object"], vadd.inputs[0])
    comb = b.n("ShaderNodeCombineXYZ")
    b.link(b.math("MULTIPLY", oi.outputs["Random"], 37.0), comb.inputs[0])
    b.link(comb.outputs[0], vadd.inputs[1])
    nz = b.n("ShaderNodeTexNoise", Scale=noise_scale, Detail=6.0, Roughness=0.6)
    b.link(vadd.outputs[0], nz.inputs["Vector"])
    ln = b.n("ShaderNodeVectorMath", p_operation="LENGTH")
    b.link(tc.outputs["Object"], ln.inputs[0])
    fall = b.math("SUBTRACT", 1.0, ln.outputs["Value"], clamp=True)
    fall = b.math("POWER", fall, 0.8)
    dens = b.math("MULTIPLY", b.math("MULTIPLY", b.math("SUBTRACT", nz.outputs["Fac"], 0.35, clamp=True), fall), density * 4)
    vol = b.n("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = rgba(color)
    vol.inputs["Anisotropy"].default_value = 0.3
    b.link(dens, vol.inputs["Density"])
    b.out(None, vol)
    return m


def fire_volume(name="fuego", density=2.5, temperature=1600.0, intensity=12.0):
    """Bola de fuego: humo oscuro + emisión de cuerpo negro según el ruido."""
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    tc = b.n("ShaderNodeTexCoord")
    nz = b.n("ShaderNodeTexNoise", Scale=2.2, Detail=8.0, Roughness=0.65, Distortion=0.6)
    b.link(tc.outputs["Object"], nz.inputs["Vector"])
    ln = b.n("ShaderNodeVectorMath", p_operation="LENGTH")
    b.link(tc.outputs["Object"], ln.inputs[0])
    fall = b.math("SUBTRACT", 1.0, ln.outputs["Value"], clamp=True)
    dens = b.math("MULTIPLY", b.math("MULTIPLY", b.math("SUBTRACT", nz.outputs["Fac"], 0.3, clamp=True), fall), density * 4)
    core = b.math("POWER", b.math("SUBTRACT", 1.0, b.math("MULTIPLY", ln.outputs["Value"], 1.25), clamp=True), 1.6)
    heat = b.math("MULTIPLY", core, nz.outputs["Fac"])
    vol = b.n("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.05, 0.045, 0.04, 1)
    b.link(dens, vol.inputs["Density"])
    vol.inputs["Blackbody Intensity"].default_value = 1.0
    b.link(b.math("MULTIPLY", heat, intensity), vol.inputs["Blackbody Intensity"])
    vol.inputs["Temperature"].default_value = temperature
    m["fire_intensity_node"] = vol.name
    b.out(None, vol)
    return m


def rain_streak(name="gota_lluvia"):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    e = b.n("ShaderNodeEmission")
    e.inputs["Color"].default_value = (0.8, 0.85, 1.0, 1)
    e.inputs["Strength"].default_value = 3.0
    tr = b.n("ShaderNodeBsdfTransparent")
    mix = b.n("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.22
    b.link(tr.outputs[0], mix.inputs[1])
    b.link(e.outputs[0], mix.inputs[2])
    b.out(mix)
    return m


def light_cone(name, color=(1.0, 0.8, 0.55), strength=0.25):
    """Cono de luz 'volumétrico' barato: emisión aditiva con degradado."""
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    tc = b.n("ShaderNodeTexCoord")
    sep = b.n("ShaderNodeSeparateXYZ")
    b.link(tc.outputs["Generated"], sep.inputs[0])
    grad = b.math("POWER", sep.outputs["Z"], 2.0)
    lw = b.n("ShaderNodeLayerWeight", Blend=0.5)
    edge = b.math("SUBTRACT", 1.0, lw.outputs["Facing"])
    fac = b.math("MULTIPLY", b.math("MULTIPLY", grad, edge), strength)
    e = b.n("ShaderNodeEmission")
    e.inputs["Color"].default_value = rgba(color)
    b.link(fac, e.inputs["Strength"])
    tr = b.n("ShaderNodeBsdfTransparent")
    add = b.n("ShaderNodeAddShader")
    b.link(tr.outputs[0], add.inputs[0])
    b.link(e.outputs[0], add.inputs[1])
    b.out(add)
    m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    return m


def skid(name="marcas_derrape"):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    tc = b.n("ShaderNodeTexCoord")
    nz = b.n("ShaderNodeTexNoise", Scale=30.0, Detail=4.0)
    b.link(tc.outputs["UV"], nz.inputs["Vector"])
    p = b.n("ShaderNodeBsdfPrincipled", Roughness=0.7)
    p.inputs["Base Color"].default_value = (0.003, 0.003, 0.003, 1)
    a = b.math("MULTIPLY", nz.outputs["Fac"], 1.2, clamp=True)
    b.link(a, p.inputs["Alpha"])
    b.out(p)
    return m


def debris(name="metralla"):
    return principled(name, color=(0.04, 0.035, 0.03), metallic=0.6, roughness=0.5,
                      emission=(1.0, 0.35, 0.05), strength=4.0)


# ---------------------------------------------------------------- partículas 'soft'
def _soft_alpha(b, density, noise_scale=2.2):
    """Alfa de partícula suave: núcleo por 'facing' x ruido x alfa del objeto."""
    tc = b.n("ShaderNodeTexCoord")
    oi = b.n("ShaderNodeObjectInfo")
    off = b.n("ShaderNodeVectorMath", p_operation="ADD")
    b.link(tc.outputs["Object"], off.inputs[0])
    comb = b.n("ShaderNodeCombineXYZ")
    b.link(b.math("MULTIPLY", oi.outputs["Random"], 31.0), comb.inputs[0])
    b.link(b.math("MULTIPLY", oi.outputs["Random"], 17.0), comb.inputs[1])
    b.link(comb.outputs[0], off.inputs[1])
    nz = b.n("ShaderNodeTexNoise", Scale=noise_scale, Detail=3.0, Roughness=0.55)
    b.link(off.outputs[0], nz.inputs["Vector"])
    nm = b.n("ShaderNodeMapRange", **{"From Min": 0.32, "From Max": 0.72})
    b.link(nz.outputs["Fac"], nm.inputs["Value"])
    lw = b.n("ShaderNodeLayerWeight", Blend=0.5)
    core = b.math("POWER", b.math("SUBTRACT", 1.0, lw.outputs["Facing"], clamp=True), 3.2)
    a = b.math("MULTIPLY", b.math("MULTIPLY", core, nm.outputs[0]), oi.outputs["Alpha"])
    a = b.math("MULTIPLY", a, density, clamp=True)
    return a, nz, core


def smoke_soft(name="humo_soft", density=1.0, color=(0.6, 0.6, 0.62), noise_scale=2.2):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    a, nz, core = _soft_alpha(b, density, noise_scale)
    dif = b.n("ShaderNodeBsdfDiffuse")
    dif.inputs["Color"].default_value = rgba(color)
    tr = b.n("ShaderNodeBsdfTransparent")
    mix = b.n("ShaderNodeMixShader")
    b.link(a, mix.inputs[0])
    b.link(tr.outputs[0], mix.inputs[1])
    b.link(dif.outputs[0], mix.inputs[2])
    b.out(mix)
    return m


def fire_soft(name="fuego_soft", density=1.3, intensity=9.0):
    m, nt = _new(name)
    if nt is None:
        return m
    b = NB(nt)
    a, nz, core = _soft_alpha(b, density, 2.6)
    heat = b.math("MULTIPLY", core, nz.outputs["Fac"])
    temp = b.math("ADD", b.math("MULTIPLY", heat, 2600.0), 900.0)
    bb = b.n("ShaderNodeBlackbody")
    b.link(temp, bb.inputs["Temperature"])
    em = b.n("ShaderNodeEmission")
    b.link(bb.outputs[0], em.inputs["Color"])
    oi = b.n("ShaderNodeObjectInfo")
    b.link(b.math("MULTIPLY", b.math("MULTIPLY", b.math("POWER", heat, 1.5), intensity * 3), oi.outputs["Alpha"]), em.inputs["Strength"])
    dark = b.n("ShaderNodeBsdfDiffuse")
    dark.inputs["Color"].default_value = (0.02, 0.018, 0.016, 1)
    sm = b.n("ShaderNodeMixShader")
    b.link(b.math("POWER", heat, 0.6), sm.inputs[0])
    b.link(dark.outputs[0], sm.inputs[1])
    b.link(em.outputs[0], sm.inputs[2])
    tr = b.n("ShaderNodeBsdfTransparent")
    mix = b.n("ShaderNodeMixShader")
    b.link(a, mix.inputs[0])
    b.link(tr.outputs[0], mix.inputs[1])
    b.link(sm.outputs[0], mix.inputs[2])
    b.out(mix)
    return m
