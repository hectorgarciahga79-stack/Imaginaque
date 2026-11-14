"""Portadas dibujadas a medida (cover.py --scene scenes_covers) para capítulos ya renderizados. Personajes grandes, composición limpia."""
from engine import *
from cine import *
from scenes_c4 import marta, julian, dani, smoke, glow, candle, flat, stairs, facade
from scenes_c23 import rosa, jug, radio, torch
import cairo, math

def cover_c2(c):   # Rosa, la del 9º, con la garrafa vacía en la puerta
    wall_room(c, C['wall2'], 1460, 0.75)
    door(c, 760, 1460, 420, 900, open_=0.75, light=0.9, night=0.75, t=0)
    glow(c, 760, 1100, 700, (1, 0.9, 0.65), 0.35)
    rosa(c, 720, 1470, 700, "carry", 0.3, face=-1, expr="worried", look=(0, 0.2), lit=0.95)
    jug(c, 560, 1300, 1.6, fill=0.0)
    marta(c, 230, 1470, 680, "alarm", 0.2, face=1, expr="shock", lit=0.9)
    vig(c, 0.3)

def cover_c3(c):   # Julián con la única radio del edificio
    wall_room(c, C['wall2'], 1460, 0.8)
    window_city(c, 560, 760, 420, 420, 0, night=0.95, lights_out=1)
    glow(c, 640, 1150, 650, (1, 0.8, 0.5), 0.35)
    box(c, 360, 1230, 330, 26, C['wood'], 6)
    box(c, 385, 1256, 22, 214, C['wood2'], 4, 3); box(c, 643, 1256, 22, 214, C['wood2'], 4, 3)
    radio(c, 525, 1150, 1.0, 0.5, on=True, vol=1.0, wave=1.0)
    julian(c, 220, 1470, 680, "listen", 0.3, face=1, expr="focus", lit=0.95)
    marta(c, 820, 1470, 600, "alarm", 0.1, face=-1, expr="shock", lit=0.9)
    vig(c, 0.3)

def cover_c4(c):   # ¡fuego! humo en la escalera y Dani gritando
    stairs(c, 1.0, 0.75, smoke_k=0.8)
    glow(c, 820, 1000, 800, (1, 0.45, 0.15), 0.55)
    smoke(c, 1.3, 400, 800, 1080, 1400, 12, 0.5, seed=4, rise=0, col=(0.15, 0.14, 0.15))
    candle(c, 860, 1440, 1.4, 0.4)
    dani(c, 380, 1470, 720, "alarm", 0.2, face=1, expr="shock", lit=0.95)
    vig(c, 0.3)

COVER = {"C2": cover_c2, "C3": cover_c3, "C4": cover_c4}

SCENES = {}
BOOMS = {}
