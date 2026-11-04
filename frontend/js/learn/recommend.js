/* ¿Qué estudio ahora? Recomendación y selección de ejercicios. Funciones puras.

   Plan de «Hoy» (F1.7):
     1. repasos vencidos (siempre primero);
     2. errores recientes, conceptos que se olvidan y conceptos empezados sin dominar, ordenados por
        la prioridad P = 0,25 R + 0,25 E + 0,20 D + 0,15 W + 0,15 T (ver priority());
     3. contenido nuevo, solo si sus prerrequisitos están firmes;
     4. repaso general de lo dominado hace más tiempo.
   Cada acción dice por qué se recomienda. */

import { errorsTested } from "./answers.js";
import { activeErrors, allStats, daysBetween, INTERVAL_DAYS } from "./mastery.js";

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
  return concept.requires.filter((id) => !isReady(stats.get(id)));
}

/** Firme: dominio suficiente o superado en la prueba de nivel. */
export const isReady = (s) => s.score >= READY_SCORE || s.placed;

/**
 * Siguiente concepto nuevo de la ruta. Si el primero pendiente tiene prerrequisitos flojos,
 * se devuelve igualmente con `blockedBy` para poder decir «Necesitas reforzar X antes de pasar a Y».
 */
export function nextNewConcept(index, stats) {
  const id = index.path.find((cid) => !isStarted(stats.get(cid)) && !stats.get(cid).placed);
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

/* ---------- Prioridad explicable (F1.7) ---------- */

/** Pesos de la fórmula P = 0,25 R + 0,25 E + 0,20 D + 0,15 W + 0,15 T. Hipótesis inicial: se validan
    con pruebas de propiedades (tests/unit/recommend.test.mjs), no se presentan como óptimos. */
export const WEIGHTS = Object.freeze({ R: 0.25, E: 0.25, D: 0.2, W: 0.15, T: 0.15 });
/** A partir de estos días, un examen ya no sube la prioridad. */
export const EXAM_HORIZON_DAYS = 60;
/** Errores activos de un concepto que cuentan como «muchos» (E = 1). */
const ERRORS_FULL = 2;

/** Examen o entrega más cercano del módulo del concepto (o null). `exams` viene de upcomingExams(). */
const examFor = (index, conceptId, exams) => exams.find((e) => !e.module || e.module === index.concepts.get(conceptId).module) ?? null;

/**
 * Factores normalizados (0-1) de la prioridad de un concepto y su explicación.
 * R: necesidad de repaso (vencido, o se está olvidando); E: errores activos; D: déficit de dominio;
 * W: importancia curricular (1-3 → 0-1); T: proximidad del examen o entrega de su módulo.
 */
export function priority(index, state, s, now = new Date(), { exams = [], errors = [] } = {}) {
  const concept = index.concepts.get(s.id);
  const box = state.concepts[s.id]?.box ?? 0;
  const overdue = s.due && s.nextReview ? Math.max(0, daysBetween(`${s.nextReview}T00:00:00`, now)) : 0;
  const R = s.due ? Math.min(1, (overdue + 1) / Math.max(1, INTERVAL_DAYS[Math.max(box, 1)])) : s.forgotten ? 1 - s.retention : 0;
  const E = Math.min(1, errors.length / ERRORS_FULL);
  const D = s.attempted ? 1 - s.score : 1;
  const W = (concept.importance ?? concept.daw ?? 1) / 3;
  const exam = examFor(index, s.id, exams);
  const T = exam ? Math.max(0, 1 - exam.days / EXAM_HORIZON_DAYS) : 0;
  const factors = { R, E, D, W, T };
  const value = Object.entries(WEIGHTS).reduce((sum, [key, weight]) => sum + weight * factors[key], 0);
  const why = [];
  if (s.due) why.push(overdue > 0 ? `repaso vencido hace ${overdue} ${overdue === 1 ? "día" : "días"}` : "repaso programado para hoy");
  else if (s.forgotten) why.push(`retención estimada del ${Math.round(s.retention * 100)} %`);
  if (errors.length) why.push(`${errors.length} ${errors.length === 1 ? "error activo" : "errores activos"}`);
  if (s.attempted) why.push(s.enough ? `dominio del ${Math.round(s.score * 100)} %` : "pocas evidencias");
  why.push(concept.daw === 3 ? "imprescindible para DAW" : "importante para DAW");
  if (exam) why.push(`${exam.kind === "entrega" ? "entrega" : "examen"} «${exam.title}» en ${exam.days} ${exam.days === 1 ? "día" : "días"}`);
  return { value: Math.round(value * 1000) / 1000, factors, why };
}

/**
 * Plan de estudio para hoy: hasta PLAN_SIZE acciones, cada una con su motivo, su prioridad y por qué.
 * item = { type: "review" | "errors" | "practice" | "learn" | "reinforce", concept, reason, priority, why, errors?, before? }
 *
 * Reglas duras (no las cambia la fórmula):
 *   1. los repasos vencidos van primero (como mucho dos, para dejar sitio a lo demás);
 *   2. el contenido nuevo solo si sus prerrequisitos están firmes; si no, se propone reforzarlos;
 *   3. lo que el alumno ya ha hecho, pospuesto o rechazado hoy no se vuelve a proponer (`skip`).
 * El resto se ordena por la prioridad P. Lo pospuesto ayer lo dice en el motivo.
 * `options.exams` = upcomingExams() del planificador.
 */
export function todayPlan(index, state, now = new Date(), stats = allStats(index, state, now), { exams = [], skip = new Set(), postponed = new Set() } = {}) {
  const plan = [];
  const used = new Set(skip);
  const title = (id) => index.concepts.get(id).title;
  const errorsOf = errorsByConcept(index, state, now);
  const score = (id) => priority(index, state, stats.get(id), now, { exams, errors: errorsOf.get(id) ?? [] });
  const push = (item) => {
    if (plan.length >= PLAN_SIZE || used.has(item.concept)) return;
    used.add(item.concept);
    const p = score(item.concept);
    const reason = postponed.has(item.concept) ? `${item.reason} Lo pospusiste ayer.` : item.reason;
    plan.push({ ...item, reason, priority: p.value, why: p.why });
  };
  const byPriority = (items) => items.map((item) => ({ item, p: score(item.concept).value })).sort((a, b) => b.p - a.p).map((x) => x.item);

  // 1. Repasos vencidos, del más prioritario (en empate, del más atrasado)
  const due = index.path
    .map((id) => stats.get(id))
    .filter((s) => s.due && !used.has(s.id))
    .sort((a, b) => score(b.id).value - score(a.id).value || a.nextReview.localeCompare(b.nextReview))
    .slice(0, 2);
  for (const s of due) {
    const days = s.last ? daysBetween(s.last, now) : 0;
    push({ type: "review", concept: s.id, reason: days > 0 ? `Toca repasarlo: lo practicaste hace ${days} ${days === 1 ? "día" : "días"}.` : "Toca repasarlo hoy." });
  }

  // Siguiente concepto nuevo y lo que lo bloquea
  const next = nextNewConcept(index, stats);
  const blockers = new Set(next?.blockedBy ?? []);
  const reinforce = (id) => ({
    type: "reinforce",
    concept: id,
    before: next.id,
    reason: `Necesitas reforzar ${title(id)} antes de pasar a ${title(next.id)}.`,
  });

  // 2. Candidatos ordenados por prioridad: errores recientes, conceptos que se olvidan, conceptos
  //    empezados y aún no dominados, y lo que bloquea el siguiente concepto
  const candidates = [];
  for (const [concept, errors] of errorsOf) {
    candidates.push({ type: "errors", concept, errors: errors.map((e) => e.id), reason: `Error reciente: ${index.errors.get(errors[0].id).label}.` });
  }
  for (const s of index.path.map((id) => stats.get(id))) {
    if (s.forgotten && !s.due) candidates.push({ type: "review", concept: s.id, reason: "Se está olvidando: hace tiempo que pasó su repaso." });
    else if (isStarted(s) && !s.placed && s.status !== "dominado") {
      candidates.push(
        blockers.has(s.id)
          ? reinforce(s.id)
          : {
              type: "practice",
              concept: s.id,
              reason: s.enough ? `${index.concepts.get(s.id).daw === 3 ? "Importante para DAW" : "Para DAW"} y aún no lo dominas (${Math.round(s.score * 100)} %).` : "Aún hay pocas evidencias de que lo sepas.",
            },
      );
    }
  }
  for (const id of blockers) candidates.push(reinforce(id));
  // Errores y refuerzo de un mismo concepto: se queda la entrada de más valor (la primera tras ordenar)
  byPriority(candidates).forEach(push);

  // 3. Contenido nuevo si sus prerrequisitos están firmes
  if (next && blockers.size === 0) push({ type: "learn", concept: next.id, reason: "Siguiente concepto de la ruta." });

  // 4. Repaso general: consolidar lo superado en la prueba de nivel y lo dominado hace más tiempo
  if (plan.length < 3) {
    index.path
      .map((id) => stats.get(id))
      .filter((s) => s.placed && s.status !== "dominado")
      .forEach((s) => push({ type: "practice", concept: s.id, reason: "Lo superaste en la prueba de nivel: practícalo para consolidarlo." }));
  }
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

/** Duración orientativa de cada actividad del plan diario, en minutos. */
export const ACTION_MINUTES = Object.freeze({
  review: 10,
  errors: 15,
  practice: 15,
  learn: 15,
  reinforce: 15,
});

/**
 * Ajusta el plan al tiempo disponible sin cambiar la prioridad pedagógica.
 * Las tareas que no caben se devuelven como diferidas, no se eliminan del plan original.
 * El presupuesto se limita a 15–180 minutos para evitar valores accidentales.
 */
export function fitPlanToBudget(plan, availableMinutes = 45) {
  const budget = Math.min(180, Math.max(15, Math.round(Number(availableMinutes) || 45)));
  let remaining = budget;
  const items = [];
  const deferred = [];
  let deferRemaining = false;

  for (const item of plan) {
    const minutes = ACTION_MINUTES[item.type] ?? 15;
    if (!deferRemaining && minutes <= remaining) {
      items.push({ ...item, minutes });
      remaining -= minutes;
    } else {
      // El plan está ordenado por prioridad: no saltar una tarea para meter otra posterior.
      deferRemaining = true;
      deferred.push({ ...item, minutes });
    }
  }

  return {
    items,
    deferred,
    availableMinutes: budget,
    plannedMinutes: budget - remaining,
    remainingMinutes: remaining,
    deferredCount: deferred.length,
  };
}

