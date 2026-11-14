"""M1C · banda sonora sintetizada + efectos + voz → mix_m1a.wav"""
import numpy as np, soundfile as sf, librosa, math, sys
sys.path.insert(0, "/home/claude/t3d")
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; TOT = 74.1
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
# ---- música: dron + pulso 90 bpm; final: acorde mayor al aterrizar, oscuro en la revelación
beat = 60/90
for b_ in range(int(71.6/beat)):
    t0 = b_*beat
    n_ = [38, 38, 41, 37][(b_//8) % 4] if not (48.5 < t0 < 55.2) else [43, 43, 47, 45][(b_//8) % 4]
    x = lp(tone(NOTE(n_), beat*0.8, "saw", 0.006), 420)*env(0.01, 0.25, 0.4, 0.2, beat*0.8)
    place(music, x, t0, 0.07 if t0 < 39 else 0.09)
    if b_ % 2 == 0 and (t0 < 12.4 or 39.3 < t0 < 48.5 or t0 > 61.9): place(music, thump(0.3, 50)[:int(0.4*SR)], t0)
    if b_ % 4 == 3 and t0 > 18: place(music, hp(rng.normal(0, 1, int(0.04*SR)), 6000)*np.linspace(1, 0, int(0.04*SR)), t0, 0.06)
for t0, dur, ch in ((0, 12.4, (50, 53, 57)), (12.4, 11.2, (46, 50, 53)), (23.6, 15.7, (49, 53, 56)), (39.3, 9.2, (50, 53, 57)),
                    (48.5, 6.7, (55, 59, 62)), (55.2, 6.7, (46, 49, 53)), (61.9, 10.0, (45, 49, 52))):
    for n_ in ch:
        x = lp(tone(NOTE(n_), dur, "saw", 0.005), 850)*env(1.0, 1.0, 0.8, 1.2, dur)
        place(music, x, t0, 0.028)
for t0, dur in ((4.8, 2.0), (19.0, 4.6), (39.3, 4.0), (55.3, 6.6), (61.9, 8.0)):
    tt = np.arange(int(dur*SR))/SR; f = 300*2**(tt/dur*1.0)
    x = np.sin(2*np.pi*np.cumsum(f)/SR)*env(0.4, 0.3, 0.8, 0.6, dur)
    place(music, x, t0, 0.035)
music[int(71.6*SR):] *= np.linspace(1, 0, N-int(71.6*SR))
# ---- efectos
place(sfx, thump(1.0, 45), 0.05, 0.6); place(amb, wind(73.5), 0.0, 0.05)
place(sfx, creak(0.8), 1.2, 0.35); place(sfx, creak(0.7), 5.0, 0.35)
place(sfx, whoosh(1.0), 7.2, 0.4); place(sfx, thump(0.8, 70), 8.8, 0.5)             # salto a la farola siguiente
for t0 in (10.0, 10.75, 11.5): place(sfx, thump(0.5, 90)[:int(0.25*SR)], t0, 0.35); place(sfx, ping()*0.3, t0, 0.08)
place(amb, wind(6.4), 12.4, 0.14); place(sfx, whoosh(2.0), 12.6, 0.3)
for t0 in (20.4, 20.9, 21.5, 22.0, 22.6, 23.1): place(sfx, crunch()*0.5, t0, 0.25)  # coches que tiemblan
place(sfx, thump(0.6, 80), 24.2, 0.4)
place(amb, wind(1.9), 27.4, 0.16)
place(sfx, ping(), 29.4, 0.12)                                                    # REGLA #5
place(sfx, whoosh(0.5), 35.4, 0.3); place(sfx, thump(0.9, 60), 35.9, 0.55); place(sfx, crunch()*0.5, 36.4, 0.3)
for t0 in (39.6, 41.2): place(sfx, whoosh(0.8), t0, 0.35); place(sfx, creak(0.6), t0+0.2, 0.3)
place(sfx, whoosh(1.2), 42.6, 0.45); place(sfx, whoosh(0.9), 43.9, 0.4)
place(sfx, thump(1.2, 40), 45.45, 0.8); place(sfx, crunch(), 45.5, 0.5)
for t0 in (45.9, 46.4, 46.9): place(sfx, crunch()*0.6, t0, 0.3)
place(sfx, bell()*0.5, 48.6, 0.2)
place(sfx, whoosh(1.4), 51.1, 0.3); place(amb, wind(20.0), 51.2, 0.1)
place(sfx, thump(1.0, 38), 55.3, 0.6); place(sfx, roar(2.5), 58.2, 0.12)
place(sfx, thump(1.2, 35), 61.95, 0.75)
place(sfx, thump(1.0, 40), 71.9, 0.7)
for t0 in (4.8, 6.6, 9.6, 12.4, 18.8, 23.6, 27.4, 29.3, 34.2, 39.3, 43.2, 45.2, 48.55, 51.05, 55.25, 58.0, 61.9, 67.0): place(sfx, whoosh(), t0-0.2, 0.1)
# ---- voz
y, _ = librosa.load("/home/claude/m1c/raw.wav", sr=SR)
voice = np.zeros(N); i = int(0.15*SR); voice[i:i+len(y)] = y[:N-i]
vabs = np.abs(voice); ven = np.convolve(vabs, np.ones(int(0.15*SR))/int(0.15*SR), 'same')
duck = 1-0.6*np.clip(ven/0.05, 0, 1)
mix = music*duck + sfx*(1-0.35*np.clip(ven/0.05, 0, 1)) + amb*duck + voice
mix = np.tanh(mix*1.2)/1.2
mix = mix/np.max(np.abs(mix))*0.93
st = np.stack([mix, mix], 1)
sf.write("/home/claude/t3d/mix_m1c.wav", st.astype(np.float32), SR)
print("MIX OK", round(len(st)/SR, 2))
