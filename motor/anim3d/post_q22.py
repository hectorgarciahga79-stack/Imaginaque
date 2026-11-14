"""Postproducción por fotograma: etalonaje por escena, noche con bloom, efecto de congelación (tinte + onda
de distorsión), cristal del escaparate, viñeta, grano. Uso: python3 post.py A/N"""
import os, sys, json, glob, math
import numpy as np, cv2

FR = os.environ.get("FR", "/home/claude/t3d/fr"); OUT = os.environ.get("PP", "/home/claude/t3d/pp"); os.makedirs(OUT, exist_ok=True)
TOTAL = float(os.environ.get("TOTAL", "59.4"))
FPS = 24
meta = {}
for f in glob.glob(f"{FR}/meta_*.json"): meta.update(json.load(open(f)))
H, W = 1280, 720
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt(((xx-W/2)/W)**2+((yy-H*0.45)/H)**2)
VIG = np.clip(1-0.55*rr**2*2.2, 0, 1)[..., None]

GR = {  # (multiplicador RGB, saturación, contraste, lift)
    "rain": ((0.92, 0.98, 1.06), 0.82, 1.05, 0.02),
    "day": ((1.06, 1.0, 0.93), 1.08, 1.06, 0.0),
    "day_sad": ((0.95, 0.98, 1.04), 0.7, 1.02, 0.02),
    "cafe": ((1.08, 1.0, 0.88), 1.05, 1.05, 0.01),
    "field": ((1.02, 1.04, 0.96), 1.12, 1.06, 0.0),
    "office": ((0.97, 1.0, 1.04), 0.92, 1.04, 0.01),
    "night": ((0.90, 0.94, 1.12), 0.85, 1.10, 0.0),
    "alarm": ((1.08, 0.96, 0.92), 1.02, 1.08, 0.0),
    "lab": ((0.98, 1.0, 1.04), 0.95, 1.04, 0.01),
    "deep": ((0.72, 0.95, 1.12), 0.85, 1.05, 0.0),
    "abyss": ((0.62, 0.88, 1.10), 0.8, 1.10, -0.02),
    "cold": ((0.80, 0.98, 1.14), 0.75, 1.05, 0.01),
    "sonar": ((0.85, 1.05, 0.95), 0.95, 1.10, 0.0),
    "dawn": ((1.10, 0.98, 0.88), 1.1, 1.06, 0.0),
}
GRAD = (1.0-0.55*np.clip((yy/H), 0, 1))[..., None]

def sat(img, k):
    g = img.mean(2, keepdims=True); return g+(img-g)*k

def bloom(img, mask_img, strength=0.8, ksize=61):
    b = cv2.GaussianBlur(mask_img, (0, 0), ksize/3)
    b2 = cv2.GaussianBlur(mask_img, (0, 0), ksize)
    return img + strength*(0.6*b+0.4*b2)

def ripple(img, p, cx=W/2, cy=H*0.48, amp=10.0, col=(0.6, 0.95, 1.0)):
    R = p*1.25*math.hypot(W, H)*0.6
    d = np.sqrt((xx-cx)**2+(yy-cy)**2)+1e-3
    w = np.exp(-((d-R)/38.0)**2)*(1-p)
    off = amp*w*np.sin((d-R)/9.0)
    mx = (xx+off*(xx-cx)/d).astype(np.float32); my = (yy+off*(yy-cy)/d).astype(np.float32)
    out = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    out += (w*0.35)[..., None]*np.array(col, np.float32)[None, None, :]
    return out

def process(i):
    m = meta.get(str(i), {})
    p = f"{FR}/f{i:05d}.png"
    if m.get("black") or not os.path.exists(p):
        return np.zeros((H, W, 3), np.float32)
    raw = cv2.imread(p, cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float32)/255
    img = raw.copy()
    g = GR.get(m.get("grade", "day"), GR["day"])
    if m.get("grade") == "night":
        # luces: píxeles amarillos/claros del render (farolas, ventanas, charcos, faros)
        lum = raw.mean(2)
        warm = np.clip((raw[..., 0]+raw[..., 1])/2 - raw[..., 2]*0.75, 0, 1)
        lm = np.clip((lum-0.62)*3.0, 0, 1)*np.clip(warm*4, 0, 1)
        violet = np.clip(raw[..., 2]-raw[..., 1]*0.9, 0, 1)*np.clip((raw[..., 0]-0.5)*4, 0, 1)
        img = img*np.array(g[0], np.float32)[None, None, :]
        img = sat(img, g[1]); img = (img-0.5)*g[2]+0.5-0.02
        light = np.stack([lm*1.0, lm*0.78, lm*0.45], 2) + np.stack([violet*0.7, violet*0.35, violet*1.0], 2)
        img = img*(1-0.65*lm[..., None]) + raw*0.65*lm[..., None]
        img = bloom(img, light.astype(np.float32), 1.3, 45)
    else:
        img = img*np.array(g[0], np.float32)[None, None, :]
        img = sat(img, g[1]); img = (img-0.5)*g[2]+0.5+g[3]
    if m.get("grade") in ("deep", "abyss", "cold"):
        # agua: oscurece hacia abajo, velo azul y rayos de luz suaves desde arriba
        d = m.get("dark", 0.0)
        rays = (np.sin(xx*0.018 + yy*0.006 + i*0.03)*0.5+0.5)**6*np.clip(1-yy/(H*0.7), 0, 1)*0.10*(1-d)
        img = img*(GRAD*(1-0.6*d)+0.15) + np.array((0.02, 0.10, 0.16), np.float32)*(1-d) + rays[..., None]*np.array((0.6, 0.9, 1.0), np.float32)
        if m.get("dark"):
            eye = np.clip((raw[..., 0]+raw[..., 1])/2-raw[..., 2]-0.25, 0, 1)*3
            img = bloom(img, np.stack([eye*0.8, eye*1.0, eye*0.3], 2).astype(np.float32), 0.8*d, 25)
    if m.get("glow_mark"):
        cy = np.clip((raw[..., 1]+raw[..., 2])/2-raw[..., 0]*0.8-0.35, 0, 1)*3
        pulse = 0.7+0.3*math.sin(i/FPS*9)
        img = bloom(img, np.stack([cy*0.3, cy*1.0, cy*1.1], 2).astype(np.float32), 0.9*pulse, 35)
    if m.get("glass"):
        q = np.array([[c[0]*W, (1-c[1])*H] for c in m["glass"]], np.int32)
        mk = np.zeros((H, W), np.float32); cv2.fillPoly(mk, [q], 1.0); mk = cv2.GaussianBlur(mk, (0, 0), 2)
        bl = cv2.GaussianBlur(img, (0, 0), 1.2)
        tint = bl*np.array((0.78, 0.9, 1.05), np.float32)+0.06
        streak = (np.sin((xx*0.6+yy)*0.012)*0.5+0.5)**18*0.18
        img = img*(1-mk[..., None]) + (tint+streak[..., None])*mk[..., None]
    if m.get("glass_full"):
        streak = (np.sin((xx*0.6+yy)*0.010)*0.5+0.5)**20*0.12
        img = img*np.array((0.9, 0.96, 1.05), np.float32)+streak[..., None]
    if m.get("freeze"):
        img = sat(img, 0.72)*np.array((0.93, 1.0, 1.08), np.float32)
        # aberración cromática muy suave
        sh = 2
        img[..., 0] = np.roll(img[..., 0], sh, 1); img[..., 2] = np.roll(img[..., 2], -sh, 1)
    if "ripple" in m: img = ripple(img, m["ripple"])
    if "ripple_v" in m: img = ripple(img, m["ripple_v"], amp=16, col=(0.8, 0.5, 1.0))
    if m.get("blur"): img = cv2.GaussianBlur(img, (0, 0), 0.5+4.0*m["blur"])
    if m.get("scope"):
        d = np.sqrt((xx-W/2)**2+(yy-H*0.47)**2); R = W*0.46
        mk = np.clip((R-d)/6.0, 0, 1)[..., None]
        ring = (np.exp(-((d-R)/5.0)**2)*0.5)[..., None]
        img = img*mk + ring*np.array((0.3, 0.3, 0.32), np.float32)
    img = img*(VIG*0.6+0.4) if m.get("grade") == "night" else img*(VIG*0.5+0.5)
    rng = np.random.default_rng(i); img += rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)
    if m.get("alarm"):
        img = img*(1+0.10*max(0, math.sin(i/FPS*7.0)))*np.array((1.0, 0.94, 0.92), np.float32)
    if m.get("flash"): img = img*0.5+0.5
    if m.get("fade"): img *= (1-m["fade"])
    return np.clip(img, 0, 1)

if __name__ == "__main__":
    a, n = [int(x) for x in sys.argv[1].split("/")]
    N = int(math.ceil(TOTAL*FPS))
    for i in range(N):
        if i % n != a: continue
        o = f"{OUT}/p{i:05d}.png"
        if os.path.exists(o) and "--force" not in sys.argv: continue
        if not os.path.exists(f"{FR}/f{i:05d}.png") and not meta.get(str(i), {}).get("black"): continue
        img = process(i)
        cv2.imwrite(o, (img[:, :, ::-1]*255).astype(np.uint8))
    print("POST DONE", a)
