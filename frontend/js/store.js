/* Estado compartido: progreso (local + cuenta) y sesión del usuario. */

import { ApiError, apiEnabled, request, setToken } from "./api.js";
import { createUploader } from "./uploader.js";
import { claimLocalProgress, STASH_PREFIX } from "./local-owner.js";

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

// Lecciones completadas que no se pudieron enviar: se reintentan subiendo la lista entera, que el
// servidor une con la suya (POST /progress/import). Al iniciar sesión ya se sube con syncProgress().
const lessonsUploader = createUploader({
  name: "lessons",
  label: "las lecciones completadas",
  gate: {
    get ready() {
      return Boolean(state.user);
    },
    sync: async () => Boolean(state.user),
  },
  push: async () => {
    if (!state.user) return false;
    await request("POST", "/api/progress/import", { json: { lesson_slugs: [...state.completed] } });
    return true;
  },
});

/** Sube ya las lecciones que no se pudieron enviar (antes de cerrar sesión). */
export async function flushLessonsSync() {
  if (!state.user) return true;
  return lessonsUploader.flush();
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
    if (done && error?.status !== 401) lessonsUploader.changed(); // se reintenta (desmarcar no se puede importar)
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

/** Sin token: la sesión va en la cookie HttpOnly. Con token: solo en memoria. */
export async function startSession(token = null) {
  setToken(token);
  const user = await request("GET", "/api/users/me");
  rememberSession(!token);
  // Se recarga con el progreso de esta cuenta: la promesa no termina para que nadie siga con la sesión
  if (claimOwnProgress(user, token)) return new Promise(() => {});
  state.user = user;
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

/** El progreso de este navegador era de otra cuenta (o esta tenía algo apartado): se cambia y se
    recarga, para que la app no mezcle cuentas (AUTH-02). Devuelve true si se va a recargar. */
function claimOwnProgress(user, token) {
  let swapped = false;
  try {
    swapped = claimLocalProgress(user.id, localStorage).swapped;
  } catch {
    return false; // sin almacenamiento no hay progreso de nadie que mezclar
  }
  if (!swapped) return false;
  try {
    sessionStorage.setItem(
      "pld:flash",
      token
        ? "En este navegador había progreso de otra cuenta: lo hemos apartado sin mezclarlo. Vuelve a iniciar sesión."
        : "En este navegador había progreso de otra cuenta: lo hemos apartado sin mezclarlo con el tuyo.",
    );
  } catch {
    // sin aviso: se recarga igualmente
  }
  location.reload();
  return true;
}

/** Borra de este navegador todo lo personal (progreso, borradores, nombre del certificado,
    logros…). Se conservan solo las preferencias de aspecto. Para equipos compartidos. */
export function clearLocalData() {
  try {
    for (const key of Object.keys(localStorage)) {
      // Lo apartado de otras cuentas (AUTH-02) no es de quien cierra la sesión: se conserva
      if (key.startsWith("pld:") && key !== "pld:prefs" && !key.startsWith(STASH_PREFIX)) localStorage.removeItem(key);
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
  lessonsUploader.sessionEnded();
  emit({ type: "user" });
}

window.addEventListener("pld:session-expired", () => {
  rememberSession(false);
  if (!state.user) return;
  state.user = null;
  lessonsUploader.sessionEnded();
  emit({ type: "user", expired: true });
});
