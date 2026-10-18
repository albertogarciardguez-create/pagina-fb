# Fábrica de reels — Señor Fútbol

Este repositorio genera los reels animados de la página de Facebook **Señor Fútbol** (facebook.com/senorfutbol), de Alberto García (Ciudad Juárez). Formato: video vertical 1080×1920, 25–35 s, gráficas animadas estilo papel/tinta, voz en off en español, música y efectos, subtítulos. **Nadie sale a cuadro.** Todo el contenido es original (sin escudos, fotos ni clips de transmisiones), para que la página pueda monetizar.

## Flujo diario (lo que debe hacer la tarea programada)

Cada mañana se entregan **2 videos distintos**:

| Video | Contenido | Duración | Publicar |
|---|---|---|---|
| **A — La noticia** (`"kind": "noticia"`) | Lo más fuerte de Liga MX en las últimas 24 h: resultado, polémica, crisis o racha, fichaje, declaración. Prioridad a FC Juárez. | 25–35 s, 6–8 escenas | **1:00–2:00 pm** |
| **B — La Pizarra Señor Fútbol** (`"kind": "pizarra"`) | Táctica de **fútbol 7** para entrenadores y jugadores de ligas amateur, con ideas del juego de posición y la presión estilo **PSG de Luis Enrique** (presión alta, regla de 5 segundos, salida desde atrás, defensas por dentro, falso 9, tercer hombre, amplitud, bloque junto, balón parado, sistemas 2-3-1 / 3-2-1 / 3-1-2 / 2-1-2-1). Usa escenas `board`. Incluye un ejercicio para entrenarlo. | 45–65 s, 8–10 escenas | **8:00–9:30 pm** |

Reglas de la Pizarra: es contenido que no caduca, no necesita noticia ni fuentes (solo verifica cualquier dato real que menciones); termina con "Guarda este video para tu próximo entrenamiento" y una pregunta; la penúltima escena puede anunciar el **Libro de Jugadas de Fútbol 7**. Ejemplo completo: `stories/2026-10-16-pizarra-presion-psg.json`. Nunca uses escudos ni logos de clubes.

Todos los videos usan `"captionMode": "words"` (subtítulos de 1–2 palabras a la vez).

Los dos videos no deben repetir tema, equipo protagonista ni gancho. Revisa `stories/` para no repetir los temas de los últimos 7 días.

1. **Instalar** (una vez por sesión): `bash setup.sh`
2. **Elegir los temas.** Video A: primero corre `python3 engine/noticias.py` y lee `noticias/AAAA-MM-DD.md` (temas de las últimas 36 h ya agrupados y ordenados, con ⭐ si es de FC Juárez y ⚠️ si se parece a una historia reciente). Si termina con código 2 (sin internet desde la terminal, como en la nube), busca en la web lo más relevante de Liga MX de las últimas 24–48 h y el calendario de hoy. Ese archivo son pistas, no datos: el paso 3 sigue siendo obligatorio. Si hay algo de **FC Juárez**, dale prioridad. Video B: elige el siguiente concepto táctico de fútbol 7 que no se haya hecho en `stories/` (revisa los `kind: pizarra` anteriores).
3. **Verificar datos.** Cada número y cada hecho debe salir de una fuente confiable (Mediotiempo, ESPN, Récord, TUDN, Claro Sports, El Informador, sitio oficial de la Liga MX, etc.). Usa WebFetch para leer la nota, no solo el titular. **Nunca inventes ni estimes un dato.** Si no puedes confirmarlo, no lo uses. Anota las URL en `sources`.
4. **Escribir las dos historias** en `stories/AAAA-MM-DD-a-tema-corto.json` (noticia) y `stories/AAAA-MM-DD-b-pizarra-tema.json` (pizarra). Ejemplos: `stories/2026-10-15-juarez-ultimo.json` y `stories/2026-10-16-pizarra-presion-psg.json`.
   - Duración y número de escenas según la tabla de arriba.
   - Escena 1 = gancho fuerte (dato impactante en los primeros 3 s).
   - Última escena = tipo `question`, con una pregunta polémica y "¡Te leo en los comentarios!" en la voz.
   - `say`: lo que dice la voz. Español mexicano, frases cortas, exclamaciones y preguntas para darle energía. **Números con letra** ("ochenta y cuatro"), nunca dígitos.
   - `captions`: el mismo texto partido en trozos de 2–5 palabras, con dígitos ("84") y `<em>palabra</em>` para resaltar en verde las palabras clave.
   - Textos en pantalla en MAYÚSCULAS y cortos.
5. **Revisar** cada una: `python3 engine/build.py stories/<archivo>.json --preview` y abre `salida/<id>/revision.png` con Read. Revisa que no haya textos encimados o cortados, que todo se lea y que los datos sean correctos. Si hay cuadros que no se distinguen bien, abre los individuales en `salida/<id>/revision/`. Corrige y repite.
6. **Generar los videos**: `python3 engine/build.py stories/<archivo>.json` (~3–5 min cada uno). Quedan en `salida/<id>/<id>.mp4` y el texto para publicar en `salida/<id>/post.txt`, que ya incluye las ligas de `config/ligas.json` que correspondan al `kind` del video (libro, afiliados, publicidad).
7. **Entregar a Alberto**: manda los dos MP4 con SendUserFile. En tu mensaje final, para cada video (A y B) incluye, listo para copiar: la hora exacta sugerida para programarlo hoy, el texto del post con hashtags y las fuentes.
8. **Guardar**: haz commit solo de los JSON de las historias (`salida/` está ignorada) y push a `main`. Si el push falla, continúa.

## Voz en off

El motor de voz se elige en `config/voz.json` (`"motor"`), o para una prueba con `VOZ_MOTOR=<motor> python3 engine/build.py ...`:

| Motor | Qué es | Requisitos |
|---|---|---|
| `kokoro` | Voz offline gratuita (`em_alex`). Respaldo de todos los demás. | Ninguno (lo instala `setup.sh`) |
| `elevenlabs` | Voz más expresiva por API; puede ser la voz clonada de Alberto. Gasta créditos. | Llave en `~/.config/senorfutbol/elevenlabs.key` o `ELEVENLABS_API_KEY`; `voice_id` en `config/voz.json` |
| `chatterbox` | Voz clonada de Alberto a partir de una grabación, con control de emoción (`exageracion`). Gratis y local, licencia MIT; en la Mac usa el chip M. | `python3 -m pip install chatterbox-tts` y la grabación en `chatterbox.referencia` (10–20 s, WAV) |

- Cada computadora puede tener sus propios ajustes en `~/.config/senorfutbol/voz.json` (fuera de git; mismo formato, solo lo que cambia, p. ej. `{"motor": "chatterbox"}`). Tienen prioridad sobre `config/voz.json`.
- Si el motor elegido falla (sin llave, sin internet, sin paquete o sin grabación), el video sale completo con `kokoro` y `build.py` imprime `AVISO:`. Menciona ese aviso en el mensaje final.
- Cada línea se guarda en caché (`~/.cache/senorfutbol/voz/`): la hoja de revisión y el video final usan el mismo audio y ElevenLabs no cobra dos veces. Cambiar el texto de una escena solo regenera esa línea (y, con ElevenLabs, las vecinas, porque usa el contexto para la entonación).
- Nunca guardes la llave de ElevenLabs en el repositorio ni la pongas en un mensaje.
- En la nube no hay acceso a ElevenLabs ni a Hugging Face desde la terminal: ahí siempre sale con `kokoro`.

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
  "kind": "noticia",                    // noticia | pizarra (decide qué ligas lleva el post)
  "captionMode": "words",               // subtítulos de 1–2 palabras
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
| `board` | **pizarra táctica de fútbol 7** (cancha completa) | ver abajo |

### Escena `board` (pizarra)

Coordenadas en % de la cancha: `x` 0–100 de izquierda a derecha, `y` 0–100 de arriba (portería rival) a abajo (portería propia).

```json
{"type": "board", "title": "REGLA DE LOS 5 SEGUNDOS", "say": "...", "captions": ["..."],
 "team":  [{"id": "PO", "x": 50, "y": 94}, {"id": "DI", "label": "DF", "x": 32, "y": 78}, ...],   // 7 jugadores verdes (label opcional, máx. 3 letras)
 "rival": [{"id": "R1", "x": 50, "y": 6}, ...],                                                  // rojos
 "ball": "MC",                                   // id del que la tiene o [x, y]
 "inherit": false,                               // true = arranca con las posiciones finales de la escena board anterior (omite team/rival)
 "view": "top",                                  // opcional: acerca la media cancha de arriba (y 0–50 llena toda la pizarra); úsalo en balón parado y jugadas en el área
 "timer": {"from": 5, "label": "SEG", "at": 0.12, "end": 0.95},   // cuenta regresiva opcional
 "note": "EJERCICIO",                            // etiqueta opcional
 "steps": [                                      // momentos dentro de la línea de voz (at 0–1)
   {"at": 0.2, "pos": {"MD": [82, 36]}, "ball": "R6",
    "arrows": [{"from": "MD", "to": [82, 37], "kind": "press"}],   // kind: pass (punteada), run (verde), press (roja); from/to = id o [x,y]; "curve" opcional
    "zone": {"x": 56, "y": 26, "w": 42, "h": 26, "label": "PRESIÓN", "color": "red|green"}, "zoneHold": true, "hit": true}
 ]}
```

Una flecha de carrera o presión debe terminar donde el jugador queda en ese paso (`pos`). Revisa en la hoja de revisión que ningún jugador quede encimado con otro.

## Reglas

- Sin escudos, logos, fotos ni video de transmisiones: solo las gráficas de la plantilla.
- Polémica sí, insultos o burlas a personas no. Nada de promover apuestas.
- Si no hay una noticia de Liga MX con datos verificables ese día, haz un video de contexto (tabla, goleo, carrera por la Liguilla) con datos confirmados, nunca inventados.
- No cambies `engine/` en la tarea diaria salvo que algo esté roto; si lo arreglas, explícalo en el mensaje final.
