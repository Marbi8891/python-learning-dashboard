# PLD Video Factory

Convierte las lecciones reales de PLD en vídeos educativos en español e inglés: guion, voz,
animación, subtítulos, miniatura, metadatos e informe de calidad. Todo se ejecuta en local y con
herramientas gratuitas (Manim, Kokoro, FFmpeg). No hay claves ni servicios de pago.

Estado: **piloto**. Lo comprobado y lo pendiente está en [Estado del piloto](#estado-del-piloto).

## Cómo funciona

```
frontend/data/*.json ──► inventory ──► video-production/catalog.json   (103 lecciones reales)
                              │
                           script ──► video-production/scripts/<id>.json   (escenas ES + EN)
                              │
                            audio ──► narration_<idioma>.wav + timeline.json   (Kokoro)
                              │            la duración de cada escena la marca la voz
                           render ──► un clip por escena (Manim) ──► MP4 + VTT + JPG (FFmpeg)
                              │
                         validate ──► video-production/reports/<id>.validation.{json,md}
                              │
                  review ──► publish     (solo si supera la validación y la revisión manual)
```

- **La narración manda.** Se sintetiza frase a frase, se mide y con eso se fija la duración de
  cada escena. La animación se adapta a esa línea de tiempo y los subtítulos salen de ella, así que
  voz, imagen y subtítulos no se desfasan.
- **Un clip por escena.** Cada escena se renderiza en un proceso de Manim distinto y se guarda con
  la huella de sus entradas. Si cambias una frase, solo se rehace esa escena. Si el proceso se
  corta, basta con repetir la orden: lo terminado no se repite.
- **Componentes reutilizables.** Las 14 escenas de `video_factory/animation/scenes.py` se dibujan
  con los datos del guion. Una lección nueva no necesita código nuevo.

## Qué lecciones tienen vídeo

`python -m video_factory inventory` lee el temario y escribe `video-production/catalog.json`:

| Familia | Origen | Lecciones |
|---|---|---|
| `learn` | `frontend/data/learning.json` (conceptos con teoría propia y unidades de POO) | 20 |
| `pcap` | `frontend/data/lessons.json` | 27 |
| `daw` | `frontend/data/courses/*/lessons.json` | 56 |

- 11 conceptos de «Aprender» no tienen teoría propia: enlazan a una lección del PCAP. No se les
  hace otro vídeo; la lección del PCAP los lista en `also_covers`.
- El curso de Ciberseguridad no entra: es un plan semanal, no lecciones con teoría y ejemplo.
- No existe ninguna lección «PY-001 Hello, World!» en el temario, así que el piloto es la primera
  lección real: `pcap-variables` («Variables y print()»).
- El catálogo es un JSON generado: no se edita a mano. Si cambia el temario, se regenera (hay una
  prueba que falla si no está al día). El estado de producción de cada lección se conserva.

Estados: `pending` → `scripted` → `audio_ready` → `animation_ready` → `rendered` → `reviewed` →
`published`, y `error` (con el motivo en el campo `error`).

## Instalación en macOS (Intel)

Probado el diseño para un MacBook Pro de 2019 (i5, 16 GB, sin GPU). No usa CUDA.

```bash
brew install ffmpeg cairo pango pkg-config     # FFmpeg y las bibliotecas que necesita Manim
python3.12 -m venv .venv-video                 # Python 3.11 o 3.12
source .venv-video/bin/activate
pip install -r video_factory/requirements-dev.txt
cp video_factory/.env.example video_factory/.env
python -m video_factory models                 # dice cuánto ocupa la descarga y cuánto espacio hay
python -m video_factory models --download      # ~120 MB, a ~/.cache/pld-video-factory/models
python -m video_factory doctor                 # comprueba que todo está listo
```

- **No hace falta LaTeX**: las escenas solo usan texto (Pango), no fórmulas.
- **Kokoro** (`kokoro-onnx`, modelo cuantizado de 92 MB + 28 MB de voces) funciona en CPU. En uso
  ocupa unos 500 MB de RAM y se libera antes de empezar a renderizar: voz y animación no están en
  memoria a la vez. Voces por defecto: `ef_dora` (español) y `af_heart` (inglés), las dos femeninas.
- **Otro motor de voz** sin tocar el código: `PLD_TTS_ENGINE=command` y la orden en
  `PLD_TTS_COMMAND`. Sirve para Piper, para `say` de macOS o para un proveedor externo. Ejemplo con
  la voz del sistema: `say -v Mónica -o {out} --data-format=LEI16@24000 -f {text_file}`.
- La pronunciación de términos técnicos se ajusta en `video_factory/pronunciation.json`
  (solo cambia lo que se lee, no los subtítulos).

## Uso

```bash
python -m video_factory inventory                          # regenerar el catálogo
python -m video_factory script --lesson pcap-variables     # crear o comprobar el guion
python -m video_factory audio  --lesson pcap-variables --language es
python -m video_factory render --lesson pcap-variables --language es --quality preview
python -m video_factory build  --lesson pcap-variables     # todo, en los dos idiomas
python -m video_factory build  --lesson pcap-variables --dry-run
python -m video_factory validate --lesson pcap-variables
python -m video_factory review --lesson pcap-variables --approve
python -m video_factory publish --lesson pcap-variables
python -m video_factory build-all --family pcap            # todas las que tengan guion listo
python -m video_factory report                             # estado y espacio usado
```

| Opción | Para qué |
|---|---|
| `--quality preview` | 854×480 a 15 fps: rápido, para revisar ritmo y contenido |
| `--quality final` | 1920×1080 a 30 fps, H.264 + AAC (por defecto) |
| `--dry-run` | Muestra qué se haría y el espacio estimado, sin hacer nada |
| `--jobs N` | Escenas renderizadas a la vez (por defecto 1; con 16 GB, no más de 2) |
| `--retries N` | Intentos por paso antes de dar la lección por fallida (por defecto 2) |
| `--force` | Rehacer aunque la caché esté al día |

`build-all` procesa las lecciones de una en una, comprueba el espacio antes de cada una, registra
los fallos en el catálogo y en `factory.log` y sigue con la siguiente.

### Archivos de cada lección

En `PLD_VIDEO_WORK_DIR/renders/final/` (por defecto dentro de `video-production/`, ignorado por git):

`<id>-es.mp4`, `<id>-en.mp4`, `<id>-es.vtt`, `<id>-en.vtt`, `<id>-<idioma>.txt` (transcripción),
`<id>-<idioma>.jpg` (miniatura) y `<id>-<idioma>.json` (metadatos de producción). La narración está
en `audio/<id>/<idioma>/narration_<idioma>.wav`. Los MP4 llevan además los subtítulos incrustados
como pista de texto.

## Guiones

El guion es un JSON validado con Pydantic (`video_factory/models.py`). Cada escena tiene: `id`,
`type` (el componente), `section`, `narration` y `heading` en los dos idiomas, `code`, `output`,
`steps` (lo que aparece y cuándo) y `data` (datos propios del componente).

`script --lesson <id>` genera un **borrador** con el contenido de la lección: teoría troceada en
escenas, ejemplo con sus notas línea a línea, salida real del ejemplo (se ejecuta), ejercicio y
resumen. El borrador no se puede producir tal cual:

- La narración en español es la teoría leída, sin adaptar al formato de vídeo.
- **El temario de PLD no está en inglés**, así que la narración inglesa queda vacía.
- Las escenas sin texto propio se marcan con `needs_edit`.

Para terminarlo se edita el JSON, se pone `"origin": "edited"` (así no se sobrescribe) y se repite
`script --lesson <id>`, que lista lo que falta. Reglas que comprueban las pruebas y el validador:

- Todo el código que se muestra tiene que estar en la lección (ejemplo, teoría, ejercicio o
  plantilla). El vídeo no puede enseñar código inventado.
- El español y el inglés tienen el mismo número de frases por escena, porque los pasos se
  sincronizan con `"sentence": n` (aparece al empezar la frase n). También valen `"at"` y
  `"until"` (fracción de la escena) o nada (reparto uniforme).
- Un texto `{"es": …, "en": …}` dentro de `data` se muestra en el idioma del vídeo.

### Componentes

| `type` | Componente | Datos (`data`) |
|---|---|---|
| `title` | `TitleScene` | `kicker` |
| `concept` | `ConceptScene` | `emphasis` (opcional); viñetas en `steps[].text` |
| `code` | `CodeScene` | `filename`, `run_at_sentence`; líneas en `steps[].line`; con `output`, lo ejecuta |
| `terminal` | `TerminalScene` | `command`, `output_at_sentence` |
| `variable` | `VariableScene` | `assignments`: `[{name, value, code}]` (repetir nombre = reasignar) |
| `datatype` | `DataTypeScene` | `items`: `[{value, type, note}]` |
| `conditional` | `ConditionalScene` | `condition`, `branches`: `[{label, body}]`, `taken` |
| `loop` | `LoopScene` | `variable`, `items`, `outputs` |
| `function` | `FunctionScene` | `name`, `params`, `args`, `result` |
| `list` | `ListScene` | `name`, `items`; posiciones en `steps[].index` |
| `dictionary` | `DictionaryScene` | `name`, `pairs`; claves en `steps[].key` |
| `error` | `ErrorScene` | `error_type`, `message`, `fix` |
| `exercise` | `ExerciseScene` | viñetas en `steps[].text`; plantilla en `code` |
| `summary` | `SummaryScene` | puntos en `steps[].text` |

Los colores son los del tema oscuro de la web (`frontend/css/tokens.css`), en
`video_factory/animation/theme.py`. La primera escena (`title`) hace de introducción y la última
(`summary`) de cierre. La música está desactivada; se activa con `PLD_MUSIC_FILE` y solo debe
usarse música propia o con una licencia que lo permita.

## Control de calidad

`validate` comprueba, para cada idioma: que el vídeo existe y se abre, resolución, FPS, códecs
(H.264 yuv420p y AAC), que la duración coincide con la narración (±0,5 s), que los subtítulos son
WebVTT válido, sin solapes y dentro del vídeo, y que ninguna escena está vacía (se mira un
fotograma de cada una). Además: guion completo en los dos idiomas, código igual al de la lección,
guion al día respecto a la lección y sin errores de renderizado.

El informe incluye la lista de **revisión manual** (sincronización, pronunciación, legibilidad,
exactitud didáctica). `review --approve` solo funciona si la validación en calidad final está
superada, y `publish` solo si la lección está revisada. Un vídeo no pasa a `published` de otra forma.

## Almacenamiento y publicación

- Los MP4 **no van al repositorio**. `PLD_VIDEO_WORK_DIR` puede apuntar a otra carpeta o disco.
- `publish` copia los archivos finales a `PLD_VIDEO_PUBLISH_DIR` (por defecto `frontend/videos/`,
  ignorado por git) para probarlos en local.
- Estimación antes de producir en lote: unos 392 minutos por idioma en todo el catálogo. El espacio
  real por minuto todavía no está medido (ver abajo); `build --dry-run` da la estimación actual.
- Dónde alojar los vídeos publicados está **sin decidir**: no caben en el repositorio de Pages.

## Pruebas

```bash
python -m pytest video_factory/tests -q
ruff check video_factory && ruff format --check video_factory
```

Las pruebas usan una voz muda y clips lisos, así que no necesitan Manim ni modelos. Las de
`test_manim_scenes.py` renderizan los 14 componentes de verdad y se saltan si Manim no está
instalado. Todavía no están en `ci.yml`.

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `pangocairo >= 1.30.0 is required` al instalar | Faltan Cairo y Pango: `brew install cairo pango pkg-config` |
| `Faltan los modelos de Kokoro` | `python -m video_factory models --download` |
| `falta el audio actualizado` | Cambió el guion o la voz: repite `audio --lesson <id>` |
| `Espacio insuficiente` | Libera espacio o mueve `PLD_VIDEO_WORK_DIR` a otro disco |
| El código sale sin colores | La fuente une caracteres: cambia `PLD_FONT_MONO` (por ejemplo `Menlo`) |
| Una palabra se pronuncia mal | Añádela a `video_factory/pronunciation.json` y repite `audio` |
| Validación: «escenas vacías» | El clip es liso: revisa `PLD_RENDERER` y el `factory.log` |

## Estado del piloto

Comprobado en un contenedor Linux (sin Manim, que allí no se puede instalar):

- Inventario de 103 lecciones reales y borrador de guion para todas.
- Guion piloto `pcap-variables` completo en español e inglés.
- Narración real con Kokoro en los dos idiomas (150 s y 149 s) con su línea de tiempo.
- Subtítulos, transcripción, montaje H.264 + AAC, miniatura, metadatos, caché, reanudación y
  validación, usando clips lisos en lugar de animaciones.

Pendiente:

- **Renderizar las animaciones con Manim** y corregir lo que falle: el código de las escenas está
  escrito pero todavía no se ha ejecutado.
- Escuchar las dos voces y ajustar la pronunciación.
- Medir tamaño y tiempo de render reales, y decidir el alojamiento.
- Reproductor en la web y trabajo de CI.
- Guiones del resto de lecciones (cada uno necesita adaptación y la versión inglesa).
