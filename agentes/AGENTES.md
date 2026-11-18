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

## 1 · Planeador semanal (sábado)

1. Lee esta guía, `git log --oneline -40` y los nombres de `stories/`, `diorama/` y `cola/estado/` de los últimos 14 días para no repetir temas. Si hay estados con resultados, fíjate qué formatos sí se publicaron.
2. Busca en la web el calendario de Liga MX (o Liguilla) y de FC Juárez para la semana siguiente (lunes a domingo).
3. Escribe en la hoja (añade filas debajo de las existentes, H vacío) **4 publicaciones por día**:

| Página | Hora | Formato (motor) | Contenido |
|---|---|---|---|
| Señor Fútbol | 13:15 | Noticia (reel) | Lo más fuerte de Liga MX del día; prioridad Bravos. El tema exacto se decide esa mañana: en E pon el partido/tema probable y en F el ángulo. |
| Señor Fútbol | 20:30 | Pizarra F7 (reel) lun–mié–vie–dom · Debate/Top (reel: ranking/compare/question) mar–jue–sáb | Pizarra: un concepto táctico de fútbol 7 que no se haya hecho, con ejercicio. Debate: ranking o cara a cara con pregunta polémica. |
| Impulso Real | 07:30 | Reflexión papel (diorama, plantilla papel) | 35–45 s. Estoicismo, liderazgo, fe, hábitos, finanzas personales. Público 30–44 años. |
| Impulso Real | 21:00 | Historia (diorama, papel o infografía) | 45–75 s. Historia bíblica, de un estoico o una lección de vida/película, con giro final y pregunta. |

   - En G pon `FB, IG, YT, TikTok` salvo que Alberto haya pedido otra cosa en la hoja.
   - En E y F escribe tema y gancho concretos (los primeros 2 s del video), no genéricos.
4. Mensaje final (corto): link de la hoja, la tabla compacta de la semana y “Marca Sí / Sí con cambios / No en la columna Autorizado. Lo que no esté autorizado el día anterior no se produce.”

## 2 · Agente Impulso Real (diario, 5:20 am) y 3 · Agente Señor Fútbol (diario, 8:45 am)

1. Lee la hoja (`Temario!A:K`). Toma las filas de **hoy** de tu página con H autorizado y J vacío o “Pendiente”. Si no hay ninguna, actualiza J de las filas de hoy sin autorización con `No autorizado` y termina con un mensaje de una línea.
2. Antes de producir, revisa `cola/estado/` de ayer: escribe en J de esas filas `Publicado: FB ✅ IG ✅ YT ✅ TikTok ✅` (o el error en pocas palabras).
3. Para cada fila autorizada:
   - **Señor Fútbol (motor `reel`)**: sigue el “Flujo diario” de CLAUDE.md (verificación con fuentes, historia en `stories/AAAA-MM-DD-a-…json` o `-b-…json`, `--preview` y revisar `revision.png` con Read). Voz: la de `config/voz.json`.
   - **Impulso Real (motor `diorama`)**: historia en `diorama/AAAA-MM-DD-<tema>-reel.json` con `"plantilla": "papel"` (o `"infografia"`), `"tts": "edge"`, `"edge_voz": "es-MX-DaliaNeural"`, sin campo `audio`. Reutiliza escenas `vis` existentes siempre que se pueda; si hace falta una nueva, agrégala en la plantilla y revisa que se vea bien. Gancho en el segundo 0–2, cierre `"tipo": "cierre"` con pregunta. Preview con `python3 engine/build_diorama.py <json> --preview` y revisa la hoja con Read.
   - No hace falta generar el MP4 final aquí: lo genera el publicador en GitHub.
   - Crea `cola/<id>.json`:
     ```json
     {"id": "2026-11-20-ir-manana-la-piedra", "pagina": "impulsoreal", "motor": "diorama",
      "historia": "diorama/2026-11-20-la-piedra-reel.json", "hora": "2026-11-20 07:30",
      "redes": ["facebook", "instagram", "youtube", "tiktok"], "titulo": "Título corto para YouTube #Shorts"}
     ```
     `pagina`: `senorfutbol` | `impulsoreal`. `motor`: `reel` (stories/) | `diorama` | `anime` | `largo`. `redes` según la columna G. El texto del post sale de `post` + `hashtags` de la historia (más ligas en los reels de SF); pon `"texto"` solo si quieres otro.
   - Si la hora ya está a menos de 25 min, pásala a la siguiente media hora libre y anótalo en J.
4. `git add` de las historias y de `cola/*.json`, commit `Agente <página> AAAA-MM-DD` y push a `main` (reintenta con `git pull --rebase` si falla). El push dispara el publicador.
5. En la hoja, J = `En cola · <hora>` y K = `https://github.com/albertogarciardguez-create/pagina-fb/releases/download/cola/<id>.mp4` (el video aparece ahí ~10 min después).
6. Mensaje final (corto, listo para leer en el celular): por cada publicación, hora, tema, redes y link del video; y una línea con el resultado de ayer. Nada de explicar el proceso.

## Publicador (GitHub Actions)

- Se dispara con cada push que agrega `cola/*.json` y cada 20 min.
- Genera el video una sola vez (lo guarda en el release `cola`), programa **Facebook** (Reels API) y **YouTube** (`publishAt`) en cuanto llega, y sube **Instagram** (Reels, subida reanudable) y **TikTok** (bandeja de borradores) a su hora.
- Si faltan los secretos de una red, la marca como omitida y sigue con las demás. Cada red se reintenta hasta 3 veces. Lo que no salió 36 h después de su hora se marca `caducado`.
- Prueba sin publicar: `python3 engine/publicador.py --simular`. Ver qué toca: `python3 engine/publicador.py --revisar`.
- Configuración de cuentas y secretos: `agentes/CONFIGURAR.md`.
