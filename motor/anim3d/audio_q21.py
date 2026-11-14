"""Q21 · Banda sonora propia (sintetizada) + efectos + voces → mix.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 76.99
N = int(TOT*SR)
rng = np.random.default_rng(21)
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
place(sfx, ring(1.2), 0.2, 0.10); place(sfx, ring(1.2), 1.6, 0.10); place(sfx, ring(1.0), 3.0, 0.08)
def chaching():
    tt = np.arange(int(0.5*SR))/SR
    return (np.sin(2*np.pi*1800*tt)+0.6*np.sin(2*np.pi*2700*tt))*np.exp(-tt*9)*0.6 + bp(rng.normal(0, 1, len(tt)), 3000, 8000)*np.exp(-tt*30)*0.4
def knock():
    tt = np.arange(int(0.18*SR))/SR; return lp(rng.normal(0, 1, len(tt)), 600)*np.exp(-tt*30)*2 + np.sin(2*np.pi*90*tt)*np.exp(-tt*25)
def phone_ring(d=1.2):
    tt = np.arange(int(d*SR))/SR; return (np.sin(2*np.pi*1300*tt)+np.sin(2*np.pi*1700*tt))*(np.sin(2*np.pi*20*tt) > 0)*0.3
def creak(d=1.4):
    tt = np.arange(int(d*SR))/SR; f = 140+40*np.sin(2*np.pi*1.3*tt)
    return bp((2*((np.cumsum(f)/SR) % 1)-1), 200, 1500)*np.minimum(1, tt/0.2)*np.minimum(1, (d-tt)/0.3)
def siren(d):
    tt = np.arange(int(d*SR))/SR; f = 700+250*np.sin(2*np.pi*0.8*tt)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*0.3
# ---- música: pulso tenso (gancho) → caja de música (flashback) → funk de riqueza → épica → silencio final
for t0, ch, dd in ((0.0, (38, 45, 50), 7.4),):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 800)*env(0.3, 0.8, 0.8, 0.8, dd), t0, 0.05)
for b_ in range(14): place(music, thump(0.35, 45)[:int(0.35*SR)], b_*0.53)
mb = [72, 76, 79, 84, 79, 76, 74, 77, 81, 77]
for k in range(26): place(music, reverb(np.sin(2*np.pi*NOTE(mb[k % 10])*np.arange(int(0.6*SR))/SR)*np.exp(-np.arange(int(0.6*SR))/SR*5), 1.5, 0.4), 7.5+k*0.5, 0.035)
beat = 60/118
for b_ in range(int(15.5/beat)):
    t0 = 20.54+b_*beat; n_ = [48, 48, 53, 55][(b_//4) % 4]
    place(music, lp(tone(NOTE(n_), beat*0.6, "saw", 0.006), 900)*env(0.005, 0.12, 0.3, 0.08, beat*0.6), t0, 0.08)
    if b_ % 2 == 0: place(music, thump(0.35, 55)[:int(0.3*SR)], t0)
    place(music, hp(rng.normal(0, 1, int(0.05*SR)), 6000)*np.linspace(1, 0, int(0.05*SR)), t0+beat/2, 0.04)
beat = 60/128
for b_ in range(int(26.9/beat)):
    t0 = 34.62+b_*beat; n_ = [45, 45, 48, 43][(b_//4) % 4]
    place(music, lp(tone(NOTE(n_), beat*0.8, "saw", 0.006), 1000)*env(0.005, 0.15, 0.4, 0.1, beat*0.8), t0, 0.09)
    place(music, thump(0.36, 50)[:int(0.3*SR)], t0)
for t0, ch, dd in ((42.14, (45, 52, 57), 8.6), (50.8, (43, 50, 55, 59), 10.2), (60.98, (38, 45, 50, 53), 8.0)):
    for n_ in ch: place(music, lp(tone(NOTE(n_), dd, "saw", 0.005), 1100)*env(0.4, 0.8, 0.8, 0.8, dd), t0, 0.045)
for k in range(8): place(music, reverb(np.sin(2*np.pi*NOTE([72, 76, 79, 84][k % 4])*np.arange(int(0.8*SR))/SR)*np.exp(-np.arange(int(0.8*SR))/SR*4), 1.8, 0.5), 69.0+k*0.9, 0.04)
music[int(76.4*SR):] *= np.linspace(1, 0, N-int(76.4*SR))
# ---- efectos
for k in range(5): place(sfx, knock(), 4.6+k*0.8, 0.6)
place(amb, siren(7.0), 0.5, 0.05); place(amb, siren(8.0), 68.9, 0.05)
place(sfx, chaching(), 11.0, 0.5)
for k in range(5): place(sfx, chaching(), 20.6+k*1.2, 0.25)
place(sfx, creak(1.6), 32.1, 0.4); place(sfx, crunch(), 33.0, 0.3)
place(sfx, boom(1.8), 48.4, 0.9); place(sfx, crunch(), 48.5, 0.6)
place(sfx, phone_ring(1.4), 56.1, 0.25); place(sfx, phone_ring(1.4), 57.6, 0.25)
place(sfx, boom(1.8), 65.0, 0.4); place(sfx, crunch(), 69.0, 0.2)
for t0 in (7.46, 13.9, 20.54, 27.02, 34.62, 39.2, 42.14, 46.0, 50.8, 60.98, 68.92): place(sfx, whoosh(), t0-0.2, 0.12)
y, _ = librosa.load("/home/claude/anim/build/Q21/voice.wav", sr=SR)
voice = np.zeros(N); voice[:min(N, len(y))] = y[:N]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_q21.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
