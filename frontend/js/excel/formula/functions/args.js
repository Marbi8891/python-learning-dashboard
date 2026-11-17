/* Ayudas comunes de las funciones: cómo se leen los argumentos.

   Cada argumento llega como { kind, value }: «range» (un rango), «ref» (una celda escrita como
   referencia) o «value» (cualquier otra expresión, ya calculada). Excel trata distinto un texto
   según venga de una referencia (se ignora en SUMA) o escrito directamente (se convierte). */

import { ERROR_CODES, isError, xlError } from "../errors.js";
import { toNumber } from "../values.js";

/** Números de los argumentos de una función de agregación (SUMA, PROMEDIO, MIN, MAX, PRODUCTO). */
export function collectNumbers(args) {
  const out = [];
  for (const arg of args) {
    if (arg.kind === "range" || arg.kind === "ref") {
      const values = arg.kind === "range" ? arg.value.values() : [arg.value];
      for (const value of values) {
        if (isError(value)) return value;
        if (typeof value === "number") out.push(value);
      }
      continue;
    }
    const number = toNumber(arg.value);
    if (isError(number)) return number;
    out.push(number);
  }
  return out;
}

/** Un único valor: una celda, o un rango de una sola celda. Un rango mayor da #¡VALOR!. */
export function scalar(arg) {
  if (arg.kind !== "range") return arg.value;
  const range = arg.value;
  if (range.rows === 1 && range.cols === 1) return range.values().next().value;
  return xlError(ERROR_CODES.VALUE, "Aquí va un solo valor, no un rango de varias celdas.");
}

export const numberArg = (arg) => toNumber(scalar(arg));
