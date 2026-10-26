/* Documento de XP, racha y logros de la web (clave pld:game y /api/course-state/game).
   Funciones puras (sin DOM ni localStorage): las usa game.js y se prueban con node --test. */

const ID = /^[a-z0-9][a-z0-9_-]{0,60}$/;
const DAY = /^\d{4}-\d{2}-\d{2}$/;
const MAX_ITEMS = 2000; // muy por encima de lo real (27 lecciones, 20 logros, años de días)
const LISTS = ["read", "passed", "tried", "firstTry", "challenges", "badges"];
const FLAGS = ["firstRun", "bugHunter", "lastRunFailed"];

export function emptyGame() {
  return {
    quiz: {}, // slug -> mejor número de aciertos
    read: [], // lecciones cuya teoría el alumno ha marcado como leída
    passed: [], // ejercicios superados
    tried: [], // ejercicios comprobados al menos una vez
    firstTry: [], // ejercicios superados en el primer intento
    challenges: [], // retos superados
    days: [], // días con actividad (AAAA-MM-DD, hora local)
    flags: { firstRun: false, bugHunter: false, lastRunFailed: false },
    badges: [],
  };
}

const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const ids = (value, pattern = ID) =>
  Array.isArray(value) ? [...new Set(value.filter((item) => typeof item === "string" && pattern.test(item)))].slice(-MAX_ITEMS) : [];

/**
 * Valida un documento que llega de fuera (localStorage o la cuenta): solo pasan los tipos esperados
 * e ids con formato de id, para que nada manipulado acabe en el HTML ni en el cálculo de XP.
 */
export function cleanGame(value) {
  const game = emptyGame();
  if (!isObject(value)) return game;
  for (const list of LISTS) game[list] = ids(value[list]);
  game.days = ids(value.days, DAY).sort();
  if (isObject(value.quiz)) {
    for (const [slug, best] of Object.entries(value.quiz)) {
      if (ID.test(slug) && Number.isInteger(best) && best >= 0 && best <= 3) game.quiz[slug] = best;
    }
  }
  if (isObject(value.flags)) for (const flag of FLAGS) game.flags[flag] = value.flags[flag] === true;
  return game;
}

/**
 * Fusiona la copia de la cuenta con la local sin perder nada de ninguna: listas unidas, mejor nota
 * de cada quiz y logros conseguidos en cualquier dispositivo. Modifica y devuelve `local`.
 */
export function mergeGame(local, remote) {
  const other = cleanGame(remote);
  for (const list of LISTS) local[list] = [...new Set([...local[list], ...other[list]])];
  local.days = [...new Set([...local.days, ...other.days])].sort();
  for (const [slug, best] of Object.entries(other.quiz)) local.quiz[slug] = Math.max(local.quiz[slug] ?? 0, best);
  // lastRunFailed describe la última ejecución de este navegador: no se copia de otro
  local.flags.firstRun ||= other.flags.firstRun;
  local.flags.bugHunter ||= other.flags.bugHunter;
  return local;
}
