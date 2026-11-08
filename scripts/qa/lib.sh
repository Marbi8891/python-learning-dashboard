# Funciones comunes de los scripts de QA (pre-push-check.sh, security_scan.sh, claude-task-check.sh).
# Se carga con: source "$(dirname "$0")/lib.sh"
#
# Cada comprobación se ejecuta con `run_step <id> "<nombre>" <comando...>`:
#   - guarda la salida completa en reports/qa/logs/<id>.log
#   - anota el resultado (PASS, FAIL, WARN o SKIP) en reports/qa/results.jsonl
#   - si falla, muestra el diagnóstico (archivo afectado, causa probable y solución) y, salvo
#     QA_KEEP_GOING=1, detiene el script con código 1
# Un comando puede devolver 0 (PASS), 1 (FAIL), 77 (SKIP: no se pudo ejecutar aquí) o 78 (WARN).
# Nunca se convierte un fallo en éxito: SKIP y WARN se ven en el informe y nunca cuentan como PASS.

QA_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QA_REPORT_DIR="${QA_REPORT_DIR:-$QA_ROOT/reports/qa}"
QA_LOG_DIR="$QA_REPORT_DIR/logs"
QA_RESULTS="$QA_REPORT_DIR/results.jsonl"
QA_KEEP_GOING="${QA_KEEP_GOING:-0}"
QA_FAILED=0
QA_WARNED=0

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_BLUE=$'\033[36m'; C_BOLD=$'\033[1m'; C_OFF=$'\033[0m'
else
  C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""; C_BOLD=""; C_OFF=""
fi

qa_init() {
  mkdir -p "$QA_LOG_DIR"
  if [ "${QA_APPEND:-0}" != "1" ]; then
    : >"$QA_RESULTS"
    rm -f "$QA_LOG_DIR"/*.log
  fi
}

# Python del proyecto: el del entorno virtual si existe (.venv), si no python3/python
qa_python() {
  if [ -n "${QA_PYTHON:-}" ]; then echo "$QA_PYTHON"
  elif [ -x "$QA_ROOT/.venv/bin/python" ]; then echo "$QA_ROOT/.venv/bin/python"
  elif [ -x "$QA_ROOT/.venv/Scripts/python.exe" ]; then echo "$QA_ROOT/.venv/Scripts/python.exe"
  elif command -v python3 >/dev/null 2>&1; then echo python3
  else echo python
  fi
}

_json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"; s="${s//\"/\\\"}"; s="${s//$'\n'/\\n}"; s="${s//$'\r'/}"; s="${s//$'\t'/ }"
  printf '%s' "$s"
}

_record() { # id nombre estado segundos detalle
  printf '{"id":"%s","name":"%s","status":"%s","seconds":%s,"detail":"%s","log":"%s"}\n' \
    "$1" "$(_json_escape "$2")" "$3" "$4" "$(_json_escape "$5")" "reports/qa/logs/$1.log" >>"$QA_RESULTS"
}

# Primeras líneas con aspecto de «archivo:línea» del log: el archivo afectado
_affected_files() {
  {
    grep -oE '([A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(py|js|mjs|html|css|json|yml|yaml|toml|sh|txt):[0-9]+' "$1" 2>/dev/null
    # Formatos que ponen el archivo solo en una línea (stylelint, html-validate)
    grep -oE '^\s*(\./)?(frontend|backend|scripts|tests|e2e)/[^ :]+\.[a-z]+\s*$' "$1" 2>/dev/null | tr -d ' '
  } | sed "s#^${QA_ROOT#/}/##; s#^\./##" \
    | grep -v -E '(^node:|site-packages|/lib/python|^usr/|^tmp/)' | awk '!seen[$0]++' | head -5
}

# Causa probable y solución según el tipo de comprobación y el texto del error
_diagnose() { # id log
  local id="$1" log="$2"
  case "$id" in
    branch) echo "Causa: se está trabajando en una rama protegida o sin formato tipo/descripcion.|Solución: git switch -c feature/<descripcion> (o fix/, test/) y repite.";;
    clean-tree) echo "Causa: hay cambios sin commit o archivos nuevos sin añadir; el push no los incluiría.|Solución: revisa git status; haz commit de lo que corresponde a la tarea o guárdalo con git stash.";;
    conflicts) echo "Causa: marcas de conflicto sin resolver o cambios que chocan con la rama base.|Solución: git fetch origin && git rebase origin/<base>, resuelve los archivos indicados y repite.";;
    changed-files) echo "Causa: el cambio borra o salta pruebas, o edita a mano un JSON generado.|Solución: restaura las pruebas; regenera el JSON con su script (docs/TESTING.md).";;
    lint-python|format-python)
      echo "Causa: el código Python no cumple ruff (pyproject de backend).|Solución: cd backend && ruff check --fix . ../e2e ../scripts ../tests && ruff format . ../e2e ../scripts ../tests";;
    syntax-python) echo "Causa: error de sintaxis de Python.|Solución: abre el archivo en la línea indicada y corrígelo.";;
    frontend-static) echo "Causa: import, export, ruta o recurso inexistente en el frontend (detalle en el log).|Solución: sigue la «Solución» de cada error de scripts/qa/frontend_static.mjs.";;
    lint-html) echo "Causa: HTML no válido (html-validate:standard).|Solución: npx html-validate frontend/*.html y corrige la regla indicada.";;
    lint-css) echo "Causa: CSS con propiedades, unidades o selectores que no existen.|Solución: npx stylelint \"frontend/css/*.css\" y corrige la regla indicada.";;
    unit-frontend|qa-frontend) echo "Causa: un test unitario del frontend falla: un cambio rompe la lógica que prueba.|Solución: npm run test:unit (o test:frontend) y lee el primer «not ok».";;
    browser-frontend) echo "Causa: la web no carga un módulo o el Web Worker de Python no responde en Chromium.|Solución: npx playwright test -c tests/frontend --debug";;
    backend) if grep -q "Required test coverage" "$log" && ! grep -qE "^(FAILED|ERROR) " "$log"; then
               echo "Causa: la cobertura del backend ha bajado del 100 %.|Solución: añade tests para las líneas «Missing» del informe de cobertura.";
             else echo "Causa: un test del backend falla.|Solución: cd backend && python -m pytest -x -q <archivo>::<test> para reproducirlo."; fi;;
    qa-python) echo "Causa: contrato de API, autorización o errores de la API han cambiado.|Solución: python -m pytest tests/backend -x -q; si el cambio es intencionado, revisa el contrato (no debilites la prueba).";;
    integration) echo "Causa: el frontend y el backend ya no encajan (ruta, campo JSON, CORS, CSP o variables).|Solución: python -m pytest tests/integration -x -q y alinea los dos lados.";;
    generated) echo "Causa: un JSON generado o el precache no están al día con sus scripts.|Solución: ejecuta el script indicado sin --check (docs/TESTING.md) y haz commit del resultado.";;
    security-tests) echo "Causa: CSP, secretos, cookies o autorización ya no cumplen las reglas.|Solución: python -m pytest tests/security -x -q";;
    pip-audit|npm-audit) echo "Causa: dependencia con una vulnerabilidad conocida.|Solución: sube la versión mínima en requirements.txt / package.json a la que la corrige y repite.";;
    bandit) echo "Causa: Bandit encuentra un patrón inseguro de severidad media o alta en backend/app.|Solución: corrige el código; un # nosec solo con justificación revisada.";;
    gitleaks) echo "Causa: posible secreto en el código o en el historial.|Solución: si es real, quítalo y ROTA la clave (ya se considera filtrada); si es un falso positivo, añádelo a .gitleaks.toml con una explicación.";;
    e2e) echo "Causa: una prueba end-to-end falla.|Solución: npx playwright test <archivo> --debug; sin red hacia el CDN de Pyodide, ver docs/TESTING.md.";;
    *) echo "Causa: ver el log.|Solución: ejecuta el comando del paso a mano para ver el error completo.";;
  esac
}

run_step() { # id nombre comando...
  local id="$1" name="$2"; shift 2
  local log="$QA_LOG_DIR/$id.log" start end code status detail
  printf '%s▶ %s%s ... ' "$C_BLUE" "$name" "$C_OFF"
  start=$(date +%s)
  ( cd "$QA_ROOT" && "$@" ) >"$log" 2>&1
  code=$?
  end=$(date +%s)
  # En CI (QA_STRICT=1) una herramienta que falta es un fallo de configuración, no un SKIP
  if [ "$code" = 77 ] && [ "${QA_STRICT:-0}" = "1" ]; then
    echo "QA-DETAIL: no se ha podido ejecutar en CI (QA_STRICT): $(grep -m1 '^SKIP:' "$log" | sed 's/^SKIP: //')" >>"$log"
    code=1
  fi
  case "$code" in
    0) status=PASS; printf '%sPASS%s (%ss)\n' "$C_GREEN" "$C_OFF" "$((end - start))";;
    77) status=SKIP; QA_WARNED=1; printf '%sSKIP%s\n' "$C_YELLOW" "$C_OFF";;
    78) status=WARN; QA_WARNED=1; printf '%sWARNING%s\n' "$C_YELLOW" "$C_OFF";;
    *) status=FAIL; QA_FAILED=1; printf '%sFAIL%s (código %s)\n' "$C_RED" "$C_OFF" "$code";;
  esac
  detail="$(grep -E '^(QA-DETAIL|SKIP|WARN):' "$log" | sed -E 's/^[A-Z-]+: ?//' | head -3 | paste -sd ' ' -)"
  if [ "$status" = SKIP ] || [ "$status" = WARN ]; then
    [ -n "$detail" ] && printf '    %s\n' "$detail"
  fi
  if [ "$status" = FAIL ]; then
    local diag files
    diag="$(_diagnose "$id" "$log")"
    files="$(_affected_files "$log" | paste -sd ' ' -)"
    [ -z "$detail" ] && detail="$(grep -m1 -iE 'error|fail|not ok|assert|✘' "$log" | cut -c1-240)"
    printf '%s\n' "${C_RED}${C_BOLD}── Fallo en «$name» ──${C_OFF}"
    printf '  Error: %s\n' "${detail:-ver el log}"
    printf '  Archivos afectados: %s\n' "${files:-no identificados (ver el log)}"
    printf '  %s\n' "${diag%%|*}"
    printf '  %s\n' "${diag##*|}"
    printf '  Log completo: reports/qa/logs/%s.log\n' "$id"
    printf '  Últimas líneas:\n'
    tail -n 15 "$log" | sed 's/^/    │ /'
    detail="${detail} · ${files:+Archivos: $files · }${diag//|/ · }"
  fi
  _record "$id" "$name" "$status" "$((end - start))" "$detail"
  if [ "$status" = FAIL ] && [ "$QA_KEEP_GOING" != "1" ]; then
    return 1
  fi
  return 0
}

# Para un comando que no está instalado: SKIP con el motivo (nunca PASS)
require_cmd() { # comando motivo
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "SKIP: $1 no está instalado ($2)"
    return 77
  fi
}
