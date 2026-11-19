/* Funciones matemáticas: SUMA, PRODUCTO y REDONDEAR (v1); REDONDEAR.MAS, ENTERO y RESIDUO (M04). */

import { ERROR_CODES, isError, xlError } from "../errors.js";
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

/** REDONDEAR.MAS: redondea alejándose de cero. */
export function ROUNDUP([numberArgument, digitsArgument]) {
  const number = numberArg(numberArgument);
  const digits = numberArg(digitsArgument);
  if (isError(number) || isError(digits)) return isError(number) ? number : digits;
  const d = Math.trunc(digits);
  const scale = 10 ** Math.abs(d);
  const up = Math.ceil(round15(d >= 0 ? Math.abs(number) * scale : Math.abs(number) / scale));
  return Math.sign(number) * (d >= 0 ? up / scale : up * scale);
}

/** ENTERO: hacia abajo (ENTERO(-2,5) da -3). */
export function INT([arg]) {
  const number = numberArg(arg);
  return isError(number) ? number : Math.floor(round15(number));
}

/** RESIDUO: resto con el signo del divisor (RESIDUO(-3;2) da 1). */
export function MOD([numberArgument, divisorArgument]) {
  const n = numberArg(numberArgument);
  const d = numberArg(divisorArgument);
  if (isError(n) || isError(d)) return isError(n) ? n : d;
  if (d === 0) return xlError(ERROR_CODES.DIV0);
  return round15(n - d * Math.floor(round15(n / d)));
}
