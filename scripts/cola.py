"""ImaginaQue · estado de la Bandeja: cola de publicación, renders pendientes y control de duplicados.

La Bandeja (https://claude.ai/artifact/5aZ6DAFJysLm7ZiPScsxkx) solo se lee con la herramienta
ArtifactData. Claude la vuelca primero:
    ArtifactData list · collection "videos" · query.limit 300 · out_dir <DIR>
y luego:
    python3 scripts/cola.py <DIR>/videos                  # informe
    python3 scripts/cola.py <DIR>/videos --titulo "¿Y si…?" # ¿esta idea ya existe?
No escribe nada: solo lee los JSON volcados."""
import json, glob, sys, re, unicodedata, difflib, os

def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\b(y si|que pasaria si|que pasa si|un dia|parte \d+|mañana)\b", " ", s)
    return " ".join(s.split())

def load(d):
    rows = []
    for f in glob.glob(os.path.join(d, "*.json")):
        r = json.load(open(f)); r = r.get("data", r); r["_id"] = os.path.basename(f)[:-5]; rows.append(r)
    return rows

def parecidos(rows, titulo, umbral=0.72):
    t = norm(titulo); out = []
    for r in rows:
        k = difflib.SequenceMatcher(None, t, norm(r.get("title"))).ratio()
        if k >= umbral: out.append((round(k, 2), r["_id"], r.get("title"), r.get("prod_status")))
    return sorted(out, reverse=True)

def main():
    d = sys.argv[1]; rows = load(d)
    if "--titulo" in sys.argv:
        t = sys.argv[sys.argv.index("--titulo")+1]; p = parecidos(rows, t)
        print("DUPLICADO PROBABLE" if p else "IDEA NUEVA", *p, sep="\n  "); sys.exit(1 if p else 0)
    vivos = [r for r in rows if r.get("prod_status") not in ("descartado", "retirado", "error")]
    q = sorted(int(m.group(1)) for r in rows if (m := re.fullmatch(r"Q(\d+)", r["_id"])))
    m = sorted(int(x.group(1)) for r in rows if (x := re.fullmatch(r"M(\d+)[ABC]", r["_id"])))
    print(f"Filas: {len(rows)} · siguiente Q libre: Q{(q[-1] if q else 0)+1} · siguiente mini-historia: M{(m[-1] if m else 0)+1}A")
    enc = [r for r in rows if "curso" in str(r.get("prod_status", ""))]
    print("Renders en curso:", ", ".join(r["_id"] for r in enc) or "ninguno")
    tt = [r for r in vivos if r.get("prod_status") == "listo" and not re.search(r"Programado|Publicado", str(r.get("pub_status")))]
    print("Listos sin programar en TikTok:", ", ".join(f'{r["_id"]} «{r.get("title")}»' for r in tt) or "ninguno")
    yt = [r for r in vivos if r.get("prod_status") == "listo" and re.search(r"Pendiente", str(r.get("yt_status")))]
    print("Pendientes en YouTube:", ", ".join(f'{r["_id"]} ({str(r.get("yt_status"))[:50]})' for r in yt) or "ninguno")
    # duplicados entre filas vivas
    dup = []
    for i, a in enumerate(vivos):
        for b in vivos[i+1:]:
            if a.get("series") and a.get("series") == b.get("series") and a.get("part") != b.get("part") and a.get("series") != "YSI": continue
            if (a.get("format") in ("A", None)) and a["_id"][:1] == b["_id"][:1] and a["_id"][:1] in "ABCMS" and a["_id"] != b["_id"] and not a["_id"].startswith("Q"): continue
            k = difflib.SequenceMatcher(None, norm(a.get("title")), norm(b.get("title"))).ratio()
            if k >= 0.85 and a.get("asset_id") and b.get("asset_id"): dup.append((a["_id"], b["_id"], round(k, 2)))
    print("Posibles duplicados publicables:", dup or "ninguno")

if __name__ == "__main__":
    main()
