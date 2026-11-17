/* Funciones estadísticas implementadas en la v1: PROMEDIO, MIN, MAX, CONTAR y CONTARA. */

import { ERROR_CODES, isError, xlError } from "../errors.js";
import { toNumber } from "../values.js";
import { collectNumbers } from "./args.js";

export function AVERAGE(args) {
  const numbers = collectNumbers(args);
  if (isError(numbers)) return numbers;
  if (numbers.length === 0) return xlError(ERROR_CODES.DIV0, "PROMEDIO no tiene ningún número que promediar.");
  let total = 0;
  for (const n of numbers) total += n;
  return total / numbers.length;
}

export function MIN(args) {
  const numbers = collectNumbers(args);
  if (isError(numbers)) return numbers;
  return numbers.length === 0 ? 0 : Math.min(...numbers);
}

export function MAX(args) {
  const numbers = collectNumbers(args);
  if (isError(numbers)) return numbers;
  return numbers.length === 0 ? 0 : Math.max(...numbers);
}

/** CONTAR: en rangos y referencias cuenta solo números; escritos directamente, lo que se pueda convertir. */
export function COUNT(args) {
  let count = 0;
  for (const arg of args) {
    if (arg.kind === "range" || arg.kind === "ref") {
      const values = arg.kind === "range" ? arg.value.values() : [arg.value];
      for (const value of values) if (typeof value === "number") count += 1;
      continue;
    }
    if (!isError(arg.value) && !isError(toNumber(arg.value))) count += 1;
  }
  return count;
}

/** CONTARA: cuenta lo que no está vacío, incluidos textos, booleanos y errores. */
export function COUNTA(args) {
  let count = 0;
  for (const arg of args) {
    if (arg.kind === "range" || arg.kind === "ref") {
      const values = arg.kind === "range" ? arg.value.values() : [arg.value];
      for (const value of values) if (value !== null && value !== undefined) count += 1;
      continue;
    }
    count += 1;
  }
  return count;
}
