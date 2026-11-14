"""python3 render.py stills  → un fotograma por plano (QA)
   python3 render.py frames A/N → fotogramas f%05d.png (reparto A de N) + meta.json"""
import os, sys, json, time, math
os.environ.setdefault("EGL_PLATFORM", "surfaceless")
sys.path.insert(0, "/home/claude/t3d")
import importlib
shots = importlib.import_module(os.environ.get("SHOTS", "shots"))   # SHOTS=shots_<vid>
globals().update({k: v for k, v in vars(shots).items() if not k.startswith("__")})

OUT = os.environ.get("FR", "/home/claude/t3d/fr"); os.makedirs(OUT, exist_ok=True)
LOOK = os.environ.get("LOOK", "cine")          # cine: color + profundidad + cámara para lux.py · classic: como antes
HANDHELD = float(os.environ.get("HANDHELD", "1"))

def _n(T, a, b, c):
    return 0.55*math.sin(T*a)+0.3*math.sin(T*b+1.7)+0.15*math.sin(T*c+4.1)

def handheld(T):
    """micro-movimiento orgánico de cámara (steadicam): suave, continuo y proporcional a la focal"""
    import vox
    if HANDHELD <= 0 or vox.CAM is None: return
    import bpy
    C = vox.CAM; tg = bpy.data.objects[C["tgt"]]
    last = C.get("hh")      # si el plano no volvió a colocar la cámara, quita el desplazamiento anterior (no se acumula)
    if last and abs(C.location.x-last[4]) < 1e-6 and abs(C.location.z-last[5]) < 1e-6:
        C.location.x -= last[0]; C.location.z -= last[1]; tg.location.x -= last[2]; tg.location.z -= last[3]
    k = HANDHELD*min(1.0, 28.0/max(C.data.lens, 10.0))
    o = (0.010*k*_n(T, 0.83, 1.71, 2.9), 0.008*k*_n(T, 0.67, 1.93, 3.3), 0.014*k*_n(T, 0.51, 1.37, 2.3), 0.011*k*_n(T, 0.73, 1.21, 2.7))
    C.location.x += o[0]; C.location.z += o[1]; tg.location.x += o[2]; tg.location.z += o[3]
    C["hh"] = [*o, C.location.x, C.location.z]

def cam_meta(M):
    import bpy, vox
    from mathutils import Vector
    bpy.context.view_layer.update()
    sc = bpy.context.scene; C = vox.CAM
    M["cam"] = [[round(v, 5) for v in r] for r in C.matrix_world]
    M["lens"] = C.data.lens; M["dof"] = bool(C.data.dof.use_dof)
    tg = bpy.data.objects[C["tgt"]]; M["fd"] = round((C.matrix_world.translation-tg.matrix_world.translation).length, 3)
    M["ld"] = [round(v, 4) for v in sc.display.light_direction]
    wc = tuple(sc.world.color)
    M["wc"] = [round(v, 4) for v in wc]
    M["wc_s"] = [round(((1.055*v**(1/2.4)-0.055) if v > 0.0031308 else v*12.92), 4) for v in wc]

def zpath(p):
    d, b = os.path.split(p); return os.path.join(d, "z"+b[1:-4]+".npz")

def render_cine(p):
    """un solo render a EXR multicapa → PNG sRGB (idéntico al de siempre) + profundidad a media resolución"""
    import bpy, OpenEXR, numpy as np, cv2
    sc = bpy.context.scene; vl = sc.view_layers[0]; vl.use_pass_z = True
    im = sc.render.image_settings
    if im.file_format != 'OPEN_EXR_MULTILAYER':
        im.media_type = 'MULTI_LAYER_IMAGE'; im.file_format = 'OPEN_EXR_MULTILAYER'; im.color_depth = '16'; im.exr_codec = 'ZIP'
    tmp = p[:-4]+".exr"; sc.render.filepath = tmp; bpy.ops.render.render(write_still=True)
    ch = {}
    for part in OpenEXR.File(tmp).parts: ch.update({k: v.pixels for k, v in part.channels.items()})
    c = ch['ViewLayer.Combined'][..., :3].astype(np.float32); z = ch['ViewLayer.Depth.Z'].astype(np.float32)
    s = np.where(c <= 0.0031308, c*12.92, 1.055*np.power(np.clip(c, 0, None), 1/2.4)-0.055)
    zs = cv2.resize(np.minimum(z, 1e6), (z.shape[1]//2, z.shape[0]//2), interpolation=cv2.INTER_AREA).astype(np.float16)
    np.savez_compressed(zpath(p), z=zs)
    cv2.imwrite(p, (np.clip(s, 0, 1)[..., ::-1]*255+0.5).astype(np.uint8))
    os.remove(tmp)
W = shots.build(); W["env"] = shots.Env()
mode = sys.argv[1]
if mode == "stills":
    os.makedirs("/tmp/st3", exist_ok=True)
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    for t0, t1, f in shots.SH:
        if only and f.__name__ not in only: continue
        for j, fr in enumerate((0.3, 0.8)):
            T = t0+(t1-t0)*fr
            M = frame(W, T)
            if M.get("black"): continue
            render_to(f"/tmp/st3/{f.__name__}_{j}.png")
    print("STILLS OK")
elif mode == "preview":
    import bpy
    bpy.context.scene.render.resolution_percentage = 50
    os.makedirs("/home/claude/t3d/pv", exist_ok=True)
    step = int(sys.argv[2]); a, n = [int(x) for x in sys.argv[3].split("/")]
    N = int(math.ceil(shots.TOTAL*shots.FPS)); meta = {}
    for i in range(0, N, step):
        if (i//step) % n != a: continue
        M = frame(W, i/shots.FPS); meta[str(i)] = M
        if not M.get("black") and not os.path.exists(f"/home/claude/t3d/pv/f{i:05d}.png"): render_to(f"/home/claude/t3d/pv/f{i:05d}.png")
    json.dump(meta, open(f"/home/claude/t3d/pv/meta_{a}.json", "w")); print("PV DONE", flush=True)
elif mode == "one":
    T = float(sys.argv[2]); M = frame(W, T); render_to(f"/tmp/one_{T:.2f}.png"); print(M)
elif mode == "probe":
    # fotogramas sueltos con todo lo de cine (para comparar): python3 render.py probe 5.0,14.2,…
    meta = {}
    for T in [float(x) for x in sys.argv[2].split(",")]:
        i = int(round(T*shots.FPS)); M = frame(W, T); meta[str(i)] = M
        if M.get("black"): continue
        for d in (-1, 0):          # el anterior también, para el desenfoque de movimiento
            if d: Mp = frame(W, (i-1)/shots.FPS); handheld((i-1)/shots.FPS); cam_meta(Mp); meta[str(i-1)] = Mp; render_cine(f"{OUT}/f{i-1:05d}.png"); continue
        M = frame(W, T); handheld(T); cam_meta(M); meta[str(i)] = M; render_cine(f"{OUT}/f{i:05d}.png")
    json.dump(meta, open(f"{OUT}/meta_0.json", "w")); print("PROBE OK", flush=True)
else:
    a, n = [int(x) for x in sys.argv[2].split("/")]
    N = int(math.ceil(shots.TOTAL*shots.FPS)); meta = {}
    t0 = time.time()
    mp = f"{OUT}/meta_{a}.json"
    if os.path.exists(mp): meta = json.load(open(mp))
    rg = os.environ.get("RANGO")      # «ini:fin» en segundos: solo ese tramo (previsualizar escenas)
    i0, i1 = (int(float(x)*shots.FPS) for x in rg.split(":")) if rg else (0, N)
    for i in range(N):
        if i % n != a or not (i0 <= i < i1): continue
        p = f"{OUT}/f{i:05d}.png"
        T = i/shots.FPS
        M = frame(W, T); meta[str(i)] = M
        if M.get("black"):
            continue
        if LOOK == "cine":
            handheld(T); cam_meta(M)
            if not os.path.exists(p) or not os.path.exists(zpath(p)): render_cine(p)
        elif not os.path.exists(p): render_to(p)
        if i % 48 == a: print("F", i, "/", N, round(time.time()-t0), flush=True); json.dump(meta, open(mp, "w"))
    json.dump(meta, open(mp, "w")); print("DONE", a, flush=True)
