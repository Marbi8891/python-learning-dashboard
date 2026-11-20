> **Ejemplo ficticio.** Generado con `scripts/audit/auditor.py` a partir de los informes inventados de
> `scripts/audit/fixtures/` y de pruebas simuladas. No describe el código real del proyecto.

# Auditoría del proyecto · 20261120T1000Z

Commit `?` en `?` · profundidad `standard` · modo `read-only` · fuentes: ejemplo-1-revision, ejemplo-1-red-team.

## Executive Summary

Estado: **con riesgos relevantes** (63/100). Hay 4 hallazgo(s) abiertos: 0 CRITICAL, 2 HIGH, 1 MEDIUM, 1 LOW, 0 INFO. En esta auditoría: 4 nuevo(s), 0 resuelto(s) y 0 regresión(es). De las pruebas, 1 pasan, 1 fallan y 1 no se han ejecutado. Categorías revisadas por los agentes: security, bugs, architecture, performance, code-quality, testing, ux-accessibility, dependencies, docs, config-deploy, integration, content.

## Project Health Score

**63/100** — evaluación heurística del auditor, no una métrica objetiva. Se parte de 100 y se resta por cada hallazgo abierto según su severidad, por cada prueba que falla y por cada prueba sin ejecutar (lo no comprobado resta porque es incertidumbre). Pesos en `project-auditor.toml` → `[score]`.

- 2 × HIGH abierto: −20
- 1 × MEDIUM abierto: −4
- 1 × LOW abierto: −1
- 1 prueba(s) que fallan: −10
- 1 prueba(s) sin ejecutar (incertidumbre): −2

## Comparación con la auditoría anterior

Primera auditoría registrada: no hay con qué comparar.

## Critical Findings

Ningún hallazgo CRITICAL abierto.

## Security Findings

#### AUD-003 · Falta límite de intentos en el endpoint de ejemplo · **nuevo**

- **Severidad / prioridad:** HIGH / P1 · **Tipo:** Sospecha
- **Dónde:** `backend/app/routers/ejemplo.py` línea 10
- **Categoría:** security · **Fuente:** ejemplo-1-red-team · ref. RT-900
- **Descripción:** POST /api/v1/ejemplo no aplica rate_limit.
- **Evidencia:**

```text
ejemplo.py:10 @router.post sin Depends(rate_limit)
```

- **Impacto:** Fuerza bruta contra la cuenta. · **Probabilidad:** medium
- **Solución recomendada:** Añadir la dependencia de límite de intentos existente.
- **Esfuerzo:** S · **Riesgo de la solución:** low · **Modo:** APPROVAL REQUIRED (severidad HIGH > MEDIUM; categoría «security»; archivo protegido: backend/app/routers/ejemplo.py)
- **Test de regresión:** Test que hace N+1 intentos y espera 429.

## Functional Bugs

#### AUD-001 · El temporizador del simulacro no se detiene al salir de la vista · **nuevo**

- **Severidad / prioridad:** MEDIUM / P2 · **Tipo:** Hecho
- **Dónde:** `frontend/js/ejemplo/simulacro.js` línea 42 (`startTimer`)
- **Categoría:** bugs · **Fuente:** ejemplo-1-revision
- **Descripción:** setInterval se crea al entrar y no se limpia al cambiar de vista.
- **Evidencia:**

```text
simulacro.js:42 setInterval(tick, 1000) sin clearInterval en unmount
```

- **Impacto:** El contador sigue corriendo y descuenta tiempo de otro intento. · **Probabilidad:** medium
- **Solución recomendada:** Guardar el id y llamar a clearInterval al salir.
- **Esfuerzo:** S · **Riesgo de la solución:** low · **Modo:** SAFE FIX
- **Test de regresión:** Unitario: salir de la vista y comprobar que no hay timers activos.

## Architecture Review

Sin hallazgos abiertos.

## Performance Review

Sin hallazgos abiertos.

## Code Quality

#### AUD-002 · Función de render de 180 líneas · **nuevo**

- **Severidad / prioridad:** LOW / P3 · **Tipo:** Recomendación
- **Dónde:** `frontend/js/ejemplo/panel.js` (`renderPanel`)
- **Categoría:** code-quality · **Fuente:** ejemplo-1-revision
- **Descripción:** Mezcla cálculo de datos y construcción del DOM.
- **Evidencia:**

```text
(recomendación sin evidencia de fallo)
```

- **Impacto:** Difícil de probar y de cambiar. · **Probabilidad:** low
- **Solución recomendada:** Extraer el cálculo a una función pura con su test.
- **Esfuerzo:** M · **Riesgo de la solución:** low · **Modo:** SAFE FIX
- **Test de regresión:** Unitario de la función extraída.

## Testing Review

#### AUD-004 · Falla la prueba «Tests unitarios del frontend» · **nuevo**

- **Severidad / prioridad:** HIGH / P1 · **Tipo:** Hecho
- **Dónde:** `project-auditor.toml` (`frontend-unit`)
- **Categoría:** testing · **Fuente:** checks
- **Descripción:** `/usr/local/bin/python3 -c import sys; print('# fail 1'); sys.exit(1)` terminó en failed (1).
- **Evidencia:**

```text
# fail 1
```

- **Impacto:** Una prueba del proyecto no pasa: el cambio no está terminado (CLAUDE.md). · **Probabilidad:** high
- **Solución recomendada:** Leer la salida, reproducirla en local y corregir la causa sin tocar la prueba.
- **Esfuerzo:** M · **Riesgo de la solución:** medium · **Modo:** APPROVAL REQUIRED (severidad HIGH > MEDIUM; riesgo de la solución «medium»; una prueba que falla se investiga antes de corregir)
- **Test de regresión:** La propia prueba `frontend-unit`.

### Pruebas ejecutadas

| Prueba | Resultado | Tiempo | Detalle |
|---|---|---|---|
| Tests del backend (pytest) (`backend-tests`) | ✅ pasa | 0.02 s |  |
| Tests unitarios del frontend (`frontend-unit`) | ❌ falla | 0.02 s | código 1 |
| End-to-end y WCAG (Playwright) (`e2e`) | ⚪ no ejecutada | 0.0 s | necesita profundidad «deep»; esta ejecución: «standard» |

**Total:** 1 pasan, 1 fallan, 0 agotan el tiempo y 1 no se han ejecutado. Una prueba no ejecutada no cuenta como aprobada.

## UX and Accessibility

Sin hallazgos abiertos.

## Dependencies

Sin hallazgos abiertos.

## Technical Debt

2 hallazgo(s) de deuda abiertos (arquitectura, calidad, documentación, pruebas y dependencias). Esfuerzo: 0 S, 2 M, 0 L.

## Recommended Actions

| # | Id | Acción | Prioridad | Severidad | Esfuerzo | Modo |
|---|---|---|---|---|---|---|
| 1 | AUD-003 | Añadir la dependencia de límite de intentos existente. | P1 | HIGH | S | APPROVAL REQUIRED |
| 2 | AUD-004 | Leer la salida, reproducirla en local y corregir la causa sin tocar la prueba. | P1 | HIGH | M | APPROVAL REQUIRED |
| 3 | AUD-001 | Guardar el id y llamar a clearInterval al salir. | P2 | MEDIUM | S | SAFE FIX |
| 4 | AUD-002 | Extraer el cálculo a una función pura con su test. | P3 | LOW | M | SAFE FIX |

## Positive Findings

- La lógica del repaso espaciado está aislada en funciones puras con tests.
- Pruebas que pasan: Tests del backend (pytest).

## Límites de esta auditoría

- 1 hallazgo(s) rechazados por no cumplir el esquema:
  - ejemplo-1-red-team: «Hallazgo sin evidencia (se rechaza)»: un hecho o una sospecha necesita evidencia
- No ejecutadas: `e2e` (necesita profundidad «deep»; esta ejecución: «standard»).
- Los hallazgos de los agentes son revisión asistida por IA: los marcados como Sospecha necesitan confirmación antes de actuar.
