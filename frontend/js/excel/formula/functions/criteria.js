/* Criterios de SUMAR.SI y familia (MF-22; reglas en FORMULA_ENGINE_SPEC.md §6.2): 5, ">100",
   "<>Pagada", "=" (vacías), "<>" (no vacías); comodines * ? ~ con = y <>. */

import { isError } from "../errors.js";
import { FALSE_WORD, parseSpanishNumber, TRUE_WORD } from "../locale-es.js";
import { COMPARE, round15 } from "../values.js";

const OPERATORS = ["<=", ">=", "<>", "<", ">", "="];
const STAR = Symbol("*");
const ANY = Symbol("?");
const blank = (v) => v === null || v === undefined || v === "";

/** ¿`text` encaja con el patrón? Sin expresiones regulares: O(n·m). */
export function wildcardMatch(text, pattern) {
  const tokens = [];
  for (let i = 0; i < pattern.length; i += 1) {
    if (pattern[i] === "~" && i + 1 < pattern.length) tokens.push(pattern[(i += 1)]);
    else tokens.push(pattern[i] === "*" ? STAR : pattern[i] === "?" ? ANY : pattern[i]);
  }
  let t = 0;
  let p = 0;
  let star = -1;
  let from = 0;
  while (t < text.length) {
    if (tokens[p] === ANY || tokens[p] === text[t]) [t, p] = [t + 1, p + 1];
    else if (tokens[p] === STAR) [star, from, p] = [p, t, p + 1];
    else if (star >= 0) [p, from, t] = [star + 1, from + 1, from + 1];
    else return false;
  }
  while (tokens[p] === STAR) p += 1;
  return p === tokens.length;
}
const order = (a, b) => (a === b ? 0 : a < b ? -1 : 1);

/** Función que dice si una celda casa con el criterio, o null si el criterio es un error. */
export function compileCriterion(criterion) {
  if (isError(criterion)) return null;
  if (typeof criterion === "boolean") return (v) => v === criterion;
  if (typeof criterion !== "string") return typed("=", "number", round15(criterion ?? 0));
  const op = OPERATORS.find((o) => criterion.startsWith(o)) ?? "=";
  const operand = criterion.slice(criterion.startsWith(op) ? op.length : 0);
  if (operand === "") return op === "=" ? blank : op === "<>" ? (v) => !blank(v) : () => false;
  const number = parseSpanishNumber(operand.trim());
  if (number !== null) return typed(op, "number", round15(number));
  const word = operand.trim().toUpperCase();
  if (word === TRUE_WORD || word === FALSE_WORD) return op === "=" || op === "<>" ? typed(op, "boolean", word === TRUE_WORD) : () => false;
  return typed(op, "string", operand.toUpperCase());
}

function typed(op, type, target) {
  const wild = type === "string" && (op === "=" || op === "<>") && /[*?~]/.test(target);
  return (value) => {
    if (isError(value)) return false;
    if (typeof value !== type) return op === "<>";
    if (wild) return wildcardMatch(value.toUpperCase(), target) === (op === "=");
    const v = type === "number" ? round15(value) : type === "string" ? value.toUpperCase() : value;
    return COMPARE[op](order(v, target));
  };
}
