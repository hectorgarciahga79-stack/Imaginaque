"""Q8 · Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 62.64
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
# ---- música A: oscura submarina (0–37.1), 90 bpm
beat = 60/90
for b_ in range(int(37.0/beat)):
    t0 = b_*beat; n_ = [33, 33, 36, 31][(b_//4) % 4]
    x = lp(tone(NOTE(n_), beat*0.9, "saw", 0.006), 380)*env(0.02, 0.2, 0.5, 0.2, beat*0.9)
    place(music, x, t0, 0.10)
    if b_ % 2 == 0: place(music, thump(0.3, 45)[:int(0.4*SR)], t0)
for t0, ch in ((0, (45, 48, 52)), (10.6, (43, 47, 50)), (21.2, (41, 45, 48)), (31.6, (45, 48, 52))):
    dd = 10.6 if t0 < 31 else 5.6
    for n_ in ch:
        x = lp(tone(NOTE(n_), dd, "saw", 0.005), 700)*env(1.2, 1.0, 0.8, 1.2, dd); place(music, x, t0, 0.03)
x = lp(tone(NOTE(28), 2.8, "saw", 0.01), 200)*env(0.4, 0.5, 0.8, 0.5, 2.8); place(music, x, 37.2, 0.14)
# ---- música B: huida (41.3–50.2), 140 bpm
beat = 60/140
for b_ in range(int(8.9/beat)):
    t0 = 41.3+b_*beat; n_ = [38, 38, 41, 40][(b_//4) % 4]
    place(music, lp(tone(NOTE(n_), beat*0.8, "saw", 0.006), 700)*env(0.005, 0.15, 0.4, 0.1, beat*0.8), t0, 0.11)
    place(music, thump(0.4, 55)[:int(0.3*SR)], t0)
# ---- música C: juguetona (50.2–62.6)
beat = 0.5; chords = [(60, 64, 67), (65, 69, 72), (67, 71, 74), (60, 64, 67)]
for bar in range(7):
    ch = chords[bar % 4]; t0 = 50.2+bar*beat*4
    for k in range(8):
        n_ = ch[(k*2) % 3]+12*(k % 2)
        place(music, lp(tone(NOTE(n_), 0.22, "saw"), 3200)*env(0.003, 0.16, 0.0, 0.05, 0.22), t0+k*beat/2, 0.05)
    place(music, lp(tone(NOTE(ch[0]-24), beat*4, "saw"), 400)*env(0.01, 0.3, 0.6, 0.3, beat*4), t0, 0.07)
music[int(62.1*SR):] *= np.linspace(1, 0, N-int(62.1*SR))
# ---- efectos
place(amb, waves(5.0), 0.0, 0.25); place(amb, waves(10.3), 37.16, 0.22); place(amb, waves(5.0), 50.2, 0.15)
place(sfx, groan(1.3, 105), 1.0, 0.35); place(sfx, groan(1.6, 90), 3.2, 0.3)
for k in range(110):
    tk = 5.0+rng.random()*26.5
    if 28.0 < tk < 31.56: continue
    place(sfx, bubble(), tk, 0.12)
for t0 in np.arange(5.2, 25.9, 1.4): place(sfx, thump(0.3, 38), t0, 0.25)
place(sfx, whale(2.2), 25.9, 0.35)
for t0 in (28.1, 29.4, 30.7): place(sfx, ping(), t0, 0.22)
place(sfx, groan(1.0, 80), 32.0, 0.25)
place(sfx, thump(1.0, 40), 39.95, 0.8); place(sfx, groan(1.8, 95), 40.0, 0.5)
for k in range(30):
    tk = 41.3+k*0.14+rng.random()*0.08; place(sfx, groan(0.5, 80+rng.random()*60), tk, 0.08)
place(amb, siren(4.6), 45.5, 0.10)
for t0 in (4.98, 10.6, 15.24, 19.1, 25.94, 28.0, 31.56, 37.16, 41.28, 45.46, 47.78, 50.22, 56.94): place(sfx, whoosh(), t0-0.2, 0.12)
place(sfx, bell(), 54.0, 0.15)
# ---- voz (voice.wav ya trae 0,15 s de margen)
y, _ = librosa.load("/home/claude/anim/build/Q8/voice.wav", sr=SR)
voice = np.zeros(N); voice[:min(N, len(y))] = y[:N]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_q8.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
