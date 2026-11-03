/* Ejecuta Python en un Web Worker con Pyodide.

   - El Worker evita que un bucle largo congele la página.
   - Si el código tarda más que timeoutMs (por ejemplo, un bucle infinito),
     se destruye el Worker y la siguiente ejecución lo vuelve a crear.
   - stop() hace lo mismo a petición del alumno (botón «Detener»): un Worker ocupado en un bucle
     no atiende mensajes, así que la única forma fiable de pararlo es terminarlo. */

export const PYODIDE_VERSION = "314.0.7";
const DEFAULT_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// Con conexión lenta la primera descarga (unos 10 MB) puede tardar minutos: a los 20 s se avisa
// de que sigue descargando y a los 5 min se abandona con un error que se puede reintentar.
export const SLOW_LOAD_MS = 20_000;
export const LOAD_TIMEOUT_MS = 300_000;
const PYODIDE_CACHE = "pld-pyodide"; // la misma caché que sw.js

export class TimeoutError extends Error {}
export class StoppedError extends Error {}

/** ¿Está ya Python guardado en este navegador? Sirve para no anunciar una descarga que no habrá. */
export async function isPythonCached(indexURL = DEFAULT_INDEX_URL) {
  try {
    if (typeof caches === "undefined") return false;
    const cache = await caches.open(PYODIDE_CACHE);
    return (await cache.keys()).some((request) => request.url.startsWith(indexURL) && request.url.endsWith(".wasm"));
  } catch {
    return false;
  }
}

export class PythonRunner {
  constructor({ indexURL, timeoutMs = 10_000, onStatus = () => {}, slowLoadMs = SLOW_LOAD_MS, loadTimeoutMs = LOAD_TIMEOUT_MS } = {}) {
    this.indexURL = indexURL || DEFAULT_INDEX_URL;
    this.timeoutMs = timeoutMs;
    this.slowLoadMs = slowLoadMs;
    this.loadTimeoutMs = loadTimeoutMs;
    this.onStatus = onStatus;
    this.worker = null;
    this.ready = null;
    this.pending = new Map();
    this.nextId = 0;
  }

  /** true mientras hay una ejecución o una comprobación en curso. */
  get busy() {
    return this.pending.size > 0;
  }

  /** Detiene lo que se esté ejecutando. Devuelve false si no había nada que detener. */
  stop() {
    if (!this.busy) return false;
    for (const job of this.pending.values()) {
      clearTimeout(job.timer);
      job.reject(new StoppedError("Has detenido el programa."));
    }
    this.pending.clear();
    this.#reset();
    this.onStatus("idle");
    return true;
  }

  run(code, stdin = "") {
    return this.#call({ type: "run", code, stdin });
  }

  check(code, cases) {
    return this.#call({ type: "check", code, cases: JSON.stringify(cases) });
  }

  #start() {
    if (this.ready) return this.ready;
    this.onStatus("loading");
    this.worker = new Worker(new URL("./pyodide-worker.js", import.meta.url), { type: "module" });
    this.ready = new Promise((resolve, reject) => {
      this.loadTimers = [
        setTimeout(() => this.onStatus("slow-loading"), this.slowLoadMs),
        setTimeout(
          () => reject(new Error("Python no ha terminado de descargarse. Comprueba tu conexión y vuelve a intentarlo.")),
          this.loadTimeoutMs,
        ),
      ];
      this.worker.onmessage = ({ data }) => {
        if (data.type === "ready") resolve();
        else if (data.type === "load-error") reject(new Error(data.message));
        else this.#settle(data);
      };
      this.worker.onerror = (event) => reject(new Error(event.message || "No se pudo iniciar Python"));
    });
    this.worker.postMessage({
      type: "init",
      indexURL: this.indexURL,
      runnerUrl: new URL("../py/runner.py", import.meta.url).href,
    });
    const ready = this.ready;
    ready.then(
      () => {
        this.#clearLoadTimers();
        this.onStatus("ready");
      },
      () => {
        // Solo si sigue siendo esta carga: si el alumno pulsó Detener, ya hay otro Worker o ninguno
        if (this.ready !== ready) return;
        this.onStatus("error");
        this.#reset();
      },
    );
    return this.ready;
  }

  async #call(message) {
    // El trabajo cuenta como pendiente desde el principio, también mientras Pyodide se carga,
    // para que «Detener» funcione en cualquier momento
    const id = ++this.nextId;
    const job = { timer: null };
    const done = new Promise((resolve, reject) => Object.assign(job, { resolve, reject }));
    this.pending.set(id, job);
    // Si se detiene durante la carga, el Worker se destruye y #start() no termina nunca: gana `done`
    await Promise.race([this.#start(), done]).catch((error) => {
      this.pending.delete(id);
      throw error;
    });
    job.timer = setTimeout(() => {
      this.pending.delete(id);
      this.#reset();
      this.onStatus("idle");
      job.reject(new TimeoutError(`Tu programa ha tardado más de ${this.timeoutMs / 1000} s y se ha detenido.`));
    }, this.timeoutMs);
    this.worker.postMessage({ ...message, id });
    return done;
  }

  #settle({ id, result, error }) {
    const job = this.pending.get(id);
    if (!job) return;
    clearTimeout(job.timer);
    this.pending.delete(id);
    if (error) job.reject(new Error(error));
    else job.resolve(result);
  }

  #clearLoadTimers() {
    for (const timer of this.loadTimers ?? []) clearTimeout(timer);
    this.loadTimers = [];
  }

  #reset() {
    this.#clearLoadTimers();
    this.worker?.terminate();
    this.worker = null;
    this.ready = null;
    for (const job of this.pending.values()) {
      clearTimeout(job.timer);
      job.reject(new Error("Python se ha reiniciado"));
    }
    this.pending.clear();
  }
}
