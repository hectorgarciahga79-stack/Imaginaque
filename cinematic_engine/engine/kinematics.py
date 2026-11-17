"""Cinemática y física básica de vehículos (Python puro, sin bpy).

Un vehículo recorre una ruta (polilínea suavizada) con un perfil de velocidad.
A partir de ahí se derivan, por integración:
  * posición y orientación (tangente de la ruta + ángulo de deriva/derrape),
  * aceleración lateral -> balanceo de carrocería y derrape automático,
  * aceleración longitudinal -> cabeceo (frenada / aceleración),
  * giro de ruedas y ángulo de dirección (con contravolante en derrape).

Todo es determinista: el mismo guion produce siempre la misma animación, lo que
permite renderizar planos sueltos o por lotes y reanudar renders.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


# --------------------------------------------------------------------------- utilidades
def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a, b):
    return a if x < a else b if x > b else x


def smoothstep(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = clamp((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def interp_table(table, x):
    """Interpolación lineal en una tabla [[x, y], ...] (extrapola constante)."""
    if x <= table[0][0]:
        return table[0][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            return lerp(y0, y1, (x - x0) / (x1 - x0) if x1 != x0 else 1.0)
    return table[-1][1]


def wrap_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


# --------------------------------------------------------------------------- rutas
class Route:
    """Ruta 2D muestreada densamente con longitud de arco.

    Se define con puntos de control y radios de redondeo opcionales en cada
    esquina (``fillets``), de modo que las curvas son arcos de radio conocido
    (física coherente: a = v^2 / R).
    """

    def __init__(self, points, fillet=0.0, step=0.25, z=0.0):
        pts = [tuple(map(float, p[:2])) for p in points]
        self.z = z
        self.samples = self._build(pts, fillet, step)
        self.s = [0.0]
        for a, b in zip(self.samples, self.samples[1:]):
            self.s.append(self.s[-1] + math.dist(a, b))
        self.length = self.s[-1]

    @staticmethod
    def _build(pts, fillet, step):
        if len(pts) < 3 or fillet <= 0:
            out = []
            for a, b in zip(pts, pts[1:]):
                n = max(1, int(math.dist(a, b) / step))
                out += [(lerp(a[0], b[0], i / n), lerp(a[1], b[1], i / n)) for i in range(n)]
            out.append(pts[-1])
            return out
        out = [pts[0]]
        cur = pts[0]
        for i in range(1, len(pts) - 1):
            p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
            d0 = (p1[0] - p0[0], p1[1] - p0[1])
            d1 = (p2[0] - p1[0], p2[1] - p1[1])
            l0, l1 = math.hypot(*d0), math.hypot(*d1)
            u0 = (d0[0] / l0, d0[1] / l0)
            u1 = (d1[0] / l1, d1[1] / l1)
            ang = math.acos(clamp(u0[0] * u1[0] + u0[1] * u1[1], -1, 1))
            if ang < 1e-4:
                continue
            r = fillet
            t = r * math.tan(ang / 2)
            t = min(t, l0 * 0.49, l1 * 0.49)
            r = t / math.tan(ang / 2)
            a = (p1[0] - u0[0] * t, p1[1] - u0[1] * t)
            b = (p1[0] + u1[0] * t, p1[1] + u1[1] * t)
            # recta hasta a
            n = max(1, int(math.dist(cur, a) / step))
            out += [(lerp(cur[0], a[0], k / n), lerp(cur[1], a[1], k / n)) for k in range(1, n + 1)]
            # arco a -> b
            cross = u0[0] * u1[1] - u0[1] * u1[0]
            side = 1 if cross > 0 else -1
            nrm = (-u0[1] * side, u0[0] * side)
            c = (a[0] + nrm[0] * r, a[1] + nrm[1] * r)
            a0 = math.atan2(a[1] - c[1], a[0] - c[0])
            a1 = math.atan2(b[1] - c[1], b[0] - c[0])
            da = wrap_angle(a1 - a0)
            n = max(2, int(abs(da) * r / step))
            out += [(c[0] + r * math.cos(a0 + da * k / n), c[1] + r * math.sin(a0 + da * k / n)) for k in range(1, n + 1)]
            cur = b
        p = pts[-1]
        n = max(1, int(math.dist(cur, p) / step))
        out += [(lerp(cur[0], p[0], k / n), lerp(cur[1], p[1], k / n)) for k in range(1, n + 1)]
        return out

    def _index(self, s):
        s = clamp(s, 0.0, self.length)
        lo, hi = 0, len(self.s) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.s[mid] <= s:
                lo = mid
            else:
                hi = mid
        return lo, s

    def point(self, s):
        """Posición (x, y) a distancia s; extrapola linealmente fuera de rango."""
        if s < 0 or s > self.length:
            base = 0.0 if s < 0 else self.length
            hx, hy = self.tangent(base)
            px, py = self.point(base)
            d = s - base
            return (px + hx * d, py + hy * d)
        i, s = self._index(s)
        j = min(i + 1, len(self.samples) - 1)
        seg = self.s[j] - self.s[i]
        t = (s - self.s[i]) / seg if seg > 0 else 0
        a, b = self.samples[i], self.samples[j]
        return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))

    def tangent(self, s, h=0.5):
        s = clamp(s, h, self.length - h)
        a, b = self.point(s - h), self.point(s + h)
        d = math.dist(a, b) or 1
        return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)

    def heading(self, s):
        tx, ty = self.tangent(s)
        return math.atan2(ty, tx)

    def curvature(self, s, h=1.5):
        """Curvatura con signo (+ = giro a la izquierda)."""
        h1, h2 = self.heading(s - h), self.heading(s + h)
        return wrap_angle(h2 - h1) / (2 * h)

    def nearest_s(self, x, y):
        best, bs = 1e18, 0.0
        for p, s in zip(self.samples, self.s):
            d = (p[0] - x) ** 2 + (p[1] - y) ** 2
            if d < best:
                best, bs = d, s
        return bs


# --------------------------------------------------------------------------- vehículo
@dataclass
class VehicleState:
    t: float
    x: float
    y: float
    z: float
    yaw: float          # orientación de la carrocería (rad, 0 = +X)
    roll: float         # balanceo (rad)
    pitch: float        # cabeceo (rad)
    speed: float        # m/s
    steer: float        # ángulo ruedas delanteras (rad)
    wheel_rot: float    # rotación acumulada de ruedas (rad)
    slip: float         # ángulo de deriva (rad)
    lat_acc: float
    lon_acc: float
    s: float
    drifting: float     # 0..1 intensidad de derrape (humo, chirrido)


@dataclass
class VehicleSpec:
    wheelbase: float = 2.65
    wheel_radius: float = 0.34
    grip: float = 7.5             # m/s^2 de aceleración lateral antes de deslizar
    drift_gain: float = 0.075     # rad de deriva por m/s^2 por encima del agarre
    max_slip: float = math.radians(38)
    slip_lag: float = 0.35        # s (inercia del derrape)
    roll_gain: float = 0.0085     # rad por m/s^2
    pitch_gain: float = 0.006
    drift_enabled: bool = True


@dataclass
class Trajectory:
    """Trayectoria de un actor: ruta + perfil de distancia s(t)."""
    route: Route
    spec: VehicleSpec
    speed_table: list = field(default_factory=lambda: [[0, 20]])
    s0: float = 0.0
    lane_offset: float = 0.0
    s_fn: object = None           # función opcional t -> s (persecuciones)
    slip_extra: list = None       # tabla [[t, grados]] (trompos, choques)
    stop_s: float = None          # choque: no avanza más allá de esta s
    stop_decel: float = 30.0
    z: float = 0.0
    dt: float = 1 / 240

    def __post_init__(self):
        self._cache = None

    # s(t) integrando la tabla de velocidades (o la función externa)
    def s_at(self, t):
        if self.s_fn is not None:
            s = self.s_fn(t)
        else:
            n = max(1, int(abs(t) / self.dt))
            dt = t / n
            s = self.s0
            for i in range(n):
                s += interp_table(self.speed_table, (i + 0.5) * dt) * dt
        if self.stop_s is not None and s > self.stop_s:
            s = self.stop_s
        return s

    def bake(self, t0, t1, rate=240.0):
        """Simula a alta frecuencia y devuelve una lista de VehicleState."""
        n = int((t1 - t0) * rate) + 2
        dt = (t1 - t0) / (n - 1)
        states = []
        slip = 0.0
        wheel = 0.0
        prev_s = self.s_at(t0 - dt)
        prev_v = None
        sm_lat = 0.0
        sm_lon = 0.0
        # pre-integración acumulativa para eficiencia
        s_vals = [self.s_at(t0 + i * dt) for i in range(n)] if self.s_fn is not None else None
        if s_vals is None:
            s = self.s_at(t0)
            s_vals = [s]
            for i in range(1, n):
                t = t0 + (i - 0.5) * dt
                s += interp_table(self.speed_table, t) * dt
                if self.stop_s is not None:
                    s = min(s, self.stop_s)
                s_vals.append(s)
        for i in range(n):
            t = t0 + i * dt
            s = s_vals[i]
            v = (s - prev_s) / dt
            prev_s = s
            if prev_v is None:
                prev_v = v
            lon = (v - prev_v) / dt
            prev_v = v
            k = self.route.curvature(s)
            lat = v * v * k
            # suavizado (suspensión)
            a = dt / 0.12
            sm_lat += (lat - sm_lat) * min(1, a)
            sm_lon += (clamp(lon, -14, 10) - sm_lon) * min(1, a)
            # derrape automático: exceso de aceleración lateral sobre el agarre
            target = 0.0
            if self.spec.drift_enabled and abs(lat) > self.spec.grip:
                target = math.copysign(min(self.spec.max_slip, (abs(lat) - self.spec.grip) * self.spec.drift_gain + math.radians(12)), lat)
            if self.slip_extra:
                target += math.radians(interp_table(self.slip_extra, t))
            slip += (target - slip) * min(1.0, dt / self.spec.slip_lag)
            hx, hy = self.route.tangent(s)
            px, py = self.route.point(s)
            # carril (desplazamiento lateral a la izquierda de la marcha)
            px += -hy * self.lane_offset
            py += hx * self.lane_offset
            yaw = math.atan2(hy, hx) + slip
            steer_geo = math.atan(self.spec.wheelbase * k)
            steer = clamp(steer_geo - slip * 1.25, -0.6, 0.6)
            wheel += v * dt / self.spec.wheel_radius * (1 + 0.6 * abs(slip))
            roll = clamp(-sm_lat * self.spec.roll_gain, -0.09, 0.09)
            pitch = clamp(-sm_lon * self.spec.pitch_gain, -0.05, 0.05)
            drifting = clamp(abs(slip) / math.radians(18), 0, 1)
            states.append(VehicleState(t, px, py, self.z, yaw, roll, pitch, v, steer, wheel, slip, lat, lon, s, drifting))
        return states


def sample_states(states, t):
    """Estado interpolado en el instante t (para fotogramas / subfotogramas)."""
    if t <= states[0].t:
        return states[0]
    if t >= states[-1].t:
        return states[-1]
    dt = states[1].t - states[0].t
    i = int((t - states[0].t) / dt)
    i = clamp(i, 0, len(states) - 2)
    a, b = states[i], states[i + 1]
    f = (t - a.t) / (b.t - a.t)
    yaw = a.yaw + wrap_angle(b.yaw - a.yaw) * f
    return VehicleState(
        t, lerp(a.x, b.x, f), lerp(a.y, b.y, f), lerp(a.z, b.z, f), yaw,
        lerp(a.roll, b.roll, f), lerp(a.pitch, b.pitch, f), lerp(a.speed, b.speed, f),
        lerp(a.steer, b.steer, f), lerp(a.wheel_rot, b.wheel_rot, f), lerp(a.slip, b.slip, f),
        lerp(a.lat_acc, b.lat_acc, f), lerp(a.lon_acc, b.lon_acc, f), lerp(a.s, b.s, f),
        lerp(a.drifting, b.drifting, f))


# --------------------------------------------------------------------------- tiempo
class TimeMap:
    """Mapea tiempo de pantalla -> tiempo de simulación (cámara lenta / speed ramp).

    ``speed`` es una tabla [[t_pantalla_rel, factor]]; 1 = tiempo real,
    0.25 = cámara lenta x4. Se integra para obtener el tiempo de simulación.
    """

    def __init__(self, sim_start, duration, speed=None, res=2000):
        self.sim_start = sim_start
        self.duration = duration
        self.speed = speed or [[0, 1.0]]
        self.res = res
        self._tab = [0.0]
        dt = duration / res
        acc = 0.0
        for i in range(res):
            acc += interp_table(self.speed, (i + 0.5) * dt) * dt
            self._tab.append(acc)

    def sim(self, t_rel):
        x = clamp(t_rel / self.duration, 0, 1) * self.res
        i = int(min(x, self.res - 1))
        f = x - i
        base = lerp(self._tab[i], self._tab[i + 1], f)
        extra = max(0.0, t_rel - self.duration) * interp_table(self.speed, self.duration)
        extra += min(0.0, t_rel) * interp_table(self.speed, 0)
        return self.sim_start + base + extra

    def rate(self, t_rel):
        return interp_table(self.speed, t_rel)

    @property
    def sim_end(self):
        return self.sim(self.duration)
