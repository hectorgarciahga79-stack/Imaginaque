import json
W = json.load(open("au/q26_words.json"))
FIX = {"Danichas": "Dani", "queó": "chasqueó", "votara": "botara", "alarró": "agarró", "rió": "rio", "¿hablas": "«Hablas", "todo?": "todo».", "dijo,": "dijo:", "Dijo,": "Dijo", "noche": "noche,"}
words = []
for i, (w, s_, e) in enumerate(W):
    if w == "Danichas" and i > 20: words.append(("Dani", s_, e)); continue
    words.append((FIX.get(w, w), s_, e))
words = [w for w in words if w[0]]
def ts(x):
    h = int(x//3600); m = int(x % 3600//60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"
hdr = open("subs_q24.py").read().split('hdr = """')[1].split('"""')[0]
ev = [f"Dialogue: 2,{ts(0.0)},{ts(4.7)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}RETROCEDES\\N10 SEGUNDOS"]
CH = [(4.8, 7.6, "-10 S"), (16.6, 17.2, "-10 S"), (19.4, 20.0, "-10 S"), (22.2, 22.8, "-10 S"), (28.9, 29.6, "-10 S"),
      (35.3, 36.2, "-10 S"), (59.42, 61.4, "-10 S")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(60,60)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(77.34)},{ts(80.5)},End,,0,0,0,,{{\\fad(200,0)}}¿QUÉ 10 SEGUNDOS\\N{{\\c&H0040D8FF&}}REPETIRÍAS?")
chunks = []; cur = []
for w in words:
    if 77.34 <= w[1]: continue
    cur.append(w)
    if len(cur) == 3 or w[0].endswith(('.', ',', '?', '!', '…', ':', '»')): chunks.append(cur); cur = []
if cur: chunks.append(cur)
for ch in chunks:
    for k, (w, s, e) in enumerate(ch):
        st = s; en = ch[k+1][1] if k+1 < len(ch) else e+0.18
        txt = " ".join((f"{{\\c&H0040D8FF&}}{x[0].upper()}{{\\c&HFFFFFF&}}" if j == k else x[0].upper()) for j, x in enumerate(ch))
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{{\\fscx104\\fscy104}}{txt}")
open("subs_q26.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
