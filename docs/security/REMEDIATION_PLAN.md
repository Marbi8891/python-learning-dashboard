# Plan de corrección

Qué se corrige, en qué orden, quién lo hace y con qué archivos. Lo mantiene `security-lead`.
Ninguna corrección empieza sin estar en la tabla «En curso» (bloqueo de archivos, ver
[`AGENT_WORKFLOW.md`](AGENT_WORKFLOW.md) §4) y ninguna afecta a producción sin autorización de la persona.

## En curso

Archivos bloqueados mientras un agente los edita. Vacía = nadie está corrigiendo nada.

| Hallazgo | Dueño | Archivos | Desde |
|---|---|---|---|
| — | — | — | — |

## Pendientes, por prioridad

| Orden | Hallazgo | Corrección propuesta | Dueño | Archivos | Pruebas | ¿Autorización? |
|---|---|---|---|---|---|---|
| 1 | PLD-SEC-002 | `escapeHtml()` en `data-module`, `href` y `data-slug`; test de formato de slugs | frontend-security + security-qa | `frontend/js/app.js`, `backend/tests/test_content.py` | `npm run test:unit`, `npm run test:e2e`, pytest de contenido | No (cambio de bajo riesgo dentro del alcance) |
| 2 | PLD-SEC-004 | Primero **probar** si el Worker tiene CSP (e2e); decidir después | frontend-security + security-qa | `e2e/security.spec.js` | `npx playwright test e2e/security.spec.js` | No para la prueba; sí para cambiar la CSP |
| 3 | PLD-SEC-003 | Quitar `http://127.0.0.1:8000` y `http://localhost:8000` de la CSP publicada sin romper el modo local | frontend-security | `frontend/index.html` y, si hace falta, `backend/app/local_site.py` (api-security) | `npm run test:e2e` completo | **Sí**: cambia la web publicada |
| 4 | PLD-SEC-005 | Requisitos con *hashes* para la imagen de Render | dependency-security | `backend/requirements*.txt`, `backend/Dockerfile` (lo cambia la persona) | Build de Docker, pytest | **Sí**: cambia el despliegue |

## Hechas

| Hallazgo | Corrección | Commit / PR | Verificación |
|---|---|---|---|
| PLD-SEC-001 | `backend/tests/test_security_isolation.py` | rama `security/appsec-hardening-oxxazk` | 4 tests pasan; suite con 100 % de cobertura |
| PLD-SEC-FP1 | `# nosec B310` justificado en `backend/app/mailer.py`, `.gitleaksignore` por huella | ídem | Bandit `-ll -ii` y Gitleaks sin hallazgos |

## Pendiente de la persona (no lo pueden hacer los agentes)

Ver [`SECURITY_TESTING.md`](SECURITY_TESTING.md) §6: activar *secret scanning* y *push protection*,
Dependabot alerts, CodeQL (*default setup*) y la regla de protección de `main` con los checks nuevos.
