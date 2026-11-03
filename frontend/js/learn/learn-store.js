/* Progreso por conceptos: se guarda en este navegador (pld:learn) y, con sesión iniciada, en la
   cuenta (/api/course-state/learn).
   El contenido (learning.json) se descarga una vez por visita. */

import { request } from "../api.js";
import { state as session, subscribe } from "../store.js";
import { createDocSync } from "../doc-sync.js";
import { createSyncGate } from "../sync-gate.js";
import { createUploader } from "../uploader.js";
import { buildIndex, cleanLearning, mergeLearning } from "./mastery.js";

const KEY = "pld:learn";
const COURSE = "learn";

function load() {
  try {
    return cleanLearning(JSON.parse(localStorage.getItem(KEY)));
  } catch {
    return cleanLearning(null); // sin almacenamiento o dañado: se empieza de cero
  }
}

/** Documento de progreso (mutable: las funciones de mastery.js lo modifican y luego se llama a saveLearning). */
export const learning = load();

const listeners = new Set();
export const onLearningChange = (listener) => listeners.add(listener);

function mergeRemote(remote) {
  mergeLearning(learning, remote.data);
  saveLearning();
}

// Sube con la versión leída: si otra pestaña guardó antes (409), relee, fusiona y reintenta
const doc = createDocSync({
  path: `/api/course-state/${COURSE}`,
  request,
  data: () => learning,
  merge: mergeRemote,
  valid: () => gate.ready,
});

// No se sube nada hasta haber fusionado la copia de la cuenta (AUD-001)
const gate = createSyncGate({
  name: "el progreso de aprendizaje",
  active: () => Boolean(session.user),
  load: () => request("GET", `/api/course-state/${COURSE}`),
  merge: (remote) => {
    mergeRemote(remote);
    doc.adopt(remote);
  },
  onSynced: () => uploader.changed(), // sube el resultado con la misma espera que cualquier cambio
});

// Estado de la subida y reintentos (uploader.js)
const uploader = createUploader({
  name: "learn",
  label: "el progreso por conceptos",
  gate,
  push: () => doc.push(),
});

export function saveLearning() {
  try {
    localStorage.setItem(KEY, JSON.stringify(learning));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
  for (const listener of listeners) listener();
  if (session.user) uploader.changed();
}


/** Sube ya el cambio pendiente (antes de cerrar sesión). Devuelve si la cuenta lo tiene todo. */
export async function flushLearnSync() {
  if (!session.user) return true;
  return uploader.flush();
}

let content = null;

/** Contenido educativo indexado (conceptos, ejercicios, errores). */
export function loadLearningContent() {
  if (!content) {
    content = fetch("data/learning.json")
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then(buildIndex);
    content.catch(() => {
      content = null; // se reintenta la próxima vez
    });
  }
  return content;
}

/** Al iniciar sesión, trae la copia de la cuenta, la fusiona y sube el resultado (con reintentos). */
export function initLearnSync() {
  subscribe((change) => {
    if (change.type !== "user") return;
    if (session.user) uploader.sessionStarted();
    else uploader.sessionEnded();
    gate.restart();
  });
}
