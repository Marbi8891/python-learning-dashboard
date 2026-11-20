// PLD-004: con el Python de verdad del navegador (Pyodide, el mismo paquete de npm que se publica),
// un ejercicio no contamina los siguientes. Las mismas pruebas, con más detalle, están en CPython en
// backend/tests/test_runner_isolation.py; aquí se comprueba que en Pyodide también se cumplen.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { before, test } from "node:test";
import { loadPyodide } from "pyodide";

let pyodide;
let runFn;
let checkFn;

before(async () => {
  pyodide = await loadPyodide();
  pyodide.runPython(readFileSync(new URL("../../frontend/py/runner.py", import.meta.url), "utf8"));
  runFn = pyodide.globals.get("run_for_js");
  checkFn = pyodide.globals.get("check_for_js");
});

const run = (code, stdin = "") => {
  const result = JSON.parse(runFn(code, stdin));
  assert.equal(result.restart, false, "la restauración no debería fallar");
  return result;
};
const outputOf = (code) => {
  const result = run(code);
  assert.equal(result.error, null, result.error);
  return result.output;
};

test("math.sqrt cambiado en una ejecución funciona bien en la siguiente", () => {
  run("import math\nmath.sqrt = lambda x: 999");
  assert.equal(outputOf("import math\nprint(math.sqrt(16))"), "4.0\n");
});

test("funciones integradas, sys.path, sys.meta_path y sys.modules vuelven a su estado", () => {
  run(
    "import builtins, sys\nbuiltins.len = None\nsys.path.clear()\n" +
      "class Rompe:\n    def find_spec(self, *a):\n        raise ImportError('roto')\n" +
      "sys.meta_path.insert(0, Rompe())\nsys.modules['falso'] = type(sys)('falso')",
  );
  assert.equal(outputOf("import sys, statistics\nprint(len(sys.path) > 0, 'falso' in sys.modules)"), "True False\n");
});

test("clases y funciones de la biblioteca estándar se restauran; las del alumno conservan sus cambios", () => {
  run("import json, textwrap\njson.JSONEncoder.default = lambda s, o: 'X'\ntextwrap.dedent.__code__ = (lambda t: 'roto').__code__");
  const code = "import json, textwrap\ntry:\n    json.dumps(object())\nexcept TypeError:\n    print('TypeError')\nprint(textwrap.dedent('  a'))";
  assert.equal(outputOf(code), "TypeError\na\n");

  const student = "class C:\n    n = 0\n\nC.n = 5";
  const result = JSON.parse(checkFn(student, JSON.stringify([{ test: "assert C.n == 5" }])));
  assert.equal(result.passed, true, result.message);
});

test("los archivos de una ejecución no llegan a la siguiente ni tapan módulos", () => {
  // En Pyodide sys.path empieza por '' (la carpeta actual): un random.py del alumno taparía al de verdad
  run("open('random.py', 'w').write('x = 1')\nopen('notas.txt', 'w').write('hola')");
  assert.equal(outputOf("import os, sys\nsys.modules.pop('random', None)\nimport random\nprint(os.path.exists('notas.txt'), hasattr(random, 'randint'))"), "False True\n");
});

test("tras un error, exit() o un RecursionError el intérprete también queda limpio", () => {
  for (const ending of ["1 / 0", "exit()", "def f():\n    f()\nf()"]) {
    run(`import math, sys\nmath.pi = 3\nsys.setrecursionlimit(80)\n${ending}`);
    assert.equal(outputOf("import math, sys\nprint(math.pi > 3.1, sys.getrecursionlimit())"), "True 1000\n");
  }
});

test("aislar una ejecución cuesta milisegundos, no los segundos de recargar Pyodide", () => {
  const rounds = 20;
  const start = performance.now();
  for (let i = 0; i < rounds; i++) run("x = sum(range(1000))\nprint(x)");
  const average = (performance.now() - start) / rounds;
  // Medido: ~8 ms por ejecución frente a ~2 000 ms de cargar Pyodide (docs/AISLAMIENTO_PYTHON.md)
  assert.ok(average < 150, `cada ejecución tarda ${average.toFixed(1)} ms`);
});
