"""Director: convierte un guion (JSON) en escenas de Blender por plano.

Flujo:
  1. simulate(): integra las trayectorias de todos los actores (tiempo de
     simulación continuo para toda la historia).
  2. build_base(): construye la ciudad UNA vez y la guarda en un .blend base
     (reutilización de escenarios entre planos y entre vídeos).
  3. build_shot(): abre la base, añade actores animados, efectos, peatones,
     cámara y composición para un plano -> guarda <plano>.blend.
  4. render_shot(): renderiza la secuencia PNG del plano (reanudable).
  5. export_timeline(): datos por fotograma (cámara, actores, eventos) para
     el diseño de sonido y los subtítulos sincronizados.
"""
import json
import math
import os

from .kinematics import Route, Trajectory, VehicleSpec, TimeMap, sample_states, interp_table

ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_storyboard(path):
    with open(path, encoding="utf-8") as f:
        sb = json.load(f)
    sb["_path"] = os.path.abspath(path)
    # resolver 'sim_start': 'after_previous' (continuidad de acción entre planos)
    prev = None
    for shot in sb["shots"]:
        if shot.get("sim_start") == "after_previous":
            shot["sim_start"] = shot_time_map(prev).sim_end if prev else 0.0
        prev = shot
    return sb


# ============================================================ simulación (sin bpy)
def build_trajectories(sb):
    routes = {}
    for name, r in sb["routes"].items():
        routes[name] = Route(r["points"], fillet=r.get("fillet", 0.0))
    trajs = {}
    order = sorted(sb["actors"].items(), key=lambda kv: 1 if "follow" in kv[1] else 0)
    for name, a in order:
        spec = VehicleSpec(**a.get("physics", {}))
        route = routes[a["route"]]
        tr = Trajectory(route, spec, speed_table=a.get("speed", [[0, 20]]), lane_offset=a.get("lane_offset", 0.0),
                        slip_extra=a.get("slip_extra"))
        if "anchor" in a:  # colocar el actor para que pase por un punto en un instante
            anc = a["anchor"]
            s_target = route.nearest_s(*anc["point"])
            tr.s0 = 0.0
            tr.s0 = s_target - tr.s_at(anc["t"])
        if "follow" in a:
            fl = a["follow"]
            leader = trajs[fl["actor"]]
            jx, jy = fl["join"]
            s_lead_ref = leader.route.nearest_s(jx, jy)
            s_self_ref = route.nearest_s(jx, jy)
            gap = fl["gap"]
            lead = leader

            def s_fn(t, lead=lead, gap=gap, a0=s_lead_ref, b0=s_self_ref):
                return lead.s_at(t) - a0 + b0 - interp_table(gap, t)
            tr.s_fn = s_fn
        if "stop_at" in a:
            tr.stop_s = route.nearest_s(*a["stop_at"])
        trajs[name] = tr
    return trajs


def simulate(sb, t0=-1.0, t1=None, rate=120.0):
    trajs = build_trajectories(sb)
    t1 = t1 or sb["duration_sim"] + 1.0
    states = {name: tr.bake(t0, t1, rate) for name, tr in trajs.items()}
    return trajs, states


def crash_time(states, name):
    """Primer instante en que el actor queda detenido tras ir rápido (choque)."""
    hist = []
    for st in states[name]:
        hist.append(st.speed)
        if len(hist) > 30:
            hist.pop(0)
        if st.speed < 0.3 and max(hist) > 8:
            # instante exacto: primer estado con s ya en el tope
            return st.t - 0.5 / 120.0
    return None


def shot_time_map(shot):
    return TimeMap(shot["sim_start"], shot["duration"], shot.get("speed_ramp"))


def shot_frames(sb, shot):
    fps = sb["fps"]
    n = int(round(shot["duration"] * fps))
    tm = shot_time_map(shot)
    times = [tm.sim(i / fps) for i in range(n)]
    return n, tm, times


# ============================================================ escenas (bpy)
def build_base(sb, base_path, quality="high"):
    import bpy
    from .city import CityBuilder
    bpy.ops.wm.read_factory_settings(use_empty=True)
    w = sb["world"]
    font = w.get("font")
    if font and not os.path.isabs(font):
        font = os.path.join(ENGINE_DIR, font)
    CityBuilder(seed=w.get("seed", 7), y_min=w.get("y_min", -1000), y_max=w.get("y_max", 320),
                block=w.get("block", 80), turn_y=w.get("turn_y", 0), west_extent=w.get("west_extent", 420),
                quality=quality, font_path=font).build()
    CityBuilder.build_world(strength=w.get("sky_strength", 1.0))
    _props(sb)
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=base_path, compress=True)
    return base_path


def _props(sb):
    """Atrezo del guion: barricadas, bidones, coches aparcados."""
    import bpy
    from . import materials as M
    from .vehicles import box, cylinder
    from .fx import _coll
    c = _coll("Atrezo")
    for p in sb.get("props", []):
        if p["type"] == "barrels":
            x, y = p["at"]
            red = M.principled("bidon_rojo", (0.5, 0.03, 0.02), 0.6, 0.35)
            yel = M.principled("bidon_amarillo", (0.8, 0.5, 0.02), 0.6, 0.35)
            for i in range(p.get("count", 9)):
                cylinder("bidon", 0.3, 0.9, (x + (i % 3) * 0.65 - 0.65, y + (i // 3) * 0.65 - 0.65, 0.6), c,
                         red if i % 2 else yel, 16)
            stripes = M.principled("barrera_naranja", (0.9, 0.25, 0.02), 0, 0.5)
            box("barrera", (0.15, 4.0, 1.0), (x + 1.6, y, 0.7), c, stripes, 0.03)
            box("baliza_obras", (0.2, 0.2, 0.2), (x + 1.6, y + 1.8, 1.35), c, M.emission("ambar_obras", (1.0, 0.45, 0.02), 120))
        elif p["type"] == "parked_cars":
            from .vehicles import build_vehicle
            import random
            rng = random.Random(p.get("seed", 3))
            cols = [(0.02, 0.25, 0.4), (0.9, 0.9, 0.88), (0.05, 0.05, 0.05), (0.4, 0.05, 0.4), (0.03, 0.3, 0.25), (0.7, 0.55, 0.1)]
            for i, (x, y, yaw) in enumerate(p["positions"]):
                v = build_vehicle("aparcado%d" % i, "sports", cols[i % len(cols)], coll=c, headlights=False, real_lights=False)
                v["root"].location = (x, y, 0)
                v["root"].rotation_euler = (0, 0, math.radians(yaw))
                # pilotos apagados
                v["tail_mat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.3
                for o in v["coll"].objects:
                    if "_faro" in o.name:
                        o.hide_render = True


def build_shot(sb, shot, profile, states, base_path, out_blend, device_cfg=None):
    import bpy
    from . import vehicles as V
    from . import fx as FX
    from . import render as R
    from .camera import CameraDirector, build_camera
    from .characters import build_pedestrian, animate_pedestrian

    bpy.ops.wm.open_mainfile(filepath=base_path)
    FX.FX_MODE = "volume" if profile.get("volumetric_fx") else "soft"
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    scene = bpy.context.scene
    fps = sb["fps"]
    n, tm, times = shot_frames(sb, shot)
    f0 = 1
    scene.frame_start, scene.frame_end = f0, f0 + n - 1
    scene.render.fps = fps
    visible = shot.get("actors", list(sb["actors"].keys()))
    parts = {}
    for name in visible:
        a = sb["actors"][name]
        p = V.build_vehicle(name, a.get("model", "sports"), tuple(a.get("paint", (0.6, 0.01, 0.03))),
                            underglow=tuple(a["underglow"]) if a.get("underglow") else None,
                            siren=a.get("siren", False))
        V.animate_vehicle(p, states[name], times, f0, siren_phase=a.get("siren_phase", 0.0))
        parts[name] = p
    # efectos de acción
    t_first, t_last = times[0], times[-1]
    for fxs in shot.get("fx", []):
        kind = fxs["type"]
        if kind == "tire_smoke" and profile.get("smoke", True):
            name = fxs["actor"]
            sp = V.SPORTS if sb["actors"][name].get("model", "sports") == "sports" else V.POLICE
            wb, tr = sp["wheelbase"], sp["track"]
            sysm = FX.tire_smoke(states[name], [(-wb / 2, tr), (-wb / 2, -tr)], t_first - 2.5, t_last,
                                 rate=fxs.get("rate", 24), seed=hash(name) % 100, min_drift=fxs.get("min_drift", 0.35))
            sysm.bake(times, f0)
        elif kind == "skid_marks":
            name = fxs["actor"]
            sp = V.SPORTS if sb["actors"][name].get("model", "sports") == "sports" else V.POLICE
            wb, tr = sp["wheelbase"], sp["track"]
            FX.skid_marks(states[name], [(-wb / 2, tr), (-wb / 2, -tr), (wb / 2, tr), (wb / 2, -tr)],
                          fxs.get("t0", t_first - 3), fxs.get("t1", t_last), times, f0)
        elif kind == "explosion":
            from .director import crash_time
            tb = crash_time(states, fxs["actor"]) if "actor" in fxs else fxs["t"]
            st = sample_states(states[fxs["actor"]], tb) if "actor" in fxs else None
            center = fxs.get("at") or (st.x, st.y, 0.3)
            FX.explosion(center, tb + fxs.get("delay", 0.0), seed=fxs.get("seed", 5), scale=fxs.get("scale", 1.0),
                         frame_times=times, frame_start=f0)
            if fxs.get("wreck_fire", True):
                FX.burning_wreck(center, tb + 0.6, t_last + 0.1, frame_times=times, frame_start=f0)
            if "actor" in fxs and fxs.get("char", True):  # carrocería calcinada tras el impacto
                _char_vehicle(parts.get(fxs["actor"]), tb, times, f0)
    if sb.get("weather", {}).get("rain", True) and shot.get("rain", True):
        pass  # se añade tras crear la cámara
    # peatones
    for i, ped in enumerate(shot.get("pedestrians", [])):
        cam_dir = CameraDirector(states, tm, fps)
        st_pos = cam_dir._point(ped["at"], times[0])
        pp = build_pedestrian("peaton%d" % i, seed=ped.get("seed", i))
        run = None
        if "run" in ped:
            run = (ped["run"]["t"], math.radians(ped["run"]["dir"]), ped["run"]["speed"])
        animate_pedestrian(pp, (st_pos.x, st_pos.y), math.radians(ped.get("dir", 90)), ped.get("speed", 1.3),
                           times, f0, phase=i * 1.7, run_from=run)
    # cámara
    director = CameraDirector(states, tm, fps)
    cam = build_camera("Camara_" + shot["id"], shot, director, n, f0, focus_actor=shot["camera"].get("focus"))
    scene.camera = cam
    # lluvia
    wcfg = sb.get("weather", {})
    if wcfg.get("rain", True) and shot.get("rain", True):
        rate = tm.rate(shot["duration"] / 2)
        FX.add_rain(cam, f0, f0 + n, time_scale=rate, density=profile.get("rain_density", 1.0) * shot.get("rain_density", 1.0))
    # niebla volumétrica local (haces de luz)
    if profile.get("volumetrics") and shot.get("volumetric"):
        v = shot["volumetric"]
        FX.add_fog_volume(v["center"], v["size"], density=v.get("density", 0.004))
    R.configure(scene, profile, device_cfg)
    post = dict(sb.get("compositing", {}))
    post.update(shot.get("compositing", {}))
    R.compositor(scene, **post)
    scene["shot_id"] = shot["id"]
    os.makedirs(os.path.dirname(out_blend), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True)
    return scene


def _char_vehicle(p, t_crash, times, f0):
    """Tras el choque: pintura carbonizada y faros apagados (por fotograma)."""
    if not p:
        return
    import bpy
    for o in p["coll"].objects:
        if o.type == "LIGHT" and "_haz" in o.name:
            for i, t in enumerate(times):
                o.data.energy = o.data.energy if t < t_crash else 0.0
                o.data.keyframe_insert("energy", frame=f0 + i)


def render_shot(blend_path, out_dir, step=1):
    import bpy
    from . import render as R
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    sc = bpy.context.scene
    R.render_animation(sc, out_dir, sc.frame_start, sc.frame_end, step)


# ============================================================ timeline para audio/subtítulos
def export_timeline(sb, states, path):
    """Por fotograma de pantalla: plano, t pantalla, t simulación, posición de
    cámara (aprox. sin vibración) y estado de cada actor."""
    from .kinematics import TimeMap
    fps = sb["fps"]
    data = {"fps": fps, "frames": [], "shots": [], "events": []}
    t_screen0 = 0.0
    for shot in sb["shots"]:
        n, tm, times = shot_frames(sb, shot)
        data["shots"].append({"id": shot["id"], "start": t_screen0, "duration": shot["duration"],
                              "sim_start": times[0], "sim_end": times[-1], "slowmo": min(r[1] for r in (shot.get("speed_ramp") or [[0, 1]]))})
        cam_keys = shot["camera"]["keys"]
        try:
            from .camera import CameraDirector
            cd = CameraDirector(states, tm, fps)
            have_cam = True
        except Exception:
            have_cam = False
        for i, t in enumerate(times):
            fr = {"shot": shot["id"], "t": round(t_screen0 + i / fps, 4), "sim": round(t, 4), "rate": tm.rate(i / fps)}
            if have_cam:
                p, tg, lens, roll = cd.evaluate(cam_keys, i / fps)
                fr["cam"] = [round(p.x, 2), round(p.y, 2), round(p.z, 2)]
                fr["cam_dir"] = [round(tg.x - p.x, 3), round(tg.y - p.y, 3)]
            fr["actors"] = {}
            for name in sb["actors"]:
                st = sample_states(states[name], t)
                fr["actors"][name] = {"x": round(st.x, 2), "y": round(st.y, 2), "v": round(st.speed, 2),
                                      "drift": round(st.drifting, 3), "acc": round(st.lon_acc, 2)}
            data["frames"].append(fr)
        t_screen0 += shot["duration"]
    for name in sb["actors"]:
        ct = crash_time(states, name)
        if ct is not None:
            data["events"].append({"type": "crash", "actor": name, "sim": ct})
    with open(path, "w") as f:
        json.dump(data, f)
    return data
