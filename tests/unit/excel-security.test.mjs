// Motor de fórmulas: seguridad, límites y rendimiento (P-SEG-01, P-SEG-03, P-REN-01, P-REN-02).
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { checkFormula } from "../../frontend/js/excel/checks.js";
import { evaluate, parseFormula } from "../../frontend/js/excel/formula/index.js";

const EXCEL = fileURLToPath(new URL("../../frontend/js/excel/", import.meta.url));

function files(folder) {
  return readdirSync(folder).flatMap((name) => {
    const path = join(folder, name);
    return statSync(path).isDirectory() ? files(path) : [path];
  });
}

test("el motor no usa eval, Function ni código en texto", () => {
  for (const file of files(EXCEL)) {
    const source = readFileSync(file, "utf8");
    for (const banned of ["eval(", "new Function", "Function(", 'setTimeout("', "setTimeout('", "innerHTML +="]) {
      assert.ok(!source.includes(banned), `${file} contiene ${banned}`);
    }
  }
});

test("el motor pesa menos de 60 KB sin minificar", () => {
  const formula = files(join(EXCEL, "formula"));
  const bytes = formula.reduce((total, file) => total + statSync(file).size, 0);
  assert.ok(bytes < 60 * 1024, `${bytes} bytes`);
});

test("límites de ejecución: rango enorme, presupuesto de pasos y ciclos", () => {
  assert.equal(evaluate(parseFormula("=SUMA(A1:CV101)")).value, "LÍMITE"); // 100 × 101 celdas
  assert.equal(evaluate(parseFormula("=SUMA(A1:CV100)")).value, 0); // 10 000 celdas: dentro del límite
  const costly = evaluate(parseFormula("=SUMA(A1:A9000)+SUMA(A1:A9000)"), { environment: { limits: { maxSteps: 10000 } } });
  assert.equal(costly.value, "LÍMITE");
  assert.match(costly.message, /demasiado costosa/);
  assert.equal(evaluate(parseFormula("=A1"), { grid: { A1: { f: "=B1" }, B1: { f: "=A1" } } }).value, "CICLO");
  assert.equal(evaluate(parseFormula("=A1"), { grid: { A1: { f: "=A1+1" } } }).value, "CICLO");
});

test("un texto con <script> es solo un texto", () => {
  const result = evaluate(parseFormula('="<script>alert(1)</script>"&A1'), { grid: { A1: "<img onerror=x>" } });
  assert.deepEqual(result, { type: "text", value: "<script>alert(1)</script><img onerror=x>" });
});

test("comprobar un ejercicio con copia de 500 celdas tarda menos de 50 ms (p95)", () => {
  const grid = Object.fromEntries(Array.from({ length: 500 }, (_, i) => [`B${i + 2}`, i * 3.5]));
  grid.E1 = 0.21;
  const question = { id: "perf", grid, cell: "D2", checks: [{ type: "value" }, { type: "fill", to: "D501" }], expect: 0, solution: { formula: "=B2*$E$1" } };
  const times = [];
  for (let i = 0; i < 20; i += 1) {
    const start = performance.now();
    assert.equal(checkFormula(question, "=B2*$E$1").ok, true);
    times.push(performance.now() - start);
  }
  times.sort((a, b) => a - b);
  const p95 = times[Math.ceil(times.length * 0.95) - 1];
  assert.ok(p95 < 50, `p95 = ${p95.toFixed(1)} ms`);
});
