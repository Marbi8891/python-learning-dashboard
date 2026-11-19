/* Valores del motor y sus conversiones (docs/excel-academy/FORMULA_ENGINE_SPEC.md §5).

   Un valor es un número, un texto, un booleano, null (celda vacía) o un XlError. Un rango es un
   RangeValue, que solo aparece como argumento de una función. */

import { ERROR_CODES, isError, xlError } from "./errors.js";
import { FALSE_WORD, formatNumber, parseSpanishNumber, TRUE_WORD } from "./locale-es.js";

export class RangeValue {
  /**
   * @param {object} bounds { sheet, c1, r1, c2, r2 } con c1 <= c2 y r1 <= r2
   * @param {(col: number, row: number) => any} read lee una celda (cuenta pasos y detecta ciclos)
   */
  constructor(bounds, read) {
    Object.assign(this, bounds);
    this.read = read;
    Object.freeze(this);
  }

  get rows() {
    return this.r2 - this.r1 + 1;
  }

  get cols() {
    return this.c2 - this.c1 + 1;
  }

  /** Valores por filas, de izquierda a derecha. */
  *values() {
    for (let row = this.r1; row <= this.r2; row += 1) {
      for (let col = this.c1; col <= this.c2; col += 1) yield this.read(col, row);
    }
  }
}

export const isRange = (value) => value instanceof RangeValue;

/** Número de un valor para operar (+, -, *…). Devuelve un número o un XlError. */
export function toNumber(value) {
  if (isError(value)) return value;
  if (value === null || value === undefined) return 0;
  if (typeof value === "number") return value;
  if (typeof value === "boolean") return value ? 1 : 0;
  if (typeof value === "string") {
    const number = parseSpanishNumber(value);
    return number === null ? xlError(ERROR_CODES.VALUE, `«${value}» es un texto y no se puede usar como número.`) : number;
  }
  return xlError(ERROR_CODES.VALUE);
}

/** Texto de un valor para concatenar con &. Devuelve un texto o un XlError. */
export function toText(value) {
  if (isError(value)) return value;
  if (value === null || value === undefined) return "";
  if (typeof value === "number") return formatNumber(value);
  if (typeof value === "boolean") return value ? TRUE_WORD : FALSE_WORD;
  return String(value);
}

/** Número redondeado a 15 cifras significativas, como compara Excel. */
export const round15 = (n) => (n === 0 ? 0 : Number(n.toPrecision(15)));

const typeRank = (value) => (typeof value === "number" ? 0 : typeof value === "string" ? 1 : 2);

/**
 * Compara dos valores como Excel: textos sin distinguir mayúsculas; entre tipos distintos,
 * número < texto < booleano; la celda vacía vale 0, "" o FALSO según el otro lado.
 * Devuelve -1, 0 o 1, o un XlError.
 */
export function compareValues(a, b) {
  if (isError(a)) return a;
  if (isError(b)) return b;
  let left = a ?? null;
  let right = b ?? null;
  if (left === null && right === null) return 0;
  const blankFor = (other) => (typeof other === "string" ? "" : typeof other === "boolean" ? false : 0);
  if (left === null) left = blankFor(right);
  if (right === null) right = blankFor(left);
  const ra = typeRank(left);
  const rb = typeRank(right);
  if (ra !== rb) return ra < rb ? -1 : 1;
  if (typeof left === "number") {
    const x = round15(left);
    const y = round15(right);
    return x === y ? 0 : x < y ? -1 : 1;
  }
  if (typeof left === "string") {
    const x = left.toUpperCase();
    const y = right.toUpperCase();
    return x === y ? 0 : x < y ? -1 : 1;
  }
  return left === right ? 0 : left ? 1 : -1;
}

/** Operador de comparación aplicado al resultado de compareValues (-1, 0 o 1). */
export const COMPARE = Object.freeze({ "=": (o) => o === 0, "<>": (o) => o !== 0, "<": (o) => o < 0, ">": (o) => o > 0, "<=": (o) => o <= 0, ">=": (o) => o >= 0 });

/** Valor en el formato público de la API: { type, value } (y `message` en los errores). */
export function publicValue(value) {
  if (isError(value)) return { type: "error", value: value.code, message: value.message };
  if (value === null || value === undefined) return { type: "number", value: 0 };
  if (typeof value === "number") return { type: "number", value };
  if (typeof value === "boolean") return { type: "boolean", value };
  return { type: "text", value: String(value) };
}
