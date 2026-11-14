"""Tiranosaurio, gallina y bici de bloques (diseños originales) para Q7."""
import math
from vox import *

class TRex:
    """~14 u de largo (≈12 m), cadera a 3,9 u. Mira hacia +X por defecto (face=0 → +X)."""
    def __init__(self, name, col="#5E7A3A", belly="#C8B07A", s=1.0):
        self.s = s; self.n = name
        G = tmat(f"{name}_skin", col, 8, 0.14, hash(name) % 997)
        D = tmat(f"{name}_dark", "#3E5428" if col == "#5E7A3A" else col, 8, 0.12, 5)
        Bm = mat(belly)
        self.root = group(name)
        self.hips = group(name+"_hips", (0, 0, 3.9*s), self.root)
        box(name+"_body", (0.9*s, 0, 0.3*s), (4.4*s, 2.0*s, 2.2*s), G, self.hips)
        box(name+"_belly", (1.1*s, 0, -0.55*s), (3.4*s, 1.6*s, 0.6*s), Bm, self.hips)
        box(name+"_ridge", (0.6*s, 0, 1.47*s), (3.6*s, 0.5*s, 0.16*s), D, self.hips)
        # cola: 3 segmentos encadenados hacia -X
        self.tail = []; par = self.hips; x0 = -1.2*s
        for i, (L, w) in enumerate(((2.4, 1.6), (2.4, 1.1), (2.4, 0.6))):
            p = group(f"{name}_t{i}", (x0, 0, 0.3*s if i == 0 else 0), par)
            box(f"{name}_tb{i}", (-L*s/2, 0, 0), (L*s, w*s, w*s), G, p)
            box(f"{name}_tr{i}", (-L*s/2, 0, w*s/2+0.06*s), (L*s*0.9, 0.3*s, 0.12*s), D, p)
            self.tail.append(p); par = p; x0 = -L*s
        # cuello y cabeza
        self.neck = group(name+"_neck", (3.0*s, 0, 0.9*s), self.hips)
        box(name+"_nk", (0.5*s, 0, 0.5*s), (1.4*s, 1.3*s, 1.6*s), G, self.neck)
        self.head = group(name+"_head", (0.9*s, 0, 1.2*s), self.neck)
        box(name+"_skull", (0.9*s, 0, 0.35*s), (2.4*s, 1.3*s, 1.0*s), G, self.head)
        box(name+"_snout", (2.4*s, 0, 0.2*s), (1.0*s, 1.0*s, 0.7*s), G, self.head)
        box(name+"_brow", (0.9*s, 0, 0.9*s), (1.0*s, 1.36*s, 0.2*s), D, self.head)
        for sy in (-1, 1):
            box(f"{name}_eye{sy}", (0.75*s, sy*0.66*s, 0.6*s), (0.3*s, 0.05*s, 0.26*s), mat("#F4D03F"), self.head)
            box(f"{name}_pup{sy}", (0.8*s, sy*0.69*s, 0.6*s), (0.1*s, 0.04*s, 0.24*s), mat("#141216"), self.head)
            box(f"{name}_nos{sy}", (2.82*s, sy*0.3*s, 0.5*s), (0.16*s, 0.14*s, 0.08*s), mat("#2A3420"), self.head)
        for i in range(7):  # dientes superiores
            x = (0.6+i*0.38)*s
            for sy in (-1, 1):
                box(f"{name}_tu{i}{sy}", (x, sy*0.44*s, -0.2*s), (0.12*s, 0.1*s, 0.24*s), mat("#F4F0E2"), self.head)
        self.jaw = group(name+"_jaw", (0.0, 0, -0.2*s), self.head)
        box(name+"_jw", (1.3*s, 0, -0.25*s), (2.8*s, 1.1*s, 0.45*s), G, self.jaw)
        box(name+"_tongue", (1.0*s, 0, -0.02*s), (1.8*s, 0.7*s, 0.06*s), mat("#B04050"), self.jaw)
        for i in range(6):
            x = (0.8+i*0.4)*s
            for sy in (-1, 1):
                box(f"{name}_tl{i}{sy}", (x, sy*0.4*s, 0.08*s), (0.1*s, 0.1*s, 0.2*s), mat("#F4F0E2"), self.jaw)
        # bracitos
        self.arms = {}
        for sy in (-1, 1):
            a = group(f"{name}_arm{sy}", (2.6*s, sy*0.95*s, -0.3*s), self.hips)
            box(f"{name}_ua{sy}", (0.2*s, 0, -0.3*s), (0.3*s, 0.25*s, 0.7*s), G, a)
            box(f"{name}_cl{sy}", (0.4*s, 0, -0.65*s), (0.3*s, 0.2*s, 0.12*s), mat("#E8E0C8"), a)
            self.arms[sy] = a
        # patas
        self.th = {}; self.sh = {}; self.ft = {}
        for sy in (-1, 1):
            t = group(f"{name}_th{sy}", (0.4*s, sy*1.05*s, -0.2*s), self.hips)
            box(f"{name}_thb{sy}", (0.0, 0, -0.9*s), (1.3*s, 0.8*s, 2.0*s), G, t)
            k = group(f"{name}_kn{sy}", (0.0, 0, -1.8*s), t)
            box(f"{name}_snb{sy}", (-0.1*s, 0, -0.85*s), (0.6*s, 0.55*s, 1.8*s), G, k)
            f = group(f"{name}_ft{sy}", (-0.1*s, 0, -1.75*s), k)
            box(f"{name}_fb{sy}", (0.45*s, 0, -0.08*s), (1.3*s, 0.75*s, 0.3*s), D, f)
            for j in (-1, 0, 1):
                box(f"{name}_cw{sy}{j}", (1.15*s, j*0.24*s, -0.12*s), (0.22*s, 0.12*s, 0.16*s), mat("#E8E0C8"), f)
            self.th[sy] = t; self.sh[sy] = k; self.ft[sy] = f

    def place(self, x, y, face=0.0, z=0.0):
        self.root.location = (x, y, z); self.root.rotation_euler = (0, 0, math.radians(face))
    def show(self, v=True): show(self.root, v)

    def pose(self, t, walk=None, speed=1.0, jaw=0.0, head_pitch=0.0, head_yaw=0.0, crouch=0.0, roar=0.0, peck=0.0):
        s = self.s
        if walk is not None:
            ph = walk*2*math.pi
            for sy in (-1, 1):
                a = math.sin(ph + (0 if sy > 0 else math.pi))
                self.th[sy].rotation_euler = (0, -0.45*a - 0.1, 0)
                self.sh[sy].rotation_euler = (0, max(0, math.cos(ph + (0 if sy > 0 else math.pi)))*0.7+0.15, 0)
                self.ft[sy].rotation_euler = (0, -0.1*a, 0)
            bob = abs(math.cos(ph))*0.18*s
            self.hips.rotation_euler = (math.sin(ph)*0.04, 0.03, 0)
            for i, p in enumerate(self.tail): p.rotation_euler = (0, 0.04, math.sin(ph-0.8-i*0.6)*0.12)
        else:
            for sy in (-1, 1):
                self.th[sy].rotation_euler = (0, -0.1 - 0.5*crouch, 0)
                self.sh[sy].rotation_euler = (0, 0.15 + 0.9*crouch, 0)
                self.ft[sy].rotation_euler = (0, -0.4*crouch, 0)
            bob = math.sin(t*1.6)*0.05*s
            self.hips.rotation_euler = (0, 0.02, 0)
            for i, p in enumerate(self.tail): p.rotation_euler = (0, 0.03+0.02*math.sin(t*1.3+i), math.sin(t*0.9-i*0.7)*0.08)
        self.hips.location.z = 3.9*s - crouch*1.1*s + bob
        r = roar
        self.neck.rotation_euler = (0, -0.1 - 0.35*r + head_pitch*0.5 + 0.9*peck, head_yaw*0.5)
        self.head.rotation_euler = (0, -0.25*r + head_pitch*0.5 + 0.5*peck, head_yaw*0.5)
        self.jaw.rotation_euler = (0, clamp(max(jaw, r))*0.75, 0)
        for sy in (-1, 1): self.arms[sy].rotation_euler = (0, 0.3+0.25*math.sin(t*3+sy), 0)

class Chicken:
    def __init__(self, name, s=1.0):
        self.s = s
        W_ = tmat(name+"_w", "#F4F1EA", 8, 0.06, 3)
        self.root = group(name)
        self.body = group(name+"_body", (0, 0, 0.55*s), self.root)
        box(name+"_b", (0, 0, 0.2*s), (0.9*s, 0.6*s, 0.6*s), W_, self.body)
        box(name+"_tail", (-0.5*s, 0, 0.5*s), (0.25*s, 0.4*s, 0.5*s), W_, self.body)
        for sy in (-1, 1): box(f"{name}_wing{sy}", (-0.05*s, sy*0.32*s, 0.22*s), (0.6*s, 0.06*s, 0.4*s), mat("#E2DCCE"), self.body)
        self.head = group(name+"_head", (0.4*s, 0, 0.45*s), self.body)
        box(name+"_h", (0.05*s, 0, 0.25*s), (0.38*s, 0.36*s, 0.5*s), W_, self.head)
        box(name+"_comb", (0.05*s, 0, 0.56*s), (0.3*s, 0.1*s, 0.16*s), mat("#D0302A"), self.head)
        box(name+"_wat", (0.24*s, 0, 0.08*s), (0.08*s, 0.08*s, 0.16*s), mat("#D0302A"), self.head)
        box(name+"_beak", (0.3*s, 0, 0.26*s), (0.16*s, 0.14*s, 0.1*s), mat("#F0A830"), self.head)
        for sy in (-1, 1): box(f"{name}_eye{sy}", (0.14*s, sy*0.185*s, 0.34*s), (0.07*s, 0.02*s, 0.08*s), mat("#141216"), self.head)
        self.legs = []
        for sy in (-1, 1):
            l = group(f"{name}_leg{sy}", (0, sy*0.15*s, 0.55*s), self.root)
            box(f"{name}_lb{sy}", (0, 0, -0.27*s), (0.07*s, 0.07*s, 0.55*s), mat("#F0A830"), l)
            box(f"{name}_lf{sy}", (0.08*s, 0, -0.53*s), (0.25*s, 0.18*s, 0.04*s), mat("#F0A830"), l)
            self.legs.append(l)
    def place(self, x, y, face=0.0, z=0.0):
        self.root.location = (x, y, z); self.root.rotation_euler = (0, 0, math.radians(face))
    def show(self, v=True): show(self.root, v)
    def pose(self, t, peck=0.0, walk=None):
        self.head.rotation_euler = (0, 0.9*peck, 0)
        self.body.rotation_euler = (0, 0.35*peck, 0)
        if walk is not None:
            for i, l in enumerate(self.legs): l.rotation_euler = (0, 0.5*math.sin(walk*2*math.pi+i*math.pi), 0)
        else:
            for l in self.legs: l.rotation_euler = (0, 0, 0)

class Bike:
    def __init__(self, name):
        self.root = group(name)
        self.wheels = []
        for x in (-0.55, 0.55):
            w = group(f"{name}_w{x}", (x, 0, 0.36), self.root)
            box(f"{name}_wa{x}", (0, 0, 0), (0.7, 0.05, 0.12), mat("#1C1C20"), w)
            box(f"{name}_wb{x}", (0, 0, 0), (0.12, 0.05, 0.7), mat("#1C1C20"), w)
            box(f"{name}_wc{x}", (0, 0, 0), (0.5, 0.06, 0.5), mat("#2A2A2E"), w, rot=(0, math.pi/4, 0))
            box(f"{name}_wh{x}", (0, 0, 0), (0.1, 0.08, 0.1), mat("#B0B4BA"), w)
            self.wheels.append(w)
        c = "#2E8BD0"
        box(name+"_f1", (0, 0, 0.62), (1.0, 0.06, 0.07), mat(c), self.root)
        box(name+"_f2", (-0.15, 0, 0.55), (0.07, 0.06, 0.5), mat(c), self.root, rot=(0, -0.3, 0))
        box(name+"_f3", (0.5, 0, 0.6), (0.07, 0.06, 0.55), mat(c), self.root, rot=(0, 0.25, 0))
        box(name+"_seat", (-0.25, 0, 0.88), (0.3, 0.14, 0.06), mat("#1C1C20"), self.root)
        box(name+"_bar", (0.58, 0, 0.92), (0.06, 0.6, 0.06), mat("#1C1C20"), self.root)
    def place(self, x, y, face=0.0):
        self.root.location = (x, y, 0); self.root.rotation_euler = (0, 0, math.radians(face))
    def show(self, v=True): show(self.root, v)
    def spin(self, a):
        for w in self.wheels: w.rotation_euler = (0, a, 0)
