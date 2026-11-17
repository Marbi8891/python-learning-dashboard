/* Funciones matemáticas implementadas en la v1: SUMA, PRODUCTO y REDONDEAR. */

import { isError } from "../errors.js";
import { round15 } from "../values.js";
import { collectNumbers, numberArg } from "./args.js";

export function SUM(args) {
  const numbers = collectNumbers(args);
  if (isError(numbers)) return numbers;
  let total = 0;
  for (const n of numbers) total += n;
  return total;
}

export function PRODUCT(args) {
  const numbers = collectNumbers(args);
  if (isError(numbers)) return numbers;
  if (numbers.length === 0) return 0; // como Excel: PRODUCTO sin números da 0
  let total = 1;
  for (const n of numbers) total *= n;
  return total;
}

/**
 * Redondeo «mitad lejos de cero» con el número tal como se ve en decimal: REDONDEAR(2,675;2) da 2,68
 * aunque 2,675 no tenga representación binaria exacta.
 */
export function roundHalfAwayFromZero(number, digits) {
  const scale = 10 ** Math.abs(digits);
  const magnitude = Math.abs(number);
  const scaled = digits >= 0 ? magnitude * scale : magnitude / scale;
  const rounded = Math.round(round15(scaled));
  const result = digits >= 0 ? rounded / scale : rounded * scale;
  return number < 0 ? -result : result;
}

export function ROUND([numberArgument, digitsArgument]) {
  const number = numberArg(numberArgument);
  if (isError(number)) return number;
  const digits = numberArg(digitsArgument);
  if (isError(digits)) return digits;
  return roundHalfAwayFromZero(number, Math.trunc(digits));
}
