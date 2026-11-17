/* Español de España (Excel 365 es-ES): nombres de funciones, booleanos y números.

   El motor trabaja con el nombre inglés canónico de cada función (el que guarda un .xlsx); aquí se
   traduce del español. Argumentos separados por «;» y coma decimal, como en Excel en español. */

/** Nombre en español → nombre canónico. Son las 45 funciones de la especificación. */
export const FUNCTION_NAMES = Object.freeze({
  // Matemáticas
  SUMA: "SUM",
  PRODUCTO: "PRODUCT",
  REDONDEAR: "ROUND",
  "REDONDEAR.MAS": "ROUNDUP",
  ENTERO: "INT",
  RESIDUO: "MOD",
  // Estadísticas
  PROMEDIO: "AVERAGE",
  MIN: "MIN",
  MAX: "MAX",
  CONTAR: "COUNT",
  CONTARA: "COUNTA",
  // Lógicas
  SI: "IF",
  Y: "AND",
  O: "OR",
  NO: "NOT",
  "SI.CONJUNTO": "IFS",
  "SI.ERROR": "IFERROR",
  // Condicionales
  "SUMAR.SI": "SUMIF",
  "SUMAR.SI.CONJUNTO": "SUMIFS",
  "CONTAR.SI": "COUNTIF",
  "CONTAR.SI.CONJUNTO": "COUNTIFS",
  "PROMEDIO.SI": "AVERAGEIF",
  "MAX.SI.CONJUNTO": "MAXIFS",
  "MIN.SI.CONJUNTO": "MINIFS",
  // Texto
  CONCAT: "CONCAT",
  IZQUIERDA: "LEFT",
  DERECHA: "RIGHT",
  EXTRAE: "MID",
  LARGO: "LEN",
  ESPACIOS: "TRIM",
  MAYUSC: "UPPER",
  HALLAR: "SEARCH",
  // Fecha
  FECHA: "DATE",
  AÑO: "YEAR",
  MES: "MONTH",
  DIA: "DAY",
  "FIN.MES": "EOMONTH",
  "DIAS.LAB": "NETWORKDAYS",
  // Búsqueda y referencia
  BUSCARV: "VLOOKUP",
  INDICE: "INDEX",
  COINCIDIR: "MATCH",
  BUSCARX: "XLOOKUP",
  // Matrices dinámicas
  FILTRAR: "FILTER",
  ORDENAR: "SORT",
  UNICOS: "UNIQUE",
});

/** Nombre canónico → nombre en español (para mostrar). */
export const SPANISH_NAME = Object.freeze(
  Object.fromEntries(Object.entries(FUNCTION_NAMES).map(([es, en]) => [en, es])),
);

export const TRUE_WORD = "VERDADERO";
export const FALSE_WORD = "FALSO";
export const ARG_SEPARATOR = ";";
export const DECIMAL_SEPARATOR = ",";

export const upper = (text) => text.toUpperCase();

/** Nombre canónico de una función escrita en español, o null si no es ninguna de las 45. */
export function canonicalName(name) {
  return FUNCTION_NAMES[upper(name)] ?? null;
}

const isDigit = (ch) => ch >= "0" && ch <= "9";

/**
 * Lee un número escrito en español al principio de `text` desde `start`.
 * Devuelve { value, end } o null. Acepta «3», «3,5», «,5», «1,5E3», «2E-2».
 */
export function readNumber(text, start = 0) {
  let i = start;
  let digits = "";
  while (i < text.length && isDigit(text[i])) digits += text[i++];
  let decimals = "";
  if (text[i] === DECIMAL_SEPARATOR && isDigit(text[i + 1] ?? "")) {
    i += 1;
    while (i < text.length && isDigit(text[i])) decimals += text[i++];
  }
  if (!digits && !decimals) return null;
  let exponent = "";
  if ((text[i] === "E" || text[i] === "e") && i + 1 < text.length) {
    let j = i + 1;
    let sign = "";
    if (text[j] === "+" || text[j] === "-") sign = text[j++];
    let expDigits = "";
    while (j < text.length && isDigit(text[j])) expDigits += text[j++];
    if (expDigits) {
      exponent = `e${sign}${expDigits}`;
      i = j;
    }
  }
  return { value: Number(`${digits || "0"}.${decimals || "0"}${exponent}`), end: i };
}

/**
 * Convierte un texto en número como hace Excel en español al operar con él
 * («3,5» → 3,5; « -2 » → -2; «50%» → 0,5). Devuelve null si el texto no es un número.
 */
export function parseSpanishNumber(text) {
  const source = text.trim();
  let i = 0;
  let sign = 1;
  if (source[i] === "-" || source[i] === "+") {
    if (source[i] === "-") sign = -1;
    i += 1;
  }
  const number = readNumber(source, i);
  if (!number) return null;
  let value = sign * number.value;
  i = number.end;
  if (source[i] === "%") {
    value /= 100;
    i += 1;
  }
  return i === source.length ? value : null;
}

/** Un número como texto, como lo concatena Excel en español: hasta 15 cifras y coma decimal. */
export function formatNumber(value) {
  if (Object.is(value, -0)) return "0";
  const rounded = Number(value.toPrecision(15));
  let text = String(rounded);
  if (text.includes("e")) {
    const [mantissa, exp] = text.split("e");
    const sign = exp.startsWith("-") ? "-" : "+";
    const digits = exp.replace(/^[+-]/, "").padStart(2, "0");
    text = `${mantissa}E${sign}${digits}`;
  }
  return text.replace(".", DECIMAL_SEPARATOR);
}
