# CLAUDE.md

Instrucciones para Claude Code en este repositorio. La arquitectura está en
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), las pruebas en [`docs/TESTING.md`](docs/TESTING.md) y
el plan general de agentes de desarrollo (por fases, cada una con autorización) en
[`docs/AGENTS.md`](docs/AGENTS.md).

## Reglas del proyecto

- **Hacer merge a `main` publica la web** (`.github/workflows/pages.yml`). El merge lo hace siempre la
  persona. Nunca `git push` a `main`, `gh pr merge` ni `deploy.ps1`.
- Trabaja en una rama `tipo/descripcion` con cambios pequeños, y revisa `git diff` antes de cada commit.
- No leas ni muestres `.env`, claves, keystores ni `backend/.local-secret`. No toques secretos de GitHub
  ni variables de Render.
- No uses servicios ni APIs de pago: solo herramientas gratuitas.
- Nadie edita a mano un JSON generado de `frontend/data/`: se cambia su script y se regenera.
- Una tarea no está terminada hasta que pasan las pruebas de `docs/TESTING.md` §3 que le tocan.
  Prohibido saltar o debilitar un test para que pase.

## Equipo AppSec

Ocho agentes de seguridad en `.claude/agents/`. Flujo, dependencias y reglas en
[`docs/security/AGENT_WORKFLOW.md`](docs/security/AGENT_WORKFLOW.md).

| Agente | Para qué |
|---|---|
| `security-lead` | Coordina la auditoría, verifica, prioriza y mantiene `docs/security/SECURITY_FINDINGS.md` |
| `security-auditor` | Revisión OWASP Top 10 / API Top 10, solo lectura |
| `auth-security` | Google, JWT, cookies, sesiones, recuperación, fuerza bruta, aislamiento entre cuentas |
| `api-security` | FastAPI, Pydantic, SQLAlchemy, CORS/CSRF, límites, Alembic |
| `frontend-security` | XSS, CSP, Pyodide, almacenamiento local, recursos externos |
| `dependency-security` | Dependencias y secretos (pip-audit, npm audit, Gitleaks) |
| `security-qa` | Pruebas de regresión de seguridad |
| `security-devsecops` | GitHub Actions y comprobaciones automáticas |

Cómo invocarlos:
- Auditoría completa con el coordinador como sesión principal (recomendado):
  `claude --agent security-lead "Auditoría completa de seguridad desde la línea base"`.
- Un especialista concreto en una sesión normal: `@agent-auth-security revisa el login con Google`
  o «usa el agente api-security para revisar los routers».
- Comprobaciones automáticas sin agentes: `python scripts/security/run_checks.py`.

El guardián `.claude/hooks/appsec-guard.mjs` (necesita Node) solo actúa si has aceptado el diálogo de
confianza de la carpeta al abrir `claude` aquí por primera vez.

Reglas comunes de los agentes (las hace cumplir en parte el guardián):
- Trabajar solo dentro del alcance autorizado y del área de archivos de cada uno.
- No inventar archivos, endpoints, vulnerabilidades ni resultados; citar `archivo:línea`.
- Distinguir confirmado, probable y no verificable; una alerta de herramienta no fija la severidad.
- No revelar secretos en mensajes, logs, commits o informes.
- Nada de DoS, escaneos externos ni pruebas destructivas; producción solo en lectura pasiva y con autorización.
- Conservar los cambios de la persona; crear pruebas cuando sea razonable; documentar riesgos residuales.
