/* Evaluador: interpreta el AST sobre una cuadrícula de datos, sin eval ni Function.

   Es puro: no lee el reloj, el DOM ni la red. La cuadrícula es un objeto { "Hoja1!A1": valor } (sin
   hoja, la de la fórmula) o una función de lectura. Una celda puede llevar un valor directo o
   { v, f, format }: `f` es una fórmula del autor del ejercicio, que se calcula al leerla.

   Controles (FORMULA_ENGINE_SPEC.md §7 y §11): presupuesto de pasos, tamaño máximo de rango y
   detección de ciclos con la pila de celdas que se están calculando. */

import { ERROR_CODES, isError, LimitExceeded, xlError } from "./errors.js";
import { functionInfo } from "./functions/registry.js";
import { SPANISH_NAME } from "./locale-es.js";
import { parseFormula } from "./parser.js";
import { address, parseAddress } from "./references.js";
import { DEFAULT_LIMITS } from "./tokenizer.js";
import { COMPARE, compareValues, isRange, publicValue, RangeValue, toNumber, toText } from "./values.js";

export const DEFAULT_SHEET = "Hoja1";

const cellKey = (sheet, col, row) => `${sheet.toUpperCase()}!${col},${row}`;

const prepared = new WeakMap();

/** Índice de la cuadrícula: celdas por clave normalizada y nombres de hoja. Se guarda por objeto. */
function prepareGrid(grid, defaultSheet) {
  if (typeof grid === "function") return { read: grid, sheets: null };
  let byDefault = prepared.get(grid);
  if (!byDefault) {
    byDefault = new Map();
    prepared.set(grid, byDefault);
  }
  const cached = byDefault.get(defaultSheet);
  if (cached) return cached;
  const cells = new Map();
  const sheets = new Set([defaultSheet.toUpperCase()]);
  for (const [key, value] of Object.entries(grid ?? {})) {
    const { sheet, col, row } = parseAddress(key, defaultSheet);
    sheets.add(sheet.toUpperCase());
    cells.set(cellKey(sheet, col, row), value);
  }
  const index = { read: (sheet, col, row) => cells.get(cellKey(sheet, col, row)), sheets };
  byDefault.set(defaultSheet, index);
  return index;
}

const isCellObject = (raw) => raw !== null && typeof raw === "object" && !Array.isArray(raw);

class Context {
  constructor({ grid, sheet, environment }) {
    this.limits = { ...DEFAULT_LIMITS, ...(environment?.limits ?? {}) };
    this.environment = environment ?? {};
    this.grid = prepareGrid(grid, sheet);
    this.steps = 0;
    this.stack = []; // celdas en cálculo: { sheet, col, row }
    this.memo = new Map();
  }

  step(count = 1) {
    this.steps += count;
    if (this.steps > this.limits.maxSteps) throw new LimitExceeded("La fórmula es demasiado costosa para comprobarla aquí.");
  }

  sheetExists(sheet) {
    return this.grid.sheets === null || this.grid.sheets.has(sheet.toUpperCase());
  }

  inStack(sheet, c1, r1, c2, r2) {
    const upperSheet = sheet.toUpperCase();
    return this.stack.some((cell) => cell.sheet.toUpperCase() === upperSheet && cell.col >= c1 && cell.col <= c2 && cell.row >= r1 && cell.row <= r2);
  }

  /** Valor de una celda (calcula su fórmula si la tiene). */
  readCell(sheet, col, row) {
    this.step();
    const raw = this.grid.read(sheet, col, row);
    if (!isCellObject(raw)) return raw ?? null;
    if (typeof raw.f !== "string") return raw.v ?? null;
    const key = cellKey(sheet, col, row);
    if (this.memo.has(key)) return this.memo.get(key);
    if (this.inStack(sheet, col, row, col, row)) return xlError(ERROR_CODES.CYCLE);
    let ast;
    try {
      ast = parseFormula(raw.f, { limits: this.limits });
    } catch {
      return xlError(ERROR_CODES.VALUE, `La fórmula de la celda ${sheet}!${address(col, row)} del ejercicio no es válida.`);
    }
    this.stack.push({ sheet, col, row });
    const value = scalarResult(this.evaluate(ast, sheet));
    this.stack.pop();
    this.memo.set(key, value);
    return value;
  }

  /** Evalúa un nodo. Devuelve un valor o un RangeValue. */
  evaluate(node, sheet) {
    this.step();
    switch (node.type) {
      case "Number":
      case "Text":
      case "Bool":
        return node.value;
      case "Error":
        return xlError(node.code);
      case "Missing":
        return 0;
      case "Name":
        return xlError(
          ERROR_CODES.NAME,
          `«${node.name}» no es una función, una celda ni un valor de Excel. Si es un texto, escríbelo entre comillas.`,
        );
      case "Ref":
        return this.reference(node.ref, sheet);
      case "Range":
        return this.range(node, sheet);
      case "Unary": {
        const value = scalarResult(this.evaluate(node.operand, sheet));
        if (node.op === "+") return value;
        const number = toNumber(value);
        return isError(number) ? number : -number;
      }
      case "Percent": {
        const number = toNumber(scalarResult(this.evaluate(node.operand, sheet)));
        return isError(number) ? number : number / 100;
      }
      case "Binary":
        return this.binary(node, sheet);
      case "Call":
        return this.call(node, sheet);
      default:
        return xlError(ERROR_CODES.UNSUPPORTED);
    }
  }

  reference(ref, sheet) {
    const target = ref.sheet ?? sheet;
    if (!this.sheetExists(target)) return xlError(ERROR_CODES.REF, `La hoja «${target}» no existe en este libro.`);
    if (this.inStack(target, ref.col, ref.row, ref.col, ref.row)) return xlError(ERROR_CODES.CYCLE);
    return this.readCell(target, ref.col, ref.row);
  }

  range(node, sheet) {
    const target = node.start.sheet ?? sheet;
    if (!this.sheetExists(target)) return xlError(ERROR_CODES.REF, `La hoja «${target}» no existe en este libro.`);
    const c1 = Math.min(node.start.col, node.end.col);
    const c2 = Math.max(node.start.col, node.end.col);
    const r1 = Math.min(node.start.row, node.end.row);
    const r2 = Math.max(node.start.row, node.end.row);
    if ((c2 - c1 + 1) * (r2 - r1 + 1) > this.limits.maxRangeCells) {
      throw new LimitExceeded(`El rango es demasiado grande (máximo ${this.limits.maxRangeCells} celdas).`);
    }
    if (this.inStack(target, c1, r1, c2, r2)) return xlError(ERROR_CODES.CYCLE);
    return new RangeValue({ sheet: target, c1, r1, c2, r2 }, (col, row) => this.readCell(target, col, row));
  }

  binary(node, sheet) {
    const left = scalarResult(this.evaluate(node.left, sheet));
    const right = scalarResult(this.evaluate(node.right, sheet));
    if (node.op === "&") {
      const a = toText(left);
      if (isError(a)) return a;
      const b = toText(right);
      return isError(b) ? b : a + b;
    }
    if (COMPARE[node.op]) {
      const order = compareValues(left, right);
      return isError(order) ? order : COMPARE[node.op](order);
    }
    const a = toNumber(left);
    if (isError(a)) return a;
    const b = toNumber(right);
    if (isError(b)) return b;
    if (node.op === "/" && b === 0) return xlError(ERROR_CODES.DIV0);
    if (node.op === "^" && a === 0 && b <= 0) return b === 0 ? xlError(ERROR_CODES.NUM, "0 elevado a 0 no tiene resultado en Excel.") : xlError(ERROR_CODES.DIV0);
    const result = { "+": a + b, "-": a - b, "*": a * b, "/": a / b, "^": a ** b }[node.op];
    return Number.isFinite(result) ? result : xlError(ERROR_CODES.NUM);
  }

  call(node, sheet) {
    if (node.name === null) {
      return xlError(ERROR_CODES.NAME, `${node.written} no es una función de Excel en español.`);
    }
    const info = functionInfo(node.name);
    if (info.status !== "implemented") {
      return xlError(ERROR_CODES.NAME, `${SPANISH_NAME[node.name]} todavía no está disponible en PLD.`);
    }
    if (info.lazy) return info.impl(this.lazyArgs(node.args, sheet), this);
    const args = node.args.map((arg) => {
      const value = this.evaluate(arg, sheet);
      if (isRange(value)) return { kind: "range", value };
      return { kind: arg.type === "Ref" ? "ref" : "value", value };
    });
    return info.impl(args, this);
  }

  /** Argumentos sin calcular de una función `lazy`: value(i) (puede ser un rango), scalar(i),
      range(i) (un rango o una celda; si no, #¡VALOR!) y rangeAt(hoja, c1, r1, c2, r2). */
  lazyArgs(nodes, sheet) {
    const value = (i) => this.evaluate(nodes[i], sheet);
    const rangeAt = (target, c1, r1, c2, r2) => this.range({ start: { sheet: target, col: c1, row: r1 }, end: { col: c2, row: r2 } }, sheet);
    const range = (i) => {
      const { type, ref } = nodes[i];
      if (type === "Ref") return rangeAt(ref.sheet ?? sheet, ref.col, ref.row, ref.col, ref.row);
      const result = value(i);
      return isRange(result) || isError(result) ? result : xlError(ERROR_CODES.VALUE, "Aquí va un rango de celdas, no un valor.");
    };
    return { count: nodes.length, value, scalar: (i) => scalarResult(value(i)), range, rangeAt };
  }
}

/** Un rango donde se espera un valor: si es de una celda, su valor; si no, #¡VALOR!. */
function scalarResult(value) {
  if (!isRange(value)) return value;
  if (value.rows === 1 && value.cols === 1) return value.values().next().value;
  return xlError(ERROR_CODES.VALUE, "Un rango de varias celdas no es un único valor (v1 de PLD).");
}

/**
 * Evalúa un AST.
 * @param {object} ast resultado de parseFormula
 * @param {object} options
 * @param {object|Function} options.grid cuadrícula
 * @param {string} [options.sheet] hoja de la fórmula (por defecto «Hoja1»)
 * @param {string} [options.at] celda donde está la fórmula («D2» o «Hoja1!D2»), para detectar ciclos
 * @param {object} [options.environment] { limits }
 * @returns {{type: string, value: any, message?: string}}
 */
export function evaluate(ast, { grid = {}, sheet = DEFAULT_SHEET, at = null, environment } = {}) {
  const context = new Context({ grid, sheet, environment });
  if (at) {
    const cell = parseAddress(at, sheet);
    context.stack.push(cell);
  }
  try {
    return publicValue(scalarResult(context.evaluate(ast, at ? parseAddress(at, sheet).sheet : sheet)));
  } catch (error) {
    if (error instanceof LimitExceeded) return publicValue(xlError(ERROR_CODES.LIMIT, error.message));
    throw error;
  }
}
