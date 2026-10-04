/* Modelo del aprendizaje por conceptos (ADR-0031). Funciones puras sobre un documento JSON:
   no tocan el DOM ni localStorage (eso lo hace learn-store.js), así que se prueban con node --test.

   Documento (clave pld:learn y /api/course-state/learn):
   {
     v: 1,
     ex:       { [idEjercicio]: { h: [true, false…] (últimos 5), last: ISO, n: intentos } },
     concepts: { [idConcepto]: { box: 0-5, due: "AAAA-MM-DD" | null, last: ISO | null, read: ISO | null } },
     errors:   { [idError]: { n: veces, last: ISO, streak: aciertos seguidos desde el último fallo } },
     log:      [ { at: ISO, ex: id, ok: bool, err: idError | null } ]   (los últimos LOG_SIZE)
     exams:    [ { date: ISO, kind, correct, total, seconds, concepts: { [id]: [aciertos, total] } } ]
   } */

import { errorsTested } from "./answers.js";

export const INTERVAL_DAYS = [0, 1, 3, 7, 14, 30]; // como el repaso del PCAP y de los cursos
const MAX_BOX = INTERVAL_DAYS.length - 1;
const HISTORY = 5;
export const LOG_SIZE = 300;
const EXAMS = 20;
/** Un error deja de estar «activo» tras FIXED_STREAK aciertos en ejercicios que lo detectan. */
export const FIXED_STREAK = 2;
/** …o si hace más de ERROR_DAYS días que no se repite. */
export const ERROR_DAYS = 21;
const LEVEL_WEIGHT = { 1: 1, 2: 1.5, 3: 2 };

export const emptyLearning = () => ({ v: 1, ex: {}, concepts: {}, errors: {}, log: [], exams: [] });

export const isoDay = (date = new Date()) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

export function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return isoDay(next);
}

/** Días completos entre dos fechas (por día del calendario local). */
export function daysBetween(fromIso, now = new Date()) {
  const from = new Date(fromIso);
  const a = Date.UTC(from.getFullYear(), from.getMonth(), from.getDate());
  const b = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.round((b - a) / 86_400_000);
}

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

const conceptEntry = (state, id) => (state.concepts[id] ??= { box: 0, due: null, last: null, read: null });

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
  }
  conceptEntry(state, exercise.concept).last = at;
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
 * Programa el siguiente repaso del concepto al terminar una sesión (cajas de Leitner):
 * ≥ 80 % de acierto → sube de caja y el repaso se aleja; < 50 % → caja 1 (mañana); entre medias, se mantiene.
 */
export function reviewConcept(state, conceptId, accuracy, now = new Date()) {
  const entry = conceptEntry(state, conceptId);
  if (accuracy >= 0.8) entry.box = Math.min(entry.box + 1, MAX_BOX);
  else if (accuracy < 0.5) entry.box = 1;
  else entry.box = Math.max(entry.box, 1);
  entry.due = addDays(now, INTERVAL_DAYS[entry.box]);
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

/**
 * Dominio de un concepto.
 * - score (0-1): ejercicios cuyo último intento fue correcto, ponderados por nivel, sobre el total
 *   de ejercicios del concepto. No basta con acertar uno: hay que cubrir el concepto.
 * - status: nuevo · leido · aprendiendo (< 50 %) · progreso · dominado (≥ 80 %, con al menos un
 *   ejercicio de aplicación acertado y sin errores activos).
 */
export function conceptStats(index, state, conceptId, now = new Date()) {
  const exercises = index.byConcept.get(conceptId) ?? [];
  const entry = state.concepts[conceptId];
  let total = 0;
  let earned = 0;
  let attempted = 0;
  for (const exercise of exercises) {
    const weight = LEVEL_WEIGHT[exercise.level] ?? 1;
    total += weight;
    if (state.ex[exercise.id]) attempted += 1;
    if (lastOk(state, exercise.id)) earned += weight;
  }
  const score = total ? earned / total : 0;
  const advanced = exercises.filter((e) => e.level >= 2);
  const appliedOk = advanced.length === 0 || advanced.some((e) => lastOk(state, e.id));
  const errors = activeErrors(state, now).filter((e) => index.errors.get(e.id)?.concept === conceptId);
  let status;
  if (attempted === 0) status = entry?.read ? "leido" : "nuevo";
  else if (score >= 0.8 && appliedOk && errors.length === 0) status = "dominado";
  else if (score >= 0.5) status = "progreso";
  else status = "aprendiendo";
  const due = Boolean(entry?.due && entry.due <= isoDay(now));
  return { id: conceptId, score, status, attempted, count: exercises.length, due, nextReview: entry?.due ?? null, errors, last: entry?.last ?? null };
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
 * esperados e ids con formato de id, para que nada manipulado acabe en el HTML (ADR-0022).
 */
export function cleanLearning(value) {
  const state = emptyLearning();
  if (!isObject(value)) return state;
  state.ex = cleanMap(value.ex, (e) =>
    Array.isArray(e.h) && isIso(e.last) && isCount(e.n) ? { h: e.h.filter((x) => typeof x === "boolean").slice(-HISTORY), last: e.last, n: e.n } : null,
  );
  state.concepts = cleanMap(value.concepts, (c) => ({
    box: Number.isInteger(c.box) && c.box >= 0 && c.box <= MAX_BOX ? c.box : 0,
    due: typeof c.due === "string" && DAY.test(c.due) ? c.due : null,
    last: isoOrNull(c.last),
    read: isoOrNull(c.read),
  }));
  state.errors = cleanMap(value.errors, (e) => (isCount(e.n) && isIso(e.last) ? { n: e.n, last: e.last, streak: isCount(e.streak) ? e.streak : 0 } : null));
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
  return state;
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
  for (const [id, entry] of Object.entries(other.ex)) local.ex[id] = !local.ex[id] || entry.n > local.ex[id].n ? entry : local.ex[id];
  for (const [id, entry] of Object.entries(other.concepts)) {
    const mine = local.concepts[id];
    if (!mine) {
      local.concepts[id] = entry;
      continue;
    }
    const newer = later(mine, entry);
    local.concepts[id] = { ...newer, read: [mine.read, entry.read].filter(Boolean).sort().at(-1) ?? null };
  }
  for (const [id, entry] of Object.entries(other.errors)) {
    const mine = local.errors[id];
    local.errors[id] = !mine ? entry : { ...later(mine, entry), n: Math.max(mine.n, entry.n) };
  }
  const log = new Map([...other.log, ...local.log].map((l) => [`${l.at}|${l.ex}`, l]));
  local.log = [...log.values()].sort((a, b) => a.at.localeCompare(b.at)).slice(-LOG_SIZE);
  const exams = new Map([...other.exams, ...local.exams].map((e) => [e.date, e]));
  local.exams = [...exams.values()].sort((a, b) => a.date.localeCompare(b.date)).slice(-EXAMS);
  return local;
}
