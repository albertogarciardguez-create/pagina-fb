# Señor Fútbol — fábrica de reels

Genera reels animados (1080×1920) para la página de Facebook **Señor Fútbol** a partir de una historia en JSON: gráficas animadas, voz en off en español, música, efectos y subtítulos.

```bash
bash setup.sh
python3 engine/build.py stories/2026-10-15-juarez-ultimo.json --preview   # hoja de revisión
python3 engine/build.py stories/2026-10-15-juarez-ultimo.json             # video final
```

El video y el texto para publicar quedan en `salida/<id>/`. Las instrucciones completas, el esquema de escenas y las reglas de contenido están en `CLAUDE.md`.
