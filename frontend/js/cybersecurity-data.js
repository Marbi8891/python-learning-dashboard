/* Progreso del curso de ciberseguridad: forma del documento, limpieza, fusión y cambios.
   No toca el DOM ni la red (eso lo hace cybersecurity-store.js), así que se prueba con node --test.

   Documento (pld:cybersecurity:v1 en el navegador y /api/course-state/cybersecurity en la cuenta):
     { v: 2, weeks: { "semana-01": { done, at } }, quiz: { "semana-01": { score, at } } }
   Cada semana y cada cuestionario llevan la fecha de su último cambio: al fusionar dos copias gana el
   cambio más reciente, así que desmarcar una semana en un dispositivo no la vuelve a marcar el otro.

   La versión anterior guardaba { completed: [...], quizScores: {...} } sin fechas, solo en el
   navegador. Se sigue leyendo: sus datos entran con la fecha 0 (LEGACY_AT), de modo que cualquier
   cambio con fecha los sustituye y ninguno se pierde por la migración. */

export const WEEK_ID = /^semana-\d{2}$/;
export const MAX_SCORE = 3;
/** Fecha de lo que venía del formato anterior, que no guardaba fechas. */
export const LEGACY_AT = new Date(0).toISOString();

const KNOWN = new Set(["v", "weeks", "quiz", "completed", "quizScores"]);

const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const isScore = (value) => Number.isInteger(value) && value >= 0 && value <= MAX_SCORE;

/** Fecha en ISO normalizado (comparable como texto), o null si no es una fecha válida. */
function isoOrNull(value) {
  if (typeof value !== "string" || value.length > 40) return null;
  const time = Date.parse(value);
  return Number.isNaN(time) ? null : new Date(time).toISOString();
}

/** Documento válido a partir de cualquier cosa (localStorage, la cuenta o el formato anterior).
    Conserva los campos que no conoce (DEC-007): una versión antigua de la web no borra los de una nueva. */
export function cleanCyber(raw) {
  const source = isObject(raw) ? raw : {};
  const doc = { v: 2, weeks: {}, quiz: {} };
  for (const [key, value] of Object.entries(source)) if (!KNOWN.has(key)) doc[key] = value;

  for (const [id, entry] of Object.entries(isObject(source.weeks) ? source.weeks : {})) {
    const at = isoOrNull(entry?.at);
    if (WEEK_ID.test(id) && typeof entry.done === "boolean" && at) doc.weeks[id] = { done: entry.done, at };
  }
  for (const [id, entry] of Object.entries(isObject(source.quiz) ? source.quiz : {})) {
    const at = isoOrNull(entry?.at);
    if (WEEK_ID.test(id) && isScore(entry.score) && at) doc.quiz[id] = { score: entry.score, at };
  }

  // Formato anterior: solo rellena lo que el formato nuevo no tenga
  for (const id of Array.isArray(source.completed) ? source.completed : []) {
    if (typeof id === "string" && WEEK_ID.test(id) && !doc.weeks[id]) doc.weeks[id] = { done: true, at: LEGACY_AT };
  }
  for (const [id, score] of Object.entries(isObject(source.quizScores) ? source.quizScores : {})) {
    if (WEEK_ID.test(id) && isScore(score) && !doc.quiz[id]) doc.quiz[id] = { score, at: LEGACY_AT };
  }
  return doc;
}

// Gana el cambio más reciente. Con la misma fecha (p. ej. dos copias del formato anterior), lo que
// conserva más progreso: así la fusión no depende del orden y nunca pierde una semana hecha.
const newerWeek = (a, b) => a.at > b.at || (a.at === b.at && a.done && !b.done);
const newerQuiz = (a, b) => a.at > b.at || (a.at === b.at && a.score > b.score);

/** Fusiona en `local` la copia `remote`. Devuelve si `local` ha cambiado (para repintar solo entonces). */
export function mergeCyber(local, remote) {
  const other = cleanCyber(remote);
  let changed = false;
  for (const [id, entry] of Object.entries(other.weeks)) {
    if (!local.weeks[id] || newerWeek(entry, local.weeks[id])) {
      local.weeks[id] = entry;
      changed = true;
    }
  }
  for (const [id, entry] of Object.entries(other.quiz)) {
    if (!local.quiz[id] || newerQuiz(entry, local.quiz[id])) {
      local.quiz[id] = entry;
      changed = true;
    }
  }
  for (const [key, value] of Object.entries(other)) {
    if (!(key in local)) {
      local[key] = value;
      changed = true;
    }
  }
  return changed;
}

/* ---------- Lectura ---------- */

export const isWeekDone = (doc, id) => doc.weeks[id]?.done === true;
/** Último resultado del cuestionario de la semana, o undefined si no se ha hecho. */
export const quizScore = (doc, id) => doc.quiz[id]?.score;
export const completedWeeks = (doc) => Object.values(doc.weeks).filter((entry) => entry.done).length;

/* ---------- Cambios (los llama la interfaz; después, saveCyber) ---------- */

export function setQuizScore(doc, id, score, now = new Date()) {
  if (WEEK_ID.test(id) && isScore(score)) doc.quiz[id] = { score, at: now.toISOString() };
}

/** Marca la semana como completada o pendiente. Solo se puede completar con el cuestionario superado. */
export function toggleWeek(doc, id, now = new Date()) {
  if (!WEEK_ID.test(id)) return;
  const done = !isWeekDone(doc, id);
  if (done && (quizScore(doc, id) ?? 0) < 2) return;
  doc.weeks[id] = { done, at: now.toISOString() };
}
