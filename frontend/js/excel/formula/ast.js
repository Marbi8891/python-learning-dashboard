/* Utilidades sobre el AST: recorrerlo, copiar la fórmula a otra celda y volver a escribirla. */

import { ERROR_CODES } from "./errors.js";
import { formatNumber, SPANISH_NAME } from "./locale-es.js";
import { formatRef, shiftRef } from "./references.js";

/** Llama a `visit(node)` en cada nodo, en profundidad. */
export function walk(node, visit) {
  visit(node);
  switch (node.type) {
    case "Unary":
    case "Percent":
      walk(node.operand, visit);
      break;
    case "Binary":
      walk(node.left, visit);
      walk(node.right, visit);
      break;
    case "Call":
      for (const arg of node.args) walk(arg, visit);
      break;
    default:
  }
}

function freeze(node) {
  for (const value of Object.values(node)) if (value && typeof value === "object" && !Object.isFrozen(value)) freeze(value);
  return Object.freeze(node);
}

const REF_ERROR = Object.freeze({ type: "Error", code: ERROR_CODES.REF });

function shiftNode(node, rows, cols) {
  switch (node.type) {
    case "Ref": {
      const ref = shiftRef(node.ref, rows, cols);
      return ref ? { type: "Ref", ref } : REF_ERROR;
    }
    case "Range": {
      const start = shiftRef(node.start, rows, cols);
      const end = shiftRef(node.end, rows, cols);
      return start && end ? { type: "Range", start, end } : REF_ERROR;
    }
    case "Unary":
      return { ...node, operand: shiftNode(node.operand, rows, cols) };
    case "Percent":
      return { ...node, operand: shiftNode(node.operand, rows, cols) };
    case "Binary":
      return { ...node, left: shiftNode(node.left, rows, cols), right: shiftNode(node.right, rows, cols) };
    case "Call":
      return { ...node, args: node.args.map((arg) => shiftNode(arg, rows, cols)) };
    default:
      return node;
  }
}

/**
 * La fórmula copiada `rows` filas abajo y `cols` columnas a la derecha (negativos: arriba o a la
 * izquierda). Respeta los $; una referencia que se sale de la hoja pasa a ser #¡REF!, como en Excel.
 */
export function shiftFormula(ast, { rows = 0, cols = 0 } = {}) {
  return freeze(shiftNode(ast, rows, cols));
}

const PRECEDENCE = { "=": 1, "<>": 1, "<": 1, ">": 1, "<=": 1, ">=": 1, "&": 2, "+": 3, "-": 3, "*": 4, "/": 4, "^": 5 };

function precedence(node) {
  if (node.type === "Binary") return PRECEDENCE[node.op];
  if (node.type === "Percent") return 6;
  if (node.type === "Unary") return 7;
  return 8;
}

function print(node) {
  switch (node.type) {
    case "Number":
      return formatNumber(node.value);
    case "Text":
      return `"${node.value.replaceAll('"', '""')}"`;
    case "Bool":
      return node.value ? "VERDADERO" : "FALSO";
    case "Error":
      return node.code;
    case "Missing":
      return "";
    case "Name":
      return node.name;
    case "Ref":
      return formatRef(node.ref);
    case "Range":
      return `${formatRef(node.start)}:${formatRef(node.end, { withSheet: false })}`;
    case "Unary": {
      const inner = print(node.operand);
      return node.op + (precedence(node.operand) < 7 ? `(${inner})` : inner);
    }
    case "Percent": {
      const inner = print(node.operand);
      return `${precedence(node.operand) < 6 ? `(${inner})` : inner}%`;
    }
    case "Binary": {
      const p = PRECEDENCE[node.op];
      const left = print(node.left);
      const right = print(node.right);
      const l = precedence(node.left) < p ? `(${left})` : left;
      const r = precedence(node.right) <= p ? `(${right})` : right;
      return `${l}${node.op}${r}`;
    }
    case "Call":
      return `${node.name ? SPANISH_NAME[node.name] : node.written}(${node.args.map(print).join(";")})`;
    default:
      return "";
  }
}

/** Vuelve a escribir la fórmula en español, con «=» delante. */
export const toFormula = (ast) => `=${print(ast)}`;
