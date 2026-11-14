import json
W = json.load(open("au/q12_words.json"))
FIX = {"6": "seis", "8": "ocho", "45": "45", "9": "9"}
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
ev = [f"Dialogue: 2,{ts(0.0)},{ts(2.95)},Hook,,0,0,0,,{{\\fad(0,200)\\t(0,1500,\\fscx108\\fscy108)}}¿Y SI LA TIERRA\\NFUERA UN CUBO?"]
CH = [(3.0, 5.0, "MISMA MASA"), (5.5, 8.0, "6 CARAS · 8 ESQUINAS"), (10.7, 13.3, "LA GRAVEDAD TIRA AL CENTRO"), (16.5, 19.2, "6 OCÉANOS REDONDOS"),
      (20.9, 24.2, "AIRE SOLO EN EL CENTRO"), (27.6, 31.0, "PLANO… PERO CUESTA ARRIBA"), (31.6, 35.7, "RAMPA DE ~45°"),
      (36.3, 38.9, "ESQUINA: ~8.900 KM"), (39.3, 43.1, "+3.800 KM QUE UNA CARA"), (45.8, 48.3, "SIN AIRE"),
      (48.5, 50.7, "EVEREST: 8,8 KM"), (50.8, 53.8, "ESQUINA: +3.800 KM"), (58.3, 60.6, "TERREMOTOS GLOBALES"), (61.1, 63.9, "DE VUELTA A BOLA")]
for a, b, t in CH:
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\3c&H1E3AD8&\\fad(80,80)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{t}")
ev.append(f"Dialogue: 2,{ts(65.8)},{ts(68.2)},End,,0,0,0,,{{\\fad(200,0)}}¿EN QUÉ CARA\\N{{\\c&H0040D8FF&}}VIVIRÍAS?")
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
open("subs_q12.ass", "w").write(hdr+"\n".join(ev)+"\n"); print(len(ev), "events")
