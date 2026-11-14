from engine import *
from props import *
from scenes import FLOOR, space, daysky, clouds, street, arrow, big_wave, cloud

# ---------------- A2 ----------------
def a2_0(c, lt, d, t):  # frena poco a poco durante años
    space(c, t)
    rot = 0.6*(1-math.exp(-lt*0.9))
    globe(c, W/2, 1050, 340, rot)
    leo(c, W/2-40, 1050-330, 0.36, "stand", "happy" if lt > d*0.6 else "neutral", t, tilt=-0.1)
    label_tag(c, "FRENA DURANTE AÑOS", W/2, 420, 56, PAL['yellow'])

def a2_1(c, lt, d, t):  # problema resuelto? pues no
    daysky(c); clouds(c, t); ground(c, FLOOR)
    if lt < d*0.5:
        leo(c, W/2, FLOOR+10, 1.1, "cheer", "happy", t)
    else:
        leo(c, W/2, FLOOR+10, 1.1, "scared", "shock", t)
        burst_text(c, "¡NO!", 780, 600, lt-d*0.5, 130, PAL['red'], 0.12)

def a2_2(c, lt, d, t):  # un día dura un año
    grad_bg(c, hexc("#FFE3A3"), hexc("#F7C873"))
    calendar(c, 300, 760, 1.0, "24 h", "1 DÍA HOY")
    if lt > d*0.3:
        c.set_source_rgb(*PAL['red']); c.set_line_width(22)
        k = clamp((lt-d*0.3)/0.3)
        c.move_to(130, 600); c.line_to(130+340*k, 600+340*k); c.stroke()
    if lt > d*0.45:
        k = back((lt-d*0.45)*3)
        c.save(); c.translate(760, 1000); c.scale(max(k, 1e-3), max(k, 1e-3)); calendar(c, 0, 0, 1.1, "1 AÑO", "1 DÍA SIN GIRO"); c.restore()
    leo(c, 230, FLOOR+30, 0.75, "point", "shock", t, facing=1)

def a2_3(c, lt, d, t):  # 6 meses sol, 6 noche
    c.save(); c.rectangle(0, 0, W/2, H); c.clip(); daysky(c); sun(c, W/4, 650, 110, t); ground(c, FLOOR, PAL['sand'], PAL['sand_d']); c.restore()
    c.save(); c.rectangle(W/2, 0, W/2, H); c.clip(); grad_bg(c, PAL['night'], PAL['night2']); stars(c, 60, 2, t); moon(c, W*0.75, 650, 90); ground(c, FLOOR, PAL['snow'], PAL['ice']); c.restore()
    c.set_source_rgb(*INK); c.set_line_width(10); c.move_to(W/2, 0); c.line_to(W/2, H); c.stroke()
    label_tag(c, "6 MESES DE SOL", W/4, 960, 44, PAL['yellow'])
    if lt > d*0.45: label_tag(c, "6 MESES DE NOCHE", W*0.75, 960, 44, PAL['line'])
    leo(c, W/4, FLOOR+20, 0.6, "stand", "happy", t)
    if lt > d*0.45: leo(c, W*0.75, FLOOR+20, 0.6, "stand", "worried", t, facing=-1)

def a2_4(c, lt, d, t):  # cara iluminada, se calienta
    grad_bg(c, hexc("#FF8C42"), hexc("#FFD166"))
    sun(c, W/2, 520, 180+20*math.sin(t*2), t)
    heat_waves(c, t, 800, FLOOR)
    ground(c, FLOOR-80, PAL['sand'], PAL['sand_d'])
    c.set_source_rgb(*PAL['sand_d']); c.set_line_width(8)
    for i in range(7):
        x = 60+i*150; c.move_to(x, FLOOR-60); c.line_to(x+40, FLOOR+20); c.line_to(x+10, FLOOR+120); c.stroke()
    thermometer(c, 900, 1250, 0.9, 0.3+0.7*eout(lt/d), t)
    leo(c, 420, FLOOR-60, 0.95, "stand", "worried", t)

def a2_5(c, lt, d, t):  # cara oscura, se congela
    grad_bg(c, PAL['night'], hexc("#33507A")); stars(c, 80, 9, t); moon(c, 820, 450, 90)
    ground(c, FLOOR-80, PAL['snow'], PAL['ice'])
    for i, x in enumerate((140, 960)):
        c.new_path(); c.move_to(x-120, FLOOR-80); c.line_to(x, FLOOR-80-300-i*80); c.line_to(x+120, FLOOR-80); c.close_path(); fill_stroke(c, PAL['ice'])
    snowflakes(c, t)
    k = clamp(lt/d)
    leo(c, W/2, FLOOR-60, 0.95, "scared", "scared", t, hoodie=mix(PAL['hoodie'], PAL['ice'], k*0.6))

def a2_6(c, lt, d, t):  # plantas y animales locos
    daysky(c, 0.2); ground(c, FLOOR)
    for i, x in enumerate((120, 300, 480, 660, 840, 980)):
        flower(c, x, FLOOR, 1.1, droop=math.sin(t*3+i)*0.8, col=[PAL['red'], PAL['yellow'], PAL['b5']][i % 3])
    for i in range(5):
        a = t*2.5+i*1.25
        bird(c, W/2+math.cos(a)*300, 650+math.sin(a)*170, 1.0, flap=t*12+i)
    question_marks(c, W/2, 380, lt)

def a2_7(c, lt, d, t):  # tu cuerpo no entendería nada
    room(c, night=0.3)
    window(c, 300, 620, 380, 440, "day" if int(t*1.5) % 2 == 0 else "night", t)
    c.save(); c.translate(800, 560); circle(c, 0, 0, 150); fill_stroke(c, PAL['white'])
    for h in range(12):
        a = h*math.pi/6; c.set_source_rgb(*INK); circle(c, math.cos(a)*120, math.sin(a)*120, 8); c.fill()
    c.set_line_width(12); c.move_to(0, 0); c.line_to(math.cos(t*8)*100, math.sin(t*8)*100); c.stroke()
    c.set_line_width(16); c.move_to(0, 0); c.line_to(math.cos(t*1.5)*70, math.sin(t*1.5)*70); c.stroke(); c.restore()
    c.save(); c.translate(W/2+70, FLOOR-205); c.rotate(-math.pi/2); leo(c, 0, 0, 0.5, "stand", "sleepy" if lt < d*0.5 else "worried", t); c.restore()
    bed(c, W/2, FLOOR, 1.2)
    if lt > d*0.5: question_marks(c, W/2, 1000, lt-d*0.5)

def a2_8(c, lt, d, t):  # vivir en la frontera día/noche
    c.save(); c.rectangle(0, 0, W/2, H); c.clip(); grad_bg(c, hexc("#FF9A5A"), hexc("#FFD59A")); c.restore()
    c.save(); c.rectangle(W/2, 0, W/2, H); c.clip(); grad_bg(c, PAL['night'], PAL['night2']); stars(c, 50, 4, t); c.restore()
    g = cairo.LinearGradient(W/2-200, 0, W/2+200, 0); g.add_color_stop_rgba(0, 1, 0.6, 0.35, 0); g.add_color_stop_rgba(0.5, 0.6, 0.4, 0.6, 0.6); g.add_color_stop_rgba(1, 0.1, 0.1, 0.3, 0)
    c.set_source(g); c.rectangle(W/2-200, 0, 400, H); c.fill()
    sun(c, 120, 800, 90, t)
    ground(c, FLOOR, hexc("#B88A6A"), hexc("#9C7052"))
    cols = [PAL['hoodie'], hexc("#4CC9F0"), hexc("#B5179E"), hexc("#80B918"), hexc("#F72585")]
    for i in range(5):
        x = W/2-260+i*130+((t*60) % 130)
        leo(c, x, FLOOR+15+(i % 2)*25, 0.45, "stand", "neutral", t+i, walk=t*1.4+i*0.3, hoodie=cols[i], facing=1)
    label_tag(c, "LA FRONTERA DÍA / NOCHE", W/2, 450, 50, PAL['white'])
    arrow(c, W/2, 560, 420, lt, PAL['yellow'], 44)

def a2_9(c, lt, d, t):  # nómada otra vez
    grad_bg(c, hexc("#7B2CBF"), hexc("#FF9E00"))
    sun(c, W/2, FLOOR-60, 150, 0, hexc("#FF6D00"))
    c.new_path(); c.move_to(-50, FLOOR-40)
    for x in range(-50, W+60, 60): c.line_to(x, FLOOR-40-60*math.sin(x/200))
    c.line_to(W+50, H); c.line_to(-50, H); c.close_path(); fill_stroke(c, hexc("#3C1642"))
    for i in range(7):
        x = 100+i*140+t*25
        leo(c, x % (W+100)-50, FLOOR-30-60*math.sin(((x % (W+100))-50)/200), 0.3, "stand", "neutral", t+i, walk=t*1.3+i*0.2, hoodie=INK, hair=INK, skin=INK)
    label_tag(c, "NÓMADAS OTRA VEZ", W/2, 450, 56, PAL['yellow'])

def a2_10(c, lt, d, t):  # ni siquiera eso es lo más loco
    space(c, t)
    leo(c, W/2, 2250, 2.1, "stand", "smirk", t, look=(-0.3, 0))

def a2_11(c, lt, d, t):  # el océano se movería... parte 3
    daysky(c, 0.1)
    c.rectangle(0, 900, W, H); c.set_source_rgb(*PAL['sea']); c.fill()
    for i in range(12):
        y = 950+i*80; c.set_source_rgba(1, 1, 1, .5); c.set_line_width(8)
        c.new_path()
        for x in range(0, W+40, 40): c.line_to(x, y+12*math.sin(x/80+t*3+i))
        c.stroke()
    k = eout(lt/(d*0.6))
    c.save(); c.translate(W/2, 1300); c.rotate(-math.pi/2); arrow(c, 0+k*80, 0, 360, lt, PAL['yellow'], 50); c.restore()
    c.save(); c.translate(W/2, 1300); c.rotate(math.pi/2); arrow(c, 0+k*80, 0, 360, lt, PAL['yellow'], 50); c.restore()
    question_marks(c, W/2, 700, lt, 1)
    if lt > d*0.62: burst_text(c, "PARTE 3 →", W/2, 450, lt-d*0.62, 110, PAL['yellow'], -0.06)

# ---------------- A3 ----------------
def squashed_globe(c, x, y, r, squash, t, rot=0.0, **kw):
    c.save(); c.translate(x, y); c.scale(1+squash, 1-squash); globe(c, 0, 0, r, rot, **kw); c.restore()

def a3_0(c, lt, d, t):  # no es una bola perfecta
    space(c, t)
    sq = 0.08*eout(lt/(d*0.7))
    squashed_globe(c, W/2, 950, 360, sq, t, t*0.1)
    c.set_dash([20, 16]); c.set_source_rgba(1, 1, 1, .8); c.set_line_width(5); circle(c, W/2, 950, 360); c.stroke(); c.set_dash([])
    label_tag(c, "UN POCO ACHATADA", W/2, 420, 56, PAL['yellow'])

def a3_1(c, lt, d, t):  # +21 km en el ecuador
    space(c, t)
    squashed_globe(c, W/2, 950, 340, 0.08, t, t*0.1)
    c.set_source_rgb(*PAL['yellow']); c.set_line_width(8); c.set_dash([26, 14]); c.move_to(W/2-400, 950); c.line_to(W/2+400, 950); c.stroke(); c.set_dash([])
    k = 0.5+0.5*math.sin(lt*5)
    arrow(c, W/2+430+k*20, 950, 160, lt, PAL['yellow'], 40)
    c.save(); c.translate(W/2-430-k*20, 950); c.rotate(math.pi); arrow(c, 0, 0, 160, lt, PAL['yellow'], 40); c.restore()
    burst_text(c, "+21 km", W/2, 470, lt-0.3, 100, PAL['yellow'], -0.05)

def a3_2(c, lt, d, t):  # barriga de agua
    space(c, t)
    squashed_globe(c, W/2, 950, 340, 0.08, t, t*0.1)
    c.save(); c.translate(W/2, 950); c.scale(1.08, 0.92); c.new_path(); c.arc(0, 0, 336, 0, 2*math.pi); c.clip()
    c.rectangle(-400, -60-10*math.sin(lt*4), 800, 120+20*math.sin(lt*4)); c.set_source_rgba(*PAL['sea_d'], 0.9); c.fill(); c.restore()
    label_tag(c, "AQUÍ SE ACUMULA EL AGUA", W/2, 420, 50, PAL['white'])
    leo(c, 200, FLOOR+30, 0.7, "point", "smirk", t)

def a3_3(c, lt, d, t):  # el agua se va a los polos
    space(c, t)
    k = eout(lt/d)
    squashed_globe(c, W/2, 950, 340, 0.08*(1-k), t, 0.3)
    for sgn in (-1, 1):
        c.save(); c.translate(W/2, 950+sgn*(120+k*120)); c.rotate(sgn*math.pi/2); arrow(c, 0, 0, 200, lt, PAL['sea'], 50); c.restore()
    label_tag(c, "EL AGUA SE VA A LOS POLOS", W/2, 420, 48, PAL['yellow'])

def a3_4(c, lt, d, t):  # dos océanos gigantes
    space(c, t)
    globe(c, W/2, 950, 360, 0.3, oceans_to_poles=eout(lt/(d*0.6)))
    if lt > d*0.4: label_tag(c, "OCÉANO NORTE", W/2, 520, 50, PAL['line'])
    if lt > d*0.7: label_tag(c, "OCÉANO SUR", W/2, 1325, 50, PAL['line'])
    label_tag(c, "SIMULACIÓN", 200, 330, 40, PAL['white'])

def a3_5(c, lt, d, t):  # supercontinente
    space(c, t)
    globe(c, W/2, 950, 360, 0.3, oceans_to_poles=1)
    pulse = 0.5+0.5*math.sin(lt*6)
    c.set_source_rgba(*PAL['yellow'], 0.35+0.3*pulse); rrect(c, W/2-380, 950-170, 760, 340, 40); c.set_line_width(14); c.stroke()
    burst_text(c, "1 SOLO CONTINENTE", W/2, 450, lt, 76, PAL['yellow'], -0.04)

def a3_6(c, lt, d, t):  # fondo marino -> tierra seca
    daysky(c, 0.05); ground(c, FLOOR-150, PAL['sand'], PAL['sand_d'])
    c.save(); c.translate(760, FLOOR-130); c.rotate(-0.25)
    c.new_path(); c.move_to(-260, -120); c.line_to(260, -120); c.line_to(190, 40); c.line_to(-200, 40); c.close_path(); fill_stroke(c, PAL['red'])
    rrect(c, -80, -260, 160, 140, 10); fill_stroke(c, PAL['white']); c.restore()
    for i, x in enumerate((180, 420)):
        c.save(); c.translate(x, FLOOR-60); c.set_source_rgb(*INK); c.set_line_width(8)
        c.move_to(-60, 0); c.line_to(60, 0); c.stroke()
        for k in range(4): c.move_to(-40+k*28, -24); c.line_to(-40+k*28, 24); c.stroke()
        c.new_path(); c.move_to(60, 0); c.line_to(100, -30); c.line_to(100, 30); c.close_path(); c.stroke(); c.restore()
    leo(c, 300+lt*60, FLOOR-130, 0.9, "stand", "shock", t, walk=lt*1.2)
    label_tag(c, "ANTES: FONDO DEL MAR", W/2, 450, 52, PAL['white'])

def a3_7(c, lt, d, t):  # norte de Europa y Canadá bajo el agua
    daysky(c, 0.4); clouds(c, t, 60, 0.4)
    city(c, FLOOR, t, 0, 0, lit=0.4, scale=0.9, dark=0.3)
    lvl = FLOOR-80-eout(lt/d)*520
    c.rectangle(-50, lvl, W+100, H); c.set_source_rgba(*PAL['sea'], 0.92); c.fill()
    c.set_source_rgb(1, 1, 1); c.set_line_width(8); c.new_path()
    for x in range(-50, W+60, 40): c.line_to(x, lvl+10*math.sin(x/70+t*3))
    c.stroke()
    label_tag(c, "NORTE DE EUROPA · CANADÁ", W/2, 450, 48, PAL['white'])

def a3_8(c, lt, d, t):  # campo magnético
    space(c, t)
    sun(c, 110, 380, 110, t)
    fade = 1-0.7*eout(lt/d)
    c.set_line_width(8)
    for k in range(1, 5):
        c.set_source_rgba(0.55, 0.85, 1, fade*0.8)
        for sgn in (-1, 1):
            c.save(); c.translate(W/2, 1000); c.scale(sgn, 1); c.new_path(); c.move_to(0, -300)
            c.curve_to(200*k, -420-k*40, 200*k, 420+k*40, 0, 300); c.stroke(); c.restore()
    globe(c, W/2, 1000, 260, 0.3, oceans_to_poles=1)
    c.set_source_rgba(1, 0.85, 0.2, 0.9); c.set_line_width(10)
    r = random.Random(2)
    for i in range(10):
        y0 = 380+r.random()*250; ph = (lt*1.3+r.random()) % 1
        x = 230+ph*(W/2-120); c.move_to(x, y0+ph*500); c.line_to(x+80, y0+ph*500+50); c.stroke()
    label_tag(c, "HIPÓTESIS", W/2, 1580, 44, PAL['yellow'])

def a3_9(c, lt, d, t):  # ya no sería nuestro planeta
    space(c, t)
    globe(c, W/2, 1150, 420, 0.3, oceans_to_poles=1, terminator=0.0)
    leo(c, W/2-60, 1150-410, 0.4, "sit", "worried", t, look=(0.5, -1))

def a3_10(c, lt, d, t):  # día eterno o noche eterna
    c.save(); c.rectangle(0, 0, W/2, H); c.clip(); daysky(c); sun(c, W/4, 600, 110, t); ground(c, FLOOR, PAL['sand'], PAL['sand_d']); c.restore()
    c.save(); c.rectangle(W/2, 0, W/2, H); c.clip(); grad_bg(c, PAL['night'], PAL['night2']); stars(c, 60, 2, t); moon(c, W*0.75, 600, 90); ground(c, FLOOR, PAL['snow'], PAL['ice']); c.restore()
    c.set_source_rgb(*INK); c.set_line_width(10); c.move_to(W/2, 0); c.line_to(W/2, H); c.stroke()
    leo(c, W/2, FLOOR+20, 1.0, "shrug", "worried", t)
    label_tag(c, "DÍA ETERNO", W/4, 950, 46, PAL['yellow'])
    label_tag(c, "NOCHE ETERNA", W*0.75, 950, 46, PAL['line'])
    if lt > d*0.6: burst_text(c, "¿CUÁL ELIGES?", W/2, 430, lt-d*0.6, 80, PAL['yellow'], -0.05)

SCENES = {
 "A2": [a2_0, a2_1, a2_2, a2_3, a2_4, a2_5, a2_6, a2_7, a2_8, a2_9, a2_10, a2_11],
 "A3": [a3_0, a3_1, a3_2, a3_3, a3_4, a3_5, a3_6, a3_7, a3_8, a3_9, a3_10],
}
BOOMS = {"A2": [1, 11], "A3": [4, 8]}
