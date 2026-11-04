/* Repaso espaciado común (F1.2): cajas de Leitner para conceptos, preguntas del PCAP y de los cursos.
   Antes había tres copias con reglas parecidas pero no iguales (AUD-011). Funciones puras: no tocan
   el DOM ni localStorage, así que se prueban con node --test.

   Elemento: { box: 0-5, due: "AAAA-MM-DD" | null, last: ISO | null }.
   - La caja 0 es «sin repasar todavía»; los intervalos son 0, 1, 3, 7, 14 y 30 días.
   - Subir de caja solo se puede cuando el repaso ha vencido (o el elemento es nuevo). Así repetir
     cinco veces en una tarde no manda el repaso a dentro de un mes (AUD-004): lo que se acierta antes
     de tiempo se queda donde estaba.
   - Fallar devuelve siempre a la caja 1 (repaso mañana), haya vencido o no. */

export const INTERVAL_DAYS = Object.freeze([0, 1, 3, 7, 14, 30]);
export const MAX_BOX = INTERVAL_DAYS.length - 1;

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

/** ¿Toca repasarlo hoy (o se quedó atrasado)? */
export const isDue = (item, now = new Date()) => Boolean(item?.due && item.due <= isoDay(now));

/** Se puede subir de caja: nuevo, sin fecha o con el repaso vencido. */
export const canAdvance = (item, now = new Date()) => !item || !item.box || !item.due || isDue(item, now);

/**
 * Siguiente estado tras un repaso.
 * @param {{box?: number, due?: string|null}|null|undefined} item estado actual (no se modifica)
 * @param {"up"|"keep"|"down"} outcome up = bien, keep = regular, down = mal
 * @returns {{box: number, due: string, last: string}}
 */
export function schedule(item, outcome, now = new Date()) {
  const box = Number.isInteger(item?.box) ? Math.min(Math.max(item.box, 0), MAX_BOX) : 0;
  const last = now.toISOString();
  if (outcome === "down") return { box: 1, due: addDays(now, INTERVAL_DAYS[1]), last };
  if (!canAdvance(item, now)) return { box, due: item.due, last }; // antes de tiempo: no se comprime
  const next = outcome === "up" ? Math.min(box + 1, MAX_BOX) : Math.max(box, 1);
  return { box: next, due: addDays(now, INTERVAL_DAYS[next]), last };
}

/** Respuesta a una pregunta suelta (PCAP y cursos): acierto = up, fallo = down. */
export const scheduleAnswer = (item, ok, now = new Date()) => schedule(item, ok ? "up" : "down", now);
