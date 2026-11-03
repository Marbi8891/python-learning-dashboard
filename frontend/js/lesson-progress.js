/* Progreso por lección de los cursos de DAW: lecciones completadas y última lección estudiada.
   Vive dentro del documento de cada curso (pld:course:<id> y /api/course-state/<id>), junto a
   las respuestas, así que usa la misma sincronización y la misma puerta de fusión (AUD-001).

   - done: { "<lección>": "<fecha ISO en que se completó>" }. Solo crece: completar una lección es
     idempotente y la fusión es una unión, así que una copia vacía o parcial no borra nada.
   - lastLesson: { slug, at } con la última lección abierta. En la fusión gana la más reciente. */

const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const SLUG = /^[a-z0-9][a-z0-9-]{0,79}$/;
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);

/** Lecciones completadas con un id y una fecha válidos; lo demás se descarta. */
export function cleanDone(value) {
  const clean = {};
  if (!isObject(value)) return clean;
  for (const [slug, at] of Object.entries(value)) {
    if (SLUG.test(slug) && typeof at === "string" && ISO.test(at)) clean[slug] = at;
  }
  return clean;
}

/** Última lección estudiada, o null si no es válida. */
export function cleanLastLesson(value) {
  if (!isObject(value) || typeof value.slug !== "string" || !SLUG.test(value.slug)) return null;
  if (typeof value.at !== "string" || !ISO.test(value.at)) return null;
  return { slug: value.slug, at: value.at };
}

/**
 * Fusiona en `local` el progreso por lección de `remote` sin perder nada de ninguno.
 * Una lección completada en cualquiera de los dos sigue completada (con la fecha más antigua).
 */
export function mergeLessonProgress(local, remote) {
  const done = cleanDone(local.done);
  for (const [slug, at] of Object.entries(cleanDone(remote?.done))) {
    if (!done[slug] || at < done[slug]) done[slug] = at;
  }
  local.done = done;
  const mine = cleanLastLesson(local.lastLesson);
  const theirs = cleanLastLesson(remote?.lastLesson);
  local.lastLesson = !mine ? theirs : !theirs ? mine : theirs.at > mine.at ? theirs : mine;
  return local;
}

/** Marca una lección como completada. Devuelve false si ya lo estaba (no cambia nada). */
export function completeLesson(course, slug, now = new Date().toISOString()) {
  course.done = cleanDone(course.done);
  if (course.done[slug]) return false;
  course.done[slug] = now;
  return true;
}

/** Recuerda la última lección abierta. Devuelve false si ya era esa (no hace falta guardar). */
export function visitLesson(course, slug, now = new Date().toISOString()) {
  if (course.lastLesson?.slug === slug) return false;
  course.lastLesson = { slug, at: now };
  return true;
}

/** Cuántas lecciones de `order` están completadas. */
export const completedCount = (course, order) => order.filter((slug) => course.done?.[slug]).length;
