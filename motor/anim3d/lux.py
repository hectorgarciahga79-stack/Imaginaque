"""lux — iluminación cinematográfica y efectos de cámara en post para el motor 3D de bloques (ImaginaQue).

Entrada por fotograma (de render.py con LOOK=cine): FR/f%05d.png (color Workbench), FR/z%05d.npz (profundidad a
media resolución) y meta_*.json (cámara, luz y ambiente de cada fotograma).
Salida: FRC/f%05d.png con la misma convención, para que los post_*.py de siempre (etalonaje, viñeta, grano,
efectos especiales) se apliquen después sin cambios.

Qué añade (en espacio lineal):
  · reiluminación: luz principal con temperatura de color por ambiente, coherente con la dirección de las sombras
    (light_dir del plano), relleno hemisférico cielo/suelo y luz de contorno que separa al sujeto del fondo
  · oclusión ambiental por profundidad · perspectiva atmosférica (niebla por distancia del color del cielo)
  · rayos volumétricos cuando el sol está en plano · bloom de altas luces
  · motas de polvo / polen / brasas ancladas en el espacio 3D (paralaje real, ocultas por la escena)
  · profundidad de campo suave (si el plano no usa ya la DOF de Blender) · desenfoque de movimiento de cámara
    por reproyección · transición de entrada en cada cambio de plano
Uso:  FR=… FRC=… python3 lux.py A/N        (LUX=0 copia sin tocar)"""
import os, sys, json, glob, math, shutil, hashlib
import numpy as np, cv2

FR = os.environ.get("FR", "/home/claude/t3d/fr"); OUT = os.environ.get("FRC", FR + "_c"); os.makedirs(OUT, exist_ok=True)
H, W = 1280, 720
h2, w2 = 640, 360
cv2.setNumThreads(2)

meta = {}
for f in glob.glob(f"{FR}/meta_*.json"): meta.update(json.load(open(f)))
for f in glob.glob(f"{FR}/meta_*.json"): shutil.copy(f, OUT)

# ------------------------------------------------------------------ ambientes
def K(t):
    """temperatura de color (K) → RGB lineal normalizado (aprox. Tanner Helland)"""
    t = t/100.0
    r = 255 if t <= 66 else 329.7*((t-60)**-0.1332)
    g = 99.47*math.log(t)-161.12 if t <= 66 else 288.12*((t-60)**-0.0755)
    b = 255 if t >= 66 else (0 if t <= 19 else 138.52*math.log(t-10)-305.04)
    c = np.clip(np.array([r, g, b])/255.0, 0, 1)
    c = c**1.3; return c/c.max()        # saturación moderada: tinte de luz, no filtro de color

def mood(key_k, key, fill_k, fill, rim_k, rim, fog, fog_start, fog_max, dust, rays=False, bloom=0.22, ao=0.35, dof=1.0, ember=False, expo=1.35):
    return dict(key_c=K(key_k), key=key, fill_c=K(fill_k), fill=fill, rim_c=K(rim_k), rim=rim, fog=fog, fog_start=fog_start,
                fog_max=fog_max, dust=dust, rays=rays, bloom=bloom, ao=ao, dof=dof, ember=ember, expo=expo)

LOOKS = {  # key K, key, fill K, fill, rim K, rim, niebla, inicio, máx, polvo
    "day":     mood(5800, 0.75, 9000, 0.50, 6500, 0.30, 0.010, 10.0, 0.28, 40, rays=True, bloom=0.18),
    "field":   mood(5400, 0.80, 9500, 0.45, 5200, 0.35, 0.009, 12.0, 0.28, 70, rays=True, bloom=0.20),
    "dawn":    mood(3300, 0.80, 8500, 0.40, 2900, 0.55, 0.030, 4.0, 0.55, 60, rays=True, bloom=0.30),
    "cafe":    mood(3200, 0.70, 6500, 0.45, 4200, 0.30, 0.012, 4.0, 0.25, 45, bloom=0.26),
    "room":    mood(3600, 0.65, 7000, 0.50, 4500, 0.30, 0.010, 4.0, 0.22, 40, bloom=0.24),
    "office":  mood(4800, 0.60, 7500, 0.55, 6000, 0.30, 0.012, 5.0, 0.25, 30, bloom=0.18),
    "lab":     mood(6800, 0.60, 9000, 0.55, 8000, 0.40, 0.012, 5.0, 0.25, 25, bloom=0.22),
    "day_sad": mood(6500, 0.50, 8000, 0.60, 7000, 0.20, 0.025, 4.0, 0.45, 25, bloom=0.12),
    "cold":    mood(8500, 0.55, 11000, 0.60, 9000, 0.35, 0.035, 3.0, 0.60, 0, bloom=0.20),
    "rain":    mood(7500, 0.45, 9500, 0.65, 8000, 0.30, 0.040, 3.0, 0.60, 0, bloom=0.22),
    "night":   mood(9000, 0.55, 12000, 0.55, 3600, 0.65, 0.022, 4.0, 0.40, 25, bloom=0.38, ember=True, expo=1.75),
    "alarm":   mood(3000, 0.70, 8500, 0.45, 2600, 0.55, 0.018, 4.0, 0.35, 20, bloom=0.40, expo=1.4),
    "deep":    mood(9500, 0.45, 12000, 0.55, 9000, 0.40, 0.060, 2.0, 0.75, 80, bloom=0.30),
    "abyss":   mood(10000, 0.40, 12000, 0.50, 9000, 0.35, 0.080, 1.5, 0.85, 90, bloom=0.35),
    "sonar":   mood(9000, 0.45, 11000, 0.55, 9000, 0.40, 0.040, 2.0, 0.60, 40, bloom=0.30),
}
DEFAULT = "day"

# ------------------------------------------------------------------ utilidades
def lin(s): return np.where(s <= 0.04045, s/12.92, ((s+0.055)/1.055)**2.4).astype(np.float32)
def srgb(l):
    l = np.clip(l, 0, None)
    return np.where(l <= 0.0031308, l*12.92, 1.055*np.power(l, 1/2.4)-0.055).astype(np.float32)
def lum(c): return c[..., 0]*0.2126+c[..., 1]*0.7152+c[..., 2]*0.0722
def nrm(v): return v/np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-6)
def up(a): return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)
SKY = 300.0

def cam_of(m):
    M4 = np.array(m["cam"], np.float32); R = M4[:3, :3]; t = M4[:3, 3]
    f = m["lens"]*H/24.0          # sensor vertical de 24 mm (vox.camera)
    return R, t, f

yy2, xx2 = np.mgrid[0:h2, 0:w2].astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def view_pos(z, f):
    """profundidad (media res.) → posición en espacio de cámara (−Z hacia delante)"""
    fh = f*0.5
    x = (xx2+0.5-w2/2)/fh*z; y = -(yy2+0.5-h2/2)/fh*z
    return np.stack([x, y, -z], -1)

def normals(P):
    dxf = np.roll(P, -1, 1)-P; dxb = P-np.roll(P, 1, 1)
    dyf = np.roll(P, -1, 0)-P; dyb = P-np.roll(P, 1, 0)
    dx = np.where((np.abs(dxf[..., 2]) < np.abs(dxb[..., 2]))[..., None], dxf, dxb)
    dy = np.where((np.abs(dyf[..., 2]) < np.abs(dyb[..., 2]))[..., None], dyf, dyb)
    n = nrm(np.cross(dy, dx))
    flip = (np.sum(n*P, -1) > 0)[..., None]
    return np.where(flip, -n, n)

def shot_index():
    """primer fotograma de cada plano (para la transición y para anclar el polvo)"""
    first = {}; order = []
    for k in sorted(meta, key=int):
        s = meta[k].get("shot")
        if s and s not in first: first[s] = int(k); order.append(s)
    return first, order
FIRST, ORDER = shot_index()

def scene_cuts():
    """cortes donde cambia el ambiente (grade): ahí va el destello de luz (light leak) que cruza el corte"""
    cuts = []; prev = None
    for k in sorted(meta, key=int):
        g = meta[k].get("grade"); sh = meta[k].get("shot")
        if prev and sh != prev[1] and g != prev[0] and not meta[k].get("black"): cuts.append(int(k))
        prev = (g, sh)
    return cuts
CUTS = scene_cuts()

# ------------------------------------------------------------------ efectos
def relight(c, z, P, N, R, m, L):
    near = (z < SKY).astype(np.float32)
    ld = np.array(m.get("ld", (0.45, -0.55, 0.7)), np.float32); ld = ld/np.linalg.norm(ld)
    Lv = R.T @ ld                                    # luz en espacio de cámara
    ndl = np.sum(N*Lv, -1)
    key = np.clip((ndl+0.15)/1.15, 0, 1)**1.25
    Nw = N @ R.T                                     # normal en mundo
    hemi = 0.5+0.5*Nw[..., 2]
    sky = np.array(m.get("wc", (0.5, 0.6, 0.7)), np.float32); sky = sky/max(sky.max(), 1e-3)
    fillc = 0.7*L["fill_c"]+0.3*sky
    ground = np.array((0.45, 0.40, 0.36), np.float32)
    V = nrm(-P)
    fres = np.clip(1-np.sum(N*V, -1), 0, 1)**3.5
    back = np.clip(0.35-0.65*Lv[2], 0.2, 1.0)        # el contorno manda más si la luz viene de detrás
    light = (L["key"]*key[..., None]*L["key_c"] + L["fill"]*(hemi[..., None]*fillc+(1-hemi[..., None])*ground*0.6)
             + L["rim"]*back*fres[..., None]*L["rim_c"]*(z < 25)[..., None])
    norm = L["key"]*0.62+L["fill"]*0.7
    gain = np.clip(light/norm, 0.22, 2.6)
    s = 0.95*m.get("shi_k", 1.0)
    gain = 1+(gain-1)*s
    gain = gain*near[..., None]+(1-near[..., None])
    return c*up(gain)

def edge_light(c, z, R, m, L):
    """luz de contorno: filo luminoso en el borde de lo cercano que mira hacia la luz (separa sujeto y fondo)"""
    if L["rim"] <= 0: return c
    ld = np.array(m.get("ld", (0.45, -0.55, 0.7)), np.float32); ld = ld/np.linalg.norm(ld)
    Lv = R.T @ ld; d = np.array([Lv[0], -Lv[1]], np.float32)
    n = np.linalg.norm(d)
    d = d/n if n > 1e-3 else np.array([0, -1], np.float32)
    acc = np.zeros_like(z)
    for px in (2, 4):
        A = np.float32([[1, 0, -d[0]*px], [0, 1, -d[1]*px]])
        zs = cv2.warpAffine(z, A, (w2, h2), borderMode=cv2.BORDER_REPLICATE)
        acc = np.maximum(acc, np.clip((zs-z)/np.maximum(z, 0.1)-0.15, 0, 1))
    acc *= (z < 30)
    e = up(cv2.GaussianBlur(acc, (0, 0), 0.8))
    k = L["rim"]*(1.4 if m.get("grade") in ("night", "alarm", "dawn", "deep", "abyss") else 0.9)
    return c+(k*0.55*e)[..., None]*L["rim_c"]*(0.35+lum(c)[..., None])

STARS = None
def sky(c, z, R, f, m, L, T):
    """cielo con degradado, halo del sol, nubes en movimiento y estrellas de noche (solo donde no hay geometría)"""
    global STARS
    skym = up((z >= SKY).astype(np.float32))
    if skym.max() < 0.5: return c
    q = 4; hq, wq = H//q, W//q
    yq, xq = np.mgrid[0:hq, 0:wq].astype(np.float32)
    fq = f/q
    d = np.stack([(xq+0.5-wq/2)/fq, -(yq+0.5-hq/2)/fq, -np.ones_like(xq)], -1)
    dw = nrm(d) @ R.T
    el = np.clip(dw[..., 2], -0.2, 1)
    base = lin(np.array(m.get("wc_s", (0.6, 0.7, 0.8)), np.float32))
    night = base.max() < 0.05
    zen = base*(0.78 if not night else 0.7); hor = base*0.75+(0.25*base.mean()+0.01)*(1.4 if not night else 0.6)
    g = np.clip(el*2.2, 0, 1)[..., None]**0.7
    col = hor*(1-g)+zen*g
    ld = np.array(m.get("ld", (0.45, -0.55, 0.7)), np.float32); ld = ld/np.linalg.norm(ld)
    sd = np.clip(np.sum(dw*ld, -1), 0, 1)
    if not night:
        col = col+(sd**400*1.8+sd**40*0.12+sd**10*0.05)[..., None]*L["key_c"]*np.array((1.0, 0.92, 0.8), np.float32)
        # nubes: ruido de baja frecuencia proyectado en el cielo, que se desplaza
        ph = int(hashlib.md5(str(m.get("shot", "")).encode()).hexdigest()[:6], 16)
        rg = np.random.default_rng(ph)
        if not hasattr(sky, "nz") or sky.ph != ph:
            n0 = rg.random((64, 64)).astype(np.float32)
            sky.nz = cv2.GaussianBlur(cv2.resize(n0, (256, 256)), (0, 0), 9)
            sky.nz = (sky.nz-sky.nz.min())/(np.ptp(sky.nz)+1e-6); sky.ph = ph
        u = dw[..., 0]/np.maximum(el+0.12, 0.05)*40+T*1.2; v = dw[..., 1]/np.maximum(el+0.12, 0.05)*40
        cl = cv2.remap(sky.nz, (u % 256).astype(np.float32), (v % 256).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        cl = np.clip((cl-0.5)*2.2, 0, 1)*np.clip(el*3, 0, 1)
        col = col*(1-0.45*cl[..., None])+cl[..., None]*np.minimum(base*1.25+0.05, 1.0)*0.45
    else:
        if STARS is None:
            rs = np.random.default_rng(7); STARS = (rs.random((512, 1024)) > 0.9965).astype(np.float32)*rs.uniform(0.3, 1, (512, 1024)).astype(np.float32)
        az = (np.arctan2(dw[..., 1], dw[..., 0])/(2*np.pi)+0.5)*1023; alt = (1-np.clip(el, 0, 1))*511
        st = cv2.remap(STARS, az.astype(np.float32), alt.astype(np.float32), cv2.INTER_NEAREST)
        col = col+st[..., None]*0.05*np.clip(el*4, 0, 1)[..., None]+(sd**30*0.05)[..., None]
    col = up(col)
    return c*(1-skym[..., None])+col*skym[..., None]

def ambient_occlusion(c, z, L):
    zb = cv2.GaussianBlur(z, (0, 0), 5)
    d = np.clip((z-zb)/(0.08*z+0.04), 0, 1)*(z < SKY)
    ao = 1-L["ao"]*cv2.GaussianBlur(d, (0, 0), 1.2)
    return c*up(ao)[..., None]

def fog(c, z, m, L):
    sky = lin(np.array(m.get("wc_s", (0.6, 0.7, 0.8)), np.float32))
    col = (0.6*sky+0.4*sky.mean()*L["key_c"])*1.15
    f = L["fog_max"]*(1-np.exp(-L["fog"]*np.clip(z-L["fog_start"]*1.8, 0, None)))*(z < SKY)
    f = up(f)[..., None]
    return c*(1-f)+col*f

def practicals(c0):
    """máscara de fuentes de luz prácticas a partir del color original (sRGB): saturadas y luminosas"""
    mx = c0.max(-1); mn = c0.min(-1); sat = (mx-mn)/np.maximum(mx, 1e-4)
    m = np.clip((sat-0.45)*3, 0, 1)*np.clip((mx-0.55)*3.5, 0, 1)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

def bloom(c, L, pm=None):
    l = lum(c); b = np.clip(l-0.62, 0, None)[..., None]*c/np.maximum(l[..., None], 1e-4)
    if pm is not None: b = b+pm[..., None]*c*L.get("glow", 1.2)
    s = cv2.resize(b, (W//4, H//4), interpolation=cv2.INTER_AREA)
    acc = cv2.GaussianBlur(s, (0, 0), 3)*0.5+cv2.GaussianBlur(s, (0, 0), 9)*0.35+cv2.GaussianBlur(s, (0, 0), 22)*0.25
    return c+L["bloom"]*up(acc)

def god_rays(c, z, R, f, m, L):
    ld = np.array(m.get("ld", (0.45, -0.55, 0.7)), np.float32); ld = ld/np.linalg.norm(ld)
    Lv = R.T @ ld
    if Lv[2] > -0.15: return c                       # el sol no está delante de la cámara
    sx = W/2+f*Lv[0]/(-Lv[2]); sy = H/2-f*Lv[1]/(-Lv[2])
    if not (-0.6*W < sx < 1.6*W and -0.6*H < sy < 1.2*H): return c
    q = 4
    rr = np.hypot((xx-sx)/(0.42*H), (yy-sy)/(0.42*H))
    mask = (up(z) >= SKY).astype(np.float32)*np.clip(lum(c)-0.35, 0, 1)*np.exp(-rr**2)   # solo cielo cerca del sol
    mk = cv2.resize(mask, (W//q, H//q), interpolation=cv2.INTER_AREA); acc = np.zeros_like(mk)
    cx, cy = sx/q, sy/q
    for i in range(28):
        s = 1-i*0.022
        A = np.float32([[s, 0, cx*(1-s)], [0, s, cy*(1-s)]])
        acc += cv2.warpAffine(mk, A, (mk.shape[1], mk.shape[0]), flags=cv2.INTER_LINEAR)*(0.965**i)
    acc = up(acc/10.0)
    return c+0.25*acc[..., None]*L["key_c"]

def dust(c, z, R, t, f, i, m, L):
    n = L["dust"]
    s = m.get("shot")
    if not n or not s or s not in FIRST: return c
    m0 = meta[str(FIRST[s])]
    if "cam" not in m0: return c
    R0, t0, _ = cam_of(m0)
    seed = int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
    rg = np.random.default_rng(seed)
    pv = np.stack([rg.uniform(-3.2, 3.2, n), rg.uniform(-2.6, 2.6, n), rg.uniform(-9.0, -0.6, n)], 1)
    pw = pv @ R0.T+t0
    T = m.get("T", i/24.0)-meta[str(FIRST[s])].get("T", 0)
    vel = np.stack([rg.normal(0, 0.05, n), rg.normal(0, 0.05, n), rg.normal(-0.03, 0.03, n)], 1)
    if L.get("ember"): vel[:, 2] = np.abs(vel[:, 2])+0.04
    pw = pw+vel*T+0.06*np.stack([np.sin(T*0.7+pv[:, 0]*3), np.cos(T*0.5+pv[:, 1]*2), np.sin(T*0.6+pv[:, 2])], 1)
    pc = (pw-t) @ R
    vis = pc[:, 2] < -0.3
    pc = pc[vis]
    if not len(pc): return c
    u = W/2+f*pc[:, 0]/(-pc[:, 2]); v = H/2-f*pc[:, 1]/(-pc[:, 2]); d = -pc[:, 2]
    ok = (u > 0) & (u < W-1) & (v > 0) & (v < H-1)
    u, v, d = u[ok], v[ok], d[ok]
    zs = z[(v/2).astype(int).clip(0, h2-1), (u/2).astype(int).clip(0, w2-1)]
    ok = d < zs-0.05
    u, v, d = u[ok], v[ok], d[ok]
    small = np.zeros((H, W), np.float32); big = np.zeros((H, W), np.float32)
    fd = m.get("fd", 3.0)
    for x, y, dd in zip(u, v, d):
        a = 0.9*min(1.0, 2.2/dd)
        if abs(dd-fd) > 1.8 or dd < 1.2: big[int(y), int(x)] += a*2.5
        else: small[int(y), int(x)] += a
    acc = cv2.GaussianBlur(small, (0, 0), 1.3)*6+cv2.GaussianBlur(big, (0, 0), 4.5)*9
    col = L["key_c"] if not L.get("ember") else K(2400)*np.array((1.0, 0.85, 0.7), np.float32)
    k = 0.10 if not L.get("ember") else 0.08
    return c+k*acc[..., None]*col

def dof(c, z, m, L):
    if m.get("dof") or L["dof"] <= 0: return c
    F = max(m.get("fd", 3.0), 0.5)
    coc = np.clip(np.abs(z-F)/np.maximum(z, 0.1)*1.4, 0, 1)*L["dof"]
    coc = cv2.GaussianBlur(up(coc), (0, 0), 3)[..., None]
    b1 = cv2.GaussianBlur(c, (0, 0), 1.6); b2 = cv2.GaussianBlur(c, (0, 0), 3.6)
    w1 = np.clip(coc*2, 0, 1); w2 = np.clip(coc*2-1, 0, 1)
    return c*(1-w1)+b1*(w1-w2)+b2*w2

def motion_blur(c, z, P, R, t, f, i, m):
    mp = meta.get(str(i-1))
    if not mp or mp.get("shot") != m.get("shot") or "cam" not in mp or mp.get("black"): return c
    Rp, tp, fp = cam_of(mp)
    Pw = P @ R.T+t
    Pp = (Pw-tp) @ Rp
    zp = np.maximum(-Pp[..., 2], 0.05)
    up_ = w2/2+fp*0.5*Pp[..., 0]/zp; vp_ = h2/2-fp*0.5*Pp[..., 1]/zp
    vx = (xx2+0.5-up_)*2; vy = (yy2+0.5-vp_)*2
    vx = np.clip(vx, -48, 48); vy = np.clip(vy, -48, 48)
    if np.percentile(np.hypot(vx, vy), 90) < 0.8: return c
    vx = up(vx)*0.5; vy = up(vy)*0.5                # obturador de 180°
    acc = np.zeros_like(c); taps = np.linspace(-0.5, 0.5, 7)
    for k in taps:
        acc += cv2.remap(c, (xx-vx*k).astype(np.float32), (yy-vy*k).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc/len(taps)

def transition(c, i, m):
    s = m.get("shot")
    if not s or s not in FIRST or ORDER.index(s) == 0 or os.environ.get("LUX_PROBE"): return c
    j = i-FIRST[s]; n = 6
    if j >= n: return c
    k = (1-j/n)**2
    acc = np.zeros_like(c)
    for q in range(5):
        sc = 1+0.07*k*(1+q*0.35)
        A = np.float32([[sc, 0, W/2*(1-sc)], [0, sc, H*0.45*(1-sc)]])
        acc += cv2.warpAffine(c, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (acc/5)*(1+0.10*k)

def aces(x):
    a, b, c_, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x*(a*x+b))/(x*(c_*x+d)+e), 0, 1)

POOL = None
def light_pool(c):
    """el sujeto (centro-alto del encuadre vertical) recibe algo más de luz que los bordes"""
    global POOL
    if POOL is None:
        r = np.sqrt(((xx-W*0.5)/(W*0.62))**2+((yy-H*0.43)/(H*0.55))**2)
        POOL = (1.08-0.30*np.clip(r, 0, 1.4)**2)[..., None].astype(np.float32)
    return c*POOL

def finish(c, L):
    c = light_pool(c)
    e = c*L.get("expo", 1.35)
    l0 = np.maximum(lum(e), 1e-5)[..., None]
    t = 0.5*aces(e)+0.5*np.clip(e*aces(l0)/l0, 0, 1)     # ACES que conserva el tono (cielos azules, pieles)
    l = lum(t); lb = cv2.GaussianBlur(l, (0, 0), 18)
    t = t*np.clip(1+0.35*(l-lb)/np.maximum(l, 0.02), 0.7, 1.4)[..., None]    # claridad (microcontraste local)
    return t

def light_leak(c, i):
    """destello de luz cálida que se revela antes del corte y se retira después (≈ 0,5 s, solo en cambios de escena)"""
    if not CUTS or os.environ.get("LUX_PROBE"): return c
    k = min(CUTS, key=lambda x: abs(x-i)); d = i-k; n = 6
    if abs(d) >= n: return c
    a = math.cos(d/n*math.pi/2)**2*0.24
    rg = np.random.default_rng(k)
    q = 8; lw, lh = W//q, H//q
    yq, xq = np.mgrid[0:lh, 0:lw].astype(np.float32)
    leak = np.zeros((lh, lw, 3), np.float32)
    hues = [np.array(h, np.float32) for h in ((1.0, 0.55, 0.2), (1.0, 0.3, 0.35), (1.0, 0.8, 0.45))]
    for b in range(3):
        side = rg.choice((-0.15, 1.15)); cx = (side+rg.uniform(-0.1, 0.1))*lw+(d/n)*lw*0.3; cy = rg.uniform(0.1, 0.9)*lh; r = rg.uniform(0.3, 0.55)*lw
        leak += np.exp(-((xq-cx)**2+(yq-cy)**2)/(2*r*r))[..., None]*hues[b]
    leak = up(np.clip(leak, 0, 1.5))*a
    return c+leak*(1-np.clip(c, 0, 1))      # mezcla «trama» (screen): ilumina sin quemar

# ------------------------------------------------------------------ fotograma
def process(i):
    m = meta.get(str(i), {})
    c0 = cv2.imread(f"{FR}/f{i:05d}.png")[:, :, ::-1].astype(np.float32)/255.0
    c = lin(c0)
    zp = f"{FR}/z{i:05d}.npz"
    L = LOOKS.get(m.get("grade", DEFAULT), LOOKS[DEFAULT])
    if "cam" not in m or not os.path.exists(zp):
        return srgb(c)
    z = np.load(zp)["z"].astype(np.float32); z[~np.isfinite(z)] = 1e6; z = np.minimum(z, 1e6)
    R, t, f = cam_of(m)
    P = view_pos(np.minimum(z, SKY), f)
    N = normals(cv2.GaussianBlur(P, (0, 0), 0.7))
    c = sky(c, z, R, f, m, L, m.get("T", i/24.0))
    c = relight(c, z, P, N, R, m, L)
    c = edge_light(c, z, R, m, L)
    c = ambient_occlusion(c, z, L)
    c = fog(c, z, m, L)
    if L["rays"]: c = god_rays(c, z, R, f, m, L)
    c = dust(c, z, R, t, f, i, m, L)
    c = dof(c, z, m, L)
    c = motion_blur(c, z, P, R, t, f, i, m)
    c = bloom(c, L, practicals(c0)*(1.0 if m.get("grade") in ("night", "alarm", "deep", "abyss", "sonar", "lab", "cafe", "room") else 0.4))
    c = transition(c, i, m)
    c = light_leak(c, i)
    return srgb(finish(c, L))

if __name__ == "__main__":
    a, n = [int(x) for x in sys.argv[1].split("/")]
    frames = sorted(int(os.path.basename(p)[1:6]) for p in glob.glob(f"{FR}/f*.png"))
    off = os.environ.get("LUX", "1") == "0"
    for i in frames:
        if i % n != a: continue
        o = f"{OUT}/f{i:05d}.png"
        if os.path.exists(o) and "--force" not in sys.argv: continue
        if off: shutil.copy(f"{FR}/f{i:05d}.png", o); continue
        img = process(i)
        cv2.imwrite(o, (np.clip(img, 0, 1)[:, :, ::-1]*255+0.5).astype(np.uint8))
    print("LUX DONE", a, flush=True)
