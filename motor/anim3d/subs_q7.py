import json
W = json.load(open("au/q7_words.json")); OFF = 0.15
FIX = {"¿Uir": "¿Huir", "abestruces": "avestruces", "1000": "1.000", "Tú": "¿Tú", "Newtons.": "newtons."}
words = []
for w, s, e in W:
    w = FIX.get(w, w)
    if w == "pisándosemáforos":
        m = (s+e)/2; words += [("pisando", s+OFF, m+OFF), ("semáforos", m+OFF, e+OFF)]; continue
    if w == ".000": words[-1] = (words[-1][0]+".000", words[-1][1], e+OFF); continue
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
ev = [f"Dialogue: 2,{ts(0.0)},{ts(2.4)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}¿UN T. REX\\NEN TU CALLE?"]
CH = [(5.7, 8.35, "≈ 12 METROS"), (8.35, 9.9, "≈ 8 TONELADAS"), (11.75, 13.7, "+35.000 N"), (20.45, 22.2, "≈ 20 KM/H"),
      (26.45, 27.25, "×10"), (27.25, 28.0, "×100"), (28.0, 31.25, "×1.000"),
      (40.9, 44.5, "PROTEÍNAS DE T. REX"), (44.5, 47.25, "≈ GALLINA Y AVESTRUZ")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(52.3)},{ts(56.6)},End,,0,0,0,,{{\\fad(200,0)}}¿CORRER, ESCONDERTE\\N{{\\c&H0040D8FF&}}O TIRARLE PIENSO?")
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
open("subs_q7.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
