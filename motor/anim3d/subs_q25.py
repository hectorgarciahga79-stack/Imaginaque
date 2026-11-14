import json
W = json.load(open("au/q25_words.json"))
FIX = {"niró": "miró", "Secenta": "Sesenta", "decía,": "decía…", "Sólo": "Solo", "¡Vivas!": "¡Vivas!", "para": "paracaídas,", "caídas,": ""}
words = []
for w, s_, e in W:
    if w.startswith(".") and words:
        pw, ps, pe = words[-1]; words[-1] = (pw+w, ps, e); continue
    words.append((FIX.get(w, w), s_, e))
words = [w for w in words if w[0]]
def ts(x):
    h = int(x//3600); m = int(x % 3600//60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"
hdr = open("subs_q24.py").read().split('hdr = """')[1].split('"""')[0]
ev = [f"Dialogue: 2,{ts(0.0)},{ts(4.9)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}VES CUÁNTO\\NTE QUEDA DE VIDA"]
CH = [(26.2, 30.6, "ESPERANZA DE VIDA EN ESPAÑA ≈ 84 AÑOS (INE)"), (41.8, 43.9, "QUEDAN 8 MIN"), (51.3, 54.8, "10 SEGUNDOS")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(74.8)},{ts(78.19)},End,,0,0,0,,{{\\fad(200,0)}}¿REGALARÍAS\\N{{\\c&H0040D8FF&}}AÑOS DE TU VIDA?")
chunks = []; cur = []
for w in words:
    if 74.8 <= w[1]: continue
    cur.append(w)
    if len(cur) == 3 or w[0].endswith(('.', ',', '?', '!', '…', ':')): chunks.append(cur); cur = []
if cur: chunks.append(cur)
for ch in chunks:
    for k, (w, s, e) in enumerate(ch):
        st = s; en = ch[k+1][1] if k+1 < len(ch) else e+0.18
        txt = " ".join((f"{{\\c&H0040D8FF&}}{x[0].upper()}{{\\c&HFFFFFF&}}" if j == k else x[0].upper()) for j, x in enumerate(ch))
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{{\\fscx104\\fscy104}}{txt}")
open("subs_q25.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
