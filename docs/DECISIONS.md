# Decisiones de arquitectura

Registro breve de las decisiones que condicionan la evolución de PLD. Cada una dice qué se decidió,
por qué y qué consecuencias tiene. Las decisiones anteriores a este registro están explicadas en la
memoria del proyecto (`docs/memoria/memoria.md`).

## DEC-001 · Plataforma personal, sin SaaS (04/11/2026)

**Decisión:** el objetivo actual es una plataforma personal de estudio para DAM/DAW y PCAP. No se
desarrollan profesores, aulas, pagos ni multi-tenancy.
**Por qué:** lo pidió el autor en el plan de evolución adaptativa.
**Consecuencia:** el PR #84 (estrategia de negocio) no se fusiona tal cual. De él se conservan aquí
DEC-002 y DEC-003, que coinciden con este plan.

## DEC-002 · Sincronización sin conflictos (recogida del PR #84, ADR-005)

**Decisión:** cada documento de progreso se fusiona con la copia de la cuenta antes de subir nada,
lleva la versión leída (409 → releer, fusionar, reintentar) y nunca borra datos de la otra copia.
**Por qué:** pérdidas de progreso reales (AUD-001, SYNC-01).
**Consecuencia:** todo almacén nuevo usa `sync-gate.js`, `doc-sync.js` y `uploader.js`, como `planner-store.js`.

## DEC-003 · Recomendaciones transparentes primero (recogida del PR #84, ADR-006)

**Decisión:** el motor usa reglas y fórmulas explicables y deterministas, no modelos opacos.
**Por qué:** el alumno tiene que poder entender por qué se le recomienda algo.
**Consecuencia:** cada acción del plan lleva su motivo y sus factores (`why`).

## DEC-004 · Alcance de la Fase 1 (D1 de la auditoría, 04/11/2026)

**Decisión:** el motor 2.0 trabaja sobre los 22 conceptos del núcleo (Programación en Python). El
repaso espaciado se unifica para el PCAP y los cursos. Los cursos de DAW entrarán en el grafo de
conceptos en una fase aparte.
**Por qué:** dar conceptos, prerrequisitos y errores típicos a 520 preguntas es trabajo de contenido, no de motor.

## DEC-005 · Documento `planner` separado (D2 de la auditoría, 04/11/2026)

**Decisión:** el planificador se guarda en un documento propio (`/api/course-state/planner`) en lugar
de dentro de `learn`.
**Por qué:** las pestañas abiertas con una versión anterior no lo conocen y no pueden pisarlo.

## DEC-006 · El dominio puede bajar (D3 de la auditoría, 04/11/2026)

**Decisión:** con evidencias, confianza y retención, algunos conceptos que antes salían como
«dominado» pasan a «en progreso», «Pocas evidencias» o «Se está olvidando».
**Por qué:** el estado anterior confundía actividad con dominio y no tenía en cuenta el olvido.

## DEC-007 · Compatibilidad hacia delante de los documentos (F1.0)

**Decisión:** las funciones de limpieza conservan los campos y bloques que no conocen. Los ids de
conceptos, ejercicios, errores, preguntas y lecciones solo pueden crecer (`ids.lock.json`).
**Por qué:** una versión antigua de la web no debe borrar datos de una nueva al sincronizar (EVO-10).

## DEC-008 · Repaso espaciado sin compresión (F1.1)

**Decisión:** una caja solo sube cuando el repaso ha vencido.
**Por qué:** antes, cinco sesiones en una tarde llevaban el repaso a 30 días (AUD-004). Cambia el
comportamiento que fijaba el test anterior: lo aprobó el autor al aprobar la auditoría.

## DEC-009 · Pesos de la prioridad provisionales (F1.7)

**Decisión:** P = 0,25 R + 0,25 E + 0,20 D + 0,15 W + 0,15 T, como hipótesis inicial.
**Por qué:** no hay datos de uso real para ajustarlos. Las pruebas fijan propiedades, no valores.
**Consecuencia:** revisar los pesos cuando haya semanas de uso (porcentaje de recomendaciones hechas en el planificador).

## DEC-010 · Sin dependencias nuevas en la Fase 1

**Decisión:** todo el motor se escribe en JavaScript sin bibliotecas nuevas. El backend solo gana un id de documento.
**Por qué:** coste de mantenimiento y arquitectura actual (HTML, CSS, ES modules, FastAPI).

## DEC-016 · El módulo de POO vive en el núcleo por conceptos

(DEC-011 a DEC-015 están reservadas por el Career Roadmap, PR #101.)

**Decisión:** las 10 unidades de POO son conceptos del área `poo` de `learning.json`, con campos de unidad opcionales; no un curso de DAW aparte. El id `poo` pasa a ser la Unidad 2.
**Por qué:** reutiliza el runner de Pyodide, los errores típicos, el repaso espaciado y las recomendaciones sin crear otro motor; los cursos de DAW no corrigen código en la web. Lo eligió el autor el 11/11/2026.
**Consecuencia:** `#/teoria/poo` y el progreso existente se conservan; las unidades de POO quedan fuera del simulacro DAW y de la prueba de nivel hasta el Sprint 7 (`docs/MODULO_POO.md`).

## DEC-017 · Correspondencias curriculares con estado

**Decisión:** cada relación unidad → CE lleva `status` (`verified`, `proposed`, `unassigned`), `source` y `reviewed`. Todas nacen `proposed`; solo una persona puede marcarlas `verified` (`by`).
**Por qué:** no se pueden presentar como oficiales relaciones que nadie ha validado (auditoría del piloto DAW).
**Consecuencia:** la web enseña «pendiente de validar» junto a cada CE propuesto; el validador rechaza un `verified` sin autor.

## DEC-018 · Catálogo de cursos por familias (Excel profesional, P0)

**Decisión:** los cursos con documento de progreso se registran en `frontend/js/catalog.js` en dos familias: `daw` (`DAW_COURSES`, sin cambios) y `academia` (`ACADEMY_COURSES`, hoy solo `excel`). La sincronización recorre `SYNCED_COURSES` (las dos); las vistas, el panel por módulo, la portada y los certificados de DAW siguen usando solo `DAW_COURSES`.
**Por qué:** Excel profesional no es un módulo del ciclo y no debe contarse ni certificarse como DAW, pero tiene que reutilizar el progreso, la sincronización con versión y 409, la exportación y el borrado de la cuenta sin duplicarlos. Lo aprobó el autor el 16/11/2026, junto con el nombre visible «Excel profesional» y la ruta `#/academia/excel`.
**Consecuencia:** el backend solo gana el id `excel` en `COURSES` (sin tablas ni migraciones). Una prueba comprueba que el catálogo y `COURSES` coinciden y otra que `DAW_COURSES` es idéntico al anterior. El curso está registrado (`status: "planned"`) pero no tiene contenido ni ruta visibles hasta P1.

## DEC-019 · Motor de fórmulas propio para Excel profesional (P1)

**Decisión:** los ejercicios de Excel se corrigen con un motor de fórmulas propio, en `frontend/js/excel/formula/` (analizador léxico por estados, parser de descenso recursivo, AST inmutable y evaluador con presupuesto de pasos), sin `eval` ni `Function` y sin dependencias. La v1 calcula 8 funciones (SUMA, PROMEDIO, MIN, MAX, CONTAR, CONTARA, PRODUCTO, REDONDEAR), operadores, referencias relativas, absolutas y mixtas, otras hojas y la copia de fórmulas; las otras 37 de la especificación están registradas como previstas y dan #¿NOMBRE? con el aviso «todavía no está disponible en PLD». Los ejercicios se comprueban por lo que hacen (valor, copia, otros datos, referencias, números escritos a mano), nunca comparando el texto de la fórmula.
**Por qué:** ninguna biblioteca gratuita calcula y encaja a la vez (SheetJS CE y ExcelJS no calculan; Formula.js no tiene BUSCARX ni FILTRAR; HyperFormula es GPL), y el mismo código tiene que corregir en el navegador y comprobar las respuestas al generar el curso. Lo autorizó el autor el 17/11/2026 (P1).
**Consecuencia:** el generador (`course_builder.py`) acepta cursos sin módulo oficial y los tipos `formula` y `formula-result`, y los comprueba con el motor en Node (`scripts/courses/excel/eval.mjs`). La corrección es formativa: las soluciones están en el JSON público. Detalle en [`docs/excel-academy/FORMULA_ENGINE_SPEC.md`](excel-academy/FORMULA_ENGINE_SPEC.md).

## DEC-020 · Excel profesional con vista y carpeta de datos propias (P2)

**Decisión:** el curso se ve en `#/academia/excel` (alias `#/excel-academy`) con su propio módulo, `frontend/js/excel/course.js`, que se carga solo en esas rutas, y sus JSON van en `frontend/data/academia/excel/`, generados por `scripts/courses/excel_course.py`. Reutiliza el generador, el documento de progreso de la cuenta (`course-store.js`, `lesson-progress.js` y el repaso de `srs.js`), el Markdown seguro, la página 404 y los estilos de DAW. La unidad se da por «superada» con el 80 % del test (último intento) y sus fórmulas obligatorias resueltas (`excel/progress.js`); «completada» sigue siendo el botón.
**Por qué:** `daw.js` y `frontend/data/courses/` están atados a DAW (migas, currículo oficial, `DAW_COURSES`, pruebas, recursos y registro de ids que recorren esa carpeta). Ampliarlos era el riesgo R-05 de la especificación; así, DAW no cambia ni un byte y el motor no se descarga fuera de Excel. Lo autorizó el autor el 17/11/2026 (P2), con el curso visible al fusionar; la especificación consolidada prevalece sobre la propuesta «Excel Academy» de ese día (sin XP, sin tutor, sin tablas nuevas). Detalle en `docs/excel-academy/MASTER_SPECIFICATION.md` §6 (DA-22 a DA-27, DT-05 y DT-06).
**Consecuencia:** los ids de Excel tienen su propio registro estable (`scripts/courses/academia.lock.json`, comprobado por `backend/tests/test_excel_course.py` y `lock_ids.py --check` en CI). Un curso nuevo de la academia seguiría el mismo camino.

## DEC-021 · Funciones `lazy` en el motor de Excel (P4.1)

**Decisión:** las funciones que no pueden recibir sus argumentos ya calculados llevan la marca `lazy` en el registro (`frontend/js/excel/formula/functions/registry.js`) y reciben un objeto `lazyArgs` del evaluador: SI, SI.CONJUNTO y SI.ERROR (solo calculan la rama que toca) y la familia SUMAR.SI (necesita la posición de cada rango). Los criterios se comparan con un algoritmo propio de comodines, sin expresiones regulares.
**Por qué:** con los argumentos ya calculados, `=SI(B2=0;0;A2/B2)` daría #¡DIV/0! y SUMAR.SI no podría ajustar el rango de suma como Excel. Una marca en el registro deja igual las 8 funciones de la v1 y su prueba de referencia. Sin expresiones regulares no hay riesgo de vuelta atrás exponencial con un patrón como `*A*A*A…`. El autor pidió el 17/11/2026 seguir con las lecciones (DA-28: P4.1, M03-M05, antes de P3).
**Consecuencia:** el motor ocupa 61 387 bytes de los 61 440 del presupuesto (RNF-10). Antes de M06 hay que decidir si cada módulo carga sus funciones aparte o si se amplía el límite con una medida de rendimiento (DP-17).

