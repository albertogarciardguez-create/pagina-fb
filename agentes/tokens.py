#!/usr/bin/env python3
"""Saca los valores para los secretos de GitHub (córrelo en tu Mac; ver agentes/CONFIGURAR.md).

  python3 agentes/tokens.py facebook   # tokens de página que no caducan + IDs de página e Instagram
  python3 agentes/tokens.py youtube    # refresh token de un canal de YouTube (repite por canal)
  python3 agentes/tokens.py tiktok     # refresh token de una cuenta de TikTok (repite por cuenta)

Nada se guarda en disco ni se sube al repositorio: copia cada valor directo a GitHub > Settings >
Secrets and variables > Actions.
"""
import getpass, http.server, json, secrets, sys, urllib.parse, urllib.request, webbrowser

G = "https://graph.facebook.com/v23.0"


def pedir(t, oculto=False):
    return (getpass.getpass if oculto else input)(t + ": ").strip()


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode())


def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def facebook():
    print("1) En developers.facebook.com/tools/explorer elige tu app y genera un token de USUARIO con:\n"
          "   pages_show_list, pages_read_engagement, pages_manage_posts, business_management,\n"
          "   instagram_basic, instagram_content_publish\n")
    app, sec = pedir("App ID"), pedir("App Secret", True)
    corto = pedir("Token de usuario (corto)", True)
    largo = get(f"{G}/oauth/access_token?" + urllib.parse.urlencode(
        {"grant_type": "fb_exchange_token", "client_id": app, "client_secret": sec, "fb_exchange_token": corto}))["access_token"]
    pags = get(f"{G}/me/accounts?fields=name,id,access_token,instagram_business_account&limit=50&access_token={largo}")["data"]
    for p in pags:
        nombre = p["name"].lower()
        pre = "SF" if "fútbol" in nombre or "futbol" in nombre else ("IR" if "impulso" in nombre else "??")
        print(f"\n=== {p['name']} → prefijo {pre} ===")
        print(f"{pre}_FB_PAGE_ID = {p['id']}")
        print(f"{pre}_FB_TOKEN   = {p['access_token']}")
        ig = (p.get("instagram_business_account") or {}).get("id")
        print(f"{pre}_IG_ID      = {ig or '(esta página no tiene Instagram profesional vinculado)'}")
    print("\nLos tokens de página que salen de un token de usuario largo no caducan (salvo que cambies tu contraseña o quites permisos).")


def youtube():
    print("Necesitas un cliente OAuth tipo 'App de escritorio' en console.cloud.google.com (API YouTube Data v3 activada).")
    cid, sec = pedir("YT_CLIENT_ID"), pedir("YT_CLIENT_SECRET", True)
    port, estado = 8765, secrets.token_urlsafe(16)
    redir = f"http://127.0.0.1:{port}/"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redir, "response_type": "code", "access_type": "offline", "prompt": "consent",
        "scope": "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly", "state": estado})
    codigo = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == estado and "code" in q:
                codigo["c"] = q["code"][0]
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write("Listo, ya puedes cerrar esta pestaña y volver a la terminal.".encode())

        def log_message(self, *a):
            pass

    print("\nSe abrirá el navegador: entra con tu cuenta y ELIGE EL CANAL correcto (Impulso_Real o el de Señor Fútbol).")
    webbrowser.open(url)
    print("Si no se abre, copia esta liga:\n" + url)
    srv = http.server.HTTPServer(("127.0.0.1", port), H)
    while "c" not in codigo:
        srv.handle_request()
    t = post("https://oauth2.googleapis.com/token", {"code": codigo["c"], "client_id": cid, "client_secret": sec,
                                                     "redirect_uri": redir, "grant_type": "authorization_code"})
    canal = get("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true&access_token=" + t["access_token"])
    nombre = canal.get("items", [{}])[0].get("snippet", {}).get("title", "?")
    print(f"\nCanal autorizado: {nombre}")
    print("Guárdalo como IR_YT_REFRESH (Impulso Real) o SF_YT_REFRESH (Señor Fútbol):")
    print(t.get("refresh_token", "(no llegó refresh token: borra el acceso de la app en myaccount.google.com/permissions y repite)"))


def tiktok():
    print("Necesitas una app en developers.tiktok.com con Login Kit + Content Posting API (permiso video.upload).\n"
          "En Login Kit registra como Redirect URI: https://github.com/albertogarciardguez-create/pagina-fb")
    key, sec = pedir("TIKTOK_CLIENT_KEY"), pedir("TIKTOK_CLIENT_SECRET", True)
    redir = "https://github.com/albertogarciardguez-create/pagina-fb"
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
        "client_key": key, "scope": "user.info.basic,video.upload", "response_type": "code",
        "redirect_uri": redir, "state": secrets.token_urlsafe(8)})
    webbrowser.open(url)
    print("\nAutoriza con la cuenta de TikTok correcta. Te mandará a GitHub; copia la dirección COMPLETA de la barra.\n" + url)
    vuelta = pedir("Pega aquí la dirección a la que llegaste")
    code = urllib.parse.parse_qs(urllib.parse.urlparse(vuelta).query)["code"][0]
    t = post("https://open.tiktokapis.com/v2/oauth/token/", {"client_key": key, "client_secret": sec, "code": code,
                                                             "grant_type": "authorization_code", "redirect_uri": redir})
    print("\nGuárdalo como SF_TIKTOK_REFRESH o IR_TIKTOK_REFRESH (dura 365 días):")
    print(t.get("refresh_token", t))


if __name__ == "__main__":
    {"facebook": facebook, "youtube": youtube, "tiktok": tiktok}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
