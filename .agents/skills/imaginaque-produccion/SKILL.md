---
name: imaginaque-produccion
description: Ciclo de producción de ImaginaQue desde Claude Code (idea → guion → voz ElevenLabs → 3D de bloques → montaje → QA → Bandeja → publicación con confirmación). Úsala para producir, retomar un render, revisar la cola o preparar publicaciones en TikTok (imaginaquepasara) y YouTube (OtraRealidadXX).
---

# ImaginaQue · producción desde Claude Code

El procedimiento es **`motor/NIGHTLY.md` (manual v9)**: síguelo entero. Esta skill solo explica cómo se ejecuta en Claude Code; no cambia el sistema de producción.
Para la voz y la animación, aplica también la skill `voz-humana-animacion-dinamica`.

## 0. Arranque (en cada sesión)
1. `bash scripts/bootstrap.sh`. Copia `motor/` a `/home/claude/motor`, ejecuta los `setup.sh` y `setup3d.sh` originales y tiene que imprimir `MOTOR OK` y `MOTOR 3D OK`. Esto sustituye al paso 1 del manual («descargar el Motor del artefacto»): el repo ya contiene el Motor.
2. Reloj: `TZ=Europe/Madrid date` (y `date -u`).
3. Estado: vuelca la Bandeja con ArtifactData (`list`, collection `videos`, `query.limit` 300, `out_dir` en el scratchpad) y ejecuta `python3 scripts/cola.py <out_dir>/videos`. Muestra la siguiente Q libre, los renders en curso, los vídeos listos sin programar, los pendientes de YouTube y los posibles duplicados.

## 1. Fuentes de verdad
| Qué | Dónde |
|---|---|
| Manual, código del motor, `series.json` | `motor/` en este repo, con copia en el artefacto Motor https://claude.ai/artifact/GvBRuyVDzp6ghyHY6ejsfn |
| Vídeos producidos, métricas y aprendizajes | Bandeja https://claude.ai/artifact/5aZ6DAFJysLm7ZiPScsxkx (colecciones `videos`, `metricas`, `aprendizajes`, y los mp4 como assets) |
| Voz | Conector ElevenLabs (voz por defecto Juanjo Viral `30jLfQdV8RTduXvosh02`, flow `1SQesMcyvPai6CTHxkg6`) |

Cuando crees o cambies archivos del motor (`shots_<vid>.py`, `audio_<vid>.py`, `subs_<vid>.py`, `series.json`), guárdalos en **los dos sitios**: haz commit en `motor/` y publícalos en el artefacto Motor (`files` + MANIFEST.txt), como pide el manual. Las sesiones que sigan usando el artefacto no deben perder continuidad.

## 2. Ideas sin duplicados
- Antes de escribir un guion: `python3 scripts/cola.py <dump>/videos --titulo "<pregunta>"`. Si devuelve «DUPLICADO PROBABLE» (código 1), elige otra idea.
- Orden de elección: `series.json → estrategia_v11` y `independientes` (lista de Héctor, banco de ideas, regla de variedad).
- Ejemplo de ficha de idea: `produccion/Q31_idea.md`.

## 3. Producción 3D (pasos 3–7 del manual)
- Voz: **una** llamada a `creative_generate_speech`, `generations_count` = 1. Descárgala a `/home/claude/anim/build/<VID>/voice.wav` (mono) y guárdala también en la Bandeja como asset.
- Palabras con tiempos: `asr.transcribe` → `/home/claude/t3d/au/<vid>_words.json` (WER < 0,08).
- Planos: `shots_<vid>.py` a partir de `shots_t1.py` o del vídeo más parecido. QA con `SHOTS=shots_<vid> python3 render.py stills` y revisión de `/tmp/st3` con Read (dos pasadas), y después `render.py preview 4 0/1`.
- Montaje completo, reanudable: `bash scripts/montar3d.sh <vid> <TOTAL> <post_modulo>` en segundo plano (`run_in_background`). Encadena los fotogramas (2 procesos), el etalonaje, el audio con normalización a -14 LUFS, los subtítulos y el ffmpeg final, y saca `/home/claude/t3d/final/<VID>.mp4` y `<VID>_tt.mp4` (< 10 MB).
- Si la sesión se corta, vuelve a lanzar el mismo comando: los fotogramas hechos se saltan. Mientras tanto, en la Bandeja la fila queda con `prod_status: "render en curso"`.
- QA final: 12 fotogramas del montaje revisados con Read. Si algo falla, se corrige y no se publica.

## 4. Entrega y registro (pasos 8–9)
Artifact publish a la Bandeja (`asset: true`, mp4 + portada + voz) y una fila en `videos/<VID>` con todos los campos del paso 9. Si algo falla: `prod_status: "error"`, el motivo exacto y los créditos gastados.

## 5. Publicación: SIEMPRE con confirmación de Héctor (orden del 14-11-2026)
- Antes de subir o programar nada, enseña a Héctor el vídeo, el título, la descripción, los hashtags, la hora y la plataforma, y **espera su «sí»**. Esto prevalece sobre el paso 10 del manual, que publicaba solo.
- Antes de subir: `scripts/cola.py` sin duplicados y comprobación en Studio → Contenido de que no está ya programado ni publicado.
- **TikTok (cuenta imaginaquepasara):** desde el Chrome de Héctor con Claude in Chrome (paso 10c del manual). Solo funciona en una sesión conectada a su ordenador. En la nube no hay Chrome: allí el vídeo queda «listo» en la Bandeja.
- **YouTube (OtraRealidadXX, UCGg6XX6kUy5AFkyokILCXqw):** desde YouTube Studio en Chrome (paso 10e), con el mismo calendario. El conector vidIQ también está conectado a este canal con `canPublish: true`. Es una vía alternativa para cuando Chrome no esté, pero solo con confirmación y respetando `calendario.youtube`.
- Nada de Metricool ni de alojamientos públicos. Etiqueta «Contenido generado por IA» activada.

## Reglas que no se rompen
Las del manual: no gastar dinero ni comprar créditos, nada de imágenes ni vídeo de IA, solo voces de hombre de España, no inventar datos, no afirmar nada que no se haya hecho, y no exponer claves.
