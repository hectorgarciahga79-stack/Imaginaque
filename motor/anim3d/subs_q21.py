import json
W = json.load(open("au/q21_words.json"))
FIX = {"Alex": "Álex", "41,": "41,", "entendió,": "entendió:", "20,": "20:", ",000": "1.000", "30": "30:", "tierra.": "Tierra.", "mar.": "mar?", "La": "La"}
words = []
for w, s_, e in W:
    if w.startswith(".") and words:
        pw, ps, pe = words[-1]; words[-1] = (pw+w, ps, e); continue
    words.append((FIX.get(w, w), s_, e))
for i in range(len(words)-1):
    if words[i][0] == "La" and words[i+1][0] == "entregarías": words[i] = ("¿La",)+tuple(words[i][1:])
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
ev = [f"Dialogue: 2,{ts(0.0)},{ts(7.2)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}HORA 41\\NMÁS RICO QUE ESPAÑA"]
CH = [(11.0, 13.8, "HORA 1 = 2 €"), (16.1, 20.4, "HORA 10 = 1.024 €"), (27.1, 34.5, "HORA 20 = 1.048.576 € (≈ 7,9 T)"), (46.0, 50.7, "HORA 30 = 1.073 MILLONES"),
      (50.9, 56.1, "HORA 41 = 2,2 BILLONES > PIB DE ESPAÑA"), (61.1, 68.8, "HORA 90: MÁS QUE LA MASA DE LA TIERRA")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(73.2)},{ts(76.99)},End,,0,0,0,,{{\\fad(200,0)}}¿LA ENTREGAS\\N{{\\c&H0040D8FF&}}O AL MAR?")
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
open("subs_q21.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
