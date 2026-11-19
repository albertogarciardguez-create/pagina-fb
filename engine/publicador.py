#!/usr/bin/env python3
"""Publicador de la cola (corre en GitHub Actions; ver agentes/AGENTES.md).

Cada archivo cola/<id>.json es una publicación autorizada:
  {"id": "2026-11-19-sf-a-bravos", "pagina": "senorfutbol" | "impulsoreal",
   "motor": "reel" | "diorama" | "anime" | "largo", "historia": "stories/....json",
   "hora": "2026-11-19 13:15",                       # hora de Ciudad Juárez
   "redes": ["facebook", "instagram", "youtube", "tiktok"],
   "titulo": "Título para YouTube (opcional)", "texto": "texto del post (opcional; si no, sale de post.txt)"}
Si la historia trae "redes_textos" {"facebook": "...", "instagram": "...", "youtube": {"titulo", "descripcion"},
"tiktok": "..."}, cada red usa su texto (TikTok va a la bandeja: su texto queda en el estado para pegarlo).

El estado de cada una queda en cola/estado/<id>.json. El video se genera una sola vez y se guarda como
archivo del release "cola" del repositorio, para que las corridas siguientes no lo vuelvan a generar.

  python3 engine/publicador.py --revisar     # imprime trabajo=si|no y generar=si|no (para el workflow)
  python3 engine/publicador.py               # genera y publica lo que toca
  python3 engine/publicador.py --simular     # igual, pero sin llamar a las API ni generar (prueba)
"""
import glob, json, os, subprocess, sys, time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import redes  # noqa: E402

TZ = ZoneInfo("America/Ciudad_Juarez")
MOTORES = {"reel": "engine/build.py", "diorama": "engine/build_diorama.py", "anime": "engine/build_anime.py", "largo": "engine/build_largo.py"}
PREF = {"senorfutbol": "SF", "impulsoreal": "IR"}
ESPERAN_HORA = {"instagram": 5 * 60, "tiktok": 30 * 60}  # se mandan hasta (hora - margen); FB y YouTube se programan desde ya
MAX_INTENTOS = 3
CADUCA = 36 * 3600  # una publicación que no salió 36 h después de su hora ya no se manda (noticias viejas)
SIMULAR = "--simular" in sys.argv


def log(*a):
    print("[publicador]", *a, flush=True)


def env(n):
    return os.environ.get(n, "").strip()


def epoch(hora):
    return datetime.strptime(hora, "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp()


def hora_red(item, red):
    """Cada red puede tener su propia hora: "horas": {"tiktok": "2026-11-20 19:00"}; si no, usa "hora"."""
    return epoch(item.get("horas", {}).get(red, item["hora"]))


def metricas_pendientes():
    """Una vez al día, después de las 6 am, si hay secretos de Meta o YouTube."""
    if not (env("SF_FB_TOKEN") or env("IR_FB_TOKEN") or env("YT_CLIENT_ID")) or datetime.now(TZ).hour < 6:
        return False
    p = os.path.join(ROOT, "cola", "metricas", "seguidores.json")
    hoy = datetime.now(TZ).strftime("%Y-%m-%d")
    return not (os.path.exists(p) and hoy in json.load(open(p, encoding="utf-8")))


def estado_path(i):
    return os.path.join(ROOT, "cola", "estado", f"{i}.json")


def cargar_estado(i):
    p = estado_path(i)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"redes": {}}


def guardar_estado(i, est):
    os.makedirs(os.path.dirname(estado_path(i)), exist_ok=True)
    est["actualizado"] = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    json.dump(est, open(estado_path(i), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def credenciales(red, pagina):
    p = PREF[pagina]
    need = {"facebook": [f"{p}_FB_PAGE_ID", f"{p}_FB_TOKEN"],
            "instagram": [f"{p}_IG_ID", f"{p}_FB_TOKEN"],
            "youtube": ["YT_CLIENT_ID", "YT_CLIENT_SECRET", f"{p}_YT_REFRESH"],
            "tiktok": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", f"{p}_TIKTOK_REFRESH"]}[red]
    faltan = [n for n in need if not env(n)]
    return (None, faltan) if faltan else ([env(n) for n in need], [])


def pendientes(item, est, ahora):
    """Redes que toca intentar en esta corrida."""
    out = []
    for red in item.get("redes", []):
        ts = hora_red(item, red)
        r = est["redes"].get(red, {})
        if r.get("ok") or r.get("omitido") or r.get("intentos", 0) >= MAX_INTENTOS:
            continue
        if ahora < ts - ESPERAN_HORA.get(red, 10 ** 9):
            continue
        out.append(red)
    return out


def terminado(item, est):
    return all(est["redes"].get(r, {}).get("ok") or est["redes"].get(r, {}).get("omitido")
               or est["redes"].get(r, {}).get("intentos", 0) >= MAX_INTENTOS for r in item.get("redes", []))


def items():
    for f in sorted(glob.glob(os.path.join(ROOT, "cola", "*.json"))):
        try:
            it = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            log("JSON inválido:", os.path.basename(f), e)
            continue
        it.setdefault("id", os.path.basename(f)[:-5])
        if it.get("pagina") not in PREF or it.get("motor", "reel") not in MOTORES or not it.get("hora"):
            log("item incompleto (pagina/motor/hora):", it["id"])
            continue
        yield it


def gh(*args, check=True):
    return subprocess.run(["gh", *args], cwd=ROOT, check=check, capture_output=True, text=True)


def asegurar_video(item, est):
    """Devuelve (mp4, texto). Genera el video si no existe; si ya se generó en otra corrida, lo baja del release."""
    historia = json.load(open(os.path.join(ROOT, item["historia"]), encoding="utf-8"))
    sid = historia["id"]
    carpeta = os.path.join(ROOT, "salida", sid)
    mp4 = os.path.join(carpeta, f"{sid}.mp4")
    if not os.path.exists(mp4) and est.get("video") and not SIMULAR:
        os.makedirs(carpeta, exist_ok=True)
        r = gh("release", "download", "cola", "-p", f"{item['id']}.mp4", "-O", mp4, "--clobber", check=False)
        if r.returncode:
            log("no pude bajar el video del release; lo genero de nuevo:", r.stderr.strip()[:200])
    if not os.path.exists(mp4):
        if SIMULAR:
            return "(simulado).mp4", item.get("texto") or historia.get("post", "")
        log("generando", item["historia"], "con", MOTORES[item.get("motor", "reel")])
        r = subprocess.run([sys.executable, MOTORES[item.get("motor", "reel")], item["historia"]], cwd=ROOT,
                           capture_output=True, text=True)
        print(r.stdout[-3000:], r.stderr[-3000:], flush=True)
        if r.returncode:
            raise RuntimeError(f"el motor falló ({r.returncode}): " + (r.stderr or r.stdout)[-1200:])
        if "AVISO" in r.stdout + r.stderr:
            est["aviso"] = [l for l in (r.stdout + r.stderr).splitlines() if "AVISO" in l][-1][:300]
        gh("release", "view", "cola", check=False).returncode and gh(
            "release", "create", "cola", "--title", "Cola de publicación", "--notes",
            "Videos generados por el publicador automático (agentes/AGENTES.md).", check=False)
        tmp = os.path.join(carpeta, f"{item['id']}.mp4")
        if tmp != mp4:
            subprocess.run(["cp", mp4, tmp], check=True)
        r = gh("release", "upload", "cola", tmp, "--clobber", check=False)
        if r.returncode == 0:
            repo = env("GITHUB_REPOSITORY")
            est["video"] = f"https://github.com/{repo}/releases/download/cola/{item['id']}.mp4" if repo else True
        else:
            log("AVISO: no pude guardar el video en el release:", r.stderr.strip()[:200])
    post = os.path.join(carpeta, "post.txt")
    texto = item.get("texto") or (open(post, encoding="utf-8").read().split("\n---\n")[0].strip() if os.path.exists(post) else historia.get("post", ""))
    return mp4, texto


def textos_red(item):
    try:
        return json.load(open(os.path.join(ROOT, item["historia"]), encoding="utf-8")).get("redes_textos") or {}
    except Exception:
        return {}


def publicar(red, item, mp4, texto, cred, ahora):
    tr = textos_red(item).get(red)
    if red == "youtube" and isinstance(tr, dict):
        item = {**item, "titulo": item.get("titulo") or tr.get("titulo")}
        texto = tr.get("descripcion") or texto
    elif isinstance(tr, str) and tr.strip() and not item.get("texto"):
        texto = tr.strip()
    ts = hora_red(item, red)
    futuro = ts > ahora + 15 * 60
    if SIMULAR:
        return {"id": "simulado", "url": None, "programado": futuro and red in ("facebook", "youtube")}
    if red == "facebook":
        return redes.facebook_reel(cred[0], cred[1], mp4, texto, ts if futuro else None)
    if red == "instagram":
        return redes.instagram_reel(cred[0], cred[1], mp4, texto)
    if red == "youtube":
        titulo = item.get("titulo") or texto.split("\n")[0]
        titulo = titulo if "#shorts" in titulo.lower() else (titulo[:91].rstrip() + " #Shorts")
        tags = [h.lstrip("#") for h in texto.split() if h.startswith("#")]
        when = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if futuro else None
        return redes.youtube_short(*cred, mp4, titulo, texto, when, tags, "17" if item["pagina"] == "senorfutbol" else "22")
    if red == "tiktok":
        res = redes.tiktok_borrador(*cred, mp4)
        return {**(res or {}), "texto_para_pegar": texto}
    raise ValueError(red)


def main():
    ahora = time.time()
    revisar = "--revisar" in sys.argv
    trabajo = generar = False
    resumen = []
    for item in items():
        est = cargar_estado(item["id"])
        if est.get("estado") in ("completo", "caducado"):
            continue
        ts = epoch(item["hora"])
        if ahora > ts + CADUCA and not any(r.get("ok") for r in est["redes"].values()):
            est["estado"] = "caducado"
            if not revisar:
                guardar_estado(item["id"], est)
                log("caducado (pasaron más de 36 h de su hora):", item["id"])
            trabajo = True
            continue
        reds = pendientes(item, est, ahora)
        if not reds:
            continue
        trabajo = True
        if not est.get("video"):
            generar = True
        if revisar:
            continue
        try:
            mp4, texto = asegurar_video(item, est)
        except Exception as e:
            est["error_video"] = str(e)[-1500:]
            est["intentos_video"] = est.get("intentos_video", 0) + 1
            if est["intentos_video"] >= MAX_INTENTOS:
                est["estado"] = "error"
            guardar_estado(item["id"], est)
            log("ERROR al generar", item["id"], e)
            continue
        for red in reds:
            cred, faltan = credenciales(red, item["pagina"])
            r = est["redes"].get(red, {})
            if cred is None and not SIMULAR:
                est["redes"][red] = {"omitido": "faltan secretos: " + ", ".join(faltan)}
                log(item["id"], red, "omitido (faltan secretos)")
                continue
            try:
                res = publicar(red, item, mp4, texto, cred, ahora)
                est["redes"][red] = {"ok": True, **res, "fecha": datetime.now(TZ).strftime("%Y-%m-%d %H:%M")}
                log(item["id"], red, "OK", res.get("url") or "")
            except Exception as e:
                est["redes"][red] = {"ok": False, "error": str(e)[:500], "intentos": r.get("intentos", 0) + 1}
                log(item["id"], red, "ERROR", str(e)[:300])
        if terminado(item, est):
            est["estado"] = "completo"
        guardar_estado(item["id"], est)
        resumen.append((item, est))
    medir = metricas_pendientes()
    if revisar and env("GITHUB_STEP_SUMMARY"):
        nombres = [f"{p}_{n}" for p in ("SF", "IR") for n in ("FB_PAGE_ID", "FB_TOKEN", "IG_ID", "YT_REFRESH", "TIKTOK_REFRESH")]
        nombres += ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"]
        with open(env("GITHUB_STEP_SUMMARY"), "a", encoding="utf-8") as f:
            f.write("### Secretos que ve el publicador\n\n" + " · ".join(f"{n} {'✅' if env(n) else '—'}" for n in nombres) + "\n\n")
    if revisar:
        print(f"trabajo={'si' if trabajo or medir else 'no'}")
        print(f"generar={'si' if generar else 'no'}")
        return
    if medir and not SIMULAR:
        try:
            import metricas
            metricas.main()
            log("indicadores actualizados: cola/metricas/RESUMEN.md")
        except Exception as e:
            log("AVISO: no pude actualizar indicadores:", str(e)[:300])
    if resumen and env("GITHUB_STEP_SUMMARY"):
        with open(env("GITHUB_STEP_SUMMARY"), "a", encoding="utf-8") as f:
            f.write("| Publicación | Hora | Red | Resultado |\n|---|---|---|---|\n")
            for it, est in resumen:
                for red, r in est["redes"].items():
                    res = "✅ " + (r.get("url") or "") if r.get("ok") else ("⏭️ " + r["omitido"] if r.get("omitido") else "❌ " + r.get("error", "")[:120])
                    f.write(f"| {it['id']} | {it['hora']} | {red} | {res} |\n")


if __name__ == "__main__":
    main()
