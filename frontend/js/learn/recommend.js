/* ¿Qué estudio ahora? Recomendación y selección de ejercicios (ADR-0031). Funciones puras.

   Prioridad del plan de «Hoy» (la pidió el autor):
     1. conceptos con repaso pendiente;
     2. conceptos con errores recientes sin corregir;
     3. conceptos importantes para DAW que aún no están dominados;
     4. contenido nuevo, solo si sus prerrequisitos están firmes;
     5. repaso general de lo dominado hace más tiempo. */

import { errorsTested } from "./answers.js";
import { activeErrors, allStats, daysBetween } from "./mastery.js";

export const PLAN_SIZE = 4;
/** Un prerrequisito está «firme» con este dominio. Por debajo, se pide reforzarlo antes de avanzar. */
export const READY_SCORE = 0.6;
/** El repaso general solo propone lo que no se ha practicado en estos días. */
export const GENERAL_REVIEW_DAYS = 3;

const isStarted = (s) => s.attempted > 0;

/**
 * Prerrequisitos que faltan por reforzar antes de aprender `conceptId`.
 * Devuelve [] si se puede avanzar.
 */
export function missingPrerequisites(index, stats, conceptId) {
  const concept = index.concepts.get(conceptId);
  return concept.requires.filter((id) => stats.get(id).score < READY_SCORE);
}

/**
 * Siguiente concepto nuevo de la ruta. Si el primero pendiente tiene prerrequisitos flojos,
 * se devuelve igualmente con `blockedBy` para poder decir «Necesitas reforzar X antes de pasar a Y».
 */
export function nextNewConcept(index, stats) {
  const id = index.path.find((cid) => !isStarted(stats.get(cid)));
  if (!id) return null;
  return { id, blockedBy: missingPrerequisites(index, stats, id) };
}

function errorsByConcept(index, state, now) {
  const grouped = new Map();
  for (const error of activeErrors(state, now)) {
    const concept = index.errors.get(error.id)?.concept;
    if (!concept) continue;
    if (!grouped.has(concept)) grouped.set(concept, []);
    grouped.get(concept).push(error);
  }
  return grouped; // en orden del error más reciente
}

/**
 * Plan de estudio para hoy: hasta PLAN_SIZE acciones, cada una con su motivo.
 * item = { type: "review" | "errors" | "practice" | "learn" | "reinforce", concept, reason, errors?, before? }
 */
export function todayPlan(index, state, now = new Date(), stats = allStats(index, state, now)) {
  const plan = [];
  const used = new Set();
  const push = (item) => {
    if (plan.length >= PLAN_SIZE || used.has(item.concept)) return;
    used.add(item.concept);
    plan.push(item);
  };
  const title = (id) => index.concepts.get(id).title;

  // 1. Repasos pendientes, del más atrasado al más reciente (como mucho dos, para dejar sitio a lo demás)
  const due = index.path
    .map((id) => stats.get(id))
    .filter((s) => s.due)
    .sort((a, b) => a.nextReview.localeCompare(b.nextReview))
    .slice(0, 2);
  for (const s of due) {
    const days = s.last ? daysBetween(s.last, now) : 0;
    push({ type: "review", concept: s.id, reason: days > 0 ? `Toca repasarlo: lo practicaste hace ${days} ${days === 1 ? "día" : "días"}.` : "Toca repasarlo hoy." });
  }

  // 2. Errores recientes sin corregir
  for (const [concept, errors] of errorsByConcept(index, state, now)) {
    const label = index.errors.get(errors[0].id).label;
    push({ type: "errors", concept, errors: errors.map((e) => e.id), reason: `Error reciente: ${label}.` });
  }

  // Siguiente concepto nuevo y lo que lo bloquea (se usa en los pasos 3 y 4)
  const next = nextNewConcept(index, stats);
  const blockers = new Set(next?.blockedBy ?? []);
  const reinforce = (id) => ({
    type: "reinforce",
    concept: id,
    before: next.id,
    reason: `Necesitas reforzar ${title(id)} antes de pasar a ${title(next.id)}.`,
  });

  // 3. Importantes para DAW, empezados y aún no dominados (los más flojos primero).
  //    Si además bloquean el siguiente concepto, se dice explícitamente.
  index.path
    .map((id) => stats.get(id))
    .filter((s) => isStarted(s) && s.status !== "dominado" && index.concepts.get(s.id).daw === 3)
    .sort((a, b) => a.score - b.score)
    .forEach((s) =>
      push(blockers.has(s.id) ? reinforce(s.id) : { type: "practice", concept: s.id, reason: `Importante para DAW y aún no lo dominas (${Math.round(s.score * 100)} %).` }),
    );

  // 4. Contenido nuevo si sus prerrequisitos están firmes; si no, qué reforzar antes
  if (next && blockers.size === 0) push({ type: "learn", concept: next.id, reason: "Siguiente concepto de la ruta." });
  for (const id of blockers) push(reinforce(id));

  // 5. Repaso general: lo dominado que hace más tiempo que no se practica
  if (plan.length < 3) {
    index.path
      .map((id) => stats.get(id))
      .filter((s) => s.status === "dominado" && s.last && daysBetween(s.last, now) >= GENERAL_REVIEW_DAYS)
      .sort((a, b) => a.last.localeCompare(b.last))
      .forEach((s) => push({ type: "review", concept: s.id, reason: "Repaso general para que no se olvide." }));
  }
  return plan;
}

/** Nivel de dificultad adecuado según el dominio actual del concepto. */
export const targetLevel = (score) => (score < 0.4 ? 1 : score < 0.8 ? 2 : 3);

/**
 * Elige `count` ejercicios de los conceptos dados, priorizando:
 *   los que detectan errores activos del alumno → los fallados → los nuevos → el resto,
 * evitando los que ya domina (últimos intentos correctos) y los de un nivel muy por encima del suyo.
 * `kinds` limita los tipos de ejercicio, `only` los ejercicios concretos y `random` permite tests deterministas.
 */
export function selectExercises(index, state, conceptIds, count, { now = new Date(), random = Math.random, kinds = null, exclude = [], only = null } = {}) {
  const stats = allStats(index, state, now);
  const active = new Set(activeErrors(state, now).map((e) => e.id));
  const skip = new Set(exclude);
  const candidates = conceptIds
    .flatMap((id) => index.byConcept.get(id) ?? [])
    .filter((e) => !skip.has(e.id) && (!kinds || kinds.includes(e.kind)) && (!only || only.includes(e.id)));
  const scored = candidates.map((exercise) => {
    const history = state.ex[exercise.id]?.h ?? [];
    const level = targetLevel(stats.get(exercise.concept).score);
    let score = random(); // desempate y variedad
    if (errorsTested(exercise).some((id) => active.has(id))) score += 6;
    if (history.length === 0) score += 3;
    else if (history.at(-1) === false) score += 4;
    else if (history.length >= 2 && history.at(-2) === true) score -= 6; // dominado: no repetir sin motivo
    else if (daysBetween(state.ex[exercise.id].last, now) === 0) score -= 3; // acertado hoy mismo
    if (exercise.level > level + 1) score -= 4;
    else if (exercise.level > level) score -= 1;
    return { exercise, score };
  });
  scored.sort((a, b) => b.score - a.score);
  // Progresión dentro de la sesión: de lo más sencillo a lo más completo
  return scored
    .slice(0, count)
    .map((s) => s.exercise)
    .sort((a, b) => a.level - b.level);
}

/** Ejercicio parecido (mismo concepto y, si es posible, que detecte el mismo error) para el «nuevo intento». */
export function similarExercise(index, exercise, errorId, exclude = []) {
  const skip = new Set([exercise.id, ...exclude]);
  const pool = (index.byConcept.get(exercise.concept) ?? []).filter((e) => !skip.has(e.id) && e.kind !== "code");
  return (errorId && pool.find((e) => errorsTested(e).includes(errorId))) || pool.find((e) => e.level <= exercise.level) || null;
}

/** Ejercicios que trabajan un error concreto (para «practicar este error»). */
export const exercisesForError = (index, errorId) => index.data.exercises.filter((e) => errorsTested(e).includes(errorId));
