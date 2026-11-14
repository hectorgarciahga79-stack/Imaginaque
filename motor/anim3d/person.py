"""Personaje de bloques articulado (original): cabeza grande, cara de «píxeles» en relieve
(ojos con pupila y brillo, cejas, boca que se abre), brazos con codo y mano con pulgar e índice,
piernas con rodilla. Pivotes = empties; el posado se hace por ángulos."""
import math, zlib
from vox import *

LEO = dict(skin="#F2C9A0", hair="#5A3820", hair2="#7A5030", eye="#2B4A8A", top="#2C8C9C", top2="#22707D",
           stripe="#F28A24", legs="#2F4A7A", legs2="#273E66", shoe="#F4F1EA", shoe2="#D8453A", watch=True)

def npc_look(seed):
    r = random.Random(seed)
    skins = ["#F2C9A0", "#E0B08A", "#C68E62", "#8D5A3A", "#F5D6B8", "#B97A50"]
    hairs = ["#2A1E18", "#5A3820", "#C9A060", "#1C1C22", "#8A4A2A", "#B8B4AE", "#3A2A20"]
    tops = ["#B5443A", "#3A6EA8", "#6A9A48", "#E0B040", "#7A4E8A", "#D0D0CC", "#4A4A54", "#C46A2E", "#2E7A6A", "#A83E6E"]
    legs = ["#2F3A52", "#3A3A40", "#5A4A3A", "#22304A", "#6A6A70", "#304A3A"]
    t = r.choice(tops)
    return dict(skin=r.choice(skins), hair=r.choice(hairs), hair2=r.choice(hairs), eye=r.choice(["#2A2A30", "#3A5A2A", "#4A3020", "#2B4A8A"]),
                top=t, top2=t, stripe=t, legs=r.choice(legs), legs2=r.choice(legs), shoe=r.choice(["#2A2A2E", "#F0EEE8", "#6A4A30"]),
                shoe2=r.choice(["#2A2A2E", "#C03A30", "#3A5AA0"]), watch=False, hstyle=r.choice(["short", "long", "cap", "bald"]))

FIG = dict(skin="#B8B0C0", hair="#141218", hair2="#141218", eye="#B46CFF", top="#1A1820", top2="#24202C", stripe="#1A1820",
           legs="#141218", legs2="#141218", shoe="#0E0C10", shoe2="#0E0C10", watch=False, hstyle="hat", glow_eyes=True)

class Person:
    def __init__(self, name, L, h=1.0):
        s = h; self.s = s; self.n = name; self.L = L
        M = lambda c, tag=None: tmat(f"{name}_{tag or c}", c, 8, 0.06, zlib.crc32((name+c).encode()) % 999) if True else mat(c)
        self.root = group(name)
        self.hips = group(name+"_hips", (0, 0, 0.78*s), self.root)
        # torso (pivote en cadera)
        self.chest = group(name+"_chest", (0, 0, 0), self.hips)
        box(name+"_torso", (0, 0, 0.36*s), (0.50*s, 0.28*s, 0.72*s), M(L['top'], 'top'), self.chest)
        box(name+"_stripe", (0, -0.141*s, 0.48*s), (0.505*s, 0.01*s, 0.08*s), mat(L['stripe']), self.chest)
        box(name+"_zip", (0, -0.142*s, 0.36*s), (0.03*s, 0.01*s, 0.66*s), mat(L['top2']), self.chest)
        box(name+"_hood", (0, 0.15*s, 0.68*s), (0.40*s, 0.06*s, 0.16*s), mat(L['top2']), self.chest)
        if L.get('hstyle') == 'hat':  # abrigo largo de la figura
            box(name+"_coat", (0, 0, -0.18*s), (0.54*s, 0.32*s, 0.40*s), mat(L['top2']), self.chest)
        # cabeza
        self.neck = group(name+"_neck", (0, 0, 0.74*s), self.chest)
        self.head = group(name+"_head", (0, 0, 0), self.neck)
        hs = 0.56*s
        box(name+"_skull", (0, 0, hs/2), (hs, hs, hs), M(L['skin'], 'skin'), self.head)
        self._hair(name, L, s, hs)
        f = -hs/2-0.004*s
        self.eyes = []; self.pup = []; self.hl = []
        for sx in (-1, 1):
            e = box(f"{name}_ew{sx}", (sx*0.125*s, f, 0.30*s), (0.13*s, 0.012*s, 0.12*s), mat("#FBFBF6"), self.head)
            p = box(f"{name}_ep{sx}", (sx*0.125*s, f-0.004*s, 0.295*s), (0.07*s, 0.012*s, 0.085*s), mat(L['eye'] if not L.get('glow_eyes') else "#C890FF"), self.head)
            hl = box(f"{name}_eh{sx}", (sx*0.125*s+0.018*s, f-0.008*s, 0.318*s), (0.025*s, 0.01*s, 0.025*s), mat("#FFFFFF"), self.head)
            self.eyes.append(e); self.pup.append(p); self.hl.append(hl)
        self.brows = [box(f"{name}_br{sx}", (sx*0.125*s, f-0.006*s, 0.405*s), (0.15*s, 0.014*s, 0.035*s), mat(L['hair']), self.head) for sx in (-1, 1)]
        self.mouth = box(name+"_mouth", (0, f-0.002*s, 0.14*s), (0.15*s, 0.012*s, 0.035*s), mat("#7A2E2A"), self.head)
        self.teeth = box(name+"_teeth", (0, f-0.006*s, 0.152*s), (0.12*s, 0.012*s, 0.018*s), mat("#FBFBF6"), self.head)
        self.nose = box(name+"_nose", (0, f-0.01*s, 0.215*s), (0.05*s, 0.03*s, 0.04*s), M(L['skin'], 'skin'), self.head)
        # brazos: hombro → codo → mano (+pulgar, índice)
        self.sh = {}; self.el = {}; self.hand = {}; self.thumb = {}; self.index = {}
        for sx in (-1, 1):
            shp = group(f"{name}_sh{sx}", (sx*0.36*s, 0, 0.66*s), self.chest)
            box(f"{name}_ua{sx}", (0, 0, -0.17*s), (0.2*s, 0.22*s, 0.36*s), M(L['top'], 'top'), shp)
            elb = group(f"{name}_el{sx}", (0, 0, -0.34*s), shp)
            box(f"{name}_fa{sx}", (0, 0, -0.15*s), (0.19*s, 0.21*s, 0.30*s), M(L['top'], 'top'), elb)
            box(f"{name}_cuff{sx}", (0, 0, -0.29*s), (0.2*s, 0.22*s, 0.04*s), mat(L['top2']), elb)
            hd = group(f"{name}_hd{sx}", (0, 0, -0.31*s), elb)
            box(f"{name}_palm{sx}", (0, 0, -0.07*s), (0.16*s, 0.18*s, 0.14*s), M(L['skin'], 'skin'), hd)
            th = group(f"{name}_th{sx}", (-sx*0.085*s, -0.05*s, -0.03*s), hd)
            box(f"{name}_thb{sx}", (0, 0, -0.04*s), (0.05*s, 0.06*s, 0.09*s), M(L['skin'], 'skin'), th)
            ix = group(f"{name}_ix{sx}", (-sx*0.04*s, -0.06*s, -0.14*s), hd)
            box(f"{name}_ixb{sx}", (0, 0, -0.04*s), (0.05*s, 0.05*s, 0.09*s), M(L['skin'], 'skin'), ix)
            if L.get('watch') and sx == -1:
                box(f"{name}_wband", (0, 0, -0.255*s), (0.205*s, 0.225*s, 0.05*s), mat("#1E1E24"), elb)
                self.watchface = box(f"{name}_wface", (0, -0.115*s, -0.255*s), (0.1*s, 0.012*s, 0.07*s), mat("#E8F4F0"), elb)
                self.watchhand = box(f"{name}_whand", (0, -0.123*s, -0.255*s), (0.008*s, 0.006*s, 0.03*s), mat("#C0302A"), elb, origin=(0, 0, -0.015*s))
            if sx == 1 and L.get('watch'):
                self.mark = box(f"{name}_mark", (0, -0.112*s, -0.25*s), (0.07*s, 0.012*s, 0.07*s), mat("#7FF6FF"), elb)
                hid(self.mark, True)
            self.sh[sx] = shp; self.el[sx] = elb; self.hand[sx] = hd; self.thumb[sx] = th; self.index[sx] = ix
        # piernas: cadera → rodilla
        self.hp = {}; self.kn = {}
        for sx in (-1, 1):
            hpp = group(f"{name}_hp{sx}", (sx*0.125*s, 0, 0.0), self.hips)
            box(f"{name}_th{sx}b", (0, 0, -0.19*s), (0.24*s, 0.26*s, 0.40*s), M(L['legs'], 'legs'), hpp)
            kn = group(f"{name}_kn{sx}", (0, 0, -0.39*s), hpp)
            box(f"{name}_sn{sx}", (0, 0, -0.17*s), (0.23*s, 0.25*s, 0.32*s), M(L['legs'], 'legs'), kn)
            box(f"{name}_sh{sx}b", (0, -0.035*s, -0.355*s), (0.25*s, 0.33*s, 0.09*s), mat(L['shoe']), kn)
            box(f"{name}_sole{sx}", (0, -0.035*s, -0.392*s), (0.255*s, 0.335*s, 0.025*s), mat(L['shoe2']), kn)
            self.hp[sx] = hpp; self.kn[sx] = kn
        self.blink_off = (zlib.crc32(name.encode()) % 100)/37.0
        self.ph = (zlib.crc32((name+'ph').encode()) % 1000)/159.0      # fase propia: nadie se mueve igual
        self.bper = 2.9+(zlib.crc32((name+'bl').encode()) % 100)/55.0  # cada uno parpadea a su ritmo

    def _hair(self, name, L, s, hs):
        st = L.get('hstyle', 'leo'); H = mat(L['hair']); H2 = mat(L['hair2'])
        h = self.head; t = hs/2
        if st == 'bald': return
        if st == 'hat':
            box(name+"_hatb", (0, 0, hs+0.02*s), (hs+0.26*s, hs+0.26*s, 0.04*s), mat("#141218"), h)
            box(name+"_hatt", (0, 0, hs+0.17*s), (hs+0.02*s, hs+0.02*s, 0.28*s), mat("#141218"), h)
            box(name+"_hatr", (0, 0, hs+0.07*s), (hs+0.03*s, hs+0.03*s, 0.06*s), mat("#5A2A8A"), h)
            return
        box(name+"_hcap", (0, 0.01*s, hs+0.04*s), (hs+0.04*s, hs+0.04*s, 0.09*s), H, h)
        box(name+"_hback", (0, t+0.015*s, hs*0.62), (hs+0.04*s, 0.05*s, hs*0.78), H, h)
        for sx in (-1, 1): box(f"{name}_hside{sx}", (sx*(t+0.015*s), 0.04*s, hs*0.72), (0.05*s, hs*0.86, hs*0.56), H, h)
        if st == 'cap':
            box(name+"_cap", (0, 0, hs+0.08*s), (hs+0.06*s, hs+0.06*s, 0.12*s), mat(L['top']), h)
            box(name+"_capv", (0, -t-0.1*s, hs+0.04*s), (hs*0.9, 0.22*s, 0.04*s), mat(L['top']), h)
            return
        if st == 'long':
            box(name+"_hlong", (0, t*0.6, hs*0.2), (hs+0.06*s, hs*0.5, hs*0.5), H, h)
        # flequillo de Leo: mechones escalonados
        fr = [(-0.19, 0.10, 0.09), (-0.07, 0.13, 0.12), (0.06, 0.10, 0.08), (0.17, 0.07, 0.10)] if st == 'leo' else [(-0.14, 0.07, 0.07), (0.05, 0.08, 0.07), (0.18, 0.06, 0.06)]
        for i, (x, w, d) in enumerate(fr):
            box(f"{name}_fr{i}", (x*s, -t-0.012*s, hs-d*s/2+0.02*s), (w*s, 0.05*s, d*s), H if i % 2 == 0 else H2, h)
        if st == 'leo':
            self.tuft = box(name+"_tuft", (0.06*s, -0.04*s, hs+0.13*s), (0.12*s, 0.12*s, 0.1*s), H2, h, rot=(0.2, 0, 0.3))
            self.grey = box(name+"_grey", (0.16*s, -t-0.014*s, hs-0.04*s), (0.09*s, 0.052*s, 0.09*s), mat("#D8D6D0"), h)
            hid(self.grey, True)

    # ------------------------------------------------------------ posado
    def place(self, x, y, face=0.0, z=0.0):
        """face en grados: 0 = mira a -Y (cámara por defecto); 90 = mira a +X"""
        self.root.location = (x, y, z); self.root.rotation_euler = (0, 0, math.radians(face))
    def face_to(self, x, y, tx, ty, z=0.0):
        self.place(x, y, math.degrees(math.atan2(tx-x, -(ty-y))), z)
    def show(self, v=True): show(self.root, v)

    def arm(self, sx, fwd=0.0, side=0.0, elbow=0.0, twist=0.0, wrist=0.0):
        """fwd: levantar hacia delante (rad, + = adelante); side: abrir hacia fuera; elbow: doblar (+)"""
        self.sh[sx].rotation_euler = (-fwd, -sx*side, twist*sx)
        self.el[sx].rotation_euler = (-elbow, 0, 0)
        self.hand[sx].rotation_euler = (-wrist, 0, 0)
    def leg(self, sx, fwd=0.0, knee=0.0):
        self.hp[sx].rotation_euler = (-fwd, 0, 0); self.kn[sx].rotation_euler = (knee, 0, 0)
    def fingers(self, sx, thumb=0.0, index=0.0):
        self.thumb[sx].rotation_euler = (-thumb, 0, 0); self.index[sx].rotation_euler = (-index, 0, 0)

    def idle(self, t, amp=1.0):
        """reposo vivo: respiración, transferencia de peso y brazos con frecuencias propias (sin simetrías)"""
        p = self.ph; s_ = self.s
        br = math.sin(t*1.9+p)                                    # respiración ~0,3 Hz
        sw = 0.6*math.sin(t*0.47+p*1.3)+0.4*math.sin(t*0.83+p*2.1)  # balanceo lento del peso
        for sx in (-1, 1):
            q = p+(0.9 if sx > 0 else 0.0)
            self.arm(sx, fwd=amp*(0.035*math.sin(t*0.9+q)+0.015*math.sin(t*2.3+q*1.7)), side=0.08+0.015*math.sin(t*0.7+q),
                     elbow=0.18+0.035*math.sin(t*1.1+q)+0.02*br)
            self.leg(sx, 0.012*sw*sx*amp, 0.02+0.03*max(0.0, sw*sx)*amp); self.fingers(sx, 0.3, 0.4+0.06*math.sin(t*1.3+q))
        self.hips.location.z = 0.78*s_ + 0.004*br*s_ - 0.004*abs(sw)*s_
        self.hips.location.x = 0.012*sw*amp*s_
        self.hips.rotation_euler = (0, -0.018*sw*amp, 0.02*math.sin(t*0.39+p)*amp)
        self.chest.rotation_euler = (-0.02*br*amp, 0.012*sw*amp, -0.015*math.sin(t*0.61+p)*amp)

    def walk(self, ph, speed=1.0, run=False):
        """ph = fase en ciclos; ciclo de paso con rodilla, contrabalanceo de brazos y rebote"""
        s = math.sin(ph*2*math.pi); c = math.cos(ph*2*math.pi)
        A = 0.75 if run else 0.45
        for sx in (-1, 1):
            k = sx*s
            self.leg(sx, fwd=A*k, knee=max(0, -sx*c)*(1.3 if run else 0.7)+0.05)
            kl = sx*math.sin(ph*2*math.pi-0.35)                     # el brazo va algo retrasado respecto a la pierna
            self.arm(sx, fwd=-A*0.9*kl, side=0.07, elbow=(1.3 if run else 0.35)+0.15*max(0, kl))
            self.fingers(sx, 0.4, 0.8 if run else 0.4)
        self.hips.location.z = 0.78*self.s + abs(c)*(0.05 if run else 0.025)*self.s - (0.04 if run else 0)*self.s
        self.hips.rotation_euler = (0, 0.035*c, 0.08*s)
        self.hips.location.x = 0.018*c*self.s*(0.6 if run else 1.0)
        self.chest.rotation_euler = (-(0.22 if run else 0.04)-0.02*abs(c), -0.02*c, -0.1*s)

    def face(self, t, expr="neutral", look=(0.0, 0.0), talk=0.0, blink=True, brow=None):
        """expr: neutral, happy, shock, worried, smirk, scared, angry, sad. talk 0..1 abre la boca."""
        s = self.s
        E = dict(neutral=(0, 0, 0, 1.0), happy=(0.02, 0.1, 0.5, 1.0), shock=(0.05, 0, 0.9, 1.25), worried=(0.02, 0.35, 0.1, 1.05),
                 smirk=(0.03, -0.15, 0.25, 0.9), scared=(0.05, 0.4, 0.6, 1.3), angry=(-0.02, -0.35, 0.1, 0.85), sad=(0.0, 0.45, 0.0, 0.95))[expr]
        by, bt, mo, ey = E
        if brow is not None: by, bt = brow
        for i, sx in enumerate((-1, 1)):
            b = self.brows[i]; b.location.z = 0.405*s + by*s
            tilt = bt*sx
            if expr == "smirk" and sx == 1: b.location.z += 0.05*s; tilt = 0.25
            b.rotation_euler = (0, tilt, 0)
        bl = 1.0
        if blink:
            ph = (t + self.blink_off) % self.bper
            if ph < 0.18: bl = 1.0-0.88*math.sin(math.pi*ph/0.18)**0.8
        for i, sx in enumerate((-1, 1)):
            self.eyes[i].scale = (1, 1, ey*bl); self.pup[i].scale = (1, 1, bl*(0.9 if expr in ("shock", "scared") else 1.0))
            self.pup[i].location.x = sx*0.125*s + look[0]*0.03*s
            self.pup[i].location.z = 0.295*s + look[1]*0.025*s
            self.hl[i].location.x = sx*0.125*s + 0.018*s + look[0]*0.03*s
            hid(self.hl[i], bl < 0.5)
        op = clamp(max(mo*0.6, talk))
        self.mouth.scale = (1.0 - 0.25*op if expr not in ("happy", "smirk") else 1.15, 1, 1 + 2.4*op)
        self.mouth.location.x = 0.03*s if expr == "smirk" else 0.0
        self.mouth.rotation_euler = (0, 0.18 if expr == "smirk" else 0.0, 0)
        hid(self.teeth, not (expr in ("happy",) or op > 0.35))
        self.teeth.location.z = 0.152*s + 0.02*op*s
        p = self.ph
        self.head.rotation_euler = (-look[1]*0.25+0.025*math.sin(t*0.73+p)+0.012*math.sin(t*1.9+p*2), 0.02*math.sin(t*0.51+p*1.4),
                                    -look[0]*0.35+0.03*math.sin(t*0.43+p*0.7))
