/* Agregación condicional (M05). `lazy`: cada rango llega con su posición. En SUMAR.SI y
   PROMEDIO.SI el rango de suma toma el tamaño del rango del criterio, como en Excel. */

import { ERROR_CODES, isError, xlError } from "../errors.js";
import { compileCriterion } from "./criteria.js";

const PAIRS = "Faltan parejas de rango y criterio.";

/** Posiciones que casan con todas las parejas (rango; criterio) desde `first`, o un XlError. */
function matches(lazy, first, size, last = lazy.count) {
  let picked = null;
  for (let i = first; i < last; i += 2) {
    const range = lazy.range(i);
    if (isError(range)) return range;
    if (size && (range.rows !== size.rows || range.cols !== size.cols)) return xlError(ERROR_CODES.VALUE, "Los rangos no miden lo mismo.");
    size ??= range;
    const criterion = lazy.scalar(i + 1);
    const test = compileCriterion(criterion);
    if (!test) return criterion;
    picked = [...range.values()].map((value, k) => (!picked || picked[k]) && test(value));
  }
  return picked;
}

/** Números de `target` donde casa; un error en una celda que casa se propaga. */
function pick(target, picked) {
  if (isError(target) || isError(picked)) return isError(target) ? target : picked;
  const out = [];
  let k = 0;
  for (const value of target.values()) {
    if (!picked[k++]) continue;
    if (isError(value)) return value;
    if (typeof value === "number") out.push(value);
  }
  return out;
}

/** SUMAR.SI y PROMEDIO.SI: (rango; criterio; [rango de suma]). */
function single(lazy) {
  const range = lazy.range(0);
  if (isError(range) || lazy.count < 3) return pick(range, matches(lazy, 0, null, 2));
  const o = lazy.range(2);
  return pick(isError(o) ? o : lazy.rangeAt(o.sheet, o.c1, o.r1, o.c1 + range.cols - 1, o.r1 + range.rows - 1), matches(lazy, 0, null, 2));
}

/** (rango del resultado; rango1; criterio1; …). */
function multiple(lazy) {
  if (lazy.count % 2 === 0) return xlError(ERROR_CODES.VALUE, PAIRS);
  const target = lazy.range(0);
  return pick(target, isError(target) ? target : matches(lazy, 1, target));
}

const sum = (list) => list.reduce((total, n) => total + n, 0);
const or = (fn) => (list) => (isError(list) ? list : fn(list));
const count = or((list) => list.filter(Boolean).length);

export const SUMIF = (lazy) => or(sum)(single(lazy));
export const SUMIFS = (lazy) => or(sum)(multiple(lazy));
export const MAXIFS = (lazy) => or((list) => (list.length ? Math.max(...list) : 0))(multiple(lazy));
export const MINIFS = (lazy) => or((list) => (list.length ? Math.min(...list) : 0))(multiple(lazy));
export const AVERAGEIF = (lazy) =>
  or((list) => (list.length ? sum(list) / list.length : xlError(ERROR_CODES.DIV0, "Ninguna celda cumple el criterio.")))(single(lazy));
export const COUNTIF = (lazy) => count(matches(lazy, 0, null, 2));
export const COUNTIFS = (lazy) => (lazy.count % 2 ? xlError(ERROR_CODES.VALUE, PAIRS) : count(matches(lazy, 0, null)));
