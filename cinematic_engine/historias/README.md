# Retention videos (`run.py viral`)

Goal: **people watch to the end and want another one**. Visual quality
comes second; every video reuses the 3D footage that's already rendered plus,
if needed, a cheap close-up shot (`engine/inserts.py`, ~6 s/frame).

## Filter before producing (if it fails one, throw the idea out)

1. Would I stop? The first 2 s carry the most striking image + a personal
   or impossible line (never an intro or presentation).
2. Does it make me curious? An open question in the first 5 s.
3. Do I want to know what happens next? Escalation every 3–5 s.
4. Would I watch to the end? The reveal comes in the last 6 s.
5. Would it make me comment? Ends with a twist + a question with several answers.

## Story format (`historias/<name>.json`)

- `sources`: folders of rendered frames (`projects/.../renders/...`).
- `narration.file`: ElevenLabs voice. **One phrase per line** in the text you
  send to ElevenLabs; the engine aligns each phrase on its own and removes
  long silences (`gap`).
- `beats`: one per phrase (a change of shot every 1–2.5 s):
  - `src`, `a`, `b`: shot and frame range (it stretches/compresses to fill the phrase).
  - `zoom` [start, end], `center` [x, y], `shake` (px), `hold` (freeze in s),
    `reverse`, `speed`.
  - `look`: `rewind` | `bw` | `cold`; `flash`, `glitch`.
  - `text` (giant hook text, `accent` = yellow), `stamp`, `circle` [x, y, r]
    in 1080×1920 coordinates (`circle_at: "hold"` = at the moment of the freeze).
  - `sfx`: `whoosh`, `whoosh_down`, `hit`, `impact`, `explosion`, `metal`,
    `rewind`, `scratch`, `heartbeat`, `siren`, `screech`, `riser`, `thunder`
    (`"scratch:hold"` = at the moment of the freeze).
  - `music`: `dip` (music filtered and down) | `cut` (dead silence for impact).
  - `pause`: dramatic silence before the phrase. `no_sub`: no subtitles.
- `ending`: `question` + `cta` (final card that drives comments).
- `music.drop_beat`: beat where the music comes in hard.

The edit always adds: word-by-word subtitles, a progress bar,
SFX on every cut, ducking of the music under the voice, −14 LUFS.

```bash
.venv/bin/python run.py viral historias/la_placa.json
# -> projects/virales/la_placa/la_placa.mp4  (~1–2 min with the footage already rendered)
.venv/bin/python run.py inserto "R. VEGA"   # close-up shot of the badge (~8 min CPU)
```
