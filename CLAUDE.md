# Fábrica de reels — Señor Fútbol

Este repositorio genera los reels animados de la página de Facebook **Señor Fútbol** (facebook.com/senorfutbol), de Alberto García (Ciudad Juárez). Formato: video vertical 1080×1920, 25–35 s, gráficas animadas estilo papel/tinta, voz en off en español, música y efectos, subtítulos. **Nadie sale a cuadro.** Todo el contenido es original (sin escudos, fotos ni clips de transmisiones), para que la página pueda monetizar.

## Flujo diario (lo que debe hacer la tarea programada)

Cada mañana se entregan **2 videos de temas distintos**:

| Video | Contenido | Publicar |
|---|---|---|
| **A — La noticia** | Lo más fuerte de las últimas 24 h: resultado, polémica, crisis o racha, fichaje, declaración | **1:00–2:00 pm** |
| **B — El contexto** | Datos que generan debate: carrera por la Liguilla, tabla de goleo, rachas, cara a cara del próximo partido importante | **8:00–9:30 pm** (en fin de semana o días de partido: antes del partido más importante del día) |

Los dos videos no deben repetir tema, equipo protagonista ni gancho. Revisa `stories/` para no repetir los temas de los últimos 7 días.

1. **Instalar** (una vez por sesión): `bash setup.sh`
2. **Elegir los dos temas — Liga MX.** Busca en la web lo más relevante de las últimas 24–48 h y el calendario de partidos de hoy. Elige los temas con más potencial de debate para la afición mexicana. Si hay algo relevante de **FC Juárez**, dale prioridad en uno de los dos (la audiencia es de Juárez).
3. **Verificar datos.** Cada número y cada hecho debe salir de una fuente confiable (Mediotiempo, ESPN, Récord, TUDN, Claro Sports, El Informador, sitio oficial de la Liga MX, etc.). Usa WebFetch para leer la nota, no solo el titular. **Nunca inventes ni estimes un dato.** Si no puedes confirmarlo, no lo uses. Anota las URL en `sources`.
4. **Escribir las dos historias** en `stories/AAAA-MM-DD-a-tema-corto.json` y `stories/AAAA-MM-DD-b-tema-corto.json` (ver esquema abajo y el ejemplo `stories/2026-10-15-juarez-ultimo.json`).
   - 6 a 8 escenas, 25–35 s en total. Varía los tipos de escena entre los dos videos.
   - Escena 1 = gancho fuerte (dato impactante en los primeros 3 s).
   - Última escena = tipo `question`, con una pregunta polémica y "¡Te leo en los comentarios!" en la voz.
   - `say`: lo que dice la voz. Español mexicano, frases cortas, exclamaciones y preguntas para darle energía. **Números con letra** ("ochenta y cuatro"), nunca dígitos.
   - `captions`: el mismo texto partido en trozos de 2–5 palabras, con dígitos ("84") y `<em>palabra</em>` para resaltar en verde las palabras clave.
   - Textos en pantalla en MAYÚSCULAS y cortos.
5. **Revisar** cada una: `python3 engine/build.py stories/<archivo>.json --preview` y abre `salida/<id>/revision.png` con Read. Revisa que no haya textos encimados o cortados, que todo se lea y que los datos sean correctos. Si hay cuadros que no se distinguen bien, abre los individuales en `salida/<id>/revision/`. Corrige y repite.
6. **Generar los videos**: `python3 engine/build.py stories/<archivo>.json` (~3 min cada uno). Quedan en `salida/<id>/<id>.mp4` y el texto para publicar en `salida/<id>/post.txt`.
7. **Entregar a Alberto**: manda los dos MP4 con SendUserFile. En tu mensaje final, para cada video (A y B) incluye, listo para copiar: la hora exacta sugerida para programarlo hoy, el texto del post con hashtags y las fuentes.
8. **Guardar**: haz commit solo de los JSON de las historias (`salida/` está ignorada) y push a `main`. Si el push falla, continúa.

## Publicación automática (cuando esté configurada)

Después del paso 6, intenta programar cada video directo en la página:

1. Busca en Google Drive (conector) el archivo **`senorfutbol-facebook.json`** con `{"page_id": "...", "token": "..."}`. Nunca copies el token al repositorio, a un commit ni a tu mensaje.
2. Programa cada video con su hora del día (formato `AAAA-MM-DD HH:MM`, hora de Ciudad Juárez):
   `FB_PAGE_ID=<page_id> FB_PAGE_TOKEN=<token> python3 engine/publish.py salida/<id>/<id>.mp4 salida/<id>/post.txt "<hora>"`
3. Si salió bien, en tu mensaje final di que el video **ya quedó programado** y a qué hora (Alberto puede borrarlo en Meta Business Suite si algo no le gusta), y manda igual el MP4 con SendUserFile para que lo vea.
4. Si no existe el archivo, no hay acceso de red a Facebook o la API marca error (token vencido, permisos), entrega como siempre para publicar a mano y explica el error en una línea.

## Esquema de la historia

```json
{
  "id": "2026-10-16-tema",            // igual al nombre del archivo, sin .json
  "header": "LIGA MX · APERTURA 2026",  // línea pequeña bajo la marca
  "voice": "em_alex",                   // voz por defecto (la que eligió Alberto)
  "scenes": [ { "type": "...", "say": "...", "captions": ["..."], "bg": "18", ... } ],
  "post": "Texto para publicar con pregunta al final 👇",
  "hashtags": ["#LigaMX", "..."],
  "sources": ["https://..."]
}
```

Campos comunes de cada escena: `type`, `say`, `captions`, `bg` (palabra o número gigante de fondo, opcional), `speed` (velocidad de voz, 1.05–1.15, def. 1.12), `gap` (silencio después, s, def. 0.3). Colores permitidos donde aplique: `ink`, `green`, `red`.

| type | Para qué | Campos |
|---|---|---|
| `stats` | 1–3 datos gigantes | `items`: [{`n`, `label`, `color`}] |
| `table` | fragmento de tabla general | `title`, `sub`, `rows`: [{`pos`, `team`, `pts`, `hl`}] (máx. 6, `hl:true` resalta), `stamp` (sello rojo opcional) |
| `results` | racha de resultados | `title`, `seq`: ["W","D","L","Q"] (G/E/P, Q = pendiente; máx. 16), `labels` (opcional, def. J1..), `counter`: {`value`, `label` (usa \n), `color`, `plus`, `suffix`} |
| `scoreboard` | marcador con goles animados | `tag`, `home`, `away`, `goals`: [{`side`:"home"/"away", `at`: 0–1 = momento dentro de la línea de voz}], `note`, `noteHL`, `ballsFor` |
| `play` | jugada animada en media cancha | `minute`, `vs`, `sub`, `play`: corner_right, corner_left, cross_right, cross_left, shot, penalty, counter; `passer`, `scorer`, `result` |
| `count` | cuenta regresiva / lo que falta | `big`, `dots` (0–10), `sub`, `subLabel`, `subColor` |
| `headline` | titular de noticia (fichaje, declaración) | `tag`, `title` (usa \n), `sub` |
| `compare` | cara a cara entre dos equipos/jugadores | `title`, `left`, `right`, `rows`: [{`label`, `l`, `r`}] (máx. 4) |
| `ranking` | top con barras (goleo, puntos, etc.) | `title`, `sub`, `rows`: [{`name`, `team`, `val`, `hl`}] (máx. 5) |
| `question` | cierre para comentarios | `pre`, `q` (usa \n), `opts`: [2 opciones] |

## Reglas

- Sin escudos, logos, fotos ni video de transmisiones: solo las gráficas de la plantilla.
- Polémica sí, insultos o burlas a personas no. Nada de promover apuestas.
- Si no hay una noticia de Liga MX con datos verificables ese día, haz un video de contexto (tabla, goleo, carrera por la Liguilla) con datos confirmados, nunca inventados.
- No cambies `engine/` en la tarea diaria salvo que algo esté roto; si lo arreglas, explícalo en el mensaje final.
