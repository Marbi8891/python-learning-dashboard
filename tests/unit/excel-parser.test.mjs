// Motor de fórmulas: analizador léxico, sintáctico y errores de sintaxis con su posición (P-UNI-01, P-UNI-02).
import assert from "node:assert/strict";
import { test } from "node:test";

import { DEFAULT_LIMITS, FormulaSyntaxError, parseFormula, toFormula } from "../../frontend/js/excel/formula/index.js";
import { tokenize } from "../../frontend/js/excel/formula/tokenizer.js";

const types = (text) => tokenize(text).map((t) => t.type);

function syntaxError(formula, options) {
  try {
    parseFormula(formula, options);
  } catch (error) {
    assert.ok(error instanceof FormulaSyntaxError, `${formula}: ${error}`);
    return error;
  }
  assert.fail(`${formula} debería dar un error de sintaxis`);
}

test("el tokenizer reconoce números con coma decimal, textos, booleanos, errores, referencias y hojas", () => {
  assert.deepEqual(types('3,5+"a ""b"""&VERDADERO'), ["number", "op", "string", "op", "bool", "eof"]);
  assert.equal(tokenize('"a ""b"""')[0].value, 'a "b"');
  assert.equal(tokenize("1,5E3")[0].value, 1500);
  assert.equal(tokenize(",5")[0].value, 0.5);
  assert.deepEqual(tokenize("#N/D")[0], { type: "error", value: "#N/D", pos: 0 });
  assert.deepEqual(tokenize("$E$1")[0].ref, { sheet: null, col: 5, row: 1, colAbs: true, rowAbs: true });
  assert.deepEqual(tokenize("A$1")[0].ref, { sheet: null, col: 1, row: 1, colAbs: false, rowAbs: true });
  assert.equal(tokenize("Enero!B5")[0].ref.sheet, "Enero");
  assert.equal(tokenize("'Hoja 2'!A1")[0].ref.sheet, "Hoja 2");
  assert.equal(tokenize("'Ana''s'!A1")[0].ref.sheet, "Ana's");
  assert.deepEqual(types("SUMAR.SI(A1:A3;2)"), ["func", "lparen", "ref", "colon", "ref", "sep", "number", "rparen", "eof"]);
  assert.deepEqual(types("<=>=<>"), ["op", "op", "op", "eof"]);
  assert.deepEqual(types("hola"), ["name", "eof"]); // ni celda ni función: #¿NOMBRE? al evaluar
  assert.deepEqual(types("XFD1048576"), ["ref", "eof"]);
  assert.deepEqual(types("XFE1"), ["name", "eof"]); // columna fuera de la hoja
});

test("la precedencia es la de Excel (el signo antes que la potencia)", () => {
  const shape = (formula) => toFormula(parseFormula(formula));
  assert.deepEqual(parseFormula("=-2^2"), {
    type: "Binary",
    op: "^",
    left: { type: "Unary", op: "-", operand: { type: "Number", value: 2 } },
    right: { type: "Number", value: 2 },
  });
  assert.equal(parseFormula("=2+3*4").op, "+");
  assert.equal(parseFormula("=2^3^2").left.op, "^"); // potencia asociativa por la izquierda
  assert.equal(parseFormula('="a"&1+1').op, "&");
  assert.equal(parseFormula("=1+1=2").op, "=");
  assert.equal(parseFormula("=-10%").type, "Percent");
  assert.equal(shape("=(1+2)*3"), "=(1+2)*3");
  assert.equal(shape("=1-(2-3)"), "=1-(2-3)");
  assert.equal(shape("=-(2^2)"), "=-(2^2)");
  assert.equal(shape("=SUMA(A1:B2;$C$3;1,5)"), "=SUMA(A1:B2;$C$3;1,5)");
  assert.equal(shape("suma(a1)"), "=SUMA(A1)"); // sin «=» y en minúsculas
});

test("el AST es inmutable", () => {
  const ast = parseFormula("=SUMA(A1;2)");
  assert.ok(Object.isFrozen(ast) && Object.isFrozen(ast.args) && Object.isFrozen(ast.args[0]));
});

test("los errores de sintaxis dicen qué falla y dónde", () => {
  assert.equal(syntaxError("=").message, "La fórmula está vacía.");
  assert.equal(syntaxError("=(1+2").message, "Falta cerrar un paréntesis.");
  assert.equal(syntaxError("=1+2)").position, 4);
  assert.match(syntaxError("=1+").message, /incompleta/);
  assert.match(syntaxError("=SUMA(A1,B1)").message, /se separan con «;»/);
  assert.equal(syntaxError("=SUMA(A1,B1)").position, 8);
  assert.match(syntaxError('="abc').message, /comillas/);
  assert.match(syntaxError("=1 2").message, /Falta un operador/);
  assert.match(syntaxError("=SUMA()").message, /al menos 1 argumento/);
  assert.match(syntaxError("=REDONDEAR(1;2;3)").message, /como mucho 2/);
  assert.match(syntaxError("=*2").message, /Falta un valor/);
  assert.match(syntaxError("=A1:5").message, /otra celda/);
  assert.match(syntaxError("=2A").message, /Número mal escrito/);
  assert.match(syntaxError("=$hola").message, /no es una referencia/);
});

test("lo que no soporta la v1 se rechaza como «no soportado», nunca con un resultado inventado", () => {
  for (const formula of ["=SUMA(Enero:Marzo!B5)", "=SUMA(A:A)", "=SUMA(1:3)", "={1;2}", "=[Libro]Hoja!A1", "=@A1", "=Enero!A1:Febrero!B2"]) {
    assert.equal(syntaxError(formula).unsupported, true, formula);
  }
});

test("límites: longitud, anidamiento y número de argumentos", () => {
  assert.match(syntaxError(`=${"1+".repeat(1000)}1`).message, /demasiado larga/); // 2 001 caracteres
  const nest = (n) => `=${"SUMA(".repeat(n)}1${")".repeat(n)}`;
  assert.doesNotThrow(() => parseFormula(nest(DEFAULT_LIMITS.maxDepth)));
  assert.match(syntaxError(nest(DEFAULT_LIMITS.maxDepth + 1)).message, /demasiado anidada/);
  assert.match(syntaxError(`=${"(".repeat(33)}1${")".repeat(33)}`).message, /demasiado anidada/);
  assert.match(syntaxError(`=SUMA(${Array(65).fill(1).join(";")})`).message, /Demasiados argumentos|como mucho 64/);
  assert.match(syntaxError(`=${Array(600).fill("1").join("+")}`).message, /demasiado larga/); // más de 1 000 tokens
});
