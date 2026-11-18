# Cinematic Engine 3D (ImaginaQue)

A programmable 3D audiovisual production engine: builds 3D sets, animates
vehicles with basic physics, simulates FX, directs cameras, renders with
Blender Cycles (PBR, reflections, depth of field, motion blur), designs the sound
by code, places the ElevenLabs narration and exports the vertical MP4 for TikTok
and YouTube Shorts. **No images with zooms**: every frame is a real 3D render.

Independent of the rest of ImaginaQue; it plugs in through the CLI (`run.py`)
or by importing `engine.*`.

## Requirements (all free)

| Tool | Use | Install |
|---|---|---|
| Python 3.11–3.13 | engine | — |
| `bpy` (official Blender as a Python module) | 3D, render | `python -m venv .venv && .venv/bin/pip install bpy numpy scipy` |
| FFmpeg ≥ 6 with libass and libx264 | assembly, subtitles, export | `apt install ffmpeg` / ffmpeg.org |
| Fonts | subtitles | included in `assets/fonts` (OFL licence) |
| ElevenLabs (optional) | narration | your account: file generated with the integration, or `ELEVENLABS_API_KEY` |

On Linux servers without a GPU, also install `libegl1` (`apt install libegl1`).

## Quick start

```bash
cd cinematic_engine
.venv/bin/python run.py audit --bench          # hardware audit + GPU benchmark
.venv/bin/python run.py all -p auto            # full video (auto profile)
# or step by step:
.venv/bin/python run.py shots -p preview --step 8      # fast preview to tune cameras
.venv/bin/python run.py shots -p cpu_balanced          # final render (resumable)
.venv/bin/python run.py audio                          # music + SFX + narration
.venv/bin/python run.py post  -p cpu_balanced          # assembly + export MP4
.venv/bin/python run.py check -p cpu_balanced          # automatic QA
```

The result lands in `projects/<storyboard>/video/final.mp4`.

### Quality profiles (`engine/profiles.py`)

| Profile | Resolution | Samples | When |
|---|---|---|---|
| `preview` | 360×640 | 6 | tune framing (1 frame in 4–8) |
| `cpu_draft` | 540×960 → 1080×1920 | 10 | weak CPU |
| `cpu_balanced` | 720×1280 → 1080×1920 | 14 | CPU with no GPU (this cloud environment) |
| `gpu_mid` | 1080×1920 | 64 | GPU with < 10 GB VRAM |
| `gpu_high` | 1080×1920 | 192 + real volumes | GPU ≥ 10 GB |

`audit` detects OPTIX/CUDA/HIP/METAL/ONEAPI and, with `--bench`, measures
**each GPU on its own and combined** before using them together.

## Architecture

```
engine/
  hardware.py    audit + device/profile selection
  kinematics.py  routes, speed profiles, drift/roll/pitch physics, slow motion (TimeMap)
  city.py        procedural coastal city (art deco + neon, towers, beach, palms, streetlights, sky)
  vehicles.py    procedural sports and police cars (rig, real lights, sirens)
  characters.py  pedestrians with walk/run cycle
  fx.py          rain, volumetric fog, tyre smoke, skid marks, explosions, fire
  camera.py      camera system (aerial, travelling, tracking, orbit, crane, handheld)
  materials.py   procedural PBR materials (car paint, wet asphalt, facades, neon...)
  render.py      Cycles + compositing (fog, bloom, chromatic aberration)
  director.py    storyboard -> base scene -> scenes per shot -> render
  audio.py       synthesized music and SFX spatialized from the simulation
  narration.py   ElevenLabs / manual file, phrase-by-phrase sync
  subtitles.py   animated word-by-word ASS subtitles + neon titles
  post.py        assembly, grading, grain, export and QA
storyboards/     videos as data (JSON)
projects/<x>/    .blend files (base + one per shot), renders, audio, video
```

**Scene reuse:** the city is built once (`ciudad_base.blend`) and every
shot opens it and adds only actors, FX and camera. **Batch rendering**: one
subprocess per shot, PNG frames, resumable (frames already done are not
redone).

## Making new videos from an idea or script

1. Copy `storyboards/persecucion_costa_neon.json` → `storyboards/my_video.json`.
2. Edit:
   - `world`: seed (another city), extent, turn street.
   - `routes`: points `[x, y]` (X = east, Y = north; avenue at x≈±8,
     cross streets every `block` m westward from `turn_y`). `fillet` =
     curve radius.
   - `actors`: `model` (`sports`/`police`), `paint`, `underglow`, `speed`
     (table `[t, m/s]`), `anchor` (pass a point at instant t), `follow`
     (chase with a gap), `stop_at` (crash), `physics` (grip, maximum drift).
   - `shots`: `duration`, `sim_start` (or `"after_previous"`), `speed_ramp`
     (slow motion: `[[t, factor]]`), `camera.keys` (position/target fixed
     `world`, or relative to an actor with `offset` [forward, left, up] in
     `heading` space or `world` space), `lens`, `fstop`, `shake`, `smooth`,
     `fx` (`tire_smoke`, `skid_marks`, `explosion`), `pedestrians`,
     `volumetric`.
   - `narration.text` (for ElevenLabs) and `narration.phrases` with the
     screen time `at` of each phrase.
   - `titles`, `subtitles`, `music` (`bpm`, `root`, `drop_at`), `grade`.
3. Preview: `run.py shots -s storyboards/my_video.json -p preview --step 8`
   and check `renders/preview/*`.
4. Final: `run.py all -s storyboards/my_video.json -p auto`.

### Narration with ElevenLabs

- **Option A (used in this prototype):** generate the voice with the ElevenLabs
  integration in Claude (voice “Omar – Narrador cálido y natural”, Spanish
  from Spain, model `eleven_v4`), save the MP3 to `assets/narration/` and point
  `narration.file` at it.
- **Option B:** `export ELEVENLABS_API_KEY=...` and leave `narration.file` empty or
  pointing to a non-existent file: the engine calls the API with your account.
- **Option C (manual):** put any audio file in `narration.file`.

The track is automatically split into phrases by silence detection and each
phrase is placed at its `at` time; the subtitles use those real timings.

## Licences and assets

Everything is generated procedurally (geometry, materials, music, effects).
Signs, place names and vehicle designs are original. No commercial assets
from any video game are used. Fonts: Montserrat and Bebas Neue (SIL OFL).

## Measured results (this prototype)

Cloud environment without a GPU (4-thread Xeon @ 2.1 GHz, 16 GB RAM), `cpu_balanced` profile:

| Shot | Frames | Render time |
|---|---|---|
| s1_aereo | 96 | 52 min |
| s2_avenida | 96 | 61 min |
| s3a_esquina | 42 | 28 min |
| s3b_lateral | 39 | 27 min |
| s3c_frontal | 39 | 21 min |
| s4_derrape | 96 | ~55 min |
| s5_final | 72 | 59 min |

Total ≈ 5 h for 480 frames (≈ 30–38 s/frame). Audio + assembly + QA: < 3 min.
Final QA: 1080×1920, H.264 High, 24 fps, AAC 48 kHz, 20.0 s, −14.2 LUFS,
no black or frozen segments. On a modern GPU (`gpu_mid`/`gpu_high`) the
same storyboard should drop to minutes (not measured: there was no GPU available).

Not tested in this prototype: GPU paths (OPTIX/CUDA/HIP/METAL), volumetric
fog in the final render (tested, but disabled in `cpu_balanced` because it doubles
the CPU time) and rendering a storyboard generated with `tools/nuevo_guion.py`
(validated only at simulation level).
