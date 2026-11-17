// Motor de fórmulas: registro de funciones, implementadas y previstas (P-UNI-05), y errores (P-UNI-06).
import assert from "node:assert/strict";
import { test } from "node:test";

import { evaluate, FUNCTIONS, functionStatus, parseFormula } from "../../frontend/js/excel/formula/index.js";
import { FUNCTION_NAMES } from "../../frontend/js/excel/formula/locale-es.js";

const run = (formula, grid = {}) => evaluate(parseFormula(formula), { grid });
const IMPLEMENTED = ["SUM", "PRODUCT", "ROUND", "AVERAGE", "MIN", "MAX", "COUNT", "COUNTA"];

test("el registro tiene las 45 funciones de la especificación: 8 implementadas y 37 previstas", () => {
  assert.equal(FUNCTIONS.length, 45);
  assert.equal(Object.keys(FUNCTION_NAMES).length, 45);
  assert.deepEqual(FUNCTIONS.filter((f) => f.status === "implemented").map((f) => f.name).sort(), [...IMPLEMENTED].sort());
  assert.equal(FUNCTIONS.filter((f) => f.status === "planned").length, 37);
  for (const f of FUNCTIONS) {
    assert.ok(f.spanish, `${f.name} sin nombre en español`);
    assert.ok(f.since && f.category, `${f.name} sin versión o categoría`);
    if (f.status === "implemented") assert.ok(f.minArgs >= 1 && f.maxArgs >= f.minArgs, `${f.name} sin firma`);
    else assert.match(f.module, /^M\d\d$/, `${f.name} sin módulo previsto`);
  }
  assert.equal(functionStatus("BUSCARX"), "planned");
  assert.equal(functionStatus("suma"), "implemented");
  assert.equal(functionStatus("SUM"), "implemented");
  assert.equal(functionStatus("NOEXISTE"), null);
});

test("toda función prevista da #¿NOMBRE? con el aviso «todavía no está disponible en PLD»", () => {
  for (const f of FUNCTIONS.filter((x) => x.status === "planned")) {
    const result = run(`=${f.spanish}(1)`);
    assert.equal(result.value, "#¿NOMBRE?", f.spanish);
    assert.equal(result.message, `${f.spanish} todavía no está disponible en PLD.`);
  }
});

test("una función que no existe o escrita en inglés da #¿NOMBRE?", () => {
  assert.equal(run("=SUM(1;2)").value, "#¿NOMBRE?");
  assert.match(run("=SUM(1;2)").message, /no es una función de Excel en español/);
  assert.equal(run("=texto").value, "#¿NOMBRE?");
});

test("los errores se propagan, y CONTAR y CONTARA los cuentan como Excel", () => {
  const grid = { A1: 10, A2: { f: "=1/0" }, A3: 5 };
  assert.equal(run("=SUMA(A1:A3)", grid).value, "#¡DIV/0!");
  assert.equal(run("=PROMEDIO(A1:A3)", grid).value, "#¡DIV/0!");
  assert.equal(run("=MAX(A1:A3)", grid).value, "#¡DIV/0!");
  assert.equal(run("=CONTAR(A1:A3)", grid).value, 2);
  assert.equal(run("=CONTARA(A1:A3)", grid).value, 3);
  assert.equal(run("=A2&\"x\"", grid).value, "#¡DIV/0!");
  assert.equal(run("=#N/D=1").value, "#N/D");
  assert.equal(run("=1/0+#N/D").value, "#¡DIV/0!"); // el primero que se calcula
});

test("cada función implementada: caso normal, límite, inválido, anidado, error y vacío", () => {
  const grid = { A1: 4, A2: 6, A3: "x", B1: { f: "=1/0" } };
  const cases = {
    SUMA: [["=SUMA(A1:A2)", 10], ["=SUMA(0)", 0], ["=SUMA(\"x\")", "#¡VALOR!"], ["=SUMA(SUMA(A1;1);2)", 7], ["=SUMA(B1;1)", "#¡DIV/0!"], ["=SUMA(Z1)", 0]],
    PRODUCTO: [["=PRODUCTO(A1:A2)", 24], ["=PRODUCTO(1E-3;1000)", 1], ["=PRODUCTO(\"x\")", "#¡VALOR!"], ["=PRODUCTO(SUMA(1;1);3)", 6], ["=PRODUCTO(B1)", "#¡DIV/0!"], ["=PRODUCTO(Z1)", 0]],
    REDONDEAR: [["=REDONDEAR(2,345;2)", 2.35], ["=REDONDEAR(0,5;0)", 1], ["=REDONDEAR(\"x\";2)", "#¡VALOR!"], ["=REDONDEAR(PROMEDIO(1;2);0)", 2], ["=REDONDEAR(B1;2)", "#¡DIV/0!"], ["=REDONDEAR(Z1;2)", 0]],
    PROMEDIO: [["=PROMEDIO(A1:A2)", 5], ["=PROMEDIO(7)", 7], ["=PROMEDIO(\"x\")", "#¡VALOR!"], ["=PROMEDIO(MIN(A1:A2);MAX(A1:A2))", 5], ["=PROMEDIO(B1)", "#¡DIV/0!"], ["=PROMEDIO(Z1)", "#¡DIV/0!"]],
    MIN: [["=MIN(A1:A3)", 4], ["=MIN(-0,5)", -0.5], ["=MIN(\"x\")", "#¡VALOR!"], ["=MIN(MAX(1;2);3)", 2], ["=MIN(B1)", "#¡DIV/0!"], ["=MIN(Z1)", 0]],
    MAX: [["=MAX(A1:A3)", 6], ["=MAX(1E15;1)", 1e15], ["=MAX(\"x\")", "#¡VALOR!"], ["=MAX(MIN(5;9);2)", 5], ["=MAX(B1)", "#¡DIV/0!"], ["=MAX(Z1)", 0]],
    CONTAR: [["=CONTAR(A1:A3)", 2], ["=CONTAR(0)", 1], ["=CONTAR(\"x\")", 0], ["=CONTAR(SUMA(1;2))", 1], ["=CONTAR(B1)", 0], ["=CONTAR(Z1)", 0]],
    CONTARA: [["=CONTARA(A1:A3)", 3], ["=CONTARA(0)", 1], ["=CONTARA(\"x\")", 1], ["=CONTARA(CONTAR(A1))", 1], ["=CONTARA(B1)", 1], ["=CONTARA(Z1)", 0]],
  };
  for (const [name, list] of Object.entries(cases)) {
    assert.equal(list.length, 6, name);
    for (const [formula, want] of list) assert.equal(run(formula, grid).value, want, formula);
  }
});
