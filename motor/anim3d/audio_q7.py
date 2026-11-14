"""Q7 · Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 56.6
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
def thump(g=1.0, f=48):
    d = 0.7; tt = np.arange(int(d*SR))/SR
    x = np.sin(2*np.pi*(f+60*np.exp(-tt*18))*tt)*np.exp(-tt*6) + 0.5*lp(rng.normal(0, 1, len(tt)), 300)*np.exp(-tt*14)
    return x*g
def roar(d=1.4):
    tt = np.arange(int(d*SR))/SR
    f = 95 + 50*np.sin(np.pi*tt/d)
    ph = np.cumsum(f)/SR
    x = (2*(ph % 1)-1)*(0.6+0.4*np.sin(2*np.pi*31*tt))
    n = bp(rng.normal(0, 1, len(tt)), 200, 1800)
    e = np.minimum(1, tt/0.15)*np.minimum(1, (d-tt)/0.4)
    return reverb(lp(x, 900)*0.7 + n*0.5, 1.4, 0.3)*e
def crunch():
    d = 0.6; tt = np.arange(int(d*SR))/SR
    n = rng.normal(0, 1, len(tt))*(rng.random(len(tt)) < 0.08)
    x = bp(n, 800, 6000)*np.exp(-tt*5) + thump(0.8, 60)[:len(tt)]
    return x
def whoosh(d=0.45):
    tt = np.arange(int(d*SR))/SR; e = np.sin(np.pi*tt/d)**2
    return bp(rng.normal(0, 1, len(tt)), 400, 3000)*e
def siren(d):
    tt = np.arange(int(d*SR))/SR; f = 700 + 250*np.sin(2*np.pi*0.8*tt)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*0.5
def cluck():
    out = np.zeros(int(0.5*SR))
    for k, a in enumerate((0.0, 0.12, 0.22)):
        tt = np.arange(int(0.08*SR))/SR; f = 900-2000*tt
        x = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*30)
        i = int(a*SR); out[i:i+len(x)] += x
    return bp(out, 400, 4000)
def bell():
    tt = np.arange(int(0.8*SR))/SR
    return (np.sin(2*np.pi*2100*tt)+0.6*np.sin(2*np.pi*3150*tt))*np.exp(-tt*6)
# ---- música A: tensión (0–36.7), 100 bpm, bajo y golpes
beat = 60/100
for b_ in range(int(36.6/beat)):
    t0 = b_*beat
    n_ = [38, 38, 41, 36][(b_//4) % 4]
    x = lp(tone(NOTE(n_), beat*0.9, "saw", 0.006), 500)*env(0.01, 0.2, 0.5, 0.2, beat*0.9)
    place(music, x, t0, 0.10)
    if b_ % 2 == 0: place(music, thump(0.35, 55)[:int(0.4*SR)], t0)
    if b_ % 4 == 2: place(music, hp(rng.normal(0, 1, int(0.05*SR)), 5000)*np.linspace(1, 0, int(0.05*SR)), t0, 0.08)
for t0, ch in ((0, (50, 53, 57)), (9.6, (48, 52, 55)), (19.2, (46, 50, 53)), (28.8, (50, 53, 57))):
    for n_ in ch:
        x = lp(tone(NOTE(n_), 9.6 if t0 < 28 else 7.9, "saw", 0.005), 900)*env(1.0, 1.0, 0.8, 1.2, 9.6 if t0 < 28 else 7.9)
        place(music, x, t0, 0.03)
# susurro: dron grave
x = lp(tone(NOTE(33), 3.0, "saw", 0.01), 220)*env(0.4, 0.5, 0.8, 0.5, 3.0); place(music, x, 36.7, 0.12)
# ---- música B: juguetona (39.7–56.6), 120 bpm, plucks en Do mayor
beat = 0.5; chords = [(60, 64, 67), (65, 69, 72), (67, 71, 74), (60, 64, 67)]
for bar in range(int(16.9/(beat*4))+1):
    ch = chords[bar % 4]; t0 = 39.7+bar*beat*4
    for k in range(8):
        n_ = ch[(k*2) % 3]+12*(k % 2)
        x = lp(tone(NOTE(n_), 0.22, "saw"), 3200)*env(0.003, 0.16, 0.0, 0.05, 0.22)
        place(music, x, t0+k*beat/2, 0.05)
    x = lp(tone(NOTE(ch[0]-24), beat*4, "saw"), 400)*env(0.01, 0.3, 0.6, 0.3, beat*4); place(music, x, t0, 0.07)
music[int(56.2*SR):] *= np.linspace(1, 0, N-int(56.2*SR))
# ---- efectos
place(sfx, roar(1.5), 0.55, 0.55)
for t0 in np.arange(2.5, 5.0, 0.91): place(sfx, thump(), t0, 0.6)
for t0 in (5.4, 7.2, 9.0): place(sfx, thump(), t0, 0.35)
place(sfx, roar(1.1), 10.6, 0.3)
place(sfx, crunch(), 15.45, 0.7); place(sfx, thump(1.0, 40), 15.45, 0.5)
for t0 in np.arange(16.9, 22.1, 1.19): place(sfx, thump(), t0, 0.45)
place(sfx, bell(), 22.35, 0.18); place(sfx, whoosh(0.6), 22.3, 0.2)
for k in range(46):
    tk = 23.7 + k*0.165 + rng.random()*0.1
    place(sfx, thump(0.4+0.6*min(1, (tk-23.6)/5), 40+rng.random()*20), tk, 0.35)
place(sfx, roar(1.6), 27.9, 0.45)
place(amb, siren(5.4), 31.3, 0.10)
for t0 in (31.8, 33.0, 34.4, 35.5): place(sfx, np.sin(2*np.pi*440*np.arange(int(0.35*SR))/SR)*0.5, t0, 0.10)
for t0 in (2.4, 5.08, 9.94, 13.72, 16.68, 22.2, 23.6, 31.3, 39.66, 47.3, 52.16): place(sfx, whoosh(), t0-0.2, 0.12)
place(sfx, cluck(), 44.5, 0.35); place(sfx, cluck(), 45.6, 0.25)
place(sfx, whoosh(0.35), 48.9, 0.2)
for t0 in (50.3, 50.8, 51.3, 51.8): place(sfx, thump(0.25, 90)[:int(0.2*SR)], t0, 0.35)
place(sfx, cluck(), 50.0, 0.3); place(sfx, cluck(), 53.3, 0.25)
x = lp(tone(NOTE(84), 0.5, "saw"), 4000)*env(0.003, 0.3, 0.0, 0.1, 0.5); place(sfx, x, 55.7, 0.12)
# ---- voz
y, _ = librosa.load("/home/claude/t3d/au/q7.mp3", sr=SR)
voice = np.zeros(N); i = int(0.15*SR); voice[i:i+len(y)] = y[:N-i]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_q7.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
