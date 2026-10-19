/* Cálculos del panel del alumno (ADR-0035). Funciones puras, sin DOM ni almacenamiento:
   se prueban con node --test. Nunca inventan datos: si algo no se puede calcular, devuelven null. */

/** Secciones del panel, en el orden del menú. La primera es la de entrada. */
export const SECTIONS = [
  { id: "resumen", label: "Resumen" },
  { id: "cursos", label: "Mis cursos" },
  { id: "progreso", label: "Mi progreso" },
  { id: "actividad", label: "Actividad" },
  { id: "planificacion", label: "Planificación" },
  { id: "logros", label: "Logros" },
  { id: "perfil", label: "Mi perfil" },
];

export const PANEL_ROUTE = "#/panel";

/** Sección de una ruta «#/panel/<sección>»; cualquier otra cosa lleva al resumen. */
export function sectionFromRoute(hash) {
  const id = hash.startsWith(`${PANEL_ROUTE}/`) ? hash.slice(PANEL_ROUTE.length + 1) : "";
  return SECTIONS.some((s) => s.id === id) ? id : SECTIONS[0].id;
}

/** Fecha de la API. SQLite (en local) las devuelve sin zona: siempre son UTC. */
export function parseServerDate(value) {
  if (typeof value !== "string" || !value) return null;
  const date = new Date(/(Z|[+-]\d{2}:?\d{2})$/.test(value) ? value : `${value}Z`);
  return Number.isNaN(date.getTime()) ? null : date;
}

export const isoDay = (date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

/** Última vez que se practicó un curso con banco de preguntas (repaso espaciado), o null. */
export function lastPractice(courseState) {
  const moments = Object.values(courseState?.srs ?? {})
    .map((item) => item?.last)
    .filter((last) => typeof last === "string" && !Number.isNaN(Date.parse(last)));
  return moments.length ? moments.sort().at(-1) : null;
}

/** La actividad más reciente de una lista de candidatas { at, ... } (at puede faltar). */
export function latestActivity(candidates) {
  return (
    candidates
      .filter((c) => c && c.at instanceof Date && !Number.isNaN(c.at.getTime()))
      .sort((a, b) => b.at - a.at)[0] ?? null
  );
}

/**
 * Actividad por día de los últimos `days` días (hora local), para la gráfica de evolución.
 * - serverDaily: [{ day: "AAAA-MM-DD", lessons_completed, attempts }] del curso PCAP (ya en hora local).
 * - learnLog: [{ at: ISO }] ejercicios del núcleo por conceptos.
 * Devuelve un elemento por día, también los días sin actividad, del más antiguo al de hoy.
 */
export function dailySeries({ serverDaily = [], learnLog = [], days = 30, now = new Date() }) {
  const series = [];
  const byDay = new Map();
  for (let i = days - 1; i >= 0; i -= 1) {
    const date = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
    const item = { day: isoDay(date), lessons: 0, attempts: 0, concepts: 0, total: 0 };
    series.push(item);
    byDay.set(item.day, item);
  }
  for (const entry of serverDaily) {
    const item = byDay.get(entry.day);
    if (!item) continue;
    item.lessons += entry.lessons_completed;
    item.attempts += entry.attempts;
  }
  for (const entry of learnLog) {
    const at = new Date(entry.at);
    const item = Number.isNaN(at.getTime()) ? null : byDay.get(isoDay(at));
    if (item) item.concepts += 1;
  }
  for (const item of series) item.total = item.lessons + item.attempts + item.concepts;
  return series;
}

/**
 * Simulacros de todos los cursos: cuántos y la mejor nota (0-100).
 * Los del núcleo guardan aciertos/total; los del PCAP y DAW guardan su nota.
 */
export function examSummary({ learnExams = [], courseExams = [] }) {
  const scores = [
    ...learnExams.filter((e) => e.total > 0).map((e) => Math.round((e.correct / e.total) * 100)),
    ...courseExams.map((e) => e.score).filter((score) => Number.isFinite(score)),
  ];
  return { count: scores.length, best: scores.length ? Math.max(...scores) : null };
}

/** Errores que se repiten (al menos `min` veces), de más a menos frecuentes. */
export function recurringErrors(errors = {}, { min = 2, limit = 5 } = {}) {
  return Object.entries(errors)
    .filter(([, e]) => e.n >= min)
    .sort((a, b) => b[1].n - a[1].n || b[1].last.localeCompare(a[1].last))
    .slice(0, limit)
    .map(([id, e]) => ({ id, ...e }));
}

/** Porcentaje entero solo si el denominador se conoce y no es cero. */
export const safePercent = (done, total) => (Number.isInteger(total) && total > 0 ? Math.round((done / total) * 100) : null);
