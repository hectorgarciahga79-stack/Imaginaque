import json
W = json.load(open("au/q8_words.json")); OFF = 0.0
FIX = {"zombies?": "zombis?", "huya": "huye", "Canarias,": "Canarias…", "Al": "¿Al", "azotea.": "azotea?"}
words = []; first_ni = True
for w, s_, e in W:
    if w == "ni" and first_ni: w = "mil"; first_ni = False
    w = FIX.get(w, w)
    words.append((w, s_+OFF, e+OFF))
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
ev = [f"Dialogue: 2,{ts(0.0)},{ts(2.6)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}¿ZOMBIS\\NDESDE EL MAR?"]
CH = [(3.5, 4.98, "1.000.000.000"), (11.2, 15.2, "−1.000 M: CERO LUZ"), (16.4, 19.0, "≈ 4 °C"), (20.2, 22.2, "+1 ATM CADA 10 M"),
      (22.2, 25.9, "4.000 M = 400 VECES"), (31.7, 34.4, "1.000 MILL. ≈ 500 KM²"), (34.4, 37.1, "MADRID ≈ 604 KM²"),
      (43.45, 44.08, "CÁDIZ"), (44.08, 44.72, "GALICIA"), (44.72, 45.45, "CANARIAS"),
      (51.0, 54.0, "EL MAR BAJA ≈ 0,0002 MM"), (54.0, 56.9, "UN PELO ≈ 0,07 MM")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(59.3)},{ts(62.64)},End,,0,0,0,,{{\\fad(200,0)}}¿AL MONTE\\N{{\\c&H0040D8FF&}}O A LA AZOTEA?")
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
open("subs_q8.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
