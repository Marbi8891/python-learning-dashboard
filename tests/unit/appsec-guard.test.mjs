import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { AREAS, decide, isSecretPath } from "../../.claude/hooks/appsec-guard.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const GUARD = path.join(ROOT, ".claude/hooks/appsec-guard.mjs");
const AGENTS_DIR = path.join(ROOT, ".claude/agents");
const TEAM = [
  "security-lead",
  "security-auditor",
  "auth-security",
  "api-security",
  "frontend-security",
  "dependency-security",
  "security-qa",
  "security-devsecops",
];

const edit = (file) => ({ tool_name: "Edit", tool_input: { file_path: file } });
const bash = (command) => ({ tool_name: "Bash", tool_input: { command } });

test("los ocho agentes existen, con cabecera válida y el guardián con su propio nombre", () => {
  const files = readdirSync(AGENTS_DIR).filter((f) => f.endsWith(".md"));
  assert.deepEqual(files.map((f) => f.replace(/\.md$/, "")).sort(), [...TEAM].sort());
  for (const agent of TEAM) {
    const text = readFileSync(path.join(AGENTS_DIR, `${agent}.md`), "utf8");
    const header = text.match(/^---\n([\s\S]*?)\n---\n/);
    assert.ok(header, `${agent}: falta la cabecera YAML`);
    assert.match(header[1], new RegExp(`^name: ${agent}$`, "m"));
    assert.match(header[1], /^description: .{40,}/m);
    assert.match(header[1], /^tools: /m);
    assert.ok(header[1].includes(`appsec-guard.mjs" ${agent}`), `${agent}: el hook no lleva su nombre`);
    assert.match(text, /## Criterios de finalización/, `${agent}: faltan criterios de finalización`);
    assert.ok(text.length > 1500, `${agent}: instrucciones demasiado cortas`);
  }
  assert.deepEqual(Object.keys(AREAS).sort(), [...TEAM].sort());
});

test("cada agente solo edita su área", () => {
  assert.equal(decide("security-qa", edit("backend/tests/test_x.py"), ROOT), null);
  assert.ok(decide("security-qa", edit("backend/app/main.py"), ROOT).deny);
  assert.equal(decide("api-security", edit("backend/app/routers/dashboard.py"), ROOT), null);
  assert.ok(decide("api-security", edit("backend/app/routers/auth.py"), ROOT).deny);
  assert.equal(decide("auth-security", edit("backend/app/routers/auth.py"), ROOT), null);
  assert.equal(decide("frontend-security", edit(path.join(ROOT, "frontend/index.html")), ROOT), null);
  assert.ok(decide("frontend-security", edit("frontend/data/learning.json"), ROOT).deny);
  assert.ok(decide("frontend-security", edit("frontend/js/api.js"), ROOT).deny);
  assert.ok(decide("security-auditor", edit("docs/security/SECURITY_FINDINGS.md"), ROOT).deny);
  assert.equal(decide("security-lead", edit("docs/security/SECURITY_FINDINGS.md"), ROOT), null);
  assert.equal(decide("security-devsecops", edit(".github/workflows/security.yml"), ROOT), null);
});

test("nadie edita la configuración de agentes, de despliegue ni fuera del repositorio", () => {
  for (const agent of TEAM) {
    for (const file of [".claude/agents/security-lead.md", "CLAUDE.md", "render.yaml", "deploy.ps1"]) {
      assert.ok(decide(agent, edit(file), ROOT).deny, `${agent} podría editar ${file}`);
    }
    assert.ok(decide(agent, edit("/etc/passwd"), ROOT).deny);
  }
  assert.ok(decide("intruso", edit("docs/security/x.md"), ROOT).deny);
});

test("ningún agente lee secretos, pero sí las plantillas", () => {
  for (const file of ["backend/.env", ".env.production", "app.jks", "id.pem", "backend/.local-secret"]) {
    assert.ok(isSecretPath(file), file);
    assert.ok(decide("security-auditor", { tool_name: "Read", tool_input: { file_path: file } }, ROOT).deny);
  }
  assert.equal(isSecretPath("backend/.env.example"), false);
  assert.equal(decide("security-auditor", bash("cat backend/.env.example"), ROOT), null);
  assert.ok(decide("security-auditor", bash("cat backend/.env"), ROOT).deny);
  assert.ok(decide("security-auditor", bash("printenv"), ROOT).deny);
  assert.ok(decide("security-auditor", bash('echo "$JWT_SECRET"'), ROOT).deny);
});

test("bloquea publicar, destruir trabajo y atacar; producción se pregunta", () => {
  for (const command of [
    "git push origin main",
    "git push --force origin security/x",
    "git reset --hard HEAD~1",
    "git clean -fdx",
    "gh pr merge 50",
    "gh secret set JWT",
    "pwsh ./deploy.ps1",
    "rm -rf backend",
    "nmap pld-api.onrender.com",
    "sqlmap -u http://127.0.0.1:8000",
  ]) {
    assert.ok(decide("security-lead", bash(command), ROOT)?.deny, command);
  }
  assert.ok(decide("security-qa", bash("curl -sI https://pld-api.onrender.com/api/v1/health"), ROOT).ask);
  for (const command of ["git push -u origin security/appsec-hardening", "python -m pytest -q", "git status"]) {
    assert.equal(decide("security-lead", bash(command), ROOT), null, command);
  }
});

test("el script real bloquea con código 2 y pregunta con JSON", () => {
  const run = (agent, event) =>
    spawnSync(process.execPath, [GUARD, agent], { input: JSON.stringify(event), encoding: "utf8" });
  const denied = run("security-qa", edit("backend/app/main.py"));
  assert.equal(denied.status, 2);
  assert.match(denied.stderr, /no es del área de security-qa/);
  const asked = run("security-qa", bash("curl https://pld-api.onrender.com/api/v1/health"));
  assert.equal(asked.status, 0);
  assert.equal(JSON.parse(asked.stdout).hookSpecificOutput.permissionDecision, "ask");
  const allowed = run("security-qa", bash("git status"));
  assert.equal(allowed.status, 0);
  assert.equal(allowed.stdout, "");
});
