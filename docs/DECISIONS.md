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
