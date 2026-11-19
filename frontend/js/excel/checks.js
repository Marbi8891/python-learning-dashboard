/* Corrección de los ejercicios de Excel profesional (docs/excel-academy/CURRICULUM_M1_M2.md §4).

   - `formula-result`: el alumno escribe (o elige) lo que devuelve una fórmula dada.
   - `formula`: el alumno escribe la fórmula; se comprueba lo que hace, no cómo está escrita:
     su valor, que funcione al copiarla, que funcione con otros datos y, si el ejercicio lo pide,
     qué referencias y funciones usa y que no lleve números escritos a mano.

   La corrección es formativa: la solución está en el JSON público del curso (DA-14).
   Todo es puro: lo usan la web y el generador (scripts/courses/excel/eval.mjs). */

import { parseSpanishNumber } from "./formula/locale-es.js";
import { evaluate, FormulaSyntaxError, formatRef, parseAddress, parseFormula, shiftFormula, walk } from "./formula/index.js";

export const DEFAULT_TOLERANCE = 0.005;
export const MAX_GRID_CELLS = 200;
export const CHECK_TYPES = Object.freeze(["value", "fill", "variants", "references", "noConstants", "functions"]);

const DEFAULT_SHEET = "Hoja1";

/* ---------- Comparar resultados ---------- */

/** ¿El resultado del motor ({ type, value }) es el esperado? `expected`: número, texto, booleano o { error }. */
export function sameValue(actual, expected, tolerance = DEFAULT_TOLERANCE) {
  if (!actual) return false;
  if (expected !== null && typeof expected === "object" && "error" in expected) {
    return actual.type === "error" && actual.value === expected.error;
  }
  if (typeof expected === "number") return actual.type === "number" && Math.abs(actual.value - expected) <= tolerance + 1e-12;
  if (typeof expected === "boolean") return actual.type === "boolean" && actual.value === expected;
  if (typeof expected === "string") {
    return actual.type === "text" && actual.value.trim().toUpperCase() === expected.trim().toUpperCase();
  }
  return false;
}

/** Texto de un resultado para los mensajes, en español. */
export function describe(result) {
  if (!result) return "";
  if (result.type === "number") return String(Number(result.value.toPrecision(15))).replace(".", ",");
  if (result.type === "boolean") return result.value ? "VERDADERO" : "FALSO";
  if (result.type === "error") return result.value;
  return `«${result.value}»`;
}

/* ---------- Celdas y rangos ---------- */

function cellsBetween(fromKey, toKey, sheet) {
  const from = parseAddress(fromKey, sheet);
  const to = parseAddress(toKey, sheet);
  const cells = [];
  for (let row = Math.min(from.row, to.row); row <= Math.max(from.row, to.row); row += 1) {
    for (let col = Math.min(from.col, to.col); col <= Math.max(from.col, to.col); col += 1) {
      if (col !== from.col || row !== from.row) cells.push({ sheet: from.sheet, col, row, rows: row - from.row, cols: col - from.col });
    }
  }
  return cells;
}

const keyOf = (cell) => `${cell.sheet}!${formatRef({ ...cell, colAbs: false, rowAbs: false, sheet: null })}`;

/* ---------- Datos distintos (variantes) ---------- */

function hashString(text) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/** Generador pseudoaleatorio con semilla (mulberry32): mismas variantes en la web y en el generador. */
function random(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const rawNumber = (raw) => (typeof raw === "number" ? raw : raw && typeof raw === "object" && typeof raw.v === "number" && raw.f === undefined ? raw.v : null);

function inVary(key, vary, sheet) {
  if (!vary) return true;
  const cell = parseAddress(key, sheet);
  return vary.some((spec) => {
    const [a, b = a] = spec.split(":");
    const start = parseAddress(a, sheet);
    const end = parseAddress(b.includes("!") ? b : `${start.sheet}!${b}`, sheet);
    return (
      cell.sheet.toUpperCase() === start.sheet.toUpperCase() &&
      cell.col >= Math.min(start.col, end.col) &&
      cell.col <= Math.max(start.col, end.col) &&
      cell.row >= Math.min(start.row, end.row) &&
      cell.row <= Math.max(start.row, end.row)
    );
  });
}

/** La cuadrícula con los números cambiados (entre la mitad y vez y media), con semilla. */
export function variantGrid(question, index) {
  const sheet = question.sheet ?? DEFAULT_SHEET;
  const next = random(hashString(`${question.id}#${index}`));
  const grid = {};
  for (const [key, raw] of Object.entries(question.grid)) {
    const number = rawNumber(raw);
    if (number === null || number === 0 || !inVary(key, question.vary, sheet)) {
      grid[key] = raw;
      continue;
    }
    const factor = 0.5 + next();
    const changed = Number.isInteger(number) ? Math.max(1, Math.round(number * factor)) * Math.sign(number) : Math.round(number * factor * 100) / 100 || number;
    grid[key] = typeof raw === "number" ? changed : { ...raw, v: changed };
  }
  return grid;
}

/* ---------- Referencias, números y funciones de la fórmula ---------- */

function referencesOf(ast) {
  const found = new Set();
  walk(ast, (node) => {
    if (node.type === "Ref") {
      found.add(formatRef(node.ref).toUpperCase());
      found.add(formatRef(node.ref, { withSheet: false }).toUpperCase());
    }
    if (node.type === "Range") {
      const start = formatRef(node.start, { withSheet: false }).toUpperCase();
      const end = formatRef(node.end, { withSheet: false }).toUpperCase();
      found.add(`${start}:${end}`);
      found.add(`${formatRef(node.start).toUpperCase()}:${end}`);
      found.add(start);
      found.add(end);
    }
  });
  return found;
}

function constantsOf(ast) {
  const numbers = [];
  walk(ast, (node) => {
    if (node.type === "Number") numbers.push(node.value);
  });
  return numbers;
}

function functionsOf(ast) {
  const names = new Set();
  walk(ast, (node) => {
    if (node.type === "Call" && node.name) names.add(node.name);
  });
  return names;
}

/* ---------- Comprobar una fórmula ---------- */

const MESSAGES = {
  value: (got, want) => `El resultado es ${got} y debería ser ${want}.`,
  fill: (cell, got, want) => `Al copiarla, en ${cell} da ${got} y debería dar ${want}. Revisa qué referencias tienen que quedarse fijas con $.`,
  variants: () => "Con otros datos la fórmula ya no da el resultado correcto: no escribas a mano los resultados, usa las celdas.",
  references: (missing) => `Tu fórmula tiene que usar ${missing}${missing.includes("$") ? " (fija la celda con $, tecla F4)" : ""}.`,
  forbiddenRef: (ref) => `Tu fórmula no debería usar ${ref}.`,
  noConstants: (n) => `Hay un número escrito a mano en la fórmula (${String(n).replace(".", ",")}). Usa la celda que lo contiene.`,
  requires: (name) => `Este ejercicio se resuelve con ${name}.`,
  forbid: (name) => `En este ejercicio no se usa ${name}.`,
};

function evalAt(ast, grid, sheet, at, environment) {
  return evaluate(ast, { grid, sheet, at, environment });
}

/**
 * Comprueba la fórmula del alumno.
 * @returns {{ ok: boolean, needsEquals?: boolean, syntax?: {message: string, position: number, unsupported: boolean},
 *   value?: object, results: Array<{type: string, kind: string, ok: boolean, message: string}>, message: string }}
 */
export function checkFormula(question, input, { environment, spanishName = (n) => n } = {}) {
  const text = String(input ?? "").trim();
  const sheet = question.sheet ?? DEFAULT_SHEET;
  if (!text.startsWith("=")) {
    return { ok: false, needsEquals: true, results: [], message: "Una fórmula empieza por «=». Escríbelo delante." };
  }
  let ast;
  try {
    ast = parseFormula(text, { limits: environment?.limits });
  } catch (error) {
    if (!(error instanceof FormulaSyntaxError)) throw error;
    const syntax = { message: error.message, position: error.position, unsupported: error.unsupported };
    return { ok: false, syntax, results: [], message: `${error.message} (carácter ${error.position + 1})` };
  }
  let solution = null;
  const solutionAst = () => {
    if (!solution) solution = parseFormula(question.solution.formula);
    return solution;
  };
  const tolerance = question.tolerance ?? DEFAULT_TOLERANCE;
  const value = evalAt(ast, question.grid, sheet, question.cell, environment);
  const results = [];
  const fillCheck = question.checks.find((c) => c.type === "fill");

  for (const check of question.checks) {
    const kind = check.kind ?? (["references", "noConstants", "functions"].includes(check.type) ? "procedure" : "result");
    const result = { type: check.type, kind, ok: true, message: "" };
    switch (check.type) {
      case "value": {
        const expected = check.expect ?? question.expect;
        result.ok = sameValue(value, expected, tolerance);
        if (!result.ok) result.message = MESSAGES.value(describe(value), describe(expectedResult(expected)));
        break;
      }
      case "fill": {
        const cells = cellsBetween(question.cell, check.to, sheet);
        for (const [i, cell] of cells.entries()) {
          const at = keyOf(cell);
          const got = evalAt(shiftFormula(ast, cell), question.grid, sheet, at, environment);
          const want = check.expect
            ? expectedResult(check.expect[i])
            : evalAt(shiftFormula(solutionAst(), cell), question.grid, sheet, at, environment);
          const ok = check.expect ? sameValue(got, check.expect[i], tolerance) : sameResult(got, want, tolerance);
          if (!ok) {
            result.ok = false;
            result.message = MESSAGES.fill(at.split("!")[1], describe(got), describe(want));
            break;
          }
        }
        break;
      }
      case "variants": {
        for (let i = 0; i < (check.count ?? 2) && result.ok; i += 1) {
          const grid = variantGrid(question, i);
          const targets = [{ rows: 0, cols: 0, at: question.cell }];
          if (fillCheck) for (const cell of cellsBetween(question.cell, fillCheck.to, sheet)) targets.push({ ...cell, at: keyOf(cell) });
          for (const target of targets) {
            const got = evalAt(shiftFormula(ast, target), grid, sheet, target.at, environment);
            const want = evalAt(shiftFormula(solutionAst(), target), grid, sheet, target.at, environment);
            if (!sameResult(got, want, tolerance)) {
              result.ok = false;
              result.message = MESSAGES.variants();
              break;
            }
          }
        }
        break;
      }
      case "references": {
        const used = referencesOf(ast);
        const missing = (check.must ?? []).find((ref) => !used.has(ref.toUpperCase()));
        const forbidden = (check.mustNot ?? []).find((ref) => used.has(ref.toUpperCase()));
        if (missing) {
          result.ok = false;
          result.message = MESSAGES.references(missing);
        } else if (forbidden) {
          result.ok = false;
          result.message = MESSAGES.forbiddenRef(forbidden);
        }
        break;
      }
      case "noConstants": {
        const allowed = check.except ?? [];
        const extra = constantsOf(ast).find((n) => !allowed.includes(n));
        if (extra !== undefined) {
          result.ok = false;
          result.message = MESSAGES.noConstants(extra);
        }
        break;
      }
      case "functions": {
        const used = functionsOf(ast);
        const missing = (check.requires ?? []).find((name) => !used.has(name));
        const forbidden = (check.forbid ?? []).find((name) => used.has(name));
        if (missing) {
          result.ok = false;
          result.message = MESSAGES.requires(spanishName(missing));
        } else if (forbidden) {
          result.ok = false;
          result.message = MESSAGES.forbid(spanishName(forbidden));
        }
        break;
      }
      default:
        throw new Error(`Comprobación desconocida: ${check.type}`);
    }
    if (!result.ok && check.message) result.message = check.message;
    results.push(result);
  }
  const first = results.find((r) => !r.ok);
  return { ok: !first, value, results, message: first ? first.message : "¡Correcto!" };
}

function expectedResult(expected) {
  if (expected !== null && typeof expected === "object" && "error" in expected) return { type: "error", value: expected.error };
  if (typeof expected === "number") return { type: "number", value: expected };
  if (typeof expected === "boolean") return { type: "boolean", value: expected };
  return { type: "text", value: String(expected) };
}

function sameResult(a, b, tolerance) {
  if (a.type !== b.type) return false;
  if (a.type === "number") return Math.abs(a.value - b.value) <= tolerance + 1e-12;
  if (a.type === "text") return a.value.trim().toUpperCase() === b.value.trim().toUpperCase();
  return a.value === b.value;
}

/* ---------- «¿Qué devuelve esta fórmula?» ---------- */

/** Lee lo que escribió el alumno: número con coma o punto, VERDADERO/FALSO o texto. */
export function parseAnswer(text, input) {
  const clean = String(text ?? "").trim();
  if (input === "number") {
    const normalized = clean.includes(",") ? clean.replaceAll(" ", "") : clean.replaceAll(" ", "").replace(".", ",");
    return parseSpanishNumber(normalized);
  }
  return clean;
}

/**
 * Corrige una respuesta de `formula-result`. `given` es el índice elegido (input «choice») o el texto
 * escrito («number» o «text»).
 */
export function checkResult(question, given) {
  if (question.input === "choice") {
    const ok = Number(given) === question.answer;
    return { ok, message: ok ? "¡Correcto!" : "No es esa. Fíjate en cómo trata la función cada celda." };
  }
  const answer = parseAnswer(given, question.input);
  if (answer === null || answer === "") return { ok: false, empty: true, message: "Escribe un número, por ejemplo 12,5." };
  const tolerance = question.tolerance ?? DEFAULT_TOLERANCE;
  const ok =
    question.input === "number"
      ? Math.abs(answer - question.answer) <= tolerance + 1e-12
      : String(answer).toUpperCase() === String(question.answer).trim().toUpperCase();
  return { ok, message: ok ? "¡Correcto!" : "No es ese resultado." };
}

/* ---------- Comprobaciones del generador ---------- */

function roundDigitsOf(ast) {
  const digits = [];
  walk(ast, (node) => {
    if (node.type === "Call" && node.name === "ROUND" && node.args[1]?.type === "Number") digits.push(node.args[1].value);
  });
  return digits;
}

/**
 * Comprueba que un ejercicio está bien hecho antes de publicarlo. Devuelve la lista de problemas
 * (vacía si está bien). La usa el generador del curso con Node.
 */
export function verifyQuestion(question) {
  const problems = [];
  const sheet = question.sheet ?? DEFAULT_SHEET;
  const id = question.id ?? "(sin id)";
  if (!question.grid || typeof question.grid !== "object") return [`${id}: falta la cuadrícula (grid)`];
  if (Object.keys(question.grid).length > MAX_GRID_CELLS) problems.push(`${id}: la cuadrícula tiene más de ${MAX_GRID_CELLS} celdas`);
  try {
    for (const key of Object.keys(question.grid)) parseAddress(key, sheet);
  } catch (error) {
    problems.push(`${id}: ${error.message}`);
    return problems;
  }

  if (question.kind === "formula-result") {
    let result;
    try {
      result = evaluate(parseFormula(question.formula), { grid: question.grid, sheet, at: question.cell ?? null });
    } catch (error) {
      return [...problems, `${id}: la fórmula del enunciado no es válida: ${error.message}`];
    }
    if (question.input === "choice") {
      const options = question.options ?? [];
      if (!(question.answer >= 0 && question.answer < options.length)) problems.push(`${id}: respuesta fuera de las opciones`);
      const matching = options.filter((option) => sameValue(result, option, question.tolerance ?? DEFAULT_TOLERANCE));
      if (matching.length !== 1 || !sameValue(result, options[question.answer], question.tolerance ?? DEFAULT_TOLERANCE)) {
        problems.push(`${id}: el motor da ${describe(result)} y tiene que coincidir solo con la opción correcta`);
      }
    } else if (question.input === "number" || question.input === "text") {
      if (!sameValue(result, question.answer, question.tolerance ?? DEFAULT_TOLERANCE)) {
        problems.push(`${id}: el motor da ${describe(result)} y la respuesta escrita es ${String(question.answer)}`);
      }
    } else {
      problems.push(`${id}: input desconocido ${question.input}`);
    }
    return problems;
  }

  if (question.kind !== "formula") return [...problems, `${id}: tipo desconocido ${question.kind}`];
  if (!question.cell) problems.push(`${id}: falta la celda (cell)`);
  else if (Object.keys(question.grid).some((key) => keyOf(parseAddress(key, sheet)) === keyOf(parseAddress(question.cell, sheet)))) {
    problems.push(`${id}: la celda ${question.cell} tiene que estar vacía en la cuadrícula`);
  }
  if (!Array.isArray(question.checks) || question.checks.length === 0) problems.push(`${id}: faltan las comprobaciones`);
  for (const check of question.checks ?? []) if (!CHECK_TYPES.includes(check.type)) problems.push(`${id}: comprobación desconocida ${check.type}`);
  if (!question.solution?.formula) problems.push(`${id}: falta la solución`);
  if (!question.hints?.length) problems.push(`${id}: falta al menos una pista`);
  const formulaMistakes = (question.mistakes ?? []).filter((m) => String(m.error).trim().startsWith("="));
  if (formulaMistakes.length === 0) problems.push(`${id}: falta al menos un error frecuente que sea una fórmula`);
  if (problems.length) return problems;

  const tolerance = question.tolerance ?? DEFAULT_TOLERANCE;
  for (const digits of roundDigitsOf(parseFormula(question.solution.formula))) {
    if (tolerance >= 0.5 * 10 ** -digits) problems.push(`${id}: la tolerancia ${tolerance} deja pasar resultados sin redondear a ${digits} decimales`);
  }
  const solved = checkFormula(question, question.solution.formula);
  if (!solved.ok) problems.push(`${id}: la solución no pasa sus comprobaciones: ${solved.message}`);
  for (const mistake of formulaMistakes) {
    if (checkFormula(question, mistake.error).ok) problems.push(`${id}: el error frecuente ${mistake.error} pasa todas las comprobaciones`);
  }
  return problems;
}
