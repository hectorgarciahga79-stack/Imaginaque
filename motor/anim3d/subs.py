import sys, json; sys.path.insert(0,'/home/claude/anim'); sys.path.insert(0,'/home/claude/t3d')
import asr
from audio_clips import CL
words = {}
for f in ("nar","pro","fig"):
    _, w = asr.transcribe(f"au/{f}.mp3"); words[f] = w
def ts(x):
    h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h}:{m:02d}:{s:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat,66,&H00FFFFFF,&H00FFFFFF,&H00141216,&H96000000,1,0,0,0,100,100,0,0,1,7,3,8,70,70,360,1
Style: Hook,Anton,104,&H0040D8FF,&H0040D8FF,&H00141216,&H96000000,0,0,0,0,100,100,2,0,1,8,4,8,60,60,250,1
Style: End,Anton,118,&H00FFFFFF,&H00FFFFFF,&H00141216,&H96000000,0,0,0,0,100,100,2,0,1,8,4,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
ev.append(f"Dialogue: 1,{ts(0.05)},{ts(1.68)},Hook,,0,0,0,,{{\\fad(120,200)\\t(0,1500,\\fscx106\\fscy106)}}¿Y SI PUDIERAS\\NPARAR EL TIEMPO?")
HL = {"nar": "&H0040D8FF&", "pro": "&H0040D8FF&", "fig": "&H00FF70C8&"}
for cid,(f,a,b,at) in CL.items():
    ws = [(w,s,e) for (w,s,e) in words[f] if s >= a-0.05 and e <= b+0.15 and w.strip(",.").lower() not in ("ej",)]
    chunks=[]; cur=[]
    for w in ws:
        cur.append(w)
        if len(cur)==3 or w[0].endswith(('.',',','?','!','…')): chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
    for ch in chunks:
        for k,(w,s,e) in enumerate(ch):
            st = at+s-a; en = at+(ch[k+1][1] if k+1<len(ch) else e+0.18)-a
            txt = " ".join((f"{{\\c{HL[f]}}}{x[0].upper()}{{\\c&HFFFFFF&}}" if j==k else x[0].upper()) for j,x in enumerate(ch))
            ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{{\\fscx104\\fscy104}}{txt}")
ev.append(f"Dialogue: 2,{ts(56.75)},{ts(59.4)},End,,0,0,0,,{{\\fad(300,0)\\t(0,2500,\\fscx108\\fscy108)}}¿QUIERES SABER\\NQUÉ PASA\\N{{\\c&H0040D8FF&}}DESPUÉS?")
open("subs.ass","w").write(hdr+"\n".join(ev)+"\n"); print(len(ev),"events")
