// Motor de fórmulas: referencias relativas, absolutas y mixtas, y copia de fórmulas (P-UNI-03).
import assert from "node:assert/strict";
import { test } from "node:test";

import { columnLetters, evaluate, parseCell, parseFormula, shiftFormula, toFormula } from "../../frontend/js/excel/formula/index.js";
import { columnIndex } from "../../frontend/js/excel/formula/references.js";

const copy = (formula, rows, cols) => toFormula(shiftFormula(parseFormula(formula), { rows, cols }));

test("letras de columna y números", () => {
  for (const [letters, n] of [["A", 1], ["Z", 26], ["AA", 27], ["AZ", 52], ["BA", 53], ["XFD", 16384]]) {
    assert.equal(columnIndex(letters), n);
    assert.equal(columnLetters(n), letters);
  }
  assert.equal(parseCell("A0"), null);
  assert.equal(parseCell("A01"), null);
  assert.equal(parseCell("A1048577"), null);
  assert.equal(parseCell("ABCD1"), null);
});

test("al copiar, lo relativo se mueve y lo que lleva $ se queda", () => {
  assert.equal(copy("=B2*$E$1", 1, 0), "=B3*$E$1");
  assert.equal(copy("=B2*$E$1", 0, 1), "=C2*$E$1");
  assert.equal(copy("=$A2*B$1", 2, 2), "=$A4*D$1");
  assert.equal(copy("=SUMA(B2:B7)", 0, 1), "=SUMA(C2:C7)");
  assert.equal(copy("=SUMA($B$2:B2)", 3, 0), "=SUMA($B$2:B5)"); // acumulado
  assert.equal(copy("=Enero!B5+1", 1, 0), "=Enero!B6+1");
  assert.equal(copy("='Hoja 2'!A1", 0, 1), "='Hoja 2'!B1");
  assert.equal(copy("=B3", -1, 0), "=B2");
});

test("una referencia que se sale de la hoja al copiar pasa a #¡REF!", () => {
  assert.equal(copy("=A1+1", -1, 0), "=#¡REF!+1");
  assert.equal(copy("=SUMA(A1:B2)", 0, -1), "=SUMA(#¡REF!)");
  assert.deepEqual(evaluate(shiftFormula(parseFormula("=A1+1"), { rows: -1 })), { type: "error", value: "#¡REF!", message: "La referencia no es válida." });
  assert.equal(copy("=$A$1", -5, -5), "=$A$1");
});

test("copiar no cambia la fórmula original", () => {
  const ast = parseFormula("=B2*$E$1");
  shiftFormula(ast, { rows: 4 });
  assert.equal(toFormula(ast), "=B2*$E$1");
});

test("las hojas se comparan sin distinguir mayúsculas y una hoja que no existe da #¡REF!", () => {
  const grid = { "Enero!B5": 4200 };
  assert.equal(evaluate(parseFormula("=ENERO!B5"), { grid }).value, 4200);
  assert.equal(evaluate(parseFormula("=Abril!B5"), { grid }).value, "#¡REF!");
  assert.equal(evaluate(parseFormula("=A1"), { grid: { "Resumen!A1": 3 }, sheet: "Resumen" }).value, 3);
});
