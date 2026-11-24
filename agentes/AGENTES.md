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

- **Nada se produce sin autorización.** Cuenta como autorizada la fila cuya columna H diga `Sí`, `Sí con cambios` o `Autorizado` (sin importar mayúsculas). Si la columna I (Cambios que pides) trae algo, aplícalo siempre. Vacío o `No` = no se hace.
- Gasta pocos tokens: no leas archivos enteros que no necesitas, un solo preview por video salvo que haya errores, mensajes finales cortos.
- Español mexicano. Nunca inventes datos; todo dato real se verifica (ver CLAUDE.md). Sin escudos, logos, fotos ni clips de terceros. Nada de apuestas.
- Nunca pongas tokens ni llaves en el repositorio, en la hoja ni en mensajes. Los secretos viven solo en GitHub.
- Clona con `git clone --depth 30 https://github.com/albertogarciardguez-create/pagina-fb ~/pagina-fb` (tiempo de espera generoso) y corre `bash setup.sh` antes de generar.

## Objetivo número 1: MONETIZAR (vistas + seguidores/suscriptores)

Todo lo que planean y producen los agentes debe acercar a las páginas a los requisitos de pago de `config/metas.json`. El avance real está en la sección **“Camino a monetizar”** de `cola/metricas/RESUMEN.md`:

| Plataforma | Requisito para cobrar | Qué hacen los agentes |
|---|---|---|
| **YouTube Shorts** | Nivel 1: 500 suscriptores + 3 M vistas de Shorts en 90 días (+3 subidas). Nivel 2 (anuncios): 1,000 suscriptores + 10 M vistas en 90 días; **desde el 1 feb 2027 serán 20 M para canales nuevos**, así que hay que entrar antes. | Todo reel se sube también como Short. Cierre con “Suscríbete para la parte 2”. Prioridad a formatos con más vistas. |
| **TikTok** (Creator Rewards, México) | 10,000 seguidores + 100,000 vistas en 30 días; **solo pagan videos de 1 minuto o más**. | Pizarras, historias y top: **61–75 s**. La noticia puede seguir corta (25–35 s), porque su objetivo es atraer seguidores. |
| **Facebook** (Monetización de contenido) | Por invitación; paga por el rendimiento de contenido **original**. Hitos internos: 2,500 → 5,000 → 10,000 seguidores. | 100 % contenido original (ya lo es). Alberto registra su interés en Panel profesional → Monetización. |
| **Instagram** | Sin programa de pago directo; sirve para seguidores y marcas. Hitos: 1,000 → 5,000 → 10,000. | Los mismos reels a su hora. |

Palancas que deben usar siempre:
- **Series con continuación** (“Parte 1 de 3”, “mañana te cuento cómo terminó”): la razón número 1 para seguir una cuenta es querer ver lo que sigue.
- **Llamado a seguir en el último segundo**, con un motivo concreto (“Sígueme: cada noche una historia que te cambia el día”), no un “sígueme” genérico.
- Gancho en el segundo 0–2 y **retención** (re-gancho a la mitad, final en bucle). Las vistas que cuentan para cobrar son las que pasan de los primeros segundos.
- Mismo video en las 4 redes el mismo día. Constancia: 6 reels diarios (3 de Señor Fútbol + 3 de Impulso Real) + 1 post de foto por página en Facebook (la tarea “Genera impulso” de Facebook pide publicaciones además de reels), sin días vacíos.
- Temas con alto volumen de búsqueda (Liga MX en jornada y Liguilla; historias bíblicas y estoicas conocidas) y títulos que se buscan (“¿Por qué…?”, “La historia de…”).

## Indicadores (lo que deben mover los agentes)

Cada publicación se mide en FB, IG y YouTube (TikTok no da datos sin auditoría) y se resume en **`cola/metricas/RESUMEN.md`** (lo actualiza el publicador una vez al día):

**Puntaje = 10×seguidores nuevos + reproducciones/25 + 2×compartidos + 2×comentarios + guardados + 0.5×reacciones**

Seguidores y reproducciones pesan más porque son los requisitos para monetizar. Metas:
- Semanas 1–2: línea base (todas las franjas y formatos con al menos 5 publicaciones).
- Desde la semana 3: **+10 % de puntaje promedio por semana** por página y **seguidores netos al alza en cada red**.
- Regla 60/30/10 al planear: 60 % de las publicaciones con los 2 formatos de mejor puntaje, 30 % variaciones de esos (otro gancho, otro tema), 10 % experimentos nuevos.
- Un formato o una hora que quede en el último lugar dos semanas seguidas (con ≥5 publicaciones) se reemplaza o se mueve ±90 min hacia la mejor hora.
- Los agentes diarios copian la **estructura y el tipo de gancho** del Top 5 (no el tema).

## Horarios iniciales (Ciudad Juárez) — se ajustan con los datos

| Franja | Facebook / YouTube | Instagram | TikTok (bandeja) |
|---|---|---|---|
| IR · Reflexión mañana | 09:00 | 09:00 | 09:00 |
| SF · Post foto (solo FB) | 10:30 | – | – |
| SF · Posiciones 3D | 11:30 | 11:30 | 11:30 |
| IR · Lección / Tecnología mediodía | 12:00 | 12:00 | 12:00 |
| SF · Noticia | 13:15 | 12:30 | 14:00 |
| IR · Post foto (solo FB) | 15:00 | – | – |
| SF · Explica / Jugada 3D | 17:00 | 17:00 | 17:00 |
| SF · Pizarra / Debate | 19:00 | 19:00 | 19:00 |
| IR · Historia noche | 20:00 | 19:30 | 20:00 |

**Zona horaria:** las horas son de Ciudad Juárez, pero el público está casi todo en hora del centro (CDMX, UTC−6). En invierno Juárez va **1 h atrás** de CDMX (09:00 Juárez = 10:00 CDMX). Desde el 14 mar 2027 Juárez cambia al horario de verano y queda igual que CDMX: ese día el planeador suma 1 h a todas las franjas para seguir cayendo en la misma hora del público.
Los estudios de 2026 (Sprout Social: ~2,000 millones de interacciones, hora local del público) marcan para Facebook la ventana **12–20 h** (mejor martes y miércoles; lunes 12–13 h; jueves 12–14 h y 20 h; fines de semana lo más flojo); Metricool marca 10–12 h. Por eso nada sale antes de las 10:00 ni después de las 21:00 hora CDMX. Cuando haya ≥5 publicaciones por franja con métricas reales, mandan los datos propios.
Se basan en los picos generales de mediodía (Instagram) y tarde-noche (Facebook y TikTok) y en la rutina del público (camino al trabajo, comida, noche). Cuando una red lleva otra hora que la de Facebook, va en `"horas"` del item de la cola.

## Estructuras de video (las que retienen y generan comentarios, guardados y seguidores)

Reglas para todos: **gancho en el segundo 0–2** (dato, pregunta o afirmación fuerte, texto grande, sin saludo ni logo), cambio visual cada 1.5–3 s, subtítulos palabra por palabra, un **re-gancho a la mitad** (“pero lo peor viene ahora…”), cierre con **pregunta de respuesta fácil (A o B)** y un final que conecte con el inicio para que se repita.

| Formato | Duración | Estructura | Indicador que busca |
|---|---|---|---|
| SF · Noticia | 25–35 s | 1 dato o polémica · 2 contexto (marcador/tabla) · 3–4 lo que nadie está diciendo · 5 qué sigue (Liguilla, próximo rival) · 6 pregunta A/B | Comentarios, compartidos |
| SF · Pizarra F7 | 61–70 s | 1 problema del amateur (“¿te pasa que…?”) · 2–4 solución en 3 pasos en la pizarra · 5 error común · 6 ejercicio · 7 “guárdalo y mándaselo a tu equipo” · 8 pregunta | Guardados, compartidos |
| SF · Explica 3D | 61–70 s | 1 pregunta-gancho con dato (“¿Por qué…?”, “Ninguna cancha mide igual”) · 2–4 el concepto se arma paso a paso en el mundo 3D (aparecen gradas, cotas, contadores) · 5 re-gancho (“pero lo que nunca cambia…”) · 6 cierre con pregunta A/B + “sígueme, cada semana te explico el fútbol como nadie” | Compartidos, seguidores |
| SF · Posiciones 3D | 45–60 s | 1 gancho del error típico de esa posición en el amateur (“tu lateral solo corre… y nadie sabe para qué”) · 2 la zona de la posición se ilumina en la cancha 3D (F7) · 3–4 sus 3 tareas con flechas (con balón, sin balón, al perderla) · 5 el error común EN PAUSA · 6 “compártelo con tu [posición]” + pregunta A/B | Seguidores, compartidos |
| SF · Jugada 3D | 61–70 s | 1 el error en la cancha 3D (“tu nueve pica… y se lo comen”) · 2 EN PAUSA: se marca al rival clave · 3–4 la solución con flechas y zona · 5 la repetición con otra cámara · 6 “compártelo con tu equipo” + pregunta | Guardados, compartidos |
| SF · Debate/Top | 61–70 s | Top 5 en cuenta regresiva, el #1 polémico · “¿quién falta?” | Comentarios |
| IR · Reflexión | 35–45 s | 1 frase contraintuitiva · 2 metáfora visual en papel · 3 tres aplicaciones a la vida diaria · 4 giro · 5 “Envíaselo a quien lo necesite” + pregunta | Compartidos, seguidores |
| IR · Lección | 50–65 s | 1 dato o frase de un autor/emprendedor (“Brian Tracy decía…”) · 2 el método en 3 pasos con objetos (hoja, frasco, calendario) · 3 dato que lo respalda · 4 re-gancho · 5 “Envíaselo a ese amigo que…” + pregunta. Serie “Parte N” por autor. | Guardados, seguidores |
| IR · Tecnología | 45–60 s | 1 la noticia en una frase de impacto · 2 qué pasó exactamente (datos verificados) · 3 por qué importa · 4 cómo te afecta a ti / qué hacer · 5 pregunta A/B (“¿te da miedo o te emociona?”) | Comentarios, compartidos |
| IR · Historia | 61–75 s | 1 empieza en el momento más tenso · 2 contexto · 3 conflicto · 4 giro · 5 la lección en una frase · 6 pregunta personal (“¿Tú qué habrías hecho?”) | Seguidores, retención |

En el texto del post: primera línea = el gancho (no el título), una pregunta para comentar y 3–5 hashtags.

## 1 · Planeador semanal (sábado)

1. Lee esta guía y **`cola/metricas/RESUMEN.md`** (si existe): “Camino a monetizar”, formatos, horas y días con mejor y peor puntaje, Top 5 y tendencia de seguidores. Planea para cerrar la brecha más grande de ese avance (p. ej., si YouTube va lento en suscriptores, más series con “parte 2”). Revisa `git log --oneline -40` y los nombres de `stories/` y `diorama/` de los últimos 14 días para no repetir temas.
2. Busca en la web el calendario de Liga MX (o Liguilla) y de FC Juárez para la semana siguiente (lunes a domingo).
3. Escribe en la hoja (añade filas debajo de las existentes, H vacío) **9 publicaciones por día** (Señor Fútbol: 4 reels + 1 post de foto; Impulso Real: 3 reels + 1 post de foto) con las franjas de la tabla de horarios (o las que los datos indiquen) y aplicando la regla 60/30/10:

| Página | Franja | Formato (motor) | Contenido |
|---|---|---|---|
| Señor Fútbol | Noticia | Noticia (reel) | Lo más fuerte de Liga MX del día; prioridad Bravos. El tema exacto se decide esa mañana: en E pon el partido/tema probable y en F el ángulo. |
| Señor Fútbol | Tarde 17:00 | Explica 3D o Jugada 3D (diorama, plantilla iso) — se alternan día por día | Explica: un “¿por qué…?” del fútbol (reglas, medidas, estadios, balón, VAR) con datos verificados en la fuente oficial (IFAB/FIFA). Jugada: una idea táctica de F7 en la cancha 3D, distinta a la pizarra de esa semana. Estilo de los videos que pasó Alberto (mundo isométrico con gente, cancha 3D con jugadores marcados). |
| Señor Fútbol | Mañana 11:30 (diario) | Posiciones 3D (diorama, plantilla iso, `vis: jugada`, cancha f7) | Serie de aprendizaje pedida por Alberto: qué hace cada posición en fútbol 7 (portero, defensa central, lateral, contención/5, interior, 10, extremo, 9, falso 9, portero-líbero…), con sus tareas con y sin balón y el error común. Una posición por día, sin repetir hasta completar la serie; marca “Parte N”. Historia en `diorama/AAAA-MM-DD-sf-posicion-<tema>.json`; en la cola `"formato": "SF · Posiciones 3D"`. |
| Señor Fútbol | Noche | Pizarra F7 o Debate/Top (reel) | Pizarra: un concepto táctico de fútbol 7 que no se haya hecho, con ejercicio. Debate: ranking o cara a cara con pregunta polémica. Reparte según el puntaje de cada uno. |
| Impulso Real | Mañana | Reflexión (diorama, plantilla papel) | Estoicismo, liderazgo, fe, hábitos, finanzas personales. Público 30–44 años. |
| Impulso Real | Mediodía (12:00) | Lección o Tecnología (diorama, plantilla papel; fondos `noche`/`interior` para el look oscuro) | Alterna: **Lección** de un autor o emprendedor (Brian Tracy, Jim Rohn, Darren Hardy, etc.: metas, hábitos, dinero, productividad), en serie “Parte N”; y **Tecnología**: la noticia más importante de IA, SpaceX, Tesla, robots o tecnología de las últimas 24–48 h, contada con el ángulo de qué significa para tu vida o tu trabajo. En Tecnología, E = “Noticia de tecnología del día” y el tema exacto se decide esa mañana con fuentes (Reuters, AP, The Verge, sitio oficial…), nunca inventado. |
| Impulso Real y Señor Fútbol | Post foto (10:30 SF · 15:00 IR) | Post foto (motor `post`, solo FB) | Imagen 4:5 con una frase o dato + pregunta fácil de contestar. IR: frase de un autor/estoico o reto del día. SF: dato verificado del día, encuesta (“¿A o B?”) o “completa la frase”. En G pon `FB`. |
| Impulso Real | Noche | Historia (diorama, papel o infografía) | Historia bíblica, de un estoico o una lección de vida/película, con giro final. |

   - En B pon la hora de Facebook; si IG o TikTok van a otra hora, escríbelo en F (“IG 12:30 · TikTok 14:00”).
   - En G pon `FB, IG, YT, TikTok` salvo que Alberto haya pedido otra cosa en la hoja.
   - En E y F escribe tema y gancho concretos (la frase de los primeros 2 s), no genéricos. Marca con “🧪” los experimentos del 10 %.
4. Mensaje final (corto): link de la hoja, el avance hacia monetizar (seguidores y vistas por red contra la meta), 3 líneas de lo que dicen los indicadores (qué funcionó, qué se cambia y por qué), la tabla compacta de la semana y “Marca Sí / Sí con cambios / No en la columna Autorizado. Lo que no esté autorizado el día anterior no se produce.”

## 2 · Agente Impulso Real (diario, 5:20 am) y 3 · Agente Señor Fútbol (diario, 8:45 am)

1. Lee la hoja (`Temario!A:K`). Toma las filas de **hoy** de tu página con H autorizado y J vacío o “Pendiente”. Si no hay ninguna, actualiza J de las filas de hoy sin autorización con `No autorizado` y termina con un mensaje de una línea.
2. Antes de producir, revisa `cola/estado/` de ayer: escribe en J de esas filas `Publicado: FB ✅ IG ✅ YT ✅ TikTok ✅` (o el error en pocas palabras).
3. Para cada fila autorizada:
   - **Señor Fútbol (motor `reel`)**: sigue el “Flujo diario” de CLAUDE.md (verificación con fuentes, historia en `stories/AAAA-MM-DD-a-…json` o `-b-…json`, `--preview` y revisar `revision.png` con Read). Voz: pon en la historia `"tts": "edge", "edge_voz": "es-MX-JorgeNeural"` (voz gratis más fluida que kokoro; Alberto la pidió así). En la nube el preview puede salir con kokoro; el video final en GitHub sale con Jorge. Escribe `say` con puntuación natural (comas, puntos suspensivos) para que fluya, sin exclamaciones en cada frase.
   - **Señor Fútbol · Posiciones 3D (motor `diorama`, 11:30)**: igual que la Jugada 3D (`"vis": "jugada"`, cancha f7, base `diorama/2026-11-24-sf-jugada-tercer-hombre.json`), pero centrada en UNA posición: marca al jugador con `label` ("TÚ") y `marca`, ilumina su zona con `zone`, y muestra sus tareas con y sin balón con flechas; una escena “EN PAUSA” con el error común. Archivo `diorama/AAAA-MM-DD-sf-posicion-<tema>.json`; cola con `"formato": "SF · Posiciones 3D"`.
   - **Señor Fútbol · Explica 3D / Jugada 3D (motor `diorama`)**: historia en `diorama/AAAA-MM-DD-sf-explica-<tema>.json` o `-sf-jugada-<tema>.json` con `"plantilla": "iso"`, `"marca": "senorfutbol"`, `"tts": "edge"`, `"edge_voz": "es-MX-JorgeNeural"` (esquema en CLAUDE.md, “Plantilla iso”). Ejemplos: `diorama/2026-11-23-sf-explica-medidas-cancha.json` y `diorama/ejemplo-sf-jugada-3d.json`. Preview con `build_diorama.py --preview` y revisa que las figuras se vean grandes y nada quede en la zona roja. En la cola: `"motor": "diorama"`, `"pagina": "senorfutbol"`, `"formato": "SF · Explica 3D"` o `"SF · Jugada 3D"`.
   - Si ya existe una historia de esa fecha y tema en `stories/` o `diorama/` (p. ej. una prueba previa), reúsala y ajústala en vez de escribirla de cero.
   - **Post foto (motor `post`, solo Facebook)**: escribe `posts/AAAA-MM-DD-<ir|sf>-post-<tema>.json` (esquema en `engine/build_post.py`: `kicker`, `texto` con `<em>` para la palabra clave, `autor` o `dato`, `pregunta` sin emojis, `post`, `hashtags`, `sources` si hay datos), corre `python3 engine/build_post.py <json>` y revisa `salida/<id>/<id>.jpg` con Read. Cola: `{"id": "...", "pagina": "...", "motor": "post", "historia": "posts/....json", "hora": "...", "redes": ["facebook"], "formato": "IR · Post foto" | "SF · Post foto", "tema": "..."}`. El texto del post: primera línea = gancho, una pregunta y 2–4 hashtags; no metas ligas (Facebook les baja el alcance).
   - **IR · Tecnología**: verifica cada dato en la nota completa (WebFetch) y anota las URL en `sources`; si no hay una noticia confirmable de las últimas 48 h, haz una Lección.
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
4. `git add` de las historias, `posts/` y `cola/*.json`, commit `Agente <página> AAAA-MM-DD` y push a `main` (reintenta con `git pull --rebase` si falla). El push dispara el publicador.
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
