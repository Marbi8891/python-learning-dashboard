# Informes de QA

Los generan los scripts de `scripts/qa/` y **no se suben a Git** (están en `.gitignore`), porque
cambian en cada ejecución:

| Archivo | Lo genera |
|---|---|
| `latest-report.md` | `bash scripts/qa/pre-push-check.sh` (y el workflow `qa-tests.yml`, como artefacto) |
| `security-report.md` | `bash scripts/qa/security_scan.sh` (y `security.yml`) |
| `task-report.md` | `bash scripts/qa/claude-task-check.sh "<tarea>"` |
| `logs/<paso>.log` | Salida completa de cada comprobación |
| `*.json` | Resultados de pip-audit, npm audit, Bandit, Gitleaks (sin valores de secretos) y del validador del frontend |

Estados: **PASS** (todo superado), **WARNING** (avisos o comprobaciones no ejecutadas: revisar),
**FAIL** (no integrar). Guía: [`docs/QA_GUIDE.md`](../../docs/QA_GUIDE.md).
