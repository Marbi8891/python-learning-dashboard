> **Ejemplo ficticio.** Generado con `scripts/audit/auditor.py` a partir de los informes inventados de
> `scripts/audit/fixtures/` y de pruebas simuladas. No describe el código real del proyecto.

# Auditoría del proyecto · 20261127T1000Z

Commit `?` en `?` · profundidad `standard` · modo `read-only` · fuentes: ejemplo-2-revision.

## Executive Summary

Estado: **bueno, con puntos que atender** (86/100). Hay 3 hallazgo(s) abiertos: 0 CRITICAL, 1 HIGH, 0 MEDIUM, 2 LOW, 0 INFO. En esta auditoría: 1 nuevo(s), 2 resuelto(s) y 0 regresión(es). De las pruebas, 2 pasan, 0 fallan y 1 no se han ejecutado. Categorías revisadas por los agentes: bugs, code-quality, ux-accessibility, security.

## Project Health Score

**86/100** — evaluación heurística del auditor, no una métrica objetiva. Se parte de 100 y se resta por cada hallazgo abierto según su severidad, por cada prueba que falla y por cada prueba sin ejecutar (lo no comprobado resta porque es incertidumbre). Pesos en `project-auditor.toml` → `[score]`.

- 1 × HIGH abierto: −10
- 2 × LOW abierto: −2
- 1 prueba(s) sin ejecutar (incertidumbre): −2

## Comparación con la auditoría anterior

Comparado con 20261120T1000Z (commit `?`):

- **Puntuación:** 63 → 86 (+23)
- **Nuevos:** 1 · **Resueltos:** 2 · **Regresiones:** 0 · **Cambiados:** 1 · **Siguen igual:** 0
- **Deuda técnica abierta:** 2 → 1
- **Abiertos por severidad:** CRITICAL 0 → 0, HIGH 2 → 1, MEDIUM 1 → 0, LOW 1 → 2, INFO 0 → 0

Resueltos en esta auditoría:

- AUD-003 · Falta límite de intentos en el endpoint de ejemplo — ejemplo.py:10 ahora usa Depends(rate_limit); test_ejemplo_429 pasa (ejemplo-2-revision)
- AUD-004 · Falla la prueba «Tests unitarios del frontend» — la prueba «frontend-unit» ha pasado en 20261127T1000Z

No re-detectados (siguen abiertos: sin evidencia no se dan por resueltos):

- AUD-002 · Función de render de 180 líneas (1 auditoría(s) sin verlo)

## Critical Findings

Ningún hallazgo CRITICAL abierto.

## Security Findings

Sin hallazgos abiertos.

## Functional Bugs

#### AUD-001 · El temporizador del simulacro no se detiene al salir · **cambiado**

- **Severidad / prioridad:** HIGH / P1 · **Tipo:** Hecho
- **Antes:** MEDIUM / P2
- **Dónde:** `frontend/js/ejemplo/simulacro.js` línea 44 (`startTimer`)
- **Categoría:** bugs · **Fuente:** ejemplo-2-revision
- **Descripción:** Ahora además se duplica al volver a entrar.
- **Evidencia:**

```text
simulacro.js:44 dos setInterval activos tras volver a entrar
```

- **Impacto:** El tiempo baja al doble de velocidad. · **Probabilidad:** high
- **Solución recomendada:** Guardar el id y llamar a clearInterval al salir.
- **Esfuerzo:** S · **Riesgo de la solución:** low · **Modo:** APPROVAL REQUIRED (severidad HIGH > MEDIUM)
- **Test de regresión:** Unitario: entrar dos veces, un único timer.

## Architecture Review

Sin hallazgos abiertos.

## Performance Review

Sin hallazgos abiertos.

## Code Quality

Siguen abiertos sin cambios (detalle en informes anteriores):

| Id | Hallazgo | Severidad | Prioridad | Desde |
|---|---|---|---|---|
| AUD-002 | Función de render de 180 líneas | LOW | P3 | 20261120T1000Z |

## Testing Review

Sin hallazgos abiertos.

### Pruebas ejecutadas

| Prueba | Resultado | Tiempo | Detalle |
|---|---|---|---|
| Tests del backend (pytest) (`backend-tests`) | ✅ pasa | 0.02 s |  |
| Tests unitarios del frontend (`frontend-unit`) | ✅ pasa | 0.02 s |  |
| End-to-end y WCAG (Playwright) (`e2e`) | ⚪ no ejecutada | 0.0 s | necesita profundidad «deep»; esta ejecución: «standard» |

**Total:** 2 pasan, 0 fallan, 0 agotan el tiempo y 1 no se han ejecutado. Una prueba no ejecutada no cuenta como aprobada.

## UX and Accessibility

#### AUD-005 · Imagen de portada sin texto alternativo · **nuevo**

- **Severidad / prioridad:** LOW / P2 · **Tipo:** Hecho
- **Dónde:** `frontend/ejemplo.html` línea 12
- **Categoría:** ux-accessibility · **Fuente:** ejemplo-2-revision
- **Descripción:** &lt;img&gt; decorativa sin alt.
- **Evidencia:**

```text
ejemplo.html:12 <img src=portada.webp>
```

- **Impacto:** Un lector de pantalla lee el nombre del archivo. · **Probabilidad:** high
- **Solución recomendada:** Añadir alt="" por ser decorativa.
- **Esfuerzo:** S · **Riesgo de la solución:** low · **Modo:** SAFE FIX
- **Test de regresión:** La e2e de axe (regla image-alt).

## Dependencies

Sin hallazgos abiertos.

## Technical Debt

1 hallazgo(s) de deuda abiertos (arquitectura, calidad, documentación, pruebas y dependencias). Esfuerzo: 0 S, 1 M, 0 L.

## Recommended Actions

| # | Id | Acción | Prioridad | Severidad | Esfuerzo | Modo |
|---|---|---|---|---|---|---|
| 1 | AUD-001 | Guardar el id y llamar a clearInterval al salir. | P1 | HIGH | S | APPROVAL REQUIRED |
| 2 | AUD-005 | Añadir alt="" por ser decorativa. | P2 | LOW | S | SAFE FIX |
| 3 | AUD-002 | Extraer el cálculo a una función pura con su test. | P3 | LOW | M | SAFE FIX |

## Positive Findings

- Pruebas que pasan: Tests del backend (pytest), Tests unitarios del frontend.

## Límites de esta auditoría

- No ejecutadas: `e2e` (necesita profundidad «deep»; esta ejecución: «standard»).
- Los hallazgos de los agentes son revisión asistida por IA: los marcados como Sospecha necesitan confirmación antes de actuar.
