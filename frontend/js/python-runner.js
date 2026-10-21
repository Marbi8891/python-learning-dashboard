/* Ejecuta Python en un Web Worker con Pyodide.

   - El Worker evita que un bucle largo congele la página.
   - Si el código tarda más que timeoutMs (por ejemplo, un bucle infinito),
     se destruye el Worker y la siguiente ejecución lo vuelve a crear. */

export const PYODIDE_VERSION = "314.0.7";
const DEFAULT_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

export class TimeoutError extends Error {}
/** El alumno ha pulsado «Detener»: no es un fallo de su código ni de Python. */
export class StoppedError extends Error {}

export class PythonRunner {
  constructor({ indexURL, timeoutMs = 10_000, onStatus = () => {} } = {}) {
    this.indexURL = indexURL || DEFAULT_INDEX_URL;
    this.timeoutMs = timeoutMs;
    this.onStatus = onStatus;
    this.worker = null;
    this.ready = null;
    this.pending = new Map();
    this.nextId = 0;
  }

  run(code, stdin = "") {
    return this.#call({ type: "run", code, stdin });
  }

  check(code, cases) {
    return this.#call({ type: "check", code, cases: JSON.stringify(cases) });
  }

  /** ¿Hay alguna ejecución o comprobación en marcha? */
  get busy() {
    return this.pending.size > 0;
  }

  /**
   * Detiene lo que se esté ejecutando: destruye el Worker (la única forma de cortar un bucle en
   * Pyodide sin SharedArrayBuffer) y la siguiente ejecución lo vuelve a crear con Python limpio.
   * Devuelve false si no había nada que detener.
   */
  stop() {
    if (!this.busy) return false;
    this.#reset(new StoppedError("Has detenido el programa. Python se ha reiniciado."));
    this.onStatus("idle");
    return true;
  }

  #start() {
    if (this.ready) return this.ready;
    this.onStatus("loading");
    this.worker = new Worker(new URL("./pyodide-worker.js", import.meta.url), { type: "module" });
    this.ready = new Promise((resolve, reject) => {
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
    this.ready.then(
      () => this.onStatus("ready"),
      () => {
        this.onStatus("error");
        this.#reset();
      },
    );
    return this.ready;
  }

  async #call(message) {
    await this.#start();
    return new Promise((resolve, reject) => {
      const id = ++this.nextId;
      const timer = setTimeout(() => {
        this.pending.delete(id);
        this.#reset();
        this.onStatus("idle");
        reject(new TimeoutError(`Tu programa ha tardado más de ${this.timeoutMs / 1000} s y se ha detenido.`));
      }, this.timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      this.worker.postMessage({ ...message, id });
    });
  }

  #settle({ id, result, error }) {
    const job = this.pending.get(id);
    if (!job) return;
    clearTimeout(job.timer);
    this.pending.delete(id);
    if (error) job.reject(new Error(error));
    else job.resolve(result);
  }

  #reset(reason = new Error("Python se ha reiniciado")) {
    this.worker?.terminate();
    this.worker = null;
    this.ready = null;
    for (const job of this.pending.values()) {
      clearTimeout(job.timer);
      job.reject(reason);
    }
    this.pending.clear();
  }
}
