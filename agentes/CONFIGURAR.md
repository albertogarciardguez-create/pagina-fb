# Configurar las cuentas (una sola vez, ~40 min)

Los secretos se guardan en **GitHub → repositorio pagina-fb → Settings → Secrets and variables → Actions → New repository secret**. Nunca en el repositorio, en la hoja ni en un chat. Mientras falten los de una red, el publicador la salta y sigue con las demás.

Los valores se sacan con `python3 agentes/tokens.py <red>` en tu Mac (desde la carpeta del repo).

## 1. Facebook + Instagram (las dos páginas) — 15 min

1. Cada cuenta de Instagram debe ser **profesional** (Creador o Empresa) y estar **vinculada a su página** (Meta Business Suite → Configuración → Cuentas de Instagram).
2. En [developers.facebook.com](https://developers.facebook.com/apps) → Crear app → caso de uso **“Administrar todo en tu página”** y agrega **“Instagram: administrar mensajes y contenido”**. Puede quedarse en modo desarrollo: tú eres administrador de la app y de las páginas.
3. En [Graph API Explorer](https://developers.facebook.com/tools/explorer) elige tu app → “Obtener token de usuario” con: `pages_show_list`, `pages_read_engagement`, `read_insights`, `pages_manage_posts`, `business_management`, `instagram_basic`, `instagram_content_publish`. Marca las dos páginas y las dos cuentas de Instagram.
4. `python3 agentes/tokens.py facebook` → pega App ID, App Secret y el token. Te imprime, por página:

| Secreto | Señor Fútbol | Impulso Real |
|---|---|---|
| ID de página | `SF_FB_PAGE_ID` | `IR_FB_PAGE_ID` |
| Token de página (no caduca) | `SF_FB_TOKEN` | `IR_FB_TOKEN` |
| ID de Instagram | `SF_IG_ID` | `IR_IG_ID` |

## 2. YouTube Shorts — 15 min

1. [console.cloud.google.com](https://console.cloud.google.com) → proyecto nuevo → activa **YouTube Data API v3**.
2. Pantalla de consentimiento OAuth: Externa, tu correo; en **Estado de publicación pon “En producción”** (si se queda en “Prueba”, el acceso caduca cada 7 días). Google mostrará “app no verificada”: Avanzado → Continuar.
3. Credenciales → ID de cliente OAuth → **App de escritorio** → guarda `YT_CLIENT_ID` y `YT_CLIENT_SECRET`.
4. `python3 agentes/tokens.py youtube` → elige el canal **Impulso_Real** → guarda `IR_YT_REFRESH`. Si quieres Shorts de Señor Fútbol, repite eligiendo ese canal → `SF_YT_REFRESH`.
5. **Importante:** YouTube deja como **privados** los videos subidos por proyectos nuevos hasta que pasan su auditoría. Mientras tanto se suben y quedan en YouTube Studio para que los hagas públicos con un clic. Pide la auditoría (gratis) en [este formulario](https://support.google.com/youtube/contact/yt_api_form); al aprobarla, salen programados solos.

## 3. TikTok — opcional, 10 min

1. [developers.tiktok.com](https://developers.tiktok.com) → Manage apps → app nueva → agrega **Login Kit** y **Content Posting API** (permisos `user.info.basic`, `video.upload`).
2. En Login Kit registra el Redirect URI `https://github.com/albertogarciardguez-create/pagina-fb`.
3. Guarda `TIKTOK_CLIENT_KEY` y `TIKTOK_CLIENT_SECRET`.
4. Usa el modo **Sandbox** con tus cuentas como usuarios de prueba; si TikTok no permite subir así, manda la app a revisión.
5. `python3 agentes/tokens.py tiktok` → autoriza con la cuenta de cada marca → `SF_TIKTOK_REFRESH` / `IR_TIKTOK_REFRESH` (duran 365 días).
6. El video llega a tu **bandeja de TikTok** a la hora programada: ábrelo, pon un sonido en tendencia si quieres y toca Publicar. TikTok no permite publicar 100 % solo a apps sin auditoría.

## 4. Revisar que funcione

GitHub → Actions → **Publicador de redes** → Run workflow. En el resumen de cada corrida aparece una tabla con ✅ / ⏭️ (falta secreto) / ❌ (error) por red.
