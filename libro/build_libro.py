#!/usr/bin/env python3
"""Genera el PDF 'Libro de Jugadas · Fútbol 7' de Señor Fútbol.
Uso: python3 libro/build_libro.py  ->  libro/salida/Libro-de-Jugadas-Futbol7-SenorFutbol.pdf
"""
import os, html
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(HERE), "engine", "fonts")
OUT = os.path.join(HERE, "salida")
INK, LIME, GREEN, RED, PAPER, GRAY = "#151515", "#B8E62E", "#4F7A06", "#E03A2D", "#F2EFE8", "#A7A196"
e = html.escape
_uid = [0]


def uid():
    _uid[0] += 1
    return f"m{_uid[0]}"


# ---------- Diagramas ----------
def pitch(players=(), rivals=(), arrows=(), zones=(), ball=None, w=360, h=520, square=None, cones=()):
    """Cancha de fútbol 7 vertical. Coordenadas en % (x izq→der, y 0 = portería rival arriba)."""
    m = uid()
    X = lambda v: v / 100 * w
    Y = lambda v: v / 100 * h
    s = [f'<svg viewBox="-20 -24 {w+40} {h+48}" width="100%" xmlns="http://www.w3.org/2000/svg">',
         f'<defs>'
         f'<marker id="{m}k" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker>'
         f'<marker id="{m}g" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{GREEN}"/></marker>'
         f'<marker id="{m}r" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{RED}"/></marker>'
         f'</defs>',
         f'<g fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round">',
         f'<rect x="0" y="0" width="{w}" height="{h}"/>',
         f'<line x1="0" y1="{h/2}" x2="{w}" y2="{h/2}"/><circle cx="{w/2}" cy="{h/2}" r="{w*0.13}"/>',
         f'<rect x="{w*.22}" y="0" width="{w*.56}" height="{h*.15}"/><rect x="{w*.22}" y="{h*.85}" width="{w*.56}" height="{h*.15}"/>',
         f'<path d="M{w*.38} 0 L{w*.38} -14 L{w*.62} -14 L{w*.62} 0" stroke-width="4"/>',
         f'<path d="M{w*.38} {h} L{w*.38} {h+14} L{w*.62} {h+14} L{w*.62} {h}" stroke-width="4"/></g>',
         f'<circle cx="{w/2}" cy="{h/2}" r="3.5" fill="{INK}"/>']
    for z in zones:
        x, y, zw, zh, lab = z[:5]
        col = z[5] if len(z) > 5 else "red"
        fill, st, tc = ("rgba(184,230,46,.38)", GREEN, GREEN) if col == "green" else ("rgba(224,58,45,.16)", RED, "#C2301F")
        s.append(f'<rect x="{X(x)}" y="{Y(y)}" width="{X(zw)}" height="{Y(zh)}" rx="8" fill="{fill}" stroke="{st}" stroke-width="2.5" stroke-dasharray="8 6"/>')
        if lab:
            s.append(f'<text x="{X(x)+8}" y="{Y(y)+20}" font-family="Barlow" font-weight="800" font-size="17" fill="{tc}">{e(lab)}</text>')
    if square:
        x, y, sw, sh = square
        s.append(f'<rect x="{X(x)}" y="{Y(y)}" width="{X(sw)}" height="{Y(sh)}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="3 7"/>')
    for c in cones:
        cx, cy = X(c[0]), Y(c[1])
        s.append(f'<path d="M{cx-8} {cy+7} L{cx} {cy-9} L{cx+8} {cy+7} Z" fill="#F08A24" stroke="{INK}" stroke-width="2"/>')
    for a in arrows:
        x1, y1, x2, y2, kind = a[:5]
        cv = a[5] if len(a) > 5 else 0
        col, mk, dash = {"pass": (INK, "k", "7 7"), "run": (GREEN, "g", "none"), "press": (RED, "r", "none"),
                         "dribble": (INK, "k", "2 6")}[kind]
        ax, ay, bx, by = X(x1), Y(y1), X(x2), Y(y2)
        mx, my = (ax + bx) / 2 + cv * (by - ay), (ay + by) / 2 - cv * (bx - ax)
        s.append(f'<path d="M{ax} {ay} Q{mx} {my} {bx} {by}" fill="none" stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="{dash}" marker-end="url(#{m}{mk})"/>')
    for p in rivals:
        x, y = X(p[0]), Y(p[1])
        lab = p[2] if len(p) > 2 else ""
        s.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{RED}" stroke="{INK}" stroke-width="3"/>')
        if lab:
            s.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" font-family="Anton" font-size="15" fill="{PAPER}">{e(lab)}</text>')
    for p in players:
        x, y = X(p[0]), Y(p[1])
        lab = p[2] if len(p) > 2 else ""
        s.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{LIME}" stroke="{INK}" stroke-width="3"/>')
        if lab:
            s.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" font-family="Anton" font-size="{15 if len(lab) < 3 else 12}" fill="{INK}">{e(lab)}</text>')
    if ball:
        bx, by = X(ball[0]), Y(ball[1])
        s.append(f'<circle cx="{bx}" cy="{by}" r="7" fill="#fff" stroke="{INK}" stroke-width="2.5"/><circle cx="{bx}" cy="{by}" r="2.4" fill="{INK}"/>')
    s.append('</svg>')
    return "".join(s)


GK = (50, 94, "PO")


def sys_players(kind):
    return {
        "2-3-1": [GK, (32, 78, "DF"), (68, 78, "DF"), (16, 54, "MI"), (50, 60, "MC"), (84, 54, "MD"), (50, 30, "9")],
        "3-2-1": [GK, (20, 76, "DF"), (50, 80, "DF"), (80, 76, "DF"), (34, 54, "MC"), (66, 54, "MC"), (50, 30, "9")],
        "3-1-2": [GK, (20, 74, "DF"), (50, 80, "DF"), (80, 74, "DF"), (50, 58, "MC"), (34, 30, "9"), (66, 30, "9")],
        "2-1-2-1": [GK, (32, 80, "DF"), (68, 80, "DF"), (50, 64, "MC"), (20, 46, "IN"), (80, 46, "IN"), (50, 26, "9")],
    }[kind]


# ---------- Contenido ----------
SISTEMAS = [
    ("2-3-1", "El más usado en fútbol 7",
     "Dos defensas, tres medios y un delantero. Es el sistema más equilibrado: siempre tienes gente por dentro y por fuera, y los triángulos salen solos.",
     ["Equilibrio entre ataque y defensa", "Amplitud natural con los medios exteriores", "Triángulos en todo el campo"],
     ["El 9 se queda solo si los exteriores no suben", "Espalda de los exteriores cuando atacan"],
     "Base para casi cualquier equipo; ideal si tienes medios con buen ida y vuelta.",
     ["Exteriores pegados a la raya al atacar", "El MC nunca se va arriba si el balón se pierde", "Defensas abiertos para salir jugando"]),
    ("3-2-1", "Sólido atrás", "Tres defensas, dos medios y un delantero. Te da seguridad y una salida de balón cómoda con el portero como cuarto hombre.",
     ["Seguridad defensiva", "Salida de 3 + portero", "Bueno contra rivales con dos puntas"],
     ["Poca gente en ataque", "Inferioridad en medio contra tres medios"],
     "Para cuidar una ventaja o contra rivales muy rápidos.",
     ["Los defensas de banda suben por fuera, de uno en uno", "Los dos MC siempre cerca, para no partirse", "El 9 aguanta de espaldas y descarga"]),
    ("3-1-2", "Dos puntas para presionar", "Tres defensas, un medio y dos delanteros. Siempre tienes dos opciones arriba y puedes presionar la salida rival.",
     ["Presión alta con dos delanteros", "Dos referencias de pase arriba", "Mucho gol"],
     ["Bandas desprotegidas", "Un solo medio de contención"],
     "Contra rivales que salen jugando desde atrás o cuando necesitas gol.",
     ["El MC debe ser tu jugador más inteligente", "Los defensas de banda cubren la raya", "Los dos 9 presionan en diagonal a los defensas"]),
    ("2-1-2-1", "El rombo de la posesión", "Dos defensas, un contención, dos interiores y un delantero. Los cuatro de arriba forman un rombo que domina el centro: es el que más se parece al juego de posición.",
     ["Control del centro", "Muchísimos triángulos", "Ideal para tener la pelota"],
     ["La amplitud depende de los interiores", "Exige buena condición física"],
     "Para equipos técnicos que quieren tener el balón.",
     ["Los interiores abren la cancha", "El 9 baja entre líneas para cerrar el rombo", "El contención protege la espalda de todos"]),
]

PRINCIPIOS = [
    dict(t="Salida desde atrás", s="El portero es un jugador más",
         p="Como hacen los equipos que juegan al estilo del PSG de Luis Enrique, la jugada empieza en el portero. Con él tienes superioridad: si el rival presiona con dos, tú sales con tres.",
         d=dict(players=[GK, (22, 82, "DF"), (78, 82, "DF"), (50, 66, "MC"), (12, 56, "MI"), (88, 56, "MD"), (50, 34, "9")], rivals=[(40, 70), (60, 70), (50, 50)],
                arrows=[(50, 93, 22, 83, "pass"), (22, 82, 12, 58, "pass", .15), (50, 66, 50, 60, "run")], ball=(50, 91)),
         k=["Defensas bien abiertos, casi en la banda", "El MC se ofrece de frente, nunca de espaldas", "Si te presionan arriba, busca al exterior"],
         x="Que el portero la reviente por miedo: pierdes la superioridad.", ej=4),
    dict(t="Presión alta", s="Presionar con disparadores",
         p="No se presiona todo el tiempo: se presiona cuando hay una señal. Las tres señales más claras son un pase hacia atrás, un mal control y el balón en la banda.",
         d=dict(players=[GK, (32, 66, "DF"), (68, 66, "DF"), (30, 36, "MI"), (55, 40, "MC"), (80, 30, "MD"), (62, 20, "9")], rivals=[(50, 6), (30, 18), (78, 18), (50, 30)],
                arrows=[(80, 30, 78, 20, "press"), (62, 20, 54, 12, "press"), (55, 40, 50, 32, "press")], zones=[(60, 8, 36, 22, "BANDA = PRESIÓN")], ball=(78, 18)),
         k=["Todos salen juntos a la señal", "El primero corre en curva para tapar el pase al centro", "Si uno presiona solo, es mejor no presionar"],
         x="Presionar de uno en uno: te cansas y te pasan fácil.", ej=5),
    dict(t="Regla de los 5 segundos", s="Presión tras pérdida",
         p="Al perder el balón, el rival está desordenado. Los tres más cercanos van por él al mismo tiempo durante cinco segundos. Si no la recuperan, todos atrás y juntos.",
         d=dict(players=[GK, (32, 76, "DF"), (68, 62, "DF"), (36, 46, "MI"), (64, 44, "MC"), (82, 36, "MD"), (58, 34, "9")], rivals=[(50, 6), (34, 20), (66, 20), (24, 36), (50, 40), (80, 42)],
                arrows=[(82, 46, 82, 38, "press"), (52, 54, 64, 46, "press"), (50, 30, 58, 35, "press")], zones=[(56, 26, 42, 26, "5 SEGUNDOS")], ball=(80, 42)),
         k=["Uno presiona, otro tapa el pase al centro, otro cierra la banda", "Cuenta los cinco segundos en voz alta en el entrenamiento", "Pasados los cinco, repliegue de todos"],
         x="Quedarse a reclamar la falta en vez de presionar.", ej=1),
    dict(t="Defensas por dentro", s="Superioridad en el centro",
         p="Cuando tienes el balón, un defensa da un paso al medio y se suma a la construcción. Así ganas un hombre en el centro, donde se decide el partido.",
         d=dict(players=[GK, (32, 78, "DF"), (60, 62, "DF"), (14, 48, "MI"), (44, 52, "MC"), (86, 48, "MD"), (50, 26, "9")], rivals=[(40, 40), (60, 40), (50, 24)],
                arrows=[(68, 78, 60, 63, "run"), (60, 62, 44, 52, "pass"), (44, 52, 14, 49, "pass", -.15)], ball=(60, 62)),
         k=["Solo sube por dentro un defensa a la vez", "El MC se abre para dejarle espacio", "El otro defensa queda de seguro atrás"],
         x="Que suban los dos defensas y te quedes sin nadie atrás.", ej=15),
    dict(t="El 9 que baja", s="Falso 9 y extremos al espacio",
         p="Tu delantero baja a recibir entre líneas y arrastra a un defensa. El hueco que deja lo atacan los exteriores en diagonal.",
         d=dict(players=[GK, (32, 78, "DF"), (68, 78, "DF"), (16, 40, "MI"), (50, 60, "MC"), (84, 40, "MD"), (50, 42, "9")], rivals=[(50, 6), (36, 22), (64, 22), (50, 38)],
                arrows=[(50, 30, 50, 41, "run"), (50, 60, 50, 44, "pass"), (84, 40, 62, 14, "run", .1), (50, 42, 62, 16, "pass")], ball=(50, 44)),
         k=["El 9 baja de espaldas y juega a uno o dos toques", "Los exteriores arrancan cuando el 9 recibe", "Pase al espacio, nunca al pie del que corre"],
         x="Que el 9 baje y nadie ataque el espacio que dejó.", ej=16),
    dict(t="Tercer hombre", s="Triángulos y paredes",
         p="Si el rival tapa el pase directo, juega con un tercero: A le da a B, B de primera a C, que llega de cara. Es la base del juego de posición.",
         d=dict(players=[GK, (30, 80, "DF"), (70, 80, "DF"), (30, 56, "A"), (50, 44, "B"), (74, 36, "C"), (50, 22, "9")], rivals=[(52, 52), (60, 40)],
                arrows=[(30, 56, 50, 45, "pass"), (50, 44, 72, 37, "pass"), (30, 56, 40, 34, "run", -.1)], ball=(50, 44)),
         k=["El que recibe de espaldas juega a un toque", "El tercero llega en movimiento, de frente", "Practícalo con rondos de tres colores"],
         x="Que el segundo jugador se dé la vuelta y pierda el balón.", ej=8),
    dict(t="Abrir la cancha", s="Amplitud y profundidad",
         p="Una cancha grande favorece al que tiene el balón. Dos jugadores pegados a las bandas y uno amenazando la espalda estiran al rival y abren pasillos por dentro.",
         d=dict(players=[GK, (32, 76, "DF"), (68, 76, "DF"), (6, 46, "MI"), (50, 56, "MC"), (94, 46, "MD"), (50, 20, "9")], rivals=[(36, 40), (64, 40), (50, 28), (50, 12)],
                arrows=[(50, 56, 50, 32, "pass"), (6, 46, 6, 30, "run"), (94, 46, 94, 30, "run")], zones=[(38, 30, 24, 22, "PASILLO", "green")], ball=(50, 56)),
         k=["Regla: nunca dos jugadores en el mismo carril", "Los exteriores pisan la raya", "El 9 siempre amenaza la espalda"],
         x="Que todos se junten alrededor del balón.", ej=7),
    dict(t="Bloque junto", s="Defender en 20 metros",
         p="Cuando el rival tiene el balón y no lo puedes presionar, todo el equipo se junta: corto entre líneas y estrecho por dentro. Que solo pueda jugar por fuera.",
         d=dict(players=[GK, (38, 80, "DF"), (62, 80, "DF"), (26, 64, "MI"), (50, 66, "MC"), (74, 64, "MD"), (50, 48, "9")], rivals=[(50, 30), (20, 40), (80, 40), (50, 52)],
                zones=[(16, 44, 68, 42, "BLOQUE CORTO", "green")], arrows=[(50, 30, 20, 40, "pass", .2)], ball=(50, 30)),
         k=["Máximo 15 a 20 metros entre el 9 y los defensas", "Se basculan todos hacia el lado del balón", "La presión empieza cuando el balón va a la banda"],
         x="Defensas muy atrás y medios muy arriba: queda un hueco enorme.", ej=12),
]

BALON_PARADO = [
    ("Córner: pantalla al primer palo", dict(players=[(96, 2, "TC"), (44, 18, "A"), (58, 22, "B"), (40, 34, "C"), (64, 40, "D")], rivals=[(46, 12), (56, 14), (48, 26), (50, 3)],
     arrows=[(58, 22, 48, 13, "run"), (40, 34, 56, 10, "run", -.1), (96, 2, 56, 10, "pass", .15)], ball=(96, 2)),
     ["B bloquea al marcador del primer palo", "C arranca desde atrás hacia el hueco", "Centro tenso al primer palo, a media altura"]),
    ("Córner: corto y centro atrás", dict(players=[(96, 2, "TC"), (84, 12, "A"), (50, 20, "B"), (46, 30, "C")], rivals=[(50, 12), (60, 16), (82, 18)],
     arrows=[(96, 2, 84, 11, "pass"), (84, 12, 76, 16, "dribble"), (76, 16, 46, 29, "pass", .1), (50, 20, 40, 14, "run")], ball=(96, 2)),
     ["Saque corto para sacar a un rival del área", "Conducción hacia dentro", "Centro al punto penal para el que llega de frente"]),
    ("Saque de banda: pared y espalda", dict(players=[(100, 50, "SB"), (84, 44, "A"), (78, 30, "B"), (50, 28, "9")], rivals=[(86, 38), (70, 34)],
     arrows=[(100, 50, 84, 45, "pass"), (84, 44, 100, 48, "pass", .3), (100, 48, 80, 26, "pass", -.1), (78, 30, 82, 20, "run")], ball=(100, 50)),
     ["A recibe y devuelve a un toque", "El que sacó entra y juega a la espalda", "Rapidez: saca antes de que el rival se acomode"]),
    ("Tiro libre: amago y pase al costado", dict(players=[(50, 36, "A"), (56, 38, "B"), (24, 22, "C"), (70, 22, "9")], rivals=[(44, 26), (50, 26), (56, 26), (50, 4)],
     arrows=[(50, 36, 56, 37, "dribble"), (56, 38, 26, 23, "pass", .1), (24, 22, 46, 6, "pass")], ball=(52, 36)),
     ["A amaga el tiro y pasa por encima del balón", "B toca al costado para C", "C remata cruzado, lejos de la barrera"]),
]

EJ = [
    ("Rondo 4 vs 2 con 5 segundos", "Presión tras pérdida", "Cuadro de 10×10 m. Cuatro por fuera, dos al centro.", "Si un defensor roba, el que perdió el balón tiene 5 s para recuperarlo; si no, entra al centro.", "Toques limitados a dos.",
     dict(players=[(30, 30), (70, 30), (70, 70), (30, 70)], rivals=[(46, 46), (56, 56)], square=(22, 22, 56, 56), arrows=[(30, 30, 70, 30, "pass"), (70, 30, 70, 69, "pass")], ball=(30, 30))),
    ("Rondo 5 vs 2 a dos toques", "Circulación rápida", "Círculo de 12 m. Cinco por fuera y dos al centro.", "Máximo dos toques. Cada 10 pases seguidos, un punto.", "Prohibido devolver al que te pasó.",
     dict(players=[(50, 22), (78, 40), (68, 76), (32, 76), (22, 40)], rivals=[(46, 48), (56, 54)], arrows=[(50, 22, 68, 75, "pass"), (68, 76, 22, 41, "pass")], ball=(50, 22))),
    ("Posesión 4 vs 4 + 2 comodines", "Tener el balón", "Espacio de 20×15 m. Dos equipos de cuatro y dos comodines que juegan con el que tiene el balón.", "Punto cada 8 pases.", "Los comodines solo a un toque.",
     dict(players=[(24, 30), (72, 34), (30, 66), (70, 70), (50, 18, "C"), (50, 82, "C")], rivals=[(40, 40), (60, 48), (44, 62), (58, 30)], square=(14, 14, 72, 72), ball=(24, 30))),
    ("Salida desde atrás 3 + PO vs 2", "Salir jugando", "Medio campo. Portero, dos defensas y un medio contra dos delanteros.", "Punto si pasan la línea de medio campo conduciendo; los delanteros anotan en portería.", "Los defensas solo pueden dar tres toques.",
     dict(players=[GK, (22, 82, "DF"), (78, 82, "DF"), (50, 66, "MC")], rivals=[(40, 72), (60, 72)], arrows=[(50, 93, 22, 83, "pass"), (22, 82, 50, 67, "pass")], ball=(50, 92))),
    ("Presión 3 vs 3 con disparador", "Presionar a la señal", "Espacio de 25×20 m con mini porterías.", "Los defensores solo pueden presionar tras un pase atrás o en la banda; si roban y anotan en 5 s, gol doble.", "El entrenador grita la señal.",
     dict(players=[(30, 40), (50, 30), (70, 40)], rivals=[(30, 64), (50, 74), (70, 64)], arrows=[(50, 30, 50, 70, "press"), (30, 40, 30, 60, "press")], ball=(50, 74))),
    ("Transición 4 vs 4 en tres zonas", "Pierde y presiona", "Campo dividido en tres zonas. 4 vs 4.", "Al perder el balón, el equipo debe recuperar en la misma zona o retroceder a la zona propia.", "Gol vale triple si recuperas en zona rival.",
     dict(players=[(30, 30), (70, 30), (40, 60), (60, 62)], rivals=[(30, 46), (70, 46), (50, 20), (50, 76)], zones=[(0, 0, 100, 33, "ZONA 1", "green"), (0, 67, 100, 33, "ZONA 3", "green")], ball=(30, 30))),
    ("Carriles", "Ocupar bien el campo", "Campo dividido en cinco carriles verticales con conos.", "Nunca dos jugadores del mismo equipo en el mismo carril. Si pasa, balón para el rival.", "Agrega un comodín libre.",
     dict(players=[(10, 50), (30, 64), (50, 40), (70, 66), (90, 50)], rivals=[(40, 50), (60, 54)], cones=[(20, 4), (40, 4), (60, 4), (80, 4), (20, 96), (40, 96), (60, 96), (80, 96)], ball=(50, 40))),
    ("Triángulos y tercer hombre", "Juego combinativo", "Tres conos en triángulo a 8 m. Un jugador en cada cono.", "A pasa a B, B de primera a C, que llega de cara. Rota después de cada pase.", "Agrega un defensor pasivo en medio.",
     dict(players=[(30, 72, "A"), (50, 36, "B"), (72, 66, "C")], arrows=[(30, 72, 49, 38, "pass"), (50, 36, 70, 64, "pass"), (30, 72, 52, 78, "run", .2)], cones=[(30, 80), (50, 28), (72, 74)], ball=(30, 72))),
    ("Desmarque de ruptura", "Atacar la espalda", "Medio campo con portero. Un pasador y dos atacantes contra un defensa.", "El pasador busca el pase al espacio; el atacante debe arrancar en el momento del pase.", "Fuera de lugar activado.",
     dict(players=[(50, 64, "P"), (34, 40), (66, 40)], rivals=[(50, 32), (50, 4)], arrows=[(50, 64, 60, 18, "pass"), (66, 40, 60, 18, "run")], ball=(50, 64))),
    ("Centro y remate 2 vs 1", "Finalizar centros", "Medio campo con portero. Un extremo y dos rematadores contra un defensa.", "El extremo desborda y centra; los rematadores atacan primer y segundo palo.", "Solo valen goles de primera.",
     dict(players=[(88, 40, "E"), (40, 30), (60, 34)], rivals=[(50, 18), (50, 4)], arrows=[(88, 40, 90, 16, "dribble"), (90, 16, 44, 10, "pass", .1), (40, 30, 44, 11, "run"), (60, 34, 62, 12, "run")], ball=(88, 40))),
    ("Contragolpe 3 vs 2", "Atacar rápido", "Campo completo. Tres atacantes salen desde medio campo contra dos defensas.", "Máximo 8 segundos para finalizar.", "Un defensor extra sale 3 s después.",
     dict(players=[(30, 52), (50, 56), (70, 52)], rivals=[(40, 28), (60, 28), (50, 4)], arrows=[(50, 56, 50, 40, "dribble"), (50, 40, 70, 30, "pass"), (30, 52, 34, 20, "run")], ball=(50, 56))),
    ("Defensa en bloque 4 vs 4", "Bloque junto", "Medio campo. Los defensores deben mantener 15 m de distancia entre su primera y última línea.", "Si se separan más, el ataque suma punto.", "El entrenador marca cuándo se puede presionar.",
     dict(players=[(30, 70), (70, 70), (40, 56), (60, 56)], rivals=[(20, 34), (50, 28), (80, 34), (50, 44)], zones=[(22, 50, 56, 28, "15 METROS", "green")], ball=(50, 28))),
    ("Recupera y finaliza", "De la presión al gol", "Medio campo con portero. 3 vs 3.", "Los defensores, al recuperar, tienen 6 s para anotar.", "Gol vale doble si recuperan en los primeros 3 s.",
     dict(players=[(36, 42), (64, 42), (50, 30)], rivals=[(40, 56), (60, 58), (50, 70), (50, 4)], arrows=[(36, 42, 40, 54, "press"), (64, 42, 60, 56, "press")], ball=(60, 58))),
    ("Partido: gol doble en campo rival", "Presión alta en partido", "Partido 6 vs 6 con porteros.", "Si el gol llega tras recuperar en campo rival, vale doble.", "Gol triple si fue en menos de 5 s.",
     dict(players=[GK, (30, 70), (70, 70), (50, 54), (30, 34), (70, 34)], rivals=[(50, 6), (40, 22), (60, 22), (50, 40)], zones=[(0, 0, 100, 50, "GOL DOBLE", "green")], ball=(50, 40))),
    ("El defensa conduce", "Superioridad por dentro", "Medio campo. 3 vs 2 en la salida.", "El defensa debe conducir hasta atraer a un rival y entonces soltar el pase.", "Punto extra si el pase rompe una línea.",
     dict(players=[(30, 78, "DF"), (70, 78, "DF"), (50, 56, "MC")], rivals=[(50, 66), (40, 46)], arrows=[(70, 78, 58, 66, "dribble"), (58, 66, 50, 57, "pass")], ball=(70, 78))),
    ("Falso 9", "El 9 baja y los exteriores atacan", "Medio campo con portero. 4 vs 3.", "El 9 baja a recibir; el gol solo vale si anota un exterior.", "El 9 juega a un toque.",
     dict(players=[(50, 40, "9"), (20, 40), (80, 40), (50, 62)], rivals=[(36, 22), (64, 22), (50, 32), (50, 4)], arrows=[(50, 28, 50, 39, "run"), (50, 62, 50, 42, "pass"), (80, 40, 62, 14, "run")], ball=(50, 42))),
    ("Rueda de pases con remate", "Técnica y finalización", "Cuatro conos en rombo frente a la portería.", "Pase, apoyo y remate; rota de cono en cada repetición.", "Remate solo con la pierna menos hábil.",
     dict(players=[(50, 76), (28, 54), (72, 50), (50, 32)], cones=[(50, 84), (20, 54), (80, 50), (50, 40)], arrows=[(50, 76, 28, 55, "pass"), (28, 54, 72, 51, "pass"), (72, 50, 50, 33, "pass"), (50, 32, 50, 4, "pass")], ball=(50, 76))),
    ("3 vs 3 a mini porterías", "Juego reducido", "Espacio de 20×15 m con cuatro mini porterías.", "Se puede anotar en cualquiera de las dos porterías rivales.", "Gol solo tras cambio de orientación.",
     dict(players=[(30, 40), (50, 56), (70, 40)], rivals=[(30, 64), (50, 44), (70, 64)], cones=[(24, 4), (76, 4), (24, 96), (76, 96)], ball=(50, 56))),
    ("Saque de banda rápido", "Balón parado", "Banda y medio campo.", "Equipo que saca en menos de 3 s y juega a la espalda suma punto.", "Defensores pasivos al inicio.",
     dict(players=[(100, 50, "SB"), (84, 44), (78, 28)], rivals=[(86, 36), (66, 34)], arrows=[(100, 50, 84, 45, "pass"), (84, 44, 100, 47, "pass", .3), (100, 47, 80, 24, "pass", -.1)], ball=(100, 50))),
    ("Partido final con reglas de la semana", "Aplicar lo aprendido", "Partido 7 vs 7.", "Activa la regla de la semana: 5 segundos, carriles o gol doble en campo rival.", "Cambia la regla cada 10 minutos.",
     dict(players=sys_players("2-3-1"), rivals=[(50, 6), (30, 20), (70, 20), (20, 40), (50, 40), (80, 40), (50, 70)], ball=(50, 60))),
]


# ---------- Páginas ----------
def page(inner, n=None, cls=""):
    foot = f'<div class="foot"><span>SEÑOR FÚTBOL · LIBRO DE JUGADAS FÚTBOL 7</span><span>{n}</span></div>' if n else ""
    return f'<section class="page {cls}"><div class="bar"></div>{inner}{foot}</section>'


def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


MASCOT = open(os.path.join(HERE, "mascota.svg"), encoding="utf-8").read()


def build_html():
    P = []
    n = 1
    # Portada
    P.append(f'''<section class="page cover"><div class="bar"></div>
      <div class="ctag">PIZARRA SEÑOR FÚTBOL</div>
      <h1 class="ct1">LIBRO DE<br>JUGADAS</h1><div class="ct2">FÚTBOL 7</div>
      <p class="csub">4 sistemas · 8 principios de juego estilo PSG · balón parado · 20 ejercicios con diagrama · plantillas para tu equipo</p>
      <div class="cmascot">{MASCOT}</div>
      <div class="cfoot">facebook.com/senorfutbol</div></section>''')
    n += 1
    # Cómo usar + leyenda
    leg = pitch(players=[(18, 30, "MC")], rivals=[(18, 62)], arrows=[(40, 22, 88, 22, "pass"), (40, 42, 88, 42, "run"), (40, 62, 88, 62, "press"), (40, 82, 88, 82, "dribble")], w=360, h=300)
    P.append(page(f'''<h2>Cómo usar este libro</h2>
      <p class="lead">Este libro está pensado para entrenadores y capitanes de ligas de fútbol 7. Cada página tiene una idea, un diagrama y las claves para llevarla al campo el próximo entrenamiento.</p>
      <div class="two"><div>
        <h3>Plan sugerido</h3>
        <ol class="steps"><li><b>Semana 1:</b> elige tu sistema base (páginas 4–7).</li><li><b>Semanas 2 a 5:</b> un principio de juego por semana (páginas 8–15).</li><li><b>Cada sesión:</b> dos o tres ejercicios relacionados y un partido final con la regla de la semana.</li><li><b>Antes del partido:</b> usa la plantilla de alineación y repasa el balón parado.</li></ol>
        <p class="note">Las ideas están inspiradas en el juego de posición y la presión que popularizaron equipos como el PSG de Luis Enrique, adaptadas a la cancha y al número de jugadores del fútbol 7. Señor Fútbol no está afiliado a ningún club.</p>
      </div><div>
        <h3>Leyenda</h3>
        <div class="legend">{leg}</div>
        <ul class="leg"><li><i class="dot lime"></i>Tu equipo</li><li><i class="dot red"></i>Rival</li><li><i class="ln pass"></i>Pase</li><li><i class="ln run"></i>Carrera sin balón</li><li><i class="ln press"></i>Presión</li><li><i class="ln drib"></i>Conducción</li></ul>
      </div></div>''', n))
    n += 1
    # Índice
    idx = [("Sistemas", "4"), ("Principios de juego", "8"), ("Balón parado", "16"), ("20 ejercicios", "18"), ("Plantillas", "28")]
    P.append(page('<h2>Contenido</h2><div class="toc">' + "".join(f'<div class="tocrow"><span>{e(a)}</span><span class="dots"></span><span>{b}</span></div>' for a, b in idx) +
                  '</div><div class="bigq">"El balón es el que corre más rápido. Hazlo correr a él."</div><p class="note">Frase clásica del fútbol de posesión.</p>', n))
    n += 1
    # Sistemas
    for nombre, sub, desc, fort, deb, cuando, claves in SISTEMAS:
        P.append(page(f'''<div class="sec">SISTEMAS</div><h2>{e(nombre)} <span class="hsub">{e(sub)}</span></h2>
          <div class="two wide"><div class="diag">{pitch(players=sys_players(nombre))}</div><div>
            <p class="lead">{e(desc)}</p>
            <h3 class="g">Fortalezas</h3>{ul(fort)}
            <h3 class="r">Debilidades</h3>{ul(deb)}
            <h3>Cuándo usarlo</h3><p>{e(cuando)}</p>
            <h3>Claves</h3>{ul(claves, "keys")}
          </div></div>''', n))
        n += 1
    # Principios
    for i, pr in enumerate(PRINCIPIOS, 1):
        P.append(page(f'''<div class="sec">PRINCIPIO {i} DE 8</div><h2>{e(pr["t"])} <span class="hsub">{e(pr["s"])}</span></h2>
          <div class="two wide"><div class="diag">{pitch(**pr["d"])}</div><div>
            <p class="lead">{e(pr["p"])}</p>
            <h3>3 claves</h3>{ul(pr["k"], "keys")}
            <div class="err"><b>Error común:</b> {e(pr["x"])}</div>
            <div class="rel">Ejercicio relacionado: <b>#{pr["ej"]} · {e(EJ[pr["ej"]-1][0])}</b></div>
          </div></div>''', n))
        n += 1
    # Balón parado (2 por página)
    for j in range(0, 4, 2):
        cells = ""
        for t, d, k in BALON_PARADO[j:j+2]:
            cells += f'<div class="half"><h3 class="ht">{e(t)}</h3><div class="hrow"><div class="diag sm">{pitch(**d, w=360, h=300)}</div>{ul(k, "keys")}</div></div>'
        P.append(page(f'<div class="sec">BALÓN PARADO</div><h2>Jugadas preparadas</h2>{cells}', n))
        n += 1
    # Ejercicios (2 por página)
    for j in range(0, 20, 2):
        cells = ""
        for k, (t, obj, org, reg, var, d) in enumerate(EJ[j:j+2], j + 1):
            cells += f'''<div class="half ex"><div class="exn">#{k}</div><div class="hrow"><div class="diag sm">{pitch(**d, w=320, h=320)}</div><div>
              <h3 class="ht">{e(t)}</h3><div class="obj">Objetivo: {e(obj)}</div>
              <p><b>Organización.</b> {e(org)}</p><p><b>Reglas.</b> {e(reg)}</p><p><b>Variante.</b> {e(var)}</p></div></div></div>'''
        P.append(page(f'<div class="sec">EJERCICIOS</div><h2>Ejercicios {j+1} y {j+2}</h2>{cells}', n))
        n += 1
    # Plantillas
    empty = [(50, 94), (30, 76), (70, 76), (18, 52), (50, 56), (82, 52), (50, 28)]
    P.append(page(f'''<div class="sec">PLANTILLAS</div><h2>Alineación del partido</h2>
      <div class="two wide"><div class="diag">{pitch(players=[(x, y, "") for x, y in empty])}</div><div class="form">
      <p>Rival: ______________________</p><p>Fecha y hora: ________________</p><p>Sistema: ____________________</p>
      <h3>Titulares</h3>''' + "".join(f"<p>{i}. ___________________________</p>" for i in range(1, 8)) +
      '<h3>Suplentes</h3>' + "".join(f"<p>{i}. ___________________________</p>" for i in range(8, 13)) +
      '<h3>Regla de la semana</h3><p>______________________________</p></div></div>', n))
    n += 1
    rows = "".join(f"<tr><td>{d}</td><td></td><td></td><td></td></tr>" for d in ["Calentamiento (10 min)", "Ejercicio 1 (15 min)", "Ejercicio 2 (15 min)", "Ejercicio 3 (15 min)", "Partido final (20 min)", "Estiramiento (5 min)"])
    P.append(page(f'''<div class="sec">PLANTILLAS</div><h2>Plan de sesión</h2>
      <p>Principio de la semana: ______________________________ &nbsp; Fecha: ____________</p>
      <table class="plan"><tr><th>Bloque</th><th>Ejercicio #</th><th>Material</th><th>Notas</th></tr>{rows}</table>
      <h3>Qué funcionó</h3><div class="lines"></div><h3>Qué mejorar</h3><div class="lines"></div>''', n))
    n += 1
    P.append(page(f'''<div class="sec">PLANTILLAS</div><h2>Pizarra en blanco</h2>
      <div class="two"><div class="diag">{pitch()}</div><div class="diag">{pitch()}</div></div>''', n))
    n += 1
    # Contraportada
    P.append(f'''<section class="page cover back"><div class="bar"></div><div class="cmascot sm">{MASCOT}</div>
      <h2 class="bk">¿Te sirvió?</h2><p class="csub">Etiqueta a <b>Señor Fútbol</b> con la foto de tu equipo usando estas jugadas.<br>Videos nuevos de pizarra táctica todas las semanas.</p>
      <div class="cfoot">facebook.com/senorfutbol</div>
      <p class="legal">© Señor Fútbol. Uso personal y para tu equipo. Prohibida su reventa o distribución.</p></section>''')
    return P


CSS = f"""
@font-face{{font-family:Anton;src:url('file://{FONTS}/anton-latin-400-normal.woff2') format('woff2');}}
@font-face{{font-family:Barlow;font-weight:600;src:url('file://{FONTS}/barlow-condensed-latin-600-normal.woff2') format('woff2');}}
@font-face{{font-family:Barlow;font-weight:800;src:url('file://{FONTS}/barlow-condensed-latin-800-normal.woff2') format('woff2');}}
@page{{size:letter;margin:0}}
*{{box-sizing:border-box}}
body{{margin:0;background:{PAPER};color:{INK};font-family:Barlow,sans-serif;font-weight:600;font-size:15.5px;line-height:1.35}}
.page{{width:8.5in;height:11in;position:relative;padding:.75in .65in .7in;overflow:hidden;page-break-after:always;background:{PAPER}}}
.bar{{position:absolute;left:0;top:0;right:0;height:14px;background:{LIME};border-bottom:5px solid {INK}}}
.foot{{position:absolute;left:.65in;right:.65in;bottom:.35in;display:flex;justify-content:space-between;font-weight:800;font-size:12px;letter-spacing:3px;color:#6f6a62}}
h1,h2{{font-family:Anton;font-weight:400;margin:0;letter-spacing:.5px}}
h2{{font-size:44px;line-height:1;margin:6px 0 18px}}
.hsub{{font-family:Barlow;font-weight:800;font-size:22px;color:#6f6a62;letter-spacing:1px;margin-left:8px}}
h3{{font-family:Barlow;font-weight:800;font-size:17px;letter-spacing:2.5px;text-transform:uppercase;margin:14px 0 6px}}
h3.g{{color:{GREEN}}} h3.r{{color:#C2301F}}
.sec{{display:inline-block;background:{INK};color:{LIME};font-weight:800;letter-spacing:4px;font-size:13px;padding:5px 12px 3px}}
.lead{{font-size:17px;line-height:1.4}}
p{{margin:6px 0}}
ul{{margin:4px 0;padding-left:20px}} li{{margin:3px 0}}
ul.keys{{list-style:none;padding:0}} ul.keys li{{padding-left:26px;position:relative;margin:7px 0}}
ul.keys li:before{{content:'';position:absolute;left:0;top:3px;width:15px;height:15px;background:{LIME};border:2.5px solid {INK};border-radius:50%}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:26px}}
.two.wide{{grid-template-columns:1fr 1.05fr}}
.diag svg{{display:block}}
.err{{margin-top:14px;padding:10px 14px;border:2.5px solid {RED};background:rgba(224,58,45,.08)}}
.rel{{margin-top:12px;font-size:14px}}
.note{{font-size:13px;color:#4a4740}}
.half{{border-top:3px solid {INK};padding-top:10px;margin-top:8px;height:4.15in;position:relative}}
.half .ht{{font-size:19px;letter-spacing:1.5px;margin-top:2px}}
.hrow{{display:grid;grid-template-columns:2.9in 1fr;gap:20px;align-items:start}}
.diag.sm svg{{max-height:3.6in;width:100%}}
.ex .hrow p{{font-size:14.5px}}
.ex .ht{{padding-right:64px}}
.exn{{position:absolute;right:0;top:6px;font-family:Anton;font-size:46px;color:{LIME};-webkit-text-stroke:2px {INK}}}
.obj{{display:inline-block;background:{LIME};font-weight:800;font-size:13px;letter-spacing:1.5px;padding:3px 9px 2px;margin-bottom:6px;text-transform:uppercase}}
.steps li{{margin:6px 0}}
.legend svg{{max-height:2.3in}}
.leg{{list-style:none;padding:0;columns:2}} .leg li{{display:flex;align-items:center;gap:8px;margin:6px 0}}
.dot{{display:inline-block;width:16px;height:16px;border-radius:50%;border:2.5px solid {INK}}} .dot.lime{{background:{LIME}}} .dot.red{{background:{RED}}}
.ln{{display:inline-block;width:34px;height:0;border-top:3px solid {INK}}} .ln.pass{{border-top-style:dashed}} .ln.run{{border-color:{GREEN}}} .ln.press{{border-color:{RED}}} .ln.drib{{border-top-style:dotted}}
.toc{{margin-top:20px}} .tocrow{{display:flex;align-items:baseline;gap:10px;font-family:Anton;font-size:30px;margin:14px 0}}
.tocrow .dots{{flex:1;border-bottom:3px dotted {INK};transform:translateY(-6px)}}
.bigq{{margin-top:60px;font-family:Anton;font-size:40px;line-height:1.1;border-left:10px solid {LIME};padding-left:20px}}
.form p{{margin:9px 0}}
table.plan{{width:100%;border-collapse:collapse;margin-top:12px}} .plan th,.plan td{{border:2.5px solid {INK};padding:10px;text-align:left;height:56px;vertical-align:top}} .plan th{{background:{INK};color:{LIME};height:auto;letter-spacing:2px}}
.lines{{height:1.3in;background:repeating-linear-gradient({PAPER} 0 30px,#bdb6a8 30px 32px)}}
.cover{{padding:1in .8in}}
.ctag{{display:inline-block;background:{LIME};font-weight:800;letter-spacing:5px;font-size:18px;padding:7px 16px 5px;margin-top:.3in}}
.ct1{{font-size:118px;line-height:.92;margin-top:22px}}
.ct2{{display:inline-block;font-family:Anton;font-size:96px;line-height:1;background:{INK};color:{LIME};padding:8px 22px 0;margin-top:10px}}
.csub{{font-size:21px;font-weight:800;max-width:5.2in;margin-top:24px;line-height:1.3}}
.cmascot{{position:absolute;right:.55in;bottom:1.1in;width:3.6in}} .cmascot svg{{width:100%;height:auto}}
.cmascot.sm{{position:static;width:2.6in;margin:.6in auto 0}}
.cfoot{{position:absolute;left:.8in;bottom:.7in;font-weight:800;letter-spacing:4px;font-size:16px}}
.back{{text-align:center}} .back .csub{{margin:18px auto}} .bk{{font-size:64px;margin-top:20px}}
.legal{{position:absolute;left:0;right:0;bottom:.35in;font-size:11px;color:#6f6a62;text-align:center}}
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    doc = f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(build_html())}</body></html>'
    hp = os.path.join(OUT, "libro.html")
    open(hp, "w", encoding="utf-8").write(doc)
    pdf = os.path.join(OUT, "Libro-de-Jugadas-Futbol7-SenorFutbol.pdf")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto("file://" + hp)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        pg.pdf(path=pdf, format="Letter", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    print("PDF:", pdf)


if __name__ == "__main__":
    main()
