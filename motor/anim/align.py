"""Turn a connector-generated narration (one file per part) into a timeline: transcribe with word
timestamps, align to the script phrases, and run audio QA. Usage: python3 align.py A1 el/A1.mp3"""
import json, sys, os, difflib, subprocess
import numpy as np, soundfile as sf, librosa
sys.path.insert(0, "/home/claude/anim")
import asr
from voice import classify
from pipeline import SCRIPTS, phrases_of, ROOT

def build(vid, src):
    B = f"{ROOT}/build/{vid}"; os.makedirs(B, exist_ok=True)
    y, sr = librosa.load(src, sr=24000)
    lead = 0.15
    y = np.concatenate([np.zeros(int(lead*sr), np.float32), y, np.zeros(int(0.6*sr), np.float32)])
    sf.write(f"{B}/voice.wav", y, sr)
    hyp, words = asr.transcribe(f"{B}/voice.wav")
    # script tokens with phrase index
    phrases = [(si, p) for si, (txt, _) in enumerate(SCRIPTS[vid]["scenes"]) for p in phrases_of(txt)]
    stoks, sidx = [], []
    for k, (_, p) in enumerate(phrases):
        for w in asr.norm(p): stoks.append(w); sidx.append(k)
    htoks, hidx = [], []
    for j, (w, a, b) in enumerate(words):
        for t in asr.norm(w): htoks.append(t); hidx.append(j)
    sm = difflib.SequenceMatcher(None, stoks, htoks, autojunk=False)
    tmap = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): tmap[blk.a+k] = hidx[blk.b+k]
    tl = {"engine": "elevenlabs", "scenes": [{"start": None, "end": None} for _ in SCRIPTS[vid]["scenes"]], "phrases": []}
    prev = None; prev_end = lead
    for k, (si, p) in enumerate(phrases):
        idxs = [tmap[i] for i, kk in enumerate(sidx) if kk == k and i in tmap]
        if idxs:
            st, en = words[min(idxs)][1], words[max(idxs)][2]
        else:
            st, en = prev_end, prev_end+0.6
        st = max(st, prev_end-0.05)
        tl["phrases"].append({"scene": si, "text": p, "kind": classify(p, prev), "start": round(st, 3), "end": round(max(en, st+0.3), 3), "matched": len(idxs)})
        prev = p; prev_end = tl["phrases"][-1]["end"]
    for ph in tl["phrases"]:
        sc = tl["scenes"][ph["scene"]]
        if sc["start"] is None: sc["start"] = ph["start"]-0.12
        sc["end"] = ph["end"]
    total = len(y)/sr
    # v8 (04-11-2026): sin relleno para llegar a 66 s (hundía la retención; la monetización exige 10.000 seguidores).
    # Capítulos: END_PAD=2.2 deja la cartela «CONTINUARÁ» 2 s. Formato B: sin relleno.
    END_PAD = float(os.environ.get("END_PAD", "0"))
    if END_PAD > 0:
        y = np.concatenate([y, np.zeros(int(END_PAD*sr), np.float32)]); sf.write(f"{B}/voice.wav", y, sr); total = len(y)/sr
    MIN_TOTAL = float(os.environ.get("MIN_TOTAL", "0"))
    if total < MIN_TOTAL:
        y = np.concatenate([y, np.zeros(int((MIN_TOTAL-total)*sr), np.float32)]); sf.write(f"{B}/voice.wav", y, sr)
        tl["padded"] = round(MIN_TOTAL-total, 2); total = len(y)/sr
    tl["scenes"][0]["start"] = 0.0; tl["scenes"][-1]["end"] = total
    for i in range(len(tl["scenes"])-1): tl["scenes"][i]["end"] = tl["scenes"][i+1]["start"]
    tl["total"] = total
    # QA
    ref = " ".join(w for w in asr.norm(" ".join(p for _, p in phrases)) if w not in NUMW)
    h = " ".join(w for w in asr.norm(hyp) if not any(ch.isdigit() for ch in w) and w not in NUMW)
    gaps = [words[i+1][1]-words[i][2] for i in range(len(words)-1)]
    tl["qa"] = {"wer": round(asr.wer(ref, h), 3), "max_gap_s": round(max(gaps), 2) if gaps else 0,
                "unmatched_phrases": [ph["text"] for ph in tl["phrases"] if ph["matched"] == 0], "transcript": hyp}
    json.dump(tl, open(f"{B}/timeline.json", "w"), ensure_ascii=False, indent=1)
    return tl

NUMW = set("cero uno una dos tres cuatro cinco seis siete ocho nueve diez once doce veinte veinticuatro veintiun veintiuno treinta cien ciento trescientos mil millon millones ochenta".split())

if __name__ == "__main__":
    tl = build(sys.argv[1], sys.argv[2])
    q = tl["qa"]; print(sys.argv[1], "total", round(tl["total"], 1), "WER", q["wer"], "max_gap", q["max_gap_s"], "unmatched", q["unmatched_phrases"])
