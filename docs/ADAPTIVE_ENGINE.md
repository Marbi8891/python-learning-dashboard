# Motor adaptativo 2.0

Cómo decide PLD qué sabes, qué se te está olvidando y qué estudiar hoy. Todo es **determinista**
(el mismo progreso y la misma fecha dan el mismo resultado), **explicable** (cada cifra se puede
justificar con datos del alumno) y se calcula en el navegador con funciones puras probadas con
`node --test`. La auditoría que motivó estos cambios está en [`AUDITORIA_EVOLUCION_PLD.md`](AUDITORIA_EVOLUCION_PLD.md)
y las decisiones, en [`DECISIONS.md`](DECISIONS.md).

> Los porcentajes son **estimaciones internas** para orientar el estudio. No son calificaciones
> oficiales ni predicen la nota de un examen. No se afirma que el motor mejore el aprendizaje hasta
> tener semanas de uso real con las que comparar.

## Archivos

| Archivo | Qué hace |
|---|---|
| `frontend/js/srs.js` | Repaso espaciado común a conceptos, PCAP y cursos (cajas de Leitner) |
| `frontend/js/learn/mastery.js` | Evidencias, dominio, confianza, retención, errores, limpieza y fusión del progreso |
| `frontend/js/learn/recommend.js` | Prioridad explicable y plan de «Hoy» |
| `frontend/js/learn/planner.js` | Planificador: tiempo, exámenes y entregas, tareas hechas/pospuestas/rechazadas, historial |
| `frontend/js/learn/planner-store.js` | Guarda el planificador (`pld:planner`) y lo sincroniza con la cuenta |
| `frontend/js/pcap-store.js`, `course-store.js` | Preparación del PCAP y de los cursos con cobertura mínima |
| `scripts/learning/concepts.py` (`CURRICULUM_CE`) | Qué criterios de evaluación (CE) trabaja cada concepto |
| `scripts/learning/ids.lock.json` | Ids estables de conceptos, ejercicios y errores |

## 1. Modelo de conocimiento

Cada concepto de `frontend/data/learning.json` (se genera con `scripts/learning/build_learning.py`,
nunca a mano) tiene:

| Campo | Origen |
|---|---|
| `id` | Estable; registrado en `ids.lock.json` |
| `title`, `area`, `ut` (unidad) | `concepts.py` |
| `requires` (prerrequisitos) | `concepts.py`; el script comprueba que no hay ciclos |
| `ce` (criterios de evaluación) | `CURRICULUM_CE`; el script comprueba que existen en `daw-cyl.json` |
| `ra` (resultados de aprendizaje) y `module` | Se derivan de `ce` |
| `difficulty` (1-3) | Nivel medio de sus ejercicios |
| `importance` (1-3) | La importancia para DAW que ya tenía (`daw`) |

La relación con los CE es de la plataforma, para orientar el estudio. No es una programación didáctica oficial.

## 2. Evidencias

Un intento (`recordAttempt`) guarda por ejercicio: los 5 últimos resultados (`h`), el número de
intentos (`n`), la fecha del último intento (`last`) y la del **último acierto** (`okAt`, nuevo).
Se distingue:

| Qué | Dónde | Cuenta para el dominio |
|---|---|---|
| Contenido leído | `concepts[id].read` | No |
| Lección completada (módulo de POO) | `sections[id]` | No |
| Ejercicio intentado | `ex[id]` existe | Sí, con su último resultado |
| Respuesta correcta | `ex[id].h.at(-1) === true`, `okAt` | Sí |
| Nuevo intento tras ver la explicación | solo `log` y errores | No |
| Fallo en la prueba de nivel | solo `log` y errores | No (el concepto sigue «nuevo») |
| Conocimiento demostrado | estado `dominado` | Ver §3 |

`conceptStats().evidence` devuelve la lista de evidencias (ejercicio, tipo, nivel, resultado, intentos,
fechas) para poder enseñar de dónde sale cada cifra.

## 3. Dominio, confianza y retención

```
base       = Σ peso(nivel) de los ejercicios cuyo último intento fue correcto
             ─────────────────────────────────────────────────────────────── pesos: 1 / 1,5 / 2
             Σ peso(nivel) de TODOS los ejercicios del concepto

retención  = 1 hasta la fecha de repaso; después, 0,5 ^ (días de retraso / semivida(caja))
             semivida(caja) = max(14, 3 × intervalo de la caja) días

dominio    = base × retención

confianza  = min(1, ejercicios distintos / min(4, ejercicios del concepto))
           × min(1, tipos distintos / min(2, tipos del concepto))
```

- **Repetir no infla:** cada ejercicio distinto cuenta una vez; repetirlo solo actualiza su resultado.
- **Confianza ≠ dominio:** la confianza solo mira cuántas evidencias hay y de cuántos tipos, no si se acertaron.
- **Pocas evidencias:** con confianza < 0,5 el estado es `insuficiente` («Pocas evidencias») y la
  interfaz **no muestra porcentaje**.
- **Estados:** `nuevo` · `leido` · `insuficiente` · `aprendiendo` (< 50 %) · `progreso` · `dominado`
  (≥ 80 %, con algún ejercicio de aplicación acertado, sin errores activos y con evidencias suficientes).
- **Olvido:** `forgotten` = la base era ≥ 50 % y la retención ha bajado de 0,7. La vista lo marca
  como «Se está olvidando».
- `explainStats()` resume el dominio en una frase.

## 4. Repaso espaciado (`srs.js`)

Cajas 0-5 con intervalos de 0, 1, 3, 7, 14 y 30 días, iguales para conceptos, preguntas del PCAP y de los cursos.

- **Bien** (≥ 80 % en una sesión, o acierto en una pregunta): sube de caja **solo si el repaso había
  vencido** o el elemento es nuevo. Así, cinco sesiones seguidas en una tarde no mandan el repaso a
  un mes (AUD-004).
- **Regular** (50-80 %): mantiene la caja (al menos la 1).
- **Mal** (< 50 %, o fallo): vuelve a la caja 1, con repaso mañana.
- Un intento fuera de una sesión terminada programa el repaso para mañana si no había ninguno (AUD-003).
- El repaso manual es cualquier práctica del concepto: no adelanta la caja.

## 5. Prioridad y plan de «Hoy» (`recommend.js`)

```
P = 0,25 R + 0,25 E + 0,20 D + 0,15 W + 0,15 T          (todos los factores entre 0 y 1)
R  necesidad de repaso   (días de retraso + 1) / intervalo de la caja, o 1 − retención si se olvida
E  errores recientes     errores activos del concepto / 2
D  déficit de dominio    1 − dominio (1 si no se ha empezado)
W  importancia           importancia / 3
T  proximidad de examen  1 − días hasta el examen o entrega de su módulo / 60
```

Reglas que la fórmula no puede saltarse:

1. Los repasos vencidos van primero (como mucho dos).
2. El contenido nuevo solo aparece si sus prerrequisitos están firmes (dominio ≥ 60 % o superados en
   la prueba de nivel). Si no, se propone reforzarlos: «Necesitas reforzar X antes de pasar a Y».
3. Lo hecho, pospuesto o rechazado hoy no se vuelve a proponer. Lo pospuesto ayer lo dice en el motivo.

Cada acción lleva `reason` (el motivo principal), `priority` (P) y `why` (los factores en palabras:
«repaso vencido hace 3 días · 1 error activo · dominio del 40 % · imprescindible para DAW · examen
«UT3» en 10 días»). El plan se ajusta al tiempo disponible con `fitPlanToBudget`, sin saltarse la prioridad.

Los pesos son una **hipótesis inicial**. Las pruebas comprueban propiedades (factores normalizados,
pesos que suman 1, un examen cercano sube la prioridad, uno lejano o de otro módulo no, un repaso
vencido gana siempre), no valores concretos, para poder ajustar los pesos con datos reales.

## 6. Planificador diario (`planner.js`)

Documento propio, `pld:planner` en el navegador y `/api/course-state/planner` en la cuenta:

```json
{ "v": 1, "minutes": 45, "minutesAt": "ISO",
  "exams": [{ "id": "…", "title": "Examen UT3", "module": "0485", "date": "2026-12-15", "kind": "examen", "at": "ISO" }],
  "days": { "2026-11-04": { "variables": { "status": "hecha", "at": "ISO" } } } }
```

- Desde «Aprender»: elegir el tiempo (15-90 min), marcar cada tarea como hecha, posponerla a mañana o
  descartarla hoy, deshacer, añadir y quitar exámenes y entregas, y ver el historial de la semana con
  el porcentaje de recomendaciones hechas.
- El tiempo que antes solo vivía en `pld:daily-study-minutes` se lleva al planificador la primera vez.
- Se guardan los últimos 30 días.
- **Fusión entre dispositivos:** gana lo cambiado más tarde (tiempo, cada tarea y cada examen). Los
  exámenes borrados y las tareas deshechas se quedan marcados con su fecha para que otro dispositivo
  no los resucite.

## 7. Preparación del PCAP y de los cursos

`readiness()` pondera el acierto de cada bloque por su peso en el examen **y por la cobertura del
bloque** (cuenta entero a partir de la mitad de sus preguntas respondidas). Con menos del 20 % del
banco respondido no se muestra porcentaje («Sin datos»). Antes, una respuesta acertada por bloque
daba el 100 % (AUD-006).

## 8. Compatibilidad y sincronización

- `cleanLearning` y `cleanPlanner` **conservan los campos que no conocen** (F1.0), así una versión
  futura no pierde datos al pasar por una pestaña con la versión actual.
- Las pestañas abiertas con la versión **anterior** a F1.0 sí descartan `okAt`. No se pierde nada
  importante: `okAt` se deduce del historial cuando falta.
- La fusión de `ex` conserva el `okAt` más reciente de las dos copias (F1.6).
- No ha cambiado ningún id ni el formato de los documentos (`v: 1`).

## 9. Pruebas

| Qué | Dónde |
|---|---|
| Repaso espaciado | `tests/unit/srs.test.mjs` |
| Dominio 2.0, retención, confianza, evidencias, fusión | `tests/unit/mastery.test.mjs` |
| Prioridad y plan | `tests/unit/recommend.test.mjs` |
| Planificador | `tests/unit/planner.test.mjs` |
| Prueba de nivel | `tests/unit/exam.test.mjs`, `tests/unit/session.test.mjs` |
| Ids estables y modelo de conocimiento | `backend/tests/test_learning_ids.py` |
| Documento `planner` en la API | `backend/tests/test_course_state.py` |
| Planificador en la web | `e2e/learn.spec.js` («planificador: …») |
| Módulo de POO (lecciones, fusión, recomendaciones) | `tests/unit/poo-module.test.mjs`, `backend/tests/test_poo_module.py`, `e2e/poo.spec.js` |

## 10. Métricas para validar con uso real

Repasos hechos a tiempo, recomendaciones aceptadas (`acceptanceRate`), errores que pasan a
corregidos y evolución de los simulacros (`exams`). Hasta tener semanas de datos, los pesos se
consideran provisionales.
