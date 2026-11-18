#!/usr/bin/env python3
"""Guion (texto) -> historia JSON lista para `run.py viral`.

Automatiza el montaje: cada línea del guion es una frase de narración; el
script elige el metraje de la biblioteca del canal por palabras clave,
alterna planos para no repetir, y asigna efectos según el tipo de frase
(golpe corto, pregunta, revelación, acción...).

Formato del guion (una frase por línea; se ignoran líneas vacías y '#'):
    Imagina que en GTA 6 la policía nunca olvida tu cara. | texto=LA POLICÍA NUNCA OLVIDA
    Derrape. Humo. Y una explosión que se ve desde la playa. | clip=explosion sorpresa
Directivas tras '|': clip=<id>, texto=<TEXTO GRANDE>, sorpresa, pausa=<s>,
    musica=dip|cut, look=bw|cold|rewind, hold=<s>, sfx=a,b

Uso:
    python tools/historia_desde_guion.py guion.txt historias/x.json \
        --canal gta6 --categoria hipotetico --voz assets/narration/x.mp3 \
        --pregunta "¿QUIÉN LO ENVIÓ?" --cta "COMENTA TU TEORÍA"
Después:  python run.py viral historias/x.json
El texto para ElevenLabs (sin directivas) se guarda en <historia>_elevenlabs.txt.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(c for c in w if c.isalnum())


ACTION = {"derrape", "humo", "explosion", "pisa", "fondo", "grita", "choque", "acelera", "escapan", "corre"}
REVEAL = {"pero", "entonces", "solo", "nadie", "nunca", "vacio", "ni"}


def classify(text):
    words = [norm(w) for w in text.split() if norm(w)]
    if text.strip().endswith("?"):
        return "pregunta"
    if len(words) <= 3:
        return "golpe"
    if set(words) & ACTION:
        return "accion"
    if words and words[0] in REVEAL:
        return "revelacion"
    return "info"


def pick_clip(text, clips, recent, used_count):
    words = {norm(w) for w in text.split()}
    best, best_score = None, -1e9
    for c in clips:
        score = 3.0 * len(words & set(c["tags"]))
        if c["id"] in recent[-2:]:
            score -= 8
        elif c["id"] in recent[-5:]:
            score -= 2.5
        score -= 0.6 * used_count.get(c["id"], 0)
        if score > best_score:
            best, best_score = c, score
    return best


def build(lines, lib, args):
    clips = lib["clips"]
    by_id = {c["id"]: c for c in clips}
    recent, used = [], {}
    beats = []
    for raw in lines:
        text, _, dirs = raw.partition("|")
        text = text.strip()
        d = {}
        for tok in re.findall(r'(\w+)=("[^"]*"|[^ ]+)|(\w+)', dirs):
            if tok[0]:
                d[tok[0]] = tok[1].strip('"')
            else:
                d[tok[2]] = True
        kind = classify(text)
        clip = by_id[d["clip"]] if "clip" in d else pick_clip(text, clips, recent, used)
        n = used.get(clip["id"], 0)
        used[clip["id"]] = n + 1
        recent.append(clip["id"])
        a, b = clip["a"], clip["b"]
        if n and b - a > 30:  # reutilización: otro tramo del mismo plano
            third = (b - a) // 3
            a = a + third * (n % 3)
            b = min(clip["b"], a + max(third, 20))
        beat = {"say": text, "clip": clip["id"], "a": a, "b": b}
        if "center" in clip:
            beat["center"] = clip["center"]
        if kind == "golpe":
            beat.update({"zoom": [1.08, 1.24], "shake": 8, "sfx": ["hit"]})
        elif kind == "accion":
            beat.update({"zoom": [1.04, 1.2], "shake": 12, "flash": True, "sfx": ["whoosh", "impact"]})
        elif kind == "revelacion":
            beat.update({"zoom": [1.0, 1.12], "music": "dip", "sfx": ["whoosh_down"]})
        elif kind == "pregunta":
            beat.update({"zoom": [1.0, 1.1]})
        else:
            beat.update({"zoom": [1.0, 1.1] if len(beats) % 2 else [1.12, 1.02]})
        if "texto" in d:
            beat["text"] = d["texto"]
            beat["accent"] = True
        if d.get("sorpresa"):
            beat["surprise"] = True
            beat.setdefault("flash", True)
        for k, key in (("pausa", "pause"), ("hold", "hold")):
            if k in d:
                beat[key] = float(d[k])
        if "musica" in d:
            beat["music"] = d["musica"]
        if "look" in d:
            beat["look"] = d["look"]
        if "sfx" in d:
            beat["sfx"] = d["sfx"].split(",")
        beats.append(beat)
    beats[0].setdefault("flash", True)
    beats[0].setdefault("sfx", ["impact"])
    last = beats[-1]
    last.update({"no_sub": True, "hold": last.get("hold", 2.0)})
    story = {"title": args.titulo or os.path.splitext(os.path.basename(args.salida))[0], "channel": args.canal,
             "category": args.categoria, "narration": {"file": args.voz},
             "music": {"drop_beat": min(3, len(beats) - 1)}, "beats": beats,
             "ending": {"question": args.pregunta, "cta": args.cta}}
    return story


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("salida")
    ap.add_argument("--canal", default="gta6")
    ap.add_argument("--categoria", default="hipotetico")
    ap.add_argument("--voz", default="")
    ap.add_argument("--titulo")
    ap.add_argument("--pregunta", default="¿Y TÚ QUÉ HARÍAS?")
    ap.add_argument("--cta", default="TE LEO EN COMENTARIOS")
    args = ap.parse_args()
    canal = json.load(open(os.path.join(HERE, "canales", args.canal + ".json"), encoding="utf-8"))
    lib = json.load(open(os.path.join(HERE, canal["library"]), encoding="utf-8"))
    lines = [l.strip() for l in open(args.guion, encoding="utf-8") if l.strip() and not l.startswith("#")]
    story = build(lines, lib, args)
    with open(args.salida, "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=1)
    tts = os.path.splitext(args.salida)[0] + "_elevenlabs.txt"
    with open(tts, "w", encoding="utf-8") as f:
        f.write("\n".join(l.partition("|")[0].strip() for l in lines) + "\n")
    words = sum(len(l.partition("|")[0].split()) for l in lines)
    print("Historia: %s | %d frases | %d palabras (~%.0f s de voz)" % (args.salida, len(lines), words, words / 3.0))
    if words / 3.0 < 62:
        print("AVISO: el guion parece corto para 60 s; añade contenido real (no relleno).")
    print("Texto para ElevenLabs:", tts)


if __name__ == "__main__":
    sys.exit(main())
