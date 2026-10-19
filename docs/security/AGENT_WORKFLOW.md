# Flujo de trabajo del equipo AppSec

Cómo trabajan los ocho agentes de seguridad de `.claude/agents/`. Complementa (no sustituye) el
plan general de agentes de [`docs/AGENTS.md`](../AGENTS.md): allí el área «security» era un solo
agente; aquí se desarrolla como equipo. El resto de agentes de ese plan siguen pendientes de autorización.

## 1. El equipo

| Agente | Papel | Puede editar | Herramientas |
|---|---|---|---|
| `security-lead` | Coordina, verifica, prioriza, mantiene el registro y el informe | `docs/security/**`, `SECURITY.md`, `docs/SECURITY.md` | Todas + `Agent` (solo los siete especialistas) |
| `security-auditor` | Revisión transversal OWASP Top 10 y API Top 10 | **Nada** | Read, Grep, Glob, Bash |
| `auth-security` | Google, JWT, cookies, sesiones, recuperación, fuerza bruta, aislamiento | Archivos de autenticación del backend y `frontend/js/{api,account,private}.js` + sus tests | Read, Grep, Glob, Bash, Edit, Write |
| `api-security` | Routers, Pydantic, SQLAlchemy, CORS/CSRF, límites, Alembic | Resto de `backend/app/**`, migraciones nuevas, `backend/tests/**` | Ídem |
| `frontend-security` | XSS, CSP, Pyodide, almacenamiento, recursos externos | `frontend/**` salvo datos, vendor, `config.js` y auth; `tests/unit/**`, `e2e/security.spec.js` | Ídem |
| `dependency-security` | Dependencias y secretos | `requirements*.txt`, `package*.json`, `.gitignore`, `.gitleaks*` | Ídem |
| `security-qa` | Pruebas de regresión y validación | `backend/tests/**`, `tests/unit/**`, `e2e/**` | Ídem |
| `security-devsecops` | CI, análisis automático, protección de ramas | `.github/workflows/**`, `.github/dependabot.yml`, plantilla de PR, `.semgrep/**`, `scripts/security/**` | Ídem |

Las áreas exactas están en `AREAS` de [`.claude/hooks/appsec-guard.mjs`](../../.claude/hooks/appsec-guard.mjs),
que cada agente ejecuta como *hook* `PreToolUse`. `tools:` limita herramientas, **no rutas**
(comprobado en la Fase 1); por eso existe el guardián. Ningún agente puede editar `.claude/**`,
`CLAUDE.md`, `.mcp.json`, `render.yaml`, Docker, `deploy.ps1` ni `frontend/config.js`.

## 2. Flujo

```
persona ──► security-lead ──► (1) estado y diff desde la última revisión
                 │            (2) elige especialistas según los archivos cambiados (§3)
                 ├──► security-auditor ┐
                 ├──► auth-security    │  (3) auditorías de lectura, en paralelo si no se solapan
                 ├──► api-security     │
                 ├──► frontend-security│
                 ├──► dependency-sec.  │
                 └──► devsecops        ┘
                 │            (4) consolida y elimina duplicados   (5) verifica evidencias
                 │            (6) prioriza                         (7) correcciones autorizadas, de una en una
                 ├──► security-qa       (8) pruebas de regresión
                 │            (9) revisa el diff completo          (10) actualiza los informes
                 ▼
          persona: resumen, rama security/..., PR si lo pide (nunca merge)
```

## 3. Dependencias y criterios de delegación

| Cambió… | Especialista | Depende de |
|---|---|---|
| `backend/app/routers/{auth,account}.py`, `security.py`, `session_cookie.py`, `rate_limit.py`, `password_policy.py`, `deps.py`, `frontend/js/{api,account,private}.js` | auth-security | — |
| Resto de `backend/app/**`, `backend/migrations/**`, `backend/app/a2a/**` | api-security | auth-security si toca `deps.py` o la sesión |
| `frontend/**` (HTML, JS, CSP, `sw.js`, Worker) | frontend-security | auth-security si toca `api.js` |
| `backend/requirements*.txt`, `package*.json`, `.gitignore`, `backend/Dockerfile` | dependency-security | — |
| `.github/**`, `.semgrep/**`, `scripts/security/**` | security-devsecops | dependency-security para versiones de herramientas |
| Cualquier código | security-auditor (visión transversal) | — |
| Cualquier corrección | security-qa (siempre después de la corrección) | el especialista que corrige |

- **Incremental por defecto**: el diff desde el commit de la última revisión (anotado en
  `SECURITY_FINDINGS.md`). **Completa** si no hay revisión previa, si cambió la sesión, CORS o la
  CSP, o si la persona lo pide.
- Lanza solo los especialistas que el diff necesita. Sin cambios de código, basta
  `dependency-security` (avisos nuevos) y `security-devsecops` si cambió la CI.
- Los agentes **no se ejecutan necesariamente a la vez**: security-lead decide el orden.

## 4. Reglas para evitar conflictos en archivos

1. Las auditorías son de **solo lectura**: los especialistas devuelven hallazgos en su respuesta;
   solo security-lead escribe `docs/security/*.md`.
2. Una corrección tiene **un dueño** y una lista cerrada de archivos. security-lead la anota en la
   tabla «En curso» de `REMEDIATION_PLAN.md` antes de delegarla; nadie más toca esos archivos hasta
   que se cierre.
3. Correcciones en paralelo solo con listas de archivos disjuntas. Si dos necesitan el mismo archivo,
   van en serie.
4. Si una corrección exige un archivo de otra área, el agente para y lo devuelve a security-lead.
5. Nadie descarta cambios de otros: prohibidos `git reset --hard`, `git clean`, `git checkout .`
   (los bloquea el guardián). Antes de editar, `git status`; si hay cambios ajenos, se trabaja alrededor.
6. Las auditorías van en commits separados de las correcciones cuando sea útil para revisar.

## 5. Procedimiento de revisión

- security-lead abre cada `archivo:línea` citado y reproduce la evidencia (test o comando local).
- Lo que no se reproduce no se acepta como «confirmado»: queda «probable» o «no verificable».
- «Seguro» solo con una comprobación ejecutada (test, búsqueda exhaustiva citada), nunca por la
  opinión de otro agente.
- Antes de cada commit: `git diff` completo, `python scripts/security/run_checks.py` y las suites
  de [`SECURITY_TESTING.md`](SECURITY_TESTING.md) §2 que correspondan.

## 6. Severidad

Explotabilidad (quién puede, qué necesita) × impacto (datos de otras cuentas, toma de cuenta,
ejecución, disponibilidad, solo el propio alumno). Una alerta de herramienta **no** fija la severidad.

| Severidad | Criterio en este proyecto |
|---|---|
| Crítica | Sin autenticación o con una cuenta cualquiera: datos o control de **otras** cuentas, ejecución en el servidor, secreto de producción expuesto |
| Alta | Lo mismo con condiciones realistas (interacción de la víctima, XSS almacenado) |
| Media | Requiere condiciones poco probables o afecta a pocos datos; debilita un control |
| Baja | Defensa en profundidad; requiere acceso al repositorio o solo afecta al propio alumno |
| Informativa | Huecos de pruebas, documentación, endurecimiento sin riesgo concreto |

## 7. Condiciones para aceptar una corrección

1. Hay un test que falla sin la corrección y pasa con ella (o se explica por qué no es posible).
2. Pasa la suite completa del área: backend con 100 % de cobertura, `npm run test:unit` y, si
   toca vistas o CSP, `npm run test:e2e` (o la CI si no se puede en local, dicho explícitamente).
3. `ruff`, Bandit, Semgrep (`.semgrep/`) y Gitleaks limpios.
4. No elimina ni debilita controles, no salta tests y no rompe funciones educativas.
5. Cambio mínimo, dentro del área del dueño, revisado por security-lead en el diff.
6. Si afecta a producción (variables de Render, secretos, despliegue): solo con autorización
   expresa de la persona, que es quien lo aplica.

## 8. Escalado de riesgos críticos

1. El especialista para y avisa a security-lead con la evidencia mínima (sin valores secretos).
2. security-lead lo verifica antes que cualquier otra tarea.
3. Si se confirma: dice a la persona en una frase **qué** pasa, **a quién** afecta y **qué contención**
   propone (por ejemplo: «rota `JWT_SECRET` en Render; invalida todas las sesiones»).
4. Los agentes **no** cambian producción, no revocan credenciales y no publican. Preparan la
   corrección en una rama y las instrucciones.
5. La corrección pasa por §7 con prioridad. El hallazgo queda en `SECURITY_FINDINGS.md` sin datos
   que ayuden a explotarlo mientras no esté corregido en producción.

## 9. Límites de todos los agentes

Trabajar solo dentro del alcance; no inventar archivos, endpoints, vulnerabilidades ni resultados;
no revelar secretos en mensajes, logs, commits o informes; citar `archivo:línea`; distinguir
confirmado, probable y no verificable; nada de DoS, escaneos externos no autorizados ni pruebas
destructivas; pedir autorización si algo puede afectar a producción. El guardián bloquea lo más
peligroso, pero **la última barrera es Git**: rama, diff revisado, CI y merge hecho por la persona.
