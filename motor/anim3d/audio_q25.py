"""Q25 · Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 78.19
N = int(TOT*SR)
rng = np.random.default_rng(25)
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
def tick():
    tt = np.arange(int(0.05*SR))/SR; return np.sin(2*np.pi*1800*tt)*np.exp(-tt*90)
def horn(d=1.4):
    tt = np.arange(int(d*SR))/SR; return (np.sign(np.sin(2*np.pi*220*tt))+np.sign(np.sin(2*np.pi*277*tt)))*0.25*env(0.02, 0.1, 0.9, 0.2, d)
# música: pulso tenso (0–17), caos (17–24), euforia (24–35.6), tensión creciente (35.6–55), alivio y giro (55–78)
for t0, ch, dd in ((0.0, (45, 52, 57), 8.6), (8.62, (43, 50, 55), 8.6)):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 900)*env(0.5, 0.8, 0.8, 0.8, dd), t0, 0.05)
for b_ in range(int(17.2/0.5)): place(music, thump(0.3, 48)[:int(0.3*SR)], b_*0.5)
for t0, ch, dd in ((17.2, (41, 48, 53), 6.7),):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 900)*env(0.3, 0.8, 0.8, 0.5, dd), t0, 0.06)
beat = 60/118
for b_ in range(int(11.6/beat)):
    t0 = 23.94+b_*beat; n_ = [57, 61, 64, 66, 64, 61][b_ % 6]
    place(music, lp(tone(NOTE(n_+12), beat*0.5, "saw"), 3000)*env(0.003, 0.15, 0.1, 0.05, beat*0.5), t0, 0.035)
    place(music, thump(0.3, 50)[:int(0.3*SR)], t0)
for t0, ch, dd in ((35.66, (40, 47, 52), 8.4), (44.06, (38, 45, 50), 5.2), (49.26, (36, 43, 48), 5.9)):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 900)*env(0.5, 0.8, 0.8, 0.8, dd), t0, 0.05)
beat = 60/100
for b_ in range(int(19.3/beat)): place(music, thump(0.32, 45)[:int(0.3*SR)], 35.66+b_*beat*(1 if 35.66+b_*beat < 50 else 0.5))
for t0, ch, dd in ((57.0, (48, 55, 60, 64, 67), 8.9), (65.9, (53, 57, 60, 65), 8.9), (74.8, (48, 55, 60, 64), 3.4)):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 1600)*env(0.6, 0.8, 0.8, 0.9, dd), t0, 0.045)
for k in range(24): place(music, reverb(np.sin(2*np.pi*NOTE([84, 88, 91, 86][k % 4])*np.arange(int(0.8*SR))/SR)*np.exp(-np.arange(int(0.8*SR))/SR*4), 2.0, 0.5), 61.6+k*0.5, 0.022)
music[int(55.3*SR):int(57.0*SR)] *= 0.15
music[int(77.6*SR):] *= np.linspace(1, 0, N-int(77.6*SR))
# efectos
for k in range(8): place(sfx, tick(), 6.4+k*0.25, 0.25)
place(sfx, thump(0.7, 60), 7.4, 0.5)
place(amb, rumble(6.7), 17.2, 0.08)
for k in range(5): place(sfx, ring(0.9), 17.6+k*1.2, 0.04)
place(amb, wind(1.2), 32.4, 0.2)
place(amb, bp(rng.normal(0, 1, int(1.3*SR)), 120, 900)*np.linspace(0.3, 1, int(1.3*SR)), 34.4, 0.2)
place(amb, bp(rng.normal(0, 1, int(8.4*SR)), 60, 400), 35.66, 0.04); place(amb, bp(rng.normal(0, 1, int(8.4*SR)), 60, 400), 0.0, 0.035)
for k in range(10): place(sfx, tick(), 51.8+k*0.4, 0.3)
place(sfx, horn(1.4), 54.0, 0.35); place(amb, rumble(3.0, 40), 53.5, 0.2)
place(sfx, boom(1.8), 55.6, 0.8); place(sfx, thump(0.6, 70), 56.9, 0.6)
place(sfx, ping(), 61.6, 0.25); place(sfx, thump(0.8, 40), 64.6, 0.5)
for t0 in (8.62, 17.2, 23.94, 32.4, 33.6, 34.4, 35.66, 44.06, 49.26, 59.34, 65.9, 74.8): place(sfx, whoosh(), t0-0.2, 0.12)
y, _ = librosa.load("/home/claude/anim/build/Q25/voice.wav", sr=SR)
voice = np.zeros(N); voice[:min(N, len(y))] = y[:N]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_q25.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
