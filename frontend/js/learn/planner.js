/* Planificador diario (F1.8): tiempo disponible, fechas de exámenes y entregas, y lo que el alumno
   hace con cada tarea del plan (hecha, pospuesta o rechazada). Funciones puras sobre un documento
   JSON: no tocan el DOM ni localStorage (eso lo hace planner-store.js), así que se prueban con node --test.

   Documento (clave pld:planner y /api/course-state/planner):
   {
     v: 1,
     minutes: 15-180, minutesAt: ISO | null,            tiempo disponible al día y cuándo se cambió
     exams: [ { id, title, module, date: "AAAA-MM-DD", kind: "examen" | "entrega", at: ISO, deleted? } ],
     days: { "AAAA-MM-DD": { [idConcepto]: { status: "hecha" | "pospuesta" | "rechazada", at: ISO } } }
   }
   Los exámenes borrados se quedan marcados (`deleted`) para que otro dispositivo no los resucite al fusionar.
   Los días se guardan como mucho HISTORY_DAYS. */

import { daysBetween, isoDay } from "../srs.js";

export const HISTORY_DAYS = 30;
export const STATUSES = Object.freeze(["hecha", "pospuesta", "rechazada"]);
/** «pendiente» = deshecho: se guarda con fecha para que la fusión no resucite el estado anterior. */
const STORED = [...STATUSES, "pendiente"];
export const EXAM_KINDS = Object.freeze(["examen", "entrega"]);
export const DEFAULT_MINUTES = 45;
const MAX_EXAMS = 40;

const DAY = /^\d{4}-\d{2}-\d{2}$/;
const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const ID = /^[a-z0-9][a-z0-9.-]{0,60}$/;
const MODULE = /^(\d{4}|pcap)$/;
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const isIso = (value) => typeof value === "string" && ISO.test(value);
const later = (a, b) => ((a?.at ?? "") >= (b?.at ?? "") ? a : b);

export const emptyPlanner = () => ({ v: 1, minutes: DEFAULT_MINUTES, minutesAt: null, exams: [], days: {} });

/** Minutos válidos: entre 15 y 180 (como fitPlanToBudget). */
export const clampMinutes = (value) => Math.min(180, Math.max(15, Math.round(Number(value) || DEFAULT_MINUTES)));

function cleanExam(raw) {
  if (!isObject(raw) || typeof raw.id !== "string" || !ID.test(raw.id) || !DAY.test(raw.date ?? "")) return null;
  const title = typeof raw.title === "string" ? raw.title.trim().slice(0, 80) : "";
  return {
    id: raw.id,
    title: title || "Examen",
    module: typeof raw.module === "string" && MODULE.test(raw.module) ? raw.module : null,
    date: raw.date,
    kind: EXAM_KINDS.includes(raw.kind) ? raw.kind : "examen",
    at: isIso(raw.at) ? raw.at : "1970-01-01T00:00:00.000Z",
    ...(raw.deleted === true ? { deleted: true } : {}),
  };
}

/** Valida un documento que llega de fuera (localStorage o la cuenta). Conserva los bloques que no conoce. */
export function cleanPlanner(value) {
  const planner = emptyPlanner();
  if (!isObject(value)) return planner;
  for (const [key, raw] of Object.entries(value)) if (!(key in planner) && /^[a-zA-Z][a-zA-Z0-9]{0,30}$/.test(key)) planner[key] = raw;
  if (value.minutes !== undefined) planner.minutes = clampMinutes(value.minutes);
  planner.minutesAt = isIso(value.minutesAt) ? value.minutesAt : null;
  planner.exams = (Array.isArray(value.exams) ? value.exams : []).map(cleanExam).filter(Boolean).slice(-MAX_EXAMS);
  if (isObject(value.days)) {
    for (const [day, tasks] of Object.entries(value.days)) {
      if (!DAY.test(day) || !isObject(tasks)) continue;
      const clean = {};
      for (const [concept, task] of Object.entries(tasks)) {
        if (ID.test(concept) && isObject(task) && STORED.includes(task.status) && isIso(task.at)) clean[concept] = { status: task.status, at: task.at };
      }
      if (Object.keys(clean).length) planner.days[day] = clean;
    }
  }
  return planner;
}

/** Quita los días más antiguos que HISTORY_DAYS. */
export function prune(planner, now = new Date()) {
  for (const day of Object.keys(planner.days)) if (daysBetween(`${day}T00:00:00`, now) > HISTORY_DAYS) delete planner.days[day];
  return planner;
}

export function setMinutes(planner, minutes, now = new Date()) {
  planner.minutes = clampMinutes(minutes);
  planner.minutesAt = now.toISOString();
}

/** Marca lo que el alumno ha hecho hoy con la tarea de un concepto; `null` la vuelve a dejar pendiente. */
export function setTaskStatus(planner, conceptId, status, now = new Date()) {
  const day = isoDay(now);
  const tasks = (planner.days[day] ??= {});
  if (status === null || STATUSES.includes(status)) tasks[conceptId] = { status: status ?? "pendiente", at: now.toISOString() };
  prune(planner, now);
}

/** Tareas de hoy con estado (hecha, pospuesta o rechazada); las deshechas no aparecen. */
export function todayTasks(planner, now = new Date()) {
  return Object.fromEntries(Object.entries(planner.days[isoDay(now)] ?? {}).filter(([, t]) => t.status !== "pendiente"));
}

/** Lo pospuesto ayer vuelve hoy con prioridad (se avisa en el motivo). */
export function postponedYesterday(planner, now = new Date()) {
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const tasks = planner.days[isoDay(yesterday)] ?? {};
  return new Set(Object.entries(tasks).filter(([, t]) => t.status === "pospuesta").map(([id]) => id));
}

let counter = 0;
export function addExam(planner, { title, module = null, date, kind = "examen" }, now = new Date()) {
  counter += 1;
  const exam = cleanExam({ id: `ex-${now.getTime().toString(36)}-${counter}`, title, module, date, kind, at: now.toISOString() });
  if (!exam) return null;
  planner.exams.push(exam);
  planner.exams = planner.exams.slice(-MAX_EXAMS);
  return exam;
}

export function removeExam(planner, id, now = new Date()) {
  const exam = planner.exams.find((e) => e.id === id);
  if (exam) Object.assign(exam, { deleted: true, at: now.toISOString() });
}

/** Exámenes y entregas de hoy en adelante, del más cercano al más lejano, con los días que faltan. */
export function upcomingExams(planner, now = new Date()) {
  const today = isoDay(now);
  return planner.exams
    .filter((e) => !e.deleted && e.date >= today)
    .map((e) => ({ ...e, days: -daysBetween(`${e.date}T00:00:00`, now) }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

/** Historial de los últimos `days` días: cuántas tareas se hicieron, se pospusieron o se rechazaron. */
export function plannerHistory(planner, now = new Date(), days = 7) {
  const out = [];
  for (let i = 0; i < days; i += 1) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const day = isoDay(date);
    const tasks = Object.values(planner.days[day] ?? {});
    const count = (status) => tasks.filter((t) => t.status === status).length;
    out.push({ day, hecha: count("hecha"), pospuesta: count("pospuesta"), rechazada: count("rechazada") });
  }
  return out;
}

/** Recomendaciones aceptadas (métrica de §14 del plan): hechas / decididas. null sin datos. */
export function acceptanceRate(planner) {
  const tasks = Object.values(planner.days).flatMap((day) => Object.values(day));
  const decided = tasks.length;
  return decided ? tasks.filter((t) => t.status === "hecha").length / decided : null;
}

/** Fusiona la copia de la cuenta con la local sin perder nada: gana lo cambiado más tarde. */
export function mergePlanner(local, remote) {
  const other = cleanPlanner(remote);
  if ((other.minutesAt ?? "") > (local.minutesAt ?? "")) {
    local.minutes = other.minutes;
    local.minutesAt = other.minutesAt;
  }
  const exams = new Map(local.exams.map((e) => [e.id, e]));
  for (const exam of other.exams) exams.set(exam.id, exams.has(exam.id) ? later(exams.get(exam.id), exam) : exam);
  local.exams = [...exams.values()].sort((a, b) => a.at.localeCompare(b.at)).slice(-MAX_EXAMS);
  for (const [day, tasks] of Object.entries(other.days)) {
    const mine = (local.days[day] ??= {});
    for (const [concept, task] of Object.entries(tasks)) mine[concept] = mine[concept] ? later(mine[concept], task) : task;
  }
  for (const [key, raw] of Object.entries(other)) if (!(key in local)) local[key] = raw;
  return local;
}
