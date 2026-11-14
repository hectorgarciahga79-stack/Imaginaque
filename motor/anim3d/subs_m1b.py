import json
W = json.load(open("/home/claude/m1b/words.json")); OFF = 0.15
words = []
for w, s, e in W:
    if w == ",8": words[-1] = (words[-1][0]+",8", words[-1][1], e+OFF); continue
    w = {"3.": "TRES.", "4.": "CUATRO.", "Cuelgate": "Cuélgate"}.get(w, w)
    words.append((w, s+OFF, e+OFF))
def ts(x):
    h = int(x//3600); m = int(x % 3600//60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat,66,&H00FFFFFF,&H00FFFFFF,&H00141216,&H96000000,1,0,0,0,100,100,0,0,1,7,3,8,70,70,360,1
Style: Hook,Anton,118,&H0040D8FF,&H0040D8FF,&H00141216,&H96000000,0,0,0,0,100,100,2,0,1,9,4,2,60,60,560,1
Style: Chip,Anton,104,&H00FFFFFF,&H00FFFFFF,&H00141216,&H96000000,0,0,0,0,100,100,2,0,3,10,0,2,70,70,620,1
Style: End,Anton,112,&H00FFFFFF,&H00FFFFFF,&H00141216,&H96000000,0,0,0,0,100,100,2,0,1,8,4,2,70,70,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = [f"Dialogue: 2,{ts(0.0)},{ts(3.9)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}COLGADA\\NSOBRE EL CIELO"]
ev.append(f"Dialogue: 1,{ts(4.0)},{ts(6.0)},Chip,,0,0,0,,{{\\3c&H2A8AD8&\\fad(120,120)}}CAÍDA AL CIELO · PARTE 2")
CH = [(16.65, 26.3, "REGLA #3\\NBRAZOS ESTIRADOS"), (41.0, 45.85, "REGLA #4\\NPRUEBA EL AGARRE"), (45.95, 49.5, "TOLDOS, CANALONES,\\NANTENAS: NO"),
      (49.6, 51.95, "FAROLAS Y\\NBARANDILLAS: SÍ"), (62.5, 66.6, "LA ZONA AVANZA")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(75.62)},{ts(77.8)},End,,0,0,0,,{{\\fad(200,0)}}CONTINUARÁ…\\N{{\\c&H0040D8FF&\\fs70}}CAÍDA AL CIELO · PARTE 3")
chunks = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) == 3 or w[0].endswith(('.', ',', '?', '!', '…', ':')): chunks.append(cur); cur = []
if cur: chunks.append(cur)
for ch in chunks:
    for k, (w, s, e) in enumerate(ch):
        st = s; en = ch[k+1][1] if k+1 < len(ch) else e+0.18
        txt = " ".join((f"{{\\c&H0040D8FF&}}{x[0].upper()}{{\\c&HFFFFFF&}}" if j == k else x[0].upper()) for j, x in enumerate(ch))
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{{\\fscx104\\fscy104}}{txt}")
open("subs_m1b.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
