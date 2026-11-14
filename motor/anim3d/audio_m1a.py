"""M1A · banda sonora sintetizada + efectos + voz → mix_m1a.wav"""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 75.0
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
def creak(d=0.9):
    tt = np.arange(int(d*SR))/SR
    f = 180 + 90*np.sin(2*np.pi*1.7*tt) + 40*rng.normal(0, 1, len(tt)).cumsum()/SR*20
    x = np.sin(2*np.pi*np.cumsum(f)/SR)*(0.5+0.5*(rng.random(len(tt)) < 0.3))
    return bp(x, 150, 2500)*np.sin(np.pi*tt/d)
def ping():
    tt = np.arange(int(0.35*SR))/SR
    return (np.sin(2*np.pi*3400*tt)+0.5*np.sin(2*np.pi*5100*tt))*np.exp(-tt*14)
def wind(d):
    return bp(rng.normal(0, 1, int(d*SR)), 200, 1400)
# ---- música: dron inquietante + pulso (0–72.8), 84 bpm, Re menor
beat = 60/84
for b_ in range(int(72.6/beat)):
    t0 = b_*beat
    if t0 < 3.2: continue
    n_ = [38, 38, 41, 37][(b_//8) % 4]
    x = lp(tone(NOTE(n_), beat*0.8, "saw", 0.006), 420)*env(0.01, 0.25, 0.4, 0.2, beat*0.8)
    place(music, x, t0, 0.09 if t0 > 22.9 else 0.06)
    if b_ % 2 == 0 and t0 > 22.9: place(music, thump(0.3, 50)[:int(0.4*SR)], t0)
    if b_ % 4 == 3 and t0 > 32: place(music, hp(rng.normal(0, 1, int(0.04*SR)), 6000)*np.linspace(1, 0, int(0.04*SR)), t0, 0.06)
for t0, dur, ch in ((0, 13.1, (50, 53, 57)), (13.1, 9.8, (49, 53, 56)), (22.9, 9.8, (46, 50, 53)), (32.7, 16.0, (50, 53, 57)),
                    (48.7, 12.2, (45, 49, 52)), (60.9, 11.9, (46, 50, 53))):
    for n_ in ch:
        x = lp(tone(NOTE(n_), dur, "saw", 0.005), 850)*env(1.0, 1.0, 0.8, 1.2, dur)
        place(music, x, t0, 0.028)
# pad agudo «sin gravedad»: glissando ascendente en los planos de caída
for t0, dur in ((0.0, 3.2), (17.8, 5.1), (22.9, 9.8), (44.7, 4.0), (53.6, 7.3)):
    tt = np.arange(int(dur*SR))/SR; f = 300*2**(tt/dur*1.0)
    x = np.sin(2*np.pi*np.cumsum(f)/SR)*env(0.4, 0.3, 0.8, 0.6, dur)
    place(music, x, t0, 0.035)
music[int(72.6*SR):] *= np.linspace(1, 0, N-int(72.6*SR))
# ---- efectos
place(sfx, thump(1.0, 45), 0.05, 0.6); place(sfx, whoosh(1.2), 0.2, 0.35); place(sfx, whoosh(0.8), 1.6, 0.3)
place(amb, wind(3.2), 0.0, 0.06)
place(sfx, thump(0.9, 50), 5.85, 0.6); place(sfx, crunch(), 5.9, 0.35)          # golpe contra el techo
place(sfx, bell()*0.3, 7.0, 0.15)                                              # reloj 3:07
for t0 in (18.5, 19.7, 21.0): place(sfx, whoosh(0.7), t0, 0.3)
place(amb, wind(15.0), 17.8, 0.05)
for t0 in (24.1, 26.0, 28.0, 30.0): place(sfx, whoosh(0.9), t0, 0.25 + 0.05*(t0-24))
place(sfx, ping(), 33.3, 0.12); place(sfx, ping(), 49.4, 0.12)                 # REGLA #1 / #2
place(sfx, whoosh(1.6), 46.0, 0.35)
place(amb, wind(7.3), 53.6, 0.1)
place(sfx, creak(1.0), 66.4, 0.5); place(sfx, creak(0.7), 69.4, 0.4); place(sfx, creak(1.2), 70.5, 0.55)
for t0 in (67.6, 69.5, 70.7, 71.0): place(sfx, ping()*0.5, t0, 0.15); place(sfx, whoosh(0.4), t0+0.05, 0.15)
place(sfx, thump(1.0, 40), 72.85, 0.7)
for t0 in (3.25, 6.99, 9.31, 13.11, 17.81, 22.93, 32.75, 41.55, 44.67, 48.69, 53.65, 60.93, 65.43, 67.41): place(sfx, whoosh(), t0-0.2, 0.1)
# ---- voz
y, _ = librosa.load("/home/claude/m1/m1a.mp3", sr=SR)
voice = np.zeros(N); i = int(0.15*SR); voice[i:i+len(y)] = y[:N-i]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_m1a.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
