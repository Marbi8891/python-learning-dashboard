> **Ejemplo ficticio.** Generado con `scripts/audit/auditor.py` a partir de los informes inventados de
> `scripts/audit/fixtures/` y de pruebas simuladas. No describe el código real del proyecto.

# Plan de corrección

3 hallazgo(s) abiertos con prioridad hasta P3, ordenados por prioridad y severidad. Este plan no cambia ningún archivo.

## P1

### AUD-001 · El temporizador del simulacro no se detiene al salir

- **Severidad:** HIGH · **Esfuerzo:** S · **Riesgo de la solución:** low
- **Modo:** APPROVAL REQUIRED — severidad HIGH > MEDIUM. Necesita aprobación explícita antes de tocar nada.
- **Archivos que se modificarían:** `frontend/js/ejemplo/simulacro.js`
- **Qué hacer:** Guardar el id y llamar a clearInterval al salir.
- **Test de regresión:** Unitario: entrar dos veces, un único timer.
- **Verificar con:** `auditor.py checks --only backend-tests,frontend-unit`

## P2

### AUD-005 · Imagen de portada sin texto alternativo

- **Severidad:** LOW · **Esfuerzo:** S · **Riesgo de la solución:** low
- **Modo:** SAFE FIX. Se puede corregir en una rama propia con `auditor.py preflight-fix` y pruebas antes y después.
- **Archivos que se modificarían:** `frontend/ejemplo.html`
- **Qué hacer:** Añadir alt="" por ser decorativa.
- **Test de regresión:** La e2e de axe (regla image-alt).
- **Verificar con:** `auditor.py checks --only e2e`

## P3

### AUD-002 · Función de render de 180 líneas

- **Severidad:** LOW · **Esfuerzo:** M · **Riesgo de la solución:** low
- **Modo:** SAFE FIX. Se puede corregir en una rama propia con `auditor.py preflight-fix` y pruebas antes y después.
- **Archivos que se modificarían:** `frontend/js/ejemplo/panel.js`
- **Qué hacer:** Extraer el cálculo a una función pura con su test.
- **Test de regresión:** Unitario de la función extraída.
- **Verificar con:** `auditor.py checks --only backend-tests,frontend-unit`

