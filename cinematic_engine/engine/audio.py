"""Diseño de sonido 100% sintetizado (sin librerías de sonido con licencia).

* Música 'synthwave' original generada por código (batería, bajo, pads,
  arpegio), con estructura ligada al guion: intro, 'drop' al empezar la
  persecución, filtro y caída en la cámara lenta, golpe final.
* Efectos espacializados con los datos de la simulación (timeline.json):
  motor del deportivo (régimen según velocidad, cambios de marcha, efecto
  Doppler, paneo según cámara), sirenas de cada patrulla, chirrido de
  neumáticos proporcional al derrape, impacto y explosión, lluvia, trueno,
  'whooshes' en los cortes. En cámara lenta el sonido se ralentiza
  (tono más grave) y se filtra.
* Mezcla con 'ducking' de música bajo la narración y limitador final.
"""
import json
import math
import os

import numpy as np
from scipy import signal

SR = 48000
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    fc = np.clip(fc, 20, SR / 2 - 100)
    b, a = signal.butter(order, fc / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), f2 / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def var_lp(x, fc_curve, block=256):
    """Filtro paso bajo variable en el tiempo (1 polo + 1 polo = 12 dB/oct)."""
    y = np.zeros_like(x)
    z1 = z2 = 0.0
    n = len(x)
    for i in range(0, n, block):
        fc = float(np.clip(fc_curve[min(i, n - 1)], 20, SR / 2.5))
        a = math.exp(-2 * math.pi * fc / SR)
        seg = x[i:i + block]
        out1, zf1 = signal.lfilter([1 - a], [1, -a], seg, zi=[z1])
        out2, zf2 = signal.lfilter([1 - a], [1, -a], out1, zi=[z2])
        z1, z2 = zf1[0], zf2[0]
        y[i:i + block] = out2
    return y


def saw(phase):
    return 2 * (phase % 1.0) - 1


def adsr(n, a=0.005, d=0.1, s=0.6, r=0.1, sus_len=None):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    sus_n = max(0, n - a_n - d_n - r_n) if sus_len is None else int(sus_len * SR)
    env = np.concatenate([np.linspace(0, 1, a_n, endpoint=False), np.linspace(1, s, d_n, endpoint=False),
                          np.full(sus_n, s), np.linspace(s, 0, r_n)])
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def reverb(x, seconds=2.2, mix=0.25, seed=1, predelay=0.02):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((2, n)) * np.exp(-t * 6.9 / seconds)
    ir = np.stack([lp(ir[0], 6000), lp(ir[1], 5500)])
    ir[:, : int(predelay * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2, axis=1, keepdims=True))
    if x.ndim == 1:
        x = np.stack([x, x])
    wet = np.stack([signal.fftconvolve(x[0], ir[0])[: x.shape[1]], signal.fftconvolve(x[1], ir[1])[: x.shape[1]]])
    return x * (1 - mix) + wet * mix


def pan(x, p):
    """p en [-1, 1] (puede ser array). Ley de potencia constante."""
    ang = (np.asarray(p) + 1) * math.pi / 4
    return np.stack([x * np.cos(ang), x * np.sin(ang)])


def place(buf, clip, t):
    i = int(t * SR)
    if i >= buf.shape[-1]:
        return
    if i < 0:
        clip = clip[..., -i:]
        i = 0
    n = min(clip.shape[-1], buf.shape[-1] - i)
    buf[..., i:i + n] += clip[..., :n]


# =================================================================== música
class Music:
    def __init__(self, cfg, total, events):
        self.bpm = cfg.get("bpm", 104)
        self.root = 57 + (NOTE.get(cfg.get("root", "A"), 9) - 9)  # A3
        self.total = total
        self.beat = 60.0 / self.bpm
        self.n = int((total + 3) * SR)
        self.drop = cfg.get("drop_at", 8.0)
        self.slow = events.get("slowmo", [])
        self.end_hit = events.get("end_hit", total - 3)

    def kick(self):
        n = int(0.45 * SR)
        t = np.arange(n) / SR
        f = 45 + 110 * np.exp(-t * 28)
        ph = np.cumsum(f) / SR
        k = np.sin(2 * np.pi * ph) * np.exp(-t * 7.5)
        k += 0.4 * np.random.default_rng(1).standard_normal(n) * np.exp(-t * 120)
        return np.tanh(k * 1.6)

    def snare(self):
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(2)
        noise = bp(rng.standard_normal(n), 900, 7000) * np.exp(-t * 11)
        tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
        s = noise * 0.9 + tone * 0.5
        return s

    def hat(self, open_=False):
        n = int((0.25 if open_ else 0.06) * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(3)
        return hp(rng.standard_normal(n), 7000) * np.exp(-t * (14 if open_ else 70))

    def chord_notes(self, bar):
        # i - VI - III - VII  (Am F C G) en grados relativos a la tónica
        prog = [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]]
        return [self.root + x for x in prog[bar % 4]]

    def render(self):
        n = self.n
        L = np.zeros((2, n))
        drums = np.zeros((2, n))
        bass = np.zeros(n)
        pad = np.zeros(n)
        arp = np.zeros(n)
        beat = self.beat
        kick, snare, hat, ohat = self.kick(), self.snare(), self.hat(), self.hat(True)
        rng = np.random.default_rng(7)
        nbeats = int(self.total / beat) + 4
        for b in range(nbeats):
            t = b * beat
            bar = b // 4
            in_beat = b % 4
            drop = t >= self.drop - 0.01
            if t >= 4.0 - 0.01 and t < self.drop:  # pre-drop: hats + bombo suave
                place(drums, pan(hat * 0.25, 0.3), t + beat / 2)
                if in_beat == 0:
                    place(drums, pan(kick * 0.45, 0), t)
            if drop:
                place(drums, pan(kick, 0), t)
                if in_beat in (1, 3):
                    place(drums, pan(snare * 0.7, -0.05), t)
                for k in range(2):
                    place(drums, pan(hat * (0.35 if k else 0.22), 0.35), t + k * beat / 2 + beat / 4)
                if in_beat == 3:
                    place(drums, pan(ohat * 0.25, 0.4), t + beat / 2)
            # bajo: corcheas con octavas (synthwave)
            if t >= 4.0 - 0.01:
                root = self.chord_notes(bar)[0] - 24
                for k in range(2 if not drop else 4):
                    st = t + k * beat / (2 if not drop else 4)
                    m = root + (12 if (drop and k % 2) else 0)
                    ln = int(beat / (2 if not drop else 4) * SR * 0.9)
                    tt = np.arange(ln) / SR
                    ph = midi_hz(m) * tt
                    w = (saw(ph) + 0.5 * saw(ph * 1.005)) * adsr(ln, 0.003, 0.08, 0.5, 0.03)
                    place(bass, w, st)
            # pad (acorde por compás)
            if in_beat == 0:
                ln = int(4 * beat * SR)
                tt = np.arange(ln) / SR
                w = np.zeros(ln)
                for m in self.chord_notes(bar):
                    for det in (-0.12, 0.0, 0.11):
                        f = midi_hz(m + det)
                        w += saw(f * tt + rng.random())
                w *= adsr(ln, 0.6, 0.5, 0.8, 0.9) / 9
                place(pad, w, t)
            # arpegio (semicorcheas) desde el principio, más presente en el drop
            notes = self.chord_notes(bar)
            seq = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 24]
            for k in range(4):
                st = t + k * beat / 4
                m = seq[(in_beat * 4 + k) % 4]
                ln = int(beat / 4 * SR)
                tt = np.arange(ln) / SR
                w = np.sign(np.sin(2 * np.pi * midi_hz(m) * tt)) * 0.5 + saw(midi_hz(m) * tt) * 0.5
                w *= adsr(ln, 0.002, 0.06, 0.25, 0.02) * (0.5 if not drop else 0.8)
                place(arp, w, st)
        tvec = np.arange(n) / SR
        # filtros con automatización: intro cerrada, apertura hacia el drop, caída en cámara lenta
        fc = np.interp(tvec, [0, 4, self.drop - 0.1, self.drop, self.total + 3], [500, 900, 3500, 6000, 6000])
        slow_mask = np.zeros(n)
        for a, b in self.slow:
            slow_mask = np.maximum(slow_mask, np.clip(np.minimum((tvec - a) / 0.35, (b - tvec) / 0.35), 0, 1))
        fc = fc * (1 - slow_mask) + 280 * slow_mask
        pad_f = var_lp(pad, fc * 0.6)
        arp_f = var_lp(arp, fc)
        bass_f = lp(np.tanh(bass * 1.3), 900)
        L += pan(pad_f * 0.55, -0.25) + pan(pad_f * 0.55, 0.25)
        L += pan(arp_f * 0.32, np.sin(tvec * 1.3) * 0.5)
        L += pan(bass_f * 0.55, 0)
        L += drums * 0.8 * (1 - 0.85 * slow_mask)
        # sidechain del bombo sobre pad/bajo
        L = reverb(L, 2.4, 0.22)
        # golpe final y cola
        end = int((self.total + 0.2) * SR)
        L[:, end:] *= np.linspace(1, 0, n - end) if n > end else 1
        L *= (1 - 0.55 * slow_mask)
        return L[:, :n]


# =================================================================== SFX
class SFX:
    def __init__(self, timeline, total):
        self.tl = timeline
        self.total = total
        self.n = int((total + 3) * SR)
        fr = timeline["frames"]
        self.ft = np.array([f["t"] for f in fr])
        self.tvec = np.arange(self.n) / SR
        self.cam = np.array([f.get("cam", [0, 0, 0]) for f in fr])
        self.cdir = np.array([f.get("cam_dir", [0, 1]) for f in fr])
        self.rate = np.array([f["rate"] for f in fr])
        self.shot = [f["shot"] for f in fr]

    def actor_curves(self, name):
        fr = self.tl["frames"]
        x = np.array([f["actors"][name]["x"] for f in fr])
        y = np.array([f["actors"][name]["y"] for f in fr])
        v = np.array([f["actors"][name]["v"] for f in fr])
        d = np.array([f["actors"][name]["drift"] for f in fr])
        a = np.array([f["actors"][name]["acc"] for f in fr])
        return x, y, v, d, a

    def interp(self, arr):
        """Interpola por muestra respetando los cortes (sin suavizar entre planos)."""
        return np.interp(self.tvec, self.ft, arr)

    def spatial(self, name):
        """distancia, paneo y factor doppler por muestra para un actor."""
        x, y, v, d, a = self.actor_curves(name)
        dx = x - self.cam[:, 0]
        dy = y - self.cam[:, 1]
        dz = 0.5 - self.cam[:, 2]
        dist = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        # paneo: componente lateral respecto a la dirección de cámara
        cd = self.cdir / (np.linalg.norm(self.cdir, axis=1, keepdims=True) + 1e-6)
        right = np.stack([cd[:, 1], -cd[:, 0]], axis=1)
        lat = (dx * right[:, 0] + dy * right[:, 1]) / (dist + 1e-6)
        # velocidad radial (doppler) por diferencias
        rad = np.gradient(dist, self.ft)
        # en los cortes la derivada no es válida
        for i in range(1, len(self.shot)):
            if self.shot[i] != self.shot[i - 1]:
                rad[i - 1:i + 1] = 0
        rad = np.clip(rad / np.maximum(self.rate, 0.05), -60, 60)
        dop = 343.0 / (343.0 + rad)
        return self.interp(dist), np.clip(self.interp(lat), -1, 1), self.interp(dop), self.interp(v), self.interp(d), self.interp(a)

    def engine(self, name, base=32.0, gain=1.0, sporty=True):
        dist, lat, dop, v, drift, acc = self.spatial(name)
        rate = self.interp(self.rate)
        # marchas: régimen en diente de sierra con la velocidad
        gears = [0, 9, 17, 25, 33, 42, 60]
        rpm = np.zeros_like(v)
        for g0, g1 in zip(gears, gears[1:]):
            m = (v >= g0) & (v < g1)
            rpm[m] = 0.35 + 0.65 * (v[m] - g0) / (g1 - g0)
        rpm = signal.savgol_filter(rpm, 4801, 2) if len(rpm) > 4801 else rpm
        f0 = (base + rpm * (95 if sporty else 70)) * dop * rate
        ph = np.cumsum(f0) / SR
        tone = np.zeros(self.n)
        for h, amp in ((1, 1.0), (2, 0.7), (3, 0.45), (4, 0.3), (6, 0.18), (8, 0.1)):
            tone += amp * np.sin(2 * np.pi * h * ph + h)
        rng = np.random.default_rng(hash(name) % 1000)
        grit = bp(rng.standard_normal(self.n), 200, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * ph * 0.5))
        x = np.tanh((tone * 0.6 + grit * 0.35) * (1.2 + 1.2 * np.clip(acc / 6, 0, 1)))
        x = lp(x, 2500 if sporty else 1600)
        att = 1.0 / (1.0 + dist / 7.0) * (0.35 + 0.65 * np.clip(v / 30, 0, 1))
        x = x * att * gain
        return pan(x, lat * 0.8)

    def siren(self, name, phase=0.0, gain=0.6):
        dist, lat, dop, v, drift, acc = self.spatial(name)
        rate = self.interp(self.rate)
        # 'wail' (barrido lento) alternando con 'yelp' (rápido) cada 4 s de simulación
        sim = self.interp(np.array([f["sim"] for f in self.tl["frames"]]))
        mode = (np.floor((sim + phase * 4) / 4) % 2)
        wail = 0.5 - 0.5 * np.cos(2 * np.pi * (sim + phase) / 2.6)
        yelp = 0.5 - 0.5 * np.cos(2 * np.pi * (sim + phase) / 0.32)
        sweep = np.where(mode > 0, yelp, wail)
        f = (680 + 760 * sweep) * dop * rate
        ph = np.cumsum(f) / SR
        x = np.sin(2 * np.pi * ph) + 0.35 * np.sin(4 * np.pi * ph) + 0.2 * np.sin(6 * np.pi * ph)
        x = np.tanh(x * 1.5)
        # aparece cuando el actor está en escena (distancia razonable)
        att = 1.0 / (1.0 + dist / 14.0)
        x = bp(x, 400, 5000) * att * gain
        return pan(x, lat * 0.9)

    def screech(self, name, gain=0.9):
        dist, lat, dop, v, drift, acc = self.spatial(name)
        rate = self.interp(self.rate)
        rng = np.random.default_rng(5)
        noise = rng.standard_normal(self.n)
        x = bp(noise, 1100, 3200, 3) * 0.8
        f = (950 + 160 * np.sin(self.tvec * 23)) * rate * dop
        x += 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR)
        amt = np.clip((drift - 0.25) / 0.5, 0, 1)
        x = x * amt * (v > 3) / (1 + dist / 9) * gain
        x = var_lp(x, 800 + 6000 * rate)
        return pan(x, lat * 0.8)

    def rain(self, gain=0.18):
        rng = np.random.default_rng(9)
        n = self.n
        w = rng.standard_normal((2, n))
        x = np.stack([lp(hp(w[0], 400), 9000), lp(hp(w[1], 400), 9000)])
        drops = (rng.random((2, n)) > 0.9993) * rng.random((2, n))
        drops = np.stack([lp(drops[0], 4000), lp(drops[1], 4000)]) * 6
        out = (x * 0.5 + drops) * gain
        # aéreo (sin lluvia cercana): más lejano
        lvl = np.ones(n)
        for s in self.tl["shots"]:
            if s["id"].startswith("s1"):
                m = (self.tvec >= s["start"]) & (self.tvec < s["start"] + s["duration"])
                lvl[m] = 0.35
        return out * signal.savgol_filter(lvl, 2401, 1)

    @staticmethod
    def thunder(dur=4.0, seed=3):
        n = int(dur * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(seed)
        x = lp(rng.standard_normal(n), 180, 3) * 6
        env = np.exp(-t * 1.2) * (1 - np.exp(-t * 18))
        crack = lp(rng.standard_normal(n), 1200) * np.exp(-((t - 0.15) ** 2) / 0.003)
        return pan(np.tanh((x * env + crack * 0.6) * 1.5), 0.2)

    @staticmethod
    def whoosh(dur=0.45, up=True, seed=0):
        n = int(dur * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(seed)
        x = rng.standard_normal(n)
        fc = np.linspace(300, 4500, n) if up else np.linspace(4500, 300, n)
        y = var_lp(x, fc, 128)
        env = np.sin(np.pi * t / dur) ** 2
        return pan(y * env * 0.9, np.linspace(-0.7, 0.7, n))

    @staticmethod
    def riser(dur=3.5, seed=4):
        n = int(dur * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(seed)
        y = var_lp(rng.standard_normal(n), np.geomspace(200, 9000, n), 128)
        tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 880, n)) / SR) * 0.25
        env = (t / dur) ** 2
        return pan((y * 0.6 + tone) * env, 0)

    @staticmethod
    def impact(stretch=1.0, seed=6):
        """Golpe cinematográfico (sub + ruido); stretch>1 = cámara lenta."""
        dur = 2.5 * stretch
        n = int(dur * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(seed)
        f = (70 * np.exp(-t * 3 / stretch) + 28) / stretch ** 0.5
        sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6 / stretch)
        nz = lp(rng.standard_normal(n), 900 / stretch) * np.exp(-t * 5 / stretch)
        return pan(np.tanh((sub * 1.2 + nz * 0.8) * 1.4), 0)

    @staticmethod
    def explosion(stretch=1.0, seed=8):
        dur = 4.0 * stretch
        n = int(dur * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(seed)
        body = lp(rng.standard_normal(n), 350 / stretch, 3) * np.exp(-t * 1.3 / stretch) * 5
        f = 55 / stretch * np.exp(-t * 0.8 / stretch) + 22
        sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.1 / stretch) * 1.2
        crackle = hp((rng.random(n) > 0.997) * rng.standard_normal(n), 1500) * np.exp(-t * 0.6 / stretch) * 3
        attack = lp(rng.standard_normal(n), 4000) * np.exp(-t * 18 / stretch)
        x = np.tanh((body + sub + crackle * 0.4 + attack * 1.5) * 1.1)
        return reverb(pan(x, 0.25), 2.5, 0.3, seed=2)

    @staticmethod
    def metal_crash(stretch=1.0, seed=10):
        dur = 1.4 * stretch
        n = int(dur * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(seed)
        x = np.zeros(n)
        for f in (412, 587, 893, 1260, 1777, 2410, 3120):
            x += np.sin(2 * np.pi * f / stretch * t + rng.random() * 6) * np.exp(-t * rng.uniform(4, 12) / stretch)
        x += hp(rng.standard_normal(n), 800) * np.exp(-t * 9 / stretch) * 2
        return pan(np.tanh(x * 0.6), 0.3)


def _env_follow(x, attack=0.01, release=0.25):
    a = np.abs(x)
    b, aa = signal.butter(1, 8 / (SR / 2))
    env = signal.filtfilt(b, aa, a)
    return env / (env.max() + 1e-9)


def limiter(x, ceiling=0.94):
    peak = np.max(np.abs(x), axis=0)
    gain = np.minimum(1.0, ceiling / (peak + 1e-9))
    # suavizado (ataque instantáneo por mínimo en ventana, liberación lenta)
    # mínimo en ventana (anticipación ~5 ms) + liberación suave
    win = int(0.005 * SR)
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(gain, size=win * 2 + 1)
    g = signal.lfilter([0.0015], [1, -0.9985], g, zi=[g[0] * 0.9985])[0]
    g = np.minimum(g, minimum_filter1d(gain, size=win * 2 + 1))
    return x * g


def render_soundtrack(sb, timeline, narration, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    total = sum(s["duration"] for s in sb["shots"])
    shots = timeline["shots"]
    slow = [(s["start"], s["start"] + s["duration"]) for s in shots if s["slowmo"] < 0.9]
    music = Music(sb.get("music", {}), total, {"slowmo": slow}).render()
    sfx = SFX(timeline, total)
    n = sfx.n
    bus = np.zeros((2, n))
    actors = sb["actors"]
    for name, a in actors.items():
        if a.get("model", "sports") == "sports":
            bus += sfx.engine(name, base=34, gain=1.1, sporty=True)
            bus += sfx.screech(name, 0.9)
        else:
            bus += sfx.engine(name, base=26, gain=0.45, sporty=False)
            bus += sfx.siren(name, a.get("siren_phase", 0.0), 0.5)
            bus += sfx.screech(name, 0.5)
    bus += sfx.rain(0.16)
    place(bus, SFX.thunder() * 0.7, 0.35)
    # transiciones: whoosh en cada corte + riser antes del drop
    for i, s in enumerate(shots[1:], 1):
        place(bus, SFX.whoosh(0.4, True, i) * 0.35, s["start"] - 0.28)
    drop = sb.get("music", {}).get("drop_at", 8.0)
    place(bus, SFX.riser(3.2) * 0.35, drop - 3.2)
    place(bus, SFX.impact(1.0) * 0.8, drop)
    # cámara lenta: golpe estirado al entrar
    for a, b in slow:
        place(bus, SFX.impact(2.2, 11) * 0.9, a + 0.05)
    # choque y explosión (tiempo de simulación -> tiempo de pantalla)
    for ev in timeline["events"]:
        if ev["type"] != "crash":
            continue
        frames = timeline["frames"]
        best = min(frames, key=lambda f: abs(f["sim"] - ev["sim"]) + (0 if f["sim"] >= ev["sim"] - 0.05 else 1))
        t_screen = best["t"]
        stretch = 1.0 / max(0.2, best["rate"])
        place(bus, SFX.metal_crash(stretch) * 0.8, t_screen)
        place(bus, SFX.explosion(min(stretch, 2.5)) * 1.1, t_screen + 0.02)
    # bus de efectos
    sfx_bus = bus
    # narración + ducking
    voice = np.zeros(n)
    if narration and narration.get("track") is not None:
        tr = narration["track"]
        voice[: min(n, len(tr))] = tr[: min(n, len(tr))]
        voice = hp(voice, 90)
        # compresión suave
        env = _env_follow(voice)
        voice = voice * (1.0 / (1.0 + 1.5 * env)) * 2.2
    venv = _env_follow(voice) if voice.any() else np.zeros(n)
    # --- mezcla por objetivos de nivel (RMS en dBFS) ---
    def rms_db(x, mask=None):
        x = x if x.ndim == 1 else x.mean(axis=0)
        if mask is not None and mask.any():
            x = x[mask]
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)

    def to_db(x, cur, target):
        return x * 10 ** ((target - cur) / 20)

    voiced = venv > 0.08
    if voice.any():
        voice = to_db(voice, rms_db(voice, voiced), -16.0)
    music = music[:, :n]
    music = to_db(music, rms_db(music), -24.0 + sb.get("music", {}).get("gain_db", -9) + 9)
    sfx_bus = to_db(sfx_bus, rms_db(sfx_bus), -23.0)
    duck = 1.0 - 0.6 * np.clip(venv * 3, 0, 1)          # música -8 dB bajo la voz
    duck_sfx = 1.0 - 0.35 * np.clip(venv * 3, 0, 1)      # efectos -4 dB bajo la voz
    mix = music * duck + sfx_bus * duck_sfx + pan(voice, 0) * 1.41
    mix = hp(mix, 25)
    mix = limiter(mix, ceiling=0.89)
    levels = {"voz_dbfs": round(rms_db(pan(voice, 0) * 1.41, voiced), 1) if voice.any() else None,
              "musica_bajo_voz_dbfs": round(rms_db(music * duck, voiced), 1),
              "sfx_bajo_voz_dbfs": round(rms_db(sfx_bus * duck_sfx, voiced), 1)}
    with open(os.path.join(out_dir, "mix_levels.json"), "w") as f:
        json.dump(levels, f, indent=1)
    mix = mix[:, : int((total + 0.0) * SR)]
    # fundido final
    fo = int(0.6 * SR)
    mix[:, -fo:] *= np.linspace(1, 0, fo)
    path = os.path.join(out_dir, "banda_sonora.wav")
    _write_wav(path, mix)
    # stems para revisión
    _write_wav(os.path.join(out_dir, "stem_voz.wav"), pan(voice, 0)[:, : mix.shape[1]])
    _write_wav(os.path.join(out_dir, "stem_musica.wav"), music[:, : mix.shape[1]] * 0.5)
    _write_wav(os.path.join(out_dir, "stem_sfx.wav"), np.clip(sfx_bus[:, : mix.shape[1]] * 0.3, -1, 1))
    return path


def _write_wav(path, x):
    from scipy.io import wavfile
    x = np.clip(x, -1, 1)
    wavfile.write(path, SR, (x.T * 32767).astype(np.int16))
