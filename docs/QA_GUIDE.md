# Guía del entorno QA

Cómo comprobar que un cambio (tuyo o de Claude Code) no rompe nada antes de subirlo. Las pruebas de
siempre siguen en [TESTING.md](TESTING.md); esto las junta en un solo comando, añade las que faltaban
y deja un informe. El flujo de ramas está en [GIT_WORKFLOW.md](GIT_WORKFLOW.md) y los workflows en
[CI_CD_ARCHITECTURE.md](CI_CD_ARCHITECTURE.md).

## Preparar el entorno (una vez)

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r backend/requirements-dev.txt
pip install pip-audit==2.10.1 bandit==1.9.4    # análisis de seguridad
npm ci
npx playwright install chromium        # pruebas en el navegador
bash scripts/qa/install-hooks.sh       # opcional: cada git push valida antes
```

**Gitleaks** (secretos) es un binario aparte. Descárgalo de
<https://github.com/gitleaks/gitleaks/releases/tag/v8.28.0> (el mismo que usa CI), comprueba su
SHA-256 con el archivo `checksums.txt` de esa página y ponlo en el `PATH` (o indica su ruta con
`GITLEAKS=/ruta/gitleaks`). Sin él, el paso sale como **SKIP**, nunca como superado; en GitHub
Actions se ejecuta siempre.

En Windows, los scripts `.sh` se ejecutan con **Git Bash** (viene con Git for Windows).

## Uso diario

```bash
bash scripts/qa/pre-push-check.sh          # antes de cada push (2-3 min)
bash scripts/qa/pre-push-check.sh --e2e    # también las e2e completas (más lento)
npm run qa                                 # lo mismo que el primero
```

Lo que hace, en este orden, deteniéndose en el primer fallo:

| # | Paso | Qué detecta |
|---|---|---|
| 1 | Rama actual | Trabajar en `main`/`develop`, HEAD separado o nombre sin `tipo/descripcion` |
| 2 | Sin cambios inesperados | Archivos modificados o nuevos sin commit (no irían en el push) |
| 3 | Conflictos de Git | Marcas `<<<<<<<` sin resolver, fusiones a medias y choques con la rama base |
| 4 | Archivos modificados | Lista de cambios; **falla** si se borran pruebas, se añade `skip`/`only`/`xfail`, se rebaja la cobertura o se edita a mano un JSON generado; avisa si cambian workflows o dependencias |
| 5 | Sintaxis de Python, ruff | Errores de sintaxis, lint y formato (también en `tests/`) |
| 6 | JavaScript | Sintaxis, imports a módulos que no existen, nombres que un módulo no exporta, `import()` y Web Workers rotos, rutas de datos inexistentes, referencias rotas en HTML/CSS/manifiesto, scripts inline que la CSP bloquearía, JSON roto |
| 7 | HTML y CSS | html-validate (`standard`) y stylelint (solo reglas de errores reales) |
| 8 | Frontend | `npm run test:unit`, tests del validador y Web Workers en Chromium |
| 9 | Backend | pytest con cobertura del 100 %, contrato OpenAPI, 401 en todas las rutas protegidas, errores JSON, dependencias |
| 10 | Integración | Llamadas del frontend contra la API, cursos que sincroniza la web, CORS, CSP, variables de Render y `.env.example`, Google, contenido generado al día |
| 11 | Seguridad | CSP de cada página, secretos versionados, cookie de sesión, autorización entre cuentas, validación de entradas, pip-audit, npm audit, Bandit y Gitleaks |
| 12 | Informe | `reports/qa/latest-report.md` |

Opciones: `--keep-going` (no se detiene: informe completo), `--allow-dirty` (cambios sin commit como
aviso), `--no-fetch` (sin red: no actualiza la rama base).

### Resultado

- **PASS**: todo superado. Se puede subir.
- **WARNING**: nada falla, pero hay avisos (por ejemplo, cambian dependencias o workflows) o algo no
  se ha podido ejecutar en tu equipo (**SKIP**, por ejemplo Gitleaks sin instalar). Revísalo; en CI
  esos pasos se ejecutan siempre y un SKIP allí es un fallo.
- **FAIL**: el script sale con código 1 y el hook cancela el push.

Cuando algo falla, el script muestra el **error**, el **archivo afectado**, la **causa probable**, la
**solución** y las últimas líneas del log (`reports/qa/logs/<paso>.log`). Ejemplo real:

```
▶ Integración frontend-backend ... FAIL (código 1)
── Fallo en «Integración frontend-backend» ──
  Archivos afectados: tests/integration/test_qa_frontend_backend_contract.py:56
  Causa: el frontend y el backend ya no encajan (ruta, campo JSON, CORS, CSP o variables).
  Solución: python -m pytest tests/integration -x -q y alinea los dos lados.
    │ E  AssertionError: js/account.js: POST /api/v1/auth/logout-everywhere no existe en la API
```

## Después de cada tarea (Claude Code o cualquiera)

```bash
bash scripts/qa/claude-task-check.sh "Añadir filtro por módulo en el panel" --scope "frontend/js frontend/css"
bash scripts/qa/claude-task-check.sh "..." --scope "..." --full    # + batería completa
```

1. Muestra `git diff --stat` y 2. la lista de archivos modificados (con y sin commit).
3. Avisa de los archivos **fuera del alcance** declarado con `--scope`: hay que confirmar a mano que
   corresponden a la tarea.
4. Ejecuta **solo las pruebas que tocan** según lo que ha cambiado (la tabla «Qué ejecutar según lo
   que cambies» de [TESTING.md](TESTING.md)), y siempre Gitleaks y la revisión de pruebas borradas.
5. Con `--full`, la batería completa.
6-7. Deja el informe en `reports/qa/task-report.md`.

Reglas para Claude Code (también en CLAUDE.md):

- Si algo falla, investigar el origen y corregirlo **solo si está dentro de la tarea**. Repetir las
  pruebas. Como mucho 3 intentos por fallo y nunca la misma solución dos veces; si no se resuelve,
  parar y explicar el bloqueo.
- Nunca borrar, saltar ni debilitar una prueba, ni desactivar un control de seguridad, para que pase.
- Antes de integrar, la batería completa (`pre-push-check.sh`) en PASS o WARNING revisado.

## Pruebas por separado

| Qué | Comando |
|---|---|
| Validación estática del frontend | `npm run qa:static` |
| HTML / CSS | `npm run lint:html` · `npm run lint:css` |
| Tests del validador, HTML y CSS | `npm run test:frontend` |
| Web Workers y módulos en Chromium | `npm run test:frontend:browser` |
| Contrato de la API, errores y dependencias | `python -m pytest tests/backend -q` |
| Integración frontend-backend | `python -m pytest tests/integration -q` |
| Pruebas de seguridad | `python -m pytest tests/security -q` |
| Todo el análisis de seguridad | `bash scripts/qa/security_scan.sh` |
| Verificar el artefacto de Pages | `cp -r frontend /tmp/site && python scripts/security/production_csp.py /tmp/site && python scripts/qa/verify_pages_artifact.py /tmp/site` |

Las pruebas de Python de `tests/` se ejecutan **desde la raíz** del repositorio (usan
`tests/pytest.ini` y reutilizan las fixtures de `backend/tests/conftest.py`: SQLite en memoria, sin
red). Nunca se conectan a Render, Neon, Google ni Brevo.

**Pyodide real**: la prueba «Python real (Pyodide) ejecuta código en el Worker» necesita descargar
Pyodide del CDN. Sin red sale como *skipped* con el motivo (nunca como superada). Para ejecutarla sin
acceso al CDN, sirve Pyodide en local como explica [TESTING.md](TESTING.md) y define `PYODIDE_URL`.

## Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| `Sin cambios inesperados: FAIL` | Hay archivos sin commit | `git status`; commit o `git stash` |
| `Conflictos de Git: FAIL` | La rama choca con `develop` | Ver «Conflictos» en [GIT_WORKFLOW.md](GIT_WORKFLOW.md) |
| `Archivos modificados: FAIL … BORRA pruebas` | Se ha borrado un test | Restáuralo: `git checkout origin/develop -- <archivo>` |
| `js-missing-export` | Se ha renombrado una exportación | Exporta el nombre o corrige el import (el mensaje dice cuál) |
| `js-missing-import` con `./util` | Falta `.js` en el import | El navegador no añade extensiones: `./util.js` |
| `html-inline-script` / `html-inline-handler` | Código JS dentro del HTML | Muévelo a `frontend/js/` (la CSP lo bloquearía) |
| `Contrato de la API: rutas sin autenticación` | Ruta nueva sin `CurrentUser` | Si debe ser pública, añádela a `PUBLIC_OPERATIONS` en `tests/backend/test_qa_api_contract.py` **justificándolo en el PR** |
| `Integración: … no existe en la API` | El frontend llama a una ruta que el backend no tiene | Alinea `frontend/js` y `backend/app/routers` |
| `Backend: Coverage failure` | Código nuevo sin probar | Añade tests para las líneas `Missing` |
| `Gitleaks: posible secreto` | Clave o token en el código | Si es real, quítalo y **rota la clave**. Si es un falso positivo, añádelo a `.gitleaks.toml` con una explicación |
| `pip-audit` / `npm audit` | Dependencia vulnerable | Sube la versión mínima a la que lo corrige |
| `Módulos y Web Workers: SKIP` | Chromium de Playwright no instalado | `npx playwright install chromium` |
| Las pruebas de navegador no arrancan: puerto 5510 ocupado | Otro servidor en ese puerto | `QA_FRONTEND_PORT=5520 npm run test:frontend:browser` |
