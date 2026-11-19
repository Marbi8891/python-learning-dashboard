/* Motor de fórmulas de Excel profesional (docs/excel-academy/FORMULA_ENGINE_SPEC.md).

   API pública: es lo único que deben importar las vistas, las comprobaciones y el generador.
   Funciona igual en el navegador y en Node 22. */

import { functionInfo, FUNCTION_LIST } from "./functions/registry.js";
import { canonicalName, SPANISH_NAME } from "./locale-es.js";

export { shiftFormula, toFormula, walk } from "./ast.js";
export { ERROR_CODES, FormulaSyntaxError, XlError } from "./errors.js";
export { DEFAULT_SHEET, evaluate } from "./evaluator.js";
export { parseFormula } from "./parser.js";
export { address, columnLetters, formatRef, parseAddress, parseCell } from "./references.js";
export { DEFAULT_LIMITS } from "./tokenizer.js";

/** Versión del motor. Se escribe en el JSON del curso generado. */
export const ENGINE_VERSION = "1.1.0";

/** «implemented», «planned» o null. Acepta el nombre en español («BUSCARX») o el canónico («XLOOKUP»). */
export function functionStatus(name) {
  const upper = String(name).toUpperCase();
  return functionInfo(canonicalName(upper) ?? upper)?.status ?? null;
}

/** Las 45 funciones, con su nombre en español y su estado. */
export const FUNCTIONS = Object.freeze(
  FUNCTION_LIST.map((name) => Object.freeze({ name, spanish: SPANISH_NAME[name], ...functionInfo(name), impl: undefined })),
);
