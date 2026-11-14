"""Q27 · Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 75.0
N = int(TOT*SR)
rng = np.random.default_rng(27)
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
def ring(d=1.2):
    tt = np.arange(int(d*SR))/SR
    return np.sin(2*np.pi*2400*tt)*(np.sin(2*np.pi*14*tt) > 0)*0.5
def boom(d=1.8):
    tt = np.arange(int(d*SR))/SR
    return lp(rng.normal(0, 1, len(tt)), 180)*np.exp(-tt*2.5)*3 + thump(1.0, 32)[:len(tt)] if len(tt) <= int(0.7*SR) else np.concatenate([thump(1.0, 32), np.zeros(len(tt)-int(0.7*SR))])*1.0 + lp(rng.normal(0, 1, len(tt)), 180)*np.exp(-tt*2.5)*3
def wind(d):
    tt = np.arange(int(d*SR))/SR
    return bp(rng.normal(0, 1, len(tt)), 300, 2500)*(0.6+0.4*np.sin(tt*3))
def rumble(d, f=35):
    tt = np.arange(int(d*SR))/SR
    return lp(rng.normal(0, 1, len(tt)), 120)*3*(0.6+0.4*np.sin(tt*2.3)) + 0.4*np.sin(2*np.pi*f*tt)
def glass():
    out = np.zeros(int(1.2*SR))
    for k in range(40):
        i = int(rng.random()*0.9*SR); tt = np.arange(int(0.1*SR))/SR; out[i:i+len(tt)] += np.sin(2*np.pi*(3000+rng.random()*4000)*tt)*np.exp(-tt*50)*0.3
    return out
def clink():
    tt = np.arange(int(0.5*SR))/SR; return (np.sin(2*np.pi*2600*tt)+0.6*np.sin(2*np.pi*3900*tt))*np.exp(-tt*9)
def beep():
    tt = np.arange(int(0.12*SR))/SR; return np.sin(2*np.pi*1000*tt)*0.5
def drip():
    tt = np.arange(int(0.2*SR))/SR; return np.sin(2*np.pi*(900-2500*tt)*tt)*np.exp(-tt*25)
def phone_ring(d):
    tt = np.arange(int(d*SR))/SR; return (np.sin(2*np.pi*880*tt)+np.sin(2*np.pi*1100*tt))*(np.sin(2*np.pi*12*tt) > 0)*0.3*((tt % 1.0) < 0.6)
for t0, ch, dd in ((0.0, (45, 52, 57), 7.7), (7.66, (47, 54, 59), 6.7), (14.38, (43, 50, 55), 4.5)):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 900)*env(0.5, 0.8, 0.8, 0.8, dd), t0, 0.05)
beat = 60/120
for b_ in range(int(7.9/beat)):
    t0 = 18.92+b_*beat; n_ = [62, 66, 69, 74, 69, 66][b_ % 6]
    place(music, lp(tone(NOTE(n_+12), beat*0.5, "saw"), 3000)*env(0.003, 0.15, 0.1, 0.05, beat*0.5), t0, 0.03)
    place(music, thump(0.3, 50)[:int(0.3*SR)], t0)
for t0, ch, dd in ((26.84, (40, 47, 52), 12.0), (38.86, (38, 45, 50), 9.1), (47.92, (41, 48, 53), 9.0)):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 900)*env(0.5, 0.8, 0.8, 0.8, dd), t0, 0.05)
beat = 60/96
for b_ in range(int(18/beat)): place(music, thump(0.32, 45)[:int(0.3*SR)], 38.86+b_*beat)
for t0, ch, dd in ((56.88, (48, 55, 60, 64), 3.6), (60.44, (53, 57, 60, 65), 8.6), (69.06, (48, 55, 60, 64, 67), 5.9)):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 1600)*env(0.6, 0.8, 0.8, 0.9, dd), t0, 0.045)
for k in range(14): place(music, reverb(np.sin(2*np.pi*NOTE([84, 88, 91, 86][k % 4])*np.arange(int(0.8*SR))/SR)*np.exp(-np.arange(int(0.8*SR))/SR*4), 2.0, 0.5), 64.4+k*0.7, 0.02)
music[int(74.5*SR):] *= np.linspace(1, 0, N-int(74.5*SR))
place(sfx, crunch(), 0.7, 0.3); place(sfx, clink(), 4.4, 0.5); place(sfx, clink(), 10.4, 0.3)
place(sfx, ping(), 12.1, 0.2)
for k in range(6): place(sfx, clink(), 19.6+k*0.33, 0.12)
for k in range(5): place(sfx, thump(0.4, 55), 28.0+k*2.0, 0.25)
place(sfx, phone_ring(1.8), 42.8, 0.3)
for k in range(int(9/0.9)): place(sfx, beep(), 48.0+k*(0.9 if 48+k*0.9 < 52.8 or 48+k*0.9 > 55.4 else 1.5), 0.12)
place(amb, wind(3.6), 56.88, 0.05)
place(sfx, drip(), 64.4, 0.5)
for t0 in (7.66, 14.38, 18.92, 22.0, 26.84, 38.86, 47.92, 56.88, 60.44, 69.06): place(sfx, whoosh(), t0-0.2, 0.12)
y, _ = librosa.load("/home/claude/anim/build/Q27/voice.wav", sr=SR)
voice = np.zeros(N); voice[:min(N, len(y))] = y[:N]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_q27.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
