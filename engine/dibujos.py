#!/usr/bin/env python3
"""Dibujos de papel recortado para los posts de noticias (sin fotos, logos ni parecidos).

dibujar(lista, ancho, alto, fondo) -> imagen RGBA con la escena.
lista = [{"k": "gafas"}, {"k": "mazo"}, {"k": "prohibido"}]  (máx. 3 + marcas)
  - Cada elemento acepta "x", "y" (0–1 dentro del panel), "s" (tamaño relativo, def. según cuántos haya)
    y "color" en los que lo usan (grafica: "sube"|"baja").
  - Marcas que van ENCIMA del elemento anterior: prohibido, alerta, roto (grietas), check.
Elementos: gafas, mazo, nube, candado, telefono, dinero, grafica, robot, chip, cohete, balon, trofeo,
  guante, auto, globo, edificio, avion, servidor, rayo, matraz, persona, gente, microfono, casa,
  satelite, bandera (genérica, sin país), reloj, documento.
Prueba: python3 engine/dibujos.py  -> salida/dibujos-muestra.png con todos.
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CREMA, NAR, GRIS, CARB, AZUL, VERDE, ROJO, MOST, KRAFT, BLANCO, CIELO = (
    "#ECE9E3", "#FF6A3D", "#8A8781", "#2E2E33", "#3D6B9E", "#4F8A5B", "#C8423A", "#E8B04A", "#C9A27A", "#F7F5F0", "#7FA6C8")
MARCAS = {"prohibido", "alerta", "roto", "check"}


class Papel:
    def __init__(self, w, h, seed=7):
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.r = random.Random(seed)

    def pieza(self, pts, col, sombra=True, amt=1.6):
        xs0, ys0 = [q[0] for q in pts], [q[1] for q in pts]
        amt = min(amt, 0.025 * math.hypot(max(xs0) - min(xs0), max(ys0) - min(ys0)))
        P = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            n = max(1, int(math.dist(a, b) / 16))
            for k in range(n):
                t = k / n
                P.append((a[0] + (b[0] - a[0]) * t + self.r.uniform(-amt, amt), a[1] + (b[1] - a[1]) * t + self.r.uniform(-amt, amt)))
        if sombra:
            xs, ys = [p[0] for p in P], [p[1] for p in P]
            x0, y0, x1, y1 = int(min(xs)) - 30, int(min(ys)) - 30, int(max(xs)) + 40, int(max(ys)) + 45
            sh = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
            ImageDraw.Draw(sh).polygon([(x - x0 + 5, y - y0 + 8) for x, y in P], fill=(0, 0, 0, 120))
            self.im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), (x0, y0))
        self.d.polygon(P, fill=col)


def circ(cx, cy, r, n=36, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def rrect(x, y, w, h, r, n=6):
    r = min(r, w / 2, h / 2)
    P = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            P.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return P


def barra(a, b, w):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def rot(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


# ---- elementos: dibujados en una caja de 100×100 centrada en (cx, cy) con escala s px/unidad ----
def E(p, cx, cy, s, bg):
    def T(pts):
        return [(cx + (x - 50) * s, cy + (y - 50) * s) for x, y in pts]
    return T


def el_gafas(p, T, s, bg, o):
    for x in (8, 54):
        p.pieza(T(rrect(x, 32, 38, 30, 9)), CARB)
        p.pieza(T(rrect(x + 5, 37, 28, 20, 6)), "#5E7F9A", sombra=False)
        p.pieza(T(rrect(x + 8, 39, 9, 6, 3)), "#9FC0D8", sombra=False)
    p.pieza(T(rect(44, 38, 12, 6)), CARB, sombra=False)
    p.pieza(T(barra((4, 38), (-2, 52), 5)), CARB)
    p.pieza(T(barra((96, 38), (102, 52), 5)), CARB)
    p.pieza(T(circ(91, 38, 3.2)), NAR, sombra=False)


def el_mazo(p, T, s, bg, o):
    p.pieza(T(rrect(18, 78, 64, 12, 3)), KRAFT)
    p.pieza(T(barra((30, 68), (74, 24), 7)), "#8A5A2B")
    p.pieza(T(rot(rrect(14, 44, 42, 22, 5), 35, 55, -0.785)), "#6B4A2E")
    p.pieza(T(rot(rect(20, 47, 6, 16), 35, 55, -0.785)), MOST, sombra=False)
    p.pieza(T(rot(rect(44, 47, 6, 16), 35, 55, -0.785)), MOST, sombra=False)


def el_nube(p, T, s, bg, o):
    pts = []
    for cx, cy, r in ((32, 58, 20), (52, 44, 25), (72, 58, 18)):
        pts.append(circ(cx, cy, r))
    for c in pts:
        p.pieza(T(c), BLANCO)
    p.pieza(T(rrect(14, 56, 74, 22, 10)), BLANCO, sombra=False)
    for cx, cy, r in ((32, 58, 20), (52, 44, 25), (72, 58, 18)):
        p.pieza(T(circ(cx, cy, r - 1)), BLANCO, sombra=False)


def el_candado(p, T, s, bg, o):
    abierto = o.get("abierto")
    dx = 14 if abierto else 0
    p.pieza(T(rrect(29 + dx, 14 - (8 if abierto else 0), 42, 44, 21)), GRIS)
    p.pieza(T(rrect(37 + dx, 22 - (8 if abierto else 0), 26, 40, 13)), bg, sombra=False)
    p.pieza(T(rrect(22, 44, 56, 44, 7)), MOST)
    p.pieza(T(circ(50, 60, 6)), CARB, sombra=False)
    p.pieza(T([(47, 62), (53, 62), (55, 76), (45, 76)]), CARB, sombra=False)


def el_telefono(p, T, s, bg, o):
    p.pieza(T(rrect(28, 6, 44, 88, 9)), CARB)
    p.pieza(T(rrect(32, 14, 36, 70, 4)), "#3D6B9E", sombra=False)
    p.pieza(T(rrect(43, 9, 14, 3, 1.5)), "#55555C", sombra=False)
    for j in range(3):
        p.pieza(T(rrect(36, 20 + j * 14, 28, 9, 3)), ["#9FC0D8", CREMA, NAR][j], sombra=False)


def el_dinero(p, T, s, bg, o):
    for j in range(3):
        p.pieza(T(rot(rrect(10, 30 + j * 10, 62, 32, 3), 41, 46, -0.12 + j * 0.06)), ["#3F7A4E", "#4F8A5B", "#5E9A69"][j])
    p.pieza(T(circ(41, 66, 9)), "#3F7A4E", sombra=False)
    for j in range(3):
        p.pieza(T(circ(78, 76 - j * 8, 13, ry=5)), [MOST, "#D9A040", MOST][j])


def el_grafica(p, T, s, bg, o):
    baja = o.get("color") == "baja"
    hs = [55, 40, 28, 18] if baja else [18, 30, 44, 60]
    for j, hgt in enumerate(hs):
        p.pieza(T(rect(14 + j * 19, 88 - hgt, 14, hgt)), CREMA)
    col = ROJO if baja else VERDE
    a, b = ((12, 22), (82, 70)) if baja else ((12, 70), (82, 18))
    p.pieza(T(barra(a, b, 6)), col)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    tip = [(b[0] + 9 * math.cos(ang), b[1] + 9 * math.sin(ang)), (b[0] + 9 * math.cos(ang + 2.4), b[1] + 9 * math.sin(ang + 2.4)), (b[0] + 9 * math.cos(ang - 2.4), b[1] + 9 * math.sin(ang - 2.4))]
    p.pieza(T(tip), col, sombra=False)


def el_robot(p, T, s, bg, o):
    p.pieza(T(barra((50, 20), (50, 8), 3)), GRIS)
    p.pieza(T(circ(50, 7, 4.5)), NAR)
    p.pieza(T(rrect(20, 20, 60, 48, 12)), CREMA)
    p.pieza(T(rrect(27, 30, 46, 26, 9)), CARB, sombra=False)
    p.pieza(T(circ(40, 43, 5.5)), "#6FD0E8", sombra=False)
    p.pieza(T(circ(60, 43, 5.5)), "#6FD0E8", sombra=False)
    p.pieza(T(rrect(14, 36, 6, 16, 3)), GRIS)
    p.pieza(T(rrect(80, 36, 6, 16, 3)), GRIS)
    p.pieza(T(rrect(28, 72, 44, 22, 8)), GRIS)
    p.pieza(T(circ(50, 83, 4)), NAR, sombra=False)


def el_chip(p, T, s, bg, o):
    for j in range(4):
        for a, b in (((30 + j * 13, 14), (30 + j * 13, 26)), ((30 + j * 13, 74), (30 + j * 13, 86)), ((14, 30 + j * 13), (26, 30 + j * 13)), ((74, 30 + j * 13), (86, 30 + j * 13))):
            p.pieza(T(barra(a, b, 4)), MOST, sombra=False)
    p.pieza(T(rrect(22, 22, 56, 56, 6)), CARB)
    p.pieza(T(rrect(32, 32, 36, 36, 4)), "#44444B", sombra=False)
    p.pieza(T(circ(50, 50, 8)), NAR, sombra=False)


def el_cohete(p, T, s, bg, o):
    p.pieza(T([(42, 76), (50, 98), (58, 76)]), NAR)
    p.pieza(T([(45, 76), (50, 90), (55, 76)]), MOST, sombra=False)
    p.pieza(T([(34, 58), (22, 80), (38, 74)]), ROJO)
    p.pieza(T([(66, 58), (78, 80), (62, 74)]), ROJO)
    p.pieza(T([(50, 4), (62, 22), (64, 76), (36, 76), (38, 22)]), CREMA)
    p.pieza(T([(50, 4), (60, 18), (40, 18)]), ROJO, sombra=False)
    p.pieza(T(circ(50, 38, 7)), AZUL, sombra=False)


def el_balon(p, T, s, bg, o):
    p.pieza(T(circ(50, 50, 40, 48)), BLANCO)
    p.pieza(T(circ(50, 50, 11, 5)), CARB, sombra=False)
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        cx, cy = 50 + 30 * math.cos(a), 50 + 30 * math.sin(a)
        p.pieza(T(rot(circ(cx, cy, 9, 5), cx, cy, a + math.pi)), CARB, sombra=False)


def el_trofeo(p, T, s, bg, o):
    p.pieza(T(circ(22, 34, 13)), MOST)
    p.pieza(T(circ(22, 34, 7)), bg, sombra=False)
    p.pieza(T(circ(78, 34, 13)), MOST)
    p.pieza(T(circ(78, 34, 7)), bg, sombra=False)
    p.pieza(T([(24, 14), (76, 14), (70, 46), (58, 58), (42, 58), (30, 46)]), MOST)
    p.pieza(T(rect(44, 56, 12, 16)), "#D9A040")
    p.pieza(T(rrect(30, 72, 40, 16, 3)), "#6B4A2E")
    p.pieza(T([(36, 20), (42, 20), (40, 40), (36, 34)]), "#F5D27A", sombra=False)


def el_guante(p, T, s, bg, o):
    p.pieza(T(rrect(30, 66, 36, 26, 4)), CREMA)
    p.pieza(T(rrect(22, 16, 56, 58, 24)), ROJO)
    p.pieza(T(rrect(12, 36, 22, 28, 11)), "#B0342E")
    p.pieza(T(rect(30, 70, 36, 5)), "#B0342E", sombra=False)


def el_auto(p, T, s, bg, o):
    p.pieza(T([(6, 64), (20, 50), (40, 46), (60, 46), (88, 54), (96, 64), (96, 72), (6, 72)]), o.get("color_auto", ROJO))
    p.pieza(T([(44, 46), (50, 34), (62, 34), (66, 46)]), CARB)
    p.pieza(T(rect(84, 40, 12, 8)), CARB)
    p.pieza(T(rect(2, 52, 8, 14)), CARB)
    for x in (22, 78):
        p.pieza(T(circ(x, 74, 12)), CARB)
        p.pieza(T(circ(x, 74, 5)), GRIS, sombra=False)


def el_globo(p, T, s, bg, o):
    p.pieza(T(circ(50, 50, 40, 48)), "#3D6B9E")
    for pts in ([(22, 30), (40, 22), (46, 34), (38, 46), (30, 60), (22, 50)], [(56, 26), (74, 22), (82, 38), (70, 44), (60, 40)], [(52, 54), (66, 52), (72, 66), (60, 80), (52, 70)]):
        p.pieza(T(pts), "#5E9A69", sombra=False)
    p.pieza(T(circ(64, 22, 9)), NAR)
    p.pieza(T([(58, 26), (70, 26), (64, 40)]), NAR, sombra=False)
    p.pieza(T(circ(64, 22, 3.5)), CREMA, sombra=False)


def el_edificio(p, T, s, bg, o):
    p.pieza(T([(10, 30), (50, 8), (90, 30)]), CREMA)
    p.pieza(T(rect(12, 30, 76, 8)), "#D8D3C8")
    for j in range(5):
        p.pieza(T(rect(17 + j * 15, 40, 8, 38)), CREMA)
    p.pieza(T(rect(8, 78, 84, 8)), "#D8D3C8")
    p.pieza(T(rect(4, 86, 92, 6)), CREMA)


def el_avion(p, T, s, bg, o):
    for sg in (1, -1):
        p.pieza(T([(38, 50), (56, 50), (42, 50 - sg * 40), (32, 50 - sg * 40)]), GRIS)
        p.pieza(T([(80, 50), (90, 50), (94, 50 - sg * 16), (88, 50 - sg * 16)]), GRIS)
    p.pieza(T(rrect(4, 43, 92, 14, 7)), CREMA)
    p.pieza(T(rrect(4, 45, 12, 10, 5)), NAR, sombra=False)


def el_servidor(p, T, s, bg, o):
    for j in range(3):
        p.pieza(T(rrect(20, 12 + j * 26, 60, 22, 4)), CARB)
        for k in range(3):
            p.pieza(T(circ(30 + k * 8, 23 + j * 26, 2.6)), ["#6FD0E8", VERDE, NAR][k], sombra=False)
        p.pieza(T(rect(56, 20 + j * 26, 18, 5)), "#55555C", sombra=False)


def el_rayo(p, T, s, bg, o):
    p.pieza(T([(56, 4), (24, 54), (46, 54), (38, 96), (76, 40), (54, 40), (66, 4)]), MOST)


def el_matraz(p, T, s, bg, o):
    p.pieza(T([(40, 8), (60, 8), (60, 36), (84, 86), (16, 86), (40, 36)]), "#D8E6EE")
    p.pieza(T([(26, 64), (74, 64), (84, 86), (16, 86)]), "#6FD0E8", sombra=False)
    p.pieza(T(rect(36, 4, 28, 7)), GRIS)
    for cx, cy, r in ((40, 74, 3), (56, 70, 4), (50, 52, 2.5)):
        p.pieza(T(circ(cx, cy, r)), CREMA, sombra=False)


def el_persona(p, T, s, bg, o):
    col = o.get("color_ropa", NAR)
    p.pieza(T(rrect(26, 44, 48, 52, 20)), col)
    p.pieza(T(circ(50, 26, 17)), "#C99B74")
    p.pieza(T([(33, 22), (36, 10), (52, 6), (66, 12), (67, 22), (58, 16), (42, 16)]), "#3A2A1E", sombra=False)


def el_gente(p, T, s, bg, o):
    cols = [AZUL, NAR, VERDE, MOST, ROJO]
    for j, x in enumerate((14, 86, 32, 68, 50)):
        y = 12 if j < 2 else (6 if j < 4 else 0)
        p.pieza(T(rrect(x - 13, 58 + y, 26, 34 - y, 11)), cols[j])
        p.pieza(T(circ(x, 46 + y, 10)), ["#C99B74", "#8E6440", "#E0B990", "#A87A52", "#C99B74"][j])


def el_microfono(p, T, s, bg, o):
    p.pieza(T(rect(46, 62, 8, 24)), GRIS)
    p.pieza(T(rrect(30, 84, 40, 8, 3)), CARB)
    p.pieza(T(rrect(34, 8, 32, 56, 16)), CARB)
    for j in range(4):
        p.pieza(T(rect(38, 18 + j * 9, 24, 3)), "#55555C", sombra=False)
    p.pieza(T(rect(30, 46, 40, 6)), NAR, sombra=False)


def el_casa(p, T, s, bg, o):
    p.pieza(T(rect(20, 44, 60, 46)), CREMA)
    p.pieza(T([(10, 48), (50, 12), (90, 48)]), ROJO)
    p.pieza(T(rect(42, 62, 16, 28)), "#8A5A2B", sombra=False)
    p.pieza(T(rect(26, 54, 12, 12)), "#9FC0D8", sombra=False)
    p.pieza(T(rect(62, 54, 12, 12)), "#9FC0D8", sombra=False)


def el_satelite(p, T, s, bg, o):
    p.pieza(T(rot(rect(4, 42, 30, 16), 50, 50, -0.4)), AZUL)
    p.pieza(T(rot(rect(66, 42, 30, 16), 50, 50, -0.4)), AZUL)
    p.pieza(T(rot(barra((30, 50), (70, 50), 3), 50, 50, -0.4)), GRIS)
    p.pieza(T(rot(rrect(38, 36, 24, 28, 4), 50, 50, -0.4)), MOST)
    p.pieza(T(circ(62, 30, 7)), CREMA)


def el_bandera(p, T, s, bg, o):
    p.pieza(T(rect(16, 8, 5, 86)), GRIS)
    p.pieza(T([(21, 12), (50, 8), (84, 16), (84, 50), (52, 44), (21, 48)]), o.get("color_bandera", NAR))


def el_reloj(p, T, s, bg, o):
    p.pieza(T(circ(50, 52, 40, 48)), CREMA)
    p.pieza(T(circ(50, 52, 33, 48)), BLANCO, sombra=False)
    p.pieza(T(barra((50, 52), (50, 28), 5)), CARB, sombra=False)
    p.pieza(T(barra((50, 52), (68, 60), 5)), NAR, sombra=False)
    p.pieza(T(circ(50, 52, 4)), CARB, sombra=False)


def el_documento(p, T, s, bg, o):
    p.pieza(T([(22, 6), (66, 6), (80, 20), (80, 94), (22, 94)]), CREMA)
    p.pieza(T([(66, 6), (80, 20), (66, 20)]), "#D8D3C8", sombra=False)
    for j in range(6):
        p.pieza(T(rect(30, 30 + j * 10, 42 - (16 if j == 5 else 0), 3.5)), GRIS, sombra=False)
    p.pieza(T(circ(64, 82, 7)), ROJO, sombra=False)


# ---- marcas encima ----
def mk_prohibido(p, T, s, bg, o):
    pts_o, pts_i = circ(50, 50, 48, 48), circ(50, 50, 39, 48)
    anillo = Image.new("L", p.im.size, 0)
    dd = ImageDraw.Draw(anillo)
    dd.polygon(T(pts_o), fill=255)
    dd.polygon(T(pts_i), fill=0)
    dd.polygon(T(barra((22, 22), (78, 78), 9)), fill=255)
    sh = Image.new("RGBA", p.im.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 120), (6, 9), anillo)
    p.im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    p.im.paste(Image.new("RGBA", p.im.size, ROJO), (0, 0), anillo)


def mk_alerta(p, T, s, bg, o):
    p.pieza(T([(78, 52), (98, 88), (58, 88)]), MOST)
    p.pieza(T(rect(76, 62, 4, 14)), CARB, sombra=False)
    p.pieza(T(rect(76, 79, 4, 4)), CARB, sombra=False)


def mk_roto(p, T, s, bg, o):
    for a, b in (((40, 10), (52, 40)), ((52, 40), (44, 60)), ((44, 60), (58, 92)), ((52, 40), (70, 46))):
        p.pieza(T(barra(a, b, 3.5)), ROJO, sombra=False)


def mk_check(p, T, s, bg, o):
    p.pieza(T(circ(82, 80, 15)), VERDE)
    p.pieza(T(barra((74, 80), (80, 87), 4)), BLANCO, sombra=False)
    p.pieza(T(barra((80, 87), (91, 72), 4)), BLANCO, sombra=False)


EL = {k[3:]: v for k, v in globals().items() if k.startswith("el_")}
MK = {k[3:]: v for k, v in globals().items() if k.startswith("mk_")}
POS = {1: [(0.5, 0.52, 0.84)], 2: [(0.29, 0.54, 0.72), (0.71, 0.50, 0.72)], 3: [(0.19, 0.58, 0.56), (0.50, 0.46, 0.66), (0.81, 0.58, 0.56)]}


def dibujar(lista, w, h, bg="#E9E1D0", seed=7):
    p = Papel(w, h, seed)
    if bg:  # fondo de papel claro con un halo y dos franjas, para que la escena se lea en el feed
        p.d.rectangle([0, 0, w, h], fill=bg)
        p.d.ellipse([w * 0.18, h * 0.08, w * 0.82, h * 1.05], fill="#F3EDE0")
        p.pieza([(0, h * 0.86), (w, h * 0.80), (w, h), (0, h)], "#D8CCB0", sombra=False)
    prin = [e for e in lista if e["k"] not in MARCAS]
    base = POS.get(len(prin), POS[3])
    i, ult = -1, None
    for e in lista:
        k = e["k"]
        if k in MARCAS:
            if ult is None:
                continue
            cx, cy, s = ult
            MK[k](p, E(p, cx, cy, s, bg), s, bg, e)
            continue
        i += 1
        bx, by, bs = base[min(i, len(base) - 1)]
        cx, cy = e.get("x", bx) * w, e.get("y", by) * h
        s = e.get("s", bs) * min(w, h) / 100
        if k not in EL:
            raise SystemExit(f"[dibujos] elemento desconocido: {k}. Opciones: {', '.join(sorted(EL))}")
        EL[k](p, E(p, cx, cy, s, bg), s, bg, e)
        ult = (cx, cy, s)
    return p.im


if __name__ == "__main__":
    import os
    ks = sorted(EL)
    cols, cw = 6, 240
    filas = (len(ks) + cols - 1) // cols
    hoja = Image.new("RGBA", (cols * cw, filas * (cw + 30)), "#E9E1D0")
    f = ImageFont.load_default()
    for j, k in enumerate(ks):
        im = dibujar([{"k": k, "s": 0.8}], cw, cw)
        x, y = (j % cols) * cw, (j // cols) * (cw + 30)
        hoja.alpha_composite(im, (x, y))
        ImageDraw.Draw(hoja).text((x + 10, y + cw + 6), k, fill="#222222", font=f)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "salida", "dibujos-muestra.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    hoja.convert("RGB").save(out)
    print(out)
