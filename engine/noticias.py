#!/usr/bin/env python3
"""Reúne las noticias de Liga MX del día para elegir el tema del Video A.

Uso:
  python3 engine/noticias.py                 # últimas 36 h, top 12
  python3 engine/noticias.py --horas 24 --top 8
  python3 engine/noticias.py --rss nota.xml  # leer un feed guardado (pruebas o sin internet)

Junta las notas de config/fuentes.json, agrupa las que hablan del mismo tema, les da
puntos (qué tan reciente, cuántos medios lo cubren, prioridad FC Juárez, polémica,
fichajes...) y marca las que se parecen a historias de los últimos 7 días.

Deja noticias/AAAA-MM-DD.md (para leer) y noticias/AAAA-MM-DD.json (para la tarea).
Son PISTAS, no datos verificados: cada número se confirma leyendo la nota antes de usarlo.
Código de salida 2 = no se pudo leer ninguna fuente (la tarea debe usar búsqueda web).
"""
import argparse, datetime as dt, email.utils, glob, html, json, os, re, sys, unicodedata
import urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GNEWS = "https://news.google.com/rss/search?q={q}&hl=es-419&gl=MX&ceid=MX:es-419"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
VACIAS = set("""de la el los las y en a un una que con por para del al se su sus lo le es fue ser ha han tras ante sobre
contra como mas más pero sin entre este esta estos estas ya muy hoy liga mx vs ante cuando donde quien qué que porque
apertura clausura 2026 2025 jornada partido partidos equipo equipos futbol fútbol mexicano mexico méxico""".split())


def log(*a):
    print("[noticias]", *a, file=sys.stderr, flush=True)


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


SINONIMOS = {"entrenador": "tecnico", "dt": "tecnico", "estratega": "tecnico", "timonel": "tecnico",
             "cesa": "salida", "cesado": "salida", "despide": "salida", "despido": "salida", "destituye": "salida",
             "renuncia": "salida", "bravos": "juarez", "fcj": "juarez", "rayados": "monterrey", "chivas": "guadalajara",
             "tuzos": "pachuca", "diablos": "toluca", "felinos": "tigres", "aguilas": "america", "azulcremas": "america",
             "cementeros": "cruz", "celeste": "cruz", "pumas": "unam", "auriazules": "unam", "goles": "gol",
             "anotacion": "gol", "videoarbitraje": "var", "arbitral": "arbitro", "arbitraje": "arbitro"}
_VACIAS = {norm(v) for v in VACIAS}


def palabras(s):
    out = set()
    for w in re.findall(r"[a-z0-9ñ]+", norm(s)):
        if (len(w) > 2 or w in ("dt", "var")) and w not in _VACIAS:
            out.add(SINONIMOS.get(w, w)[:7])  # raíz corta: polémica/polémico -> polemic
    return out


def limpiar(txt):
    txt = re.sub(r"<[^>]+>", " ", html.unescape(txt or ""))
    return re.sub(r"\s+", " ", txt).strip()


def fecha(txt):
    if not txt:
        return None
    try:
        d = email.utils.parsedate_to_datetime(txt)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(txt.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def leer_feed(xml, origen):
    """RSS 2.0 o Atom -> lista de notas."""
    out = []
    root = ET.fromstring(xml)
    atom = "{http://www.w3.org/2005/Atom}"
    items = root.findall(".//item") or root.findall(f".//{atom}entry")
    for it in items:
        g = lambda tag: (it.findtext(tag) or it.findtext(atom + tag) or "")
        titulo = limpiar(g("title"))
        link = g("link") or (it.find(atom + "link").get("href") if it.find(atom + "link") is not None else "")
        src = it.find("source")
        medio = src.text.strip() if src is not None and src.text else ""
        if not medio and " - " in titulo:  # Google Noticias: "Titular - Medio"
            titulo, medio = titulo.rsplit(" - ", 1)
        if titulo.endswith(" - " + medio):
            titulo = titulo[: -len(medio) - 3]
        resumen = limpiar(g("description") or g("summary"))
        if resumen.startswith(titulo):
            resumen = ""
        out.append({"titulo": titulo.strip(), "medio": medio or origen, "link": link.strip(),
                    "fecha": fecha(g("pubDate") or g("published") or g("updated")), "resumen": resumen[:280]})
    return out


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, */*"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def recientes(dias=7):
    """Texto de las historias de los últimos días, para avisar si un tema ya se hizo."""
    hoy = dt.date.today()
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "stories", "*.json"))):
        m = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p))
        if not m or (hoy - dt.date.fromisoformat(m.group(1))).days > dias:
            continue
        try:
            s = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if s.get("kind", "noticia") != "noticia":
            continue
        txt = " ".join([s.get("id", "").replace("-", " "), s.get("post", "")] + [x.get("say", "") for x in s.get("scenes", [])])
        out.append((s.get("id", os.path.basename(p)), palabras(txt)))
    return out


def agrupar(notas):
    grupos = []
    for n in sorted(notas, key=lambda n: n["fecha"] or dt.datetime.min.replace(tzinfo=dt.timezone.utc), reverse=True):
        p = palabras(n["titulo"])
        for g in grupos:
            inter = len(p & g["pal"])
            if inter >= 3 or (p and inter / len(p | g["pal"]) >= 0.4):
                g["notas"].append(n)
                g["pal"] |= p
                break
        else:
            grupos.append({"pal": set(p), "notas": [n]})
    return grupos


def puntuar(g, cfg, ahora, horas):
    pesos = {norm(k): v for k, v in cfg.get("pesos", {}).items()}
    texto = norm(" ".join(n["titulo"] + " " + n["resumen"] for n in g["notas"]))
    medios = {n["medio"] for n in g["notas"]}
    pts = 2.0 * min(len(medios), 6)  # cuántos medios lo traen
    claves = sorted({k for k in pesos if k in texto}, key=lambda k: -pesos[k])
    pts += sum(pesos[k] for k in claves[:4])
    f = max((n["fecha"] for n in g["notas"] if n["fecha"]), default=None)
    if f:
        edad = (ahora - f).total_seconds() / 3600
        pts += max(0.0, 6 * (1 - edad / horas))
    return round(pts, 1), claves, f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--horas", type=float, default=36)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--rss", action="append", default=[], help="archivo RSS local (se puede repetir)")
    ap.add_argument("--salida", default=os.path.join(ROOT, "noticias"))
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(ROOT, "config", "fuentes.json"), encoding="utf-8"))

    fuentes = [("archivo", p) for p in a.rss]
    if not a.rss:
        dias = max(1, int(round(a.horas / 24)))
        fuentes += [(q, GNEWS.format(q=urllib.parse.quote(f"{q} when:{dias}d"))) for q in cfg.get("busquedas", [])]
        fuentes += [(u, u) for u in cfg.get("rss", [])]

    notas, ok, fallos = [], 0, []
    for nombre, url in fuentes:
        try:
            xml = open(url, "rb").read() if nombre == "archivo" else descargar(url)
            notas += leer_feed(xml, "" if nombre == "archivo" else urllib.parse.urlparse(url).netloc)
            ok += 1
        except Exception as e:  # una fuente caída no detiene a las demás
            fallos.append(f"{nombre[:40]}: {e}")
    for f in fallos:
        log("no se pudo leer", f)
    if not ok:
        log("ninguna fuente respondió; usa búsqueda web para elegir el tema")
        sys.exit(2)

    ahora = dt.datetime.now(dt.timezone.utc)
    limite = ahora - dt.timedelta(hours=a.horas)
    excl = [norm(x) for x in cfg.get("excluir", [])]
    vistos, filtradas = set(), []
    for n in notas:
        clave = norm(n["titulo"])[:90]
        if clave in vistos or not n["titulo"]:
            continue
        if n["fecha"] and n["fecha"] < limite:
            continue
        if any(x in norm(n["titulo"] + " " + n["resumen"]) for x in excl):
            continue
        vistos.add(clave)
        filtradas.append(n)

    hechas = recientes()
    temas = []
    for g in agrupar(filtradas):
        pts, claves, f = puntuar(g, cfg, ahora, a.horas)
        parecidas = [i for i, p in hechas if len(g["pal"] & p) >= 4]
        ns = sorted(g["notas"], key=lambda n: n["fecha"] or limite, reverse=True)
        temas.append({
            "puntos": pts, "titulo": ns[0]["titulo"], "fecha": f.isoformat() if f else None,
            "medios": sorted({n["medio"] for n in ns}), "claves": claves, "juarez": any(k in claves for k in ("juarez", "bravos")),
            "posible_repetido": parecidas,
            "notas": [{k: (v.isoformat() if isinstance(v, dt.datetime) else v) for k, v in n.items()} for n in ns[:5]],
        })
    temas.sort(key=lambda t: (-t["puntos"], t["fecha"] or ""))
    temas = temas[: a.top]

    os.makedirs(a.salida, exist_ok=True)
    loc = dt.datetime.now().astimezone()
    base = os.path.join(a.salida, loc.strftime("%Y-%m-%d"))
    json.dump({"generado": loc.isoformat(timespec="minutes"), "horas": a.horas, "fuentes_ok": ok,
               "fuentes_fallidas": fallos, "temas": temas}, open(base + ".json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    md = [f"# Noticias Liga MX — {loc.strftime('%d/%m/%Y %H:%M')}",
          f"Últimas {a.horas:g} h · {len(filtradas)} notas de {ok} fuentes · ordenadas por relevancia para Señor Fútbol.",
          "Son pistas: confirma cada dato leyendo la nota antes de usarlo.", ""]
    for k, t in enumerate(temas, 1):
        marcas = (" ⭐ JUÁREZ" if t["juarez"] else "") + (f" ⚠️ parecido a {', '.join(t['posible_repetido'])}" if t["posible_repetido"] else "")
        hora = dt.datetime.fromisoformat(t["fecha"]).astimezone().strftime("%d/%m %H:%M") if t["fecha"] else "s/f"
        md.append(f"## {k}. {t['titulo']}{marcas}")
        md.append(f"{t['puntos']} pts · {hora} · {len(t['medios'])} medio(s): {', '.join(t['medios'][:5])}"
                  + (f" · claves: {', '.join(t['claves'])}" if t["claves"] else ""))
        for n in t["notas"][:3]:
            md.append(f"- [{n['medio']}] {n['titulo']} — {n['link']}")
        md.append("")
    open(base + ".md", "w", encoding="utf-8").write("\n".join(md))
    print("\n".join(md[:2] + [""] + [f"{k}. {t['titulo']} ({t['puntos']} pts{', JUÁREZ' if t['juarez'] else ''})" for k, t in enumerate(temas, 1)]))
    log("listo:", base + ".md")


if __name__ == "__main__":
    main()
