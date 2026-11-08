#!/usr/bin/env bash
# Un paso del entorno QA dentro de GitHub Actions, con el mismo código que en local:
#   bash scripts/qa/ci-step.sh <id> "<nombre>" <función de checks.sh>
# Añade su resultado a reports/qa/results.jsonl (el informe final los junta) y sale con 1 si falla.
set -u
export QA_APPEND=1 QA_KEEP_GOING=0
source "$(dirname "$0")/lib.sh"
cd "$QA_ROOT" || exit 1
source "$QA_ROOT/scripts/qa/checks.sh"
qa_init
run_step "$@"
