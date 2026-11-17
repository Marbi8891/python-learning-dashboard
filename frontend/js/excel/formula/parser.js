/* Analizador sintáctico de descenso recursivo con la precedencia de Excel
   (docs/excel-academy/FORMULA_ENGINE_SPEC.md §4.2). Produce un árbol (AST) inmutable.

   De menor a mayor precedencia: comparaciones, &, + y -, * y /, ^, %, signo y valores.
   Como en Excel, el signo va antes que la potencia: =-2^2 da 4. */

import { FormulaSyntaxError } from "./errors.js";
import { functionInfo } from "./functions/registry.js";
import { canonicalName, SPANISH_NAME } from "./locale-es.js";
import { DEFAULT_LIMITS, tokenize } from "./tokenizer.js";

const COMPARE = ["=", "<>", "<", ">", "<=", ">="];

function deepFreeze(node) {
  for (const value of Object.values(node)) {
    if (value && typeof value === "object" && !Object.isFrozen(value)) deepFreeze(value);
  }
  return Object.freeze(node);
}

/**
 * Analiza una fórmula. El «=» inicial es opcional.
 * @returns {object} AST congelado
 * @throws {FormulaSyntaxError} con `position` (índice del carácter) y `message` en español
 */
export function parseFormula(formula, { limits = DEFAULT_LIMITS } = {}) {
  if (typeof formula !== "string") throw new FormulaSyntaxError("La fórmula tiene que ser un texto.", 0);
  if (formula.length > limits.maxLength) {
    throw new FormulaSyntaxError(`La fórmula es demasiado larga (máximo ${limits.maxLength} caracteres).`, limits.maxLength);
  }
  let start = 0;
  while (start < formula.length && formula[start] === " ") start += 1;
  if (formula[start] === "=") start += 1;
  const tokens = tokenize(formula.slice(start), start, limits);
  let index = 0;
  let depth = 0;

  const peek = () => tokens[index];
  const next = () => tokens[index++];
  const fail = (message, token = peek(), options) => {
    throw new FormulaSyntaxError(message, token.pos, options);
  };
  const enter = (token) => {
    depth += 1;
    if (depth > limits.maxDepth) fail(`La fórmula está demasiado anidada (máximo ${limits.maxDepth} niveles).`, token);
  };

  if (peek().type === "eof") fail("La fórmula está vacía.");

  function expression() {
    return comparison();
  }

  function comparison() {
    let left = concat();
    while (peek().type === "op" && COMPARE.includes(peek().value)) {
      const op = next().value;
      left = { type: "Binary", op, left, right: concat() };
    }
    return left;
  }

  function concat() {
    let left = additive();
    while (peek().type === "op" && peek().value === "&") {
      next();
      left = { type: "Binary", op: "&", left, right: additive() };
    }
    return left;
  }

  function additive() {
    let left = multiplicative();
    while (peek().type === "op" && (peek().value === "+" || peek().value === "-")) {
      const op = next().value;
      left = { type: "Binary", op, left, right: multiplicative() };
    }
    return left;
  }

  function multiplicative() {
    let left = power();
    while (peek().type === "op" && (peek().value === "*" || peek().value === "/")) {
      const op = next().value;
      left = { type: "Binary", op, left, right: power() };
    }
    return left;
  }

  function power() {
    let left = percent();
    while (peek().type === "op" && peek().value === "^") {
      next();
      left = { type: "Binary", op: "^", left, right: percent() };
    }
    return left;
  }

  function percent() {
    let operand = unary();
    while (peek().type === "op" && peek().value === "%") {
      next();
      operand = { type: "Percent", operand };
    }
    return operand;
  }

  function unary() {
    const token = peek();
    if (token.type === "op" && (token.value === "-" || token.value === "+")) {
      next();
      return { type: "Unary", op: token.value, operand: unary() };
    }
    return primary();
  }

  function primary() {
    const token = next();
    switch (token.type) {
      case "number":
        if (peek().type === "colon") fail("Los rangos de filas completas (1:3) todavía no están soportados en PLD.", token, { unsupported: true });
        return { type: "Number", value: token.value };
      case "string":
        return { type: "Text", value: token.value };
      case "bool":
        return { type: "Bool", value: token.value };
      case "error":
        return { type: "Error", code: token.value };
      case "ref":
        return reference(token);
      case "name":
        if (peek().type === "colon") {
          fail("Las referencias 3D (Enero:Marzo!B5) y las columnas completas (A:A) todavía no están soportadas en PLD.", token, {
            unsupported: true,
          });
        }
        return { type: "Name", name: token.value };
      case "func":
        return call(token);
      case "lparen": {
        enter(token);
        const inner = expression();
        if (peek().type !== "rparen") fail("Falta cerrar un paréntesis.");
        next();
        depth -= 1;
        return inner;
      }
      case "eof":
        index -= 1;
        return fail("La fórmula está incompleta: falta un valor al final.", token);
      case "rparen":
        return fail("Sobra un paréntesis de cierre o falta un valor antes.", token);
      case "sep":
        return fail("Falta un valor antes del «;».", token);
      default:
        return fail("Falta un valor antes de este operador.", token);
    }
  }

  function reference(token) {
    if (peek().type !== "colon") return { type: "Ref", ref: token.ref };
    next();
    const end = next();
    if (end.type !== "ref") fail("Después de «:» tiene que ir otra celda, como en A1:B5.", end);
    if (end.ref.sheet !== null) {
      const same = token.ref.sheet !== null && token.ref.sheet.toUpperCase() === end.ref.sheet.toUpperCase();
      if (!same) fail("Un rango tiene que estar en una sola hoja, como Enero!A1:B5.", end, { unsupported: true });
    }
    return { type: "Range", start: token.ref, end: { ...end.ref, sheet: null } };
  }

  function call(token) {
    const open = next(); // el tokenizer garantiza que es «(»
    enter(open);
    const args = [];
    if (peek().type === "rparen") {
      next();
    } else {
      for (;;) {
        const t = peek();
        args.push(t.type === "sep" || t.type === "rparen" ? { type: "Missing" } : expression());
        if (args.length > limits.maxArgs) fail(`Demasiados argumentos (máximo ${limits.maxArgs}).`, t);
        if (peek().type === "sep") {
          next();
          continue;
        }
        if (peek().type === "rparen") {
          next();
          break;
        }
        if (peek().type === "eof") fail(`Falta cerrar el paréntesis de ${token.name}.`);
        fail(`Falta un «;» entre los argumentos de ${token.name}.`);
      }
    }
    depth -= 1;
    const name = canonicalName(token.name);
    const info = name ? functionInfo(name) : null;
    if (info && info.status === "implemented") {
      const shown = SPANISH_NAME[name];
      if (args.length < info.minArgs) fail(`${shown} necesita al menos ${info.minArgs} argumento${info.minArgs === 1 ? "" : "s"}.`, token);
      if (args.length > info.maxArgs) fail(`${shown} admite como mucho ${info.maxArgs} argumento${info.maxArgs === 1 ? "" : "s"}.`, token);
    }
    return { type: "Call", name, written: token.name, args };
  }

  const ast = expression();
  const rest = peek();
  if (rest.type !== "eof") {
    if (rest.type === "rparen") fail("Sobra un paréntesis de cierre.", rest);
    if (rest.type === "sep") fail("El «;» solo separa los argumentos de una función.", rest);
    fail("Falta un operador entre dos valores.", rest);
  }
  return deepFreeze(ast);
}
