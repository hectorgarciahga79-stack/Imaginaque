"""Q11 · Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 63.31
N = int(TOT*SR)
rng = np.random.default_rng(11)
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
# ---- música A: despertar épico (0–14.7), 110 bpm
def ring(d=1.2):
    tt = np.arange(int(d*SR))/SR
    return np.sin(2*np.pi*2400*tt)*(np.sin(2*np.pi*14*tt) > 0)*0.5
def boom(d=1.8):
    tt = np.arange(int(d*SR))/SR
    return lp(rng.normal(0, 1, len(tt)), 180)*np.exp(-tt*2.5)*3 + thump(1.0, 32)[:len(tt)] if len(tt) <= int(0.7*SR) else np.concatenate([thump(1.0, 32), np.zeros(len(tt)-int(0.7*SR))])*1.0 + lp(rng.normal(0, 1, len(tt)), 180)*np.exp(-tt*2.5)*3
def wind(d):
    tt = np.arange(int(d*SR))/SR
    return bp(rng.normal(0, 1, len(tt)), 300, 2500)*(0.6+0.4*np.sin(tt*3))
place(sfx, ring(1.2), 0.2, 0.10); place(sfx, ring(1.2), 1.6, 0.10); place(sfx, ring(1.0), 3.0, 0.08)
def rumble(d, f=35):
    tt = np.arange(int(d*SR))/SR
    return lp(rng.normal(0, 1, len(tt)), 120)*3*(0.6+0.4*np.sin(tt*2.3)) + 0.4*np.sin(2*np.pi*f*tt)
# ---- música: pulso grave tenso → percusión de catástrofe → pad frío → giro cálido
beat = 60/96
for b_ in range(int(20.5/beat)):
    t0 = b_*beat; n_ = [38, 38, 41, 36][(b_//4) % 4]
    place(music, lp(tone(NOTE(n_), beat*0.85, "saw", 0.006), 600)*env(0.01, 0.2, 0.5, 0.15, beat*0.85), t0, 0.09)
    if b_ % 2 == 0: place(music, thump(0.4, 46)[:int(0.4*SR)], t0)
for k in range(10):
    place(music, lp(tone(NOTE([74, 77, 81, 79][k % 4]), 0.22, "saw"), 2600)*env(0.003, 0.18, 0.0, 0.05, 0.22), 0.4+k*0.6, 0.02)
for t0, ch, dd in ((20.56, (38, 45, 50), 8.3), (28.96, (36, 43, 48), 5.9), (34.86, (34, 41, 46, 50), 5.7)):
    for n_ in ch:
        place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 1000)*env(0.4, 0.8, 0.8, 0.8, dd), t0, 0.045)
beat = 60/120
for b_ in range(int(7.0/beat)):
    place(music, thump(0.3, 55)[:int(0.25*SR)], 40.6+b_*beat)
    place(music, lp(tone(NOTE([45, 45, 48, 43][(b_//2) % 4]), beat*0.7, "saw", 0.006), 900)*env(0.005, 0.15, 0.4, 0.1, beat*0.7), 40.6+b_*beat, 0.08)
for b_ in range(int(4.6/0.25)):
    place(music, thump(0.25, 60)[:int(0.18*SR)], 47.96+b_*0.25)
beat = 0.5; chords = [(57, 60, 64), (53, 57, 60), (55, 59, 62), (57, 60, 64)]
for bar in range(5):
    ch = chords[bar % 4]; t0 = 52.6+bar*beat*4
    for k in range(8):
        place(music, lp(tone(NOTE(ch[(k*2) % 3]+12*(k % 2)), 0.22, "saw"), 3000)*env(0.003, 0.16, 0.0, 0.05, 0.22), t0+k*beat/2, 0.04)
    place(music, lp(tone(NOTE(ch[0]-24), beat*4, "saw"), 400)*env(0.01, 0.3, 0.6, 0.3, beat*4), t0, 0.07)
music[int(62.8*SR):] *= np.linspace(1, 0, N-int(62.8*SR))
# ---- efectos
place(sfx, boom(1.8), 0.3, 0.5); place(sfx, boom(1.8), 5.76, 1.0); place(amb, rumble(4.0), 3.5, 0.10)
place(sfx, boom(1.8), 7.95, 1.0); place(amb, rumble(12.6), 7.9, 0.14)
for k in range(12): place(sfx, thump(0.5, 70+k*5), 8.4+k*0.6, 0.25)
place(amb, wind(5.3), 15.3, 0.10)
place(sfx, crunch(), 19.4, 0.9); place(sfx, thump(1.0, 40), 19.45, 0.8)
place(amb, rumble(6.0), 20.6, 0.05); place(amb, wind(2.1), 26.9, 0.12)
place(sfx, boom(1.8), 31.4, 0.6); place(amb, rumble(5.9), 28.96, 0.12)
place(amb, wind(5.7), 34.86, 0.14); place(sfx, crunch(), 35.1, 0.3)
for t0 in (3.46, 7.44, 12.0, 15.3, 20.56, 26.9, 28.96, 34.86, 40.58, 47.96, 52.6, 57.5): place(sfx, whoosh(), t0-0.2, 0.12)
y, _ = librosa.load("/home/claude/anim/build/Q11/voice.wav", sr=SR)
voice = np.zeros(N); voice[:min(N, len(y))] = y[:N]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_q11.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
