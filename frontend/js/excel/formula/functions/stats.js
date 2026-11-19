/* Funciones estadísticas implementadas en la v1: PROMEDIO, MIN, MAX, CONTAR y CONTARA. */

import { ERROR_CODES, isError, xlError } from "../errors.js";
import { toNumber } from "../values.js";
import { cellValues, collectNumbers } from "./args.js";

export function AVERAGE(args) {
  const numbers = collectNumbers(args);
  if (isError(numbers)) return numbers;
  if (numbers.length === 0) return xlError(ERROR_CODES.DIV0, "PROMEDIO no tiene ningún número que promediar.");
  let total = 0;
  for (const n of numbers) total += n;
  return total / numbers.length;
}

const extreme = (fn) => (args) => {
  const numbers = collectNumbers(args);
  return isError(numbers) ? numbers : numbers.length ? fn(...numbers) : 0;
};
export const MIN = extreme(Math.min);
export const MAX = extreme(Math.max);

/** CONTAR: en rangos y celdas cuenta números; escritos directamente, lo que se pueda convertir.
    CONTARA: lo que no está vacío, incluidos textos, booleanos y errores. */
const counter = (inCells, direct) => (args) => {
  let count = 0;
  for (const arg of args) {
    if (arg.kind === "value") count += direct(arg.value) ? 1 : 0;
    else for (const value of cellValues(arg)) count += inCells(value) ? 1 : 0;
  }
  return count;
};
export const COUNT = counter((v) => typeof v === "number", (v) => !isError(v) && !isError(toNumber(v)));
export const COUNTA = counter((v) => v !== null && v !== undefined, () => true);
