# Módulo de Programación orientada a objetos (POO)

Módulo de 10 unidades para aprender POO con Python desde cero hasta una aplicación completa, dentro
del núcleo por conceptos (Teoría, Practicar y motor adaptativo). Pertenece al módulo 0485 Programación
de DAW. Se construye por sprints; este documento dice qué hay en cada uno y cómo está hecho.

## Estado

| Sprint | Contenido | Estado |
|---|---|---|
| 1 | Estructura, validadores, vista de unidad, índice `#/poo`, Unidad 2 en el formato nuevo | Hecho |
| 2 | Unidades 1 a 3 (la 2 pasa a pedir la 1) | Hecho |
| 3 | Unidades 4 a 6 | Hecho |

Desde el 11/11/2026 el módulo sigue el plan de cinco PR del diseño de la Fase 2:

| PR | Contenido | Estado |
|---|---|---|
| A | Formato nuevo (buenas prácticas, referencias, origen de los ejemplos, prácticas adicionales, banco) y Unidades 1 a 6 completas, con 90 preguntas de banco | Hecho (#121) |
| B | Unidades 7 y 8 (relaciones entre objetos y métodos especiales), con 30 preguntas de banco más (120 en total) | Hecho (#122) |
| C | Unidades 9 y 10 (diseño y proyecto biblioteca, con diagrama de clases, rúbrica y retos), con 30 preguntas de banco más (150 en total) | Hecho (#134) |
| D | Cuestionario de unidad con nota (70 %), evaluación final de 30 preguntas y repaso de las falladas | En revisión |
| E | Currículo, bibliografía general, progreso, motor adaptativo y documentación | Pendiente |

## Dónde está cada cosa

| Qué | Archivo |
|---|---|
| Índice de unidades, Unidad 2 y reunión de todas las unidades | `scripts/learning/poo_module.py` |
| Una unidad completa por archivo (concepto, campos, ejercicios, banco y errores) | `scripts/learning/poo_u1.py` … `poo_u10.py` |
| Correspondencias propuestas (`proposed`), catálogo de fuentes (`SOURCES`), `ref`, `practice` y reparto del banco | `scripts/learning/poo_common.py` |
| Integración en el mapa de conceptos (área `poo`) | `scripts/learning/concepts.py` |
| Validación y generación | `scripts/learning/build_learning.py` (`check_units`) |
| Datos que usa la web (generados, no se editan a mano) | `frontend/data/learning.json` (`modules` y conceptos del área `poo`) |
| Índice del módulo y página de unidad | `frontend/js/learn/poo-view.js` (rutas en `learn-app.js`) |
| Lecciones completadas | `frontend/js/learn/mastery.js` (`markSection`, `sectionsDone`) |

## Unidades

Cada unidad es **un concepto** del núcleo. El id `poo` es la **Unidad 2** y no cambia: `#/teoria/poo`
sigue funcionando y nadie pierde su progreso. Si una unidad del índice no existiera como concepto,
saldría como «En preparación», sin enlace (hoy están las 10).

| # | Id | Título |
|---|---|---|
| 1 | `poo-fundamentos` | Fundamentos de la programación orientada a objetos |
| 2 | `poo` | Creación de clases y objetos |
| 3 | `poo-atributos-metodos` | Atributos y métodos |
| 4 | `poo-encapsulacion` | Encapsulación y propiedades |
| 5 | `poo-herencia` | Herencia |
| 6 | `poo-polimorfismo` | Polimorfismo |
| 7 | `poo-composicion` | Composición y relaciones entre objetos |
| 8 | `poo-metodos-especiales` | Métodos especiales de Python |
| 9 | `poo-diseno` | Diseño y buenas prácticas |
| 10 | `poo-proyecto` | Proyecto final: gestión de una biblioteca |

Publicadas: las 10 unidades (Sprints 2 y 3, PR A, B y C). En la ruta «Aprender» van seguidas.
Prerrequisitos: `poo-fundamentos` (pide funciones y diccionarios) → `poo` → `poo-atributos-metodos`,
que abre `poo-encapsulacion` y `poo-herencia`; `poo-polimorfismo` pide `poo-herencia`;
`poo-composicion` pide `poo-encapsulacion` y `poo-herencia`; `poo-metodos-especiales` pide `poo` y
`poo-atributos-metodos`; `poo-diseno` pide `poo-polimorfismo` y `poo-composicion`, y `poo-proyecto` pide
`poo-metodos-especiales` y `poo-diseno`.

| Unidad | Lecciones | Ejercicios | Errores típicos nuevos | CE propuestos |
|---|---|---|---|---|
| 1 | Procedural frente a objetos · Clases, objetos y modelado · Cuándo usar la POO y sus pilares | 21 (`poo1-01`…`21`) | clase-instancia, poo-siempre, atributo-metodo | RA2-a, RA2-c, RA4-a |
| 2 | Definir una clase · `__init__` y `self` · Estado de varios objetos · `__str__` | 26 (`poo-01`…`26`) | init-mal-escrito, alias-copia | RA2-h, RA4-b, RA4-d, RA4-e |
| 3 | Atributos de instancia y de clase · Métodos de instancia, de clase y estáticos · Métodos que protegen el estado | 27 (`poo3-01`…`27`) | self-en-atributo-clase, static-con-self, tipo-metodo, lista-de-clase | RA2-d, RA2-e, RA2-f, RA4-c, RA4-h |
| 4 | Público, protegido y privado · `@property` y setter · Validar y proteger el estado | 26 (`poo4-01`…`26`) | privado-absoluto, privado-desde-fuera, property-con-parentesis, setter-recursivo, validacion-fuera, sin-setter | RA4-f, RA2-d, RA4-c |
| 5 | Superclase y subclase · Constructores y `super()` · Sobrescribir y ampliar métodos · Herencia múltiple y MRO | 27 (`poo5-01`…`27`) | es-un-tiene-un, olvida-super, sobrescribir, jerarquia-al-reves | RA4-g, RA7-a, RA7-c, RA7-d, RA7-e |
| 6 | Mismo método, distinto comportamiento · Duck typing · Clases abstractas (`abc`) | 27 (`poo6-01`…`27`) | isinstance-en-cadena, necesita-herencia, abstracta-instanciable, abstracta-sin-implementar, version-base, metodo-sin-llamar | RA7-i, RA7-g, RA7-f |
| 7 | Asociación · Agregación y composición · Delegación · Herencia frente a composición | 27 (`poo7-01`…`27`) | copia-al-guardar, lista-por-defecto, herencia-por-tiene, no-delega, relacion-es-sintaxis | RA7-j, RA4-e, RA6-c |
| 8 | Qué son y cuándo los llama Python · Esenciales (`__str__`, `__repr__`, `__eq__`, `__len__`) · Avanzados (`__contains__`, `__iter__`, `__next__`) | 26 (`poo8-01`…`26`) | nombre-especial-mal, llamada-directa, imprime-en-vez-de-devolver, lista-usa-str, eq-identidad, len-no-entero, iter-no-iterador | RA4-c, RA6-d, RA4-e |
| 9 | Responsabilidad única, cohesión y acoplamiento · Composición frente a herencia e introducción a SOLID · Type hints, docstrings y dataclasses · Organización en módulos y refactorización | 27 (`poo9-01`…`27`) | clase-que-lo-hace-todo, responsabilidad-es-un-metodo, acoplado-a-detalles, copia-de-datos, if-por-tipos, herencia-que-rompe, crea-su-dependencia, hints-obligan, dataclass-lista-por-defecto, sin-documentar | RA3-g, RA7-h, RA4-i |
| 10 | Arquitectura y diagrama de clases · Libro y Usuario · Prestamo: fechas y estado · Biblioteca y excepciones propias · Pruebas, retos y rúbrica | 25 (`poo10-01`…`25`) | estado-a-medias, valida-tarde, dato-duplicado, excepcion-sin-jerarquia, excepcion-generica, except-en-mal-orden | RA4-e, RA3-h, RA3-f |

### Proyecto final (Unidad 10)

El proyecto biblioteca se construye en 6 fases, cada una un ejercicio de código con tests:
`poo10-01` Libro (guiado), `poo10-02` Usuario, `poo10-03` Prestamo, `poo10-04` excepciones propias,
`poo10-05` registro de libros y usuarios y `poo10-06` la `Biblioteca` completa (ejercicio principal).
Cada fase parte del código de las anteriores ya resuelto, así que el alumno se centra en una clase.

La unidad tiene tres apartados opcionales que solo usa el proyecto, y que el validador comprueba:

| Campo | Qué es | Comprobación (`check_project_extras`) |
|---|---|---|
| `diagram` | Diagrama de clases: cajas en una rejilla (`col`, `row`) y relaciones `asociacion`, `agregacion`, `composicion` o `herencia` | Ids únicos, sin dos cajas en la misma celda, relaciones entre clases que existen y con texto |
| `rubric` | Rúbrica de evaluación: criterio, puntos y qué se valora | Suma 100 y cada criterio tiene nombre, puntos y texto |
| `challenges` | Retos de ampliación sin tests | Ninguno vacío |

La web dibuja el diagrama en SVG con `role="img"`, `<title>` y `<desc>`, y debajo repite cada relación
en texto, que es lo que lee un lector de pantalla o quien amplía la página. La rúbrica es una tabla que
en el móvil se lee como fichas.

## Formato de una unidad

Campos opcionales del concepto (los demás conceptos no los tienen y no cambian):

| Campo | Apartado de la página |
|---|---|
| `unit` | `{ module: "poo", number }`: posición en el índice |
| `objectives` | Objetivos de aprendizaje |
| `prior` | Conocimientos previos |
| `sections` | Lecciones: `{ id, title, theory, examples: [{ code, lines, output }], quiz: [3 ids] }` |
| `key` | Conceptos importantes: `[término, definición]` |
| `example` | Ejemplo comentado (el del concepto de siempre) |
| `guided`, `autonomous` | Ejercicios guiados y ejercicio principal (de escribir código, con tests; el principal es el primero de `autonomous`) |
| `extras` | Prácticas adicionales: ejercicios de código que ya existían y dejan de ser principales (no se borra ningún id) |
| `practices` | Buenas prácticas: de 4 a 6 `{ text, why }` |
| `bank` | Cuestionario de la unidad: los ids de sus 15 preguntas de banco |
| `references` | Referencias bibliográficas: `{ source, section, supports, status }` del catálogo cerrado |
| `errors` | Errores frecuentes (los del motor: cada fallo se registra con su causa) |
| `selfcheck` | Autoevaluación |
| `recap` | Resumen (`summary` sigue siendo la frase de presentación del concepto) |
| `pass` | Criterios de superación: `{ minScore, required: [ids], text }` |
| `curriculum` | Relación con el currículo: `[{ ce, status, source, reviewed, by, note }]` |

`build_learning.py` falla si falta un apartado, si un ejemplo no se ejecuta (su salida se calcula
ejecutándolo), si un mini-quiz no tiene 3 preguntas, si una pregunta tipo test no tiene 4 opciones,
si se repite un enunciado, si un ejercicio de la unidad no aparece en ningún apartado, si el código
inicial de un ejercicio ya supera los tests o si una correspondencia curricular no tiene estado,
fuente y fecha. En los ejercicios de código, el «Resultado esperado» que ve el alumno es la salida
real de la solución.

### Banco de preguntas

Cada unidad publicada tiene exactamente 15 preguntas tipo test con `bank: true` (150 con las 10). Son ejercicios `choice` normales del motor, con dos campos más: `qtype` y un `why` en cada
opción incorrecta, que la corrección muestra al fallar («Por qué tu opción no es correcta»).
Las preguntas que ya existían entran en el banco con su mismo id (`BANK_TAGS` de cada `poo_uN.py`).
Los ejercicios de salida, completar, depurar y código no cuentan en las 15.

| `qtype` | Qué pide | Por unidad |
|---|---|---|
| `teoria` | Definir o distinguir conceptos | 3 |
| `codigo` | Interpretar qué hace un fragmento | 3 |
| `prediccion` | Elegir la salida exacta de un programa | 3 |
| `error` | Localizar el fallo y su causa | 2 |
| `solucion` | Elegir el código que cumple un requisito | 2 |
| `diseno` | Razonar qué clase, relación o método conviene | 2 |

Por nivel (`level`): 5 básicas (1), 6 intermedias (2) y 4 avanzadas (3). El validador comprueba los
dos repartos, las 4 opciones sin repetir, la explicación, el porqué de cada distractor y que la opción
correcta de cada pregunta de predicción es la salida real de su código (lo ejecuta al generar).

### Referencias

Solo se puede citar una fuente del catálogo cerrado `SOURCES` (`poo_common.py`): el tutorial de
clases, la FAQ de programación y los módulos `abc` y `dataclasses` de docs.python.org, y los RD
405/2023 y 659/2023. La normativa (`kind: "norma"`) solo sirve para el currículo: el validador
rechaza que respalde un concepto de Python. Toda referencia nace `pending` («Pendiente de
comprobación») y solo pasa a `verified` con quién (`by`) y cuándo (`date`) la comprobó. Desde el
entorno en que se escribió este contenido no se podía abrir docs.python.org, así que los nombres de
los apartados citados están sin comprobar.

Los ejemplos llevan `origin`: `original` (por defecto) o `docs` con la fuente, que debe estar también
en las referencias de la unidad.

## Ejecución de Python

Un solo motor: `PythonRunner` (`python-runner.js`) con Pyodide en un Web Worker con la red cerrada,
tiempo máximo y botón Detener. Los ejemplos de las lecciones se ejecutan con «▶ Ejecutar el
ejemplo»; los ejercicios de código, en la sesión de práctica con «▶ Ejecutar» y «Comprobar con los
tests» (`check_exercise` de `frontend/py/runner.py`, asserts con mensajes en español). El código del
alumno nunca se envía al backend.

## Progreso y motor adaptativo

- Los ejercicios del módulo son ejercicios normales del núcleo: cuentan para el dominio, el repaso
  espaciado, los errores activos y las recomendaciones («Practicar este error» propone ejercicios que
  detectan el mismo error).
- **Lecciones completadas**: `sections: { idLección: fecha }` en el documento `learn` (se sincroniza con
  la cuenta). Solo crece y al fusionar gana la primera fecha. **No cuenta para el dominio**: completar
  una lección no demuestra la competencia.
- **Cuestionarios con nota** (`quizzes: { id: { best, total, last, at, passedAt } }` en el documento
  `learn`, sincronizado): `id` es la unidad o `poo-final`. Se guarda la mejor nota, la del último
  intento y la fecha del primer aprobado, que no se pierde con una nota peor. Al fusionar dos copias gana
  la mejor nota y el primer aprobado. La nota no cuenta para el dominio; las respuestas sí, como
  cualquier intento.
- Las unidades de POO no entran en el simulacro de Preparación DAW ni en la prueba de nivel hasta
  decidirlo en el Sprint 7.

## Cuestionarios y evaluación final

| | Cuestionario de la unidad | Evaluación final |
|---|---|---|
| Dónde | Apartado «Cuestionario de la unidad» | Índice `#/poo` |
| Preguntas | Las 15 del banco de la unidad | 30: de cada unidad, una del banco de cada nivel (1, 2 y 3), al azar |
| Corrección | Al momento, con el porqué de cada opción incorrecta | Al terminar, pregunta a pregunta |
| Nuevos intentos | No: la nota es la del primer intento | No |
| Se supera con | 11 de 15 (70 %) | 21 de 30 (70 %) |
| Sesión | `kind: "quiz"` | `kind: "final"` (sin tiempo; se puede terminar antes y lo no respondido cuenta como fallo) |

`QUIZ_PASS` (`mastery.js`) fija el 70 % para los dos. El cuestionario superado es un criterio más de
«Criterios de superación» de cada unidad, junto a los ejercicios obligatorios y el dominio.

**Repaso.** Al terminar cualquiera de los dos, cada unidad trabajada recibe su fecha de repaso con el
mismo sistema de cajas que el resto (`reviewConcept`). Además, la unidad ofrece «Repasar las N preguntas
falladas»: una práctica con las preguntas del banco cuya última respuesta fue incorrecta. No cambia la
nota guardada.

`buildPooFinal` (`exam.js`) compone la evaluación final; `failedBank` y `needed` (`poo-view.js`), el
repaso y los aciertos necesarios.

## Currículo

Fuente: RD 405/2023 (anexo I), con el texto oficial en `frontend/data/curriculum/daw-cyl.json`.

| Estado | Significado | Cómo se muestra |
|---|---|---|
| `verified` | Una persona la ha validado (`by`) | «Validada» |
| `proposed` | Propuesta de la plataforma | «Propuesta de la plataforma, pendiente de validar» |
| `unassigned` | No hay una correspondencia clara | «Sin correspondencia» |

Todas las correspondencias son `proposed` hasta que alguien las valide. Los CE del concepto (`ce`) son
los de sus correspondencias asignadas. Propuesta para las 10 unidades:

| Unidad | CE propuestos |
|---|---|
| 1 | RA2-a, RA4-a |
| 2 | RA2-h, RA4-b, RA4-d, RA4-e *(ya en el contenido)* |
| 3 | RA2-d, RA2-e, RA2-f, RA4-c, RA4-h |
| 4 | RA4-c, RA4-f |
| 5 | RA4-g, RA7-a, RA7-c, RA7-d, RA7-e |
| 6 | RA7-d, RA7-g, RA7-i |
| 7 | RA7-j |
| 8 | RA6-d *(dudosa)* |
| 9 | RA3-g, RA4-i, RA7-h, RA7-j |
| 10 | RA3-d, RA3-f, RA4-e, RA7-e, RA7-f, RA7-g |

`unassigned`: RA7-b (en Python no hay modificadores que bloqueen la herencia; `typing.final` no lo
impone el intérprete), RA6-f, RA8 y RA9.

Hasta que existan las unidades 1 y 3, los CE RA2-a, RA4-a y RA4-c que tenía `poo` no tienen ningún
concepto asociado (estaban sin revisar y pasan a las unidades que los trabajan).

## Pruebas

| Qué | Dónde |
|---|---|
| Datos, apartados, ejemplos y soluciones ejecutados | `python scripts/learning/build_learning.py --check` |
| Estructura, banco (15 por unidad y repartos), referencias, currículo y validador | `backend/tests/test_poo_module.py` |
| Lecciones completadas, fusión, recomendaciones y vistas | `tests/unit/poo-module.test.mjs` |
| Nota del cuestionario, evaluación final, limpieza y fusión de `quizzes`, repaso de falladas | `tests/unit/poo-evaluation.test.mjs` |
| Índice, unidad, diagrama, rúbrica y retos, Pyodide, mini-quiz, cuestionario con el porqué del fallo, móvil y WCAG 2.2 AA | `e2e/poo.spec.js` |

Tamaño de `learning.json` con las Unidades 1 a 6 completas (PR A): 485 KB sin comprimir y 111 KB
con gzip (antes, 346 KB). El umbral para separar el módulo en otro archivo es 400 KB comprimido.

Con las 10 unidades (PR C): 760 KB sin comprimir y 171 KB con gzip, por debajo del umbral.
