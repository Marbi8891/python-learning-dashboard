// Corrección de los ejercicios de fórmulas (P-UNI-07), con los ejemplos de
// docs/excel-academy/CURRICULUM_M1_M2.md: la solución pasa y cada error frecuente falla.
import assert from "node:assert/strict";
import { test } from "node:test";

import { checkFormula, checkResult, parseAnswer, variantGrid, verifyQuestion } from "../../frontend/js/excel/checks.js";

const IVA = {
  id: "xl1-ref-07",
  kind: "formula",
  grid: { B1: "Base", B2: 100, B3: 250, B4: 80, B5: 40, B6: 1000, D1: "IVA", E1: 0.21 },
  cell: "D2",
  expect: 21,
  checks: [
    { type: "value" },
    { type: "fill", to: "D6", expect: [52.5, 16.8, 8.4, 210] },
    { type: "variants", count: 2 },
    { type: "references", must: ["B2", "$E$1"] },
    { type: "noConstants" },
  ],
  hints: ["Si copias =B2*E1 hacia abajo, ¿qué pasa con E1?"],
  solution: { formula: "=B2*$E$1" },
  mistakes: [{ error: "=B2*E1" }, { error: "=B2*0,21" }],
};

const TABLA = {
  id: "xl1-ref-10",
  kind: "formula",
  grid: { A2: 1, A3: 2, A4: 3, B1: 1, C1: 2, D1: 3 },
  cell: "B2",
  expect: 1,
  checks: [{ type: "value" }, { type: "fill", to: "D4", expect: [2, 3, 2, 4, 6, 3, 6, 9] }],
  hints: ["Fija la columna de A y la fila 1."],
  solution: { formula: "=$A2*B$1" },
  mistakes: [{ error: "=A2*B1" }, { error: "=$A$2*$B$1" }],
};

const REDONDEO = {
  id: "xl2-con-11",
  kind: "formula",
  grid: { B2: 19.99, B3: 7.4, B4: 133.33, E1: 0.21 },
  cell: "C2",
  expect: 4.2,
  tolerance: 0.0001,
  checks: [{ type: "value" }, { type: "fill", to: "C4", expect: [1.55, 28] }, { type: "functions", requires: ["ROUND"] }],
  hints: ["REDONDEAR(número;2)"],
  solution: { formula: "=REDONDEAR(B2*$E$1;2)" },
  mistakes: [{ error: "=B2*$E$1" }, { error: "=REDONDEAR(B2*E1;2)" }],
};

const HOJAS = {
  id: "xl2-hoj-08",
  kind: "formula",
  sheet: "Resumen",
  grid: { "Enero!B5": 4200, "Febrero!B5": 3900, "Marzo!B5": 4650 },
  cell: "B2",
  expect: 12750,
  checks: [{ type: "value" }, { type: "variants" }],
  hints: ["Hoja!Celda"],
  solution: { formula: "=Enero!B5+Febrero!B5+Marzo!B5" },
  mistakes: [{ error: "=B5+B5+B5" }],
};

test("los ejercicios del currículo están bien hechos", () => {
  for (const q of [IVA, TABLA, REDONDEO, HOJAS]) assert.deepEqual(verifyQuestion(q), [], q.id);
});

test("la solución y sus variantes correctas pasan; los errores frecuentes no", () => {
  assert.equal(checkFormula(IVA, "=B2*$E$1").ok, true);
  assert.equal(checkFormula(IVA, "=$E$1*B2").ok, true); // el orden no importa
  assert.equal(checkFormula(IVA, " =b2*$e$1 ").ok, true);
  const relative = checkFormula(IVA, "=B2*E1");
  assert.equal(relative.ok, false);
  assert.match(relative.message, /Al copiarla, en D3 da 0 y debería dar 52,5/);
  assert.equal(checkFormula(IVA, "=B2*0,21").results.find((r) => !r.ok).type, "variants");
  assert.equal(checkFormula(IVA, "=21").ok, false);
  assert.equal(checkFormula(TABLA, "=A2*B1").ok, false);
  assert.equal(checkFormula(TABLA, "=$A2*B$1").ok, true);
  assert.equal(checkFormula(REDONDEO, "=B2*$E$1").ok, false);
  assert.match(checkFormula(REDONDEO, "=B2*$E$1").message, /4,1979/);
  assert.equal(checkFormula(HOJAS, "=SUMA(Enero!B5;Febrero!B5;Marzo!B5)").ok, true);
  assert.equal(checkFormula(HOJAS, "=B5+B5+B5").ok, false);
});

test("las comprobaciones de procedimiento: referencias, números a mano y funciones", () => {
  const procedure = { ...IVA, checks: [{ type: "references", must: ["$E$1"], mustNot: ["E2"] }, { type: "noConstants", except: [1] }] };
  assert.match(checkFormula(procedure, "=B2*E1").message, /tiene que usar \$E\$1 \(fija la celda con \$/);
  assert.match(checkFormula(procedure, "=B2*$E$1+E2").message, /no debería usar E2/);
  assert.match(checkFormula(procedure, "=B2*$E$1*2").message, /número escrito a mano en la fórmula \(2\)/);
  assert.equal(checkFormula(procedure, "=B2*$E$1*1").ok, true);
  const fn = { ...IVA, checks: [{ type: "functions", requires: ["SUM"], forbid: ["PRODUCT"] }] };
  assert.match(checkFormula(fn, "=B2", { spanishName: () => "SUMA" }).message, /se resuelve con SUMA/);
  assert.match(checkFormula(fn, "=SUMA(PRODUCTO(B2;1))", { spanishName: () => "PRODUCTO" }).message, /no se usa PRODUCTO/);
  const custom = { ...IVA, checks: [{ type: "value", message: "Mira el tipo de IVA." }] };
  assert.equal(checkFormula(custom, "=1").message, "Mira el tipo de IVA.");
});

test("sin «=» o con un error de sintaxis no se corrige: se explica", () => {
  assert.deepEqual(checkFormula(IVA, "B2*$E$1"), { ok: false, needsEquals: true, results: [], message: "Una fórmula empieza por «=». Escríbelo delante." });
  const broken = checkFormula(IVA, "=B2*($E$1");
  assert.equal(broken.ok, false);
  assert.equal(broken.syntax.position, 9);
  assert.match(broken.message, /Falta cerrar un paréntesis. \(carácter 10\)/);
  assert.equal(checkFormula(HOJAS, "=SUMA(Enero:Marzo!B5)").syntax.unsupported, true);
});

test("las variantes son siempre las mismas para un ejercicio, y distintas de los datos originales", () => {
  assert.deepEqual(variantGrid(IVA, 0), variantGrid(IVA, 0));
  assert.notDeepEqual(variantGrid(IVA, 0), IVA.grid);
  assert.notDeepEqual(variantGrid(IVA, 0), variantGrid(IVA, 1));
  assert.equal(variantGrid(IVA, 0).B1, "Base");
  const onlyB = variantGrid({ ...IVA, vary: ["B2:B6"] }, 0);
  assert.equal(onlyB.E1, 0.21);
  assert.notEqual(onlyB.B2, 100);
});

test("«¿Qué devuelve esta fórmula?»: número con coma o punto, texto y opción", () => {
  const number = { kind: "formula-result", input: "number", answer: 1333.33, tolerance: 0.01 };
  assert.equal(checkResult(number, "1333,33").ok, true);
  assert.equal(checkResult(number, "1333.33").ok, true);
  assert.equal(checkResult(number, "1333").ok, false);
  assert.equal(checkResult(number, "").empty, true);
  assert.equal(parseAnswer("1 333,5", "number"), 1333.5);
  assert.equal(checkResult({ input: "text", answer: "Total: 5" }, " total: 5 ").ok, true);
  assert.equal(checkResult({ input: "choice", answer: 2 }, "2").ok, true);
  assert.equal(checkResult({ input: "choice", answer: 2 }, 1).ok, false);
});

test("el generador rechaza ejercicios mal hechos", () => {
  assert.match(verifyQuestion({ ...IVA, checks: [{ type: "value" }] }).join(), /=B2\*E1 pasa todas las comprobaciones/);
  assert.match(verifyQuestion({ ...REDONDEO, tolerance: 0.005 }).join(), /tolerancia 0.005 deja pasar resultados sin redondear/);
  assert.match(verifyQuestion({ ...IVA, solution: { formula: "=B2*E1" } }).join(), /la solución no pasa/);
  assert.match(verifyQuestion({ ...IVA, mistakes: [] }).join(), /error frecuente que sea una fórmula/);
  assert.match(verifyQuestion({ ...IVA, hints: [] }).join(), /pista/);
  assert.match(verifyQuestion({ ...IVA, grid: { ...IVA.grid, D2: 1 } }).join(), /tiene que estar vacía/);
  assert.match(verifyQuestion({ ...IVA, checks: [{ type: "sameAs" }] }).join(), /comprobación desconocida sameAs/);
  const result = { id: "r", kind: "formula-result", grid: { A2: "F-001", A3: 120, A6: 80 }, formula: "=CONTAR(A2:A6)", input: "number", answer: 2 };
  assert.deepEqual(verifyQuestion(result), []);
  assert.match(verifyQuestion({ ...result, answer: 3 }).join(), /el motor da 2/);
  assert.deepEqual(verifyQuestion({ ...result, input: "choice", options: [1, 2, 3], answer: 1 }), []);
  assert.match(verifyQuestion({ ...result, input: "choice", options: [2, 2, 3], answer: 1 }).join(), /solo con la opción correcta/);
  assert.match(verifyQuestion({ ...result, formula: "=1+" }).join(), /no es válida/);
  const big = Object.fromEntries(Array.from({ length: 201 }, (_, i) => [`A${i + 1}`, i]));
  assert.match(verifyQuestion({ ...result, grid: big }).join(), /más de 200 celdas/);
});
