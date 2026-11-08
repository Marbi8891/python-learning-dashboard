#!/usr/bin/env bash
# Validación completa antes de subir una rama (docs/QA_GUIDE.md).
#
#   bash scripts/qa/pre-push-check.sh            # todo menos las e2e (unos 2-3 min)
#   bash scripts/qa/pre-push-check.sh --e2e      # también las e2e completas (más lento)
#   bash scripts/qa/pre-push-check.sh --keep-going   # no se detiene en el primer fallo (informe completo)
#   bash scripts/qa/pre-push-check.sh --allow-dirty  # cambios sin commit: aviso en vez de fallo
#   bash scripts/qa/pre-push-check.sh --hook     # modo hook de Git (lo usa .git/hooks/pre-push)
#
# Sale con 0 si todo pasa (o solo hay avisos) y con 1 si algo falla. Siempre deja el informe en
# reports/qa/latest-report.md. Nunca hace push, merge ni cambia archivos del repositorio.
set -u

source "$(dirname "$0")/lib.sh"
cd "$QA_ROOT" || exit 1
source "$QA_ROOT/scripts/qa/checks.sh"

RUN_E2E=0
for arg in "$@"; do
  case "$arg" in
    --e2e) RUN_E2E=1 ;;
    --keep-going) QA_KEEP_GOING=1 ;;
    --allow-dirty) export QA_ALLOW_DIRTY=1 ;;
    --hook) : ;;  # mismo comportamiento: se detiene en el primer fallo y bloquea el push
    --no-fetch) export QA_NO_FETCH=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $arg"; exit 2 ;;
  esac
done

qa_init
echo "${C_BOLD}Validación QA · $(git symbolic-ref --short -q HEAD || echo HEAD) · $(git rev-parse --short HEAD)${C_OFF}"

finish() {
  "$PY" scripts/qa/report.py --title "Validación antes del push" >/dev/null 2>&1 \
    || echo "No se pudo generar el informe (scripts/qa/report.py)"
  local verdict
  verdict="$(sed -n 's/^\*\*Resultado final: \(.*\)\*\*$/\1/p' "$QA_REPORT_DIR/latest-report.md" 2>/dev/null | head -1)"
  echo
  echo "${C_BOLD}Resultado: ${verdict:-desconocido}${C_OFF} · informe en reports/qa/latest-report.md"
  if [ "$QA_FAILED" = 1 ]; then
    echo "${C_RED}No se puede subir: corrige el fallo y vuelve a ejecutar este script.${C_OFF}"
    exit 1
  fi
  exit 0
}
step() { run_step "$@" || finish; }

# 1-2. Git: rama y árbol de trabajo
step branch "Rama actual" check_branch
step clean-tree "Sin cambios inesperados" check_clean_tree
# 9. Conflictos (antes de gastar tiempo en tests)
step conflicts "Conflictos de Git" check_conflicts
# 8. Archivos modificados
step changed-files "Archivos modificados" check_changed_files
# 3. Sintaxis y estilo
step syntax-python "Sintaxis de Python" check_python_syntax
step lint-python "Lint de Python (ruff)" check_ruff
step format-python "Formato de Python (ruff)" check_ruff_format
step frontend-static "JavaScript: sintaxis, imports y recursos" check_frontend_static
step lint-html "Validación HTML" check_lint_html
step lint-css "Validación CSS" check_lint_css
# 4. Frontend
step unit-frontend "Tests unitarios del frontend" check_unit_frontend
step qa-frontend "Tests del validador del frontend" check_qa_frontend
step browser-frontend "Módulos y Web Workers en Chromium" check_browser_frontend
# 5. Backend
step backend "Backend FastAPI (pytest, cobertura 100 %)" check_backend
step qa-python "Contrato de la API y errores" check_qa_python
# 6. Integración
step integration "Integración frontend-backend" check_integration
step generated "Contenido generado al día" check_generated
if [ "$RUN_E2E" = 1 ]; then step e2e "End-to-end (Playwright)" check_e2e; fi
# 7. Seguridad
step security-tests "Pruebas de seguridad" check_security_tests
step pip-audit "Dependencias de Python (pip-audit)" check_pip_audit
step npm-audit "Dependencias de npm (npm audit)" check_npm_audit
step bandit "Análisis estático (Bandit)" check_bandit
step gitleaks "Secretos (Gitleaks)" check_gitleaks
# 10. Informe
finish
