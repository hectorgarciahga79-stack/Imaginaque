"""Presets de cámara reutilizables para escribir guiones rápido.

Cada preset devuelve el bloque "camera" de un plano a partir del actor
principal (y opcionalmente un secundario). Así una idea nueva se convierte
en guion indicando solo tipo de plano + duración.
"""


def aerial(actor, d=4.0):
    return {"focus": actor, "dof": False, "smooth": 0.6, "shake": 0.1, "shake_freq": 1.4, "keys": [
        {"t": 0, "pos": {"actor": actor, "offset": [170, -230, 125], "space": "world"},
         "target": {"actor": actor, "offset": [-70, 140, 8], "space": "world"}, "lens": 28},
        {"t": d, "pos": {"actor": actor, "offset": [48, -36, 26], "space": "world"},
         "target": {"actor": actor, "offset": [-12, 42, 2], "space": "world"}, "lens": 30}]}


def travelling(actor, d=4.0, side=3.6):
    """El vehículo adelanta a una cámara que se desplaza en paralelo."""
    return {"focus": actor, "fstop": 2.2, "smooth": 0.18, "shake": 0.018, "shake_freq": 9, "keys": [
        {"t": 0, "pos": {"actor": actor, "offset": [side, 21, 0.75], "space": "world"},
         "target": {"actor": actor, "offset": [0, 0, 0.7], "space": "world"}, "lens": 26, "ease": "linear"},
        {"t": d, "pos": {"actor": actor, "offset": [side + 0.1, -14, 1.15], "space": "world"},
         "target": {"actor": actor, "offset": [-1, 4, 0.6], "space": "world"}, "lens": 30, "roll": -4, "ease": "linear"}]}


def side_tracking(actor, d=1.6):
    return {"focus": actor, "fstop": 2.4, "smooth": 0.15, "shake": 0.025, "shake_freq": 11, "keys": [
        {"t": 0, "pos": {"actor": actor, "offset": [-1.0, 4.3, 0.95], "space": "heading"},
         "target": {"actor": actor, "offset": [6, 0, 0.7], "space": "heading"}, "lens": 22},
        {"t": d, "pos": {"actor": actor, "offset": [2.2, 4.0, 1.3], "space": "heading"},
         "target": {"actor": actor, "offset": [9, 0, 0.7], "space": "heading"}, "lens": 24, "roll": 3}]}


def front_reverse(actor, d=1.6):
    """Cámara delante del vehículo, retrocediendo con él."""
    return {"focus": actor, "fstop": 2.0, "smooth": 0.14, "shake": 0.025, "shake_freq": 10, "keys": [
        {"t": 0, "pos": {"actor": actor, "offset": [10, -1.4, 1.15], "space": "heading"},
         "target": {"actor": actor, "offset": [-7, 0, 0.5], "space": "heading"}, "lens": 38},
        {"t": d, "pos": {"actor": actor, "offset": [6.5, -0.6, 0.85], "space": "heading"},
         "target": {"actor": actor, "offset": [-6, 0, 0.6], "space": "heading"}, "lens": 34}]}


def chase_behind(actor, d=3.0):
    return {"focus": actor, "fstop": 2.8, "smooth": 0.2, "shake": 0.03, "shake_freq": 8, "keys": [
        {"t": 0, "pos": {"actor": actor, "offset": [-9, 0.5, 1.6], "space": "heading"},
         "target": {"actor": actor, "offset": [6, 0, 0.8], "space": "heading"}, "lens": 30},
        {"t": d, "pos": {"actor": actor, "offset": [-7, -1.0, 1.3], "space": "heading"},
         "target": {"actor": actor, "offset": [6, 0, 0.8], "space": "heading"}, "lens": 32}]}


def orbit(actor, d=4.0, radius=8.0):
    import math
    keys = []
    for i in range(5):
        a = math.radians(-60 + 120 * i / 4)
        keys.append({"t": d * i / 4, "pos": {"actor": actor, "offset": [radius * math.cos(a), radius * math.sin(a), 1.4],
                                             "space": "heading"},
                     "target": {"actor": actor, "offset": [0, 0, 0.7], "space": "heading"}, "lens": 28, "ease": "linear"})
    return {"focus": actor, "fstop": 2.4, "smooth": 0.25, "shake": 0.01, "keys": keys}


def crane_out(actor, d=3.0, start=(4.0, 0.5, 2.0), end=(38.0, -16.0, 52.0), look=(-150, 3, 4)):
    return {"focus": actor, "fstop": 4.0, "smooth": 0.35, "shake": 0.05, "shake_freq": 1.8, "keys": [
        {"t": 0, "pos": {"world": list(start)}, "target": {"actor": actor, "offset": [0, 0, 1], "space": "world"}, "lens": 24},
        {"t": d, "pos": {"world": list(end)}, "target": {"world": list(look)}, "lens": 28}]}


PRESETS = {"aerial": aerial, "travelling": travelling, "side_tracking": side_tracking, "front_reverse": front_reverse,
           "chase_behind": chase_behind, "orbit": orbit, "crane_out": crane_out}
