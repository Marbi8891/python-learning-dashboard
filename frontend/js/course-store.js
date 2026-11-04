/* Progreso de los cursos de DAW en la web.
   Un documento por curso con el mismo formato que la zona PCAP
   (answers, srs, bestCombo…). Se guarda en este navegador (pld:course:<id>) y, con sesión,
   en la cuenta (/api/course-state/<id>), así que la web y la app comparten el progreso. */

import { request } from "./api.js";
import { cleanProgress } from "./progress-guard.js";
import { blockStats, newerHistory, readiness } from "./pcap-store.js";
import { isoDay, scheduleAnswer } from "./srs.js";
import { state, subscribe } from "./store.js";
import { createDocSync } from "./doc-sync.js";
import { createSyncGate } from "./sync-gate.js";
import { mergeLessonProgress } from "./lesson-progress.js";
import { createUploader } from "./uploader.js";

/** Cursos de DAW, en el orden del catálogo. `lang` es el lenguaje para resaltar el código y
    `module`, el código del módulo oficial que trabaja (sus recursos salen de data/resources.json).
    `structure` dice de dónde sale el orden de las unidades (Fase D, 6.1): los textos, ejemplos y
    preguntas son siempre propios de la plataforma (ver daw.js, «De dónde sale este contenido»). */
export const DAW_COURSES = [
  {
    id: "programacion", module: "0485", title: "Programación", subtitle: "Módulo 0485 en Python · UT1-UT9", lang: "python",
    structure: "Sigue el orden y los contenidos de las UT1-UT9 del curso «DAW-Programacion» de César San Juan Pastor (IES Arcipreste de Hita, licencia CC BY-NC), sin copiar su texto.",
  },
  {
    id: "sql", module: "0484", title: "Bases de datos", subtitle: "Módulo 0484 · SQL · UD1-UD3 del centro", lang: "sql",
    structure: "Sigue el orden de las UD1-UD3 del temario del centro, con un bloque de ampliación propio.",
  },
  {
    id: "entornos", module: "0487", title: "Entornos de desarrollo", subtitle: "Módulo 0487 · UD1 del centro", lang: "python",
    structure: "Sigue el orden de la UD1 «Desarrollo de software» del temario del centro.",
  },
  {
    id: "marcas", module: "0373", title: "Lenguajes de marcas", subtitle: "Módulo 0373 · XML, HTML, JSON y XPath", lang: "python",
    structure: "Las unidades se organizan por los resultados de aprendizaje del Real Decreto 405/2023. Los objetivos de cada lección los resumen con palabras propias y citan el RA y sus criterios.",
  },
  {
    id: "js", module: "0612", title: "JavaScript", subtitle: "Entorno cliente", lang: "javascript",
    structure: "Selección propia de la plataforma para el módulo 0612; no sigue ningún temario.",
  },
  {
    id: "java", module: "0485", title: "Java", subtitle: "Para más adelante: Java desde cero", lang: "java",
    structure: "Curso propio de la plataforma para practicar Java; no sigue ningún temario.",
  },
];

const key = (id) => `pld:course:${id}`;

const banks = new Map();

/** Banco de preguntas de un curso (se descarga una vez por visita). */
export function loadCourseBank(id) {
  if (!banks.has(id)) {
    const url = id === "pcap" ? "data/pcap.json" : `data/courses/${id}/bank.json`;
    const loading = fetch(url).then((response) => {
      if (!response.ok) throw new Error(`No se pudo cargar ${url} (HTTP ${response.status})`);
      return response.json();
    });
    loading.catch(() => banks.delete(id)); // si falla, se reintenta la próxima vez
    banks.set(id, loading);
  }
  return banks.get(id);
}
const HISTORY = 5;

function empty() {
  return { lang: "es", answers: {}, exams: [], known: [], bestCombo: 0, flags: {}, srs: {}, plan: { examDate: null }, done: {}, lastLesson: null };
}

const states = new Map();

/** Estado de un curso (se lee de este navegador la primera vez). */
export function courseState(id) {
  if (!states.has(id)) {
    let saved = null;
    try {
      saved = cleanProgress(JSON.parse(localStorage.getItem(key(id))));
    } catch {
      // almacenamiento no disponible o dañado: se empieza de cero
    }
    states.set(id, { ...empty(), ...saved });
  }
  return states.get(id);
}

// Una puerta por curso: no se sube un curso hasta haber fusionado su copia de la cuenta (AUD-001)
const gates = new Map();
const isReady = (id) => gates.get(id)?.ready === true;
// Y un documento con versión por curso: si otra pestaña guardó antes (409), relee, fusiona y reintenta
const docs = new Map();
// Estado de la subida y reintentos de cada curso (uploader.js)
const uploaders = new Map();

export function saveCourse(id) {
  try {
    localStorage.setItem(key(id), JSON.stringify(courseState(id)));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
  if (state.user) uploaders.get(id)?.changed();
}

/** Sube ya los cambios pendientes de todos los cursos (antes de cerrar sesión).
    Los cursos que aún no se habían fusionado lo intentan ahora. Devuelve si la cuenta lo tiene todo. */
export async function flushCourseSync() {
  if (!state.user) return true;
  const results = await Promise.all([...uploaders.values()].map((uploader) => uploader.flush()));
  return results.every(Boolean);
}

/** Guarda el intento y programa el repaso espaciado (cajas de Leitner comunes, srs.js). */
export function recordCourseAnswer(id, questionId, ok, now = new Date()) {
  const course = courseState(id);
  const history = (course.answers[questionId] ??= []);
  history.push(ok);
  if (history.length > HISTORY) history.shift();
  course.srs[questionId] = scheduleAnswer(course.srs[questionId], ok, now);
}

export const dueQuestionIds = (id, ids, today = isoDay()) => {
  const { srs } = courseState(id);
  return ids.filter((q) => srs[q] && srs[q].due <= today);
};

/** Acierto por bloque con el último intento de cada pregunta, como la app (mismas reglas que el PCAP). */
export const courseBlockStats = (id, bank) => blockStats(bank.questions, bank.exam.blocks, courseState(id).answers);

/** Preparación con cobertura (AUD-006): la misma fórmula que el PCAP. */
export const courseReadiness = readiness;

const later = (a, b) => ((a?.last ?? "") >= (b?.last ?? "") ? a : b);

/**
 * Fusiona la copia de la cuenta con la local sin perder nada de ninguna (mismas reglas que la app).
 * Los campos que la web no conoce (los que añada la app en el futuro) se conservan.
 */
export function mergeCourse(id, remote = {}) {
  const local = courseState(id);
  const clean = cleanProgress(remote);
  const base = { ...empty(), ...clean };
  for (const [field, value] of Object.entries(clean)) if (!(field in local)) local[field] = value;
  for (const [q, history] of Object.entries(base.answers)) {
    local.answers[q] = newerHistory(local.answers[q], history, local.srs[q]?.last, base.srs[q]?.last);
  }
  const exams = new Map([...base.exams, ...local.exams].map((exam) => [exam.date, exam]));
  local.exams = [...exams.values()].sort((a, b) => a.date.localeCompare(b.date)).slice(-30);
  local.known = [...new Set([...local.known, ...base.known])];
  local.bestCombo = Math.max(local.bestCombo, base.bestCombo);
  for (const [flag, value] of Object.entries(base.flags ?? {})) local.flags[flag] ||= Boolean(value);
  for (const [q, item] of Object.entries(base.srs)) local.srs[q] = later(local.srs[q], item);
  local.plan.examDate ??= base.plan?.examDate ?? null;
  mergeLessonProgress(local, clean); // lecciones completadas (unión) y última lección (la más reciente)
}

/** Al iniciar sesión, trae y fusiona el progreso de cada curso guardado en la cuenta.
    Cada curso se sube solo después de fusionarse bien; si falla, se reintenta. */
export function initCourseSync(onMerged) {
  for (const { id } of DAW_COURSES) {
    const mergeRemote = (remote) => {
      mergeCourse(id, remote.data);
      saveCourse(id);
    };
    docs.set(
      id,
      createDocSync({
        path: `/api/course-state/${id}`,
        request,
        data: () => courseState(id),
        merge: mergeRemote,
        valid: () => isReady(id),
      }),
    );
    gates.set(
      id,
      createSyncGate({
        name: `el curso ${id}`,
        active: () => Boolean(state.user),
        load: () => request("GET", `/api/course-state/${id}`),
        merge: (remote) => {
          mergeRemote(remote);
          docs.get(id).adopt(remote);
        },
        onSynced: () => {
          uploaders.get(id).changed({ now: true }); // sube ya el resultado de la fusión
          onMerged();
        },
      }),
    );
    const { title } = DAW_COURSES.find((course) => course.id === id);
    uploaders.set(
      id,
      createUploader({ name: `course:${id}`, label: `el curso ${title}`, gate: gates.get(id), push: () => docs.get(id).push() }),
    );
  }
  subscribe((change) => {
    if (change.type !== "user") return;
    for (const uploader of uploaders.values()) {
      if (state.user) uploader.sessionStarted();
      else uploader.sessionEnded();
    }
    for (const gate of gates.values()) gate.restart();
  });
}
