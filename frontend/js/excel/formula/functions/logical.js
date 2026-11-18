/* Lógicas (M04, MF-21): SI, Y, O, NO, SI.CONJUNTO y SI.ERROR. SI, SI.CONJUNTO y SI.ERROR son
   `lazy`: solo calculan la rama que toca (`=SI(B1=0;0;A1/B1)` no da #¡DIV/0!). SI.ERROR no oculta
   los errores propios del motor (ciclo, límite): el alumno tiene que verlos. */

import { ERROR_CODES, isError, xlError } from "../errors.js";
import { FALSE_WORD, TRUE_WORD } from "../locale-es.js";
import { cellValues, scalar } from "./args.js";

/** Valor lógico como Excel: un número es VERDADERO si no es 0; un texto, solo «VERDADERO» o «FALSO». */
export function toBoolean(value) {
  if (isError(value) || typeof value === "boolean") return value;
  if (value === null || value === undefined) return false;
  if (typeof value === "number") return value !== 0;
  const word = String(value).trim().toUpperCase();
  if (word === TRUE_WORD || word === FALSE_WORD) return word === TRUE_WORD;
  return xlError(ERROR_CODES.VALUE, `«${value}» es un texto, no VERDADERO ni FALSO.`);
}

export function IF(lazy) {
  const test = toBoolean(lazy.scalar(0));
  if (isError(test)) return test;
  if (test) return lazy.count > 1 ? lazy.value(1) : true;
  return lazy.count > 2 ? lazy.value(2) : false;
}

export function IFS(lazy) {
  if (lazy.count % 2 !== 0) return xlError(ERROR_CODES.NA, "SI.CONJUNTO va por parejas: falta el valor de la última condición.");
  for (let i = 0; i < lazy.count; i += 2) {
    const test = toBoolean(lazy.scalar(i));
    if (isError(test) || test) return isError(test) ? test : lazy.value(i + 1);
  }
  return xlError(ERROR_CODES.NA, "Ninguna condición es VERDADERO. Para «en otro caso», pon VERDADERO como última condición.");
}

export function IFERROR(lazy) {
  const value = lazy.scalar(0);
  return isError(value) && !value.engineOnly ? lazy.value(1) : value;
}

/** Valores lógicos de Y y O: en rangos y celdas se ignoran textos y vacías. */
function logicalValues(args) {
  const out = [];
  for (const arg of args) {
    for (const value of arg.kind === "value" ? [toBoolean(scalar(arg))] : cellValues(arg)) {
      if (isError(value)) return value;
      if (typeof value === "boolean" || typeof value === "number") out.push(Boolean(value));
    }
  }
  return out.length ? out : xlError(ERROR_CODES.VALUE, "No hay ningún valor lógico que comprobar.");
}

const or = (fn) => (value) => (isError(value) ? value : fn(value));
export const AND = (args) => or((list) => list.every(Boolean))(logicalValues(args));
export const OR = (args) => or((list) => list.some(Boolean))(logicalValues(args));
export const NOT = ([arg]) => or((value) => !value)(toBoolean(scalar(arg)));
