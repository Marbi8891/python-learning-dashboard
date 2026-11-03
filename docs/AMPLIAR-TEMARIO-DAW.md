# Integración del ciclo DAW: arquitectura y cómo ampliar el temario

Fecha: 2 de noviembre de 2026. Complementa a [PLAN-CURRICULO-DAW.md](PLAN-CURRICULO-DAW.md) (diagnóstico del 26/10 y currículo oficial) y a [TESTING.md](TESTING.md).

## 1. Auditoría breve: qué había y qué se reutiliza

La sección DAW **no es una aplicación aparte**: usa el mismo frontend (HTML, CSS y módulos ES sin framework), el mismo enrutado por hash, el mismo backend FastAPI y el mismo progreso sincronizado.

| Pieza | Dónde | Cómo se usa en DAW |
|---|---|---|
| Rutas | `frontend/js/app.js` y `frontend/js/daw.js` (`#/daw/...`) | `#/daw/cursos`, `#/daw/<curso>`, `#/daw/<curso>/leccion/<lección>`, `#/daw/<curso>/practica/<bloque\|repaso>` y `#/daw/curriculo[/<módulo>]`. Todas funcionan al recargar y por enlace directo (GitHub Pages sirve `index.html` y el hash no llega al servidor). |
| Currículo oficial | `scripts/curriculum/` → `frontend/data/curriculum/daw-cyl.json` | Los 17 módulos de Castilla y León (Orden EDU/1311/2024) con los RA y los CE literales del RD 405/2023. |
| Contenido de los cursos | `scripts/courses/<curso>_course.py` → `frontend/data/courses/<curso>/{lessons,bank}.json` | Un script por asignatura. Las respuestas se comprueban **ejecutando** el código al generar. |
| Cuestionarios | `frontend/js/daw.js` | Mini-quiz por lección y práctica por bloque con test, completar el hueco, ordenar líneas y encontrar el error. Las respuestas no se muestran hasta corregir. |
| Progreso | `frontend/js/course-store.js`, `/api/v1/course-state/{curso}` | Un documento por curso en el navegador (`pld:course:<id>`) y, con sesión, en la cuenta. Fusión sin pérdidas y puerta de sincronización (AUD-001): no se sube nada hasta haber fusionado la copia de la cuenta; versión por documento con 409 si otra pestaña guardó antes. |
| Panel del alumno | `#/panel/progreso` | Preguntas practicadas y dominadas por módulo oficial (campo `module` de cada pregunta). |
| Seguridad del contenido | `frontend/js/markdown.js` (`renderMarkdown`, `escapeHtml`, `safeUrl`) y `progress-guard.js` | Markdown propio sin HTML; todo dato que llega de fuera se valida antes de pintarlo. |

**Riesgos que se han tenido en cuenta:** no tocar la puerta de sincronización ni la fusión existentes (solo se amplían); no añadir dependencias; los JSON de `frontend/data/` no se editan a mano; la lista de documentos de progreso del backend (`COURSES` en `backend/app/schemas.py`) es cerrada y hay que añadir cada curso nuevo.

**Restricciones de despliegue:** fusionar en `main` publica la web (`.github/workflows/pages.yml`). El backend vive en Render y la base de datos en Neon (plan gratuito). Ningún cambio de esta integración necesita migración de base de datos: el progreso nuevo va dentro del documento JSON de cada curso.

## 2. Qué añade esta iteración

- **Asignatura piloto: Lenguajes de marcas y sistemas de gestión de información (0373).** Seis unidades según los RA del RD 405/2023, 66 preguntas de banco y 12 de mini-quiz (`scripts/courses/marcas_course.py`).
- **Unidad completa.** Cada lección puede tener objetivos, errores frecuentes, resumen y una solución explicada del ejercicio, además de la teoría, el ejemplo, el ejercicio, el mini-quiz, el reto, las dudas y las fuentes que ya tenía. Por ahora solo Lenguajes de marcas usa estos campos; los demás cursos se ven igual que antes.
- **Completar lección y continuar.** Botón «Marcar la lección como completada»; el panel del curso muestra «x de N lecciones completadas» y «Continuar».
- **Catálogo de recursos complementarios** con licencia, acceso y fecha de verificación (`scripts/resources/build_resources.py` → `frontend/data/resources.json`), visible en el panel del curso y en cada lección.

## 3. Progreso por lección (sin pérdida de datos)

Se guarda en el mismo documento del curso, con dos campos nuevos (`frontend/js/lesson-progress.js`):

| Campo | Formato | Fusión entre la cuenta y el navegador |
|---|---|---|
| `done` | `{ "<lección>": "<fecha ISO>" }` | **Unión**. Una lección completada en cualquier copia sigue completada (con la fecha más antigua). Una copia vacía o parcial no borra nada. |
| `lastLesson` | `{ "slug": "<lección>", "at": "<fecha ISO>" }` | Gana la más reciente. |

- Completar es **idempotente**: pulsar dos veces no cambia la fecha ni vuelve a guardar.
- Abrir una lección solo guarda si es distinta de la última.
- `progress-guard.js` descarta ids raros, fechas inválidas o HTML que llegue de `localStorage` o de la cuenta.
- **Compatibilidad:** las cuentas antiguas no tienen estos campos y siguen funcionando (se tratan como vacíos). Las versiones anteriores de la web conservan los campos que no conocen, así que no los borran.
- **Reversión:** basta con revertir el commit. Los campos `done` y `lastLesson` quedarían en los documentos sin que nadie los lea, sin romper nada.
- **No se mide el tiempo de estudio:** no hay una forma fiable de hacerlo en el navegador.

## 4. Cómo añadir una asignatura

1. Crea `scripts/courses/<id>_course.py` copiando la estructura de `marcas_course.py`: bloques (`Block`), lecciones (`Lesson`) y preguntas (`Q`). Llama a `main("<id>", BLOCKS, runner, check_example, module="<código>")`, con el código oficial del módulo.
2. Genera los JSON: `python scripts/courses/<id>_course.py`.
3. Registra el curso:
   - en `frontend/js/course-store.js` (`DAW_COURSES`: id, `module`, título, subtítulo y lenguaje);
   - en `frontend/js/daw.js` (`TRY`, el texto de «Para probarlo»);
   - en `backend/app/schemas.py` (`COURSES`): sin esto, la cuenta rechaza su progreso;
   - en `.github/workflows/ci.yml` (paso «Cursos al día»).
4. Regenera el currículo para que cuente las preguntas del módulo: `python scripts/curriculum/build_curriculum.py`.
5. Ajusta las e2e que cuentan cursos o módulos (`e2e/daw.spec.js`, `e2e/dashboard.spec.js`).

## 5. Cómo crear una unidad

Una unidad es un `Lesson` dentro de un `Block`:

| Campo | Obligatorio | Qué es |
|---|---|---|
| `slug`, `title` | Sí | Id estable (no lo cambies: el progreso lo usa) y título. |
| `theory` | Sí | Markdown seguro: párrafos, listas, negrita, código y bloques de código. |
| `example` | Sí | Código que **se ejecuta** al generar: si falla, el script falla. |
| `exercise`, `starter`, `hint` | Sí | Ejercicio guiado, código de partida y pista. |
| `challenge` | Sí | Reto autónomo: título, estrellas (1-3), enunciado, código de partida y pista. |
| `questions` | Sí | Banco de práctica del bloque. |
| `quiz` | Sí | Mini-quiz de la lección. |
| `faq`, `sources` | Sí (pueden ir vacías) | Dudas frecuentes y fuentes verificables. |
| `objectives`, `mistakes`, `summary`, `solution` | No | Unidad completa. Si faltan, no salen en el JSON. |

### Formato de las preguntas

| Tipo | Ayuda en `marcas_course.py` | Cómo se comprueba la respuesta |
|---|---|---|
| Teórica (opción múltiple) | `tq` | Índice de la correcta (`answer`). |
| Sobre un fragmento | `kq` | Igual que la teórica, con el fragmento en `code`. |
| ¿Qué muestra este código? | `pq` | Se ejecuta y la salida tiene que ser `expect`; los distractores no pueden coincidir. |
| Completar el hueco | `fq` | Cada respuesta aceptada se ejecuta y tiene que dar `expect`. |
| Ordenar líneas | `oq` | Se ejecuta el orden correcto; intercambiar dos líneas vecinas no puede dar lo mismo. |
| Encontrar el error | `bq` (en `java_course.py`) | El código con error no da `target` y el corregido sí. |
| ¿Está bien formado este XML? / ¿Es JSON válido? | `wq` / `jq` | El analizador de Python tiene que darle la razón a la opción marcada. |
| Modelo de contenido de una DTD | `dq` | Exactamente una opción encaja en el modelo. |

La puntuación es la de la plataforma: acierto por bloque con el último intento de cada pregunta, ponderado por el peso del bloque (los pesos suman 100), y repaso espaciado (cajas de Leitner).

## 6. Recursos complementarios

`scripts/resources/build_resources.py` contiene el catálogo. Cada recurso tiene id (`res-…`), título, módulos, lecciones, autor, URL (y descarga si la hay), idioma, tipo, licencia, condiciones de reutilización, acceso, calidad, descripción y fecha de verificación.

- **No se inventa ninguna licencia.** Si el recurso no declara licencia, se pone «No identificada» y el acceso `licencia-no-identificada`: solo se enlaza.
- La plataforma **no copia** el contenido de estos recursos: las explicaciones de los cursos son propias.
- El validador falla con ids repetidos o mal formados, campos vacíos, URL que no son https, tipos o accesos desconocidos, módulos que no están en el currículo, lecciones que no existen y recursos «descargables» sin URL de descarga. Se ejecuta en CI (`--check`) y en `backend/tests/test_resources.py`.

Para añadir uno: añade su ficha a `RESOURCES`, ejecuta `python scripts/resources/build_resources.py` y revisa el resultado.

## 7. Pruebas

| Qué | Dónde |
|---|---|
| Respuestas y soluciones de Lenguajes de marcas | `python scripts/courses/marcas_course.py --check` |
| Catálogo de recursos | `python scripts/resources/build_resources.py --check` y `backend/tests/test_resources.py` |
| Fusión y validación del progreso por lección | `tests/unit/lesson-progress.test.mjs` |
| Enlace directo, recarga, mini-quiz, práctica, completar, continuar, recursos y sincronización con la cuenta sin borrar lo de otro dispositivo | `e2e/daw.spec.js` |
| Accesibilidad (axe, WCAG 2.1 AA) de una lección y del panel de Lenguajes de marcas | `e2e/daw.spec.js` |

## 8. Limitaciones conocidas y siguiente paso

- **Currículo de Castilla y León.** Otras comunidades tienen su propia norma con otras horas o cursos. El catálogo está en un JSON generado, así que se puede añadir otro plan sin cambiar las vistas.
- **Sin curso todavía:** Sistemas informáticos (0483), Desarrollo web en entorno servidor (0613), Despliegue (0614), Diseño de interfaces (0615), el proyecto intermodular y los módulos transversales.
- Los cursos anteriores (Programación, Bases de datos, Entornos, JavaScript y Java) aún no tienen objetivos, errores frecuentes, resumen ni solución: se pueden añadir lección a lección con los campos opcionales.
- La relación de las preguntas es con el módulo, no con criterios de evaluación concretos.
- Las preguntas de HTML, CSS, XSD y XSLT que Python no procesa son teóricas: su respuesta la ha revisado una persona, no un programa.

**Siguiente asignatura recomendada:** Diseño de interfaces web (0615). Reutiliza HTML y CSS de Lenguajes de marcas y tiene buena documentación abierta (MDN).

## Antes de abrir el PR de un curso nuevo o ampliado

1. Regenera el curso y comprueba que está al día: `python scripts/courses/<curso>_course.py` y después `--check`.
2. Registra los ids nuevos: `python scripts/courses/lock_ids.py`. Nunca borres ni renombres un id registrado sin un plan de migración, porque el progreso del alumno se guarda por id.
3. Pasa `cd backend && python -m pytest -q tests/test_daw_courses.py`: detecta contenidos vacíos, preguntas repetidas, referencias a RA o criterios que no existen y enlaces rotos.
4. Mira qué elementos pedagógicos faltan: `python scripts/courses/audit_pedagogy.py`.

La auditoría completa del temario está en [`AUDITORIA_TEMARIO_DAW.md`](AUDITORIA_TEMARIO_DAW.md).
