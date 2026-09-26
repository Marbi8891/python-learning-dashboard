/* Web Worker (tipo módulo): carga Pyodide y ejecuta el runner (frontend/py/runner.py).
   Pyodide 314+ exige workers de tipo módulo: se crea con new Worker(url, { type: "module" }). */

let pyodide = null;

self.onmessage = async ({ data }) => {
  if (data.type === "init") {
    try {
      const { loadPyodide } = await import(`${data.indexURL}pyodide.mjs`);
      pyodide = await loadPyodide({ indexURL: data.indexURL });
      const response = await fetch(data.runnerUrl);
      if (!response.ok) throw new Error(`No se pudo cargar runner.py (HTTP ${response.status})`);
      pyodide.runPython(await response.text());
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
