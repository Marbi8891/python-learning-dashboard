#!/usr/bin/env node
// Guardián del equipo AppSec (docs/security/AGENT_WORKFLOW.md).
//
// Hook PreToolUse que cada agente de .claude/agents/ declara en su cabecera:
//   node "$CLAUDE_PROJECT_DIR/.claude/hooks/appsec-guard.mjs" <agente>
//
// `tools:` limita herramientas, pero no rutas (docs/AGENTS.md §2). Este script:
//   1. bloquea leer o mostrar secretos (.env, claves, keystores, backend/.local-secret);
//   2. solo deja editar las rutas del área del agente (AREAS);
//   3. bloquea comandos destructivos o de publicación (push a main, force, merge, deploy.ps1…);
//   4. bloquea escáneres y pruebas de carga, y pide confirmación antes de tocar producción.
//
// Salida: código 2 + motivo en stderr = bloqueado. JSON con permissionDecision "ask" = preguntar
// a la persona. Sin salida = el hook no decide y siguen valiendo los permisos normales.
// Si Node no está instalado el hook no puede ejecutarse y no bloquea nada: la última barrera
// sigue siendo Git (rama, diff revisado, CI y merge humano).

import { readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Rutas que cada agente puede crear o editar (relativas a la raíz del repositorio).
// «!» excluye. Ningún agente edita .claude/**, CLAUDE.md, render.yaml, Docker ni deploy.ps1.
export const AREAS = {
  "security-lead": ["docs/security/**", "SECURITY.md", "docs/SECURITY.md"],
  "security-auditor": [],
  "auth-security": [
    "backend/app/routers/auth.py",
    "backend/app/routers/account.py",
    "backend/app/security.py",
    "backend/app/session_cookie.py",
    "backend/app/rate_limit.py",
    "backend/app/password_policy.py",
    "backend/app/security_events.py",
    "backend/app/deps.py",
    "frontend/js/account.js",
    "frontend/js/api.js",
    "frontend/js/private.js",
    "backend/tests/test_auth.py",
    "backend/tests/test_google_auth.py",
    "backend/tests/test_session_cookie.py",
    "backend/tests/test_password_reset.py",
    "backend/tests/test_account.py",
    "backend/tests/test_my_account.py",
    "backend/tests/test_hardening.py",
    "backend/tests/test_attack_detection.py",
    "backend/tests/test_security_isolation.py",
    "e2e/account.spec.js",
  ],
  "api-security": [
    "backend/app/**",
    "!backend/app/routers/auth.py",
    "!backend/app/routers/account.py",
    "!backend/app/security.py",
    "!backend/app/session_cookie.py",
    "!backend/app/password_policy.py",
    "backend/migrations/versions/**",
    "backend/tests/**",
  ],
  "frontend-security": [
    "frontend/**",
    "!frontend/data/**",
    "!frontend/vendor/**",
    "!frontend/js/account.js",
    "!frontend/js/api.js",
    "!frontend/js/private.js",
    "!frontend/config.js",
    "tests/unit/**",
    "e2e/security.spec.js",
  ],
  "dependency-security": [
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
    "package.json",
    "package-lock.json",
    ".gitignore",
    ".gitleaks.toml",
    ".gitleaksignore",
  ],
  "security-qa": ["backend/tests/**", "tests/unit/**", "e2e/**"],
  "security-devsecops": [
    ".github/workflows/**",
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
    ".semgrep/**",
    "scripts/security/**",
  ],
};

// Nadie, ni siquiera dentro de su área, toca la configuración de los agentes ni la de despliegue
const NEVER_EDIT = [
  ".claude/**",
  "CLAUDE.md",
  ".mcp.json",
  "render.yaml",
  "docker-compose.yml",
  "backend/Dockerfile",
  "deploy.ps1",
  "frontend/config.js",
  ".git/**",
];

const SECRET_FILE =
  /(^|[\\/\s"'=])(\.env(\.(?!example\b)[\w.-]+)?|[\w.-]+\.(jks|keystore|p12|pem|key)|\.local-secret)(?=$|[\s"'|;&)>])/i;

// Comandos que nunca ejecuta un agente: destruyen trabajo, publican o tocan secretos
const DENIED_COMMANDS = [
  [/\bgit\s+push\b[^|;&]*\s(-f\b|--force\b|--force-with-lease\b|\+)/, "git push forzado"],
  [/\bgit\s+push\b[^|;&]*(\s|:|refs\/heads\/)main(?=\s|$|[;&|])/, "push a main (publica la web)"],
  [/\bgit\s+reset\s+--hard\b/, "git reset --hard"],
  [/\bgit\s+clean\b/, "git clean"],
  [/\bgit\s+checkout\s+(--\s+)?\.(\s|$)/, "descartar cambios con git checkout ."],
  [/\bgit\s+restore\b[^|;&]*\s\.(\s|$)/, "descartar cambios con git restore ."],
  [/\bgit\s+branch\s+-D\b/, "borrar ramas"],
  [/\bgit\s+(filter-branch|filter-repo)\b/, "reescribir historia"],
  [/\bgh\s+pr\s+merge\b/, "hacer merge (publica la web)"],
  [/\bgh\s+(secret|variable)\b/, "tocar secretos o variables de GitHub"],
  [/\bgh\s+release\b/, "publicar una release"],
  [/\bgh\s+repo\s+(delete|edit)\b/, "cambiar el repositorio"],
  [/\bgh\s+api\b[^|;&]*(-X|--method)\s*(PUT|PATCH|DELETE|POST)\b/i, "escribir con la API de GitHub"],
  [/deploy\.ps1/i, "desplegar"],
  [/\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r/i, "rm -rf"],
  [/(^|[\s;&|(])(printenv|env|set|export\s+-p)\s*($|[|;&>])/, "volcar variables de entorno"],
  [/\$\{?[A-Z0-9_]*(SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE)[A-Z0-9_]*\}?/, "mostrar un secreto"],
  [
    /\b(nmap|masscan|sqlmap|nikto|hydra|medusa|wfuzz|ffuf|gobuster|dirb|dirbuster|zap|zaproxy|nuclei|wpscan|ab|wrk|hey|siege|locust|vegeta|slowloris)\b/,
    "escáner, fuerza bruta o prueba de carga",
  ],
];

// Producción: cualquier acceso lo confirma la persona (nunca DoS ni escaneos)
const PRODUCTION = /(pld-api\.onrender\.com|marbi8891\.github\.io|api\.render\.com|dashboard\.render\.com|neon\.tech)/i;

const EDIT_TOOLS = new Set(["Edit", "Write", "MultiEdit", "NotebookEdit"]);
const READ_TOOLS = new Set(["Read", "Grep", "Glob"]);

function globToRegExp(glob) {
  let re = "";
  for (let i = 0; i < glob.length; i += 1) {
    const c = glob[i];
    if (c === "*" && glob[i + 1] === "*") {
      re += ".*";
      i += 1;
    } else if (c === "*") re += "[^/]*";
    else if (c === "?") re += "[^/]";
    else re += c.replace(/[.+^${}()|[\]\\]/g, "\\$&");
  }
  return new RegExp(`^${re}$`);
}

export function matches(patterns, rel) {
  let allowed = false;
  for (const pattern of patterns) {
    const negated = pattern.startsWith("!");
    if (globToRegExp(negated ? pattern.slice(1) : pattern).test(rel)) allowed = !negated;
  }
  return allowed;
}

function relative(root, file) {
  const absolute = path.resolve(root, file);
  return { absolute, rel: path.relative(root, absolute).split(path.sep).join("/") };
}

const isInside = (rel) => rel !== "" && !rel.startsWith("..") && !path.isAbsolute(rel);

export function isSecretPath(file) {
  const name = String(file).split(/[\\/]/).pop();
  return SECRET_FILE.test(` ${name}`) || /(^|[\\/])backend[\\/]\.local-secret$/.test(file);
}

/** Decide sobre una llamada. Devuelve null (no decide), {deny: motivo} o {ask: motivo}. */
export function decide(agent, event, root) {
  const tool = event.tool_name;
  const input = event.tool_input ?? {};

  if (!(agent in AREAS)) return { deny: `agente desconocido para el guardián: «${agent}»` };

  if (READ_TOOLS.has(tool) || EDIT_TOOLS.has(tool)) {
    const target = input.file_path ?? input.notebook_path ?? input.path ?? "";
    if (target && isSecretPath(target)) {
      return { deny: `«${target}» puede contener secretos y ningún agente lo lee ni lo edita` };
    }
    if (tool === "Grep" && input.glob && isSecretPath(input.glob)) {
      return { deny: "no se buscan contenidos dentro de archivos de secretos" };
    }
  }

  if (EDIT_TOOLS.has(tool)) {
    const target = input.file_path ?? input.notebook_path;
    if (!target) return { deny: "edición sin ruta" };
    const { absolute, rel } = relative(root, target);
    if (!isInside(rel)) {
      const scratch = path.relative(tmpdir(), absolute);
      if (!scratch.startsWith("..") && !path.isAbsolute(scratch)) return null; // borradores temporales
      return { deny: `«${target}» está fuera del repositorio` };
    }
    if (matches(NEVER_EDIT, rel)) {
      return { deny: `«${rel}» es configuración de agentes o de despliegue: solo la cambia una persona` };
    }
    if (!matches(AREAS[agent], rel)) {
      return {
        deny: `«${rel}» no es del área de ${agent}. Devuelve el cambio propuesto a security-lead para que lo asigne a su dueño (docs/security/AGENT_WORKFLOW.md)`,
      };
    }
    return null;
  }

  if (tool === "Bash") {
    const command = String(input.command ?? "");
    for (const [pattern, label] of DENIED_COMMANDS) {
      if (pattern.test(command)) return { deny: `comando bloqueado para los agentes AppSec: ${label}` };
    }
    if (SECRET_FILE.test(` ${command}`) && !/\.env\.example\b/.test(command)) {
      return { deny: "el comando nombra un archivo de secretos; usa .env.example o pregunta a la persona" };
    }
    if (PRODUCTION.test(command)) {
      return { ask: "el comando accede a producción; solo lecturas pasivas y con autorización expresa" };
    }
    return null;
  }

  if (tool === "WebFetch" && PRODUCTION.test(String(input.url ?? ""))) {
    return { ask: "petición a producción; solo lecturas pasivas y con autorización expresa" };
  }
  return null;
}

function main() {
  const agentArg = process.argv[2];
  let event;
  try {
    event = JSON.parse(readFileSync(0, "utf8") || "{}");
  } catch {
    process.stderr.write("appsec-guard: entrada no válida\n");
    process.exit(2);
  }
  const agent = agentArg || event.agent_type;
  const root = process.env.CLAUDE_PROJECT_DIR || event.cwd || process.cwd();
  const verdict = decide(agent, event, root);
  if (verdict?.deny) {
    process.stderr.write(`appsec-guard: ${verdict.deny}\n`);
    process.exit(2);
  }
  if (verdict?.ask) {
    process.stdout.write(
      JSON.stringify({
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "ask",
          permissionDecisionReason: `appsec-guard: ${verdict.ask}`,
        },
      }),
    );
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
