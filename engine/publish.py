#!/usr/bin/env python3
"""Programa un reel en la página de Facebook con la Reels Publishing API de Meta.

Uso:
  FB_PAGE_ID=... FB_PAGE_TOKEN=... python3 engine/publish.py salida/<id>/<id>.mp4 salida/<id>/post.txt "2026-10-17 13:15"

- La hora es de Ciudad Juárez y debe estar al menos 15 minutos en el futuro (Meta pide >10 min y <29 días).
- El texto del post se toma de post.txt, sin la sección de fuentes.
- Requiere acceso de red a graph.facebook.com y rupload.facebook.com.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

GRAPH = "https://graph.facebook.com/" + os.environ.get("FB_GRAPH_VERSION", "v23.0")
try:
    TZ = ZoneInfo("America/Ciudad_Juarez")
except Exception:
    TZ = ZoneInfo("America/Denver")


def req(method, url, data=None, headers=None, raw=None):
    body = raw if raw is not None else (urllib.parse.urlencode(data).encode() if data else None)
    r = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"Error de Facebook ({e.code}): {e.read().decode()[:600]}")


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    video, post_path, when = sys.argv[1], sys.argv[2], sys.argv[3]
    page, token = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
    if not page or not token:
        sys.exit("Faltan FB_PAGE_ID y FB_PAGE_TOKEN")
    text = open(post_path, encoding="utf-8").read().split("\n---\n")[0].strip()
    ts = int(datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=TZ).timestamp())
    if ts < time.time() + 15 * 60:
        sys.exit(f"La hora {when} ya pasó o está a menos de 15 minutos; elige una más tarde.")
    size = os.path.getsize(video)
    start = req("POST", f"{GRAPH}/{page}/video_reels", {"upload_phase": "start", "access_token": token})
    vid = start["video_id"]
    up = req("POST", start.get("upload_url", f"https://rupload.facebook.com/video-upload/{GRAPH.rsplit('/', 1)[1]}/{vid}"),
             headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)},
             raw=open(video, "rb").read())
    if not up.get("success", True):
        sys.exit(f"Falló la subida: {up}")
    fin = req("POST", f"{GRAPH}/{page}/video_reels", {
        "access_token": token, "video_id": vid, "upload_phase": "finish",
        "video_state": "SCHEDULED", "scheduled_publish_time": str(ts), "description": text})
    if not fin.get("success", True):
        sys.exit(f"Facebook no aceptó la programación: {fin}")
    for _ in range(20):
        st = req("GET", f"{GRAPH}/{vid}?fields=status&access_token={urllib.parse.quote(token)}")
        s = st.get("status", {})
        if s.get("video_status") in ("ready", "upload_complete") or s.get("processing_phase", {}).get("status") == "complete":
            break
        if s.get("video_status") == "error":
            sys.exit(f"Facebook reportó error al procesar: {s}")
        time.sleep(15)
    print(json.dumps({"ok": True, "video_id": vid, "programado_para": when, "zona": str(TZ)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
