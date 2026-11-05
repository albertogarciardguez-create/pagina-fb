# Biblia del formato ANIME ÉPICO — "El día que…"

Formato copiado del video de referencia (TikTok, 75 s, 36 cortes) y adaptado al español para **Señor Fútbol** e **Impulso Real**. El motor es `engine/build_anime.py`.

## 1. ADN del formato (lo que hace que funcione)

| Elemento | Referencia | Regla para nosotros |
|---|---|---|
| Lienzo | 9:16 negro, imagen 16:9 al centro | Igual (1080×1920, imagen 1080×608). `"formato": "4:3"` la agranda |
| Título | Fijo arriba, 2 líneas, blanco, "El día que…" | Igual + firma de la marca arriba y `*palabra*` en color de acento |
| Subtítulos | Bajo la imagen, blancos, centrados | Igual, solo en español |
| Voz | **Sin narrador**: 8–10 frases cortas de personajes (2–6 palabras) | Igual; cada personaje con su voz (`voces`) |
| Ritmo | Corte seco cada ~2 s (36 tomas en 75 s) | 18–24 tomas de 1.6–2.6 s → 40–60 s |
| Música | Épica, crece, silencio antes del clímax, triunfo | Generada por el motor (sin derechos) o `musica_archivo` |
| Efectos | Cámara lenta, flash blanco, temblor, partículas, líneas de velocidad, ovación | `fx`: `lento`, `flash`, `blanco`, `golpe`, `temblor`, `lineas`, `fundido`; `sfx`: `golpe`, `boom`, `whoosh`, `silbato`, `latido`, `estadio`, `ovacion` |
| Dibujo | Anime deportivo cel-shading, estadio de noche, luces volumétricas, ojos en extremo primer plano | Ver estilo base (sección 3) |
| Cierre | Logo de TikTok | Tarjeta de la marca con pregunta y botón |

## 2. Estructura en 6 actos (copia esta curva)

1. **Apertura (0–5 s)** — objeto icónico en primer plano (balón, piedra) + plano general del lugar. Flash blanco al inicio.
2. **Problema (5–15 s)** — algo sale mal; primer plano del protagonista: "¡Necesito una solución!" / "¡No puede terminar así!".
3. **Intento (15–25 s)** — acción rápida, golpes, temblor; un aliado: "¡Aún no ha terminado!".
4. **Concentración (25–35 s)** — ojo en extremo primer plano (lento + latido), silencio que se acerca, "Sé que puedes".
5. **Clímax (35–48 s)** — carrera con partículas, salto, **3–4 ángulos del mismo momento** (abajo, lado, detrás), impacto con `blanco` + `boom`, red/objetivo. `"climax": true` en la toma del salto: la música se calla 0.7 s antes y explota ahí.
6. **Reacción (48–60 s)** — protagonista en el suelo, el entrenador "Dios mío", el rival "¿Qué fue eso?", tribuna aplaudiendo (`ovacion` + `fundido`).

Catálogo de planos que más usa la referencia: extremo primer plano de ojo · rostro en contraluz · botín pisando pasto con tierra volando · contrapicado heroico contra reflectores · general del estadio · portero volando · red ondeando · rival congelado · tribuna completa.

## 3. Dibujos: cómo sacar imágenes iguales

**Estilo base** (va en cada prompt; ya está en `"estilo"` de cada historia):
> Japanese sports anime film still, cel shading, clean bold line art, dramatic night stadium floodlights, volumetric light beams, lens flare, painterly packed crowd, high contrast cinematic color grade, 16:9 widescreen. No text, no letters, no logos, no club crests, no sponsor marks, no watermark.

**Consistencia de personajes**: primero genera una hoja de personaje por protagonista ("character sheet, front/side/back, same outfit") y úsala como imagen de referencia en todas sus tomas. Las descripciones van en `"personajes"`.

**Prompt de cada toma** = estilo base + descripción del personaje + `prompt` de la toma. `python3 engine/build_anime.py anime/<id>.json --prompts` los saca todos en `salida/<id>/prompts.txt` para pegarlos.

### Tres modos de producción

| Modo | Cómo | Costo | Resultado |
|---|---|---|---|
| **A · Gratis** | Imágenes en la app de Gemini → `anime/img/<id>/tNN.png`; el motor les da cámara, lento, temblor, flash, líneas | 0 créditos | 80 % del look; sin movimiento real dentro del dibujo |
| **B · Híbrido (recomendado)** | Igual que A, pero las 5–6 tomas del clímax (las que traen `video_prompt`) se animan en Kling / Seedance / Veo (imagen inicial = la toma) y se guardan como `tNN.mp4`; cambia `src` a `.mp4` | ~6 clips de 5 s | Casi idéntico a la referencia |
| **C · Completo** | Todas las tomas como clip de 5 s | 18–24 clips | Idéntico; el más caro |

Clips: el motor toma `desde` (segundo de inicio dentro del clip) y `dur`; con `lento` usa la mitad del clip a media velocidad.

## 4. Voces

- Mac (gratis): `"tts": "edge"` con una voz por personaje (`es-MX-JorgeNeural`, `es-US-AlonsoNeural`, `es-AR-TomasNeural`, `es-CO-GonzaloNeural`, `es-ES-AlvaroNeural`, `es-MX-DaliaNeural`…). `semitonos` hace la voz más grave/aguda, `grito: true` le da fuerza de grito.
- Nube: sale con kokoro (`VOZ_MOTOR=kokoro`), útil solo para revisar tiempos.
- ElevenLabs u otra voz: pon el archivo en la línea: `"dice": {"quien": "DT", "t": "Dios mío.", "audio": "anime/audio/dt1.mp3"}`.
- La toma se alarga sola si el diálogo no cabe.

## 5. Reglas para poder monetizar

- **Sin escudos, patrocinadores, logos de liga ni marcas** en los dibujos (ya va en el prompt negativo). La referencia los trae y es justo lo que provoca reclamos y bloqueos de monetización.
- **Jugadores reales**: decir su nombre y contar la jugada está bien; el dibujo debe ser un personaje inspirado (dorsal, colores, peinado), no un retrato fiel. Muchos generadores bloquean rostros de famosos de todos modos.
- Si la historia es real, cada dato (fecha, marcador, minuto) se verifica y va en `sources`. Si es ficción (como la plantilla del portero), no se presenta como noticia.
- Nada de clips de transmisiones ni de otros creadores.

## 6. Comandos

```bash
python3 engine/build_anime.py anime/<id>.json --prompts   # lista de prompts para Gemini/Kling
python3 engine/build_anime.py anime/<id>.json             # MP4 + portada.jpg + revision.jpg + post.txt en salida/<id>/
```
Si falta una imagen, el motor pone una tarjeta "TOMA 07 · falta t07.png" con su prompt, así puedes revisar el ritmo antes de generar nada.

## 7. Esquema

```json
{"id": "...", "marca": "senorfutbol | impulso", "titulo": "El día que *X*…", "tts": "edge | kokoro",
 "formato": "16:9 | 4:3", "pausa": 0.7, "ambiente": true, "musica_archivo": "opcional.mp3",
 "estilo": "...", "personajes": {"NOMBRE": "descripción visual"},
 "voces": {"NOMBRE": {"edge": "es-MX-JorgeNeural", "kokoro": "em_alex", "semitonos": 0, "vel": 1.05, "grito": false}},
 "tomas": [{"src": "anime/img/<id>/t01.png | .mp4", "dur": 2.0, "desde": 0, "mov": "in|out|left|right|up|down|golpe|none",
            "fx": ["lento","flash","golpe","temblor","lineas","fundido"], "blanco": 0.1,
            "sfx": ["golpe", {"k": "estadio", "at": 0.5, "dur": 4, "g": 1.0}],
            "dice": {"quien": "NOMBRE", "t": "¡Frase!", "at": 0.15, "audio": "opcional.mp3"},
            "climax": false, "portada": false, "prompt": "...", "video_prompt": "..."}],
 "cierre": {"pregunta": "...", "dur": 3.5}, "post": "...", "hashtags": ["..."], "sources": ["..."]}
```

Plantillas listas: `anime/2026-11-05-portero-ultimo-minuto.json` (Señor Fútbol) y `anime/2026-11-05-david-goliat.json` (Impulso Real).
