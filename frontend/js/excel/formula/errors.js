/* Valores de error del motor de fórmulas (docs/excel-academy/FORMULA_ENGINE_SPEC.md §5).

   Un error es un valor más: se propaga por las operaciones y es lo que devuelve la fórmula. Los de
   Excel llevan su texto en español; los propios del motor (ciclo, no soportado, límite) se muestran
   con un mensaje y nunca se hacen pasar por un resultado de Excel. */

export const ERROR_CODES = Object.freeze({
  DIV0: "#¡DIV/0!",
  NA: "#N/D",
  VALUE: "#¡VALOR!",
  REF: "#¡REF!",
  NAME: "#¿NOMBRE?",
  NUM: "#¡NUM!",
  SPILL: "#¡DESBORDAMIENTO!",
  CALC: "#¡CALC!",
  // Propios del motor: Excel no los tiene
  CYCLE: "CICLO",
  UNSUPPORTED: "NO SOPORTADO",
  LIMIT: "LÍMITE",
});

/** Errores de Excel que se pueden escribir en una fórmula como literal (en español). */
export const LITERAL_ERRORS = Object.freeze([
  ERROR_CODES.DIV0,
  ERROR_CODES.NA,
  ERROR_CODES.VALUE,
  ERROR_CODES.REF,
  ERROR_CODES.NAME,
  ERROR_CODES.NUM,
  ERROR_CODES.SPILL,
  ERROR_CODES.CALC,
]);

const ENGINE_ONLY = new Set([ERROR_CODES.CYCLE, ERROR_CODES.UNSUPPORTED, ERROR_CODES.LIMIT]);

const DEFAULT_MESSAGES = {
  [ERROR_CODES.DIV0]: "División entre cero.",
  [ERROR_CODES.NA]: "No hay ningún valor disponible.",
  [ERROR_CODES.VALUE]: "Un valor no es del tipo que necesita la operación.",
  [ERROR_CODES.REF]: "La referencia no es válida.",
  [ERROR_CODES.NAME]: "Hay un nombre que Excel no reconoce.",
  [ERROR_CODES.NUM]: "El número no es válido.",
  [ERROR_CODES.SPILL]: "El resultado no cabe en las celdas de al lado.",
  [ERROR_CODES.CALC]: "El cálculo no tiene resultado.",
  [ERROR_CODES.CYCLE]: "Referencia circular: la fórmula depende de su propia celda.",
  [ERROR_CODES.UNSUPPORTED]: "Esto todavía no está soportado en PLD.",
  [ERROR_CODES.LIMIT]: "La fórmula es demasiado costosa para comprobarla aquí.",
};

export class XlError {
  /**
   * @param {string} code uno de ERROR_CODES
   * @param {string} [message] explicación para el alumno
   */
  constructor(code, message) {
    this.code = code;
    this.message = message ?? DEFAULT_MESSAGES[code] ?? "";
    Object.freeze(this);
  }

  /** true si es un error propio del motor y no de Excel. */
  get engineOnly() {
    return ENGINE_ONLY.has(this.code);
  }

  toString() {
    return this.code;
  }
}

export const isError = (value) => value instanceof XlError;

export const xlError = (code, message) => new XlError(code, message);

/** Error de sintaxis: la fórmula no se puede analizar. `position` es el índice del carácter (0 = primero). */
export class FormulaSyntaxError extends Error {
  constructor(message, position, { unsupported = false } = {}) {
    super(message);
    this.name = "FormulaSyntaxError";
    this.position = position;
    this.unsupported = unsupported;
  }
}

/** Se lanza dentro del evaluador al superar un límite; el evaluador lo convierte en un error LÍMITE. */
export class LimitExceeded extends Error {
  constructor(message) {
    super(message);
    this.name = "LimitExceeded";
  }
}
