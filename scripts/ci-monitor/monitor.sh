#!/usr/bin/env bash
# Vigila en tu equipo las ejecuciones de GitHub Actions de un commit hasta que terminan.
#
#   scripts/ci-monitor/monitor.sh            # el último commit de la rama actual (después de git push)
#   scripts/ci-monitor/monitor.sh <sha>      # otro commit
#
# Necesita GitHub CLI con sesión iniciada (gh auth login) y Python 3.
# Solo lee: no hace commits, ni push, ni relanza nada. Sale con 0 si todo pasó y con 1 si algo falló
# (y entonces muestra el diagnóstico de cada job fallido). Detalles: docs/CI_CD_MONITORING.md.
set -euo pipefail

REPO="${REPO:-Marbi8891/python-learning-dashboard}"
SHA="${1:-$(git rev-parse HEAD)}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(command -v python3 || command -v python)"

gh auth status >/dev/null 2>&1 || { echo "GitHub CLI no tiene sesión: ejecuta «gh auth login»." >&2; exit 2; }

echo "SUBIDA DETECTADA"
echo "Commit: ${SHA:0:7} · Rama: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"

# Las ejecuciones tardan unos segundos en aparecer después del push
runs=""
for _ in $(seq 1 30); do
  runs="$(gh run list --repo "$REPO" --commit "$SHA" --json databaseId,workflowName --jq '.[] | "\(.databaseId) \(.workflowName)"')"
  [ -n "$runs" ] && break
  sleep 10
done
[ -n "$runs" ] || { echo "No hay ejecuciones de GitHub Actions para ${SHA:0:7} después de 5 minutos." >&2; exit 2; }

status=0
while read -r id name; do
  echo
  echo "CI EN EJECUCIÓN · $name · ejecución $id"
  if gh run watch "$id" --repo "$REPO" --exit-status --interval 30 >/dev/null; then
    echo "$name: SUCCESS"
  else
    status=1
    conclusion="$(gh run view "$id" --repo "$REPO" --json conclusion --jq .conclusion)"
    echo "$name: $(echo "$conclusion" | tr "[:lower:]" "[:upper:]")"
    [ "$conclusion" = "cancelled" ] && continue
    gh run view "$id" --repo "$REPO" --json jobs \
      --jq '.jobs[] | select(.conclusion == "failure") | "\(.databaseId)\t\(.name)\t\([.steps[] | select(.conclusion == "failure") | .name][0] // "")"' |
      while IFS=$'\t' read -r job_id job step; do
        log="$(mktemp)"
        gh run view --repo "$REPO" --job "$job_id" --log-failed >"$log" 2>/dev/null || gh run view --repo "$REPO" --job "$job_id" --log >"$log"
        echo
        echo "ERROR DETECTADO · job $job · paso «$step»"
        "$PYTHON" "$HERE/ci_monitor.py" diagnose --log-file "$log" --job "$job" --step "$step"
        rm -f "$log"
      done
  fi
  echo "Resumen: $(gh run view "$id" --repo "$REPO" --json jobs --jq '[.jobs[] | "\(.name): \(.conclusion // .status)"] | join(" · ")')"
done <<<"$runs"

echo
if [ "$status" -eq 0 ]; then echo "RESULTADO FINAL: GITHUB CI/CD SUCCESS · commit ${SHA:0:7}"; else echo "RESULTADO FINAL: hay fallos · commit ${SHA:0:7}"; fi
exit "$status"
