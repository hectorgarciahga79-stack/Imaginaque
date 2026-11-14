from engine import *
from props import *
from scenes import FLOOR, space, daysky, clouds, street, arrow, cloud

GREEN = hexc("#2D6A4F")

def bank_app(balance, status=None, sub="Cuenta corriente"):
    def f(c, t):
        c.set_source_rgb(*hexc("#1D3557")); c.rectangle(-205, -410, 410, 220); c.fill()
        text(c, "MI BANCO", 0, -330, 46, PAL['white'], font="Montserrat", outline=0, bold=True)
        text(c, sub, 0, -250, 30, PAL['line'], font="Montserrat", outline=0)
        text(c, "Saldo", 0, -100, 36, INK, font="Montserrat", outline=0)
        text(c, balance, 0, -20, 33 if len(balance) > 12 else 60, GREEN, font="Montserrat", outline=0, bold=True)
        if status:
            col, msg = status
            rrect(c, -170, 80, 340, 110, 24); c.set_source_rgb(*col); c.fill()
            text(c, msg, 0, 150, 36, PAL['white'], font="Montserrat", outline=0, bold=True)
        for i in range(3):
            rrect(c, -170, 230+i*55, 340, 38, 12); c.set_source_rgb(0.9, 0.91, 0.95); c.fill()
    return f

def bedroom_morning(c, t):
    from props import room
    room(c)
    window(c, 780, 600, 360, 420, "day", t)

# ---------------- B1 ----------------
def b1_0(c, lt, d, t):
    if lt < d*0.5:
        bedroom_morning(c, t); bed(c, W/2, FLOOR, 1.2)
        leo(c, W/2-60, FLOOR-120, 0.85, "phone", "sleepy" if lt < d*0.25 else "neutral", t)
    else:
        k = lt-d*0.5
        grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
        phone_big(c, W/2, 980+(1-eout(k*3))*900, 1.2, bank_app("1.000.000.000,00 €"), t)

def b1_1(c, lt, d, t):
    grad_bg(c, hexc("#1B4332"), hexc("#2D6A4F"))
    zeros = int(clamp(lt/(d*0.75))*9)
    s = "1" + "0"*zeros
    groups = []
    while len(s) > 3: groups.insert(0, s[-3:]); s = s[:-3]
    groups.insert(0, s)
    text(c, ".".join(groups), W/2, 900, 140 if zeros < 7 else 118, PAL['yellow'], outline=14)
    label_tag(c, f"{zeros} CEROS", W/2, 1120, 60, PAL['white'])
    r = random.Random(1)
    for i in range(14):
        x = r.random()*W; y = (r.random()*H+t*300) % H
        c.save(); c.translate(x, y); c.rotate(t+i); rrect(c, -60, -32, 120, 64, 8); fill_stroke(c, PAL['money'], 5); c.restore()

def b1_2(c, lt, d, t):
    daysky(c); clouds(c, t); ground(c, FLOOR)
    leo(c, 200, FLOOR+20, 0.85, "think", "happy", t)
    bubble(c, 620, 800, 760, 760, lt)
    ph = int(lt/(d/3))
    c.save(); c.translate(620, 800)
    if ph == 0: villa(c, 0, 120, 0.9)
    elif ph == 1: office_quit(c, 0, 20, 1.0)
    else:
        days = "LMXJVSD"
        for i, dd in enumerate(days):
            car(c, -240+(i % 4)*160, -60+(i//4)*230, 0.42, [PAL['red'], PAL['yellow'], PAL['b3'], PAL['land'], PAL['b5'], PAL['hoodie'], hexc("#4CC9F0")][i])
            text(c, dd, -240+(i % 4)*160, 10+(i//4)*230, 44, INK, outline=0)
    c.restore()

def b1_3(c, lt, d, t):
    grad_bg(c, PAL['night'], PAL['night2'])
    leo(c, W/2, 2250, 2.1, "stand", "smirk", t)
    if lt > d*0.35: burst_text(c, "¿SEGURO?", W/2, 500, lt-d*0.35, 100, PAL['yellow'], -0.05)

def b1_4(c, lt, d, t):
    from props import room
    room(c, hexc("#E8F1F2"))
    rrect(c, -20, 1180, W+40, 60, 10); fill_stroke(c, hexc("#C99A6B"))
    leo(c, 280, FLOOR+20, 0.9, "stand", "neutral", t)
    c.save(); c.translate(480, 1150); rrect(c, -50, -90, 100, 100, 16); fill_stroke(c, PAL['white']); c.restore()
    for i in range(3):
        c.set_source_rgba(1, 1, 1, .7); c.set_line_width(6); c.new_path(); c.move_to(460+i*20, 1040); c.curve_to(440+i*20, 990, 490+i*20, 970, 470+i*20, 920); c.stroke()
    bank(c, 800, 900, 0.75, alarm=1.0 if lt > d*0.4 else 0, t=t)

def b1_5(c, lt, d, t):
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    notebook(c, W/2, 820, 920, 900, [("Ley 10/2010", PAL['red']), ("Prevención del blanqueo", INK), ("Lo raro se revisa", INK)],
             lt/d*1.15, "EN ESPAÑA")
    leo(c, 860, FLOOR+40, 0.75, "point", "worried", t, facing=-1)

def b1_6(c, lt, d, t):
    from props import room
    room(c, hexc("#DDE5F0"))
    rrect(c, 160, 700, 760, 480, 24); fill_stroke(c, hexc("#1D3557"))
    on = math.sin(t*12) > 0
    rrect(c, 200, 740, 680, 400, 16); c.set_source_rgb(*(PAL['red'] if on else hexc("#8E1B14"))); c.fill()
    text(c, "ALERTA", W/2, 900, 110, PAL['white'], outline=0)
    text(c, "+1.000.000.000 €", W/2, 1030, 64, PAL['yellow'], outline=0)
    rrect(c, 480, 1180, 120, 100, 6); fill_stroke(c, hexc("#1D3557"))
    leo(c, 860, FLOOR+30, 0.85, "scared", "shock", t, hoodie=hexc("#6C757D"), hair=hexc("#999999"))

def b1_7(c, lt, d, t):
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    st = (PAL['red'], "RECHAZADA") if lt > d*0.45 else (hexc("#4361EE"), "ENVIAR")
    phone_big(c, W/2, 1000, 1.2, bank_app("1.000.000.000,00 €", st, "Transferencia"), t)
    if lt > d*0.45: check(c, W/2+260, 620, 1.1, False)

def b1_8(c, lt, d, t):
    street(c, t)
    atm(c, 700, FLOOR, 0.9, "NO DISPONIBLE" if lt > d*0.3 else "INTRODUZCA\nTARJETA", err=lt > d*0.3, t=t)
    leo(c, 300, FLOOR+20, 0.95, "stand", "angry" if lt > d*0.3 else "neutral", t)

def lock_screen(c, t):
    c.set_source_rgb(*hexc("#1D3557")); c.paint()
    c.save(); c.translate(0, -160)
    rrect(c, -90, -40, 180, 150, 20); fill_stroke(c, PAL['yellow'], 6)
    c.new_path(); c.arc(0, -40, 60, math.pi, 0); c.set_source_rgb(*INK); c.set_line_width(22); c.stroke(); c.restore()
    text(c, "CUENTA", 0, 80, 64, PAL['white'], outline=0); text(c, "BLOQUEADA", 0, 150, 64, PAL['red'], outline=0)

def b1_9(c, lt, d, t):
    grad_bg(c, hexc("#2B2D42"), hexc("#3D405B"))
    phone_big(c, W/2, 1000, 1.2, lock_screen, t)
    if lt > d*0.45:
        notif(c, W/2, 560, 760, "Llamada perdida", "Banco · ahora", eout((lt-d*0.45)*4))

def b1_10(c, lt, d, t):
    grad_bg(c, hexc("#2B2D42"), hexc("#3D405B"))
    c.save(); shake(c, t, 10)
    def ring(c, t):
        c.set_source_rgb(*hexc("#1D3557")); c.paint()
        text(c, "BANCO", 0, -160, 80, PAL['white'], outline=0); text(c, "llamando...", 0, -80, 40, PAL['line'], font="Montserrat", outline=0)
        circle(c, -100, 250, 60); c.set_source_rgb(*PAL['red']); c.fill(); circle(c, 100, 250, 60); c.set_source_rgb(*PAL['land']); c.fill()
    phone_big(c, W/2, 1000, 1.2, ring, t, rot=math.sin(t*30)*0.03)
    c.restore()
    if lt > d*0.55: burst_text(c, "PARTE 2 →", W/2, 430, lt-d*0.55, 110, PAL['yellow'], -0.06)

# ---------------- B2 ----------------
def b2_0(c, lt, d, t):
    street(c, t)
    leo(c, 300, FLOOR+20, 1.0, "phone", "worried", t)
    if bubble(c, 680, 700, 640, 300, lt-0.2, (-1, 1), cloud_=False):
        text(c, "¿De dónde ha salido", 680, 690, 46, INK, font="Montserrat", outline=0, bold=True)
        text(c, "ese dinero?", 680, 750, 46, INK, font="Montserrat", outline=0, bold=True)

def b2_1(c, lt, d, t):
    street(c, t)
    leo(c, W/2, FLOOR+20, 1.1, "shrug", "worried", t)
    question_marks(c, W/2, 520, lt)

def door_card(c, x, y, num, label, active, t):
    c.save(); c.translate(x, y); k = 1.08 if active else 0.92; c.scale(max(k, 1e-3), max(k, 1e-3))
    rrect(c, -190, -300, 380, 600, 30); fill_stroke(c, PAL['yellow'] if active else PAL['sole'])
    text(c, num, 0, -60, 220, INK, outline=0)
    text(c, label, 0, 170, 60, INK, outline=0)
    c.restore()

def b2_2(c, lt, d, t):
    grad_bg(c, hexc("#E0FBFC"), hexc("#C2DFE3"))
    door_card(c, 290, 900, "1", "ERROR", lt > d*0.45, t)
    door_card(c, 790, 900, "2", "???", False, t)
    leo(c, W/2, FLOOR+60, 0.7, "point", "neutral", t, facing=-1)

def b2_3(c, lt, d, t):
    grad_bg(c, hexc("#E0FBFC"), hexc("#C2DFE3"))
    rrect(c, 90, 520, 900, 300, 24); fill_stroke(c, hexc("#1D3557"))
    iban = "ES12 0049 1500 05"
    wrong = lt > d*0.35
    text(c, iban + ("7" if not wrong else "8") + "1", W/2, 700, 72, PAL['white'], font="Montserrat", outline=0, bold=True)
    if wrong:
        c.set_source_rgba(*PAL['red'], .9); c.set_line_width(10); circle(c, W/2+300, 678, 50); c.stroke()
    k = clamp((lt-d*0.45)/(d*0.4))
    if k > 0:
        for i in range(5):
            x = lerp(150, 880, k)+i*-60; y = 1150+math.sin(k*6+i)*60
            c.save(); c.translate(x, y); c.rotate(k*4+i); rrect(c, -60, -32, 120, 64, 8); fill_stroke(c, PAL['money'], 5); c.restore()
    leo(c, 200, FLOOR+40, 0.6, "stand", "neutral", t, hoodie=hexc("#6C757D"))
    leo(c, 880, FLOOR+40, 0.6, "stand", "shock" if k > 0.6 else "neutral", t, facing=-1)

def b2_4(c, lt, d, t):
    street(c, t)
    leo(c, W/2, FLOOR+20, 1.0, "cheer" if lt < d*0.55 else "stand", "happy" if lt < d*0.55 else "worried", t)
    for i, (dx, col) in enumerate(((-230, PAL['red']), (230, hexc("#4CC9F0")), (-300, PAL['yellow']))):
        rrect(c, W/2+dx-70, FLOOR-260-i*40, 140, 170, 14); fill_stroke(c, col)
    if lt > d*0.55: check(c, W/2+300, 650, 1.2, False)

def b2_5(c, lt, d, t):
    grad_bg(c, hexc("#5C4033"), hexc("#3E2C23"))
    rrect(c, 140, 420, 800, 420, 24); fill_stroke(c, PAL['paper'])
    text(c, "CÓDIGO PENAL", W/2, 540, 70, PAL['red'], outline=0)
    text(c, "Apropiación indebida", W/2, 660, 56, INK, font="Montserrat", outline=0, bold=True)
    text(c, "(dinero recibido por error)", W/2, 740, 44, INK, font="Montserrat", outline=0)
    hit = abs(math.sin(lt*3)) if lt < d*0.8 else 0
    gavel(c, W/2, 1300, 1.3, hit)

def b2_6(c, lt, d, t):
    daysky(c); clouds(c, t); ground(c, FLOOR)
    leo(c, 380, FLOOR+20, 1.0, "phone", "happy", t)
    check(c, 820, 800, 1.3, True)
    label_tag(c, "NO TOCAR · AVISAR AL BANCO", W/2, 450, 46, PAL['white'])

def b2_7(c, lt, d, t):
    grad_bg(c, hexc("#E0FBFC"), hexc("#C2DFE3"))
    door_card(c, 290, 900, "1", "ERROR", False, t)
    door_card(c, 790, 900, "2", "???", True, t)
    leo(c, W/2, FLOOR+60, 0.7, "point", "neutral", t)

def b2_8(c, lt, d, t):
    c.set_source_rgb(0.05, 0.05, 0.08); c.paint()
    g = cairo.RadialGradient(W/2, 1000, 50, W/2, 1100, 600); g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.55); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
    c.set_source(g); c.paint()
    leo(c, W/2, FLOOR, 1.1, "stand", "shock", t)

def b2_9(c, lt, d, t):
    street(c, t)
    k = eout(lt/(d*0.5))
    envelope(c, W/2, 820, 1.0, 0, "NOTARÍA") if k >= 1 else envelope(c, W/2, 820+(1-k)*-900, 1.0, 0, "NOTARÍA")
    leo(c, 250, FLOOR+20, 0.85, "stand", "shock", t)

def b2_10(c, lt, d, t):
    from props import room
    room(c, hexc("#3D405B"), night=0.2)
    portrait(c, W/2, 820, 1.1, t)
    label_tag(c, "UN FAMILIAR LEJANO", W/2, 400, 54, PAL['yellow'])
    leo(c, 850, FLOOR+30, 0.75, "stand", "shock", t, facing=-1)

def b2_11(c, lt, d, t):
    daysky(c, 0.75); clouds(c, t, 200, 0.75, n=8, y0=150, y1=700)
    if int(lt*4) % 5 == 0:
        c.set_source_rgb(*PAL['yellow']); c.set_line_width(14); c.new_path(); c.move_to(700, 300); c.line_to(640, 520); c.line_to(720, 520); c.line_to(650, 760); c.stroke()
    ground(c, FLOOR, mix(PAL['ground'], (0, 0, 0), .5), mix(PAL['ground_d'], (0, 0, 0), .5))
    leo(c, W/2, FLOOR+20, 1.0, "stand", "worried", t, look=(0.3, -1))
    if lt > d*0.55: burst_text(c, "PARTE 3 →", W/2, 430, lt-d*0.55, 110, PAL['yellow'], -0.06)

# ---------------- B3 ----------------
def b3_0(c, lt, d, t):
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    money_pile(c, W/2, FLOOR-40, 1.3)
    leo(c, W/2, FLOOR-440, 0.8, "cheer", "happy", t)
    label_tag(c, "LEGAL · TUYA", W/2, 420, 60, PAL['white'])

def b3_1(c, lt, d, t):
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    money_pile(c, 300, FLOOR, 0.9)
    k = eout(lt/(d*0.6))
    c.save(); c.translate(1500-k*720, 0)
    rrect(c, -300, 500, 600, 1060, 20); fill_stroke(c, hexc("#6C757D"))
    text(c, "HACIENDA", 0, 640, 84, PAL['white'], outline=10)
    for ex in (-120, 120):
        circle(c, ex, 820, 60); fill_stroke(c, PAL['white']); circle(c, ex-15, 830, 24); c.set_source_rgb(*INK); c.fill()
    c.restore()
    leo(c, 300, FLOOR-300, 0.6, "stand", "worried", t)

def b3_2(c, lt, d, t):
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    notebook(c, W/2, 820, 920, 900, [("Impuesto de Sucesiones", PAL['red']), ("Depende de:", INK), ("· el parentesco", INK), ("· la comunidad autónoma", INK)],
             lt/d*1.15, "HERENCIAS")
    leo(c, 860, FLOOR+40, 0.75, "think", "neutral", t, facing=-1)

def b3_3(c, lt, d, t):
    daysky(c); ground(c, FLOOR)
    leo(c, 300, FLOOR+20, 0.9, "stand", "happy", t, hoodie=hexc("#6C757D"), hair=hexc("#AAAAAA"))
    leo(c, 700, FLOOR+20, 0.8, "stand", "happy", t, facing=-1)
    c.set_source_rgb(*INK); c.set_line_width(10); c.move_to(380, 900); c.curve_to(450, 800, 560, 800, 640, 900); c.stroke()
    check(c, W/2, 640, 1.0, True)
    label_tag(c, "HIJO O PAREJA: MUY POCO", W/2, 420, 48, PAL['white'])

def b3_4(c, lt, d, t):
    grad_bg(c, hexc("#E0FBFC"), hexc("#C2DFE3"))
    k = eout(lt/(d*0.7))
    cx, cy, r = W/2, 900, 340
    circle(c, cx, cy, r); fill_stroke(c, PAL['money'], 8)
    c.new_path(); c.move_to(cx, cy); c.arc(cx, cy, r, -math.pi/2, -math.pi/2+2*math.pi*0.80*k); c.close_path(); fill_stroke(c, PAL['red'], 8)
    text(c, f"+{int(80*k)}%", cx, cy+40, 150, PAL['white'], outline=14)
    label_tag(c, "PARIENTE LEJANO · TARIFA ESTATAL", W/2, 420, 42, PAL['white'])
    text(c, "HACIENDA", cx+260, cy+400, 60, PAL['red'], outline=8)

def b3_5(c, lt, d, t):
    grad_bg(c, hexc("#E0FBFC"), hexc("#C2DFE3"))
    m = min(6, 1+int(lt/(d*0.8)*6))
    calendar(c, W/2, 900, 1.4, f"{m} MES" + ("ES" if m > 1 else ""), "PLAZO")
    leo(c, 860, FLOOR+40, 0.75, "stand", "worried", t, facing=-1)

def b3_6(c, lt, d, t):
    street(c, t, cspeed=20)
    ph = lt/(d/3)
    if ph > 0: c.save(); c.translate(0, -(1-eout(ph*2))*-400); factory(c, 260, 1100, 1.2); c.restore()
    if ph > 1: label_tag(c, "EDIFICIOS", 760, 560, 50, PAL['white'])
    if ph > 2: debt_paper(c, 760, 1000, 1.0+0.1*math.sin(t*6), 0.1)
    label_tag(c, "EMPRESAS", 260, 560, 50, PAL['white'])

def b3_7(c, lt, d, t):
    street(c, t)
    leo(c, W/2, FLOOR+20, 1.0, "scared", "worried", t)
    for i in range(4):
        k = clamp(lt/d*2-i*0.3)
        if k > 0: debt_paper(c, W/2-300+i*200, 500+k*500+(i % 2)*80, 0.55, (i-1.5)*0.4+k)

def b3_8(c, lt, d, t):
    grad_bg(c, hexc("#2B2D42"), hexc("#3D405B"))
    def screen(c, t): c.set_source_rgb(*hexc("#E9ECEF")); c.paint()
    phone_big(c, W/2, 1000, 1.25, screen, t)
    msgs = [("Primo Javi", "¡Cuánto tiempo! 😊"), ("Tía Carmen", "¿Quedamos a comer?"), ("Ex compañero", "Tengo un negocio..."), ("Número desconocido", "Hola, ¿te acuerdas?")]
    msgs = [(a, b.replace(" 😊", "")) for a, b in msgs]
    for i, (a, b) in enumerate(msgs):
        k = eout((lt-i*d*0.2)*4)
        if k > 0: notif(c, W/2, 560+i*190, 820, a, b, k)

def b3_9(c, lt, d, t):
    daysky(c, 0.1); clouds(c, t); ground(c, FLOOR)
    signpost(c, W/2, FLOOR, [("ACEPTAR", PAL['land'], 1), ("CON CUIDADO", PAL['yellow'], -1), ("RENUNCIAR", PAL['red'], 1)], lt)
    leo(c, 180, FLOOR+20, 0.8, "think", "worried", t)

def b3_10(c, lt, d, t):
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    leo(c, W/2, 2250, 2.1, "point", "smirk", t)
    if lt > d*0.4: burst_text(c, "¿TÚ QUÉ HARÍAS?", W/2, 450, lt-d*0.4, 84, PAL['yellow'], -0.05)

SCENES = {
 "B1": [b1_0, b1_1, b1_2, b1_3, b1_4, b1_5, b1_6, b1_7, b1_8, b1_9, b1_10],
 "B2": [b2_0, b2_1, b2_2, b2_3, b2_4, b2_5, b2_6, b2_7, b2_8, b2_9, b2_10, b2_11],
 "B3": [b3_0, b3_1, b3_2, b3_3, b3_4, b3_5, b3_6, b3_7, b3_8, b3_9, b3_10],
}
BOOMS = {"B1": [0, 7, 10], "B2": [5, 9], "B3": [1, 4]}
