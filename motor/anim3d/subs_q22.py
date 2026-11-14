import json
W = json.load(open("au/q22_words.json"))
FIX = {"¡ayuda!": "AYUDA.", "Vió": "Vio", "2,": "2:", "3,": "3:", "4,": "4:", "6,": "6:", "números": "números:"}
words = []
for w, s_, e in W:
    if w.startswith(".") and words:
        pw, ps, pe = words[-1]; words[-1] = (pw+w, ps, e); continue
    words.append((FIX.get(w, w), s_, e))
for i in range(len(words)-1):
    if words[i][0] == "me" and words[i+1][0] == "vía": words[i] = ("medía",)+tuple(words[i][1:]); words[i+1] = ("",)+tuple(words[i+1][1:])
words = [w for w in words if w[0]]
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
ev = [f"Dialogue: 2,{ts(0.0)},{ts(4.8)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}17 CM\\NY SU GATO LO CAZA"]
CH = [(7.5, 10.7, "10 VECES MÁS PEQUEÑO CADA HORA"), (14.7, 17.3, "1-1-2"), (21.5, 24.0, "HORA 2 · 1,75 CM"), (33.1, 38.7, "HORA 3 · 1,75 MM"), (39.2, 44.3, "HORA 4 · 0,175 MM"),
      (55.5, 59.3, "HORA 6 · ≈ 2 MICRAS"), (65.9, 70.0, "LÍMITE DEL MICROSCOPIO ≈ 200 NM"), (70.5, 73.2, "HORA 7 · 175 NM")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(77.0)},{ts(79.87)},End,,0,0,0,,{{\\fad(200,0)}}¿CÓMO LO\\N{{\\c&H0040D8FF&}}SALVARÍAS?")
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
open("subs_q22.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
