/* Resumen de la actividad real del alumno para la portada («Continúa donde lo dejaste»).

   Solo usa lo que hay guardado (núcleo por conceptos y lecciones del curso PCAP completadas):
   si no hay actividad devuelve null y la portada no muestra el bloque. Nada de datos de ejemplo.
   No depende del DOM, para poder probarlo con node --test. */

import { activeErrors, allStats, lastActivity } from "./mastery.js";
import { todayPlan } from "./recommend.js";

export const ACTION = { review: "Repasar", errors: "Corregir errores", practice: "Practicar", learn: "Aprender", reinforce: "Reforzar" };

/** Hay actividad si se ha hecho algún ejercicio o se ha leído o superado algún concepto. */
export const hasLearnActivity = (state) =>
  state.log.length > 0 || Object.values(state.concepts).some((c) => c.read || c.placed || c.last);

/**
 * @param {object|null} index índice de learning.json (null si no se pudo cargar)
 * @param {object} state documento de progreso por conceptos
 * @param {object} [options]
 * @param {Set<string>} [options.completed] lecciones del curso PCAP completadas
 * @param {string[]} [options.lessons] orden de las lecciones del curso PCAP
 * @returns {null | {learn: object|null, pcap: object|null}}
 */
export function activitySummary(index, state, { completed = new Set(), lessons = [], now = new Date() } = {}) {
  let learn = null;
  if (index && hasLearnActivity(state)) {
    const stats = allStats(index, state, now);
    const all = [...stats.values()];
    const [next] = todayPlan(index, state, now, stats);
    const last = lastActivity(index, state);
    learn = {
      mastered: all.filter((s) => s.status === "dominado").length,
      total: all.length,
      due: all.filter((s) => s.due).length,
      errors: activeErrors(state, now).filter((e) => index.errors.has(e.id)).length,
      next: next ? { ...next, title: index.concepts.get(next.concept).title, action: ACTION[next.type] } : null,
      last: last ? { at: last.at, concept: last.concept, title: index.concepts.get(last.concept)?.title ?? last.concept } : null,
    };
  }
  // Solo cuentan las lecciones que siguen existiendo en el curso
  const done = lessons.filter((slug) => completed.has(slug));
  const pcap = done.length ? { done: done.length, total: lessons.length, next: lessons.find((slug) => !completed.has(slug)) ?? null } : null;
  return learn || pcap ? { learn, pcap } : null;
}
