from engine import *

def bed(c, x, y, s=1, blanket=None):
    blanket = blanket or hexc("#6C8CD5")
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -330, -260, 40, 260, 10); fill_stroke(c, (0.55, 0.35, 0.22))
    rrect(c, -330, -120, 660, 90, 16); fill_stroke(c, (0.65, 0.42, 0.27))
    rrect(c, -300, -170, 180, 70, 30); fill_stroke(c, PAL['white'])
    rrect(c, -150, -190, 470, 90, 30); fill_stroke(c, blanket)
    rrect(c, 290, -180, 40, 180, 10); fill_stroke(c, (0.55, 0.35, 0.22))
    c.restore()

def window(c, x, y, w, h, scene="day", t=0):
    rrect(c, x-w/2, y-h/2, w, h, 12)
    if scene == "day":
        c.set_source_rgb(*PAL['sky']); c.fill_preserve()
    else:
        c.set_source_rgb(*PAL['night']); c.fill_preserve()
    c.save(); c.clip()
    if scene == "day": sun(c, x+w*0.15, y-h*0.1, 50, t)
    else: moon(c, x+w*0.15, y-h*0.1, 45)
    c.restore()
    rrect(c, x-w/2, y-h/2, w, h, 12); c.set_source_rgb(*INK); c.set_line_width(LW+8); c.stroke()
    c.set_source_rgb(1, 1, 1); c.set_line_width(14); c.move_to(x, y-h/2); c.line_to(x, y+h/2); c.move_to(x-w/2, y); c.line_to(x+w/2, y); c.stroke()

def room(c, wall=None, floor_y=1560, night=0.0):
    wall = wall or hexc("#F6E7D2")
    c.set_source_rgb(*mix(wall, (0.1, 0.12, 0.25), night)); c.paint()
    c.rectangle(-50, floor_y, W+100, H); c.set_source_rgb(*mix(hexc("#C99A6B"), (0.1, 0.1, 0.2), night)); c.fill()
    c.set_source_rgb(*INK); c.set_line_width(LW); c.move_to(-50, floor_y); c.line_to(W+50, floor_y); c.stroke()

def bubble(c, x, y, w, h, t, tail=(0, 1), cloud_=True):
    k = back(t*3)
    if k <= 0: return False
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    if cloud_:
        c.new_path()
        n = 12
        for i in range(n):
            a = i/n*2*math.pi
            c.new_sub_path(); c.arc(math.cos(a)*w/2*0.85, math.sin(a)*h/2*0.85, min(w, h)*0.22, 0, 2*math.pi)
        c.new_sub_path(); c.save(); c.scale(w/2*0.9, h/2*0.9); c.arc(0, 0, 1, 0, 2*math.pi); c.restore()
        c.set_source_rgb(*INK); c.set_line_width(LW*2.2); c.stroke_preserve(); c.set_source_rgb(1, 1, 1); c.fill()
        for i, r in enumerate((26, 16)):
            circle(c, tail[0]*(w*0.3+i*50), h/2+30+i*45, r); fill_stroke(c, PAL['white'], 6)
    else:
        rrect(c, -w/2, -h/2, w, h, 40); fill_stroke(c, PAL['white'])
        c.new_path(); c.move_to(-30, h/2-4); c.line_to(tail[0]*60, h/2+70); c.line_to(30, h/2-4); c.close_path(); fill_stroke(c, PAL['white'])
        rrect(c, -w/2+6, h/2-30, w-12, 26, 10); c.set_source_rgb(1, 1, 1); c.fill()
    c.restore(); return True

def villa(c, x, y, s=1):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -260, -220, 520, 220, 10); fill_stroke(c, PAL['white'])
    rrect(c, -300, -250, 600, 40, 10); fill_stroke(c, hexc("#E07A5F"))
    rrect(c, -200, -170, 160, 110, 8); fill_stroke(c, PAL['sky2'], 6); rrect(c, 40, -170, 160, 110, 8); fill_stroke(c, PAL['sky2'], 6)
    rrect(c, -330, -10, 660, 60, 20); fill_stroke(c, hexc("#4CC9F0"))
    tree(c, 330, 0, 0.5); c.restore()

def office_quit(c, x, y, s=1):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -150, -200, 300, 380, 12); fill_stroke(c, PAL['paper'])
    text(c, "DIMISIÓN", 0, -110, 64, PAL['red'], outline=0)
    for i in range(5):
        c.set_source_rgb(0.6, 0.6, 0.65); c.rectangle(-110, -50+i*45, 220-(i % 2)*60, 14); c.fill()
    c.restore()

def bank(c, x, y, s=1, alarm=0.0, t=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.new_path(); c.move_to(-320, -460); c.line_to(0, -620); c.line_to(320, -460); c.close_path(); fill_stroke(c, PAL['b4'])
    rrect(c, -330, -470, 660, 50, 8); fill_stroke(c, PAL['white'])
    for i in range(5):
        rrect(c, -270+i*120, -410, 60, 360, 10); fill_stroke(c, PAL['white'])
    rrect(c, -340, -60, 680, 60, 8); fill_stroke(c, PAL['b4'])
    text(c, "BANCO", 0, -495+40, 58, INK, outline=0)
    if alarm > 0:
        on = math.sin(t*14) > 0
        circle(c, 0, -660, 46); fill_stroke(c, PAL['red'] if on else hexc("#8E1B14"))
        if on:
            c.set_source_rgba(1, 0.2, 0.2, 0.35*alarm); circle(c, 0, -660, 140); c.fill()
    c.restore()

def atm(c, x, y, s=1, screen_txt="", err=False, t=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -230, -900, 460, 900, 30); fill_stroke(c, hexc("#4A6FA5"))
    rrect(c, -180, -820, 360, 280, 18); fill_stroke(c, PAL['red'] if err and math.sin(t*10) > 0 else hexc("#1D3557"), 6)
    for i, line in enumerate(screen_txt.split("\n")):
        text(c, line, 0, -720+i*70, 54, PAL['white'], outline=0)
    for i in range(3):
        for j in range(3):
            rrect(c, -120+j*85, -470+i*85, 70, 65, 10); fill_stroke(c, PAL['sole'], 5)
    rrect(c, -150, -170, 300, 30, 10); fill_stroke(c, INK, 4)
    c.restore()

def gavel(c, x, y, s=1, hit=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -220, 40, 440, 70, 20); fill_stroke(c, (0.5, 0.3, 0.18))
    c.save(); c.translate(80, 20); c.rotate(-0.9+hit*0.9)
    rrect(c, -20, -330, 40, 330, 14); fill_stroke(c, (0.62, 0.4, 0.24))
    rrect(c, -120, -400, 240, 110, 30); fill_stroke(c, (0.55, 0.33, 0.2))
    c.restore(); c.restore()

def envelope(c, x, y, s=1, opened=0.0, seal="NOTARÍA"):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -300, -190, 600, 380, 16); fill_stroke(c, hexc("#F1E3C6"))
    c.new_path(); c.move_to(-300, -190); c.line_to(0, -190+250*(1-2*opened)); c.line_to(300, -190); c.set_source_rgb(*INK); c.set_line_width(LW); c.stroke()
    circle(c, 0, 40, 70); fill_stroke(c, PAL['red'])
    text(c, seal, 0, 190+70, 52, INK, font="Montserrat", outline=0, bold=True)
    c.restore()

def portrait(c, x, y, s=1, t=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -230, -300, 460, 600, 20); fill_stroke(c, hexc("#C8A24A"))
    rrect(c, -180, -250, 360, 500, 10); fill_stroke(c, hexc("#3D405B"), 5)
    circle(c, 0, -60, 100); c.set_source_rgb(0.12, 0.12, 0.16); c.fill()
    c.new_path(); c.move_to(-170, 250); c.curve_to(-160, 60, 160, 60, 170, 250); c.close_path(); c.fill()
    text(c, "?", 0, -20, 160, PAL['yellow'], outline=10)
    c.restore()

def signpost(c, x, base, labels, t):
    rrect(c, x-18, base-900, 36, 900, 10); fill_stroke(c, (0.55, 0.35, 0.22))
    for i, (s, col, d) in enumerate(labels):
        k = back((t-i*0.35)*3)
        if k <= 0: continue
        c.save(); c.translate(x, base-820+i*190); c.scale(max(k, 1e-3), max(k, 1e-3))
        w = 520
        c.new_path()
        if d > 0: c.move_to(-40, -70); c.line_to(w-60, -70); c.line_to(w, 0); c.line_to(w-60, 70); c.line_to(-40, 70)
        else: c.move_to(40, -70); c.line_to(-w+60, -70); c.line_to(-w, 0); c.line_to(-w+60, 70); c.line_to(40, 70)
        c.close_path(); fill_stroke(c, col, 8)
        text(c, s, (w/2-30)*d, 22, 50, INK, font="Montserrat", outline=0, bold=True)
        c.restore()

def snowflakes(c, t, n=60, seed=4):
    r = random.Random(seed)
    for i in range(n):
        x = (r.random()*W + math.sin(t+i)*40) % W; y = (r.random()*H + t*(90+r.random()*120)) % H
        circle(c, x, y, r.uniform(5, 12)); c.set_source_rgba(1, 1, 1, 0.9); c.fill()

def heat_waves(c, t, y0, y1):
    c.set_source_rgba(1, 1, 1, 0.35); c.set_line_width(6)
    for i in range(8):
        x = 80+i*130
        c.new_path()
        for k in range(30):
            yy = y1-k*(y1-y0)/30; c.line_to(x+math.sin(k*0.6+t*5+i)*18, yy)
        c.stroke()

def thermometer(c, x, y, s, level, t=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -40, -400, 80, 420, 40); fill_stroke(c, PAL['white'])
    circle(c, 0, 40, 70); fill_stroke(c, PAL['red'])
    h = 380*clamp(level); rrect(c, -20, 20-h, 40, h, 20); c.set_source_rgb(*PAL['red']); c.fill()
    c.restore()

def bird(c, x, y, s=1, flap=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.new_path(); c.move_to(-60, -20*math.sin(flap)); c.curve_to(-30, -40, -10, -20, 0, 0); c.curve_to(10, -20, 30, -40, 60, -20*math.sin(flap))
    c.set_source_rgb(*INK); c.set_line_width(10); c.stroke(); c.restore()

def flower(c, x, base, s=1, droop=0.0, col=None):
    col = col or PAL['red']
    c.save(); c.translate(x, base); c.scale(s, s)
    c.new_path(); c.move_to(0, 0); c.curve_to(0, -100, droop*120, -160, droop*160, -200+droop*80); c.set_source_rgb(*PAL['land_d']); c.set_line_width(12); c.stroke()
    cx, cy = droop*160, -200+droop*80
    for i in range(6):
        a = i*math.pi/3; circle(c, cx+math.cos(a)*34, cy+math.sin(a)*34, 26); fill_stroke(c, col, 5)
    circle(c, cx, cy, 22); fill_stroke(c, PAL['yellow'], 5); c.restore()

def calendar(c, x, y, s, label, sub="", flip=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -200, -220, 400, 440, 30); fill_stroke(c, PAL['white'])
    c.save(); rrect(c, -200, -220, 400, 120, 30); c.clip(); c.set_source_rgb(*PAL['red']); c.paint(); c.restore()
    rrect(c, -200, -220, 400, 440, 30); c.set_source_rgb(*INK); c.set_line_width(LW); c.stroke()
    text(c, sub, 0, -130, 52, PAL['white'], outline=0)
    text(c, label, 0, 110 if len(label) <= 5 else 95, 150 if len(label) <= 5 else 92, INK, outline=0)
    c.restore()

def factory(c, x, base, s=1):
    c.save(); c.translate(x, base); c.scale(s, s)
    c.new_path(); c.move_to(-200, 0); c.line_to(-200, -200); c.line_to(-100, -280); c.line_to(-100, -200); c.line_to(0, -280); c.line_to(0, -200)
    c.line_to(100, -280); c.line_to(100, 0); c.close_path(); fill_stroke(c, PAL['b5'])
    rrect(c, 120, -420, 60, 420, 8); fill_stroke(c, PAL['b4'])
    c.restore()

def debt_paper(c, x, y, s=1, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rrect(c, -140, -180, 280, 360, 10); fill_stroke(c, PAL['paper'])
    text(c, "DEUDA", 0, -80, 62, PAL['red'], outline=0)
    text(c, "-2,3M €", 0, 20, 58, INK, outline=0)
    for i in range(3):
        c.set_source_rgb(0.6, 0.6, 0.65); c.rectangle(-100, 70+i*35, 200-(i % 2)*60, 12); c.fill()
    c.restore()

def money_pile(c, x, base, s=1):
    c.save(); c.translate(x, base); c.scale(s, s)
    r = random.Random(3)
    for row in range(6):
        for i in range(6-row):
            bx = -250+i*100+row*50; by = -row*60
            rrect(c, bx-48, by-55, 96, 55, 8); fill_stroke(c, PAL['money'], 5)
            text(c, "€", bx, by-12, 40, hexc("#2D6A4F"), outline=0)
    c.restore()

def notif(c, x, y, w, title, body, k=1.0, col=None):
    col = col or PAL['white']
    c.save(); c.translate(x, y); c.scale(max(k, 1e-3), max(k, 1e-3))
    rrect(c, -w/2, -70, w, 140, 30); fill_stroke(c, col, 6)
    circle(c, -w/2+70, 0, 40); fill_stroke(c, PAL['land'], 5)
    c.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(40)
    c.move_to(-w/2+130, -12); c.set_source_rgb(*INK); c.show_text(title)
    c.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); c.set_font_size(36)
    c.move_to(-w/2+130, 38); c.show_text(body); c.restore()

def check(c, x, y, s=1, ok=True):
    c.save(); c.translate(x, y); c.scale(s, s)
    circle(c, 0, 0, 90); fill_stroke(c, PAL['land'] if ok else PAL['red'], 8)
    c.set_source_rgb(1, 1, 1); c.set_line_width(24)
    if ok: c.move_to(-40, 0); c.line_to(-10, 35); c.line_to(45, -35)
    else: c.move_to(-35, -35); c.line_to(35, 35); c.move_to(35, -35); c.line_to(-35, 35)
    c.stroke(); c.restore()

def question_marks(c, x, y, t, n=3):
    for i in range(n):
        k = back((t-i*0.2)*3)
        if k > 0:
            c.save(); c.translate(x+(i-1)*110, y-abs(math.sin(t*3+i))*25); c.scale(max(k, 1e-3), max(k, 1e-3)); c.rotate((i-1)*0.25)
            text(c, "?", 0, 0, 130, PAL['yellow'], outline=12); c.restore()
