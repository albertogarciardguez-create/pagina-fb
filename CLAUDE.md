# Fábrica de reels — Señor Fútbol

Este repositorio genera los reels animados de la página de Facebook **Señor Fútbol** (facebook.com/senorfutbol), de Alberto García (Ciudad Juárez). Formato: video vertical 1080×1920, 25–35 s, gráficas animadas estilo papel/tinta, voz en off en español, música y efectos, subtítulos. **Nadie sale a cuadro.** Todo el contenido es original (sin escudos, fotos ni clips de transmisiones), para que la página pueda monetizar.

## Flujo diario (lo que debe hacer la tarea programada)

1. **Instalar** (una vez por sesión): `bash setup.sh`
2. **Elegir la noticia del día — Liga MX.** Busca en la web lo más relevante de las últimas 24–48 h: resultados y polémicas de la jornada, carrera por la Liguilla, equipos en crisis o en racha, goleadores, fichajes y declaraciones fuertes. Elige el tema con más potencial de debate para la afición mexicana. Si hay algo relevante de **FC Juárez**, dale prioridad (la audiencia es de Juárez).
3. **Verificar datos.** Cada número y cada hecho del video debe salir de una fuente confiable (Mediotiempo, ESPN, Récord, TUDN, Claro Sports, El Informador, sitio oficial de la Liga MX, etc.). Usa WebFetch para leer la nota, no solo el titular. **Nunca inventes ni estimes un dato.** Si no puedes confirmarlo, no lo uses. Anota las URL en `sources`.
4. **Escribir la historia** en `stories/AAAA-MM-DD-tema-corto.json` (ver esquema abajo y el ejemplo `stories/2026-10-15-juarez-ultimo.json`).
   - 6 a 8 escenas, 25–35 s en total.
   - Escena 1 = gancho fuerte (dato impactante en los primeros 3 s).
   - Última escena = tipo `question`, con una pregunta polémica y "¡Te leo en los comentarios!" en la voz.
   - `say`: lo que dice la voz. Español mexicano, frases cortas, exclamaciones y preguntas para darle energía. **Números con letra** ("ochenta y cuatro"), nunca dígitos.
   - `captions`: el mismo texto partido en trozos de 2–5 palabras, con dígitos ("84") y `<em>palabra</em>` para resaltar en verde las palabras clave.
   - Textos en pantalla en MAYÚSCULAS y cortos.
5. **Revisar**: `python3 engine/build.py stories/<archivo>.json --preview` y abre `salida/<id>/revision.png` con Read. Revisa que no haya textos encimados o cortados, que todo se lea y que los datos sean correctos. Si hay cuadros que no se distinguen bien, abre los individuales en `salida/<id>/revision/`. Corrige y repite.
6. **Generar el video**: `python3 engine/build.py stories/<archivo>.json` (tarda ~3 min). Queda en `salida/<id>/<id>.mp4` y el texto para publicar en `salida/<id>/post.txt`.
7. **Entregar a Alberto**: manda el MP4 con SendUserFile y en tu mensaje final incluye, listo para copiar: el texto del post con hashtags, la mejor hora para publicar ese día (según partidos) y las fuentes.
8. **Guardar**: haz commit solo del JSON de la historia (`salida/` está ignorada) y push a `main`.

## Esquema de la historia

```json
{
  "id": "2026-10-16-tema",            // igual al nombre del archivo, sin .json
  "header": "LIGA MX · APERTURA 2026",  // línea pequeña bajo la marca
  "voice": "em_santa",                  // voz por defecto
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
