// Motor de fórmulas: funciones lógicas (M04) y agregación condicional (M05), con las reglas propias
// del motor que Excel no documenta con detalle (FORMULA_ENGINE_SPEC.md §6.2). Los resultados
// comparables con LibreOffice están en tests/fixtures/excel/reference-cases.json (log-, red-, cond-).
import assert from "node:assert/strict";
import { test } from "node:test";

import { evaluate, parseFormula } from "../../frontend/js/excel/formula/index.js";
import { compileCriterion, wildcardMatch } from "../../frontend/js/excel/formula/functions/criteria.js";

const GRID = { A1: "Pagada", A2: "Pendiente", A3: "pagada", A5: "Anulada", B1: 100, B2: 50, B3: 25, B4: 10, B5: "5", C1: 0, D1: true };
const run = (formula, grid = GRID) => evaluate(parseFormula(formula), { grid });
const value = (formula, grid) => run(formula, grid).value;

test("SI, SI.CONJUNTO y SI.ERROR solo calculan la rama que toca", () => {
  // Una celda con un ciclo daría CICLO si se calculase: la rama que no toca no se mira
  const grid = { ...GRID, E1: { f: "=E1" } };
  assert.equal(value("=SI(B1>0;1;E1)", grid), 1);
  assert.equal(value("=SI.CONJUNTO(B1>0;1;E1;2)", grid), 1);
  assert.equal(value("=SI.ERROR(B1;E1)", grid), 100);
  assert.equal(value("=SI(C1=0;0;B1/C1)"), 0);
});

test("SI sin valor para una rama devuelve VERDADERO, FALSO o 0, como Excel", () => {
  assert.equal(value("=SI(B1>0)"), true);
  assert.equal(value("=SI(B1<0;1)"), false);
  assert.equal(value("=SI(B1>0;;1)"), 0);
});

test("la condición: números (0 es FALSO), booleanos y solo los textos VERDADERO y FALSO", () => {
  assert.equal(value('=SI("verdadero";1;2)'), 1);
  assert.equal(value('=SI("FALSO";1;2)'), 2);
  assert.equal(value('=SI("sí";1;2)'), "#¡VALOR!");
  assert.equal(value("=SI(D1;1;2)"), 1);
  assert.equal(value("=SI(Z9;1;2)"), 2); // vacía: FALSO
});

test("SI.ERROR captura los errores de Excel pero no los del motor", () => {
  assert.equal(value('=SI.ERROR(1/0;"x")'), "x");
  assert.equal(value('=SI.ERROR(#N/D;"x")'), "x");
  assert.equal(value('=SI.ERROR(E1;"x")', { E1: { f: "=E1" } }), "CICLO");
});

test("SI.CONJUNTO: #N/D si ninguna condición se cumple o si falta el valor de la última", () => {
  assert.equal(value('=SI.CONJUNTO(B1<0;"a")'), "#N/D");
  assert.equal(value('=SI.CONJUNTO(B1<0;"a";B1>0)'), "#N/D");
});

test("Y y O ignoran textos y vacías de los rangos, y fallan si no queda ningún valor lógico", () => {
  assert.equal(value("=Y(B1:B4)"), true);
  assert.equal(value("=O(C1;Z1)"), false);
  assert.equal(value("=Y(A1:A3)"), "#¡VALOR!");
  assert.equal(value('=Y(VERDADERO;"x")'), "#¡VALOR!"); // escrito directamente sí cuenta
  assert.equal(value("=NO(C1)"), true);
  assert.equal(value("=Y(B1>0;1/0)"), "#¡DIV/0!");
});

test("REDONDEAR.MAS, ENTERO y RESIDUO en negativos y casos límite", () => {
  assert.equal(value("=REDONDEAR.MAS(2,0001;0)"), 3);
  assert.equal(value("=REDONDEAR.MAS(-0,1;0)"), -1);
  assert.equal(value("=REDONDEAR.MAS(0;2)"), 0);
  assert.equal(value("=REDONDEAR.MAS(1,005;2)"), 1.01);
  assert.equal(value("=ENTERO(5)"), 5);
  assert.equal(value("=RESIDUO(7,5;2)"), 1.5);
  assert.equal(value('=RESIDUO("x";2)'), "#¡VALOR!");
});

test("criterios: un número solo casa con números (no con el texto «5») y <> casa con vacías", () => {
  assert.equal(value("=CONTAR.SI(B1:B5;5)"), 0);
  assert.equal(value('=CONTAR.SI(B1:B5;"<>50")'), 4);
  assert.equal(value('=CONTAR.SI(A1:A5;"<>Pagada")'), 3); // Pendiente, la vacía A4 y Anulada
  assert.equal(value('=CONTAR.SI(A1:A5;"=")'), 1);
  assert.equal(value('=CONTAR.SI(D1;VERDADERO)'), 1);
  assert.equal(value('=CONTAR.SI(D1;"VERDADERO")'), 1);
});

test("criterios desde una celda o unidos con &, y una celda de criterio vacía vale 0", () => {
  assert.equal(value("=SUMAR.SI(A1:A5;A1;B1:B5)"), 125);
  assert.equal(value('=SUMAR.SI(B1:B5;">="&B2)'), 150);
  assert.equal(value("=CONTAR.SI(C1:C2;Z9)"), 1);
});

test("una celda con error nunca casa, pero un error en el rango de suma que casa se propaga", () => {
  const grid = { A1: "x", A2: "y", B1: { f: "=1/0" }, B2: 5 };
  assert.equal(value('=CONTAR.SI(B1:B2;">0")', grid), 1);
  assert.equal(value('=SUMAR.SI(A1:A2;"y";B1:B2)', grid), 5);
  assert.equal(value('=SUMAR.SI(A1:A2;"x";B1:B2)', grid), "#¡DIV/0!");
  assert.equal(value("=SUMAR.SI(A1:A2;1/0;B1:B2)", grid), "#¡DIV/0!"); // criterio con error
});

test("tamaños: SUMAR.SI ajusta el rango de suma; las «.CONJUNTO» exigen el mismo tamaño", () => {
  assert.equal(value('=SUMAR.SI(A1:A3;"pagada";B1)'), 125);
  assert.equal(value('=SUMAR.SI.CONJUNTO(B1:B3;A1:A4;"Pagada")'), "#¡VALOR!");
  assert.equal(value('=CONTAR.SI.CONJUNTO(A1:A3;"P*";B1:B4;">0")'), "#¡VALOR!");
  assert.equal(value('=SUMAR.SI(5;5)'), "#¡VALOR!");
  assert.equal(value('=SUMAR.SI(Otra!A1:A2;1)'), "#¡REF!");
});

test("comodines: * cualquier texto, ? un carácter, ~ quita el comodín; sin expresiones regulares", () => {
  assert.equal(wildcardMatch("PAGADA", "P*"), true);
  assert.equal(wildcardMatch("PAGADA", "P?GADA"), true);
  assert.equal(wildcardMatch("PAGADA", "*GAD?"), true);
  assert.equal(wildcardMatch("PAGADA", "P?G"), false);
  assert.equal(wildcardMatch("A*B", "A~*B"), true);
  assert.equal(wildcardMatch("AXB", "A~*B"), false);
  assert.equal(wildcardMatch("", "*"), true);
  // Un patrón con muchos * sobre un texto largo termina enseguida (sin vuelta atrás exponencial)
  const started = performance.now();
  assert.equal(wildcardMatch("A".repeat(5000), `${"*A".repeat(20)}B`), false);
  assert.ok(performance.now() - started < 500);
  assert.equal(compileCriterion(undefined)(0), true); // celda de criterio vacía: = 0
});

test("MAX.SI.CONJUNTO y MIN.SI.CONJUNTO dan 0 sin coincidencias; PROMEDIO.SI da #¡DIV/0!", () => {
  assert.equal(value('=MAX.SI.CONJUNTO(B1:B4;A1:A4;"Nada")'), 0);
  assert.equal(value('=MIN.SI.CONJUNTO(B1:B4;A1:A4;"pagada")'), 25);
  assert.equal(value('=PROMEDIO.SI(A1:A4;"Nada";B1:B4)'), "#¡DIV/0!");
  assert.equal(value('=CONTAR.SI.CONJUNTO(A1:A4;"pagada";B1:B4;"<50")'), 1);
});
