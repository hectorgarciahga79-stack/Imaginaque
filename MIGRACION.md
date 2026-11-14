# Migración de ImaginaQue a Claude Code: estado y verificación

Fecha: 14-11-2026. Rama: `claude/remotion-skills-install-1pm2w6`.

## 1. Auditoría: qué había y dónde
| Componente | Dónde estaba | Estado |
|---|---|---|
| Manual de producción v9 (`NIGHTLY.md`) | Artefacto Motor GvBRuyVDzp6ghyHY6ejsfn | Copiado a `motor/NIGHTLY.md` sin cambios |
| Motor 2,5D «cine» (`anim/`: cairo, alineación, portadas, subtítulos) | Artefacto Motor | Copiado a `motor/anim/` (38 archivos) |
| Motor 3D de bloques (`anim3d/`: Blender bpy, personajes, decorados, etalonaje, audio sintetizado, subtítulos) | Artefacto Motor | Copiado a `motor/anim3d/` (78 archivos, incluidos Q7–Q30, M1A–C y T1) |
| Estrategia, ideas, calendario, voces y presupuesto (`series.json`) | Artefacto Motor | Copiado a `motor/tiktok/series.json` |
| Tipografías, música, efectos y portadas base | Artefacto Motor | Copiado a `motor/tiktok/` |
| Registro de producción: 67 vídeos, métricas, aprendizajes y mp4 | Bandeja 5aZ6DAFJysLm7ZiPScsxkx | Se queda en la Bandeja (no se duplica) y se lee con ArtifactData |
| Skill de voz y animación | `voz-humana-animacion-dinamica` (skill de cuenta) | Ya disponible en Claude Code |
| Automatización | Tarea programada «ImaginaQue · Producción (3 al día)», 02:56/10:56/18:56 Madrid | **Desactivada** y suspendida por *device_absent* (se ejecutaba en el ordenador de Héctor). Última ejecución: 11-11. No se ha tocado. |
| Voz | Conector ElevenLabs, Juanjo Viral `30jLfQdV8RTduXvosh02` | Funciona |
| Publicación en TikTok | Claude in Chrome en el ordenador de Héctor (TikTok Studio) | Depende de su ordenador |
| Publicación en YouTube | Claude in Chrome (YouTube Studio) | Depende de su ordenador; vidIQ como alternativa conectada |

En el repositorio solo había un README. **El motor no existía en git**: ahora `motor/` es su copia versionada.

## 2. Lo que se ha añadido (sin sustituir nada)
- `motor/`: el motor completo, idéntico al artefacto (versión 1794525587-f42b).
- `scripts/bootstrap.sh`: ejecuta los `setup.sh` y `setup3d.sh` originales y añade las librerías Mesa/EGL que Blender necesita en la nube.
- `scripts/montar3d.sh`: encadena los pasos 3D del manual (fotogramas → etalonaje → audio → subtítulos → montaje → copia para TikTok). Se puede reanudar.
- `scripts/cola.py`: cola de publicación, renders en curso, pendientes de YouTube y detector de ideas duplicadas, leyendo la Bandeja.
- Skill `imaginaque-produccion`: cómo seguir el manual desde Claude Code. Añade la confirmación antes de publicar.
- `CLAUDE.md`: contexto del proyecto para cualquier sesión.
- Entorno en la nube **Imaginaque** (personal): el mismo acceso que el Default más los servidores de descarga de Hugging Face, que faster-whisper necesita para transcribir. Su script de arranque instala el motor en cada sesión nueva.

## 3. Verificación (resultados reales de esta sesión)
| # | Comprobación | Resultado |
|---|---|---|
| 1 | Motores accesibles | ✅ `MOTOR OK` (cairo 1.29.2, 26 escenas 2,5D) · ✅ `MOTOR 3D OK` (bpy 5.3.0) |
| 1 | ElevenLabs | ✅ `creative_list_voices` devuelve Juanjo Viral (hombre, peninsular). ⚠️ `account_get_usage` pide reconectar el conector con más permisos: no se puede leer el saldo de créditos. |
| 1 | Transcripción (faster-whisper) | ✅ Tras abrir Hugging Face en el entorno: voz del Q30 transcrita (184 palabras, coincide con el guion). |
| 1 | Bandeja | ✅ 67 filas leídas. Siguiente id libre: Q31 / M2A. Sin renders en curso ni duplicados publicables. |
| 2 | Generación de ideas | ✅ `produccion/Q31_idea.md`: idea 14 de la lista de Héctor, comprobada contra duplicados, con un dato verificado y presentado como estimación, y un guion de 843 caracteres (~64 s) con planos. No se ha gastado voz. |
| 3–4 | Vídeo completo, edición y exportación | RESULTADO_RENDER |
| 5 | YouTube | ✅ vidIQ conectado a OtraRealidadXX (UCGg6XX6kUy5AFkyokILCXqw, 90 suscriptores, 41 vídeos) con `canPublish: true`. ⚠️ vidIQ tiene **0 créditos** hasta el 20-11-2026: hasta entonces no puede listar los vídeos programados ni publicar por esa vía. No se ha publicado nada. |
| 5 | TikTok | ❌ **No verificable desde la nube.** La cuenta imaginaquepasara solo se maneja desde el Chrome de Héctor, y en esta sesión no hay ningún ordenador conectado. Según la Bandeja, hay vídeos programados hasta el 16-11-2026 13:30 (verificados en su día en Studio). |
| 6 | Automatizaciones | Ver la sección 5. |

## 4. Qué sigue dependiendo de servicios externos
- **ElevenLabs** (voz): créditos del plan. Hay que reconectar el conector para poder leer el saldo.
- **Hugging Face** (modelo de transcripción): solo la primera descarga de cada sesión nueva.
- **Ordenador de Héctor + Claude in Chrome**: publicar y medir en TikTok Studio y en YouTube Studio. Sin él, los vídeos se quedan «listos» en la Bandeja.
- **vidIQ**: vía alternativa para YouTube, sin créditos hasta el 20-11.
- **Artefactos de claude.ai** (Motor y Bandeja): registro, assets y continuidad con las sesiones anteriores.
- Pendientes que ya estaban en la Bandeja: YouTube con límite diario de subida para Q24, Q26, Q28, Q29 y Q30. Q2 necesita que Héctor borre la versión anterior.

## 5. Automatización
La tarea programada original está desactivada desde el 11-11 y suspendida porque necesitaba el ordenador de Héctor. **No se ha reactivado ni modificado.** Opciones (decide Héctor):
1. **Producción en la nube:** una tarea nueva en el entorno Imaginaque que ejecute la skill `imaginaque-produccion`. Produce, revisa y deja el vídeo «listo» en la Bandeja, **sin publicar**. Cada vídeo gasta ~1.000–1.150 créditos de ElevenLabs.
2. **Reactivar la tarea original** cuando el ordenador de Héctor esté encendido. Habría que actualizar su texto para que pida confirmación antes de publicar, porque ahora publica sola.
3. Publicar siempre en una sesión con Héctor presente: la cola sale de `scripts/cola.py`.
