#!/usr/bin/env python3
"""Sube un video ya generado a Facebook, Instagram, YouTube y TikTok por sus API oficiales.

Lo usa engine/publicador.py (GitHub Actions). Ningún token se imprime: los errores se recortan
para no incluir la URL con parámetros.
"""
import json, os, time, urllib.error, urllib.parse, urllib.request

GRAPH = "https://graph.facebook.com/" + os.environ.get("FB_GRAPH_VERSION", "v23.0")


class ErrorRed(Exception):
    pass


def http(method, url, data=None, headers=None, raw=None, js=None, con_headers=False, timeout=900):
    h = dict(headers or {})
    if js is not None:
        body = json.dumps(js).encode()
        h.setdefault("Content-Type", "application/json; charset=UTF-8")
    elif raw is not None:
        body = raw
    elif data is not None:
        body = urllib.parse.urlencode(data).encode()
    else:
        body = None
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            txt = resp.read().decode() or "{}"
            out = json.loads(txt) if txt.lstrip()[:1] in "{[" else {"_texto": txt[:300]}
            return (out, resp.headers) if con_headers else out
    except urllib.error.HTTPError as e:
        raise ErrorRed(f"HTTP {e.code} en {url.split('?')[0]}: {e.read().decode(errors='replace')[:500]}")
    except urllib.error.URLError as e:
        raise ErrorRed(f"Sin conexión con {url.split('?')[0]}: {e.reason}")


def _bytes(mp4):
    with open(mp4, "rb") as f:
        return f.read()


# ---------------- Facebook (Reels de página) ----------------
def facebook_reel(page_id, token, mp4, texto, ts=None):
    """ts = epoch para programar (>15 min en el futuro); None = publicar ya."""
    data = _bytes(mp4)
    start = http("POST", f"{GRAPH}/{page_id}/video_reels", {"upload_phase": "start", "access_token": token})
    vid = start["video_id"]
    up = http("POST", start.get("upload_url", f"https://rupload.facebook.com/video-upload/{GRAPH.rsplit('/', 1)[1]}/{vid}"),
              headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data))}, raw=data)
    if not up.get("success", True):
        raise ErrorRed(f"Facebook no aceptó la subida: {up}")
    fin = {"access_token": token, "video_id": vid, "upload_phase": "finish", "description": texto}
    fin.update({"video_state": "SCHEDULED", "scheduled_publish_time": str(int(ts))} if ts else {"video_state": "PUBLISHED"})
    r = http("POST", f"{GRAPH}/{page_id}/video_reels", fin)
    if not r.get("success", True):
        raise ErrorRed(f"Facebook no aceptó la publicación: {r}")
    return {"id": vid, "url": f"https://www.facebook.com/reel/{vid}", "programado": bool(ts)}


# ---------------- Instagram (Reels, subida reanudable) ----------------
def instagram_reel(ig_id, token, mp4, texto):
    data = _bytes(mp4)
    c = http("POST", f"{GRAPH}/{ig_id}/media", {"media_type": "REELS", "upload_type": "resumable", "caption": texto[:2200],
                                                "share_to_feed": "true", "access_token": token})
    http("POST", c["uri"], headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data))}, raw=data)
    q = urllib.parse.quote(token)
    for _ in range(60):
        st = http("GET", f"{GRAPH}/{c['id']}?fields=status_code,status&access_token={q}")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise ErrorRed(f"Instagram no pudo procesar el video: {st.get('status')}")
        time.sleep(10)
    else:
        raise ErrorRed("Instagram tardó más de 10 min en procesar el video")
    p = http("POST", f"{GRAPH}/{ig_id}/media_publish", {"creation_id": c["id"], "access_token": token})
    try:
        link = http("GET", f"{GRAPH}/{p['id']}?fields=permalink&access_token={q}").get("permalink")
    except ErrorRed:
        link = None
    return {"id": p["id"], "url": link}


# ---------------- YouTube (Shorts) ----------------
def youtube_short(client_id, client_secret, refresh, mp4, titulo, descripcion, publish_at=None, tags=(), categoria="22"):
    """publish_at = RFC3339 UTC para programar; None = público ya.
    Ojo: si el proyecto de Google Cloud no tiene la auditoría de la API de YouTube, YouTube deja el video PRIVADO."""
    tok = http("POST", "https://oauth2.googleapis.com/token", {"client_id": client_id, "client_secret": client_secret,
                                                                "refresh_token": refresh, "grant_type": "refresh_token"})["access_token"]
    data = _bytes(mp4)
    status = {"privacyStatus": "private" if publish_at else "public", "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at
    meta = {"snippet": {"title": titulo[:100], "description": descripcion[:4900], "tags": list(tags)[:15],
                        "categoryId": categoria, "defaultLanguage": "es", "defaultAudioLanguage": "es-419"}, "status": status}
    _, hdr = http("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", js=meta,
                  headers={"Authorization": f"Bearer {tok}", "X-Upload-Content-Type": "video/mp4",
                           "X-Upload-Content-Length": str(len(data))}, con_headers=True)
    v = http("PUT", hdr["Location"], raw=data, headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"})
    return {"id": v["id"], "url": f"https://youtube.com/shorts/{v['id']}", "privacidad": v.get("status", {}).get("privacyStatus"),
            "programado": bool(publish_at)}


# ---------------- TikTok (a la bandeja de borradores) ----------------
def tiktok_borrador(client_key, client_secret, refresh, mp4):
    """Manda el video a la bandeja de TikTok (notificación en la app) para terminar de publicarlo con un toque."""
    t = http("POST", "https://open.tiktokapis.com/v2/oauth/token/", {"client_key": client_key, "client_secret": client_secret,
                                                                      "grant_type": "refresh_token", "refresh_token": refresh},
             headers={"Content-Type": "application/x-www-form-urlencoded"})
    if "access_token" not in t:
        raise ErrorRed(f"TikTok no renovó el acceso: {t.get('error_description') or t.get('error') or t}")
    acc = t["access_token"]
    data = _bytes(mp4)
    n = len(data)
    init = http("POST", "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
                js={"source_info": {"source": "FILE_UPLOAD", "video_size": n, "chunk_size": n, "total_chunk_count": 1}},
                headers={"Authorization": f"Bearer {acc}"})
    if init.get("error", {}).get("code", "ok") != "ok":
        raise ErrorRed(f"TikTok: {init['error']}")
    http("PUT", init["data"]["upload_url"], raw=data,
         headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{n - 1}/{n}", "Content-Length": str(n)})
    return {"id": init["data"].get("publish_id"), "url": None, "nota": "En tu bandeja de TikTok: ábrela y toca Publicar",
            "refresh_cambio": t.get("refresh_token") not in (None, refresh)}
