"""Render 3D de un capítulo: python3 render3d.py VID modulo [--stills]
Lee build/VID/timeline.json, construye el mundo (modulo.build) y posa cada fotograma (modulo.SCENES3D[VID]).
Salida: build/VID/3d/f00000.png… a FPS3D (15). --stills: un fotograma por escena (al 35 % y 75 %) → /tmp/qa3d_VID.jpg"""
import os, sys, json, math, importlib, subprocess, time
os.environ.setdefault("MESA_GL_VERSION_OVERRIDE", "4.6"); os.environ.setdefault("MESA_GLSL_VERSION_OVERRIDE", "460"); os.environ.setdefault("EGL_PLATFORM", "surfaceless")
sys.path.insert(0, "/home/claude/anim")
import m3d
FPS3D = 15
vid, modname = sys.argv[1], sys.argv[2]; stills = "--stills" in sys.argv
mod = importlib.import_module(modname)
B = f"/home/claude/anim/build/{vid}"
W = mod.build(); fns = mod.SCENES3D[vid]
if stills:
    out = f"/tmp/st3d_{vid}"; os.makedirs(out, exist_ok=True)
    tl = json.load(open(f"{B}/timeline.json")) if os.path.exists(f"{B}/timeline.json") else None
    for i, f in enumerate(fns):
        d = (tl["scenes"][i]["end"]-tl["scenes"][i]["start"]) if tl else 5.0
        t0 = tl["scenes"][i]["start"] if tl else i*5
        for j, fr in enumerate((0.35, 0.75)):
            f(W, fr*d, d, t0+fr*d); m3d.render_to(f"{out}/{i:02d}_{j}.png")
    subprocess.run(f"ffmpeg -loglevel error -y -pattern_type glob -i '{out}/*_1.png' -vf scale=216:384,tile=6x2 /tmp/qa3d_{vid}.jpg", shell=True)
    print("OK", f"/tmp/qa3d_{vid}.jpg"); sys.exit()
tl = json.load(open(f"{B}/timeline.json")); os.makedirs(f"{B}/3d", exist_ok=True)
n = int(math.ceil(tl["total"]*FPS3D)); si = 0; t0 = time.time()
part = [int(x) for x in os.environ.get("PART", "0/1").split("/")]
for f in range(n):
    if f % part[1] != part[0]: continue
    p = f"{B}/3d/f{f:05d}.png"
    if os.path.exists(p): continue
    t = f/FPS3D
    si = max(i for i, sc in enumerate(tl["scenes"]) if sc["start"] <= t or i == 0)
    sc = tl["scenes"][si]; lt = t-sc["start"]; d = sc["end"]-sc["start"]
    fns[si](W, lt, d, t); m3d.render_to(p)
    if f % 60 == 0: print("3D", vid, f, "/", n, round(time.time()-t0), "s", flush=True)
print("3D DONE", vid, n, round(time.time()-t0), "s", flush=True)
