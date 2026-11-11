/* Modelo del aprendizaje por conceptos. Funciones puras sobre un documento JSON:
   no tocan el DOM ni localStorage (eso lo hace learn-store.js), así que se prueban con node --test.

   Documento (clave pld:learn y /api/course-state/learn):
   {
     v: 1,
     ex:       { [idEjercicio]: { h: [true, false…] (últimos 5), last: ISO, n: intentos } },
     concepts: { [idConcepto]: { box: 0-5, due: "AAAA-MM-DD" | null, last: ISO | null, read: ISO | null,
                                 placed: ISO | null (superado en la prueba de nivel) } },
     errors:   { [idError]: { n: veces, last: ISO, streak: aciertos seguidos desde el último fallo } },
     log:      [ { at: ISO, ex: id, ok: bool, err: idError | null } ]   (los últimos LOG_SIZE)
     exams:    [ { date: ISO, kind, correct, total, seconds, concepts: { [id]: [aciertos, total] } } ]
   } */

import { errorsTested } from "./answers.js";
import { addDays, daysBetween, INTERVAL_DAYS, isoDay, MAX_BOX, schedule } from "../srs.js";

// Repaso espaciado común a conceptos, PCAP y cursos (srs.js); se reexporta para no romper imports
export { addDays, daysBetween, INTERVAL_DAYS, isoDay };
const HISTORY = 5;
export const LOG_SIZE = 300;
const EXAMS = 20;
/** Un error deja de estar «activo» tras FIXED_STREAK aciertos en ejercicios que lo detectan. */
export const FIXED_STREAK = 2;
/** …o si hace más de ERROR_DAYS días que no se repite. */
export const ERROR_DAYS = 21;
const LEVEL_WEIGHT = { 1: 1, 2: 1.5, 3: 2 };

export const emptyLearning = () => ({ v: 1, ex: {}, concepts: {}, errors: {}, log: [], exams: [] });

/* ---------- Índice del contenido (learning.json) ---------- */

export function buildIndex(data) {
  const concepts = new Map(data.concepts.map((c) => [c.id, c]));
  const exercises = new Map(data.exercises.map((e) => [e.id, e]));
  const byConcept = new Map(data.concepts.map((c) => [c.id, []]));
  for (const exercise of data.exercises) byConcept.get(exercise.concept)?.push(exercise);
  const errors = new Map();
  for (const concept of data.concepts) for (const error of concept.errors) errors.set(error.id, { ...error, concept: concept.id });
  return { data, concepts, exercises, byConcept, errors, path: data.path ?? data.concepts.map((c) => c.id), areas: data.areas };
}

/* ---------- Registrar actividad ---------- */

const conceptEntry = (state, id) => (state.concepts[id] ??= { box: 0, due: null, last: null, read: null, placed: null });

/**
 * Registra un intento. `result` = { ok, error } (de grade() o codeResult()).
 * Con `retry` (el mismo ejercicio repetido tras ver la explicación) no cuenta para el dominio:
 * solo queda en el registro y, si vuelve a fallar, en los errores.
 */
export function recordAttempt(state, exercise, result, { now = new Date(), retry = false } = {}) {
  const at = now.toISOString();
  if (!retry) {
    const entry = (state.ex[exercise.id] ??= { h: [], last: null, n: 0 });
    entry.h.push(Boolean(result.ok));
    if (entry.h.length > HISTORY) entry.h.shift();
    entry.last = at;
    entry.n += 1;
    if (result.ok) entry.okAt = at; // evidencia identificable: cuándo se acertó por última vez
  }
  const concept = conceptEntry(state, exercise.concept);
  concept.last = at;
  // Sin repaso programado (sesión abandonada antes de terminar): se programa para mañana (AUD-003).
  // La caja no cambia: la sube reviewConcept al cerrar una sesión.
  if (!retry && !concept.due) concept.due = addDays(now, INTERVAL_DAYS[1]);
  if (result.error) {
    const error = (state.errors[result.error] ??= { n: 0, last: null, streak: 0 });
    error.n += 1;
    error.last = at;
    error.streak = 0;
  } else if (result.ok && !retry) {
    for (const id of errorsTested(exercise)) {
      if (state.errors[id]) state.errors[id].streak = Math.min(state.errors[id].streak + 1, 99);
    }
  }
  state.log.push({ at, ex: exercise.id, ok: Boolean(result.ok), err: result.error ?? null });
  if (state.log.length > LOG_SIZE) state.log.splice(0, state.log.length - LOG_SIZE);
}

/** El alumno ha estudiado la teoría del concepto. */
export function markRead(state, conceptId, now = new Date()) {
  const entry = conceptEntry(state, conceptId);
  entry.read = now.toISOString();
  entry.last ??= entry.read;
}

/**
 * El alumno ha completado una lección de una unidad (módulo de POO). Solo organiza el estudio:
 * no cuenta para el dominio, que sale de los ejercicios. Es idempotente: se guarda la primera fecha.
 * Documento: sections: { [idLección]: ISO } (opcional; solo existe si hay alguna lección completada).
 */
export function markSection(state, sectionId, now = new Date()) {
  if (!ID.test(sectionId)) return;
  state.sections ??= {};
  state.sections[sectionId] ??= now.toISOString();
}

/** Lecciones completadas de una unidad: [{ id, at }] en el orden de la unidad. */
export function sectionsDone(state, concept) {
  return (concept.sections ?? []).filter((s) => state.sections?.[s.id]).map((s) => ({ id: s.id, at: state.sections[s.id] }));
}

/** El alumno ha demostrado en la prueba de nivel que ya sabe este concepto: la ruta puede saltarlo. */
export function markPlaced(state, conceptId, now = new Date()) {
  conceptEntry(state, conceptId).placed = now.toISOString();
}

/**
 * Programa el siguiente repaso del concepto al terminar una sesión (cajas de Leitner, srs.js):
 * ≥ 80 % de acierto → sube de caja y el repaso se aleja; < 50 % → caja 1 (mañana); entre medias, se mantiene.
 * Solo sube de caja si el repaso había vencido: varias sesiones el mismo día no lo comprimen (AUD-004).
 */
export function reviewConcept(state, conceptId, accuracy, now = new Date()) {
  const entry = conceptEntry(state, conceptId);
  const outcome = accuracy >= 0.8 ? "up" : accuracy < 0.5 ? "down" : "keep";
  const next = schedule(entry, outcome, now);
  entry.box = next.box;
  entry.due = next.due;
}

export function recordExam(state, exam) {
  state.exams.push(exam);
  if (state.exams.length > EXAMS) state.exams.splice(0, state.exams.length - EXAMS);
}

/* ---------- Consultas ---------- */

/** Errores que todavía hay que trabajar: recientes y sin FIXED_STREAK aciertos desde el último fallo. */
export function activeErrors(state, now = new Date()) {
  return Object.entries(state.errors)
    .filter(([, e]) => e.streak < FIXED_STREAK && daysBetween(e.last, now) <= ERROR_DAYS)
    .map(([id, e]) => ({ id, ...e }))
    .sort((a, b) => b.last.localeCompare(a.last));
}

const lastOk = (state, id) => state.ex[id]?.h.at(-1) === true;

/* ---------- Dominio 2.0 (F1.5): evidencias, confianza y retención ---------- */

/** Evidencias distintas que dan confianza plena (como mucho, los ejercicios que tenga el concepto). */
export const CONFIDENCE_EXERCISES = 4;
/** Tipos de ejercicio distintos que dan confianza plena (como mucho, los que tenga el concepto). */
export const CONFIDENCE_KINDS = 2;
/** Por debajo de esta confianza no se muestra un porcentaje: «Pocas evidencias». */
export const MIN_CONFIDENCE = 0.5;
/** Por debajo de esta retención, el concepto se considera olvidado y hay que repasarlo. */
export const FORGOTTEN = 0.7;

/** Semivida (días) de lo aprendido una vez vencido el repaso: cuanto más alta la caja, más dura. */
export const halfLifeDays = (box) => Math.max(14, 3 * INTERVAL_DAYS[Math.min(Math.max(box ?? 0, 1), MAX_BOX)]);

/**
 * Retención estimada (0-1) del concepto. Hasta la fecha de repaso se supone intacta; si el repaso se
 * pasa, baja a la mitad cada `halfLifeDays(caja)` días. Determinista: solo depende del documento y de `now`.
 */
export function retention(entry, now = new Date()) {
  if (!entry?.last) return 1;
  const due = entry.due ?? addDays(new Date(entry.last), INTERVAL_DAYS[1]);
  const overdue = Math.max(0, daysBetween(`${due}T00:00:00`, now));
  return overdue === 0 ? 1 : 0.5 ** (overdue / halfLifeDays(entry.box));
}

/** Fecha del último acierto que cuenta (los datos antiguos no la guardan: se deduce del historial). */
const okAt = (entry) => (entry.okAt && isIso(entry.okAt) ? entry.okAt : entry.h.at(-1) === true ? entry.last : null);

/**
 * Dominio de un concepto (F1.5). Explicable y reproducible:
 * - evidencias: un ejercicio distinto cuenta una vez (repetirlo no suma), con su último resultado;
 * - base (0-1): ejercicios cuyo último intento fue correcto, ponderados por nivel (1 / 1,5 / 2), sobre
 *   todos los ejercicios del concepto: hay que cubrir el concepto, no basta con acertar uno;
 * - retención: baja si el repaso programado se ha pasado;
 * - score = base × retención;
 * - confianza (0-1): cantidad y variedad de evidencias; con menos de MIN_CONFIDENCE no se muestra
 *   porcentaje (`enough: false`, estado «insuficiente»);
 * - status: nuevo · leido · insuficiente · aprendiendo (< 50 %) · progreso · dominado (≥ 80 %, con algún
 *   ejercicio de aplicación acertado y sin errores activos).
 */
export function conceptStats(index, state, conceptId, now = new Date()) {
  const exercises = index.byConcept.get(conceptId) ?? [];
  const entry = state.concepts[conceptId];
  let total = 0;
  let earned = 0;
  const evidence = [];
  for (const exercise of exercises) {
    const weight = LEVEL_WEIGHT[exercise.level] ?? 1;
    total += weight;
    const ex = state.ex[exercise.id];
    if (!ex) continue;
    const ok = lastOk(state, exercise.id);
    if (ok) earned += weight;
    evidence.push({ id: exercise.id, kind: exercise.kind, level: exercise.level, ok, n: ex.n, last: ex.last, okAt: okAt(ex) });
  }
  const attempted = evidence.length;
  const base = total ? earned / total : 0;
  const kept = attempted ? retention(entry, now) : 1;
  const score = base * kept;
  const kindsAvailable = new Set(exercises.map((e) => e.kind)).size;
  const kinds = new Set(evidence.map((e) => e.kind)).size;
  const confidence = attempted
    ? Math.min(1, attempted / Math.min(CONFIDENCE_EXERCISES, exercises.length)) * Math.min(1, kinds / Math.min(CONFIDENCE_KINDS, kindsAvailable))
    : 0;
  const enough = confidence >= MIN_CONFIDENCE;
  const advanced = exercises.filter((e) => e.level >= 2);
  const appliedOk = advanced.length === 0 || advanced.some((e) => lastOk(state, e.id));
  const errors = activeErrors(state, now).filter((e) => index.errors.get(e.id)?.concept === conceptId);
  let status;
  if (attempted === 0) status = entry?.read ? "leido" : "nuevo";
  else if (score >= 0.8 && appliedOk && errors.length === 0 && enough) status = "dominado";
  else if (!enough) status = "insuficiente";
  else if (score >= 0.5) status = "progreso";
  else status = "aprendiendo";
  const due = Boolean(entry?.due && entry.due <= isoDay(now));
  return {
    id: conceptId,
    score,
    base,
    retention: kept,
    forgotten: attempted > 0 && base >= 0.5 && kept < FORGOTTEN,
    confidence,
    enough,
    evidence,
    kinds,
    status,
    attempted,
    count: exercises.length,
    due,
    nextReview: entry?.due ?? null,
    errors,
    last: entry?.last ?? null,
    placed: Boolean(entry?.placed),
  };
}

/** Explicación en una frase de un dominio (para la interfaz y el motivo de las recomendaciones). */
export function explainStats(s) {
  if (!s.attempted) return "Aún no has practicado este concepto.";
  const parts = [`${s.attempted} de ${s.count} ejercicios practicados, de ${s.kinds} ${s.kinds === 1 ? "tipo" : "tipos"}`];
  if (!s.enough) parts.push("pocas evidencias para estimar el dominio");
  if (s.retention < 1) parts.push(`retención estimada del ${Math.round(s.retention * 100)} % porque el repaso se ha pasado`);
  return `${parts.join("; ")}.`;
}

export const allStats = (index, state, now = new Date()) => new Map(index.path.map((id) => [id, conceptStats(index, state, id, now)]));

/** Resumen por área (fundamentos, programación…) para Progreso y DAW. */
export function areaSummary(index, stats, conceptIds = null) {
  return index.areas
    .map((area) => {
      const ids = index.path.filter((id) => index.concepts.get(id).area === area.id && (!conceptIds || conceptIds.includes(id)));
      const list = ids.map((id) => stats.get(id));
      const mastered = list.filter((s) => s.status === "dominado").length;
      const score = list.length ? list.reduce((sum, s) => sum + s.score, 0) / list.length : 0;
      return { ...area, ids, mastered, total: ids.length, score };
    })
    .filter((area) => area.total > 0);
}

/** Actividad reciente para «Última actividad». */
export function lastActivity(index, state) {
  const entry = state.log.at(-1);
  if (!entry) return null;
  const exercise = index.exercises.get(entry.ex);
  return exercise ? { at: entry.at, concept: exercise.concept, ok: entry.ok } : null;
}

/* ---------- Fusión con la cuenta y limpieza ---------- */

const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const DAY = /^\d{4}-\d{2}-\d{2}$/;
const ID = /^[a-z0-9][a-z0-9.-]{0,60}$/;
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const isCount = (value) => Number.isInteger(value) && value >= 0 && value < 1e6;
const isIso = (value) => typeof value === "string" && ISO.test(value);
const isoOrNull = (value) => (isIso(value) ? value : null);

const EX_FIELDS = ["h", "last", "n", "okAt"];
const CONCEPT_FIELDS = ["box", "due", "last", "read", "placed"];
const ERROR_FIELDS = ["n", "last", "streak"];
const KNOWN_TOP = new Set(["v", "ex", "concepts", "errors", "log", "exams", "sections"]);
const EXTRA_KEY = /^[a-zA-Z][a-zA-Z0-9]{0,30}$/;
const isPrimitive = (value) =>
  value === null || typeof value === "boolean" || (typeof value === "number" && Number.isFinite(value)) || (typeof value === "string" && value.length <= 200);

/**
 * Compatibilidad hacia delante (F1.0, EVO-10): los campos que esta versión no conoce se conservan
 * para no borrarlos al fusionar y volver a subir el documento. Dentro de cada entrada solo pasan
 * valores simples (texto corto, número, booleano o null). Esta versión no los pinta nunca.
 */
function extras(raw, known) {
  const out = {};
  for (const [key, value] of Object.entries(raw)) {
    if (!known.includes(key) && EXTRA_KEY.test(key) && isPrimitive(value)) out[key] = value;
  }
  return out;
}

function cleanMap(value, item) {
  const out = {};
  if (!isObject(value)) return out;
  for (const [id, raw] of Object.entries(value)) {
    if (!ID.test(id) || !isObject(raw)) continue;
    const clean = item(raw);
    if (clean) out[id] = clean;
  }
  return out;
}

/**
 * Valida un documento que llega de fuera (localStorage o la cuenta): solo pasan los tipos
 * esperados e ids con formato de id, para que nada manipulado acabe en el HTML.
 */
export function cleanLearning(value) {
  const state = emptyLearning();
  if (!isObject(value)) return state;
  state.ex = cleanMap(value.ex, (e) =>
    Array.isArray(e.h) && isIso(e.last) && isCount(e.n)
      ? {
          ...extras(e, EX_FIELDS),
          h: e.h.filter((x) => typeof x === "boolean").slice(-HISTORY),
          last: e.last,
          n: e.n,
          ...(isIso(e.okAt) ? { okAt: e.okAt } : {}),
        }
      : null,
  );
  state.concepts = cleanMap(value.concepts, (c) => ({
    ...extras(c, CONCEPT_FIELDS),
    box: Number.isInteger(c.box) && c.box >= 0 && c.box <= MAX_BOX ? c.box : 0,
    due: typeof c.due === "string" && DAY.test(c.due) ? c.due : null,
    last: isoOrNull(c.last),
    read: isoOrNull(c.read),
    placed: isoOrNull(c.placed),
  }));
  state.errors = cleanMap(value.errors, (e) =>
    isCount(e.n) && isIso(e.last) ? { ...extras(e, ERROR_FIELDS), n: e.n, last: e.last, streak: isCount(e.streak) ? e.streak : 0 } : null,
  );
  state.log = (Array.isArray(value.log) ? value.log : [])
    .filter((l) => isObject(l) && isIso(l.at) && typeof l.ex === "string" && ID.test(l.ex) && typeof l.ok === "boolean")
    .map((l) => ({ at: l.at, ex: l.ex, ok: l.ok, err: typeof l.err === "string" && ID.test(l.err) ? l.err : null }))
    .slice(-LOG_SIZE);
  state.exams = (Array.isArray(value.exams) ? value.exams : [])
    .filter((e) => isObject(e) && isIso(e.date) && isCount(e.correct) && isCount(e.total) && isCount(e.seconds))
    .map((e) => ({
      date: e.date,
      kind: typeof e.kind === "string" && ID.test(e.kind) ? e.kind : "exam",
      correct: e.correct,
      total: e.total,
      seconds: e.seconds,
      concepts: examConcepts(e.concepts),
    }))
    .slice(-EXAMS);
  const sections = cleanSections(value.sections);
  if (Object.keys(sections).length) state.sections = sections;
  // Bloques nuevos de versiones futuras: se guardan tal cual (son JSON de la propia cuenta)
  for (const [key, raw] of Object.entries(value)) {
    if (!KNOWN_TOP.has(key) && EXTRA_KEY.test(key)) state[key] = raw;
  }
  return state;
}

/** Lecciones completadas: ids con formato de id y fecha ISO; lo demás se descarta. */
function cleanSections(raw) {
  const sections = {};
  if (!isObject(raw)) return sections;
  for (const [id, at] of Object.entries(raw)) if (ID.test(id) && isIso(at)) sections[id] = at;
  return sections;
}

/** Aciertos por concepto de un simulacro: { [id]: [aciertos, total] }. */
function examConcepts(raw) {
  const concepts = {};
  if (!isObject(raw)) return concepts;
  for (const [id, pair] of Object.entries(raw)) {
    if (ID.test(id) && Array.isArray(pair) && pair.length === 2 && pair.every(isCount)) concepts[id] = pair;
  }
  return concepts;
}

const later = (a, b, field = "last") => ((a?.[field] ?? "") >= (b?.[field] ?? "") ? a : b);

/** Fusiona la copia de la cuenta con la local sin perder nada (web y app comparten el documento). */
export function mergeLearning(local, remote) {
  const other = cleanLearning(remote);
  // El historial guarda solo los últimos intentos: gana el del intento más reciente (SYNC-02), y el
  // número total de intentos no baja. Sin fecha en alguna copia, gana la que tiene más intentos.
  for (const [id, entry] of Object.entries(other.ex)) {
    const mine = local.ex[id];
    if (!mine) {
      local.ex[id] = entry;
      continue;
    }
    const newer = mine.last && entry.last ? later(mine, entry) : entry.n > mine.n ? entry : mine;
    // El último acierto es una evidencia: se conserva el más reciente de las dos copias (F1.6, EVO-15)
    const okAt = [mine.okAt, entry.okAt].filter(Boolean).sort().at(-1);
    local.ex[id] = { ...newer, n: Math.max(mine.n, entry.n), ...(okAt ? { okAt } : {}) };
  }
  for (const [id, entry] of Object.entries(other.concepts)) {
    const mine = local.concepts[id];
    if (!mine) {
      local.concepts[id] = entry;
      continue;
    }
    const newer = later(mine, entry);
    const latest = (field) => [mine[field], entry[field]].filter(Boolean).sort().at(-1) ?? null;
    local.concepts[id] = { ...newer, read: latest("read"), placed: latest("placed") };
  }
  for (const [id, entry] of Object.entries(other.errors)) {
    const mine = local.errors[id];
    local.errors[id] = !mine ? entry : { ...later(mine, entry), n: Math.max(mine.n, entry.n) };
  }
  const log = new Map([...other.log, ...local.log].map((l) => [`${l.at}|${l.ex}`, l]));
  local.log = [...log.values()].sort((a, b) => a.at.localeCompare(b.at)).slice(-LOG_SIZE);
  const exams = new Map([...other.exams, ...local.exams].map((e) => [e.date, e]));
  local.exams = [...exams.values()].sort((a, b) => a.date.localeCompare(b.date)).slice(-EXAMS);
  // Lecciones completadas: unión de las dos copias, con la primera fecha (una copia vacía no borra nada)
  for (const [id, at] of Object.entries(other.sections ?? {})) {
    local.sections ??= {};
    if (!local.sections[id] || at < local.sections[id]) local.sections[id] = at;
  }
  // Bloques que esta versión no conoce: se conserva el de la cuenta si aquí no existe
  for (const [key, raw] of Object.entries(other)) if (!(key in local)) local[key] = raw;
  return local;
}
