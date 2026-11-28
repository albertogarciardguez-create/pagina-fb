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

## Objetivo número 1: MONETIZAR — plan de choque (desde el 27 nov 2026)

**Diagnóstico (datos del 28 oct al 26 nov 2026):**
- **Solo Facebook recibe los videos.** Instagram, YouTube y TikTok salen “omitidos (faltan secretos)” en todas las filas: el 75 % del trabajo de los agentes no llega a nadie. Hasta que Alberto cargue los secretos (`agentes/CONFIGURAR.md`), TikTok y YouTube los sube él a mano con los textos del mensaje final.
- **Facebook casi no reparte los reels** (1–7 reproducciones por reel según la API, 0 seguidores nuevos) y **Señor Fútbol pierde seguidores** cada día (1,633 → 1,619 en una semana). Publicar 9 piezas al día con la misma plantilla no crece la página: la entrena a mostrar poco.
- **TikTok de Impulso Real es lo único que crece** (58,896 vistas y 195 seguidores en 30 días), pero casi la mitad vino de un solo video (“la historia detrás de Arrópame”). Mediana: 249 vistas, **8.8 s vistos de promedio, retención 12 %**: el problema es el gancho y los primeros 5 segundos, no la cantidad.
- **Lo que funcionó:** la historia escondida detrás de una canción, un símbolo o una tradición conocida (Arrópame, “canciones que hablan de rescate”, la Catrina), parábolas cortas y memento mori. **Lo que no:** películas “explicadas en papel” de 2 min, lecciones de autores (Brian Tracy, Jim Rohn), finanzas, tecnología, estoicismo en clase, textos en MAYÚSCULAS y hashtags de relleno.
- En los nichos (vidIQ, nov 2026) lo que explota en cuentas chicas en español es: “la historia detrás de [canción]” (0.5–1.3 M vistas), historias de fe con un dolor con el que te identificas, series numeradas; en Liga MX: “¿qué necesita X para pasar?”, polémicas, humor de rivalidad y trivia.

**Decisiones (mandan sobre cualquier otra parte de esta guía):**
1. **Menos y mejor: 6 piezas al día** (por página: 2 reels + 1 post de foto). Desde el 28 nov, además, **2 noticias del día en foto en Impulso Real** (pedido de Alberto; ver “IR · Noticia del día”). Lo que se ahorra va a mejor guion, mejor gancho y voz de Edgardo en los videos estrella.
2. **Cambian los pilares** (tabla de formatos abajo). Se dejan de producir: IR Tecnología, IR Lección de autores, IR Finanzas, IR Reflexión de la mañana, SF Posiciones 3D, SF Explica 3D y SF Jugada 3D diarios. La Pizarra F7 queda **una vez por semana (viernes)**.
3. **Duración:** reels de crecimiento **30–45 s**; el video estrella de la noche **61–75 s** (cuenta para TikTok Creator Rewards y para minutos vistos en Facebook).
4. **Cada video pasa la lista de retención** (abajo) antes de hacer commit. Si no la pasa, se reescribe el inicio.
5. **Dinero que ya se puede cobrar:** Señor Fútbol tiene más de 500 seguidores hace más de 30 días → **Estrellas de Facebook** (Meta Business Suite → Monetización). Una vez por semana, solo en la historia estrella de SF, el cierre puede decir “si te gustó, mándame una estrella ⭐”. Nada de pedir dinero en cada video.

| Plataforma | Requisito para cobrar | Plazo realista con este plan |
|---|---|---|
| **Facebook SF** | Estrellas: 500 seguidores 30 días (ya cumple). Monetización de contenido: por invitación, paga por contenido original. | Estrellas: ya. Invitación: llega con reels que retengan; meta interna 2,500 seguidores. |
| **TikTok IR** | Creator Rewards (México): 10,000 seguidores + 100,000 vistas en 30 días; solo videos de 1 min o más. | Las vistas ya casi están (59 k/30 d); los seguidores son el cuello de botella → series y cierre con motivo para seguir. |
| **YouTube Shorts** | Nivel 1: 500 subs + 3 M vistas/90 d. YPP: 1,000 subs + 10 M vistas/90 d (**20 M desde el 1 feb 2027**). | Imposible antes de feb 2027 sin subir Shorts todos los días: primero los secretos de YouTube. |
| **Instagram** | Sin pago directo; sirve para seguidores y marcas. | Mismos reels cuando estén los secretos. |

### Pilares y formatos (los únicos que se planean)

| Página | Formato | Duración | Qué es | Gancho tipo (0–2 s) |
|---|---|---|---|---|
| IR | **IR · Historia detrás** (12:00) | 35–50 s | El origen escondido de una canción, símbolo, tradición o fecha que todos conocen (canciones de cuna, himnos, villancicos, Día de Muertos, Nochebuena, Guadalupe, Posadas, Año Nuevo). Se **narra** la historia: nunca se usa la grabación ni se citan letras con derechos (solo se nombra la canción; letras de antes de 1929 sí se pueden citar). | “Esta canción la cantaste mil veces… y nunca supiste por qué se escribió.” |
| IR | **IR · Fe que consuela** (12:00, alterna) | 40–55 s | Historia bíblica contada desde un dolor con el que te identificas (soledad, deudas, traición, espera, culpa). Personaje en papel, sin sermón. | “Si hoy sientes que nadie te ve… esta mujer pensó lo mismo.” |
| IR | **IR · Historia estrella** (20:00, Edgardo) | 61–75 s | Historia real, bíblica o parábola con giro final; en serie cuando se pueda (“Parte 1 de 2”). | Empieza en el momento más tenso (“Le quedaban seis horas de oxígeno…”). |
| SF | **SF · Liguilla** (13:15) | 30–40 s | Resultado de anoche + qué necesita cada uno para pasar / quién llega mejor. Datos verificados del día. | “Con este resultado, a X ya solo le sirve una cosa…” |
| SF | **SF · Polémica** (19:00 o 13:15) | 30–45 s | La jugada, decisión o declaración más discutida del día; dos posturas y voto A/B. Sin insultos. | “¿Era penal? Medio México dice que sí… y el reglamento dice otra cosa.” |
| SF | **SF · El día que…** (19:00, Edgardo L-M-V) | 61–75 s | Una historia épica real de Liga MX o del fútbol mexicano contada como película (verificada; sin escudos ni fotos). | “Minuto noventa y tres. El portero sube… y nadie lo marca.” |
| SF | **SF · Trivia** (19:00, alterna) | 30–40 s | 5 preguntas con cuenta regresiva (“¿cuántas aciertas?”); la respuesta en los comentarios de la última. | “Solo el 1 % de los aficionados contesta las cinco.” |
| SF | **SF · Pizarra F7** (viernes 19:00) | 61–70 s | Una idea táctica de fútbol 7 con ejercicio, para el fin de semana de liga. | “¿Tu equipo no pasa de media cancha? Le falta un solo pase.” |
| IR | **IR · Noticia del día** (10:00 y 17:30, solo FB, post foto) | – | Lo más importante de las últimas 24 h en tecnología, innovación, deportes (no Liga MX: eso es de SF), México y el mundo, estilo “última hora”. Tarjeta de texto con la marca de IR: sin fotos de personas, logos, banderas ni capturas de tuits. Pedido por Alberto el 27 nov para atraer público. | Primera línea = el hecho en una frase (“Un tribunal de Ámsterdam podría frenar la venta de…”). |
| Ambas | **Post foto** (SF 10:30 · IR 15:00, solo FB) | – | Encuesta A/B, “completa la frase”, dato del día o frase. | Pregunta de respuesta en una palabra. |

Fechas que se aprovechan (el planeador las pone sí o sí): Liguilla (semifinales y final de diciembre), **12 dic Virgen de Guadalupe**, **16–24 dic Posadas**, **24–25 dic Navidad**, **31 dic Año Nuevo (uvas, maletas)**, Reyes 6 ene.

### Lista de retención (cada video, antes del commit)

1. **Segundo 0:** la primera imagen ya tiene movimiento y el gancho escrito (máx. 7 palabras, en oraciones normales, no TODO EN MAYÚSCULAS). Sin logo, sin saludo, sin “hoy te voy a contar”.
2. **Segundos 0–3:** queda claro de qué trata y por qué quedarse (una promesa: “al final vas a entender por qué…”).
3. Cambio visual cada 1.5–2.5 s; frases de voz de máx. 12 palabras.
4. **Re-gancho a la mitad** (“pero lo que nadie sabe es…”).
5. **Final en bucle:** la última frase conecta con la primera para que se repita.
6. **Un solo llamado** al final y con motivo: seguir (“sígueme: cada noche una historia que no te contaron”) o comentar A/B. No apiles “guarda, comparte, comenta y sígueme”.
7. Duración según la tabla; si pasa, se recorta contexto, nunca el gancho.

### Texto del post (todas las redes)
- Primera línea = el gancho (no el título). Una pregunta fácil de contestar. **3 hashtags**: 1 amplio (#LigaMX, #Fe, #Historias) + 2 del tema. Sin ligas en reels (bajan el alcance) y sin emojis de relleno.
- TikTok: ≤150 caracteres; YouTube: título que se busca (“La historia detrás de…”, “¿Qué necesita X para…?”) + #Shorts.

## Indicadores (lo que deben mover los agentes)

Cada publicación se mide en FB, IG y YouTube (TikTok no da datos sin auditoría) y se resume en **`cola/metricas/RESUMEN.md`** (lo actualiza el publicador una vez al día). Desde el 27 nov las reproducciones de Facebook toman la métrica de **vistas** del panel (`post_media_view`) cuando es mayor que las de reels.

**Puntaje = 10×seguidores nuevos + reproducciones/25 + 2×compartidos + 2×comentarios + guardados + 0.5×reacciones**

- La métrica que manda cada semana: **vistas medianas por formato** y **seguidores netos por página**.
- Regla 70/20/10 al planear: 70 % de los formatos con mejor mediana, 20 % variaciones (otro tema, otro gancho), 10 % experimentos (🧪).
- Un formato con mediana por debajo de la de su página **dos semanas seguidas** (≥4 publicaciones) se deja de planear. Un video que pase de 3× la mediana se convierte en **serie** (parte 2, mismo tipo de tema) en la semana siguiente.
- Los agentes diarios copian la **estructura y el tipo de gancho** del Top 5 (no el tema).

## Horarios (Ciudad Juárez) — 6 piezas al día + 2 noticias de IR

| Franja | Facebook / YouTube | Instagram | TikTok |
|---|---|---|---|
| IR · Noticia del día #1 (solo FB) | 10:00 | – | – |
| SF · Post foto (solo FB) | 10:30 | – | – |
| IR · Historia detrás / Fe que consuela | 12:00 | 12:00 | 12:00 |
| SF · Liguilla / noticia | 13:15 | 12:30 | 14:00 |
| IR · Post foto (solo FB) | 15:00 | – | – |
| IR · Noticia del día #2 (solo FB) | 17:30 | – | – |
| SF · Estrella (El día que / Polémica / Trivia / Pizarra viernes) | 19:00 | 19:00 | 19:00 |
| IR · Historia estrella | 20:00 | 19:30 | 20:00 |

### Prueba A/B del video estrella de Impulso Real (30 nov – 13 dic 2026)

Pregunta: ¿el estilo con imágenes (diorama de plastilina) retiene y trae más seguidores que el papel mejorado (subtítulos grandes, empujón de cámara)? Se decide con datos, no con gustos.

| Días de la estrella IR (20:00) | Versión | `"formato"` en la cola |
|---|---|---|
| Martes, jueves y domingo | **Imágenes**: motor `diorama` sin plantilla (imágenes fijas animadas: cámara, boil, polvo, títulos), voz Edgardo | `IR · Historia estrella (imágenes)` |
| Lunes, miércoles, viernes y sábado | **Papel mejorado** (plantilla `papel`), voz Edgardo | `IR · Historia estrella (papel)` |

Mismo tipo de tema en las dos (historia real, bíblica o parábola con giro), misma duración (61–75 s) y misma hora, para que lo único que cambie sea el estilo.

**Cómo llegan las imágenes (sin gastar créditos):**
1. El **planeador** (sábado), por cada fila de imágenes de la semana, escribe `diorama/guiones/<id>-imagenes.md` con **8 prompts** (p01…p08), uno por escena, en este estilo fijo: *“Diorama de plastilina en stop-motion, figuras de plastilina hechas a mano, escenario en miniatura de papel recortado, luz cálida cinematográfica, formato vertical 9:16, sin texto, sin logotipos, [escena]”*, con los mismos personajes descritos igual en cada prompt (ropa, colores, edad) para que se parezcan. Personajes genéricos: nunca el parecido de una persona real ni de un actor. En el mensaje final le pega a Alberto los prompts de cada video.
2. **Alberto** los genera en Gemini y los sube a la carpeta de Drive **“Impulso Real · Imágenes video estrella”** (ID `1hZm8TxBIEH7EFkfiPe8wQUpO8gD8fVT-`, compartida con enlace), en una subcarpeta con el `id` del video, con los nombres `p01`, `p02`… (jpg o png). Fecha límite: la noche anterior.
3. El **agente IR**, el día del video, busca la subcarpeta en Drive (`search_files` por nombre; **no descargues las imágenes**, gastan muchos tokens): si están las 8, escribe la historia `diorama/<id>.json` con `"img_drive": {"p01": "<fileId>", …}` y escenas con `img`, `move`, `titles` (ejemplo de estructura: `diorama/2026-10-30-daniel-foso.json`), `"tts": "elevenlabs"`, `"tts_respaldo": "edge"`. El publicador de GitHub baja las imágenes y genera el video. En la nube el preview sale con marcadores café: es normal, revisa solo textos y tiempos.
4. Si faltan imágenes, **no se pierde el día**: hace la versión papel con el mismo guion, `"formato": "IR · Historia estrella (papel)"`, y lo dice en J (“sin imágenes”).

**Cómo se decide (sábado 13 dic, el planeador):** con al menos 4 videos de cada versión, compara en `RESUMEN.md` y en lo que Alberto reporte de TikTok la mediana de vistas, los segundos vistos y los seguidores nuevos. Gana la versión que saque **≥20 % más de segundos vistos o de seguidores**; si la diferencia es menor, se queda papel (es gratis y no depende de nadie). Si ganan las imágenes, se propone a Alberto pasarlas a todas las estrellas o generarlas con el conector de ElevenLabs (~406 créditos por imagen, unos 3,250 por video).

**Zona horaria:** las horas son de Ciudad Juárez, pero el público está casi todo en hora del centro (CDMX, UTC−6). En invierno Juárez va **1 h atrás** de CDMX (09:00 Juárez = 10:00 CDMX). Desde el 14 mar 2027 Juárez cambia al horario de verano y queda igual que CDMX: ese día el planeador suma 1 h a todas las franjas para seguir cayendo en la misma hora del público.
Los estudios de 2026 (Sprout Social: ~2,000 millones de interacciones, hora local del público) marcan para Facebook la ventana **12–20 h** (mejor martes y miércoles; lunes 12–13 h; jueves 12–14 h y 20 h; fines de semana lo más flojo); Metricool marca 10–12 h. Por eso nada sale antes de las 10:00 ni después de las 21:00 hora CDMX. Cuando haya ≥5 publicaciones por franja con métricas reales, mandan los datos propios.
Se basan en los picos generales de mediodía (Instagram) y tarde-noche (Facebook y TikTok) y en la rutina del público (camino al trabajo, comida, noche). Cuando una red lleva otra hora que la de Facebook, va en `"horas"` del item de la cola.

## Estructuras de video (las que retienen y generan comentarios, guardados y seguidores)

Reglas para todos: **gancho en el segundo 0–2** (dato, pregunta o afirmación fuerte, texto grande, sin saludo ni logo), cambio visual cada 1.5–3 s, subtítulos palabra por palabra, un **re-gancho a la mitad** (“pero lo peor viene ahora…”), cierre con **pregunta de respuesta fácil (A o B)** y un final que conecte con el inicio para que se repita.

| Formato | Duración | Estructura | Indicador que busca |
|---|---|---|---|
| SF · Noticia | 25–35 s | 1 dato o polémica · 2 contexto (marcador/tabla) · 3–4 lo que nadie está diciendo · 5 qué sigue (Liguilla, próximo rival) · 6 pregunta A/B | Comentarios, compartidos |
| SF · Pizarra F7 | 61–70 s | 1 problema del amateur (“¿te pasa que…?”) · 2–4 solución en 3 pasos en la pizarra · 5 error común · 6 ejercicio · 7 “guárdalo y mándaselo a tu equipo” · 8 pregunta | Guardados, compartidos |
| SF · Explica / Jugada / Posiciones 3D | 45–70 s | **Retirados del plan diario** desde el 27 nov (0 seguidores nuevos). Solo si Alberto lo pide en la hoja; la estructura sigue en el historial de git. | – |
| SF · Liguilla | 30–40 s | 1 el dato que cambia la serie · 2 marcador/tabla · 3 qué necesita cada uno · 4 re-gancho (“y ojo con…”) · 5 pregunta A/B (“¿pasa o se cae?”) | Comentarios, compartidos |
| SF · Polémica | 30–45 s | 1 la jugada/declaración en una frase · 2 lo que se ve · 3 postura A · 4 postura B · 5 lo que dice el reglamento o el dato · 6 vota A/B | Comentarios |
| SF · El día que… | 61–75 s | 1 el instante más tenso · 2 contexto en 2 frases · 3 la tensión sube · 4 silencio y clímax · 5 qué cambió después · 6 “¿lo viste en vivo?” | Seguidores, retención |
| SF · Trivia | 30–40 s | 5 preguntas con cuenta de 3 s · la 5 sin respuesta (“dímela en los comentarios”) | Comentarios |
| SF · Debate/Top | 45–60 s | Top 5 en cuenta regresiva, el #1 polémico · “¿quién falta?” (variante de Polémica) | Comentarios |
| IR · Reflexión / Lección / Tecnología | – | **Retirados del plan diario** desde el 27 nov (los de peor retención en TikTok). Solo si Alberto lo pide. | – |
| IR · Historia detrás | 35–50 s | 1 “la cantaste mil veces y nunca supiste…” · 2 quién y cuándo (dato verificado) · 3 lo que pasaba en su vida · 4 re-gancho: el detalle que nadie sabe · 5 por qué hoy significa eso · 6 pregunta personal (“¿a quién te recuerda?”) | Compartidos, seguidores |
| IR · Fe que consuela | 40–55 s | 1 el dolor del espectador (“si hoy sientes que…”) · 2 el personaje en ese mismo dolor · 3 lo que pasó · 4 giro · 5 la frase que se queda · 6 “escribe ‘amén’ si lo necesitabas” o pregunta | Comentarios, compartidos |
| IR · Historia | 61–75 s | 1 empieza en el momento más tenso · 2 contexto · 3 conflicto · 4 giro · 5 la lección en una frase · 6 pregunta personal (“¿Tú qué habrías hecho?”) | Seguidores, retención |

En el texto del post: primera línea = el gancho (no el título), una pregunta para comentar y 3–5 hashtags.

## 1 · Planeador semanal (sábado)

1. Lee esta guía y **`cola/metricas/RESUMEN.md`** (si existe): “Camino a monetizar”, formatos, horas y días con mejor y peor puntaje, Top 5 y tendencia de seguidores. Planea para cerrar la brecha más grande de ese avance (p. ej., si YouTube va lento en suscriptores, más series con “parte 2”). Revisa `git log --oneline -40` y los nombres de `stories/` y `diorama/` de los últimos 14 días para no repetir temas.
2. Busca en la web el calendario de Liga MX (o Liguilla) y de FC Juárez para la semana siguiente (lunes a domingo).
3. Escribe en la hoja (añade filas debajo de las existentes, H vacío) **6 publicaciones por día**: por página 2 reels + 1 post de foto, con las franjas y formatos de “Pilares y formatos” y “Horarios”, la regla 70/20/10 y las fechas especiales:

| Página | Franja | Formato | Reparto en la semana |
|---|---|---|---|
| Impulso Real | 12:00 | IR · Historia detrás / IR · Fe que consuela (diorama papel) | 4 Historia detrás + 3 Fe que consuela (más Historia detrás en diciembre: villancicos, Nochebuena, Posadas, Guadalupe). |
| Impulso Real | 20:00 | IR · Historia estrella — mar/jue/dom **(imágenes)**, lun/mié/vie/sáb **(papel)**, Edgardo (ver “Prueba A/B”) | Historias reales, bíblicas o parábolas con giro; series de 2 partes cuando algo funcione. En las 3 de imágenes escribe también los 8 prompts. |
| Impulso Real | 15:00 | Post foto (solo FB) | Frase, versículo o “completa la frase”. |
| Impulso Real | 10:00 y 17:30 | IR · Noticia del día (post foto, solo FB) | Diario. E = “Noticia del día (se decide esa mañana)”, F vacío, **H = `Autorizado`** (autorización permanente de Alberto del 27 nov) y I = “Autorización permanente (27 nov)”. |
| Señor Fútbol | 13:15 | SF · Liguilla (reel) | Diario mientras haya Liguilla; después, la noticia más fuerte de Liga MX (prioridad Bravos). El tema exacto se decide esa mañana. |
| Señor Fútbol | 19:00 | SF · El día que… (L-M-V, Edgardo) · SF · Polémica / Trivia (mar, jue, sáb, dom) · **SF · Pizarra F7 solo viernes** | Si el viernes cae una final, la Pizarra se pasa al sábado. |
| Señor Fútbol | 10:30 | Post foto (solo FB) | Encuesta A/B del partido del día o “completa la frase”. |

   - En B pon la hora de Facebook; si IG o TikTok van a otra hora, escríbelo en F (“IG 12:30 · TikTok 14:00”).
   - En G pon `FB, IG, YT, TikTok` salvo que Alberto haya pedido otra cosa en la hoja.
   - En E y F escribe tema y gancho concretos (la frase de los primeros 2 s), no genéricos. Marca con “🧪” los experimentos del 10 %.
4. Mensaje final (corto): link de la hoja, el avance hacia monetizar (seguidores y vistas por red contra la meta), 3 líneas de lo que dicen los indicadores (qué funcionó, qué se cambia y por qué), la tabla compacta de la semana y “Marca Sí / Sí con cambios / No en la columna Autorizado. Lo que no esté autorizado el día anterior no se produce.”

## 2 · Agente Impulso Real (diario, 5:20 am) y 3 · Agente Señor Fútbol (diario, 8:45 am)

1. Lee la hoja (`Temario!A:K`). Toma las filas de **hoy** de tu página con H autorizado y J vacío o “Pendiente”. Si no hay ninguna, actualiza J de las filas de hoy sin autorización con `No autorizado` y termina con un mensaje de una línea.
2. Antes de producir, revisa `cola/estado/` de ayer: escribe en J de esas filas `Publicado: FB ✅ IG ✅ YT ✅ TikTok ✅` (o el error en pocas palabras).
3. Para cada fila autorizada:
   - **Señor Fútbol (motor `reel`)**: sigue el “Flujo diario” de CLAUDE.md (verificación con fuentes, historia en `stories/AAAA-MM-DD-a-…json` o `-b-…json`, `--preview` y revisar `revision.png` con Read). Voz: pon en la historia `"tts": "edge", "edge_voz": "es-MX-JorgeNeural"` (voz gratis más fluida que kokoro; Alberto la pidió así). En la nube el preview puede salir con kokoro; el video final en GitHub sale con Jorge. Escribe `say` con puntuación natural (comas, puntos suspensivos) para que fluya, sin exclamaciones en cada frase.
   - *(Retirado del plan diario; solo si Alberto lo pide)* **Señor Fútbol · Posiciones 3D (motor `diorama`)**: igual que la Jugada 3D (`"vis": "jugada"`, cancha f7, base `diorama/2026-11-24-sf-jugada-tercer-hombre.json`), pero centrada en UNA posición: marca al jugador con `label` ("TÚ") y `marca`, ilumina su zona con `zone`, y muestra sus tareas con y sin balón con flechas; una escena “EN PAUSA” con el error común. Archivo `diorama/AAAA-MM-DD-sf-posicion-<tema>.json`; cola con `"formato": "SF · Posiciones 3D"`.
   - *(Retirado del plan diario; solo si Alberto lo pide)* **Señor Fútbol · Explica 3D / Jugada 3D (motor `diorama`)**: historia en `diorama/AAAA-MM-DD-sf-explica-<tema>.json` o `-sf-jugada-<tema>.json` con `"plantilla": "iso"`, `"marca": "senorfutbol"`, `"tts": "edge"`, `"edge_voz": "es-MX-JorgeNeural"` (esquema en CLAUDE.md, “Plantilla iso”). Ejemplos: `diorama/2026-11-23-sf-explica-medidas-cancha.json` y `diorama/ejemplo-sf-jugada-3d.json`. Preview con `build_diorama.py --preview` y revisa que las figuras se vean grandes y nada quede en la zona roja. En la cola: `"motor": "diorama"`, `"pagina": "senorfutbol"`, `"formato": "SF · Explica 3D"` o `"SF · Jugada 3D"`.
   - **Formatos nuevos de Señor Fútbol (motor `reel`, `stories/`, 1080×1920):** *Liguilla* = `scoreboard` o `table` + `compare`/`stats` + `question`; *Polémica* = `headline` (la jugada) + `compare` (postura A vs B) + `stats` (dato o regla, con fuente) + `question`; *El día que…* = `count`/`scoreboard`/`play` con frases cortas y tensión (ejemplo: `stories/2026-11-26-b-portero-gol-final-2013.json`); *Trivia* = 5 escenas `headline` (pregunta en `title`) con `count` de 3 s y la respuesta en la siguiente, la quinta sin respuesta. `"formato"` en la cola = el nombre exacto de la tabla (“SF · Liguilla”, “SF · Polémica”, “SF · El día que…”, “SF · Trivia”).
   - **Formatos nuevos de Impulso Real (motor `diorama`, plantilla `papel`):** *Historia detrás* y *Fe que consuela* usan `vis: "arma"` (fondos, figuras, props y carteles sin escribir código) o escenas `vis` existentes; el primer cartel lleva el gancho. En *Historia detrás* cada dato (año, autor, lugar) se verifica con 2 fuentes y va en `sources`; si la anécdota es leyenda, se dice (“cuenta la leyenda…”). Nunca la grabación de la canción ni letras con derechos.
   - **Pasa la “Lista de retención”** antes del commit (revisa los primeros 3 cuadros de `revision.png`: gancho visible, sin mayúsculas largas, algo moviéndose).
   - Si ya existe una historia de esa fecha y tema en `stories/` o `diorama/` (p. ej. una prueba previa), reúsala y ajústala en vez de escribirla de cero.
   - **Voz ElevenLabs (Edgardo) en los videos estrella** — créditos limitados (plan Starter: tope **45 videos al mes**). Solo en **IR · Historia (20:00) todos los días** y en **SF · Estrella (19:00) lunes, miércoles y viernes**. En esas historias pon `"tts": "elevenlabs", "tts_respaldo": "edge"` y deja `edge_voz` (si ElevenLabs falla o se acaban los créditos, sale con la voz de Microsoft, no con kokoro). Antes de usarla cuenta con `grep -l '"tts": "elevenlabs"' diorama/AAAA-MM-* stories/AAAA-MM-* | wc -l` las de este mes: si ya hay 45, usa edge. Escribe `say` con puntuación natural (comas, puntos suspensivos): Edgardo actúa lo que lee. En la nube el preview sale con otra voz (sin acceso a ElevenLabs); el video final lo genera GitHub con Edgardo (`voice_id` en `config/voz.json`, llave en el secreto `ELEVENLABS_API_KEY`). Si el estado trae `aviso` de ElevenLabs, dilo en el mensaje final.
   - **IR · Noticia del día (motor `post`, 2 al día)**: busca (WebSearch) lo más importante de las **últimas 24 h** en tecnología/IA, innovación y ciencia, deportes fuera de la Liga MX (Checo, Canelo, NFL, Mundial 2026, selección), México y el mundo. Elige 2 de **categorías distintas**, que no repitan tema de los últimos 3 días (`ls posts/ | grep noticia`), con preferencia por lo que le toca al público mexicano. Reglas:
     - Lee la nota completa (WebFetch o el agente web-fetch) y confirma el hecho con **2 medios confiables** (Reuters, AP, AFP, EFE, BBC, El Universal, Milenio, El Financiero, Expansión, The Verge, ESPN…). Si solo hay una fuente o es rumor, no va. Nunca “según redes”. Las dos URL van en `sources`.
     - Di quién lo informa (“según Reuters…”) y lo que es pedido, demanda o acusación se escribe así, no como hecho consumado. Si es lo que “escribió” una cuenta o una persona, debe estar citado por un medio.
     - Tono neutral: sin opinión política, sin burla, sin alarmismo, sin “URGENTE” en mayúsculas. Nada de tragedias con víctimas como gancho ni de apuestas.
     - Archivo `posts/AAAA-MM-DD-ir-noticia-<1|2>-<tema>.json`: `"kicker": "ÚLTIMA HORA · TECNOLOGÍA"` (o INNOVACIÓN, DEPORTES, MÉXICO, MUNDO), `texto` = el hecho en 15–30 palabras con `<em>` en la palabra clave, `"autor": "Fuente: <medio>"`, `pregunta` de respuesta en una palabra (“¿Te comprarías unas?”), `post` = el hecho en 2–3 líneas + contexto en una línea + la pregunta, 3 hashtags (`#Noticias` + 2 del tema). Revisa el JPG con Read (nada cortado).
     - Cola: `"formato": "IR · Noticia del día"`, `"redes": ["facebook"]`, hora 10:00 o 17:30. Si se publica tarde, la nota sigue siendo de las últimas 24 h.
   - **Post foto (motor `post`, solo Facebook)**: escribe `posts/AAAA-MM-DD-<ir|sf>-post-<tema>.json` (esquema en `engine/build_post.py`: `kicker`, `texto` con `<em>` para la palabra clave, `autor` o `dato`, `pregunta` sin emojis, `post`, `hashtags`, `sources` si hay datos), corre `python3 engine/build_post.py <json>` y revisa `salida/<id>/<id>.jpg` con Read. Cola: `{"id": "...", "pagina": "...", "motor": "post", "historia": "posts/....json", "hora": "...", "redes": ["facebook"], "formato": "IR · Post foto" | "SF · Post foto", "tema": "..."}`. El texto del post: primera línea = gancho, una pregunta y 2–4 hashtags; no metas ligas (Facebook les baja el alcance).
   - *(Retirado; solo si Alberto lo pide)* **IR · Tecnología**: verifica cada dato en la nota completa (WebFetch) y anota las URL en `sources`; si no hay una noticia confirmable de las últimas 48 h, haz una Lección.
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
