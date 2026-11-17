"""Sistema de cámaras cinematográficas.

Una cámara se describe en el guion como una lista de 'keys' en tiempo de
pantalla relativo al plano. Cada key define:
  pos:    {"world": [x,y,z]}  o  {"actor": "heroe", "offset": [adelante, izquierda, arriba],
                                   "space": "local"|"world"|"heading"}
  target: igual que pos (punto al que mira)
  lens, roll (grados, plano holandés), fstop (opcional)
Entre keys se interpola con easing; después se aplica un filtro de muelle
crítico (inercia de operador/grúa/dron) y vibración procedural (cámara en
mano, motor, dron). El foco sigue al actor 'focus' (profundidad de campo).

Tipos de movimiento resultantes: aéreo/dron, travelling, seguimiento de
vehículos, órbita, grúa, plano fijo con panorámica, cámara frontal...
"""
import math

import bpy
from mathutils import Vector, Euler, Quaternion

from .kinematics import sample_states, smoothstep, lerp, clamp


def _ease(u, kind="inout"):
    if kind == "linear":
        return u
    if kind == "in":
        return u * u
    if kind == "out":
        return 1 - (1 - u) ** 2
    return smoothstep(0, 1, u)


class CameraDirector:
    def __init__(self, actors_states, time_map, fps):
        self.states = actors_states
        self.tm = time_map
        self.fps = fps

    def _actor_point(self, spec, t_sim):
        if "world" in spec:
            return Vector(spec["world"])
        st = sample_states(self.states[spec["actor"]], spec.get("t", t_sim))
        off = spec.get("offset", [0, 0, 0])
        space = spec.get("space", "heading")
        if space == "world":
            return Vector((st.x + off[0], st.y + off[1], st.z + off[2]))
        yaw = st.yaw if space == "local" else st.yaw - st.slip  # 'heading' = dirección de la marcha
        c, s = math.cos(yaw), math.sin(yaw)
        return Vector((st.x + c * off[0] - s * off[1], st.y + s * off[0] + c * off[1], st.z + off[2]))

    def _point(self, spec, t_sim):
        if "blend" in spec:  # mezcla de dos puntos
            a = self._point(spec["blend"][0], t_sim)
            b = self._point(spec["blend"][1], t_sim)
            return a.lerp(b, spec.get("factor", 0.5))
        return self._actor_point(spec, t_sim)

    def evaluate(self, keys, t_rel):
        """Pos, target, lens, roll en t_rel (s de pantalla) sin suavizado."""
        t_sim = self.tm.sim(t_rel)
        if t_rel <= keys[0]["t"]:
            k0 = k1 = keys[0]
            u = 0
        elif t_rel >= keys[-1]["t"]:
            k0 = k1 = keys[-1]
            u = 0
        else:
            for a, b in zip(keys, keys[1:]):
                if a["t"] <= t_rel <= b["t"]:
                    k0, k1 = a, b
                    u = (t_rel - a["t"]) / (b["t"] - a["t"])
                    break
        u = _ease(u, k1.get("ease", "inout"))
        pos = self._point(k0["pos"], t_sim).lerp(self._point(k1["pos"], t_sim), u)
        tgt = self._point(k0["target"], t_sim).lerp(self._point(k1["target"], t_sim), u)
        lens = lerp(k0.get("lens", 35), k1.get("lens", 35), u)
        roll = lerp(k0.get("roll", 0), k1.get("roll", 0), u)
        return pos, tgt, lens, roll

    @staticmethod
    def _shake(t, amp, freq, seed=0.0):
        """Vibración suave (suma de senos inconmensurables ~ ruido)."""
        if amp <= 0:
            return Vector((0, 0, 0)), 0.0
        def n(k, ph):
            return (math.sin(t * freq * k + ph) * 0.6 + math.sin(t * freq * k * 2.37 + ph * 1.7) * 0.3 +
                    math.sin(t * freq * k * 5.13 + ph * 0.3) * 0.1)
        return Vector((n(1.0, seed), n(1.13, seed + 2), n(0.87, seed + 4))) * amp, n(0.71, seed + 7) * amp * 0.6


def build_camera(name, shot, director, frame_count, frame_start, focus_actor=None, collection=None):
    """Crea la cámara del plano con todas sus claves por fotograma."""
    cd = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cd)
    (collection or bpy.context.scene.collection).objects.link(cam)
    cd.sensor_width = 36
    cd.sensor_fit = "AUTO"
    cd.clip_start = 0.1
    cd.clip_end = 6000
    camspec = shot["camera"]
    keys = camspec["keys"]
    fstop = camspec.get("fstop", 2.8)
    cd.dof.use_dof = camspec.get("dof", True)
    cd.dof.aperture_fstop = fstop
    cd.dof.aperture_blades = 7
    smooth = camspec.get("smooth", 0.0)       # constante de tiempo del muelle (s)
    shake = camspec.get("shake", 0.0)
    shake_f = camspec.get("shake_freq", 7.0)
    fps = director.fps
    pos_s = tgt_s = None
    vel_p = Vector((0, 0, 0))
    vel_t = Vector((0, 0, 0))
    # pre-roll del filtro para que no arranque 'en frío'
    pre = int(fps * 0.5) if smooth > 0 else 0
    out = []
    for i in range(-pre, frame_count):
        t_rel = i / fps
        pos, tgt, lens, roll = director.evaluate(keys, t_rel)
        if smooth > 0:
            if pos_s is None:
                pos_s, tgt_s = pos.copy(), tgt.copy()
            # muelle crítico
            w = 2.0 / smooth
            dt = 1 / fps
            for (cur, vel, goal) in ((pos_s, vel_p, pos), (tgt_s, vel_t, tgt)):
                acc = (goal - cur) * (w * w) - vel * (2 * w)
                vel += acc * dt
                cur += vel * dt
            P, T = pos_s.copy(), tgt_s.copy()
        else:
            P, T = pos, tgt
        if i >= 0:
            out.append((P, T, lens, roll, t_rel))
    for i, (P, T, lens, roll, t_rel) in enumerate(out):
        f = frame_start + i
        sh, rsh = CameraDirector._shake(director.tm.sim(t_rel) if camspec.get("shake_sim_time") else t_rel, shake, shake_f, 1.3)
        d = (T - P)
        q = d.to_track_quat("-Z", "Y")
        roll_q = Quaternion(d.normalized(), math.radians(roll + rsh * 8))
        q = roll_q @ q
        cam.location = P + sh
        cam.rotation_mode = "XYZ"
        cam.rotation_euler = q.to_euler("XYZ", cam.rotation_euler)
        cd.lens = lens
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cd.keyframe_insert("lens", frame=f)
        # foco
        if focus_actor and focus_actor in director.states:
            st = sample_states(director.states[focus_actor], director.tm.sim(t_rel))
            fd = (Vector((st.x, st.y, st.z + 0.7)) - cam.location).length
        else:
            fd = d.length
        cd.dof.focus_distance = max(0.5, fd)
        cd.dof.keyframe_insert("focus_distance", frame=f)
    return cam
