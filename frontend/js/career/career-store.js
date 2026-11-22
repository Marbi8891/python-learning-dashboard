/* Itinerario profesional (DEC-012): se guarda en este navegador (pld:career) y, con sesión iniciada, en la
   cuenta (/api/course-state/career), con las mismas protecciones que el planificador: no se sube nada
   hasta haber fusionado la copia de la cuenta (sync-gate.js) y cada subida lleva la versión leída
   (doc-sync.js). La lógica está en career-data.js; el catálogo, en data/career/. Los datos económicos
   no pasan por aquí: career-finance.js, solo en el navegador. */

import { request } from "../api.js";
import { state as session, subscribe } from "../store.js";
import { createDocSync } from "../doc-sync.js";
import { createSyncGate } from "../sync-gate.js";
import { createUploader } from "../uploader.js";
import { cleanCareer, mergeCareer } from "./career-data.js";
import { storage } from "../demo/demo-mode.js";

const KEY = "pld:career";
const COURSE = "career";

function load() {
  try {
    return cleanCareer(JSON.parse(storage.getItem(KEY)));
  } catch {
    return cleanCareer(null);
  }
}

/** Documento del itinerario (mutable: las funciones de career-data.js lo modifican y luego se llama a saveCareer). */
export const career = load();

const listeners = new Set();
export const onCareerChange = (listener) => listeners.add(listener);

function mergeRemote(remote) {
  mergeCareer(career, remote.data);
  saveCareer();
}

const doc = createDocSync({
  path: `/api/course-state/${COURSE}`,
  request,
  data: () => career,
  merge: mergeRemote,
  valid: () => gate.ready,
});

const gate = createSyncGate({
  name: "el itinerario profesional",
  active: () => Boolean(session.user),
  load: () => request("GET", `/api/course-state/${COURSE}`),
  merge: (remote) => {
    mergeRemote(remote);
    doc.adopt(remote);
  },
  onSynced: () => uploader.changed({ now: true }),
});

const uploader = createUploader({
  name: "career",
  label: "el itinerario profesional",
  gate,
  push: () => doc.push(),
});

export function saveCareer() {
  try {
    storage.setItem(KEY, JSON.stringify(career));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
  for (const listener of listeners) listener();
  if (session.user) uploader.changed();
}

/** Sube ya el cambio pendiente (antes de cerrar sesión). Devuelve si la cuenta lo tiene todo. */
export async function flushCareerSync() {
  if (!session.user) return true;
  return uploader.flush();
}

const catalogs = new Map();

/** Catálogo de un itinerario (data/career/<id>.json), descargado una vez por visita y guardado por la PWA. */
export function loadRoadmap(id) {
  if (!catalogs.has(id)) {
    const url = `data/career/${encodeURIComponent(id)}.json`;
    const loading = fetch(url).then((response) => {
      if (!response.ok) throw new Error(`No se pudo cargar ${url} (HTTP ${response.status})`);
      return response.json();
    });
    loading.catch(() => catalogs.delete(id)); // si falla, se reintenta la próxima vez
    catalogs.set(id, loading);
  }
  return catalogs.get(id);
}

export function initCareerSync() {
  subscribe((change) => {
    if (change.type !== "user") return;
    if (session.user) uploader.sessionStarted();
    else uploader.sessionEnded();
    gate.restart();
  });
}
