#!/usr/bin/env bash
# Control de cada tarea de Claude Code (o de cualquiera): qué ha cambiado, si corresponde a la
# tarea y qué pruebas le tocan. Ver docs/QA_GUIDE.md, sección «Después de cada tarea».
#
#   bash scripts/qa/claude-task-check.sh "<tarea>" [--scope "frontend/js backend/app"] [--full]
#
#   <tarea>   descripción breve de lo que se pidió (va al informe)
#   --scope   carpetas o archivos que la tarea puede tocar: lo demás sale como aviso
#   --full    después de las pruebas que tocan, la batería completa (pre-push-check.sh)
#
# Deja el informe en reports/qa/task-report.md. No hace commit, push ni cambia archivos.
set -u
source "$(dirname "$0")/lib.sh"
cd "$QA_ROOT" || exit 1
export QA_ALLOW_DIRTY=1  # la tarea puede no tener commit todavía
source "$QA_ROOT/scripts/qa/checks.sh"

TASK="${1:-}"
[ -z "$TASK" ] || [[ "$TASK" == --* ]] && { sed -n '2,13p' "$0"; exit 2; }
shift
SCOPE=""; FULL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --scope) SCOPE="$2"; shift 2 ;;
    --full) FULL=1; shift ;;
    *) echo "Opción desconocida: $1"; exit 2 ;;
  esac
done

qa_init
QA_KEEP_GOING=1  # se quiere ver todo lo que falla en la tarea, no solo lo primero

BASE="$(qa_base_ref)"
RANGE="$( [ -n "$BASE" ] && git merge-base "$BASE" HEAD || git rev-parse HEAD)"
CHANGED="$( { git diff --name-only "$RANGE" HEAD; git diff --name-only HEAD; git ls-files --others --exclude-standard; } | sort -u)"

echo "${C_BOLD}Tarea:${C_OFF} $TASK"
echo "${C_BOLD}1. git diff (resumen)${C_OFF}"
git diff --stat "$RANGE" HEAD; git diff --stat HEAD
echo "${C_BOLD}2. Archivos modificados${C_OFF}"
echo "${CHANGED:-(ninguno)}" | sed 's/^/  /'

# 3. ¿Corresponden a la tarea? Lo que caiga fuera de --scope se marca para revisarlo a mano
check_scope() {
  [ -z "$CHANGED" ] && { echo "QA-DETAIL: la tarea no ha cambiado ningún archivo"; return 78; }
  [ -z "$SCOPE" ] && { echo "WARN: sin --scope: revisa a mano que cada archivo corresponde a la tarea"; echo "$CHANGED"; return 78; }
  local outside=""
  while IFS= read -r f; do
    local ok=0
    for s in $SCOPE; do [[ "$f" == "$s"* ]] && ok=1; done
    [ "$ok" = 0 ] && outside="$outside $f"
  done <<<"$CHANGED"
  if [ -n "$outside" ]; then echo "WARN: archivos fuera del alcance declarado ($SCOPE):$outside"; return 78; fi
  echo "Todos los archivos están dentro del alcance: $SCOPE"
}
run_step scope "¿Los cambios corresponden a la tarea?" check_scope
run_step changed-files "Archivos modificados (pruebas borradas o saltadas, JSON generados)" check_changed_files
run_step conflicts "Conflictos de Git" check_conflicts

# 4. Pruebas que tocan según lo que ha cambiado (tabla de docs/TESTING.md)
has() { echo "$CHANGED" | grep -qE "$1"; }
if has '\.py$'; then
  run_step syntax-python "Sintaxis de Python" check_python_syntax
  run_step lint-python "Lint de Python (ruff)" check_ruff
  run_step format-python "Formato de Python (ruff)" check_ruff_format
fi
if has '^backend/'; then
  run_step backend "Backend FastAPI (pytest, cobertura 100 %)" check_backend
  run_step qa-python "Contrato de la API y errores" check_qa_python
fi
if has '^frontend/'; then
  run_step frontend-static "JavaScript: sintaxis, imports y recursos" check_frontend_static
  run_step unit-frontend "Tests unitarios del frontend" check_unit_frontend
fi
if has '^frontend/.*\.html$'; then run_step lint-html "Validación HTML" check_lint_html; fi
if has '^frontend/css/'; then run_step lint-css "Validación CSS" check_lint_css; fi
if has '^frontend/js/(python-runner|pyodide-worker|console)\.js$|^frontend/py/|^tests/frontend/'; then
  run_step browser-frontend "Módulos y Web Workers en Chromium" check_browser_frontend
fi
if has '^scripts/qa/|^tests/frontend/|^\.htmlvalidate|^\.stylelintrc'; then
  run_step qa-frontend "Tests del validador del frontend" check_qa_frontend
fi
if has '^(backend/app|frontend/js|frontend/config\.js|render\.yaml|frontend/.*\.html)|^tests/integration/'; then
  run_step integration "Integración frontend-backend" check_integration
fi
if has '^(frontend/|scripts/(learning|curriculum|resources|web)/)'; then
  run_step generated "Contenido generado al día" check_generated
fi
if has '^(backend/app|frontend/.*\.html|backend/requirements|package|\.gitleaks|tests/security/)'; then
  run_step security-tests "Pruebas de seguridad" check_security_tests
fi
run_step gitleaks "Secretos (Gitleaks)" check_gitleaks

# 5. Batería completa antes de integrar
if [ "$FULL" = 1 ]; then
  echo "${C_BOLD}5. Batería completa${C_OFF}"
  QA_APPEND=1 QA_KEEP_GOING=1 bash scripts/qa/pre-push-check.sh --allow-dirty --keep-going >/dev/null
  [ $? -ne 0 ] && QA_FAILED=1
fi

# 6-7. Resultados e informe de validación
"$PY" scripts/qa/report.py --title "Validación de la tarea: $TASK" --output "$QA_REPORT_DIR/task-report.md" --no-actions >/dev/null
verdict="$(sed -n 's/^\*\*Resultado final: \(.*\)\*\*$/\1/p' "$QA_REPORT_DIR/task-report.md" | head -1)"
echo
echo "${C_BOLD}Resultado de la tarea: $verdict${C_OFF} · reports/qa/task-report.md"
[ "$QA_FAILED" = 1 ] && exit 1
exit 0
