"""Estilo Leo 2D (paleta luminosa) — ¿Y si…? Q3: ¿y si al parpadear aparecieras un metro más adelante?"""
from engine import *
from scenes import daysky, clouds, cloud
from cine import chip, stat_card, time_card, post, txt, box, fs, ic_check, ic_warn, ic_clock, ic_drop, C, OUT
from scenes_q1 import sea, splash
from props import calendar
import cairo, math, random

GY = 1290          # suelo (por encima de la banda de subtítulos)
PX_M = 150         # píxeles por metro
BLINK = 1.25       # segundos entre parpadeos en las escenas «en directo»

def P(lt, d, a=0.0, b=1.0): return clamp((lt/d-a)/max(1e-3, b-a))

def lids(c, k):
    """párpados negros que cierran la pantalla (k 0→1→0)"""
    if k <= 0: return
    h = H/2*k
    c.set_source_rgb(0.05, 0.05, 0.08)
    c.rectangle(0, 0, W, h); c.fill(); c.rectangle(0, H-h, W, h); c.fill()

def blink_k(t, period=BLINK, dur=0.16):
    ph = t % period
    return math.sin(ph/dur*math.pi) if ph < dur else 0.0

def hops(t, period=BLINK):
    """número de parpadeos completados (cada uno = 1 m)"""
    return int(t/period)

def ground_ruler(c, x0, y, n, step=PX_M, col=None):
    c.set_source_rgb(*(col or INK)); c.set_line_width(5)
    for i in range(n+1):
        x = x0+i*step; c.move_to(x, y+6); c.line_to(x, y+(34 if i % 5 == 0 else 22)); c.stroke()
    c.move_to(x0, y+6); c.line_to(x0+n*step, y+6); c.stroke()

def ghost(c, x, y, s, a):
    """silueta translúcida donde estaba Leo"""
    c.save(); c.push_group(); leo(c, x, y, s, "stand", "neutral", 0); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()

def land_blob(c, pts, col, col2=None):
    c.new_path(); c.move_to(*pts[0])
    for i in range(1, len(pts)): c.line_to(*pts[i])
    c.close_path(); fill_stroke(c, col, 6)

def pin(c, x, y, lab, t, col=None):
    k = back(t/0.35) if t > 0 else 0
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    c.new_path(); c.move_to(0, 0); c.curve_to(-40, -50, -36, -96, 0, -96); c.curve_to(36, -96, 40, -50, 0, 0); c.close_path()
    fill_stroke(c, col or PAL['red'], 5)
    circle(c, 0, -64, 14); c.set_source_rgb(1, 1, 1); c.fill()
    c.restore()
    if t > 0.2: label_tag(c, lab, x, y+44, 36)

def dotted(c, pts, k, col=None, lw=9):
    """polilínea discontinua que se dibuja hasta k"""
    L = [0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1]+math.hypot(b[0]-a[0], b[1]-a[1]))
    tot = L[-1]*k
    c.set_source_rgb(*(col or PAL['red'])); c.set_line_width(lw); c.set_dash([22, 16]); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(*pts[0]); end = pts[0]
    for i in range(1, len(pts)):
        if L[i] <= tot: c.line_to(*pts[i]); end = pts[i]
        else:
            f = (tot-L[i-1])/max(1e-3, L[i]-L[i-1]); a, b = pts[i-1], pts[i]
            end = (lerp(a[0], b[0], f), lerp(a[1], b[1], f)); c.line_to(*end); break
    c.stroke(); c.set_dash([]); c.set_line_cap(cairo.LINE_CAP_BUTT)
    return end

def street_bg(c, t, cam=0.0):
    daysky(c); clouds(c, t, 30, n=4, y0=330, y1=700)
    c.save(); c.translate(-cam*0.35, 0)
    for i in range(-1, 9):
        building(c, i*230+40, GY-90, 200, 300+(i*97) % 260, [PAL['b1'], PAL['b2'], PAL['b3'], PAL['b4']][i % 4], seed=i)
    c.restore()
    c.rectangle(0, GY-90, W, 90); c.set_source_rgb(*PAL['walk']); c.fill()
    c.rectangle(0, GY, W, H-GY); c.set_source_rgb(*PAL['sole']); c.fill()
    c.set_source_rgb(*INK); c.set_line_width(LW); c.move_to(0, GY); c.line_to(W, GY); c.stroke()

# ---------------- escenas ----------------
def q3_0(c, lt, d, t):   # gancho: cada parpadeo, un metro más
    n = hops(lt); bk = blink_k(lt)
    cam = n*PX_M*0.55
    z = 1.0+0.12*ease(P(lt, d))
    c.save(); c.translate(W/2, GY); c.scale(z, z); c.translate(-W/2, -GY)
    street_bg(c, t, cam)
    c.save(); c.translate(-cam, 0)
    ground_ruler(c, 160, GY, 12)
    for i in range(1, 6): txt(c, f"{i} m", 160+i*PX_M, GY+80, 30, INK, "Anton")
    for j in range(max(0, n-2), n):
        ghost(c, 160+j*PX_M, GY, 0.78, 0.18+0.12*(j-n+2))
    leo(c, 160+n*PX_M, GY, 0.78, "stand" if n == 0 else "shrug", "shock" if n else "neutral", t)
    c.restore(); c.restore()
    if lt > 0.5: chip(c, "PARPADEO = +1 METRO", W/2, 420, lt-0.5, ic_warn, size=42, bg=PAL['yellow'])
    post(c, t, 0.25, 0.04)
    lids(c, bk)

def q3_1(c, lt, d, t):   # 15–20 parpadeos por minuto
    grad_bg(c, hexc("#FFE9B8"), hexc("#FFD27A"))
    k = ease(P(lt, d, 0, 0.4))
    leo(c, W/2, 1760, 1.6, "stand", "neutral", t, look=(0.0, -0.1))
    # contador de parpadeos
    cnt = int(lerp(0, 20, P(lt, d, 0.3, 0.95)))
    stat_card(c, "PARPADEOS", "15–20", "/min", W/2, 420, lt-0.4, icon=ic_clock)
    if lt > d*0.35:
        txt(c, f"{cnt}", 160, 820, 120, PAL['red'], "Anton")
        txt(c, "PARPADEOS", 160, 870, 30, INK)
    post(c, t, 0.2, 0.04)
    lids(c, blink_k(lt+0.3, 0.9, 0.14)*k)

def q3_2(c, lt, d, t):   # 17 km al día sin dar un paso
    daysky(c); clouds(c, t, 40, n=4, y0=330, y1=640)
    k = P(lt, d, 0.05, 0.85)
    # carretera que pasa por debajo
    c.rectangle(0, GY-120, W, 120); c.set_source_rgb(*PAL['road']); c.fill()
    c.set_source_rgb(1, 1, 1); c.set_line_width(10); c.set_dash([60, 50], -(t*900) % 110)
    c.move_to(0, GY-60); c.line_to(W, GY-60); c.stroke(); c.set_dash([])
    c.rectangle(0, GY, W, H-GY); c.set_source_rgb(*PAL['ground']); c.fill()
    for i in range(6):
        x = (i*260 - t*420) % (W+300) - 150; tree(c, x, GY-120, 0.7)
    leo(c, 420, GY-30, 0.8, "stand", "happy", t)
    km = 17*ease(k)
    box(c, 600, 640, 380, 200, C['paper'], 22, 5)
    txt(c, "AL DÍA", 790, 700, 32, C['grey'])
    txt(c, f"{km:.0f} km".replace(".", ","), 790, 800, 100, INK, "Anton")
    if lt > d*0.45: chip(c, "0 PASOS", 420, 560, lt-d*0.45, ic_check, size=44, bg=PAL['yellow'])
    post(c, t, 0.2, 0.04)

def spain_map(c, t):
    grad_bg(c, PAL['sea'], PAL['sea_d'])
    pts = [(130, 520), (300, 470), (520, 500), (700, 470), (900, 520), (960, 600), (880, 700), (930, 820), (850, 960),
           (790, 1060), (700, 1150), (520, 1210), (330, 1190), (230, 1100), (160, 980), (180, 860), (120, 740), (150, 640)]
    land_blob(c, pts, PAL['sand'])
    land_blob(c, [(960, 600), (1080, 640), (1080, 400), (900, 430), (900, 520)], PAL['land'])   # Francia (insinuada)

MAD, BCN = (500, 820), (860, 680)

def q3_3(c, lt, d, t):   # en un mes, de Madrid a Barcelona
    spain_map(c, t)
    k = ease(P(lt, d, 0.2, 0.85))
    pin(c, *MAD, "MADRID", lt-0.1)
    end = dotted(c, [MAD, (680, 760), BCN], k)
    leo(c, end[0], end[1]-10, 0.28, "stand", "happy", t)
    pin(c, *BCN, "BARCELONA", lt-d*0.8, PAL['yellow'])
    calendar(c, 270, 470, 0.55, "30", "DÍAS")
    if lt > d*0.5: chip(c, "505 km EN LÍNEA RECTA", W/2, 1260, lt-d*0.5, size=34, bg=C['paper'])
    post(c, t, 0.25, 0.04)

def atlantic(c, t, k):
    grad_bg(c, PAL['sea'], PAL['sea_d'])
    for i in range(14):
        x = (i*170 + t*30) % (W+100) - 50; y = 420+(i*137) % 860
        c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(5); c.arc(x, y, 26, math.pi*1.1, math.pi*1.9); c.stroke()
    land_blob(c, [(0, 380), (210, 420), (250, 620), (190, 820), (230, 1040), (120, 1300), (0, 1300)], PAL['land'])
    land_blob(c, [(1080, 380), (890, 460), (860, 700), (920, 900), (880, 1150), (1080, 1300)], PAL['sand'])

NYC, MAD2 = (200, 720), (900, 760)

def q3_4(c, lt, d, t):   # en un año, como Madrid–Nueva York
    atlantic(c, t, 1)
    k = ease(P(lt, d, 0.15, 0.85))
    pin(c, *MAD2, "MADRID", lt-0.05)
    end = dotted(c, [MAD2, (550, 600), NYC], k, PAL['yellow'])
    leo(c, end[0], end[1]-10, 0.26, "fly", "happy", t)
    pin(c, *NYC, "NUEVA YORK", lt-d*0.75, PAL['yellow'])
    stat_card(c, "EN UN AÑO", "+6.000", "km", W/2, 1130, lt-0.5, icon=ic_check, sub="≈ 5.770 km")
    post(c, t, 0.25, 0.04)

def q3_5(c, lt, d, t):   # el pequeño problema: el océano
    daysky(c); clouds(c, t, 30, n=3, y0=340, y1=600)
    sea(c, 900, t, amp=14)
    n = hops(lt, 1.0); bk = blink_k(lt, 1.0)
    x = 330+n*110
    sink = ease(P(lt, d, 0.55, 1.0))
    leo(c, x, 1030+sink*90, 0.55, "scared", "shock", t)
    sea(c, 1000, t*1.3, amp=10, col1=hexc("#2E86AB"), col2=hexc("#155E80"))
    splash(c, x, 1000, ((lt*1.0) % 1), 1.3)
    if lt > d*0.25: chip(c, "OCÉANO ATLÁNTICO", W/2, 480, lt-d*0.25, ic_drop, size=44, bg=PAL['red'], fg=C['paper'])
    post(c, t, 0.25, 0.04)
    lids(c, bk)

def stairs(c, x0, top, steps, sw=110, sh=70):
    for i in range(steps):
        x = x0+i*sw; y = top+i*sh
        c.rectangle(x, y, sw, GY-y); c.set_source_rgb(*mix(PAL['b4'], PAL['white'], 0.2*(i % 2))); c.fill()
        c.set_source_rgb(*INK); c.set_line_width(5); c.move_to(x, y); c.line_to(x+sw, y); c.line_to(x+sw, y+sh); c.stroke()

def q3_6(c, lt, d, t):   # no eliges dónde apareces: escalera
    grad_bg(c, hexc("#F6E7D0"), hexc("#EBD3B0"))
    c.rectangle(0, GY, W, H-GY); c.set_source_rgb(*hexc("#B8936C")); c.fill()
    # rellano alto a la izquierda, escalera bajando hacia la derecha
    c.rectangle(0, 700, 360, GY-700); c.set_source_rgb(*PAL['b4']); c.fill()
    c.set_source_rgb(*INK); c.set_line_width(5); c.move_to(0, 700); c.line_to(360, 700); c.stroke()
    stairs(c, 360, 770, 8)
    jump = lt > d*0.45; bk = blink_k(lt-d*0.45+0.08, 99, 0.16) if lt > d*0.45-0.08 else 0
    if not jump:
        leo(c, 290, 700, 0.6, "stand", "neutral", t)
        ground_ruler(c, 290, 700-360, 1, PX_M, PAL['red'])
        txt(c, "1 m", 290+PX_M/2, 700-380, 34, PAL['red'], "Anton")
    else:
        f = ease(P(lt, d, 0.45, 0.8))
        leo(c, 290+PX_M, 690+f*90, 0.6, "scared", "shock", t, tilt=0.25*f)
        ghost(c, 290, 700, 0.6, 0.2)
    if lt > d*0.15: chip(c, "TÚ NO ELIGES DÓNDE", 680, 560, lt-d*0.15, ic_warn, size=42, bg=PAL['yellow'])
    post(c, t, 0.3, 0.04)
    lids(c, bk)

def q3_7(c, lt, d, t):   # 0,1–0,4 s: desapareces y vuelves
    grad_bg(c, hexc("#3A4A7A"), hexc("#22305A"))
    c.rectangle(0, GY, W, H-GY); c.set_source_rgb(*PAL['walk']); c.fill()
    ph = lt % 1.4; gone = 0.5 < ph < 0.75
    # gente que no se entera
    for i, x in enumerate((140, 940)):
        leo(c, x, GY, 0.55, "phone", "neutral", t+i, hoodie=[PAL['b3'], PAL['b5']][i], facing=-1 if i else 1)
    if not gone:
        leo(c, 540, GY, 0.7, "stand", "smirk", t)
    else:
        for r in range(6):
            a = r/6*2*math.pi+t*3; circle(c, 540+math.cos(a)*90, GY-200+math.sin(a)*90, 10); c.set_source_rgb(*PAL['yellow']); c.fill()
    time_card(c, "UN PARPADEO", "0,1–0,4", "SEGUNDOS", W/2, 400, lt-0.2, col=PAL['red'])
    post(c, t, 0.25, 0.04)

def q3_8(c, lt, d, t):   # delante de una pantalla, hasta un 66 % menos
    grad_bg(c, hexc("#2B2F4A"), hexc("#1B1E33"))
    k = ease(P(lt, d, 0.25, 0.8))
    leo(c, 300, GY, 0.85, "phone", "neutral", t, look=(0.4, 0.3))
    # barras
    for i, (lab, v, col) in enumerate((("NORMAL", 1.0, PAL['line']), ("PANTALLA", 1-0.66*k, PAL['red']))):
        x = 640+i*200; h = 560*v
        rrect(c, x, GY-h, 140, h, 10); fill_stroke(c, col, 5)
        txt(c, lab, x+70, GY+50, 28, C['paper'])
    if lt > d*0.55: chip(c, "−66 %", 910, GY-560*(1-0.66*k)-60, lt-d*0.55, size=54, bg=PAL['yellow'])
    if lt > 0.2: chip(c, "PARPADEAS MENOS", W/2, 430, lt-0.2, ic_warn, size=42, bg=C['paper'])
    post(c, t, 0.35, 0.05)

def q3_9(c, lt, d, t):   # tú, ahora mismo, casi quieto
    grad_bg(c, hexc("#FFE3C2"), hexc("#F7C99A"))
    c.rectangle(0, GY, W, H-GY); c.set_source_rgb(*hexc("#B8936C")); c.fill()
    # sofá
    rrect(c, 200, GY-300, 680, 120, 30); fill_stroke(c, PAL['red'])
    rrect(c, 160, GY-200, 760, 200, 30); fill_stroke(c, mix(PAL['red'], (0, 0, 0), 0.15))
    leo(c, 540, GY-80, 0.8, "phone", "smirk", t, look=(0.3, 0.3))
    # mini teléfono con este vídeo (bucle)
    ground_ruler(c, 240, GY+40, 4, PX_M)
    x = 540+3*ease(P(lt, d, 0.2, 0.9))
    c.set_source_rgb(*PAL['red']); circle(c, x, GY+46, 14); c.fill()
    if lt > 0.3: chip(c, "TÚ, AHORA MISMO", W/2, 430, lt-0.3, ic_check, size=44, bg=PAL['yellow'])
    if lt > d*0.55: chip(c, "CASI 0 METROS", W/2, 560, lt-d*0.55, size=36, bg=C['paper'])
    post(c, t, 0.25, 0.04)

def q3_10(c, lt, d, t):  # vuelta al mundo: 6,5 años. ¿A dónde irías?
    grad_bg(c, PAL['night'], PAL['night2']); stars(c, 120, 5, t)
    k = ease(P(lt, d, 0, 0.6))
    globe(c, W/2, 860, 340, t*0.05)
    c.set_source_rgb(*PAL['yellow']); c.set_line_width(8); c.set_dash([20, 14])
    c.save(); c.translate(W/2, 860); c.scale(1, 0.32); c.arc(0, 0, 400, math.pi, math.pi+2*math.pi*k); c.restore(); c.stroke(); c.set_dash([])
    a = math.pi+2*math.pi*k
    leo(c, W/2+math.cos(a)*400, 860+math.sin(a)*400*0.32, 0.22, "fly", "happy", t)
    if lt > 0.3: chip(c, "VUELTA AL MUNDO ≈ 6,5 AÑOS", W/2, 400, lt-0.3, ic_clock, size=36, bg=PAL['yellow'])
    for i, (lab, x, y) in enumerate((("¿PARÍS?", 230, 1260), ("¿TOKIO?", 540, 1300), ("¿TU PLAYA?", 850, 1260))):
        if lt > d*0.5+i*0.4: chip(c, lab, x, y, lt-d*0.5-i*0.4, size=34, bg=[C['paper'], PAL['yellow'], C['paper']][i])
    post(c, t, 0.3, 0.05)

SCENES = {"Q3": [q3_0, q3_1, q3_2, q3_3, q3_4, q3_5, q3_6, q3_7, q3_8, q3_9, q3_10]}
BOOMS = {"Q3": [5, 8]}
CALM = set()
