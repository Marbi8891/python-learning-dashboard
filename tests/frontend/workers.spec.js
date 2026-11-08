// Web Workers y Pyodide en un navegador real (Chromium).
//  - Con un Pyodide de mentira (fixtures/fake-pyodide): siempre, sin red. Prueban el protocolo del
//    Worker (init → ready → run/check), la carga de runner.py y que la red del Worker queda cerrada.
//  - Con el Pyodide real: solo si se puede descargar (PYODIDE_URL o acceso a cdn.jsdelivr.net).
//    Si no, la prueba sale como «skipped» con el motivo; nunca como superada.
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { test, expect } = require("@playwright/test");

const FAKE = "/__qa__/fake-pyodide/";
const fakeSource = readFileSync(path.join(__dirname, "fixtures", "fake-pyodide", "pyodide.mjs"), "utf8");

// Página vacía del mismo origen que la web: así el módulo y el Worker se cargan como en producción,
// pero sin el resto de la app (sin CSP de <meta>, que no aplica a los Workers: ver pyodide-worker.js)
async function blankPage(page) {
  await page.route("**/__qa__/blank.html", (route) =>
    route.fulfill({ contentType: "text/html", body: "<!doctype html><title>QA</title>" }),
  );
  await page.route(`**${FAKE}pyodide.mjs`, (route) =>
    route.fulfill({ contentType: "text/javascript", body: fakeSource }),
  );
  await page.goto("/__qa__/blank.html");
}

test("los módulos principales de la web se cargan en el navegador sin errores", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await blankPage(page);
  const loaded = await page.evaluate(async () => {
    const names = ["js/python-runner.js", "js/srs.js", "js/markdown.js", "js/learn/mastery.js", "js/learn/planner.js"];
    const out = {};
    for (const name of names) out[name] = Object.keys(await import(`/${name}`)).length;
    return out;
  });
  for (const [name, exports] of Object.entries(loaded)) expect(exports, name).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});

test("el Worker de Python arranca, ejecuta y devuelve el resultado (Pyodide simulado)", async ({ page }) => {
  await blankPage(page);
  const result = await page.evaluate(async (fake) => {
    const { PythonRunner } = await import("/js/python-runner.js");
    const statuses = [];
    const runner = new PythonRunner({ indexURL: location.origin + fake, onStatus: (s) => statuses.push(s) });
    const run = await runner.run("print(1)", "entrada");
    const check = await runner.check("def f(): pass", [{ args: [] }, { args: [1] }]);
    runner.worker.terminate();
    return { run, check, statuses };
  }, FAKE);
  expect(result.statuses).toEqual(["loading", "ready"]);
  expect(result.run.stdout).toBe("eco:print(1)|entrada");
  expect(result.run.runnerLoaded, "runner.py se descarga y se ejecuta al iniciar").toBe(true);
  expect(result.check).toEqual({ passed: 2, code: "def f(): pass" });
});

test("el Worker cierra la red y eval antes de ejecutar código del alumno", async ({ page }) => {
  await blankPage(page);
  const run = await page.evaluate(async (fake) => {
    const { PythonRunner } = await import("/js/python-runner.js");
    const runner = new PythonRunner({ indexURL: location.origin + fake });
    const out = await runner.run("x", "");
    runner.worker.terminate();
    return out;
  }, FAKE);
  expect(run).toMatchObject({ fetch: "SecurityError", eval: "SecurityError", importScripts: "SecurityError" });
  expect(run.Function).not.toBe("permitido");
});

test("un error de Python llega como error y el Worker sigue disponible", async ({ page }) => {
  await blankPage(page);
  const out = await page.evaluate(async (fake) => {
    const { PythonRunner } = await import("/js/python-runner.js");
    const runner = new PythonRunner({ indexURL: location.origin + fake });
    let message = null;
    try {
      await runner.check("boom", []);
    } catch (error) {
      message = error.message;
    }
    const after = await runner.run("ok", "");
    runner.worker.terminate();
    return { message, after: after.stdout };
  }, FAKE);
  expect(out.message).toBe("fallo de Python simulado");
  expect(out.after).toBe("eco:ok|");
});

test("si Pyodide no se puede descargar, el error se muestra y se puede reintentar", async ({ page }) => {
  await blankPage(page);
  await page.route("**/__qa__/missing-pyodide/**", (route) => route.fulfill({ status: 404, body: "" }));
  const out = await page.evaluate(async () => {
    const { PythonRunner } = await import("/js/python-runner.js");
    const statuses = [];
    const runner = new PythonRunner({ indexURL: `${location.origin}/__qa__/missing-pyodide/`, onStatus: (s) => statuses.push(s) });
    try {
      await runner.run("print(1)");
      return { ok: true };
    } catch (error) {
      return { ok: false, message: error.message, statuses, worker: runner.worker };
    }
  });
  expect(out.ok).toBe(false);
  expect(out.message).toBeTruthy();
  expect(out.statuses).toEqual(["loading", "error"]);
  expect(out.worker, "el Worker roto se descarta para poder reintentar").toBeNull();
});

test("Python real (Pyodide) ejecuta código en el Worker", async ({ page }) => {
  test.setTimeout(180_000);
  const { PYODIDE_VERSION } = await import("../../frontend/js/python-runner.js").catch(() => ({}));
  const indexURL = process.env.PYODIDE_URL || `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION ?? "314.0.7"}/full/`;
  let reachable = false;
  try {
    reachable = (await fetch(`${indexURL}pyodide.mjs`, { method: "HEAD", signal: AbortSignal.timeout(8000) })).ok;
  } catch {
    reachable = false;
  }
  // qa-allow-skip: sin red hacia el CDN no se puede probar Pyodide real; sale como «skipped», no como superada
  test.skip(!reachable, `Pyodide no accesible en ${indexURL} (define PYODIDE_URL para servirlo en local)`); // qa-allow-skip: sin red
  await blankPage(page);
  const out = await page.evaluate(async (url) => {
    const { PythonRunner } = await import("/js/python-runner.js");
    const runner = new PythonRunner({ indexURL: url, timeoutMs: 60_000 });
    const result = await runner.run("print(sum(range(10)))", "");
    runner.worker.terminate();
    return result;
  }, indexURL);
  expect(JSON.stringify(out)).toContain("45");
});
