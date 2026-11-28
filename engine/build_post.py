#!/usr/bin/env python3
"""Imagen para publicación de Facebook (no reel): frase o dato + pregunta, con la marca de cada página.

  python3 engine/build_post.py posts/<id>.json            # salida/<id>/<id>.jpg + post.txt
  python3 engine/build_post.py posts/<id>.json --preview  # igual (es instantáneo); revisa el JPG con Read

Esquema (posts/<id>.json):
  {"id": "2026-11-24-ir-post-tracy", "pagina": "impulsoreal" | "senorfutbol",
   "kicker": "BRIAN TRACY",                      # etiqueta pequeña arriba (opcional)
   "texto": "Escribe tus metas <em>a mano</em>.",  # frase o dato grande; <em> = acento de la marca
   "autor": "— Brian Tracy",                     # opcional, en itálica bajo la frase
   "dato": "84",                                  # opcional (SF): número gigante sobre el texto
   "pregunta": "¿Las escribes o solo las piensas?",  # va en la banda de abajo
   "dibujo": [{"k": "gafas"}, {"k": "mazo"}, {"k": "prohibido"}],  # opcional: escena de papel recortado
        # arriba (engine/dibujos.py; elementos y marcas en su docstring; muestra: python3 engine/dibujos.py)
   "post": "texto del post con pregunta 👇", "hashtags": ["#..."], "sources": ["https://..."]}
Formato 1080×1350 (4:5, el que más ocupa en el feed). Sin fotos, escudos ni logos de terceros.
"""
import json, os, re, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "engine", "fonts")
W, H = 1080, 1350
MARCA = {
    "impulsoreal": dict(bg="#0F0F10", fg="#ECE9E3", acc="#FF6A3D", dim="#8A8781", banda="#1C1C1E",
                        logo="impulso_logo.png", nombre="IMPULSO REAL", grid=True),
    "senorfutbol": dict(bg="#F2EFE8", fg="#151515", acc="#4F7A06", dim="#6F6A62", banda="#151515",
                        logo="senorfutbol_logo.png", nombre="SEÑOR FÚTBOL", grid=False),
}


def font(n, s):
    if n == "lora":
        f = ImageFont.truetype(os.path.join(F, "Lora-Italic-Variable.ttf"), s)
        try:
            f.set_variation_by_axes([600])
        except Exception:
            pass
        return f
    return ImageFont.truetype(os.path.join(F, {"xb": "Montserrat-ExtraBold.ttf", "sb": "Montserrat-SemiBold.ttf",
                                                "rg": "Montserrat-Regular.ttf"}[n]), s)


def tokens(texto):
    """'Hola <em>mundo</em>' -> [('Hola', False), ('mundo', True)] palabra por palabra."""
    out = []
    for parte in re.split(r"(<em>.*?</em>)", texto):
        em = parte.startswith("<em>")
        for w in re.sub(r"</?em>", "", parte).split():
            out.append((w, em))
    return out


def envolver(d, toks, f, ancho):
    lineas, cur, cw = [], [], 0
    sp = d.textlength(" ", font=f)
    for w, em in toks:
        lw = d.textlength(w, font=f)
        if cur and cw + sp + lw > ancho:
            lineas.append(cur); cur, cw = [], 0
        cur.append((w, em, lw)); cw += (sp if len(cur) > 1 else 0) + lw
    if cur:
        lineas.append(cur)
    return lineas, sp


def ajustar(d, toks, ancho, alto, maxs=112, mins=54):
    for s in range(maxs, mins - 1, -4):
        f = font("xb", s)
        lineas, sp = envolver(d, toks, f, ancho)
        if len(lineas) * s * 1.18 <= alto and max(d.textlength(w, font=f) for w, _ in toks) <= ancho:
            return f, s, lineas, sp
    f = font("xb", mins)
    return (f, mins, *envolver(d, toks, f, ancho))


def construir(path):
    h = json.load(open(path, encoding="utf-8"))
    m = MARCA[h["pagina"]]
    im = Image.new("RGB", (W, H), m["bg"])
    d = ImageDraw.Draw(im)
    if m["grid"]:
        for x in range(0, W, 60):
            d.line([(x, 0), (x, H)], fill="#17171A", width=1)
        for y in range(0, H, 60):
            d.line([(0, y), (W, y)], fill="#17171A", width=1)
        glow = Image.new("RGB", (W, H), m["bg"])
        ImageDraw.Draw(glow).ellipse([W * 0.15, H * 0.12, W * 0.85, H * 0.62], fill="#2A1A14")
        im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(160)), 0.55)
        d = ImageDraw.Draw(im)
    else:  # papel: marco de tinta y líneas de cuaderno tenues
        for y in range(180, H - 230, 64):
            d.line([(70, y), (W - 70, y)], fill="#E4DFD4", width=2)
        d.rectangle([34, 34, W - 34, H - 34], outline=m["fg"], width=4)

    x0, ancho = 96, W - 192
    y = 120
    dib = h.get("dibujo")
    bh = 220 if dib else 300  # alto de la banda inferior
    if h.get("kicker"):
        fk = font("sb", 34)
        k = h["kicker"].upper()
        tw = d.textlength(k, font=fk)
        d.rounded_rectangle([x0 - 4, y - 8, x0 + tw + 36, y + 50], 26, outline=m["acc"], width=3)
        d.text((x0 + 16, y + 21), k, font=fk, fill=m["acc"], anchor="lm")
        y += 100
    if dib:
        import dibujos
        pw, ph = W - 120, 470
        panel = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        esc = dibujos.dibujar(dib, pw, ph, h.get("dibujo_fondo", "#E9E1D0"), seed=len(h["id"]))
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], 36, fill=255)
        im.paste(esc, (60, y - 10), mask)
        d = ImageDraw.Draw(im)
        y += ph + 30
    if h.get("dato"):
        fd = font("xb", 260)
        d.text((x0 - 8, y - 20), str(h["dato"]), font=fd, fill=m["acc"], anchor="la")
        y += 270
    banda_y = H - bh
    alto = banda_y - y - ((90 if dib else 110) if h.get("autor") else 50)
    f, s, lineas, sp = ajustar(d, tokens(h["texto"]), ancho, alto, 84 if (h.get("dato") or dib) else 112, 44 if dib else 54)
    lh = s * 1.18
    ty = y + max(0, (alto - len(lineas) * lh) / 2) if not h.get("dato") else y
    for ln in lineas:
        x = x0
        for w, em, lw in ln:
            d.text((x, ty), w, font=f, fill=m["acc"] if em else m["fg"])
            x += lw + sp
        ty += lh
    if h.get("autor"):
        d.text((x0, ty + (12 if dib else 24)), h["autor"], font=font("lora", 38 if dib else 44), fill=m["dim"])

    # banda inferior: pregunta + marca
    d.rectangle([0, banda_y, W, H], fill=m["banda"])
    d.rectangle([0, banda_y, W, banda_y + 8], fill=m["acc"])
    fq = font("sb", 46)
    q = re.sub(r"[^\u0000-\u2FFF]", "", h.get("pregunta", "")).strip()  # sin emojis (la fuente no los tiene)
    qtoks = [(w, False) for w in q.split()]
    ql, qsp = envolver(d, qtoks, fq, W - 330)
    qy = banda_y + bh // 2 - len(ql) * 29
    for ln in ql:
        d.text((x0, qy), " ".join(w for w, _, _ in ln), font=fq, fill="#F2EFE8")
        qy += 58
    ls = 120 if dib else 170
    logo = Image.open(os.path.join(ROOT, "engine", "assets", m["logo"])).convert("RGBA").resize((ls, ls))
    im.paste(logo, (W - 96 - ls, banda_y + (30 if dib else 40)), logo)
    d.text((W - 96 - ls // 2, banda_y + (30 if dib else 40) + ls + 22), m["nombre"], font=font("sb", 22), fill="#F2EFE8", anchor="mm")

    out = os.path.join(ROOT, "salida", h["id"])
    os.makedirs(out, exist_ok=True)
    jpg = os.path.join(out, f"{h['id']}.jpg")
    im.convert("RGB").save(jpg, quality=92)
    tags = " ".join(h.get("hashtags", []))
    open(os.path.join(out, "post.txt"), "w", encoding="utf-8").write((h.get("post", "") + ("\n\n" + tags if tags else "")).strip() + "\n")
    print("[post]", jpg)
    return jpg


if __name__ == "__main__":
    construir(sys.argv[1])
