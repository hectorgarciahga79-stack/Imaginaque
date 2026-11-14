"""Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 59.4
N = int(TOT*SR)
rng = np.random.default_rng(3)
t = np.arange(N)/SR

def bp(x, lo, hi, o=4):
    sos = butter(o, [lo, hi], 'band', fs=SR, output='sos'); return sosfilt(sos, x)
def lp(x, f, o=4):
    sos = butter(o, f, 'low', fs=SR, output='sos'); return sosfilt(sos, x)
def hp(x, f, o=4):
    sos = butter(o, f, 'high', fs=SR, output='sos'); return sosfilt(sos, x)
def env(a, d, s, r, dur):
    n = int(dur*SR); e = np.ones(n)*s
    na, nd, nr = int(a*SR), int(d*SR), int(r*SR)
    e[:na] = np.linspace(0, 1, na) if na else e[:na]
    e[na:na+nd] = np.linspace(1, s, len(e[na:na+nd]))
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def place(buf, x, at, g=1.0):
    i = int(at*SR); j = min(N, i+len(x))
    if i < N: buf[i:j] += g*x[:j-i]
def gate(times, fade=0.05):
    """máscara 0..1 con tramos [(a,b,valor)]"""
    m = np.zeros(N)
    for a, b, v in times:
        i, j = int(a*SR), int(min(b, TOT)*SR); m[i:j] = v
    k = int(fade*SR); return np.convolve(m, np.ones(k)/k, 'same')
REV_IR = None
def reverb(x, dec=1.6, mix=0.3):
    global REV_IR
    if REV_IR is None:
        n = int(dec*SR); REV_IR = rng.normal(0, 1, n)*np.exp(-np.arange(n)/SR*4.5/dec); REV_IR /= np.abs(REV_IR).sum()**0.5*8
    return x*(1-mix) + fftconvolve(x, REV_IR)[:len(x)]*mix*3

def tone(f, dur, kind="saw", det=0.0):
    tt = np.arange(int(dur*SR))/SR
    if kind == "sine": return np.sin(2*np.pi*f*tt)
    ph = (f*tt) % 1; s = 2*ph-1
    if det: s = 0.5*s + 0.5*(2*((f*(1+det)*tt) % 1)-1)
    return s

NOTE = lambda n: 440*2**((n-69)/12)
music = np.zeros(N); sfx = np.zeros(N); amb = np.zeros(N)

# ---------------- música
# A: 0–23.25 · alegre (Do–Sol–Lam–Fa), 112 bpm, plucks + pad; durante las pausas, pad suspendido agudo
beat = 60/112
chords = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]
for bar in range(int(23.25/(beat*4))+1):
    ch = chords[bar % 4]; t0 = bar*beat*4
    for n_ in ch:
        x = lp(tone(NOTE(n_-12), beat*4, "saw", 0.004), 1400)*env(0.3, 0.5, 0.7, 0.6, beat*4)
        place(music, x, t0, 0.045)
    for k in range(8):
        n_ = ch[(k*2) % 3]+12+(12 if k % 4 == 3 else 0)
        x = lp(tone(NOTE(n_), 0.25, "saw"), 3000)*env(0.003, 0.18, 0.0, 0.05, 0.25)
        place(music, x, t0+k*beat/2, 0.05)
    for k in range(4):   # bombo suave
        kk = np.sin(2*np.pi*np.cumsum(np.linspace(120, 45, int(0.18*SR)))/SR)*np.linspace(1, 0, int(0.18*SR))**2
        place(music, kk, t0+k*beat, 0.18)
# pausas del tiempo en el tramo A: la música cae de golpe; queda un pad agudo y quieto
fr_A = [(1.70, 11.45), (13.95, 14.85), (17.30, 18.45), (20.35, 21.65)]
duckA = 1-gate([(a, b, 0.93) for a, b in fr_A], 0.02)
music[:int(23.25*SR)] *= duckA[:int(23.25*SR)]
for a, b in fr_A:
    d = b-a
    x = sum(lp(tone(NOTE(n_), d, "saw", 0.003), 2500) for n_ in (79, 84, 88))*env(0.4, 0.1, 1, 0.3, d)
    place(music, x*np.sin(np.linspace(0, d*2*np.pi*0.5, len(x)))**2*0+x, a, 0.012)
# B: 23.25–34.4 · menor, pulso y reloj
for bar in range(4):
    t0 = 23.25+bar*2.8
    for n_ in [(57, 60, 64), (53, 57, 60), (50, 53, 57), (52, 56, 59)][bar]:
        x = lp(tone(NOTE(n_-12), 2.8, "saw", 0.006), 900)*env(0.6, 0.5, 0.8, 0.8, 2.8)
        place(music, x, t0, 0.055)
for k in range(int(11/0.5)):
    tk = 23.4+k*0.5
    click = hp(rng.normal(0, 1, int(0.02*SR)), 2500)*np.linspace(1, 0, int(0.02*SR))
    place(sfx, click, tk, 0.08 if k % 2 else 0.12)
# aceleración del reloj del plano del reloj (25.7–28.4)
tk = 25.7; dt = 0.25
while tk < 28.4:
    click = hp(rng.normal(0, 1, int(0.015*SR)), 3000)*np.linspace(1, 0, int(0.015*SR)); place(sfx, click, tk, 0.1); dt *= 0.9; tk += max(dt, 0.04)
# C: 34.4–47.85 · drone oscuro
d = 47.85-34.4
dr = (np.sin(2*np.pi*41.2*np.arange(int(d*SR))/SR)+0.5*lp(tone(55, d, "saw", 0.01), 300))*env(1.5, 0.5, 1, 1.0, d)
place(music, dr, 34.4, 0.09)
x = lp(tone(NOTE(69), 2.2, "saw", 0.005), 1800)*env(0.5, 0.3, 0.6, 1.0, 2.2); place(music, x, 34.4, 0.03)
# silencio total tras congelar (36.0): solo drone muy bajo
music[int(36.0*SR):int(38.0*SR)] *= np.linspace(1, 0.25, int(2.0*SR))
music[int(38.0*SR):int(47.85*SR)] *= 0.35
for k in range(14):   # latidos
    tb = 39.0+k*0.75
    for o, g in ((0, 1.0), (0.18, 0.6)):
        hb = np.sin(2*np.pi*np.cumsum(np.linspace(70, 38, int(0.2*SR)))/SR)*np.linspace(1, 0, int(0.2*SR))**2
        place(music, hb, tb+o, 0.25*g)
# grave misterioso al aparecer la figura
rum = lp(rng.normal(0, 1, int(4.5*SR)), 120)*env(1.2, 0.5, 1, 1.5, 4.5); place(music, rum, 40.7, 0.8)
rum = lp(rng.normal(0, 1, int(3.8*SR)), 90)*env(0.5, 0.5, 1, 1.0, 3.8); place(music, rum, 44.2, 0.9)
# D: 47.85–56.4 · golpe + crescendo
hit = lp(rng.normal(0, 1, int(2.0*SR)), 200)*np.exp(-np.arange(int(2.0*SR))/SR*2.5); place(music, hit, 48.42, 1.2)
sub = np.sin(2*np.pi*np.cumsum(np.linspace(70, 30, int(2.5*SR)))/SR)*np.exp(-np.arange(int(2.5*SR))/SR*1.5); place(music, sub, 48.42, 0.5)
d = 56.4-48.6
for n_ in (45, 52, 57, 60):
    x = lp(tone(NOTE(n_), d, "saw", 0.007), 1200)*np.linspace(0.05, 1, int(d*SR))**1.6
    place(music, x, 48.6, 0.05)
pls = np.zeros(int(d*SR))
for k in range(int(d/0.27)):
    i0 = int(k*0.27*SR); kk = np.sin(2*np.pi*np.cumsum(np.linspace(100, 40, int(0.12*SR)))/SR)*np.linspace(1, 0, int(0.12*SR))**2
    pls[i0:i0+len(kk)] += kk[:len(pls)-i0]*(k/(d/0.27))
place(music, pls, 48.6, 0.35)
boom, bsr = sf.read("/home/claude/tiktok/sfx/boom.wav"); boom = boom.mean(1) if boom.ndim > 1 else boom
boom = librosa.resample(boom, orig_sr=bsr, target_sr=SR)
place(sfx, boom, 56.4, 0.9)
x = lp(tone(NOTE(33), 3.0, "saw", 0.01), 200)*env(0.01, 0.5, 0.6, 1.5, 3.0); place(music, x, 56.4, 0.15)

# ---------------- ambiente y efectos
wh, wsr = sf.read("/home/claude/tiktok/sfx/whoosh.wav"); wh = wh.mean(1) if wh.ndim > 1 else wh
wh = librosa.resample(wh, orig_sr=wsr, target_sr=SR)
rain = bp(rng.normal(0, 1, N), 800, 7000)*0.06
rain_m = gate([(0, 1.70, 1), (11.45, 12.85, 1), (34.4, 36.0, 0.6)], 0.01)
amb += rain*rain_m
city = lp(rng.normal(0, 1, N), 400)*0.05
amb += city*gate([(0, 1.70, 1), (11.45, 12.85, 1), (23.25, 34.4, 0.7), (34.4, 36.0, 0.6)], 0.01)
cafe = bp(rng.normal(0, 1, N), 250, 2500)*0.03*(1+0.5*np.sin(2*np.pi*3.1*t)*np.sin(2*np.pi*0.7*t))
amb += cafe*gate([(12.85, 13.95, 1), (14.85, 16.4, 1)], 0.01)
crowd = bp(rng.normal(0, 1, N), 300, 3000)*0.04
amb += crowd*gate([(16.4, 17.3, 0.8), (18.45, 19.85, 2.2)], 0.03)
for k in range(30):   # teclados
    for tk in (19.85+k*0.11+rng.random()*0.05,):
        if 20.35 < tk < 21.65 or tk > 23.2: continue
        click = hp(rng.normal(0, 1, int(0.01*SR)), 2000)*np.linspace(1, 0, int(0.01*SR)); place(sfx, click, tk, 0.05)
# coche: motor que se acerca (0–1.7) y pasa (11.45–12.4)
d = 1.7; f = np.linspace(70, 120, int(d*SR))
eng = lp(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)), 900)*np.linspace(0.1, 1, int(d*SR))**2
place(sfx, eng, 0.0, 0.18)
horn = (np.sign(np.sin(2*np.pi*415*np.arange(int(0.45*SR))/SR))+np.sign(np.sin(2*np.pi*349*np.arange(int(0.45*SR))/SR)))*0.5
place(sfx, lp(horn, 2500)*env(0.01, 0.1, 0.8, 0.05, 0.45), 1.05, 0.1)
d = 1.1; f = np.linspace(140, 60, int(d*SR))
eng = lp(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)), 900)*np.concatenate([np.linspace(1, 0.9, int(0.3*SR)), np.linspace(0.9, 0, int(0.8*SR))])
place(sfx, eng, 11.45, 0.22); place(sfx, wh, 11.4, 0.8)
splash = bp(rng.normal(0, 1, int(0.6*SR)), 1500, 8000)*np.exp(-np.arange(int(0.6*SR))/SR*5); place(sfx, splash, 11.55, 0.3)

def freeze_sfx(at, violet=False):
    n = int(0.45*SR)
    sw = hp(rng.normal(0, 1, n), 1500)*np.linspace(0, 1, n)**3          # succión
    place(sfx, sw, at-0.45, 0.25)
    dr = np.sin(2*np.pi*np.cumsum(np.linspace(220 if not violet else 110, 40, int(0.9*SR)))/SR)*np.exp(-np.arange(int(0.9*SR))/SR*3.5)
    place(sfx, dr, at, 0.45)
    ping = sum(np.sin(2*np.pi*fq*np.arange(int(1.6*SR))/SR) for fq in ((1760, 2637) if not violet else (523, 740)))*np.exp(-np.arange(int(1.6*SR))/SR*2.2)
    place(sfx, reverb(ping, 1.8, 0.5), at, 0.05)
def snap_sfx(at, g=0.5):
    n = int(0.03*SR); s = hp(rng.normal(0, 1, n), 2500)*np.exp(-np.arange(n)/SR*180)
    place(sfx, reverb(np.concatenate([s, np.zeros(int(0.4*SR))]), 0.8, 0.25), at, g)
def resume_sfx(at):
    w = wh[:int(0.8*SR)][::-1]; place(sfx, w*np.linspace(0.3, 1, len(w)), at-len(w)/SR+0.05, 0.35)

for a, b in [(1.70, 11.45), (13.95, 14.85), (17.30, 18.45), (20.35, 21.65), (36.0, None)]:
    freeze_sfx(a)
    if b: snap_sfx(b-0.03); resume_sfx(b)
for at in (13.95, 17.29, 20.34, 35.93): snap_sfx(at, 0.45)
snap_sfx(48.42, 0.7); freeze_sfx(48.45, violet=True)
# patada, gol
kick = lp(rng.normal(0, 1, int(0.08*SR)), 800)*np.linspace(1, 0, int(0.08*SR)); place(sfx, kick, 16.6, 0.6)
net = bp(rng.normal(0, 1, int(0.4*SR)), 400, 3000)*np.exp(-np.arange(int(0.4*SR))/SR*8); place(sfx, net, 18.8, 0.3)
# pasos: Leo caminando de noche (34.4–37.8), la figura (39.1–44.3), la multitud (49.0–56.4)
def step(g=1.0, low=900):
    n = int(0.09*SR); return lp(rng.normal(0, 1, n), low)*np.exp(-np.arange(n)/SR*45)*g
tk = 34.45
while tk < 37.8: place(sfx, step(0.5), tk, 0.25); tk += 0.42
tk = 38.0
while tk < 44.5: place(sfx, reverb(np.concatenate([step(1, 600), np.zeros(int(0.5*SR))]), 1.6, 0.45), tk, 0.6); tk += 0.62
for k in range(140):
    tk = 49.0+rng.random()*7.3; place(sfx, step(0.6+rng.random()*0.4, 700+rng.random()*500), tk, 0.12*(tk-48)/8)
# ---------------- voces
CL = {"P1": ("pro", 0.0, 0.775, 1.25), "N1": ("nar", 0.0, 3.225, 2.10), "P2": ("pro", 0.775, 2.505, 8.95),
      "N2": ("nar", 3.455, 7.78, 12.85), "P4": ("pro", 4.055, 5.305, 18.55),
      "P5": ("pro", 5.305, 6.905, 21.75), "N3": ("nar", 7.78, 15.345, 24.30), "N4": ("nar", 15.345, 19.86, 34.50),
      "P6": ("pro", 6.905, 8.32, 42.30), "F1": ("fig", 0.0, 3.52, 44.30), "N5": ("nar", 19.86, 24.32, 51.60)}
vo = np.zeros(N); dia = np.zeros(N)
cache = {}
for cid, (f, a, b, at) in CL.items():
    if f not in cache:
        y, _ = librosa.load(f"/home/claude/t3d/au/{f}.mp3", sr=SR); cache[f] = y
    seg = cache[f][int(a*SR):int(b*SR)].copy()
    fl = min(len(seg)//4, int(0.012*SR)); seg[:fl] *= np.linspace(0, 1, fl); seg[-fl:] *= np.linspace(1, 0, fl)
    if f == "fig": seg = reverb(seg, 1.2, 0.18); seg = seg + 0.35*lp(seg, 250)
    if f == "pro": seg = reverb(seg, 0.7, 0.10 if cid not in ("P6",) else 0.25)
    (vo if f == "nar" else dia).__setitem__(slice(int(at*SR), int(at*SR)+len(seg)), (vo if f == "nar" else dia)[int(at*SR):int(at*SR)+len(seg)] + seg)
voice = vo*1.0 + dia*1.05
# ducking de la música bajo la voz
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.55*np.clip(ven/0.05, 0, 1)
bed = music*duck + amb*(1-0.3*np.clip(ven/0.05, 0, 1))
mix = bed + sfx + voice
mix = np.tanh(mix*1.25)/1.25
mix = mix/np.max(np.abs(mix))*0.93
# estéreo: ambiente ligeramente decorrelado
L = mix + 0.02*np.roll(amb, 240); R = mix + 0.02*np.roll(amb, -240)
st = np.stack([L, R], 1); st = st/np.max(np.abs(st))*0.93
sf.write("/home/claude/t3d/mix.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2), "s")
