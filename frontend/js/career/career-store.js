/* Career Roadmap: guarda el progreso en este navegador (pld:career) y, con sesión iniciada, en la
   cuenta (/api/course-state/career), con las mismas protecciones que el planificador: no se sube
   nada hasta haber fusionado la copia de la cuenta (sync-gate.js) y cada subida lleva la versión leída
   (doc-sync.js). Carga el catálogo y reúne las señales del resto de la plataforma. La lógica está en
   career-data.js. */

import { request } from "../api.js";
import { state as session, subscribe } from "../store.js";
import { createDocSync } from "../doc-sync.js";
import { createSyncGate } from "../sync-gate.js";
import { createUploader } from "../uploader.js";
import { allStats } from "../learn/mastery.js";
import { learning, loadLearningContent } from "../learn/learn-store.js";
import { courseBlockStats, loadCourseBank } from "../course-store.js";
import { cleanCareer, emptySignals, mergeCareer } from "./career-data.js";

const KEY = "pld:career";
const COURSE = "career";

function load() {
  try {
    return cleanCareer(JSON.parse(localStorage.getItem(KEY)));
  } catch {
    return cleanCareer(null);
  }
}

/** Documento del Career Roadmap (mutable: las funciones de career-data.js lo modifican y luego se llama a saveCareer). */
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
    localStorage.setItem(KEY, JSON.stringify(career));
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

export function initCareerSync() {
  subscribe((change) => {
    if (change.type !== "user") return;
    if (session.user) uploader.sessionStarted();
    else uploader.sessionEnded();
    gate.restart();
  });
}

/* ---------- Catálogo y señales ---------- */

const catalog = new Map(); // url -> Promise<json>

function fetchJson(url) {
  if (!catalog.has(url)) {
    const loading = fetch(url).then((response) => {
      if (!response.ok) throw new Error(`No se pudo cargar ${url} (HTTP ${response.status})`);
      return response.json();
    });
    loading.catch(() => catalog.delete(url)); // si falla, se reintenta la próxima vez
    catalog.set(url, loading);
  }
  return catalog.get(url);
}

/** Lista de itinerarios (data/career/index.json). */
export const loadRoadmapIndex = () => fetchJson("data/career/index.json");

/** Un itinerario completo. El id sale de la lista, nunca de texto libre. */
export async function loadRoadmap(id) {
  const index = await loadRoadmapIndex();
  if (!index.roadmaps.some((r) => r.id === id)) throw new Error(`Itinerario desconocido: ${id}`);
  return fetchJson(`data/career/${id}.json`);
}

/**
 * Señales para career-data.js: dominio de los conceptos (motor 2.0) y acierto de los bloques de los
 * cursos de DAW que usa el itinerario. Si un banco no carga, sus bloques cuentan como sin evidencias.
 */
export async function loadSignals(roadmap, now = new Date()) {
  const signals = emptySignals();
  const concepts = new Set(roadmap.skills.flatMap((s) => s.sources.concepts));
  if (concepts.size) {
    const index = await loadLearningContent();
    for (const [id, stats] of allStats(index, learning, now)) if (concepts.has(id)) signals.concepts.set(id, stats);
  }
  const courses = new Set(roadmap.skills.flatMap((s) => s.sources.blocks.map((ref) => ref.split(":")[0])));
  await Promise.all(
    [...courses].map(async (course) => {
      try {
        const stats = courseBlockStats(course, await loadCourseBank(course));
        for (const [block, value] of Object.entries(stats)) signals.blocks.set(`${course}:${block}`, value);
      } catch {
        // sin banco: esos bloques quedan sin evidencias
      }
    }),
  );
  return signals;
}
