import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("Mi Carrera en IA está conectada al enrutador y al registro de vistas", () => {
  const app = read("../../frontend/js/app.js");
  const html = read("../../frontend/index.html");

  assert.match(app, /career: \(load\) => load\("\.\/career\/career-app\.js"\)/);
  assert.match(app, /career: \{ element: "#career-view", title: "Mi Carrera en IA/);
  assert.match(app, /location\.hash === CAREER_ROUTE \|\| location\.hash\.startsWith\(\`\$\{CAREER_ROUTE\}\/\`\)/);
  assert.match(html, /id="career-view"/);
  assert.match(html, /href="#\/carrera" data-nav="carrera"/);
});
