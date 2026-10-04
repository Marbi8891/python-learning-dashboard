/* Sesiones de estudio (ADR-0031): la lógica del ciclo
   intento → acierto/error → explicación → nuevo intento → repaso, sin DOM.

   Tipos de sesión:
   - learn:    concepto nuevo (la vista enseña antes la teoría y el ejemplo);
   - practice: práctica de uno o varios conceptos;
   - review:   repaso de lo que toca hoy;
   - errors:   ejercicios que trabajan errores concretos;
   - exam:     simulacro: sin corrección hasta el final, cronometrado y sin nuevos intentos. */

import { recordAttempt, recordExam, reviewConcept } from "./mastery.js";
import { similarExercise } from "./recommend.js";

export const MAX_RETRIES = 3; // nuevos intentos añadidos al final de una sesión, como mucho

/**
 * @param {{kind: string, title: string, exercises: string[], timeLimit?: number, now?: Date, meta?: object}} options
 */
export function createSession({ kind, title, exercises, timeLimit = null, now = new Date(), meta = {} }) {
  return {
    kind,
    title,
    meta,
    feedback: kind !== "exam",
    queue: exercises.map((id) => ({ id, retry: false, retryOf: null })),
    index: 0,
    phase: exercises.length ? "answer" : "done",
    results: [], // { id, concept, ok, error, retry }
    retries: 0,
    startedAt: now.toISOString(),
    timeLimit, // segundos, solo en los simulacros
  };
}

export const currentItem = (session) => session.queue[session.index] ?? null;

export function secondsLeft(session, now = new Date()) {
  if (!session.timeLimit) return null;
  const spent = Math.floor((now - new Date(session.startedAt)) / 1000);
  return Math.max(0, session.timeLimit - spent);
}

export const isExpired = (session, now = new Date()) => secondsLeft(session, now) === 0;

/**
 * Registra la respuesta al ejercicio actual (en la sesión y en el progreso del alumno).
 * Si falla y la sesión da corrección, programa un nuevo intento al final:
 * un ejercicio parecido que trabaje el mismo error o, si no hay, el mismo (que entonces no cuenta para el dominio).
 */
export function submit(session, index, state, result, now = new Date()) {
  const item = currentItem(session);
  const exercise = index.exercises.get(item.id);
  recordAttempt(state, exercise, result, { now, retry: item.retry });
  session.results.push({ id: item.id, concept: exercise.concept, ok: Boolean(result.ok), error: result.error ?? null, retry: item.retry });
  if (!result.ok && session.feedback && session.retries < MAX_RETRIES && !item.retryOf) {
    const queued = session.queue.map((q) => q.id);
    const similar = similarExercise(index, exercise, result.error, queued);
    session.queue.push(similar ? { id: similar.id, retry: false, retryOf: item.id } : { id: item.id, retry: true, retryOf: item.id });
    session.retries += 1;
  }
  session.phase = session.feedback ? "feedback" : "answer";
  if (!session.feedback) advance(session);
  return session;
}

/** Pasa al siguiente ejercicio (tras leer la explicación). */
export function advance(session) {
  session.index += 1;
  session.phase = session.index < session.queue.length ? "answer" : "done";
  return session;
}

/** Termina antes de tiempo (simulacro agotado o el alumno lo deja). */
export function stop(session) {
  session.phase = "done";
  return session;
}

/**
 * Resumen. Cada resultado corresponde a la entrada de la cola en la misma posición
 * (se responde en orden). El acierto cuenta solo los primeros intentos: los nuevos intentos
 * muestran si se ha entendido la explicación, pero no inflan la nota.
 */
export function summarize(session, index) {
  const isRetry = (_, i) => Boolean(session.queue[i]?.retryOf);
  const first = session.results.filter((r, i) => !isRetry(r, i));
  const retries = session.results.filter(isRetry);
  const byConcept = {};
  for (const r of first) {
    const pair = (byConcept[r.concept] ??= [0, 0]);
    pair[0] += r.ok ? 1 : 0;
    pair[1] += 1;
  }
  const errorCount = new Map();
  for (const r of session.results) if (r.error) errorCount.set(r.error, (errorCount.get(r.error) ?? 0) + 1);
  const errors = [...errorCount]
    .filter(([id]) => index.errors.has(id))
    .map(([id, count]) => ({ ...index.errors.get(id), id, count }));
  return {
    correct: first.filter((r) => r.ok).length,
    total: first.length,
    byConcept,
    errors,
    retried: retries.length,
    fixed: retries.filter((r) => r.ok).length,
    unanswered: Math.max(0, session.queue.length - session.results.length),
  };
}

/**
 * Cierra la sesión: programa el repaso de cada concepto trabajado según su acierto
 * y, si es un simulacro, lo guarda con su resultado por concepto.
 */
export function finish(session, index, state, now = new Date()) {
  const summary = summarize(session, index);
  for (const [concept, [ok, total]] of Object.entries(summary.byConcept)) reviewConcept(state, concept, ok / total, now);
  if (session.kind === "exam") {
    recordExam(state, {
      date: now.toISOString(),
      kind: session.meta.examKind ?? "exam",
      correct: summary.correct,
      // Las preguntas sin responder cuentan como falladas
      total: session.queue.length,
      seconds: Math.round((now - new Date(session.startedAt)) / 1000),
      concepts: summary.byConcept,
    });
  }
  return summary;
}
