# Módulo de Programación orientada a objetos (POO)

Módulo de 10 unidades para aprender POO con Python desde cero hasta una aplicación completa, dentro
del núcleo por conceptos (Teoría, Practicar y motor adaptativo). Pertenece al módulo 0485 Programación
de DAW. Se construye por sprints; este documento dice qué hay en cada uno y cómo está hecho.

## Estado

| Sprint | Contenido | Estado |
|---|---|---|
| 1 | Estructura, validadores, vista de unidad, índice `#/poo`, Unidad 2 en el formato nuevo | Hecho |
| 2 | Unidades 1 a 3 (la 2 pasa a pedir la 1) | Hecho |
| 3 | Unidades 4 a 6 | Pendiente |
| 4 | Unidades 7 a 9 | Pendiente |
| 5 | Proyecto final: biblioteca | Pendiente |
| 6 | Banco de ≥ 100 preguntas, evaluación por unidad y final, repaso espaciado | Pendiente |
| 7 | Motor adaptativo, progreso y currículo | Pendiente |
| 8 | Pruebas, accesibilidad y documentación | Pendiente |

## Dónde está cada cosa

| Qué | Archivo |
|---|---|
| Índice de unidades, Unidad 2 y reunión de todas las unidades | `scripts/learning/poo_module.py` |
| Una unidad completa por archivo (concepto, campos, ejercicios y errores) | `scripts/learning/poo_u1.py`, `poo_u3.py`, … |
| Correspondencias propuestas (`proposed`), fuente y fecha | `scripts/learning/poo_common.py` |
| Integración en el mapa de conceptos (área `poo`) | `scripts/learning/concepts.py` |
| Validación y generación | `scripts/learning/build_learning.py` (`check_units`) |
| Datos que usa la web (generados, no se editan a mano) | `frontend/data/learning.json` (`modules` y conceptos del área `poo`) |
| Índice del módulo y página de unidad | `frontend/js/learn/poo-view.js` (rutas en `learn-app.js`) |
| Lecciones completadas | `frontend/js/learn/mastery.js` (`markSection`, `sectionsDone`) |

## Unidades

Cada unidad es **un concepto** del núcleo. El id `poo` es la **Unidad 2** y no cambia: `#/teoria/poo`
sigue funcionando y nadie pierde su progreso. Las unidades que aún no existen salen en el índice como
«En preparación».

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

Publicadas: Unidades 1, 2 y 3 (Sprint 2). En la ruta «Aprender» van seguidas y encadenadas por
prerrequisitos: `poo-fundamentos` (pide funciones y diccionarios) → `poo` → `poo-atributos-metodos`.

| Unidad | Lecciones | Ejercicios | Errores típicos nuevos | CE propuestos |
|---|---|---|---|---|
| 1 | Procedural frente a objetos · Clases, objetos y modelado · Cuándo usar la POO y sus pilares | 13 (`poo1-01`…`13`) | clase-instancia, poo-siempre, atributo-metodo | RA2-a, RA2-c, RA4-a |
| 2 | Definir una clase · `__init__` y `self` · Estado de varios objetos | 14 (`poo-01`…`14`) | init-mal-escrito, alias-copia | RA2-h, RA4-b, RA4-d, RA4-e |
| 3 | Atributos de instancia y de clase · Métodos de instancia, de clase y estáticos · Métodos que protegen el estado | 14 (`poo3-01`…`14`) | self-en-atributo-clase, static-con-self, tipo-metodo, lista-de-clase | RA2-d, RA2-e, RA2-f, RA4-c, RA4-h |

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
| `guided`, `autonomous` | Ejercicios guiados y autónomos (de escribir código, con tests) |
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
- Las unidades de POO no entran en el simulacro de Preparación DAW ni en la prueba de nivel hasta
  decidirlo en el Sprint 7.

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
| Estructura, banco, currículo y validador | `backend/tests/test_poo_module.py` |
| Lecciones completadas, fusión, recomendaciones y vistas | `tests/unit/poo-module.test.mjs` |
| Índice, unidad, Pyodide, mini-quiz, móvil y WCAG 2.2 AA | `e2e/poo.spec.js` |
