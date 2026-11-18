/* Registro de las 45 funciones de la especificación, por su nombre canónico (inglés).

   `status` separa lo que el motor calcula (`implemented`: 8 de la v1 y 16 de M04-M05) de lo
   que todavía no
   (`planned`): una función prevista da #¿NOMBRE? con el aviso «todavía no está disponible en PLD»,
   nunca un resultado inventado. `since`: primera versión de Excel que la tiene. `lazy`: recibe
   los argumentos sin calcular (evaluator.js, lazyArgs). */

import { AVERAGEIF, COUNTIF, COUNTIFS, MAXIFS, MINIFS, SUMIF, SUMIFS } from "./conditional.js";
import { AND, IF, IFERROR, IFS, NOT, OR } from "./logical.js";
import { INT, MOD, PRODUCT, ROUND, ROUNDUP, SUM } from "./math.js";
import { AVERAGE, COUNT, COUNTA, MAX, MIN } from "./stats.js";

const ALL = "2016";

const implemented = (impl, minArgs, maxArgs, category, { lazy = false, since = ALL } = {}) =>
  ({ status: "implemented", impl, minArgs, maxArgs, since, category, lazy });
const planned = (category, module, names) =>
  Object.fromEntries(names.split(" ").map((entry) => entry.split(":")).map(([name, since = ALL]) => [name, { status: "planned", category, module, since }]));

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
  // M04
  ROUNDUP: implemented(ROUNDUP, 2, 2, "matemáticas"),
  INT: implemented(INT, 1, 1, "matemáticas"),
  MOD: implemented(MOD, 2, 2, "matemáticas"),
  IF: implemented(IF, 1, 3, "lógicas", { lazy: true }),
  AND: implemented(AND, 1, 64, "lógicas"),
  OR: implemented(OR, 1, 64, "lógicas"),
  NOT: implemented(NOT, 1, 1, "lógicas"),
  IFS: implemented(IFS, 2, 64, "lógicas", { lazy: true, since: "2019" }),
  IFERROR: implemented(IFERROR, 2, 2, "lógicas", { lazy: true }),
  // M05
  SUMIF: implemented(SUMIF, 2, 3, "condicionales", { lazy: true }),
  SUMIFS: implemented(SUMIFS, 3, 63, "condicionales", { lazy: true }),
  COUNTIF: implemented(COUNTIF, 2, 2, "condicionales", { lazy: true }),
  COUNTIFS: implemented(COUNTIFS, 2, 64, "condicionales", { lazy: true }),
  AVERAGEIF: implemented(AVERAGEIF, 2, 3, "condicionales", { lazy: true }),
  MAXIFS: implemented(MAXIFS, 3, 63, "condicionales", { lazy: true, since: "2019" }),
  MINIFS: implemented(MINIFS, 3, 63, "condicionales", { lazy: true, since: "2019" }),
  // Previstas, por módulo («NOMBRE:versión» si no está en todas)
  ...planned("texto", "M06", "CONCAT:2019 LEFT RIGHT MID LEN TRIM UPPER SEARCH"),
  ...planned("fecha", "M07", "DATE YEAR MONTH DAY EOMONTH NETWORKDAYS"),
  ...planned("búsqueda", "M08", "VLOOKUP INDEX MATCH"),
  ...planned("búsqueda", "M09", "XLOOKUP:2021"),
  ...planned("matrices dinámicas", "M09", "FILTER:2021 SORT:2021 UNIQUE:2021"),
});

/** Ficha de una función por su nombre canónico, o null si no está entre las 45. */
export const functionInfo = (name) => REGISTRY[name] ?? null;

/** «implemented», «planned» o null. */
export const functionStatus = (name) => functionInfo(name)?.status ?? null;

export const FUNCTION_LIST = Object.freeze(Object.keys(REGISTRY));
