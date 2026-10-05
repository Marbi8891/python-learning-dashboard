/* Estado compartido: progreso (local + cuenta) y sesión del usuario. */

import { ApiError, apiEnabled, request, setToken } from "./api.js";

const PROGRESS_KEY = "pld:completed";
// Solo un aviso de que hay una cookie de sesión (el token no se puede leer desde aquí): así, al
// cargar la página, no se pregunta a la API si no hubo sesión.
const SESSION_KEY = "pld:session";
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

function rememberSession(active) {
  try {
    if (active) localStorage.setItem(SESSION_KEY, "cookie");
    else localStorage.removeItem(SESSION_KEY);
  } catch {
    // sin almacenamiento: la sesión dura hasta recargar
  }
}

function hadSession() {
  try {
    return localStorage.getItem(SESSION_KEY) === "cookie";
  } catch {
    return false;
  }
}

/** Sin token: la sesión va en la cookie HttpOnly. Con token: solo en memoria (ADR-0033). */
export async function startSession(token = null) {
  setToken(token);
  state.user = await request("GET", "/api/users/me");
  rememberSession(!token);
  emit({ type: "user" });
  await syncProgress();
}

/** Al cargar la página: recupera la sesión de la cookie, si sigue siendo válida. */
export async function restoreSession() {
  if (!apiEnabled || !hadSession()) return;
  try {
    await startSession();
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) endSession();
    else console.warn("Servidor no disponible; se sigue en modo local:", error.message);
  }
}

/** Borra de este navegador todo lo personal (progreso, borradores, nombre del certificado,
    logros…). Se conservan solo las preferencias de aspecto. Para equipos compartidos (ADR-0022). */
export function clearLocalData() {
  try {
    for (const key of Object.keys(localStorage)) {
      if (key.startsWith("pld:") && key !== "pld:prefs") localStorage.removeItem(key);
    }
  } catch {
    // sin almacenamiento: no hay nada que borrar
  }
}

/** Datos del usuario cambiados desde «Mi cuenta» (nombre): repinta sin volver a sincronizar. */
export function updateUser(user) {
  state.user = user;
  emit({ type: "profile" });
}

export function endSession() {
  setToken(null);
  rememberSession(false);
  state.user = null;
  emit({ type: "user" });
}

window.addEventListener("pld:session-expired", () => {
  rememberSession(false);
  if (!state.user) return;
  state.user = null;
  emit({ type: "user", expired: true });
});
