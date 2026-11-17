/* Referencias de celda: A1, $A$1, A$1, $A1, rangos y hojas; y su desplazamiento al copiar.

   Una referencia es { sheet, col, row, colAbs, rowAbs }, con col y row empezando en 1. `sheet` es
   null cuando la fórmula no la escribe (es la hoja de la propia fórmula). */

export const MAX_COL = 16384; // XFD
export const MAX_ROW = 1048576;

const isLetter = (ch) => ch >= "A" && ch <= "Z";
const isDigit = (ch) => ch >= "0" && ch <= "9";

/** «A» → 1, «Z» → 26, «AA» → 27, «XFD» → 16384. */
export function columnIndex(letters) {
  let n = 0;
  for (const ch of letters) n = n * 26 + (ch.charCodeAt(0) - 64);
  return n;
}

/** 1 → «A», 27 → «AA». */
export function columnLetters(index) {
  let n = index;
  let out = "";
  while (n > 0) {
    const rest = (n - 1) % 26;
    out = String.fromCharCode(65 + rest) + out;
    n = Math.floor((n - 1) / 26);
  }
  return out;
}

/**
 * Analiza una dirección de celda sin hoja («B2», «$E$1»). Devuelve la referencia o null si el texto no
 * es una celda válida. No acepta minúsculas: quien llama pasa el texto en mayúsculas.
 */
export function parseCell(text) {
  let i = 0;
  const colAbs = text[i] === "$";
  if (colAbs) i += 1;
  let letters = "";
  while (i < text.length && isLetter(text[i])) letters += text[i++];
  const rowAbs = text[i] === "$";
  if (rowAbs) i += 1;
  let digits = "";
  while (i < text.length && isDigit(text[i])) digits += text[i++];
  if (i !== text.length || !letters || letters.length > 3 || !digits || digits[0] === "0") return null;
  const col = columnIndex(letters);
  const row = Number(digits);
  if (col > MAX_COL || row > MAX_ROW) return null;
  return { sheet: null, col, row, colAbs, rowAbs };
}

/** Nombre de hoja como se escribe en una fórmula: entre comillas si hace falta. */
export function sheetPrefix(sheet) {
  if (sheet === null || sheet === undefined) return "";
  let plain = sheet.length > 0;
  for (const ch of sheet) {
    const ok = isLetter(ch.toUpperCase()) || isDigit(ch) || ch === "_" || ch === "." || ch.toUpperCase() !== ch.toLowerCase();
    if (!ok) plain = false;
  }
  if (plain && isDigit(sheet[0])) plain = false;
  return plain ? `${sheet}!` : `'${sheet.replaceAll("'", "''")}'!`;
}

/** Texto de una referencia: «$E$1», «Enero!B5». */
export function formatRef(ref, { withSheet = true } = {}) {
  const cell = `${ref.colAbs ? "$" : ""}${columnLetters(ref.col)}${ref.rowAbs ? "$" : ""}${ref.row}`;
  return withSheet ? sheetPrefix(ref.sheet) + cell : cell;
}

/** Dirección sin dólares («B2»), útil como clave de la cuadrícula. */
export const address = (col, row) => `${columnLetters(col)}${row}`;

/**
 * Clave de cuadrícula «Hoja!A1» → { sheet, col, row }. Sin hoja, usa `defaultSheet`.
 * Las comillas del nombre de hoja son opcionales en las claves.
 */
export function parseAddress(key, defaultSheet) {
  const bang = key.lastIndexOf("!");
  let sheet = defaultSheet;
  let cell = key;
  if (bang >= 0) {
    sheet = key.slice(0, bang);
    if (sheet.startsWith("'") && sheet.endsWith("'")) sheet = sheet.slice(1, -1).replaceAll("''", "'");
    cell = key.slice(bang + 1);
  }
  const ref = parseCell(cell.toUpperCase().replaceAll("$", ""));
  if (!ref) throw new Error(`Dirección de celda no válida: ${key}`);
  return { sheet, col: ref.col, row: ref.row };
}

/** Desplaza una referencia al copiar la fórmula `rows` filas y `cols` columnas. null si sale de la hoja. */
export function shiftRef(ref, rows, cols) {
  const col = ref.colAbs ? ref.col : ref.col + cols;
  const row = ref.rowAbs ? ref.row : ref.row + rows;
  if (col < 1 || row < 1 || col > MAX_COL || row > MAX_ROW) return null;
  return { ...ref, col, row };
}
