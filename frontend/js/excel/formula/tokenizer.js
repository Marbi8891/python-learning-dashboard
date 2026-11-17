/* Analizador léxico: recorre la fórmula carácter a carácter (una máquina de estados, sin expresiones
   regulares) y la convierte en una lista de tokens con su posición. */

import { FormulaSyntaxError, LITERAL_ERRORS } from "./errors.js";
import { FALSE_WORD, readNumber, TRUE_WORD, upper } from "./locale-es.js";
import { parseCell } from "./references.js";

export const DEFAULT_LIMITS = Object.freeze({
  maxLength: 2000,
  maxTokens: 1000,
  maxDepth: 32,
  maxArgs: 64,
  maxRangeCells: 10000,
  maxSteps: 100000,
  maxCellsPerExercise: 500,
});

const isDigit = (ch) => ch >= "0" && ch <= "9";
const isLetter = (ch) => ch !== undefined && ch.toUpperCase() !== ch.toLowerCase();
const isWordStart = (ch) => isLetter(ch) || ch === "_" || ch === "$";
const isWordChar = (ch) => isWordStart(ch) || isDigit(ch) || ch === ".";
const isSpace = (ch) => ch === " " || ch === "\t" || ch === "\n" || ch === "\r" || ch === " ";

const TWO_CHAR_OPS = ["<=", ">=", "<>"];
const ONE_CHAR_OPS = "+-*/^&%=<>";

/**
 * @param {string} text fórmula sin el «=» inicial
 * @param {number} offset posición de `text` dentro de la fórmula original (para los mensajes)
 * @param {object} [limits]
 */
export function tokenize(text, offset = 0, limits = DEFAULT_LIMITS) {
  const tokens = [];
  let i = 0;
  const fail = (message, at = i, options) => {
    throw new FormulaSyntaxError(message, offset + at, options);
  };
  const push = (token, start) => {
    tokens.push({ ...token, pos: offset + start });
    if (tokens.length > limits.maxTokens) fail("La fórmula es demasiado larga.", start);
  };

  const readCellAfterSheet = (sheet, start) => {
    let word = "";
    while (i < text.length && isWordChar(text[i])) word += text[i++];
    const ref = parseCell(upper(word));
    if (!ref) fail(`Después de «${sheet}!» tiene que ir una celda, como ${sheet}!A1.`, start);
    push({ type: "ref", ref: { ...ref, sheet } }, start);
  };

  while (i < text.length) {
    const ch = text[i];
    const start = i;

    if (isSpace(ch)) {
      i += 1;
      continue;
    }

    if (isDigit(ch) || (ch === "," && isDigit(text[i + 1] ?? ""))) {
      const number = readNumber(text, i);
      if (!number) fail("Número mal escrito.");
      i = number.end;
      if (isWordStart(text[i] ?? "")) fail("Número mal escrito: sobra texto pegado al número.", start);
      push({ type: "number", value: number.value }, start);
      continue;
    }

    if (ch === '"') {
      let value = "";
      i += 1;
      for (;;) {
        if (i >= text.length) fail("Falta cerrar las comillas del texto.", start);
        if (text[i] === '"') {
          if (text[i + 1] === '"') {
            value += '"';
            i += 2;
            continue;
          }
          i += 1;
          break;
        }
        value += text[i++];
      }
      push({ type: "string", value }, start);
      continue;
    }

    if (ch === "'") {
      let sheet = "";
      i += 1;
      for (;;) {
        if (i >= text.length) fail("Falta cerrar la comilla del nombre de la hoja.", start);
        if (text[i] === "'") {
          if (text[i + 1] === "'") {
            sheet += "'";
            i += 2;
            continue;
          }
          i += 1;
          break;
        }
        sheet += text[i++];
      }
      if (text[i] !== "!") fail("Después del nombre de la hoja entre comillas va «!».", i);
      if (!sheet) fail("El nombre de la hoja está vacío.", start);
      i += 1;
      readCellAfterSheet(sheet, start);
      continue;
    }

    if (ch === "#") {
      const literal = LITERAL_ERRORS.find((code) => text.startsWith(code, i) || upper(text.slice(i, i + code.length)) === code);
      if (!literal) fail("Error escrito de forma no válida.");
      i += literal.length;
      push({ type: "error", value: literal }, start);
      continue;
    }

    if (isWordStart(ch)) {
      let word = "";
      while (i < text.length && isWordChar(text[i])) word += text[i++];
      const name = upper(word);
      if (text[i] === "(") {
        if (word.includes("$")) fail(`«${word}» no es un nombre de función válido.`, start);
        push({ type: "func", name }, start);
        continue;
      }
      if (text[i] === "!") {
        if (word.includes("$")) fail(`«${word}» no es un nombre de hoja válido.`, start);
        i += 1;
        readCellAfterSheet(word, start);
        continue;
      }
      const ref = parseCell(name);
      if (ref) {
        push({ type: "ref", ref }, start);
        continue;
      }
      if (name === TRUE_WORD || name === FALSE_WORD) {
        push({ type: "bool", value: name === TRUE_WORD }, start);
        continue;
      }
      if (word.includes("$")) fail(`«${word}» no es una referencia válida.`, start);
      push({ type: "name", value: word }, start);
      continue;
    }

    const two = text.slice(i, i + 2);
    if (TWO_CHAR_OPS.includes(two)) {
      i += 2;
      push({ type: "op", value: two }, start);
      continue;
    }
    if (ONE_CHAR_OPS.includes(ch)) {
      i += 1;
      push({ type: "op", value: ch }, start);
      continue;
    }

    switch (ch) {
      case "(":
        i += 1;
        push({ type: "lparen" }, start);
        continue;
      case ")":
        i += 1;
        push({ type: "rparen" }, start);
        continue;
      case ";":
        i += 1;
        push({ type: "sep" }, start);
        continue;
      case ":":
        i += 1;
        push({ type: "colon" }, start);
        continue;
      case ",":
        fail("En Excel en español los argumentos se separan con «;» y la coma es el separador decimal.");
        break;
      case "{":
        fail("Las constantes matriciales {…} todavía no están soportadas en PLD.", i, { unsupported: true });
        break;
      case "[":
        fail("Las referencias a otros libros y las referencias de tabla […] todavía no están soportadas en PLD.", i, {
          unsupported: true,
        });
        break;
      case "@":
        fail("El operador @ todavía no está soportado en PLD.", i, { unsupported: true });
        break;
      default:
        fail(`Carácter no válido: «${ch}».`);
    }
  }
  tokens.push({ type: "eof", pos: offset + text.length });
  return tokens;
}
