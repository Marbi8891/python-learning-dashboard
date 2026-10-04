/* Progreso por conceptos: se guarda en este navegador (pld:learn) y, con sesión iniciada, en la
   cuenta (/api/course-state/learn), con el mismo documento que leerá la app Android (ADR-0031).
   El contenido (learning.json) se descarga una vez por visita. */

import { request } from "../api.js";
import { state as session, subscribe } from "../store.js";
import { buildIndex, cleanLearning, mergeLearning } from "./mastery.js";

const KEY = "pld:learn";
const COURSE = "learn";
const PUSH_DELAY_MS = 1500;

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

let timer = null;

async function push() {
  timer = null;
  try {
    await request("PUT", `/api/course-state/${COURSE}`, { json: { data: learning } });
  } catch (error) {
    console.warn("No se pudo guardar el progreso de aprendizaje en la cuenta:", error.message);
  }
}

export function saveLearning() {
  try {
    localStorage.setItem(KEY, JSON.stringify(learning));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
  for (const listener of listeners) listener();
  if (!session.user) return;
  clearTimeout(timer);
  timer = setTimeout(push, PUSH_DELAY_MS);
}

const WELCOME_KEY = "pld:welcome-seen";

/** Primera visita: nunca ha visto la bienvenida ni ha hecho ningún ejercicio. */
export function isFirstVisit() {
  if (learning.log.length > 0) return false;
  try {
    return !localStorage.getItem(WELCOME_KEY);
  } catch {
    return false; // sin almacenamiento no se puede recordar: no se insiste con la bienvenida
  }
}

export function markWelcomeSeen() {
  try {
    localStorage.setItem(WELCOME_KEY, "1");
  } catch {
    // sin almacenamiento: no pasa nada
  }
}

/** Sube ya el cambio pendiente (antes de cerrar sesión). */
export async function flushLearnSync() {
  if (!timer || !session.user) return;
  clearTimeout(timer);
  await push();
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

/** Al iniciar sesión, trae la copia de la cuenta, la fusiona y sube el resultado. */
export function initLearnSync() {
  subscribe(async (change) => {
    if (change.type !== "user" || !session.user) return;
    try {
      const remote = await request("GET", `/api/course-state/${COURSE}`);
      mergeLearning(learning, remote.data);
      saveLearning();
    } catch (error) {
      console.warn("No se pudo sincronizar el progreso de aprendizaje:", error.message);
    }
  });
}
