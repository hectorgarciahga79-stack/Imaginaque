#!/usr/bin/env python3
"""Cinematic Engine 3D — CLI.

Uso (con el Python que tiene `bpy` instalado, p. ej. .venv/bin/python):

  python run.py audit [--bench]                       # auditoría de hardware
  python run.py all   -s storyboards/X.json [-p perfil]
  python run.py base  -s ...                           # construir ciudad base (.blend)
  python run.py shots -s ... [-p perfil] [--only s1,s2] [--step N]
  python run.py audio -s ...                           # música + SFX + narración
  python run.py post  -s ... [-p perfil]               # montaje, grade, subtítulos, MP4
  python run.py check -s ... [-p perfil]               # QA del MP4 + hoja de contactos

Perfiles: preview, cpu_draft, cpu_balanced, gpu_mid, gpu_high (auto = según auditoría).
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def project_dir(sb_path):
    name = os.path.splitext(os.path.basename(sb_path))[0]
    d = os.path.join(HERE, "projects", name)
    os.makedirs(d, exist_ok=True)
    return d


def resolve_profile(name, proj):
    from engine import profiles
    if name != "auto":
        return profiles.get(name), None
    from engine import hardware
    a = hardware.audit(bench=False, out_path=os.path.join(proj, "audit.json"))
    return profiles.get(a["selected_profile"]), a["selected_device"]


def cmd_audit(args):
    from engine import hardware
    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    a = hardware.audit(bench=args.bench, out_path=os.path.join(HERE, "output", "audit.json"))
    print(json.dumps(a, indent=2, ensure_ascii=False))


def cmd_base(args):
    from engine.director import load_storyboard, build_base
    sb = load_storyboard(args.storyboard)
    proj = project_dir(args.storyboard)
    path = os.path.join(proj, "blend", "ciudad_base.blend")
    t = time.time()
    build_base(sb, path)
    print("[base] %s (%.1fs)" % (path, time.time() - t))


def _shot_worker(args):
    """Subproceso: construye y renderiza UN plano (aislamiento de memoria)."""
    from engine.director import load_storyboard, simulate, build_shot, render_shot
    from engine import profiles
    sb = load_storyboard(args.storyboard)
    proj = project_dir(args.storyboard)
    prof = profiles.get(args.profile)
    device = json.loads(args.device) if args.device else None
    shot = next(s for s in sb["shots"] if s["id"] == args.shot)
    _, states = simulate(sb)
    blend = os.path.join(proj, "blend", "%s.blend" % shot["id"])
    t = time.time()
    build_shot(sb, shot, prof, states, os.path.join(proj, "blend", "ciudad_base.blend"), blend, device)
    print("[shot %s] escena construida en %.1fs" % (shot["id"], time.time() - t), flush=True)
    if args.no_render:
        return
    out = os.path.join(proj, "renders", prof["name"], shot["id"])
    t = time.time()
    render_shot(blend, out, step=args.step or prof.get("step", 1))
    print("[shot %s] render en %.1fs" % (shot["id"], time.time() - t), flush=True)


def cmd_shots(args):
    from engine.director import load_storyboard
    sb = load_storyboard(args.storyboard)
    proj = project_dir(args.storyboard)
    if not os.path.exists(os.path.join(proj, "blend", "ciudad_base.blend")) or args.rebuild_base:
        cmd_base(args)
    prof, device = resolve_profile(args.profile, proj)
    only = args.only.split(",") if args.only else None
    log = os.path.join(proj, "render_log.txt")
    for shot in sb["shots"]:
        if only and shot["id"] not in only:
            continue
        cmd = [sys.executable, __file__, "_shot", "-s", args.storyboard, "-p", prof["name"], "--shot", shot["id"]]
        if args.step:
            cmd += ["--step", str(args.step)]
        if device:
            cmd += ["--device", json.dumps(device)]
        if args.no_render:
            cmd += ["--no-render"]
        t = time.time()
        print(">>", " ".join(cmd), flush=True)
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = [l for l in r.stdout.splitlines() if l.startswith("[shot") or "Error" in l or "Traceback" in l or "Saved:" in l[-60:]]
        with open(log, "a") as f:
            f.write(r.stdout[-20000:])
        print("\n".join(l for l in lines if not l.strip().endswith(".png'")), flush=True)
        if r.returncode != 0:
            print(r.stdout[-4000:])
            raise SystemExit("Fallo en el plano %s" % shot["id"])
        print("[%s] %.1fs" % (shot["id"], time.time() - t), flush=True)


def cmd_audio(args):
    from engine.director import load_storyboard, simulate, export_timeline
    from engine import audio, narration
    sb = load_storyboard(args.storyboard)
    proj = project_dir(args.storyboard)
    _, states = simulate(sb)
    tl = export_timeline(sb, states, os.path.join(proj, "timeline.json"))
    nar = narration.prepare(sb, HERE, os.path.join(proj, "audio"))
    out = audio.render_soundtrack(sb, tl, nar, os.path.join(proj, "audio"))
    print("[audio]", out)


def cmd_post(args):
    from engine.director import load_storyboard
    from engine import post, profiles
    sb = load_storyboard(args.storyboard)
    proj = project_dir(args.storyboard)
    prof = profiles.get(args.profile if args.profile != "auto" else json.load(open(os.path.join(proj, "audit.json")))["selected_profile"])
    out = post.assemble(sb, proj, prof, args.output)
    print("[post]", out)


def cmd_check(args):
    from engine import post
    from engine.director import load_storyboard
    sb = load_storyboard(args.storyboard)
    proj = project_dir(args.storyboard)
    print(json.dumps(post.qa(args.output or os.path.join(proj, "video", "final.mp4"), proj), indent=2))


def cmd_all(args):
    t = time.time()
    cmd_shots(args)
    cmd_audio(args)
    cmd_post(args)
    cmd_check(args)
    print("Total: %.1f min" % ((time.time() - t) / 60))


def main():
    ap = argparse.ArgumentParser(description="Cinematic Engine 3D")
    ap.add_argument("command", choices=["audit", "base", "shots", "audio", "post", "check", "all", "_shot"])
    ap.add_argument("-s", "--storyboard", default=os.path.join(HERE, "storyboards", "persecucion_costa_neon.json"))
    ap.add_argument("-p", "--profile", default="auto")
    ap.add_argument("--only")
    ap.add_argument("--shot")
    ap.add_argument("--step", type=int)
    ap.add_argument("--device")
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--rebuild-base", action="store_true")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    {"audit": cmd_audit, "base": cmd_base, "shots": cmd_shots, "audio": cmd_audio, "post": cmd_post,
     "check": cmd_check, "all": cmd_all, "_shot": _shot_worker}[args.command](args)


if __name__ == "__main__":
    main()
