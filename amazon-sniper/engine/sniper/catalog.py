"""Product identification: what *exactly* is this listing?

Turns a free-text Amazon title into (family, model_key, label) and raises
anti-false-positive flags (accessory, used, refurbished, empty box, parts...).

PRIOR_EUR are conservative *orientative* floor prices used only as the
last-resort reference when the engine has no own history and no
equivalent products observed. They are labelled "prior" and capped in the
score; they are never shown as a fact.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


def norm(t: str) -> str:
    t = (t or "").replace("â„¢", " ").replace("™", " ").replace("®", " ").replace("©", " ")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip().lower()


@dataclass
class Identity:
    family: str = "other"
    model_key: str | None = None
    label: str | None = None
    value_tier: int = 0             # 0 unknown, 1 low, 2 mid, 3 high, 4 flagship
    prior_eur: float | None = None
    flags: list = field(default_factory=list)       # hard problems -> reject
    warnings: list = field(default_factory=list)    # soft doubts -> lower score


# ---------------------------------------------------------------- priors
PRIOR_EUR = {
    # GPUs (orientative street-price floors, new, Spain)
    "gpu:rtx-5090": 2100, "gpu:rtx-5080": 1000, "gpu:rtx-5070-ti": 750, "gpu:rtx-5070": 520,
    "gpu:rtx-5060-ti-16gb": 420, "gpu:rtx-5060-ti-8gb": 350, "gpu:rtx-5060": 290,
    "gpu:rtx-4090": 1700, "gpu:rtx-4080-super": 950, "gpu:rtx-4080": 950, "gpu:rtx-4070-ti-super": 750,
    "gpu:rtx-4070-ti": 700, "gpu:rtx-4070-super": 560, "gpu:rtx-4070": 500,
    "gpu:rx-9070-xt": 620, "gpu:rx-9070": 550, "gpu:rx-7900-xtx": 800, "gpu:rx-7900-xt": 650,
    "gpu:rx-9060-xt-16gb": 340,
    # CPUs
    "cpu:core-ultra-9-285k": 520, "cpu:core-ultra-7-265k": 330, "cpu:i9-14900k": 430, "cpu:i9-14900kf": 410,
    "cpu:i9-13900k": 400, "cpu:i7-14700k": 330, "cpu:i7-14700kf": 310,
    "cpu:ryzen-9-9950x3d": 650, "cpu:ryzen-9-9950x": 500, "cpu:ryzen-9-9900x3d": 520, "cpu:ryzen-9-9900x": 360,
    "cpu:ryzen-9-7950x3d": 500, "cpu:ryzen-9-7950x": 430, "cpu:ryzen-9-7900x": 330,
    "cpu:ryzen-7-9800x3d": 440, "cpu:ryzen-7-7800x3d": 330, "cpu:ryzen-7-9700x": 280,
    # consoles
    "console:ps5-pro": 700, "console:ps5": 400, "console:ps5-digital": 350,
    "console:xbox-series-x": 450, "console:switch-2": 430,
    # Apple
    "apple:macbook-pro": 1600, "apple:macbook-air": 950, "apple:ipad-pro": 1000, "apple:ipad-air": 600, "apple:mac-mini": 600, "apple:mac-studio": 2000,
    "phone:iphone-pro": 1100, "phone:iphone": 750, "phone:galaxy-s-ultra": 1000,
}
FAMILY_PRIOR = {
    "gpu-generic": None, "laptop:rtx-5090": 3500, "laptop:rtx-5080": 2600, "laptop:rtx-4090": 2800,
    "laptop:rtx-4080": 2100, "laptop:rtx-5070-ti": 1700,
    "desktop:rtx-5090": 3800, "desktop:rtx-5080": 2300, "desktop:rtx-4090": 3000, "desktop:rtx-4080": 2000,
}

# --------------------------------------------------------------- red flags
ACCESSORY_RX = re.compile(
    r"\b(soporte|holder|bracket|anti[- ]?sag|riser|cable|alargador|adaptador|extensor|funda|estuche|bolsa|"
    r"protector|skin|pegatina|vinilo|sticker|backplate|waterblock|bloque de agua|ventilador|disipador|"
    r"refrigerador|cooler|base de carga|estacion de carga|cargador|dock(?!er)|soporte vertical|kit de limpieza|"
    r"pasta termica|thermal pad|tornillos?|mando|controller|volante|auriculares|headset|"
    r"teclado|raton|mouse|alfombrilla|correa|lapiz|stylus|carcasa|cover|tapa|placa frontal|faceplate|"
    r"tarjeta regalo|gift card|codigo|suscripcion|juego para|videojuego)\b"
)
COMPAT_RX = re.compile(r"\b(compatible con|para|for|fits|apto para)\s+(\w+\s+){0,3}?(rtx|rx|ps5|playstation|xbox|switch|macbook|ipad|iphone|ryzen|core)")
USED_RX = re.compile(r"\b(usad[oa]s?|segunda mano|de ocasion|pre[- ]?owned|used)\b")
REFURB_RX = re.compile(r"\b(reacondicionad[oa]s?|renewed|renovad[oa]s?|refurbished|reformad[oa])\b")
BOX_RX = re.compile(r"\b(caja vacia|solo caja|solo la caja|empty box|box only|caja original sin|sin (la )?(tarjeta|consola|gpu|producto))\b")
PARTS_RX = re.compile(r"\b(repuesto|recambio|spare|para piezas|for parts|pieza de|averiad[oa]|defectuos[oa]|no funciona)\b")
MINING_RX = re.compile(r"\b(mineria|mining|ex[- ]?mining)\b")
GAME_RX = re.compile(r"\((ps5|ps4|xbox|switch|nintendo switch 2?)\)|\bedicion (estandar|deluxe|coleccionista)\b")


def _gpu(t: str) -> tuple[str, str, int] | None:
    m = re.search(r"\brtx\s?-?(50[5-9]0|40[5-9]0|30[5-9]0)\s?(ti\s?super|ti|super)?\b", t)
    if m:
        num, suf = m.group(1), (m.group(2) or "").replace(" ", "-")
        key = f"rtx-{num}" + (f"-{suf}" if suf else "")
        if num in ("5060", "4060") and suf == "ti":
            mem = re.search(r"\b(8|16)\s?gb\b", t)
            if mem:
                key += f"-{mem.group(1)}gb"
        tier = 4 if num in ("5090", "4090") else 3 if num in ("5080", "4080") or (num in ("5070", "4070") and "ti" in suf) else 2 if num[-2:] in ("70", "60") else 1
        label = f"RTX {num}" + (f" {suf.replace('-', ' ').upper().replace('TI', 'Ti').replace('SUPER', 'SUPER')}" if suf else "")
        return key, label, tier
    m = re.search(r"\brx\s?-?(9070|9060|7900|7800|7700|7600)\s?(xtx|xt|gre)?\b", t)
    if m:
        num, suf = m.group(1), m.group(2) or ""
        key = f"rx-{num}" + (f"-{suf}" if suf else "")
        if num == "9060" and suf == "xt":
            mem = re.search(r"\b(8|16)\s?gb\b", t)
            if mem:
                key += f"-{mem.group(1)}gb"
        tier = 3 if num in ("9070", "7900") else 2
        return key, f"RX {num} {suf.upper()}".strip(), tier
    return None


def _cpu(t: str) -> tuple[str, str, int] | None:
    m = re.search(r"\bcore\s?ultra\s?([579])\s?-?(2\d{2}[kfhsx]{0,2})\b", t)
    if m:
        return f"core-ultra-{m.group(1)}-{m.group(2)}", f"Core Ultra {m.group(1)} {m.group(2).upper()}", 3 if m.group(1) == "9" else 2
    m = re.search(r"\bi([579])[- ]?(1[0-4]\d{3}[kfsx]{0,3})\b", t)
    if m:
        return f"i{m.group(1)}-{m.group(2)}", f"Core i{m.group(1)}-{m.group(2).upper()}", 3 if m.group(1) == "9" else 2
    m = re.search(r"\bryzen\s?([579])\s?(\d{4}x3d|\d{4}x|\d{4}g?)\b", t)
    if m:
        return f"ryzen-{m.group(1)}-{m.group(2)}", f"Ryzen {m.group(1)} {m.group(2).upper()}", 3 if m.group(1) == "9" or "x3d" in m.group(2) else 2
    return None


def identify(title: str, category: str | None = None) -> Identity:
    t = norm(title)
    cat = norm(category or "")
    idn = Identity()

    # ---- red flags (independent of family)
    if USED_RX.search(t):
        idn.flags.append("usado")
    if REFURB_RX.search(t):
        idn.flags.append("reacondicionado")
    if BOX_RX.search(t):
        idn.flags.append("caja_vacia_o_incompleto")
    if PARTS_RX.search(t):
        idn.flags.append("pieza_o_repuesto")
    if MINING_RX.search(t):
        idn.warnings.append("posible_uso_mineria")

    head = t[:60]
    accessory = bool(ACCESSORY_RX.search(head)) or bool(COMPAT_RX.search(t[:90]))

    is_laptop = bool(re.search(r"\b(portatil|laptop|notebook)\b", t)) or "portatil" in cat
    is_desktop = bool(re.search(r"\b(ordenador|pc gaming|pc de sobremesa|sobremesa|desktop|gaming pc|torre gaming)\b", t)) or "sobremesa" in cat
    gpu = _gpu(t)
    cpu = _cpu(t)

    if is_laptop and gpu and not accessory:
        idn.family, idn.model_key, idn.label = "laptop", f"laptop:{gpu[0]}", f"Portátil {gpu[1]}"
        idn.value_tier = max(3, gpu[2])
    elif is_desktop and gpu and not accessory:
        idn.family, idn.model_key, idn.label = "desktop", f"desktop:{gpu[0]}", f"PC {gpu[1]}"
        idn.value_tier = max(3, gpu[2])
    elif gpu and re.search(r"tarjeta gr[a-z]*|graphics card|gddr|\bgpu\b|geforce|radeon", t):
        idn.family, idn.model_key, idn.label, idn.value_tier = "gpu", f"gpu:{gpu[0]}", gpu[1], gpu[2]
    elif cpu and re.search(r"procesador|processor|\bcpu\b|nucleos|cores|lga|am5|am4|desktop processor", t) and not is_laptop:
        idn.family, idn.model_key, idn.label, idn.value_tier = "cpu", f"cpu:{cpu[0]}", cpu[1], cpu[2]
    elif re.search(r"\b(consola|console)\b", t[:80]) and re.search(r"playstation\s?5|\bps5\b|xbox series [xs]|nintendo switch", t) and not accessory:
        if re.search(r"playstation\s?5|\bps5\b", t):
            v = "ps5-pro" if re.search(r"\bpro\b", t) else "ps5-digital" if re.search(r"digital", t) else "ps5"
            idn.family, idn.model_key, idn.label, idn.value_tier = "console", f"console:{v}", v.upper().replace("-", " "), 3 if v == "ps5-pro" else 2
        elif re.search(r"xbox series x", t):
            idn.family, idn.model_key, idn.label, idn.value_tier = "console", "console:xbox-series-x", "Xbox Series X", 2
        elif re.search(r"xbox series s", t):
            idn.family, idn.model_key, idn.label, idn.value_tier = "console", "console:xbox-series-s", "Xbox Series S", 1
        elif re.search(r"nintendo switch\s?2", t):
            idn.family, idn.model_key, idn.label, idn.value_tier = "console", "console:switch-2", "Nintendo Switch 2", 2
        elif re.search(r"nintendo switch", t):
            idn.family, idn.model_key, idn.label, idn.value_tier = "console", "console:switch", "Nintendo Switch", 1
    elif re.search(r"^(apple )?(\d{4} )?(portatil )?(apple )?macbook (pro|air)\b", t) and not accessory:
        kind = re.search(r"\bmacbook (pro|air)\b", t).group(1)
        chip = re.search(r"\bm([1-6])\s?(pro|max)?\b", t)
        idn.family = "apple"
        idn.model_key = f"apple:macbook-{kind}" + (f"-m{chip.group(1)}" + (f"-{chip.group(2)}" if chip.group(2) else "") if chip else "")
        idn.label = f"MacBook {kind.title()}" + (f" M{chip.group(1)}{' ' + chip.group(2).title() if chip.group(2) else ''}" if chip else "")
        idn.value_tier = 4 if kind == "pro" else 3
        idn.prior_eur = PRIOR_EUR[f"apple:macbook-{kind}"]
    elif re.search(r"^(apple )?(\d{4} )?(apple )?(ipad pro|ipad air|mac mini|mac studio|imac)\b", t) and not accessory:
        k = re.search(r"\bipad pro\b|\bipad air\b|\bmac mini\b|\bmac studio\b|\bimac\b", t).group(0).replace(" ", "-")
        idn.family, idn.model_key, idn.label, idn.value_tier = "apple", f"apple:{k}", k.replace("-", " ").title(), 3
    elif re.search(r"^(apple )?iphone 1[5-9]", t) and not accessory:
        m = re.search(r"\biphone (1[5-9])\s?(pro max|pro|plus|air|e)?", t)
        suf = (m.group(2) or "").replace(" ", "-")
        idn.family, idn.model_key = "phone", f"phone:iphone-{m.group(1)}" + (f"-{suf}" if suf else "")
        idn.label, idn.value_tier = f"iPhone {m.group(1)} {suf.replace('-', ' ').title()}".strip(), 3 if "pro" in suf else 2
        idn.prior_eur = PRIOR_EUR["phone:iphone-pro" if "pro" in suf else "phone:iphone"]
    elif re.search(r"\bgalaxy (s2[4-9]|z fold|z flip)", t) and not accessory:
        m = re.search(r"\bgalaxy (s2[4-9]|z fold ?\d?|z flip ?\d?)\s?(ultra|\+|plus|fe)?", t)
        idn.family, idn.model_key = "phone", "phone:galaxy-" + m.group(0).replace("galaxy ", "").replace(" ", "-").replace("+", "plus")
        idn.label, idn.value_tier = m.group(0).title(), 3 if (m.group(2) == "ultra" or "fold" in m.group(1)) else 2
    elif re.search(r"\b(ssd|nvme|m\.2)\b", t):
        cap = re.search(r"\b(\d{1,2})\s?tb\b", t)
        if cap:
            n = int(cap.group(1))
            idn.family, idn.model_key, idn.label = "ssd", f"ssd:{n}tb" + (":nvme" if "nvme" in t else ""), f"SSD {n} TB" + (" NVMe" if "nvme" in t else "")
            idn.value_tier = 3 if n >= 4 else 2 if n >= 2 else 1
    elif re.search(r"\bddr5\b", t) and re.search(r"\b(ram|memoria|dimm|kit)\b", t):
        cap = re.search(r"\b(16|24|32|48|64|96|128|192|256)\s?gb\b", t)
        if cap:
            n = int(cap.group(1))
            idn.family, idn.model_key, idn.label = "ram", f"ram:ddr5:{n}gb", f"DDR5 {n} GB"
            idn.value_tier = 3 if n >= 64 else 2 if n >= 32 else 1
    elif re.search(r"\b(placa base|motherboard)\b", t):
        chip = re.search(r"\b(z890|x870e?|x670e?|z790|b850|b650e?|b860|b760)\b", t)
        if chip:
            idn.family, idn.model_key, idn.label = "motherboard", f"mb:{chip.group(1)}", f"Placa {chip.group(1).upper()}"
            idn.value_tier = 2 if chip.group(1)[0] in "zx" else 1
    elif re.search(r"\b(oled|qd-oled|qd oled)\b", t) and re.search(r"\b(monitor|televisor|tv|smart tv)\b", t):
        size = re.search(r"\b(\d{2})\s?(\"|''|pulgadas|inch|”)", t)
        kind = "monitor" if "monitor" in t else "tv"
        sz = size.group(1) if size else "x"
        idn.family, idn.model_key, idn.label = kind, f"{kind}:oled:{sz}", f"{'Monitor' if kind == 'monitor' else 'TV'} OLED {sz}\""
        idn.value_tier = 3 if (kind == "tv" and sz.isdigit() and int(sz) >= 55) or kind == "monitor" else 2

    if idn.model_key:
        if idn.prior_eur is None:
            idn.prior_eur = PRIOR_EUR.get(idn.model_key) or FAMILY_PRIOR.get(idn.model_key)
            if idn.prior_eur is None and idn.model_key.startswith(("gpu:rtx-", "gpu:rx-")):
                idn.prior_eur = PRIOR_EUR.get(re.sub(r"-(8|16)gb$", "", idn.model_key))
            if idn.prior_eur is None and idn.model_key.startswith("cpu:"):
                base = re.sub(r"(k|kf|f|x|x3d)$", "", idn.model_key)
                idn.prior_eur = next((v for k, v in PRIOR_EUR.items() if k.startswith(base)), None)

    if accessory:
        idn.flags.append("accesorio")
        if idn.family in ("gpu", "cpu", "console", "laptop", "desktop", "apple", "phone"):
            idn.warnings.append("titulo_mezcla_accesorio_y_producto")
    if GAME_RX.search(t) and idn.family != "console":
        idn.flags.append("videojuego_no_consola")
    return idn


# --------------------------------------------------------------- research seeds
SEARCH_SEEDS = [
    # (priority, query)
    (1, "RTX 5090"), (1, "RTX 5080"), (1, "RTX 5070 Ti"), (1, "RTX 5070"), (1, "RTX 4090"), (1, "RTX 4080"),
    (1, "RX 9070 XT"), (1, "RX 7900 XTX"), (1, "tarjeta gráfica NVIDIA"), (1, "tarjeta gráfica RTX 5090 32GB"),
    (2, "Intel Core i9"), (2, "Intel Core Ultra 9 285K"), (2, "Ryzen 9 9950X3D"), (2, "Ryzen 9"), (2, "Ryzen 7 9800X3D"), (2, "Intel i7 14700K"),
    (3, "Gaming PC RTX 5090"), (3, "PC gaming RTX 5080"), (3, "ordenador gaming RTX 4090"),
    (4, "portátil gaming RTX 5090"), (4, "portátil gaming RTX 5080"), (4, "portátil gaming RTX 4090"), (4, "portátil RTX 5070 Ti"),
    (5, "PS5 Pro consola"), (5, "PS5 Slim consola"), (5, "Xbox Series X consola"), (5, "Nintendo Switch 2 consola"),
    (6, "fuente alimentación 1200W ATX 3.1"),
    (7, "DDR5 64GB"), (7, "DDR5 32GB 6000"),
    (8, "SSD 4TB NVMe"), (8, "SSD 8TB NVMe"), (8, "SSD 2TB PCIe 5.0"),
    (9, "placa base X870E"), (9, "placa base Z890"),
    (10, "monitor OLED 4K"), (10, "monitor QD-OLED 34"), (10, "monitor OLED 27 360Hz"),
    (11, "OLED 4K 65 pulgadas"), (11, "TV OLED 77"),
    (12, "MacBook Pro M4"), (12, "MacBook Pro M5"), (12, "iPad Pro M4"), (12, "Mac Studio"),
    (13, "iPhone 17 Pro Max"), (13, "Galaxy S25 Ultra"), (13, "Galaxy Z Fold"),
]

# brands x models to auto-generate new query combinations
COMBO_BRANDS = {
    "gpu": ["ASUS ROG", "ASUS TUF", "MSI Suprim", "MSI Gaming Trio", "Gigabyte Aorus", "Gigabyte Gaming OC", "Zotac", "PNY", "Palit", "Gainward", "INNO3D", "Sapphire Nitro", "PowerColor"],
    "gpu_models": ["RTX 5090", "RTX 5080", "RTX 5070 Ti", "RTX 4090", "RX 9070 XT"],
    "laptop": ["ASUS ROG Strix", "MSI Titan", "MSI Raider", "Lenovo Legion", "Alienware", "Razer Blade", "HP Omen", "Acer Predator"],
    "laptop_models": ["RTX 5090", "RTX 5080", "RTX 4090"],
}

# keywords -> priority for automatically discovered Amazon categories
CATEGORY_PRIORITY = [
    (1, r"tarjetas? graficas"), (2, r"procesadores|cpu"), (3, r"ordenadores de sobremesa|sobremesa|pc gaming"),
    (4, r"portatiles|gaming"), (5, r"consolas|playstation|xbox|nintendo"), (6, r"componentes|fuentes de alimentacion"),
    (7, r"memoria ram|^memoria"), (8, r"ssd|almacenamiento de datos internos|discos duros internos"),
    (9, r"placas base"), (10, r"monitores"), (11, r"televisores|televisión|tv"), (12, r"apple|mac|tablets"),
    (13, r"moviles|smartphones|telefonos"),
]
CATEGORY_EXCLUDE = re.compile(
    r"accesorios|cables|impresoras|escaneres|tinta|cartuchos|fundas|ratones|teclados|alfombrillas|"
    r"adaptadores|bolsas|limpieza|protectores|soportes|baterias|cargadores|software|juegos|videojuegos$|"
    r"merchandising|tarjetas regalo|suscripciones|tablets de escritura|lcd y ewriters|dispositivos de red",
    re.I,
)


def category_priority(name: str) -> int | None:
    n = norm(name)
    if CATEGORY_EXCLUDE.search(n):
        return None
    for prio, rx in CATEGORY_PRIORITY:
        if re.search(rx, n):
            return prio
    return 14
