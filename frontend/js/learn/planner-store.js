/* Planificador diario (F1.8): se guarda en este navegador (pld:planner) y, con sesión iniciada, en la
   cuenta (/api/course-state/planner), con las mismas protecciones que el progreso por conceptos:
   no se sube nada hasta haber fusionado la copia de la cuenta (sync-gate.js) y cada subida lleva la
   versión leída (doc-sync.js). La lógica está en planner.js. */

import { request } from "../api.js";
import { state as session, subscribe } from "../store.js";
import { createDocSync } from "../doc-sync.js";
import { createSyncGate } from "../sync-gate.js";
import { createUploader } from "../uploader.js";
import { cleanPlanner, mergePlanner, postponedYesterday, setMinutes, todayTasks, upcomingExams } from "./planner.js";

const KEY = "pld:planner";
const COURSE = "planner";
// Antes de F1.8 el tiempo diario solo se guardaba aquí (EVO-08): se lleva al planificador una vez
const OLD_MINUTES_KEY = "pld:daily-study-minutes";

function load() {
  let planner;
  try {
    planner = cleanPlanner(JSON.parse(localStorage.getItem(KEY)));
  } catch {
    planner = cleanPlanner(null);
  }
  try {
    const old = Number(localStorage.getItem(OLD_MINUTES_KEY));
    if (!planner.minutesAt && old) setMinutes(planner, old);
  } catch {
    // sin almacenamiento
  }
  return planner;
}

/** Documento del planificador (mutable: las funciones de planner.js lo modifican y luego se llama a savePlanner). */
export const planner = load();

const listeners = new Set();
export const onPlannerChange = (listener) => listeners.add(listener);

function mergeRemote(remote) {
  mergePlanner(planner, remote.data);
  savePlanner();
}

const doc = createDocSync({
  path: `/api/course-state/${COURSE}`,
  request,
  data: () => planner,
  merge: mergeRemote,
  valid: () => gate.ready,
});

const gate = createSyncGate({
  name: "el planificador",
  active: () => Boolean(session.user),
  load: () => request("GET", `/api/course-state/${COURSE}`),
  merge: (remote) => {
    mergeRemote(remote);
    doc.adopt(remote);
  },
  onSynced: () => uploader.changed({ now: true }),
});

const uploader = createUploader({
  name: "planner",
  label: "el planificador",
  gate,
  push: () => doc.push(),
});

export function savePlanner() {
  try {
    localStorage.setItem(KEY, JSON.stringify(planner));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
  for (const listener of listeners) listener();
  if (session.user) uploader.changed();
}

/** Sube ya el cambio pendiente (antes de cerrar sesión). Devuelve si la cuenta lo tiene todo. */
export async function flushPlannerSync() {
  if (!session.user) return true;
  return uploader.flush();
}

/** Opciones de todayPlan() según el planificador: exámenes próximos, lo ya decidido hoy y lo pospuesto ayer. */
export function planOptions(now = new Date()) {
  return { exams: upcomingExams(planner, now), skip: new Set(Object.keys(todayTasks(planner, now))), postponed: postponedYesterday(planner, now) };
}

export function initPlannerSync() {
  subscribe((change) => {
    if (change.type !== "user") return;
    if (session.user) uploader.sessionStarted();
    else uploader.sessionEnded();
    gate.restart();
  });
}
