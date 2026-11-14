import json
W = json.load(open("au/q11_words.json"))
FIX = {"puede": "puedes", "subir": "huir", "despacio,": "despacio:"}
words = []
for w, s_, e in W:
    if w.startswith(".") and words:
        pw, ps, pe = words[-1]; words[-1] = (pw+w, ps, e); continue
    words.append((FIX.get(w, w), s_, e))
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
ev = [f"Dialogue: 2,{ts(0.0)},{ts(3.4)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}¿TODOS LOS VOLCANES\\NA LA VEZ?"]
CH = [(3.5, 5.7, "1.350 VOLCANES"), (5.76, 7.4, "EN EL MISMO SEGUNDO"), (12.1, 15.2, "LAVA: SUELE IR LENTA"), (15.4, 20.5, "LA CENIZA HUNDE TEJADOS"),
      (20.7, 24.6, "TAMBORA · 1815"), (24.6, 26.9, "HASTA -3 °C"), (26.9, 28.9, "1816: NIEVE EN VERANO"), (28.96, 31.5, "X1.000"),
      (33.4, 34.8, "MESES SIN SOL"), (38.3, 40.5, "INVIERNO VOLCÁNICO"), (42.7, 47.9, "VOLCANES ≈ 0,5 GT CO2/AÑO"),
      (48.1, 52.5, "HUMANOS ≈ 40 GT (X60)"), (54.8, 57.4, "EL CALOR SIGUE AHÍ")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(60.4)},{ts(63.31)},End,,0,0,0,,{{\\fad(200,0)}}¿INVIERNO O\\N{{\\c&H0040D8FF&}}VERANO?")
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
open("subs_q11.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
