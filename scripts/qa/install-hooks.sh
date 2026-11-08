#!/usr/bin/env bash
# Instala el hook pre-push de Git: cada `git push` ejecuta antes scripts/qa/pre-push-check.sh y
# se cancela si falla. Es local (no se sube a GitHub). Para quitarlo: rm .git/hooks/pre-push
#   bash scripts/qa/install-hooks.sh
set -eu
root="$(git rev-parse --show-toplevel)"
hook="$(git rev-parse --git-path hooks)/pre-push"
if [ -e "$hook" ] && ! grep -q "scripts/qa/pre-push-check.sh" "$hook"; then
  echo "Ya hay un hook pre-push propio en $hook: no se sobrescribe. Añade a mano:"
  echo '  bash scripts/qa/pre-push-check.sh --hook || exit 1'
  exit 1
fi
cat >"$hook" <<'HOOK'
#!/usr/bin/env bash
# Instalado por scripts/qa/install-hooks.sh: valida la rama antes de subirla.
# Bloquear también el push directo a ramas protegidas, aunque las pruebas pasen
while read -r _local_ref _local_sha remote_ref _remote_sha; do
  case "$remote_ref" in
    refs/heads/main|refs/heads/master|refs/heads/develop)
      echo "Push directo a ${remote_ref#refs/heads/} bloqueado: abre un pull request (docs/GIT_WORKFLOW.md)."
      exit 1 ;;
  esac
done
cd "$(git rev-parse --show-toplevel)" && bash scripts/qa/pre-push-check.sh --hook
HOOK
chmod +x "$hook"
echo "Hook instalado en $hook (raíz: $root)"
