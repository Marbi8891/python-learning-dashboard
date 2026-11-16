// Estrategia de frontend/sw.js para los archivos de la web: primero la red y, sin conexión o si la red
// tarda (MWG-06), la copia guardada. Se ejecuta sw.js en un contexto aislado con caches y fetch simulados.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

const SOURCE = readFileSync(new URL("../../frontend/sw.js", import.meta.url), "utf8");
const ORIGIN = "https://example.test";

/** Carga sw.js con una caché en memoria y el fetch indicado. Devuelve cómo disparar un evento fetch. */
function loadServiceWorker(fetchImpl, { timers = { setTimeout } } = {}) {
  const stored = new Map();
  const cache = {
    match: async (request) => stored.get(typeof request === "string" ? `${ORIGIN}/${request}` : request.url),
    put: async (request, response) => void stored.set(request.url, response),
    add: async () => {},
    addAll: async () => {},
  };
  const listeners = {};
  const self = {
    location: { origin: ORIGIN },
    addEventListener: (type, fn) => (listeners[type] = fn),
    skipWaiting: () => {},
    clients: { claim: async () => {} },
  };
  const context = vm.createContext({
    self,
    importScripts: () => {},
    caches: { open: async () => cache, keys: async () => [], delete: async () => true },
    fetch: fetchImpl,
    Response: { error: () => ({ type: "error" }) },
    URL,
    Promise,
    setTimeout: timers.setTimeout,
  });
  vm.runInContext(SOURCE, context);
  const dispatch = (url, mode = "cors") => {
    let responded;
    const waits = [];
    listeners.fetch({
      request: { method: "GET", url, mode },
      respondWith: (promise) => (responded = promise),
      waitUntil: (promise) => waits.push(promise),
    });
    return { response: responded, done: Promise.all(waits) };
  };
  return { dispatch, stored };
}

const ok = (body) => ({ ok: true, body, clone: () => ok(body) });

test("con red, responde la red y guarda la copia", async () => {
  const sw = loadServiceWorker(async () => ok("nueva"));
  const { response, done } = sw.dispatch(`${ORIGIN}/js/app.js`);
  assert.equal((await response).body, "nueva");
  await done;
  assert.equal(sw.stored.get(`${ORIGIN}/js/app.js`).body, "nueva");
});

test("sin conexión, responde la copia guardada", async () => {
  const sw = loadServiceWorker(async () => {
    throw new TypeError("Failed to fetch");
  });
  sw.stored.set(`${ORIGIN}/js/app.js`, ok("guardada"));
  assert.equal((await sw.dispatch(`${ORIGIN}/js/app.js`).response).body, "guardada");
});

test("si la red tarda, responde la copia sin esperarla y la red actualiza la copia después (MWG-06)", async () => {
  let finish;
  const slow = new Promise((resolve) => (finish = resolve));
  const pending = [];
  // Temporizador manual: el tiempo límite «pasa» cuando la prueba lo decide
  const timers = { setTimeout: (fn) => pending.push(fn) };
  const sw = loadServiceWorker(() => slow, { timers });
  sw.stored.set(`${ORIGIN}/js/app.js`, ok("guardada"));
  const { response, done } = sw.dispatch(`${ORIGIN}/js/app.js`);
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(pending.length, 1, "se programa el tiempo límite");
  pending[0]();
  assert.equal((await response).body, "guardada");
  finish(ok("nueva"));
  await done;
  assert.equal(sw.stored.get(`${ORIGIN}/js/app.js`).body, "nueva");
});

test("si la red tarda y no hay copia, se sigue esperando a la red", async () => {
  let finish;
  const pending = [];
  const sw = loadServiceWorker(() => new Promise((resolve) => (finish = resolve)), { timers: { setTimeout: (fn) => pending.push(fn) } });
  const { response } = sw.dispatch(`${ORIGIN}/data/lessons.json`);
  await new Promise((resolve) => setImmediate(resolve));
  pending[0]();
  finish(ok("red"));
  assert.equal((await response).body, "red");
});

test("una navegación sin conexión y sin su copia abre index.html", async () => {
  const sw = loadServiceWorker(async () => {
    throw new TypeError("Failed to fetch");
  });
  sw.stored.set(`${ORIGIN}/index.html`, ok("index"));
  assert.equal((await sw.dispatch(`${ORIGIN}/`, "navigate").response).body, "index");
});
