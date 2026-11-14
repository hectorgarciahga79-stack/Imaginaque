import json
W = json.load(open("au/q27_words.json"))
FIX = {"kilates.": "quilates.", "Respiro": "Respiró.", "Sólo": "Solo", "dorada,": "dorada.", "brillante,": "Brillante.", "pesada.": "Pesada.", "blanco,": "blanco:", "100": "100"}
words = []
for i, (w, s_, e) in enumerate(W):
    words.append((FIX.get(w, w), s_, e))
words = [w for w in words if w[0]]
def ts(x):
    h = int(x//3600); m = int(x % 3600//60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"
hdr = open("subs_q24.py").read().split('hdr = """')[1].split('"""')[0]
ev = [f"Dialogue: 2,{ts(0.0)},{ts(4.3)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}SANGRAS\\NORO"]
CH = [(12.0, 14.3, "ORO DE 24 QUILATES"), (27.0, 29.4, "EL ORO NO LLEVA OXÍGENO"), (34.3, 38.7, "5 L DE ORO ≈ 96 KG")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(60,60)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(72.7)},{ts(75.0)},End,,0,0,0,,{{\\fad(200,0)}}¿HABRÍAS\\N{{\\c&H0040D8FF&}}SABIDO PARAR?")
chunks = []; cur = []
for w in words:
    if 72.7 <= w[1]: continue
    cur.append(w)
    if len(cur) == 3 or w[0].endswith(('.', ',', '?', '!', '…', ':', '»')): chunks.append(cur); cur = []
if cur: chunks.append(cur)
for ch in chunks:
    for k, (w, s, e) in enumerate(ch):
        st = s; en = ch[k+1][1] if k+1 < len(ch) else e+0.18
        txt = " ".join((f"{{\\c&H0040D8FF&}}{x[0].upper()}{{\\c&HFFFFFF&}}" if j == k else x[0].upper()) for j, x in enumerate(ch))
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{{\\fscx104\\fscy104}}{txt}")
open("subs_q27.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
