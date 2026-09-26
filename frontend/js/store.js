/* Estado compartido: progreso (local + cuenta) y sesión del usuario. */

import { ApiError, apiEnabled, getToken, request, setToken } from "./api.js";

const PROGRESS_KEY = "pld:completed";
const listeners = new Set();

function readLocal() {
  try {
    return new Set(JSON.parse(localStorage.getItem(PROGRESS_KEY)) ?? []);
  } catch {
    return new Set();
  }
}

export const state = {
  completed: readLocal(),
  user: null,
};

export function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function emit(change) {
  for (const listener of listeners) listener(change);
}

function saveLocal() {
  try {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify([...state.completed]));
  } catch {
    // Sin almacenamiento: el progreso dura hasta recargar.
  }
}

/** Marca o desmarca una lección. Con sesión iniciada, también en el servidor. */
export async function setCompleted(slug, done) {
  if (done) state.completed.add(slug);
  else state.completed.delete(slug);
  saveLocal();
  emit({ type: "progress" });
  if (!state.user) return;
  try {
    await request(done ? "PUT" : "DELETE", `/api/progress/${encodeURIComponent(slug)}`);
  } catch (error) {
    console.warn("No se pudo sincronizar el progreso:", error.message);
  }
}

/** Guarda un intento de ejercicio (solo con sesión). Si pasó, el servidor completa la lección. */
export async function recordAttempt(slug, code, passed) {
  if (passed) await setCompleted(slug, true);
  if (!state.user) return;
  try {
    await request("POST", `/api/lessons/${encodeURIComponent(slug)}/attempts`, { json: { code, passed } });
  } catch (error) {
    console.warn("No se pudo guardar el intento:", error.message);
  }
}

/** Tras iniciar sesión: sube el progreso local y adopta la lista fusionada del servidor. */
async function syncProgress() {
  const merged = await request("POST", "/api/progress/import", {
    json: { lesson_slugs: [...state.completed] },
  });
  state.completed = new Set(merged.map((item) => item.lesson_slug));
  saveLocal();
  emit({ type: "progress" });
}

export async function startSession(token) {
  setToken(token);
  state.user = await request("GET", "/api/users/me");
  emit({ type: "user" });
  await syncProgress();
}

/** Al cargar la página: recupera la sesión guardada, si sigue siendo válida. */
export async function restoreSession() {
  if (!apiEnabled || !getToken()) return;
  try {
    await startSession(getToken());
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) endSession();
    else console.warn("Servidor no disponible; se sigue en modo local:", error.message);
  }
}

export function endSession() {
  setToken(null);
  state.user = null;
  emit({ type: "user" });
}

window.addEventListener("pld:session-expired", () => {
  if (!state.user) return;
  state.user = null;
  emit({ type: "user", expired: true });
});
