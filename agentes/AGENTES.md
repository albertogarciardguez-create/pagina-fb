# Agentes de redes — Señor Fútbol e Impulso Real

Tres agentes (tareas programadas de Claude) y un publicador (GitHub Actions) trabajan en cadena. Alberto solo autoriza el temario.

```
Sábado      PLANEADOR ──► temario de la semana en la hoja "Temario" (Autorizado vacío)
                              │  Alberto marca Sí / Sí con cambios / No
Diario      AGENTE IR (5:20 am) y AGENTE SF (8:45 am)
            leen las filas de HOY con "Sí…" ─► escriben la historia ─► revisan la hoja de revisión
            ─► commit de stories|diorama + cola/<id>.json ─► push a main
GitHub      PUBLICADOR (.github/workflows/publicar.yml)
            genera el MP4 ─► Facebook y YouTube programados ─► Instagram y TikTok a su hora
            ─► estado en cola/estado/<id>.json
```

**Hoja de autorización:** [Calendario de contenido · Agentes de redes](https://docs.google.com/spreadsheets/d/1ewGkUnSL1Pk5DqJpj5Ra-ZVddGcYqDM7EW1ksnU3qwg/edit) — ID `1ewGkUnSL1Pk5DqJpj5Ra-ZVddGcYqDM7EW1ksnU3qwg`, pestaña `Temario`.
Columnas: A Fecha (AAAA-MM-DD) · B Hora (HH:MM, Ciudad Juárez) · C Página (`Señor Fútbol` | `Impulso Real`) · D Formato · E Tema · F Gancho / ángulo · G Redes (`FB, IG, YT, TikTok`) · H Autorizado (`Sí` | `Sí con cambios` | `No` | vacío) · I Cambios que pides · J Estado · K Liga.

## Reglas para todos los agentes

- **Nada se produce sin autorización.** Solo filas con H = `Sí` o `Sí con cambios` (aplica lo que diga la columna I). Vacío o `No` = no se hace.
- Gasta pocos tokens: no leas archivos enteros que no necesitas, un solo preview por video salvo que haya errores, mensajes finales cortos.
- Español mexicano. Nunca inventes datos; todo dato real se verifica (ver CLAUDE.md). Sin escudos, logos, fotos ni clips de terceros. Nada de apuestas.
- Nunca pongas tokens ni llaves en el repositorio, en la hoja ni en mensajes. Los secretos viven solo en GitHub.
- Clona con `git clone --depth 30 https://github.com/albertogarciardguez-create/pagina-fb ~/pagina-fb` (tiempo de espera generoso) y corre `bash setup.sh` antes de generar.

## Indicadores (lo que deben mover los agentes)

Cada publicación se mide en FB, IG y YouTube (TikTok no da datos sin auditoría) y se resume en **`cola/metricas/RESUMEN.md`** (lo actualiza el publicador una vez al día):

**Puntaje = 10×seguidores nuevos + 4×compartidos + 3×comentarios + 2×guardados + reacciones + reproducciones/100**

Seguidores, compartidos y comentarios pesan más porque son lo que hace crecer y monetizar la página; las reproducciones solas no. Metas:
- Semanas 1–2: línea base (todas las franjas y formatos con al menos 5 publicaciones).
- Desde la semana 3: **+10 % de puntaje promedio por semana** por página y **seguidores netos al alza** (tabla de seguidores del RESUMEN).
- Regla 60/30/10 al planear: 60 % de las publicaciones con los 2 formatos de mejor puntaje, 30 % variaciones de esos (otro gancho, otro tema), 10 % experimentos nuevos.
- Un formato o una hora que quede en el último lugar dos semanas seguidas (con ≥5 publicaciones) se reemplaza o se mueve ±90 min hacia la mejor hora.
- Los agentes diarios copian la **estructura y el tipo de gancho** del Top 5 (no el tema).

## Horarios iniciales (Ciudad Juárez) — se ajustan con los datos

| Franja | Facebook / YouTube | Instagram | TikTok (bandeja) |
|---|---|---|---|
| SF · Noticia | 13:15 | 12:30 | 19:00 |
| SF · Pizarra / Debate | 20:30 | 20:30 | 20:30 |
| IR · Reflexión mañana | 07:30 | 07:30 | 07:30 |
| IR · Historia noche | 21:00 | 20:30 | 21:00 |

Se basan en los picos generales de mediodía (Instagram) y tarde-noche (Facebook y TikTok) y en la rutina del público (camino al trabajo, comida, noche). Cuando una red lleva otra hora que la de Facebook, va en `"horas"` del item de la cola.

## Estructuras de video (las que retienen y generan comentarios, guardados y seguidores)

Reglas para todos: **gancho en el segundo 0–2** (dato, pregunta o afirmación fuerte, texto grande, sin saludo ni logo), cambio visual cada 1.5–3 s, subtítulos palabra por palabra, un **re-gancho a la mitad** (“pero lo peor viene ahora…”), cierre con **pregunta de respuesta fácil (A o B)** y un final que conecte con el inicio para que se repita.

| Formato | Duración | Estructura | Indicador que busca |
|---|---|---|---|
| SF · Noticia | 25–35 s | 1 dato o polémica · 2 contexto (marcador/tabla) · 3–4 lo que nadie está diciendo · 5 qué sigue (Liguilla, próximo rival) · 6 pregunta A/B | Comentarios, compartidos |
| SF · Pizarra F7 | 45–60 s | 1 problema del amateur (“¿te pasa que…?”) · 2–4 solución en 3 pasos en la pizarra · 5 error común · 6 ejercicio · 7 “guárdalo y mándaselo a tu equipo” · 8 pregunta | Guardados, compartidos |
| SF · Debate/Top | 30–40 s | Top 5 en cuenta regresiva, el #1 polémico · “¿quién falta?” | Comentarios |
| IR · Reflexión | 30–45 s | 1 frase contraintuitiva · 2 metáfora visual en papel · 3 tres aplicaciones a la vida diaria · 4 giro · 5 “Envíaselo a quien lo necesite” + pregunta | Compartidos, seguidores |
| IR · Historia | 50–75 s | 1 empieza en el momento más tenso · 2 contexto · 3 conflicto · 4 giro · 5 la lección en una frase · 6 pregunta personal (“¿Tú qué habrías hecho?”) | Seguidores, retención |

En el texto del post: primera línea = el gancho (no el título), una pregunta para comentar y 3–5 hashtags.

## 1 · Planeador semanal (sábado)

1. Lee esta guía y **`cola/metricas/RESUMEN.md`** (si existe): formatos, horas y días con mejor y peor puntaje, Top 5 y tendencia de seguidores. Revisa `git log --oneline -40` y los nombres de `stories/` y `diorama/` de los últimos 14 días para no repetir temas.
2. Busca en la web el calendario de Liga MX (o Liguilla) y de FC Juárez para la semana siguiente (lunes a domingo).
3. Escribe en la hoja (añade filas debajo de las existentes, H vacío) **4 publicaciones por día** con las franjas de la tabla de horarios (o las que los datos indiquen) y aplicando la regla 60/30/10:

| Página | Franja | Formato (motor) | Contenido |
|---|---|---|---|
| Señor Fútbol | Noticia | Noticia (reel) | Lo más fuerte de Liga MX del día; prioridad Bravos. El tema exacto se decide esa mañana: en E pon el partido/tema probable y en F el ángulo. |
| Señor Fútbol | Noche | Pizarra F7 o Debate/Top (reel) | Pizarra: un concepto táctico de fútbol 7 que no se haya hecho, con ejercicio. Debate: ranking o cara a cara con pregunta polémica. Reparte según el puntaje de cada uno. |
| Impulso Real | Mañana | Reflexión (diorama, plantilla papel) | Estoicismo, liderazgo, fe, hábitos, finanzas personales. Público 30–44 años. |
| Impulso Real | Noche | Historia (diorama, papel o infografía) | Historia bíblica, de un estoico o una lección de vida/película, con giro final. |

   - En B pon la hora de Facebook; si IG o TikTok van a otra hora, escríbelo en F (“IG 12:30 · TikTok 19:00”).
   - En G pon `FB, IG, YT, TikTok` salvo que Alberto haya pedido otra cosa en la hoja.
   - En E y F escribe tema y gancho concretos (la frase de los primeros 2 s), no genéricos. Marca con “🧪” los experimentos del 10 %.
4. Mensaje final (corto): link de la hoja, 3 líneas de lo que dicen los indicadores (qué funcionó, qué se cambia y por qué), la tabla compacta de la semana y “Marca Sí / Sí con cambios / No en la columna Autorizado. Lo que no esté autorizado el día anterior no se produce.”

## 2 · Agente Impulso Real (diario, 5:20 am) y 3 · Agente Señor Fútbol (diario, 8:45 am)

1. Lee la hoja (`Temario!A:K`). Toma las filas de **hoy** de tu página con H autorizado y J vacío o “Pendiente”. Si no hay ninguna, actualiza J de las filas de hoy sin autorización con `No autorizado` y termina con un mensaje de una línea.
2. Antes de producir, revisa `cola/estado/` de ayer: escribe en J de esas filas `Publicado: FB ✅ IG ✅ YT ✅ TikTok ✅` (o el error en pocas palabras).
3. Para cada fila autorizada:
   - **Señor Fútbol (motor `reel`)**: sigue el “Flujo diario” de CLAUDE.md (verificación con fuentes, historia en `stories/AAAA-MM-DD-a-…json` o `-b-…json`, `--preview` y revisar `revision.png` con Read). Voz: la de `config/voz.json`.
   - **Impulso Real (motor `diorama`)**: historia en `diorama/AAAA-MM-DD-<tema>-reel.json` con `"plantilla": "papel"` (o `"infografia"`), `"tts": "edge"`, `"edge_voz": "es-MX-DaliaNeural"`, sin campo `audio`. Reutiliza escenas `vis` existentes siempre que se pueda; si hace falta una nueva, agrégala en la plantilla y revisa que se vea bien. Gancho en el segundo 0–2, cierre `"tipo": "cierre"` con pregunta. Preview con `python3 engine/build_diorama.py <json> --preview` y revisa la hoja con Read.
   - Antes de escribir, lee el Top 5 de tu página en `cola/metricas/RESUMEN.md` y usa la **estructura** de la tabla de estructuras de video; copia el tipo de gancho que mejor funciona.
   - No hace falta generar el MP4 final aquí: lo genera el publicador en GitHub.
   - **Textos para redes**: en cada historia agrega `"redes_textos"` con un texto por red (primera línea = gancho, pregunta para comentar, 3–5 hashtags):
     `{"facebook": "post completo con contexto", "instagram": "más corto, con llamado a guardar/compartir", "youtube": {"titulo": "≤ 90 caracteres + #Shorts", "descripcion": "2–3 líneas + hashtags"}, "tiktok": "≤ 150 caracteres + 3–4 hashtags"}`.
     El publicador usa el de cada red; el de TikTok queda en el estado para pegarlo al publicar el borrador.
   - Horas: la de Facebook/YouTube es la columna B; si F dice “IG hh:mm · TikTok hh:mm”, van en `"horas"`; si no, usa la tabla de horarios.
   - Crea `cola/<id>.json`:
     ```json
     {"id": "2026-11-20-ir-manana-la-piedra", "pagina": "impulsoreal", "motor": "diorama",
      "historia": "diorama/2026-11-20-la-piedra-reel.json", "hora": "2026-11-20 07:30",
      "redes": ["facebook", "instagram", "youtube", "tiktok"], "horas": {"instagram": "2026-11-20 07:30", "tiktok": "2026-11-20 07:30"},
      "formato": "IR · Reflexión", "tema": "La piedra", "titulo": "Título corto para YouTube #Shorts"}
     ```
     `pagina`: `senorfutbol` | `impulsoreal`. `motor`: `reel` (stories/) | `diorama` | `anime` | `largo`. `redes` según la columna G. `formato` = el nombre de la tabla de estructuras (así se agrupan los indicadores). `horas` solo si IG/TikTok van a otra hora. El texto del post sale de `post` + `hashtags` de la historia (más ligas en los reels de SF); pon `"texto"` solo si quieres otro.
   - Si la hora ya está a menos de 25 min, pásala a la siguiente media hora libre y anótalo en J.
4. `git add` de las historias y de `cola/*.json`, commit `Agente <página> AAAA-MM-DD` y push a `main` (reintenta con `git pull --rebase` si falla). El push dispara el publicador.
5. En la hoja, J = `En cola · <hora>` y K = `https://github.com/albertogarciardguez-create/pagina-fb/releases/download/cola/<id>.mp4` (el video aparece ahí ~10 min después).
6. Mensaje final (corto, listo para leer en el celular): por cada publicación, hora, tema, redes, link del video y sus textos por red listos para copiar (sobre todo el de TikTok); y una línea con el resultado de ayer. Nada de explicar el proceso.

## 4 · Agente de anuncios (Meta Ads) — APAGADO hasta que Alberto genere ingresos

Configuración en `config/anuncios.json` (`"activo": false`, tope $1,500 MXN/mes, objetivo **seguidores de la página**, modo **pausa**). Mientras esté apagado **no se crea ni se gasta nada**: el publicador solo lista cada día las 2 mejores publicaciones por página en la sección “Candidatas a promoción” de `cola/metricas/RESUMEN.md`, y el planeador las menciona en su mensaje (“si hubiera presupuesto, impulsaría…”).

Cuando Alberto pida activarlo (`"activo": true`):
1. Cada lunes el planeador agrega en la hoja, pestaña `Anuncios`, las candidatas (2 por semana) con presupuesto diario = tope mensual × reparto de la página ÷ 30 y duración `dias_por_anuncio`.
2. Solo con Autorizado = Sí se crea la campaña en el Administrador de anuncios **en pausa** (objetivo Interacción → me gusta/seguidores de la página, usando la publicación existente, público de `publico`), y Alberto la activa.
3. Nunca se pasa del tope mensual ni se promociona algo que no haya funcionado orgánicamente (puntaje del Top 5).



- Se dispara con cada push que agrega `cola/*.json` y cada 20 min.
- Genera el video una sola vez (lo guarda en el release `cola`), programa **Facebook** (Reels API) y **YouTube** (`publishAt`) en cuanto llega, y sube **Instagram** (Reels, subida reanudable) y **TikTok** (bandeja de borradores) a su hora.
- Si faltan los secretos de una red, la marca como omitida y sigue con las demás. Cada red se reintenta hasta 3 veces. Lo que no salió 36 h después de su hora se marca `caducado`.
- Prueba sin publicar: `python3 engine/publicador.py --simular`. Ver qué toca: `python3 engine/publicador.py --revisar`.
- Configuración de cuentas y secretos: `agentes/CONFIGURAR.md`.
