# Comprobaciones del entorno QA. Cada función es un paso de run_step (ver lib.sh):
# devuelve 0 (PASS), 1 (FAIL), 77 (SKIP) o 78 (WARN) y escribe su salida en el log del paso.
# La usan pre-push-check.sh, security_scan.sh y claude-task-check.sh: un solo sitio para cada regla.

PROTECTED_BRANCHES="main master develop"
PY="$(qa_python)"

# Rama base con la que se compara: la del PR (GITHUB_BASE_REF), QA_BASE, o develop si existe, si no main
qa_base_ref() {
  local base="${QA_BASE:-${GITHUB_BASE_REF:-}}"
  if [ -z "$base" ]; then
    if git rev-parse --verify -q origin/develop >/dev/null; then base=develop; else base=main; fi
  fi
  if git rev-parse --verify -q "origin/$base" >/dev/null; then echo "origin/$base"
  elif git rev-parse --verify -q "$base" >/dev/null; then echo "$base"
  else echo ""
  fi
}

# 1. Rama actual
check_branch() {
  local branch
  branch="$(git symbolic-ref --short -q HEAD)" || { echo "QA-DETAIL: HEAD separado (detached): no hay rama que subir"; return 1; }
  echo "Rama: $branch"
  for p in $PROTECTED_BRANCHES; do
    if [ "$branch" = "$p" ]; then
      echo "QA-DETAIL: estás en «$branch»: a $branch solo se llega con un pull request (docs/GIT_WORKFLOW.md)"
      return 1
    fi
  done
  if ! [[ "$branch" =~ ^[a-z0-9]+/[A-Za-z0-9._-]+$ ]]; then
    echo "QA-DETAIL: «$branch» no sigue el formato tipo/descripcion"
    return 1
  fi
  if ! [[ "$branch" =~ ^(feature|fix|test)/ ]]; then
    echo "WARN: «$branch» es válida, pero el flujo QA usa feature/, fix/ o test/ (docs/GIT_WORKFLOW.md)"
    return 78
  fi
}

# 2. Sin cambios inesperados (todo lo que se sube está en commits)
check_clean_tree() {
  local status
  status="$(git status --porcelain --untracked-files=all)"
  if [ -n "$status" ]; then
    echo "$status"
    if [ "${QA_ALLOW_DIRTY:-0}" = "1" ]; then
      echo "WARN: $(echo "$status" | wc -l | tr -d ' ') archivos sin commit (se revisan, pero no se subirían con el push)"
      return 78
    fi
    echo "QA-DETAIL: $(echo "$status" | wc -l | tr -d ' ') archivos con cambios sin commit o sin añadir"
    return 1
  fi
  echo "Árbol de trabajo limpio"
}

# 9. Conflictos de Git: marcas sin resolver, rutas sin fusionar y choque con la rama base
check_conflicts() {
  local rc=0 base markers
  if [ -n "$(git ls-files -u)" ]; then
    git ls-files -u
    echo "QA-DETAIL: hay archivos sin fusionar (merge o rebase a medias)"
    return 1
  fi
  markers="$(git grep -nE '^(<<<<<<<|>>>>>>>)( |$)|^=======$' -- ':!*.md' ':!*.rst' 2>/dev/null)"
  if [ -n "$markers" ]; then
    echo "$markers"
    echo "QA-DETAIL: marcas de conflicto en $(echo "$markers" | cut -d: -f1 | sort -u | paste -sd ' ' -)"
    rc=1
  fi
  base="$(qa_base_ref)"
  if [ -z "$base" ]; then
    echo "WARN: no hay rama base (origin/develop ni origin/main) para comprobar conflictos"
    [ "$rc" = 0 ] && return 78
    return "$rc"
  fi
  if [ "${QA_NO_FETCH:-0}" != "1" ] && [ -z "${CI:-}" ]; then
    git fetch --quiet origin "${base#origin/}" 2>/dev/null || echo "Aviso: no se pudo actualizar $base (sin red); se usa la copia local"
  fi
  if git merge-tree --write-tree "$base" HEAD >/tmp/qa-merge-tree.$$ 2>&1; then
    echo "Sin conflictos con $base"
  else
    cat /tmp/qa-merge-tree.$$
    echo "QA-DETAIL: la rama choca con $base en: $(grep -E '^CONFLICT' /tmp/qa-merge-tree.$$ | sed -E 's/.*conflict in //' | paste -sd ' ' -)"
    rc=1
  fi
  rm -f /tmp/qa-merge-tree.$$
  return "$rc"
}

# 8. Archivos modificados respecto a la base: lista, pruebas borradas o saltadas, JSON generados a mano
check_changed_files() {
  local base range files rc=0 warn=0
  base="$(qa_base_ref)"
  if [ -z "$base" ]; then echo "SKIP: sin rama base con la que comparar"; return 77; fi
  range="$(git merge-base "$base" HEAD)"
  echo "Cambios respecto a $base ($(git rev-parse --short "$range")):"
  git diff --name-status "$range" HEAD
  git status --porcelain --untracked-files=all | sed 's/^/(sin commit) /'
  files="$( { git diff --name-only "$range" HEAD; git diff --name-only HEAD; git ls-files --others --exclude-standard; } | sort -u)"
  [ -z "$files" ] && { echo "No hay archivos modificados"; return 0; }

  # Pruebas borradas
  local deleted
  deleted="$(git diff --name-status --diff-filter=D "$range" HEAD | awk '{print $2}' | grep -E '^(tests|backend/tests|e2e)/' || true)"
  if [ -n "$deleted" ]; then
    echo "QA-DETAIL: el cambio BORRA pruebas: $(echo "$deleted" | paste -sd ' ' -)"
    rc=1
  fi
  # Pruebas saltadas o limitadas con .only en las líneas añadidas. Un skip condicional legítimo
  # (por ejemplo, «sin red hacia el CDN») lleva en la misma línea el comentario
  # «qa-allow-skip: <motivo>», que queda a la vista en la revisión del PR.
  local skipped
  skipped="$( { git diff "$range" HEAD -- tests backend/tests e2e; git diff HEAD -- tests backend/tests e2e; } 2>/dev/null \
    | grep -E '^\+' | grep -vE '^\+\+\+' \
    | grep -nE '(@pytest\.mark\.(skip|xfail)\b|pytest\.skip\(|\b(test|it|describe)\.(skip|only|fixme)\(|\bxit\(|--cov-fail-under=[0-9]{1,2}\b)' \
    | grep -v 'qa-allow-skip:' || true)"
  if [ -n "$skipped" ]; then
    echo "$skipped"
    echo "QA-DETAIL: el cambio añade skip/only/xfail o baja la cobertura exigida en las pruebas"
    rc=1
  fi
  # JSON generados de frontend/data editados sin tocar su script (CLAUDE.md)
  if echo "$files" | grep -qE '^frontend/data/.*\.json$' && ! echo "$files" | grep -qE '^scripts/(learning|courses|curriculum|resources)/'; then
    echo "QA-DETAIL: cambia un JSON generado de frontend/data sin cambiar su script: $(echo "$files" | grep -E '^frontend/data/' | paste -sd ' ' -)"
    rc=1
  fi
  # Avisos: workflows, dependencias y archivos grandes
  if echo "$files" | grep -qE '^\.github/workflows/'; then echo "WARN: cambian workflows de GitHub Actions: revísalos a mano"; warn=1; fi
  if echo "$files" | grep -qE '(^|/)(requirements[^/]*\.txt|package(-lock)?\.json)$'; then echo "WARN: cambian dependencias"; warn=1; fi
  while IFS= read -r f; do
    if [ -f "$f" ] && [ "$(wc -c <"$f")" -gt 1048576 ]; then echo "WARN: $f ocupa más de 1 MB"; warn=1; fi
  done <<<"$files"
  echo "Total: $(echo "$files" | wc -l | tr -d ' ') archivos"
  [ "$rc" != 0 ] && return "$rc"
  [ "$warn" = 1 ] && return 78
  return 0
}

# 3. Sintaxis
check_python_syntax() { "$PY" -m compileall -q backend/app backend/migrations scripts e2e tests >/dev/null && echo "Python: sintaxis correcta"; }
check_ruff() {
  # Misma regla que ci.yml, con las carpetas nuevas (tests/) incluidas
  (cd backend && "$PY" -m ruff check . ../e2e ../scripts ../tests)
}
check_ruff_format() { (cd backend && "$PY" -m ruff format --check . ../e2e ../scripts ../tests); }
check_frontend_static() { node --experimental-vm-modules --disable-warning=ExperimentalWarning scripts/qa/frontend_static.mjs --json "$QA_REPORT_DIR/frontend-static.json"; }
check_lint_html() { require_cmd npx "Node 22" || return $?; npx --no-install html-validate "frontend/*.html" && echo "HTML válido"; }
check_lint_css() { require_cmd npx "Node 22" || return $?; npx --no-install stylelint "frontend/css/*.css" && echo "CSS válido"; }

# 4. Frontend
check_unit_frontend() { npm run -s test:unit; }
check_qa_frontend() { npm run -s test:frontend; }
check_browser_frontend() {
  if ! node -e 'const {chromium}=require("@playwright/test");require("fs").accessSync(chromium.executablePath())' 2>/dev/null; then
    echo "SKIP: Chromium de Playwright no instalado (npx playwright install chromium)"
    return 77
  fi
  npx --no-install playwright test -c tests/frontend
}

# 5. Backend
check_backend() { (cd backend && "$PY" -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=100); }
check_qa_python() { "$PY" -m pytest -q tests/backend; }

# 6. Integración
check_integration() { "$PY" -m pytest -q tests/integration; }
check_generated() {
  local rc=0
  "$PY" scripts/learning/build_learning.py --check || rc=1
  "$PY" scripts/curriculum/build_curriculum.py --check || rc=1
  "$PY" scripts/resources/build_resources.py --check || rc=1
  node scripts/web/build_precache.mjs --check || rc=1
  return "$rc"
}
check_e2e() { npm run -s test:e2e; }

# 7. Seguridad
check_security_tests() { "$PY" -m pytest -q tests/security; }
check_pip_audit() {
  "$PY" -m pip_audit --version >/dev/null 2>&1 || { echo "SKIP: pip-audit no instalado (pip install pip-audit)"; return 77; }
  local rc=0
  "$PY" -m pip_audit -r backend/requirements.txt -f json -o "$QA_REPORT_DIR/pip-audit.json" --progress-spinner off || rc=1
  "$PY" -m pip_audit -r backend/requirements.txt --progress-spinner off || true
  # Herramientas de desarrollo: se informa, pero no llegan a producción
  if ! "$PY" -m pip_audit -r backend/requirements-dev.txt --progress-spinner off; then
    [ "$rc" = 0 ] && { echo "WARN: vulnerabilidad en una dependencia de desarrollo (no llega a producción)"; return 78; }
  fi
  return "$rc"
}
check_npm_audit() {
  npm audit --json >"$QA_REPORT_DIR/npm-audit.json" 2>/dev/null || true
  npm audit --audit-level=high
}
check_bandit() {
  "$PY" -m bandit --version >/dev/null 2>&1 || { echo "SKIP: Bandit no instalado (pip install bandit)"; return 77; }
  "$PY" -m bandit -q -r backend/app -f json -o "$QA_REPORT_DIR/bandit.json" --exit-zero
  # La API (lo que se despliega) no puede tener hallazgos de severidad media o alta
  local rc=0
  "$PY" -m bandit -q -r backend/app -ll || rc=1
  # Scripts de build: se ejecutan en local o en CI con datos propios; sus avisos se revisan, no bloquean
  echo "--- scripts/ (informativo) ---"
  "$PY" -m bandit -q -r scripts -ll --exit-zero | grep -E '^>> Issue|Location' || true
  return "$rc"
}
check_gitleaks() {
  local bin="${GITLEAKS:-gitleaks}"
  command -v "$bin" >/dev/null 2>&1 || { echo "SKIP: gitleaks no instalado (ver docs/QA_GUIDE.md); en CI se ejecuta siempre"; return 77; }
  local rc=0 base
  "$bin" dir --no-banner --redact --config .gitleaks.toml --report-format json --report-path "$QA_REPORT_DIR/gitleaks-dir.json" . || rc=1
  base="$(qa_base_ref)"
  if [ -n "$base" ]; then
    # Commits de esta rama que aún no están en la base: lo que se va a subir
    "$bin" git --no-banner --redact --config .gitleaks.toml --log-opts="$base..HEAD" \
      --report-format json --report-path "$QA_REPORT_DIR/gitleaks-git.json" . || rc=1
  fi
  return "$rc"
}
