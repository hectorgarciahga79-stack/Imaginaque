# ImaginaQue · instrucciones para Claude Code

Canal de vídeos cortos en español de Héctor: TikTok **imaginaquepasara** y YouTube **OtraRealidadXX**. Mini historias «¿Y si…?» en 3D de bloques, narradas con ElevenLabs.

- **Motor de producción:** `motor/` (copia versionada del artefacto Motor). El manual es `motor/NIGHTLY.md` (v9) y la estrategia y los datos están en `motor/tiktok/series.json`.
- **Cómo producir desde Claude Code:** skill `imaginaque-produccion` (`.agents/skills/imaginaque-produccion/SKILL.md`). Empieza siempre por `bash scripts/bootstrap.sh`.
- **Scripts propios de la migración** (no sustituyen al motor, lo encadenan):
  - `scripts/bootstrap.sh`: instala el motor 2,5D y 3D (`MOTOR OK` / `MOTOR 3D OK`).
  - `scripts/montar3d.sh <vid> <TOTAL> <post>`: montaje 3D completo y reanudable.
  - `scripts/cola.py <dump>`: cola, pendientes y control de duplicados de la Bandeja.
- **Estado de la migración y lo que depende de servicios externos:** `MIGRACION.md`.
- `src/` contiene Remotion (instalado el 14-11-2026 con sus skills). Es una herramienta adicional: **no** sustituye al motor 3D de bloques.

## Reglas
- No publicar nada sin la confirmación explícita de Héctor en la conversación.
- No gastar dinero ni comprar créditos. La voz, solo con el conector ElevenLabs (una generación por vídeo).
- Nada de imágenes ni vídeo generados por IA. Solo voces de hombre de España.
- No inventar datos ni dar por hecho algo que no se ha comprobado.
- No borrar configuraciones, credenciales ni publicaciones. No escribir claves en el repo: es **público**.
- Responder en español.
