"""Subtítulos animados (ASS/libass) sincronizados con la narración.

* Palabra a palabra: cada palabra aparece con un 'pop' (escala 125% -> 100%)
  y se resalta en color de acento mientras se pronuncia.
* Rótulo de título con brillo de neón (capa desenfocada + capa nítida).
* Posición segura para TikTok/Shorts (por encima de la interfaz inferior).
"""
import os


def _ts(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def _ass_color(rgb_hex):
    """'#RRGGBB' -> '&H00BBGGRR'"""
    if rgb_hex.startswith("&H"):
        return rgb_hex
    r, g, b = rgb_hex[1:3], rgb_hex[3:5], rgb_hex[5:7]
    return "&H00%s%s%s" % (b, g, r)


def build_ass(phrases, out_path, width=1080, height=1920, cfg=None, titles=None):
    cfg = cfg or {}
    font = cfg.get("font", "Montserrat Black")
    size = cfg.get("size", 74)
    accent = _ass_color(cfg.get("accent", "#FF2BD6"))
    outline = _ass_color(cfg.get("outline", "#12001A"))
    margin_v = cfg.get("margin_v", 560)
    title_font = cfg.get("title_font", "Bebas Neue")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{font},{size},&H00FFFFFF,&H00FFFFFF,{outline},&H96000000,0,0,0,0,100,100,1,0,1,6,3,2,80,80,{margin_v},1
Style: Title,{title_font},210,&H00FFFFFF,&H00FFFFFF,&H00D62BFF,&H00000000,0,0,0,0,100,100,6,0,1,4,0,8,40,40,300,1
Style: TitleGlow,{title_font},210,&H00D62BFF,&H00D62BFF,&H00D62BFF,&H00000000,0,0,0,0,100,100,6,0,1,14,0,8,40,40,300,1
Style: Kicker,{font},44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,12,0,1,3,0,8,40,40,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for ph in phrases:
        words = ph["text"].upper().split()
        t0, t1 = ph["start"], ph["end"]
        dur = max(0.3, t1 - t0)
        weights = [len(w) + 2 for w in words]
        tot = sum(weights)
        acc = 0.0
        parts = []
        for w, wt in zip(words, weights):
            ws = int(acc / tot * dur * 1000)
            we = int((acc + wt) / tot * dur * 1000)
            acc += wt
            pop = ws + 90
            parts.append(
                "{\\alpha&HFF&\\fscx125\\fscy125\\1c%s"
                "\\t(%d,%d,\\alpha&H00&)\\t(%d,%d,\\fscx100\\fscy100)\\t(%d,%d,\\1c&H00FFFFFF&)}%s" % (
                    accent, ws, ws + 1, ws, pop, we, we + 120, w))
        hold_end = t1 + 0.35
        text = "{\\fad(60,140)}" + " ".join(parts)
        lines.append("Dialogue: 1,%s,%s,Sub,,0,0,0,,%s" % (_ts(t0 - 0.02), _ts(hold_end), text))
    for tt in titles or []:
        a, b = tt["start"], tt["end"]
        fx = "{\\fad(350,450)\\fscx92\\fscy92\\t(0,%d,\\fscx104\\fscy104)}" % int((b - a) * 1000)
        lines.append("Dialogue: 0,%s,%s,TitleGlow,,0,0,0,,{\\blur18}%s%s" % (_ts(a), _ts(b), fx, tt["text"]))
        lines.append("Dialogue: 1,%s,%s,Title,,0,0,0,,%s%s" % (_ts(a), _ts(b), fx, tt["text"]))
        if tt.get("kicker"):
            lines.append("Dialogue: 1,%s,%s,Kicker,,0,0,0,,{\\fad(500,400)}%s" % (_ts(a + 0.3), _ts(b), tt["kicker"]))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")
    return out_path
