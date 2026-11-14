"""Q9 · Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 52.83
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

def waves(d):
    tt = np.arange(int(d*SR))/SR
    e = 0.55+0.45*np.sin(2*np.pi*tt/4.2)**2
    return lp(rng.normal(0, 1, len(tt)), 700)*e
def bubble():
    d = 0.12; tt = np.arange(int(d*SR))/SR; f = 500+rng.random()*900
    return np.sin(2*np.pi*np.cumsum(f*(1+tt*8))/SR)*np.exp(-tt*35)
def groan(d=1.2, f0=110):
    tt = np.arange(int(d*SR))/SR; f = f0*(1-0.25*tt/d)+6*np.sin(2*np.pi*5*tt)
    x = (2*((np.cumsum(f)/SR) % 1)-1); n = bp(rng.normal(0, 1, len(tt)), 300, 1500)
    e = np.minimum(1, tt/0.2)*np.minimum(1, (d-tt)/0.3)
    return reverb(lp(x, 700)*0.6+n*0.3, 1.2, 0.3)*e
def ping():
    tt = np.arange(int(1.0*SR))/SR
    return reverb(np.sin(2*np.pi*1250*tt)*np.exp(-tt*5), 1.6, 0.4)
def whale(d=2.0):
    tt = np.arange(int(d*SR))/SR; f = 180+260*np.sin(np.pi*tt/d)
    return reverb(np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/d)**2, 2.0, 0.5)
# ---- música A: misterio cósmico (0–16.2), 96 bpm
beat = 60/96
for b_ in range(int(16.0/beat)):
    t0 = b_*beat; n_ = [38, 38, 41, 36][(b_//4) % 4]
    place(music, lp(tone(NOTE(n_), beat*0.9, "saw", 0.006), 420)*env(0.02, 0.2, 0.5, 0.2, beat*0.9), t0, 0.09)
    if b_ % 2 == 0: place(music, thump(0.3, 45)[:int(0.4*SR)], t0)
for k in range(16):
    place(music, lp(tone(NOTE([74, 77, 81, 79][k % 4]), 0.25, "saw"), 3000)*env(0.003, 0.2, 0.0, 0.05, 0.25), k*1.0+0.3, 0.025)
# ---- música B: caos (16.2–30.5), 132 bpm
beat = 60/132
for b_ in range(int(14.2/beat)):
    t0 = 16.22+b_*beat; n_ = [38, 38, 41, 40][(b_//4) % 4]
    place(music, lp(tone(NOTE(n_), beat*0.8, "saw", 0.006), 750)*env(0.005, 0.15, 0.4, 0.1, beat*0.8), t0, 0.10)
    place(music, thump(0.38, 55)[:int(0.3*SR)], t0)
# ---- pads espaciales (30.5–47.1)
for t0, ch, dd in ((30.48, (38, 45, 50), 4.4), (34.82, (36, 43, 48), 5.8), (40.58, (34, 41, 46, 50), 6.6)):
    for n_ in ch:
        place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 900)*env(0.6, 1.0, 0.8, 1.0, dd), t0, 0.035)
x = lp(tone(NOTE(26), 3.0, "saw", 0.01), 220)*env(0.3, 0.5, 0.8, 0.6, 3.0); place(music, x, 44.0, 0.13)
# ---- música C: juguetona (47.1–52.8)
beat = 0.5; chords = [(60, 64, 67), (65, 69, 72), (67, 71, 74)]
for bar in range(3):
    ch = chords[bar % 3]; t0 = 47.1+bar*beat*4
    for k in range(8):
        place(music, lp(tone(NOTE(ch[(k*2) % 3]+12*(k % 2)), 0.22, "saw"), 3200)*env(0.003, 0.16, 0.0, 0.05, 0.22), t0+k*beat/2, 0.05)
    place(music, lp(tone(NOTE(ch[0]-24), beat*4, "saw"), 400)*env(0.01, 0.3, 0.6, 0.3, beat*4), t0, 0.07)
music[int(52.3*SR):] *= np.linspace(1, 0, N-int(52.3*SR))
# ---- efectos
def hum(d, f=55):
    tt = np.arange(int(d*SR))/SR
    return (np.sin(2*np.pi*f*tt)+0.5*np.sin(2*np.pi*f*1.5*tt*(1+0.002*np.sin(tt*3))))*np.minimum(1, tt/0.4)*np.minimum(1, (d-tt)/0.4)
def suck(d=1.2):
    tt = np.arange(int(d*SR))/SR; e = (tt/d)**2
    return bp(rng.normal(0, 1, len(tt)), 300, 2500)*e
place(sfx, thump(1.0, 40), 0.15, 0.6); place(amb, hum(16.0, 46), 0.2, 0.18)
place(sfx, whoosh(0.6), 7.6, 0.2); place(sfx, bell(), 9.6, 0.12)
for k in range(10): place(sfx, crunch(), 11.2+k*0.5+rng.random()*0.2, 0.08)
for k in range(14): place(sfx, suck(0.8), 16.3+k*0.34, 0.12)
for k in range(8): place(sfx, crunch(), 18.8+k*0.3, 0.2)
place(sfx, thump(1.0, 36), 18.7, 0.7); place(sfx, thump(0.8, 34), 21.24, 0.5)
place(amb, hum(9.0, 38), 21.3, 0.22)
for k in range(12): place(sfx, crunch(), 25.6+k*0.4, 0.1)
place(amb, lp(rng.normal(0, 1, int(4.3*SR)), 500)*np.sin(np.linspace(0, np.pi, int(4.3*SR))), 30.5, 0.35)
place(sfx, groan(1.6, 70), 34.9, 0.15)
for k in range(20): place(sfx, suck(0.9), 40.7+k*0.3, 0.08)
place(sfx, thump(1.0, 30), 46.9, 0.6); place(sfx, bell(), 47.4, 0.2)
for t0 in (4.68, 7.8, 10.88, 16.22, 18.7, 21.24, 25.42, 30.48, 34.82, 40.58, 47.1, 49.94): place(sfx, whoosh(), t0-0.2, 0.12)
# ---- voz (voice.wav ya trae 0,15 s de margen)
y, _ = librosa.load("/home/claude/anim/build/Q9/voice.wav", sr=SR)
voice = np.zeros(N); voice[:min(N, len(y))] = y[:N]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_q9.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
