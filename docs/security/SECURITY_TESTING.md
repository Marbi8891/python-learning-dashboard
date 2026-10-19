# Pruebas y herramientas de seguridad

Cómo se comprueba la seguridad del proyecto: pruebas automáticas, analizadores gratuitos, su
integración en CI y lo que hay que activar a mano en GitHub. Las pruebas generales están en
[`docs/TESTING.md`](../TESTING.md).

## 1. Todo de una vez (local)

```bash
python scripts/security/run_checks.py            # pip-audit, npm audit, Bandit, Semgrep, Gitleaks
python scripts/security/run_checks.py --list     # qué ejecuta y cómo instalar cada una
python scripts/security/run_checks.py --only bandit,semgrep
```

Las herramientas que falten se saltan con la instrucción para instalarlas: el script solo falla
(código 1) si una herramienta **instalada** encuentra algo. Nunca imprime secretos.

## 2. Pruebas de seguridad

| Qué | Comando | Dónde |
|---|---|---|
| Aislamiento entre dos cuentas (BOLA/IDOR) | `cd backend && python -m pytest -q tests/test_security_isolation.py` | `backend/tests/test_security_isolation.py` |
| Autenticación, Google, cookie, recuperación | `python -m pytest -q tests/test_auth.py tests/test_google_auth.py tests/test_session_cookie.py tests/test_password_reset.py` | `backend/tests/` |
| Endurecimiento, cabeceras, valores por defecto, detección | `python -m pytest -q tests/test_hardening.py tests/test_security_headers.py tests/test_security_defaults.py tests/test_attack_detection.py` | `backend/tests/` |
| Todo el backend (100 % de cobertura) | `python -m pytest -q --cov=app --cov-fail-under=100` | `backend/` |
| Markdown seguro y escape | `npm run test:unit` | `tests/unit/markdown.test.mjs` |
| Guardián y definición de los agentes | `npm run test:unit` | `tests/unit/appsec-guard.test.mjs` |
| Navegador: CSP, almacenamiento, cierre de sesión | `npx playwright test e2e/security.spec.js` | `e2e/` |

Reglas (las aplica `security-qa`): datos ficticios `@example.com`, SQLite en memoria, nunca
producción; un test de regresión debe fallar sin la corrección; prohibido saltar o debilitar tests.

## 3. Herramientas

### pip-audit (dependencias Python)
- **Analiza**: `backend/requirements.txt` contra la base de avisos de PyPI/OSV.
- **Ejecutar**: `pip install pip-audit && cd backend && pip-audit -r requirements.txt`.
- **Límites**: solo vulnerabilidades publicadas; no detecta paquetes maliciosos ni abandonados.
  Resuelve los rangos a la versión más nueva, que puede no ser la desplegada.
- **Resultados**: paquete, versión, ID del aviso y versión corregida. Se evalúa si la función
  vulnerable se usa aquí antes de fijar severidad.
- **CI**: `ci.yml`, job `backend` (bloqueante).

### npm audit (dependencias JavaScript de test)
- **Analiza**: `package-lock.json` (solo Playwright y axe; la web no usa npm).
- **Ejecutar**: `npm ci && npm audit --audit-level=high`.
- **Límites**: no cubre `frontend/vendor/` (highlight.js copiado) ni Pyodide del CDN.
- **CI**: `ci.yml`, job `e2e` (bloqueante para altas y críticas).

### Bandit (análisis estático del backend)
- **Analiza**: patrones peligrosos en `backend/app/` (SQL por texto, `subprocess`, `pickle`,
  criptografía débil, contraseñas en el código…).
- **Ejecutar**: `pip install bandit==1.9.4 && bandit -r backend/app -ll -ii` (`-ll -ii`: severidad y
  confianza media o alta; sin ellos aparecen 4 alertas bajas, falsos positivos documentados).
- **Límites**: análisis por patrones, sin flujo de datos entre funciones; muchas alertas bajas son ruido.
- **Resultados**: ID de regla (`B310`…), severidad y confianza. Un falso positivo se marca con
  `# nosec BXXX` **en la línea y con el motivo** y se registra en `SECURITY_FINDINGS.md`.
- **CI**: `security.yml`, job `bandit` (bloqueante).

### Semgrep (reglas propias y conjuntos públicos)
- **Analiza**: `.semgrep/pld-rules.yml`, nueve reglas que protegen decisiones del proyecto: SQL por
  texto, JWT sin verificar, shell o código dinámico en el backend, secretos en logs, CORS con comodín,
  `eval`/`new Function` en la web, tokens en `localStorage`, datos de la URL en `innerHTML` sin
  `escapeHtml`, y `target="_blank"` sin `rel` (aviso). `.semgrepignore` excluye vendor, Android y `node_modules`.
- **Ejecutar**: `pip install semgrep==1.181.0 && semgrep scan --metrics=off --config .semgrep/ --error`.
  En Windows, Semgrep va mejor en WSL o con Docker (`docker run --rm -v "%cd%:/src" semgrep/semgrep semgrep scan --metrics=off --config .semgrep/ --error`).
- **Límites**: las reglas propias funcionan sin conexión; los conjuntos públicos (`p/python`,
  `p/owasp-top-ten`…) se descargan de `semgrep.dev`. La versión gratuita no sigue datos entre archivos.
- **Resultados**: ID de regla, archivo y línea. Las reglas propias se probaron con código vulnerable de
  ejemplo (todas saltan) y sobre el repositorio (0 hallazgos).
- **CI**: `security.yml`, job `semgrep`: reglas propias **bloqueantes**; conjuntos públicos
  **informativos** (`continue-on-error`) hasta revisar su primera ejecución.

### Gitleaks (secretos en Git)
- **Analiza**: toda la historia (`gitleaks git`) o el árbol de trabajo (`gitleaks dir`).
- **Ejecutar**: descarga el binario 8.28.0 de [GitHub](https://github.com/gitleaks/gitleaks/releases) y
  `gitleaks git --redact .` (historia) o `gitleaks dir --redact .` (sin commit). **Siempre `--redact`**.
- **Límites**: reglas por patrones y entropía; no sabe si un secreto sigue activo. Contraseñas
  ficticias de tests dan falsos positivos.
- **Resultados**: regla, archivo, línea, commit y huella. Un falso positivo se añade a
  `.gitleaksignore` (huella + comentario). Un secreto real **no se borra ni se prueba**: se avisa a
  `security-lead` y la persona lo revoca en su proveedor (`AGENT_WORKFLOW.md` §8).
- **CI**: `security.yml`, job `gitleaks`, historia completa, binario con suma SHA-256 comprobada (bloqueante).

### Dependabot y CodeQL (GitHub)
- **Dependabot** (`.github/dependabot.yml`): PR mensuales para pip, npm, Gradle, Docker y Actions.
  Las *alerts* se activan a mano (§6).
- **CodeQL**: análisis de flujo de datos de Python y JavaScript, gratuito en repositorios públicos.
  Se usa el *default setup* (§6) y **no** un workflow propio: GitHub no permite los dos a la vez.

## 4. CI

| Workflow | Cuándo | Jobs de seguridad | Permisos |
|---|---|---|---|
| `ci.yml` | push a `main`, PR | `pip-audit`, `npm audit`, tests de seguridad dentro de pytest y unitarios | `contents: read` |
| `security.yml` | push a `main`, PR, lunes, manual | `bandit`, `semgrep`, `gitleaks` | `contents: read` |

Todas las acciones usan `persist-credentials: false`; ninguna usa secretos del repositorio, ni
`pull_request_target`, ni imprime el entorno.

## 5. Guardián de los agentes

`.claude/hooks/appsec-guard.mjs` (Node, sin dependencias) se ejecuta antes de cada herramienta de los
ocho agentes. Bloquea con código 2 leer secretos, editar fuera del área, comandos destructivos o de
publicación y escáneres; pide confirmación para cualquier acceso a producción. Sus tests están en
`tests/unit/appsec-guard.test.mjs`.

Comprobado con Claude Code 2.1.303 (19/10/2026): los ocho agentes aparecen como tipos de subagente, y
el guardián bloquea de verdad tanto con `claude --agent security-qa` como cuando la sesión principal
delega en `security-auditor` (el registro de depuración muestra `PreToolUse:Bash … finished with status 2`).

**Límites**:
- Claude Code **solo ejecuta los hooks de los agentes si la carpeta es de confianza** (el diálogo
  «Do you trust this folder?» aceptado al abrir `claude` en el repositorio). En una carpeta sin
  aceptar, o en modo `-p` sin haberla aceptado antes, los hooks se saltan y solo quedan las
  instrucciones del agente. Abre `claude` una vez en la carpeta y acepta el diálogo.
- Un hook de `Bash` ve el comando, no lo que hace un script por dentro.
- Si Node falta, el hook no se ejecuta y no bloquea.
- La última barrera es Git + CI + merge humano.

## 6. Ajustes que tiene que hacer la persona en GitHub

No se pueden versionar. Ningún paso necesita compartir un secreto.

1. *Settings → Code security*:
   - **Secret scanning** y **Push protection**: activar.
   - **Dependabot alerts** y **Dependabot security updates**: activar.
   - **Private vulnerability reporting**: activar.
   - **Code scanning → CodeQL analysis → Set up → Default**.
2. *Settings → Actions → General → Workflow permissions*: «Read repository contents and packages permissions».
3. *Settings → Rules → Rulesets → New branch ruleset* para `main`:
   - *Restrict deletions* y *Block force pushes*;
   - *Require a pull request before merging*;
   - *Require status checks to pass*: `backend`, `e2e`, `bandit`, `semgrep`, `gitleaks` (aparecen en la
     lista después de la primera ejecución de `security.yml`). Siendo la única persona del proyecto, no
     actives revisiones obligatorias de otra persona o no podrás hacer merge.
