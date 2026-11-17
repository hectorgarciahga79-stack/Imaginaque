#!/usr/bin/env python3
"""Genera un guion completo (JSON) a partir de una idea breve.

Ejemplo de idea (ideas/ejemplo_idea.json):
{
  "title": "Huida en la Bahía",
  "base": "storyboards/persecucion_costa_neon.json",   # ciudad, rutas y actores a reutilizar
  "hero_paint": [0.02, 0.35, 0.9], "underglow": [0.1, 0.9, 1.0], "seed": 21,
  "titles": [{"text": "BAHÍA ROTA", "start": 0.3, "end": 3.5}],
  "narration_file": "assets/narration/mi_voz.mp3",
  "shots": [
    {"type": "aerial",        "duration": 4,   "say": "Bahía Rota. Las tres de la mañana."},
    {"type": "travelling",    "duration": 4,   "say": "Un coche azul que nadie ha visto antes."},
    {"type": "side_tracking", "duration": 2,   "actor": "poli1", "say": "Hasta ahora."},
    {"type": "front_reverse", "duration": 3},
    {"type": "orbit",         "duration": 4,   "slowmo": 0.35, "fx": ["tire_smoke", "skid_marks"], "say": "Un giro."},
    {"type": "crane_out",     "duration": 3,   "say": "Y desaparece."}
  ]
}

Uso:  python tools/nuevo_guion.py ideas/ejemplo_idea.json storyboards/bahia_rota.json
Los tiempos de simulación se encadenan solos (continuidad); la cámara lenta
usa un 'speed ramp' suave. Después: run.py shots -s <guion> -p preview --step 8
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from engine.presets import PRESETS  # noqa: E402
from engine.kinematics import TimeMap  # noqa: E402


def build(idea):
    base = json.load(open(os.path.join(HERE, idea.get("base", "storyboards/persecucion_costa_neon.json")), encoding="utf-8"))
    sb = copy.deepcopy(base)
    sb["title"] = idea["title"]
    sb["world"]["seed"] = idea.get("seed", sb["world"]["seed"])
    hero = idea.get("hero", "heroe")
    if "hero_paint" in idea:
        sb["actors"][hero]["paint"] = idea["hero_paint"]
    if "underglow" in idea:
        sb["actors"][hero]["underglow"] = idea["underglow"]
    sb["titles"] = idea.get("titles", [])
    shots, phrases = [], []
    t_screen, t_sim = 0.0, idea.get("sim_start", 0.0)
    for i, s in enumerate(idea["shots"]):
        d = float(s["duration"])
        actor = s.get("actor", hero)
        shot = {"id": "s%d_%s" % (i + 1, s["type"]), "duration": d, "sim_start": t_sim,
                "camera": PRESETS[s["type"]](actor, d), "rain": s.get("rain", s["type"] != "aerial")}
        if s.get("slowmo"):
            f = s["slowmo"]
            shot["speed_ramp"] = [[0, 1.0], [0.4, f], [d - 0.6, f], [d, 1.0]]
        fx = []
        for kind in s.get("fx", []):
            fx.append({"type": kind, "actor": actor})
        if fx:
            shot["fx"] = fx
        shots.append(shot)
        if s.get("say"):
            phrases.append({"text": s["say"], "at": t_screen + 0.35})
        t_sim = TimeMap(t_sim, d, shot.get("speed_ramp")).sim_end
        t_screen += d
    sb["shots"] = shots
    sb["duration_sim"] = t_sim + 1.0
    sb["narration"] = {"provider": "elevenlabs", "voice": base["narration"]["voice"],
                       "text": " ".join(p["text"] for p in phrases),
                       "file": idea.get("narration_file", ""), "split": "silence", "phrases": phrases}
    return sb


if __name__ == "__main__":
    idea = json.load(open(sys.argv[1], encoding="utf-8"))
    sb = build(idea)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(sb, f, ensure_ascii=False, indent=2)
    print("Guion creado:", sys.argv[2], "| planos:", len(sb["shots"]), "| duración:", sum(s["duration"] for s in sb["shots"]), "s")
    print("Texto para ElevenLabs:\n ", sb["narration"]["text"])
