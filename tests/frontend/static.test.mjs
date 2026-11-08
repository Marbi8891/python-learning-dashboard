// Validación estática del frontend (scripts/qa/frontend_static.mjs).
// 1) La web real no tiene errores.  2) Cada comprobación detecta el fallo que dice detectar,
// sobre una copia mínima de la web en una carpeta temporal (no se toca frontend/).
// Ejecutar: npm run test:frontend
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { after, test } from "node:test";

import { checkFrontend } from "../../scripts/qa/frontend_static.mjs";

const dirs = [];
after(() => dirs.forEach((d) => rmSync(d, { recursive: true, force: true })));

/** Web mínima válida; `files` sobrescribe o añade archivos. */
function site(files = {}) {
  const root = mkdtempSync(path.join(tmpdir(), "pld-qa-"));
  dirs.push(root);
  const base = {
    "index.html":
      '<!doctype html><html lang="es"><head><link rel="canonical" href="https://example.org/pld/">' +
      '<link rel="stylesheet" href="css/app.css"><script src="config.js"></script>' +
      '<script type="module" src="js/app.js"></script></head><body></body></html>',
    "config.js": "window.PLD_CONFIG = {};",
    "css/app.css": "body { color: red; }",
    "js/package.json": '{ "type": "module" }',
    "js/app.js": 'import { helper } from "./util.js";\nhelper();',
    "js/util.js": "export function helper() {}",
    ...files,
  };
  for (const [name, content] of Object.entries(base)) {
    if (content === null) continue;
    mkdirSync(path.dirname(path.join(root, name)), { recursive: true });
    writeFileSync(path.join(root, name), content);
  }
  return root;
}

const checks = (result) => result.errors.map((e) => e.check);

test("la web real (frontend/) pasa la validación estática sin errores", async () => {
  const result = await checkFrontend();
  assert.deepEqual(result.errors, [], JSON.stringify(result.errors, null, 2));
  assert.ok(result.stats.modules > 10, "debe recorrer el grafo de módulos de app.js");
  assert.ok(result.stats.imports > 50);
});

test("una web mínima correcta no da errores", async () => {
  const result = await checkFrontend(site());
  assert.deepEqual(result.errors, []);
});

test("detecta un error de sintaxis y dice la línea", async () => {
  const result = await checkFrontend(site({ "js/util.js": "export function helper() {\n  return (1;\n}" }));
  const err = result.errors.find((e) => e.check === "js-syntax");
  assert.ok(err, JSON.stringify(result.errors));
  assert.match(err.file, /js\/util\.js$/);
  assert.equal(err.line, 2);
});

test("detecta un import de un módulo que no existe", async () => {
  const result = await checkFrontend(site({ "js/app.js": 'import { helper } from "./utils.js";' }));
  assert.deepEqual(checks(result), ["js-missing-import"]);
  assert.match(result.errors[0].file, /js\/app\.js$/);
});

test("detecta un import sin extensión .js (el navegador no la añade)", async () => {
  const result = await checkFrontend(site({ "js/app.js": 'import { helper } from "./util";' }));
  assert.deepEqual(checks(result), ["js-missing-import"]);
});

test("detecta un nombre importado que el módulo no exporta", async () => {
  const result = await checkFrontend(site({ "js/app.js": 'import { helpr } from "./util.js";\nhelpr();' }));
  assert.deepEqual(checks(result), ["js-missing-export"]);
  assert.match(result.errors[0].message, /helpr/);
  assert.match(result.errors[0].file, /js\/app\.js$/);
});

test("detecta un especificador de paquete sin import map", async () => {
  const result = await checkFrontend(site({ "js/app.js": 'import confetti from "canvas-confetti";' }));
  assert.deepEqual(checks(result), ["js-bare-specifier"]);
});

test("detecta un import() dinámico a un archivo que no existe", async () => {
  const result = await checkFrontend(site({ "js/app.js": 'export const load = () => import("./lazy.js");' }));
  assert.deepEqual(checks(result), ["js-missing-import"]);
});

test("detecta un Web Worker que no existe", async () => {
  const code = 'new Worker(new URL("./worker.js", import.meta.url), { type: "module" });';
  const result = await checkFrontend(site({ "js/app.js": code }));
  assert.deepEqual(checks(result), ["worker-missing"]);
});

test("detecta un Worker con import creado sin type: module", async () => {
  const result = await checkFrontend(
    site({
      "js/app.js": 'new Worker(new URL("./worker.js", import.meta.url));',
      "js/worker.js": 'import { helper } from "./util.js";\nhelper();',
    }),
  );
  assert.ok(checks(result).includes("worker-type"), JSON.stringify(result.errors));
});

test("detecta referencias rotas en HTML, CSS y manifiesto", async () => {
  const result = await checkFrontend(
    site({
      "index.html":
        '<!doctype html><html><head><link rel="canonical" href="https://example.org/pld/">' +
        '<link rel="stylesheet" href="/pld/css/missing.css"><link rel="manifest" href="app.webmanifest">' +
        '<script type="module" src="js/app.js"></script></head><body><img src="img/logo.png" alt=""></body></html>',
      "css/app.css": "@font-face { font-family: X; src: url(../fonts/nope.woff2); }",
      "app.webmanifest": '{ "icons": [{ "src": "icons/192.png" }] }',
    }),
  );
  const found = checks(result);
  assert.equal(found.filter((c) => c === "html-missing-reference").length, 2, JSON.stringify(result.errors));
  assert.ok(found.includes("css-missing-reference"));
  assert.ok(found.includes("manifest-missing-reference"));
});

test("las rutas absolutas con la base de GitHub Pages se resuelven bien", async () => {
  const html =
    '<!doctype html><html><head><link rel="canonical" href="https://example.org/pld/">' +
    '<link rel="stylesheet" href="/pld/css/app.css"></head><body><a href="/pld/#/x">x</a></body></html>';
  const result = await checkFrontend(site({ "404.html": html }));
  assert.deepEqual(result.errors, []);
});

test("detecta scripts inline y manejadores on* que la CSP bloquearía", async () => {
  const result = await checkFrontend(
    site({
      "privacidad.html":
        '<!doctype html><html><body><button onclick="go()">x</button><script>go()</script>' +
        '<script type="application/ld+json">{"@type":"WebSite"}</script></body></html>',
    }),
  );
  assert.deepEqual(checks(result).sort(), ["html-inline-handler", "html-inline-script"]);
});

test("detecta un JSON roto y una ruta de datos que no existe", async () => {
  const result = await checkFrontend(
    site({
      "data/lessons.json": '{ "a": 1, }',
      "js/util.js": 'export function helper() { return fetch("data/lesons.json"); }',
    }),
  );
  assert.deepEqual(checks(result).sort(), ["js-missing-resource", "json-invalid"]);
});

test("un archivo JS que nadie carga es una advertencia, no un error", async () => {
  const result = await checkFrontend(site({ "js/old.js": "export const x = 1;" }));
  assert.deepEqual(result.errors, []);
  assert.deepEqual(
    result.warnings.map((w) => w.check),
    ["js-unreferenced"],
  );
});
