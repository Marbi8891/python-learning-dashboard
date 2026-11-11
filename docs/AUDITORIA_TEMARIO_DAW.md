# Auditoría del temario de DAW (Fase D)

3 de noviembre de 2026, sobre `main` en `e34bfd4`. Parte del trabajo anterior: [`PLAN-CURRICULO-DAW.md`](PLAN-CURRICULO-DAW.md) (catálogo oficial, fases A a D) y [`AMPLIAR-TEMARIO-DAW.md`](AMPLIAR-TEMARIO-DAW.md) (cómo añadir asignaturas). Aquí se revisa lo que hay, se corrige lo que estaba mal y se dejan las pruebas que pide 6.4.

## 1. Verificación curricular

### 1.1 Normativa

| Norma | Qué fija | Comprobación de hoy |
|---|---|---|
| Real Decreto 686/2010, en la redacción del RD 405/2023 (anexo I) | RA, CE, contenidos básicos y ECTS de los 9 módulos técnicos | Los 64 RA y 516 CE del catálogo se extrajeron del XML oficial del BOE y se comprobaron literalmente (PLAN-CURRICULO-DAW, §5). No he encontrado ninguna modificación posterior en 2025 ni en 2026 |
| Real Decreto 500/2024, artículo séptimo | Módulos transversales, sin FOL, EIE ni FCT, y «Proyecto intermodular» | Sin cambios |
| Orden EDU/1311/2024, de 26 de noviembre (BOCYL 2/12/2024) | Horas, curso y horas semanales en Castilla y León | Sigue siendo la orden del ciclo: es una de las 77 órdenes de grado superior de esa fecha (EDU/1286 a EDU/1362/2024). No he encontrado ninguna corrección de errores ni modificación |

**Límite de esta comprobación:** desde el entorno de trabajo no se puede descargar el BOE ni el BOCYL (la red lo bloquea y el BOCYL no deja leer sus páginas a herramientas automáticas). La vigencia se ha comprobado con búsquedas, no releyendo el texto consolidado. Antes de presentar el proyecto conviene abrir la [ficha del título en el portal de FP de la Junta](https://www.educa.jcyl.es/fp/es/catalogo-titulos-fp-castilla-leon/catalogo-titulos-grado-superior/desarrollo-aplicaciones-web) y el texto consolidado del [RD 686/2010](https://www.boe.es/buscar/act.php?id=BOE-A-2010-9269).

### 1.2 Pendiente de verificar (sin cambios desde octubre)

1. Los RA de los cinco módulos transversales (0179, 1709, 1710, 1665 y 1708) están en el RD 659/2023 y no se han extraído. Se muestran como «pendientes», sin datos inventados, y una prueba lo vigila.
2. En la extracción de la orden no aparece en qué curso va el 0616, Proyecto intermodular.
3. El optativo I tiene 34 h con 2 h semanales, que no cuadra con 34 semanas.
4. Qué optativos ofrece el centro.
5. **Nuevo:** en el 0487, RA3, el criterio c aparece partido en dos: «c) Se han identificado las herramientas de depuración y prueba de aplicaciones» y «d) ofrecidas por el entorno de desarrollo.». Así está en `scripts/curriculum/rd_405_2023_daw.json`, extraído del XML del BOE. Si es un fallo de la extracción, las letras de la d en adelante están corridas una posición. No se ha corregido porque desde aquí no se puede abrir el BOE para comprobarlo, y ningún objetivo de la plataforma cita el RA3.

### 1.3 Origen de cada contenido

| Tipo (6.1) | Qué es en la plataforma | Dónde se dice |
|---|---|---|
| 1. Texto normativo literal | Los RA, los CE y los contenidos básicos del catálogo, con la norma y el anexo | `#/daw/curriculo/<módulo>` |
| 2. Resumen pedagógico propio | Los objetivos de las lecciones. En Lenguajes de marcas citan el RA y los criterios («RA2 a, d») | **Nuevo:** aviso bajo los objetivos que citan un RA, con enlace al texto oficial |
| 3. Explicaciones originales | Teoría, ejemplos, errores frecuentes y resúmenes | **Nuevo:** sección «De dónde sale este contenido» en cada curso |
| 4. Ejercicios y preguntas | 520 preguntas, ejercicios y retos, con las respuestas de código comprobadas al ejecutarlas | Ídem, y «son práctica, no evaluaciones del centro» |
| 5. Recursos de terceros | Las fuentes de cada lección y los 24 recursos complementarios, con autor y licencia | Ya existía. Programación sigue el orden de las UT del curso «DAW-Programacion» de César San Juan Pastor (CC BY-NC), sin copiar su texto. Ahora también se dice en el panel del curso |

Cada curso dice ahora de dónde sale el orden de sus unidades (campo `structure` de `DAW_COURSES` en `course-store.js`): las UT de un curso abierto con licencia, el temario del centro, los RA del real decreto o una selección propia.

## 2. Módulos del ciclo y contenido de la plataforma

| Código | Módulo | Curso | RA oficiales | Curso de la plataforma | Preguntas |
|---|---|---|---|---|---|
| 0373 | Lenguajes de marcas | 1º | 7 | Lenguajes de marcas | 66 |
| 0483 | Sistemas informáticos | 1º | 7 | — | 0 |
| 0484 | Bases de datos | 1º | 7 | Bases de datos (SQL) | 110 |
| 0485 | Programación | 1º | 9 | Programación (Python) y Java | 243 |
| 0487 | Entornos de desarrollo | 1º | 6 | Entornos de desarrollo | 51 |
| 0612 | Desarrollo web en entorno cliente | 2º | 7 | JavaScript | 50 |
| 0613 | Desarrollo web en entorno servidor | 2º | 9 | — | 0 |
| 0614 | Despliegue de aplicaciones web | 2º | 6 | — | 0 |
| 0615 | Diseño de interfaces web | 2º | 6 | — | 0 |
| 0179, 1709, 1665, 1708, 1710 | Transversales | 1º y 2º | Pendientes | — | 0 |
| 0616 | Proyecto intermodular | Sin localizar | Pendientes | — | 0 |

El curso PCAP sigue aparte: no está asociado a ningún módulo ni a ningún criterio de DAW.

## 3. Estructura pedagógica (6.2)

Generado con `python scripts/courses/audit_pedagogy.py`:

| Curso (lecciones) | Objetivos | Conocimientos previos | Explicación | Ejemplo comentado | Ejercicio y reto (dos niveles) | Solución razonada | Errores frecuentes | Cuestionario | Criterios de superación | Resumen para repasar | Fuentes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| entornos (4) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| java (10) | ✗ | — | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | — | ✗ | ✓ |
| js (10) | ✗ | — | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | — | ✗ | ✓ |
| marcas (6) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| programacion (12) | ✗ | — | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | — | ✗ | ✓ |
| sql (14) | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ |

✓ todas las lecciones · ✗ ninguna · — la plataforma aún no tiene ese campo.

- **Lenguajes de marcas, Entornos de desarrollo y Bases de datos tienen la unidad completa.** Los otros tres cursos (32 lecciones) tienen teoría, ejemplo, ejercicio, reto, mini-quiz y fuentes, pero no objetivos, solución razonada, errores frecuentes ni resumen.
- **Ningún curso tiene todavía «conocimientos previos» ni «criterios de superación».** Son campos nuevos: conviene definirlos en `course_builder.py` antes de rellenarlos.
- El **repaso** existe a nivel de curso (repaso espaciado de las preguntas falladas), no por lección.

Completar las lecciones es trabajo de contenido. Cada texto tiene que escribirse y comprobarse (las soluciones se ejecutan al generar el curso), así que no se rellena sin revisar. Orden propuesto: Entornos (hecho), Bases de datos (hecho), Programación (12), JavaScript y Java.

**Entornos de desarrollo, completado.** Las 4 lecciones tienen objetivos, errores frecuentes, resumen y solución explicada. Los objetivos citan solo los criterios que la lección trabaja de verdad: RA1 b, c, d, e, f y g, y RA5 a en Paradigmas (clases, objetos, atributos y métodos). Los objetivos sin un criterio claro, como «máquina virtual o contenedor» o «requisitos funcionales y no funcionales», no citan ningún RA. `check_solutions()` ejecuta las soluciones de Python y comprueba su salida (6,5; 15; 120 tres veces). La de la lección 4 es una planificación en comentarios, porque el ejercicio es de análisis y no de código. Las lecciones solo cubren el RA1 (y una parte del RA5): los RA2 a RA6 (IDE, pruebas, refactorización y control de versiones, diagramas UML) siguen sin contenido en la plataforma.

**Bases de datos, completado.** Las 14 lecciones tienen objetivos, errores frecuentes, resumen y solución explicada. Los objetivos citan los RA1, RA2, RA3, RA4 y RA6 según lo que trabaja cada lección. `check_solutions()` ejecuta las 17 consultas de las soluciones en SQLite con las tablas de ejemplo y compara su salida. También comprueba que las restricciones de las soluciones de diseño rechazan lo que deben: un préstamo de un socio que no existe, una devolución anterior a la salida, un precio negativo o un ISBN repetido. Las partes que solo existen en MySQL (`GRANT`, `CREATE USER`) van como comentario. Siguen sin contenido el RA5 (procedimientos, funciones, disparadores y cursores) y el RA7 (bases de datos no relacionales).

## 4. Generación y validación (6.4)

Lo que ya existía y sigue igual: cada generador (`scripts/courses/<curso>_course.py --check`) ejecuta las respuestas de código con Python, SQLite, Node o Java y comprueba que el JSON está al día. `build_curriculum.py --check` valida el catálogo, y `build_resources.py --check` los recursos.

**Nuevo: `backend/tests/test_daw_courses.py`** (46 pruebas, sin red):

| Qué detecta | Prueba |
|---|---|
| Identificadores que desaparecen (el progreso se guarda por id) | `test_locked_ids_still_exist`, con el registro `scripts/courses/ids.lock.json` (609 ids). `scripts/courses/lock_ids.py` añade los nuevos y nunca quita ninguno |
| Ids nuevos sin registrar, o repetidos | `test_new_ids_are_registered`, `test_ids_are_unique` |
| Contenidos vacíos (teoría, ejemplo, ejercicio, plantilla, reto, quiz y fuentes) | `test_lessons_have_no_empty_content` |
| Preguntas repetidas dentro de un curso, opciones vacías o repetidas, respuesta fuera de las opciones, huecos sin respuesta aceptada | `test_questions_are_well_formed_and_not_repeated` |
| Preguntas que apuntan a una unidad, una lección o un módulo que no existen | `test_questions_point_to_their_unit_lesson_and_module` |
| Referencias normativas inexistentes: un objetivo que cita «RA6 e» tiene que citar un RA y un criterio que existan en el catálogo | `test_cited_outcomes_and_criteria_exist` (22 citas comprobadas) |
| Enlaces rotos: fuentes sin https y enlaces internos a rutas o lecciones que no existen | `test_links_are_https_or_known_routes` |
| Soluciones vacías o iguales a la plantilla | `test_published_solutions_are_complete` |

Los enlaces externos no se comprueban contra la red en la CI: un sitio caído no debe romper el despliegue. Su formato y su licencia los valida `build_resources.py`.

**Lo que encontraron las pruebas nuevas (corregido):**

- `sql-07` era la misma pregunta que `bd-25` (`WHERE nota = NULL`). Ahora practica `IS NULL` con `OR`. Se conserva el id.
- `sql-12` era la misma pregunta que `bd-28` (`AVG(nota)`). Ahora practica `COALESCE`, que la teoría de esa lección explica. Se conserva el id.

Las dos preguntas cambian de texto pero no de id. Si un alumno ya las había respondido, su historial cuenta como de la pregunta nueva, sin perder el resto del progreso.

## 5. Otros currículos sin duplicar el contenido

La separación ya existe en los datos:

- **Estatal**, común a todas las comunidades: `scripts/curriculum/rd_405_2023_daw.json`, con los RA, CE y contenidos básicos extraídos del BOE.
- **Autonómico**: la tabla `CYL_MODULES` de `build_curriculum.py`, con las horas, el curso y las horas semanales de la orden.
- **Contenido de la plataforma**: los cursos de `frontend/data/courses/`, enlazados por el código del módulo (`"module": "0485"`), no por la comunidad.

Para añadir otra comunidad bastaría con una tabla nueva con su orden, generar `daw-<comunidad>.json` y elegir el catálogo en `curriculum.js` (hoy fijo en `daw-cyl.json`). Los cursos y las preguntas no se duplican, porque cuelgan del código del módulo, que es estatal. No se ha implementado porque nadie lo ha pedido todavía.

## 6. Siguientes pasos propuestos

1. ~~Completar Entornos de desarrollo y Bases de datos~~ (hecho). Siguiente: Programación (12 lecciones), con el mismo modelo.
2. Añadir a `course_builder.py` los campos «conocimientos previos» y «criterios de superación», y mostrarlos en la lección.
3. Extraer del RD 659/2023 los RA de los módulos transversales, con el mismo método que `extract_boe.py`. Hace falta descargar el XML del BOE desde un equipo con acceso.
4. Empezar un módulo sin contenido. El siguiente propuesto es 0615 Diseño de interfaces web.
