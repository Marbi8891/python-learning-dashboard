/* Web Worker (tipo módulo): carga Pyodide y ejecuta el runner (frontend/py/runner.py).
   Pyodide 314+ exige workers de tipo módulo: se crea con new Worker(url, { type: "module" }). */

let pyodide = null;

// APIs con las que el código de un Worker puede hablar con otros servidores.
const NETWORK_APIS = [
  "fetch",
  "XMLHttpRequest",
  "WebSocket",
  "WebSocketStream",
  "EventSource",
  "WebTransport",
  "Worker",
  "SharedWorker",
  "importScripts",
  "caches",
];

const blocked = (name) =>
  function blockedApi() {
    throw new DOMException(`${name} no está disponible en la consola de Python`, "SecurityError");
  };

const lock = (target, name) =>
  Object.defineProperty(target, name, { value: blocked(name), writable: false, configurable: false });

/** Cierra la red del Worker antes de ejecutar código del alumno.

    La CSP de la página va en un <meta> y no llega a este Worker (comprobado en Chromium): sin esto,
    un programa pegado en la consola podría enviar datos a cualquier servidor. Python ya está
    cargado y el alumno no necesita red. También se cierran eval y los constructores de funciones,
    porque con ellos se puede escribir import("https://…"), que no se puede sustituir.
    Es defensa en profundidad: la barrera completa sería que el Worker tuviera su propia CSP. */
function closeNetwork() {
  for (const name of NETWORK_APIS) {
    for (let target = self; target && target !== Object.prototype; target = Object.getPrototypeOf(target)) {
      if (Object.prototype.hasOwnProperty.call(target, name)) lock(target, name);
    }
  }
  lock(self, "eval");
  for (const fn of [function () {}, async function () {}, function* () {}, async function* () {}]) {
    lock(Object.getPrototypeOf(fn), "constructor");
  }
  lock(self, "Function");
}

self.onmessage = async ({ data }) => {
  if (data.type === "init") {
    try {
      const { loadPyodide } = await import(`${data.indexURL}pyodide.mjs`);
      pyodide = await loadPyodide({ indexURL: data.indexURL });
      const response = await fetch(data.runnerUrl);
      if (!response.ok) throw new Error(`No se pudo cargar runner.py (HTTP ${response.status})`);
      pyodide.runPython(await response.text());
      closeNetwork();
      self.postMessage({ type: "ready" });
    } catch (error) {
      self.postMessage({ type: "load-error", message: String(error?.message ?? error) });
    }
    return;
  }

  const name = data.type === "run" ? "run_for_js" : "check_for_js";
  const fn = pyodide.globals.get(name);
  try {
    const json = data.type === "run" ? fn(data.code, data.stdin) : fn(data.code, data.cases);
    self.postMessage({ id: data.id, result: JSON.parse(json) });
  } catch (error) {
    self.postMessage({ id: data.id, error: String(error?.message ?? error) });
  } finally {
    fn.destroy();
  }
};
