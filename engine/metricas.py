#!/usr/bin/env python3
"""Junta los indicadores de cada publicación y de cada cuenta (lo corre el publicador ~1 vez al día).

Salida (en git, la leen los agentes):
  cola/metricas/publicaciones.json   indicadores por publicación y red (se actualiza 14 días tras publicar)
  cola/metricas/seguidores.json      seguidores por cuenta y día
  cola/metricas/RESUMEN.md           ranking de formatos, horarios y publicaciones por PUNTAJE

PUNTAJE (lo que buscan los agentes) = 10×seguidores nuevos + reproducciones/25 + 2×compartidos + 2×comentarios
                                       + 1×guardados + 0.5×reacciones
Si una red no da un dato, ese término vale 0. TikTok no da métricas sin auditoría: se excluye.
"""
import glob, json, os, sys, time, urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from redes import GRAPH, ErrorRed, http  # noqa: E402

TZ = ZoneInfo("America/Ciudad_Juarez")
DIR = os.path.join(ROOT, "cola", "metricas")
PESOS = {"seguidores": 10, "compartidos": 2, "comentarios": 2, "guardados": 1, "reacciones": 0.5}
VISTAS_POR_PUNTO = 25  # cada 25 reproducciones = 1 punto (vistas y seguidores son lo que lleva a monetizar)
# Meta retiró post_impressions_unique (v25, jun 2026); "views" (post_media_view) es la métrica que muestra el panel.
FB_MET = {"blue_reels_play_count": "reproducciones", "fb_reels_total_plays": "reproducciones_total",
          "post_video_followers": "seguidores", "post_video_avg_time_watched": "seg_promedio_vistos",
          "post_video_social_actions": "_social", "post_video_likes_by_reaction_type": "_reacciones"}
IG_MET = {"views": "reproducciones", "reach": "alcance", "likes": "reacciones", "comments": "comentarios",
          "shares": "compartidos", "saved": "guardados", "follows": "seguidores", "ig_reels_avg_watch_time": "ms_promedio_vistos"}


def env(n):
    return os.environ.get(n, "").strip()


def _q(t):
    return urllib.parse.quote(t)


def _insights(url_base, metricas, token):
    """Pide todas juntas; si Meta rechaza alguna, las pide una por una y se queda con las que sí existen."""
    out = {}
    try:
        data = http("GET", f"{url_base}?metric={','.join(metricas)}&access_token={_q(token)}").get("data", [])
    except ErrorRed:
        data = []
        for m in metricas:
            try:
                data += http("GET", f"{url_base}?metric={m}&access_token={_q(token)}").get("data", [])
            except ErrorRed:
                pass
    for d in data:
        v = (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value"))
        out[d["name"]] = v
    return out


FB_POST_MET = {"post_media_view": "vistas", "post_total_media_view_unique": "alcance"}


def facebook(vid, token):
    raw = _insights(f"{GRAPH}/{vid}/video_insights", list(FB_MET), token)
    try:  # vistas y alcance nuevos viven en el post del reel, no en el video
        pid = http("GET", f"{GRAPH}/{vid}?fields=post_id&access_token={_q(token)}").get("post_id")
        if pid:
            for k, v in _insights(f"{GRAPH}/{pid}/insights", list(FB_POST_MET), token).items():
                raw["post:" + k] = v
    except ErrorRed:
        pass
    m = {}
    for k, v in raw.items():
        n = FB_MET.get(k) or FB_POST_MET.get(k.replace("post:", "", 1))
        if n == "_reacciones" and isinstance(v, dict):
            m["reacciones"] = sum(v.values())
        elif n == "_social" and isinstance(v, dict):
            m["comentarios"] = v.get("COMMENT", v.get("comment", 0))
            m["compartidos"] = v.get("SHARE", v.get("share", 0))
        elif n and not n.startswith("_") and isinstance(v, (int, float)):
            m[n] = v
    if "seg_promedio_vistos" in m:  # Meta lo da en milisegundos
        m["seg_promedio_vistos"] = round(m["seg_promedio_vistos"] / 1000, 1)
    # Para el puntaje manda el número más alto que dé Meta (el panel cuenta "vistas")
    m["reproducciones"] = max(m.get("reproducciones", 0), m.get("reproducciones_total", 0), m.get("vistas", 0))
    return m


def instagram(mid, token):
    raw = _insights(f"{GRAPH}/{mid}/insights", list(IG_MET), token)
    return {IG_MET[k]: v for k, v in raw.items() if isinstance(v, (int, float))}


def youtube(vid, pref):
    cid, sec, ref = env("YT_CLIENT_ID"), env("YT_CLIENT_SECRET"), env(f"{pref}_YT_REFRESH")
    if not (cid and sec and ref):
        return {}
    tok = http("POST", "https://oauth2.googleapis.com/token", {"client_id": cid, "client_secret": sec,
                                                                "refresh_token": ref, "grant_type": "refresh_token"})["access_token"]
    it = http("GET", f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={vid}",
              headers={"Authorization": f"Bearer {tok}"}).get("items", [])
    s = it[0]["statistics"] if it else {}
    return {"reproducciones": int(s.get("viewCount", 0)), "reacciones": int(s.get("likeCount", 0)),
            "comentarios": int(s.get("commentCount", 0))}


def puntaje(m):
    return round(sum(PESOS[k] * m.get(k, 0) for k in PESOS) + m.get("reproducciones", 0) / VISTAS_POR_PUNTO, 1)


def seguidores(hoy):
    path = os.path.join(DIR, "seguidores.json")
    hist = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for pref, nombre in (("SF", "senorfutbol"), ("IR", "impulsoreal")):
        tok = env(f"{pref}_FB_TOKEN")
        if not tok:
            continue
        fila = hist.setdefault(hoy, {}).setdefault(nombre, {})
        try:
            if env(f"{pref}_FB_PAGE_ID"):
                p = http("GET", f"{GRAPH}/{env(pref + '_FB_PAGE_ID')}?fields=followers_count,fan_count&access_token={_q(tok)}")
                fila["facebook"] = p.get("followers_count", p.get("fan_count"))
            if env(f"{pref}_IG_ID"):
                fila["instagram"] = http("GET", f"{GRAPH}/{env(pref + '_IG_ID')}?fields=followers_count&access_token={_q(tok)}").get("followers_count")
        except ErrorRed as e:
            fila["error"] = str(e)[:200]
    for pref, nombre in (("SF", "senorfutbol"), ("IR", "impulsoreal")):
        cid, sec, ref = env("YT_CLIENT_ID"), env("YT_CLIENT_SECRET"), env(f"{pref}_YT_REFRESH")
        if not (cid and sec and ref):
            continue
        try:
            tok = http("POST", "https://oauth2.googleapis.com/token", {"client_id": cid, "client_secret": sec,
                                                                        "refresh_token": ref, "grant_type": "refresh_token"})["access_token"]
            it = http("GET", "https://www.googleapis.com/youtube/v3/channels?part=statistics&mine=true",
                      headers={"Authorization": f"Bearer {tok}"}).get("items", [{}])
            hist.setdefault(hoy, {}).setdefault(nombre, {})["youtube"] = int(it[0].get("statistics", {}).get("subscriberCount", 0))
        except (ErrorRed, KeyError, IndexError, ValueError):
            pass
    json.dump(hist, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return hist


def main():
    os.makedirs(DIR, exist_ok=True)
    ahora = datetime.now(TZ)
    path = os.path.join(DIR, "publicaciones.json")
    pubs = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for f in glob.glob(os.path.join(ROOT, "cola", "estado", "*.json")):
        iid = os.path.basename(f)[:-5]
        cola = os.path.join(ROOT, "cola", f"{iid}.json")
        if not os.path.exists(cola):
            continue
        item, est = json.load(open(cola, encoding="utf-8")), json.load(open(f, encoding="utf-8"))
        pref = {"senorfutbol": "SF", "impulsoreal": "IR"}.get(item.get("pagina"))
        hora = datetime.strptime(item["hora"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        dias = (ahora - hora).total_seconds() / 86400
        if dias < 0.5 or dias > 14 or not pref:
            continue
        p = pubs.setdefault(iid, {"pagina": item["pagina"], "hora": item["hora"], "dia": hora.strftime("%a"),
                                  "formato": item.get("formato") or item.get("motor"), "tema": item.get("tema", ""),
                                  "redes": {}})
        for red, r in est.get("redes", {}).items():
            if not r.get("ok") or not r.get("id") or red == "tiktok":
                continue
            try:
                if red == "facebook" and env(f"{pref}_FB_TOKEN"):
                    m = facebook(r["id"], env(f"{pref}_FB_TOKEN"))
                elif red == "instagram" and env(f"{pref}_FB_TOKEN"):
                    m = instagram(r["id"], env(f"{pref}_FB_TOKEN"))
                elif red == "youtube":
                    m = youtube(r["id"], pref)
                else:
                    continue
            except ErrorRed as e:
                m = {"error": str(e)[:200]}
            m["puntaje"] = puntaje(m)
            p["redes"][red] = m
        p["puntaje"] = round(sum(x.get("puntaje", 0) for x in p["redes"].values()), 1)
        p["medido"] = ahora.strftime("%Y-%m-%d %H:%M")
    json.dump(pubs, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hist = seguidores(ahora.strftime("%Y-%m-%d"))
    resumen(pubs, hist)


def _tabla(grupos, titulo):
    filas = sorted(((k, sum(v) / len(v), len(v)) for k, v in grupos.items()), key=lambda x: -x[1])
    out = [f"\n### {titulo}\n", "| | Puntaje promedio | Publicaciones |", "|---|---|---|"]
    out += [f"| {k} | {p:.1f} | {n} |" for k, p, n in filas]
    return out


def resumen(pubs, hist):
    out = [f"# Indicadores — actualizado {datetime.now(TZ):%Y-%m-%d %H:%M}",
           "Puntaje = 10×seguidores nuevos + reproducciones/25 + 2×compartidos + 2×comentarios + guardados + 0.5×reacciones (FB+IG+YT)."]
    for pag in ("senorfutbol", "impulsoreal"):
        ps = {k: v for k, v in pubs.items() if v["pagina"] == pag}
        if not ps:
            continue
        out.append(f"\n## {'Señor Fútbol' if pag == 'senorfutbol' else 'Impulso Real'}")
        fmt, hora, dia = {}, {}, {}
        for v in ps.values():
            fmt.setdefault(v["formato"] or "?", []).append(v.get("puntaje", 0))
            hora.setdefault(v["hora"][-5:], []).append(v.get("puntaje", 0))
            dia.setdefault(v["dia"], []).append(v.get("puntaje", 0))
        out += _tabla(fmt, "Por formato") + _tabla(hora, "Por hora") + _tabla(dia, "Por día")
        out += ["\n### Top 5 publicaciones", "| Publicación | Puntaje | FB | IG | YT |", "|---|---|---|---|---|"]
        for k, v in sorted(ps.items(), key=lambda x: -x[1].get("puntaje", 0))[:5]:
            c = lambda r: ", ".join(f"{a[:4]} {b}" for a, b in v["redes"].get(r, {}).items() if a != "puntaje") or "–"
            out.append(f"| {k} | {v.get('puntaje', 0)} | {c('facebook')} | {c('instagram')} | {c('youtube')} |")
    # candidatas a promoción pagada (config/anuncios.json): mejores de los últimos 7 días con seguidores o compartidos
    try:
        cfg = json.load(open(os.path.join(ROOT, "config", "anuncios.json"), encoding="utf-8"))
    except Exception:
        cfg = {"activo": False, "por_semana": 2}
    hace7 = (datetime.now(TZ).timestamp() - 7 * 86400)
    out.append(f"\n## Candidatas a promoción ({'ACTIVO' if cfg.get('activo') else 'apagado: $0, solo sugerencia'})")
    out += ["| Página | Publicación | Puntaje | Por qué |", "|---|---|---|---|"]
    for pag in ("senorfutbol", "impulsoreal"):
        ps = [(k, v) for k, v in pubs.items() if v["pagina"] == pag and
              datetime.strptime(v["hora"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp() >= hace7]
        for k, v in sorted(ps, key=lambda x: -x[1].get("puntaje", 0))[:cfg.get("por_semana", 2)]:
            seg = sum(r.get("seguidores", 0) for r in v["redes"].values())
            comp = sum(r.get("compartidos", 0) for r in v["redes"].values())
            out.append(f"| {pag} | {k} | {v.get('puntaje', 0)} | {seg} seguidores nuevos, {comp} compartidos |")
    out += camino(pubs, hist)
    dias = sorted(hist)[-8:]
    if dias:
        out += ["\n## Seguidores (últimos días)", "| Día | SF FB | SF IG | IR FB | IR IG |", "|---|---|---|---|---|"]
        for d in dias:
            g = lambda p, r: hist[d].get(p, {}).get(r, "–")
            out.append(f"| {d} | {g('senorfutbol', 'facebook')} | {g('senorfutbol', 'instagram')} | {g('impulsoreal', 'facebook')} | {g('impulsoreal', 'instagram')} |")
    open(os.path.join(DIR, "RESUMEN.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")


def camino(pubs, hist):
    """Avance hacia los requisitos de monetización de config/metas.json."""
    try:
        metas = json.load(open(os.path.join(ROOT, "config", "metas.json"), encoding="utf-8"))
    except Exception:
        return []
    ahora = datetime.now(TZ).timestamp()
    ult = hist[sorted(hist)[-1]] if hist else {}

    def vistas(pag, red, dias):
        return sum(v["redes"].get(red, {}).get("reproducciones", 0) for v in pubs.values() if v["pagina"] == pag and
                   datetime.strptime(v["hora"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp() >= ahora - dias * 86400)

    def pct(a, b):
        return f"{min(100, 100 * a / b):.0f} %" if b else "–"
    yt, tt, fb = metas["youtube"], metas["tiktok"], metas["facebook"]
    out = ["\n## Camino a monetizar", "| Página | Meta | Actual | Avance |", "|---|---|---|---|"]
    for pag, nom in (("senorfutbol", "SF"), ("impulsoreal", "IR")):
        a = ult.get(pag, {})
        fbs = a.get("facebook") or 0
        hito = next((h for h in fb["seguidores_hito"] if h > fbs), fb["seguidores_hito"][-1])
        out.append(f"| {nom} | Facebook: {hito:,} seguidores (hito) | {fbs:,} | {pct(fbs, hito)} |")
        ys, yv = a.get("youtube") or 0, vistas(pag, "youtube", 90)
        for n in ("nivel1", "nivel2"):
            m = yt[n]
            out.append(f"| {nom} | YouTube {m['nombre']}: {m['suscriptores']:,} subs + {m['vistas_shorts_90d']:,} vistas Shorts/90 d "
                       f"| {ys:,} subs · {yv:,} vistas | {pct(ys, m['suscriptores'])} subs · {pct(yv, m['vistas_shorts_90d'])} vistas |")
        out.append(f"| {nom} | TikTok {tt['nombre']}: {tt['seguidores']:,} seguidores + {tt['vistas_30d']:,} vistas/30 d (videos ≥1 min) "
                   f"| (TikTok no da datos por API: revisa TikTok Studio) | – |")
    out.append(f"\n> {yt['nivel2']['aviso']} {tt['aviso']} {fb['aviso']}")
    return out


if __name__ == "__main__":
    main()
