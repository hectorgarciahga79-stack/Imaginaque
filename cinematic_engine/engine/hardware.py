"""Auditoría de hardware y selección automática del perfil de render.

* Detecta CPU, RAM, disco, GPUs (nvidia-smi / rocm-smi / lspci / Metal),
  versiones de Python, Blender (módulo bpy o ejecutable) y FFmpeg.
* Enumera los dispositivos Cycles por backend (OPTIX, CUDA, HIP, ONEAPI,
  METAL) y, si se pide, hace un micro-benchmark de cada GPU POR SEPARADO y
  en combinación: no se asume que todas las GPU puedan trabajar juntas
  (arquitecturas o VRAM distintas pueden ralentizar o fallar).
* Elige perfil: 'gpu_high', 'gpu_mid', 'cpu_balanced' o 'cpu_draft'.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import time


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def system_info():
    info = {
        "os": platform.platform(),
        "python": sys.version.split()[0],
        "python_executables": {p: _run([p, "--version"]) for p in ("python3", "python3.11", "python3.12", "python3.13") if shutil.which(p)},
        "cpu": _run(["sh", "-c", "lscpu | grep 'Model name' | cut -d: -f2"]).strip() or platform.processor(),
        "cpu_threads": os.cpu_count(),
        "ram_gb": None,
        "disk_free_gb": round(shutil.disk_usage(os.getcwd()).free / 1e9, 1),
        "ffmpeg": _run(["ffmpeg", "-version"]).split("\n")[0] if shutil.which("ffmpeg") else None,
        "blender_exe": _run(["blender", "--version"]).split("\n")[0] if shutil.which("blender") else None,
        "gpus": [],
    }
    try:
        with open("/proc/meminfo") as f:
            info["ram_gb"] = round(int(f.readline().split()[1]) / 1e6, 1)
    except Exception:
        pass
    if shutil.which("nvidia-smi"):
        out = _run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
        for line in out.splitlines():
            n, mem, drv = [x.strip() for x in line.split(",")]
            info["gpus"].append({"vendor": "NVIDIA", "name": n, "vram": mem, "driver": drv})
    if shutil.which("rocm-smi"):
        info["gpus"].append({"vendor": "AMD", "raw": _run(["rocm-smi", "--showproductname"])})
    if shutil.which("lspci"):
        for line in _run(["lspci"]).splitlines():
            if any(k in line for k in ("VGA", "3D controller", "Display")):
                info.setdefault("pci_display", []).append(line)
    if platform.system() == "Darwin":
        info["gpus"].append({"vendor": "Apple", "raw": _run(["system_profiler", "SPDisplaysDataType"])[:400]})
    return info


def cycles_devices():
    """Lista dispositivos Cycles por backend (requiere bpy)."""
    import bpy
    prefs = bpy.context.preferences.addons["cycles"].preferences
    found = {}
    for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            devs = [{"name": d.name, "type": d.type, "id": d.id} for d in prefs.devices if d.type == backend]
            if devs:
                found[backend] = devs
        except Exception:
            continue
    try:
        bpy_version = bpy.app.version_string
    except Exception:
        bpy_version = None
    return {"bpy": bpy_version, "backends": found, "oidn": "OPENIMAGEDENOISE" in [i.identifier for i in bpy.types.CyclesRenderSettings.bl_rna.properties["denoiser"].enum_items]}


def benchmark_device(cfg, res=(270, 480), samples=16):
    """Render de prueba corto; devuelve segundos (o None si falla)."""
    import bpy
    from . import render as R
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for i in range(40):
        bpy.ops.mesh.primitive_uv_sphere_add(location=((i % 8) * 2.2 - 8, (i // 8) * 2.2, 1))
    bpy.ops.mesh.primitive_plane_add(size=60)
    bpy.ops.object.light_add(type="AREA", location=(0, 0, 8))
    bpy.ops.object.camera_add(location=(0, -16, 6), rotation=(1.2, 0, 0))
    sc.camera = bpy.context.object
    R.configure(sc, {"samples": samples, "resolution": res}, cfg)
    sc.render.filepath = "/tmp/_ce_bench.png"
    try:
        t = time.time()
        bpy.ops.render.render(write_still=True)
        return round(time.time() - t, 2)
    except Exception as e:
        return None


def choose(audit, bench=False):
    devs = audit.get("cycles", {}).get("backends", {})
    best = {"device": "CPU"}
    best_t = None
    if bench:
        best_t = benchmark_device(best)
        audit["benchmarks"] = {"CPU": best_t}
    for backend in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        if backend not in devs:
            continue
        names = [d["name"] for d in devs[backend]]
        candidates = [[n] for n in names] + ([names] if len(names) > 1 else [])
        for combo in candidates:
            cfg = {"device": "GPU", "backend": backend, "devices": combo}
            if not bench:
                if best["device"] == "CPU":
                    best = cfg
                continue
            t = benchmark_device(cfg)
            audit["benchmarks"]["%s:%s" % (backend, "+".join(combo))] = t
            if t is not None and (best_t is None or t < best_t):
                best, best_t = cfg, t
        if best["device"] == "GPU" and not bench:
            break
    vram = 0
    for g in audit["system"].get("gpus", []):
        try:
            vram = max(vram, int(g.get("vram", "0").split()[0]))
        except Exception:
            pass
    if best["device"] == "GPU":
        profile = "gpu_high" if vram >= 10000 or vram == 0 else "gpu_mid"
    else:
        profile = "cpu_balanced" if (audit["system"].get("cpu_threads") or 1) >= 4 else "cpu_draft"
    return best, profile


def audit(bench=False, out_path=None):
    a = {"system": system_info()}
    try:
        a["cycles"] = cycles_devices()
    except Exception as e:
        a["cycles"] = {"error": str(e)}
    device, profile = choose(a, bench)
    a["selected_device"] = device
    a["selected_profile"] = profile
    if out_path:
        with open(out_path, "w") as f:
            json.dump(a, f, indent=2, ensure_ascii=False)
    return a
