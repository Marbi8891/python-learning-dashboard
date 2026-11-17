/* Registro de las 45 funciones de la especificación, por su nombre canónico (inglés).

   `status` separa lo que el motor calcula (`implemented`, las 8 de la v1) de lo que todavía no
   (`planned`): una función prevista da #¿NOMBRE? con el aviso «todavía no está disponible en PLD»,
   nunca un resultado inventado. `since` es la primera versión de Excel que la tiene. */

import { PRODUCT, ROUND, SUM } from "./math.js";
import { AVERAGE, COUNT, COUNTA, MAX, MIN } from "./stats.js";

const ALL = "2016";

const implemented = (impl, minArgs, maxArgs, category) => ({ status: "implemented", impl, minArgs, maxArgs, since: ALL, category });
const planned = (category, module, since = ALL) => ({ status: "planned", category, module, since });

const REGISTRY = Object.freeze({
  // Implementadas (v1, M01-M02)
  SUM: implemented(SUM, 1, 64, "matemáticas"),
  PRODUCT: implemented(PRODUCT, 1, 64, "matemáticas"),
  ROUND: implemented(ROUND, 2, 2, "matemáticas"),
  AVERAGE: implemented(AVERAGE, 1, 64, "estadísticas"),
  MIN: implemented(MIN, 1, 64, "estadísticas"),
  MAX: implemented(MAX, 1, 64, "estadísticas"),
  COUNT: implemented(COUNT, 1, 64, "estadísticas"),
  COUNTA: implemented(COUNTA, 1, 64, "estadísticas"),
  // Previstas
  ROUNDUP: planned("matemáticas", "M04"),
  INT: planned("matemáticas", "M04"),
  MOD: planned("matemáticas", "M04"),
  IF: planned("lógicas", "M04"),
  AND: planned("lógicas", "M04"),
  OR: planned("lógicas", "M04"),
  NOT: planned("lógicas", "M04"),
  IFS: planned("lógicas", "M04", "2019"),
  IFERROR: planned("lógicas", "M04"),
  SUMIF: planned("condicionales", "M05"),
  SUMIFS: planned("condicionales", "M05"),
  COUNTIF: planned("condicionales", "M05"),
  COUNTIFS: planned("condicionales", "M05"),
  AVERAGEIF: planned("condicionales", "M05"),
  MAXIFS: planned("condicionales", "M05", "2019"),
  MINIFS: planned("condicionales", "M05", "2019"),
  CONCAT: planned("texto", "M06", "2019"),
  LEFT: planned("texto", "M06"),
  RIGHT: planned("texto", "M06"),
  MID: planned("texto", "M06"),
  LEN: planned("texto", "M06"),
  TRIM: planned("texto", "M06"),
  UPPER: planned("texto", "M06"),
  SEARCH: planned("texto", "M06"),
  DATE: planned("fecha", "M07"),
  YEAR: planned("fecha", "M07"),
  MONTH: planned("fecha", "M07"),
  DAY: planned("fecha", "M07"),
  EOMONTH: planned("fecha", "M07"),
  NETWORKDAYS: planned("fecha", "M07"),
  VLOOKUP: planned("búsqueda", "M08"),
  INDEX: planned("búsqueda", "M08"),
  MATCH: planned("búsqueda", "M08"),
  XLOOKUP: planned("búsqueda", "M09", "2021"),
  FILTER: planned("matrices dinámicas", "M09", "2021"),
  SORT: planned("matrices dinámicas", "M09", "2021"),
  UNIQUE: planned("matrices dinámicas", "M09", "2021"),
});

/** Ficha de una función por su nombre canónico, o null si no está entre las 45. */
export const functionInfo = (name) => REGISTRY[name] ?? null;

/** «implemented», «planned» o null. */
export const functionStatus = (name) => functionInfo(name)?.status ?? null;

export const FUNCTION_LIST = Object.freeze(Object.keys(REGISTRY));
