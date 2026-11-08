// Pyodide de mentira para probar el Web Worker sin descargar los 10 MB reales (ni depender de la red).
// Imita la parte de la API que usa frontend/js/pyodide-worker.js: loadPyodide, runPython y globals.get.
// Cada función devuelve JSON, como run_for_js / check_for_js de frontend/py/runner.py.
export async function loadPyodide({ indexURL }) {
  let runnerSource = "";
  const probe = (fn) => {
    try {
      fn();
      return "permitido";
    } catch (error) {
      return error?.name ?? "error";
    }
  };
  const functions = {
    // El "programa" se ejecuta DESPUÉS de cerrar la red del Worker: así se comprueba el cierre
    run_for_js: (code, stdin) =>
      JSON.stringify({
        stdout: `eco:${code}|${stdin}`,
        indexURL,
        runnerLoaded: runnerSource.includes("def run_for_js"),
        fetch: probe(() => self.fetch("https://example.org/")),
        eval: probe(() => self.eval("1")),
        Function: probe(() => new Function("return 1")),
        importScripts: probe(() => self.importScripts("https://example.org/x.js")),
      }),
    check_for_js: (code, cases) => {
      if (code.includes("boom")) throw new Error("fallo de Python simulado");
      return JSON.stringify({ passed: JSON.parse(cases).length, code });
    },
  };
  return {
    runPython(source) {
      runnerSource = source;
    },
    globals: {
      get(name) {
        const fn = (...args) => functions[name](...args);
        fn.destroy = () => {};
        return fn;
      },
    },
  };
}
