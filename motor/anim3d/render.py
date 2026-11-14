"""python3 render.py stills  → un fotograma por plano (QA)
   python3 render.py frames A/N → fotogramas f%05d.png (reparto A de N) + meta.json"""
import os, sys, json, time, math
os.environ.setdefault("EGL_PLATFORM", "surfaceless")
sys.path.insert(0, "/home/claude/t3d")
import importlib
shots = importlib.import_module(os.environ.get("SHOTS", "shots"))   # SHOTS=shots_<vid>
globals().update({k: v for k, v in vars(shots).items() if not k.startswith("__")})

OUT = os.environ.get("FR", "/home/claude/t3d/fr"); os.makedirs(OUT, exist_ok=True)
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
else:
    a, n = [int(x) for x in sys.argv[2].split("/")]
    N = int(math.ceil(shots.TOTAL*shots.FPS)); meta = {}
    t0 = time.time()
    mp = f"{OUT}/meta_{a}.json"
    if os.path.exists(mp): meta = json.load(open(mp))
    for i in range(N):
        if i % n != a: continue
        p = f"{OUT}/f{i:05d}.png"
        T = i/shots.FPS
        M = frame(W, T); meta[str(i)] = M
        if M.get("black"):
            continue
        if not os.path.exists(p): render_to(p)
        if i % 48 == a: print("F", i, "/", N, round(time.time()-t0), flush=True); json.dump(meta, open(mp, "w"))
    json.dump(meta, open(mp, "w")); print("DONE", a, flush=True)
