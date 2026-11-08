#!/usr/bin/env bash
# Análisis de seguridad: pruebas de seguridad, pip-audit, npm audit, Bandit y Gitleaks.
# Lo usan security.yml (CI) y pre-push-check.sh (que llama a las mismas funciones de checks.sh).
#
#   bash scripts/qa/security_scan.sh               # se detiene en el primer fallo
#   bash scripts/qa/security_scan.sh --keep-going  # ejecuta todo y deja el informe completo
#
# Los resultados (sin valores de secretos: Gitleaks va con --redact) quedan en reports/qa/.
set -u
source "$(dirname "$0")/lib.sh"
cd "$QA_ROOT" || exit 1
source "$QA_ROOT/scripts/qa/checks.sh"
[ "${1:-}" = "--keep-going" ] && QA_KEEP_GOING=1

qa_init
finish() {
  "$PY" scripts/qa/report.py --title "Análisis de seguridad" --output "$QA_REPORT_DIR/security-report.md" >/dev/null 2>&1
  echo "Informe: reports/qa/security-report.md"
  [ "$QA_FAILED" = 1 ] && exit 1
  exit 0
}
step() { run_step "$@" || finish; }

step security-tests "Pruebas de seguridad (CSP, secretos, autorización, entradas)" check_security_tests
step pip-audit "Dependencias de Python (pip-audit)" check_pip_audit
step npm-audit "Dependencias de npm (npm audit)" check_npm_audit
step bandit "Análisis estático (Bandit)" check_bandit
step gitleaks "Secretos (Gitleaks)" check_gitleaks
finish
