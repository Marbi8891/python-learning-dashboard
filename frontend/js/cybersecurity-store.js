/* Progreso del curso de ciberseguridad: se guarda en este navegador y, con sesión iniciada, en la cuenta
   (/api/course-state/cybersecurity), con las mismas protecciones que el itinerario profesional: no se
   sube nada hasta haber fusionado la copia de la cuenta (sync-gate.js) y cada subida lleva la versión
   leída (doc-sync.js). Antes solo vivía en el navegador y cerrar sesión lo borraba sin copia.

   La clave del navegador sigue siendo pld:cybersecurity:v1 para leer el progreso que ya tenía cada
   alumno; dentro va el documento nuevo (cybersecurity-data.js, v: 2). Se carga con la web, no con la
   zona: así la fusión al entrar y la subida antes de cerrar sesión ocurren aunque no se abra el curso. */

import { request } from "./api.js";
import { state as session, subscribe } from "./store.js";
import { createDocSync } from "./doc-sync.js";
import { createSyncGate } from "./sync-gate.js";
import { createUploader } from "./uploader.js";
import { cleanCyber, mergeCyber } from "./cybersecurity-data.js";
import { storage } from "./demo/demo-mode.js";

const KEY = "pld:cybersecurity:v1";
const COURSE = "cybersecurity";

function load() {
  try {
    return cleanCyber(JSON.parse(storage.getItem(KEY)));
  } catch {
    return cleanCyber(null);
  }
}

/** Documento del curso (mutable: las funciones de cybersecurity-data.js lo modifican y luego se llama a saveCyber). */
export const cyber = load();

const listeners = new Set();
/** Avisa cuando la copia de la cuenta cambia lo que se ve (no en los cambios hechos en esta pestaña). */
export const onCyberMerged = (listener) => listeners.add(listener);

function mergeRemote(remote) {
  if (!mergeCyber(cyber, remote.data)) return;
  store();
  for (const listener of listeners) listener();
}

const doc = createDocSync({
  path: `/api/course-state/${COURSE}`,
  request,
  data: () => cyber,
  merge: mergeRemote,
  valid: () => gate.ready,
});

const gate = createSyncGate({
  name: "el curso de ciberseguridad",
  active: () => Boolean(session.user),
  load: () => request("GET", `/api/course-state/${COURSE}`),
  merge: (remote) => {
    mergeRemote(remote);
    doc.adopt(remote);
  },
  onSynced: () => uploader.changed({ now: true }),
});

const uploader = createUploader({
  name: COURSE,
  label: "el curso de ciberseguridad",
  gate,
  push: () => doc.push(),
});

function store() {
  try {
    storage.setItem(KEY, JSON.stringify(cyber));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
}

export function saveCyber() {
  store();
  if (session.user) uploader.changed();
}

/** Sube ya el cambio pendiente (antes de cerrar sesión). Devuelve si la cuenta lo tiene todo. */
export async function flushCyberSync() {
  if (!session.user) return true;
  return uploader.flush();
}

export function initCyberSync() {
  subscribe((change) => {
    if (change.type !== "user") return;
    if (session.user) uploader.sessionStarted();
    else uploader.sessionEnded();
    gate.restart();
  });
}
