/* Subida a la cuenta de un almacén de progreso, con estado y reintentos (SYNC-01 y SYNC-04).

   - `changed()`: hubo un cambio local. Queda "pendiente" y se sube tras una breve espera (agrupa los
     cambios seguidos). Si la fusión inicial aún no ha salido bien (sync-gate.js), no se sube nada:
     queda pendiente hasta que la puerta se abra.
   - Si la subida falla, queda "con fallo" y se reintenta con espera creciente. Un 401 (sesión
     caducada) no se reintenta: se subirá al volver a entrar.
   - Solo pasa a "guardado" cuando el servidor confirma la copia que incluye el último cambio: si
     hubo otro cambio mientras se subía, sigue pendiente.
   - `flush()` sube ya lo pendiente (antes de cerrar sesión) y devuelve si quedó todo guardado.

   No depende del DOM ni de la API, para poder probarlo con node --test. */

import { RETRY_DELAYS_MS } from "./sync-gate.js";
import { registerSyncStore, setSyncState, syncState } from "./sync-status.js";

export const PUSH_DELAY_MS = 1500;

/**
 * @param {object} options
 * @param {string} options.name identificador del almacén
 * @param {string} options.label nombre para el alumno
 * @param {{ready: boolean, sync: () => Promise<boolean>}} options.gate puerta de la fusión inicial
 * @param {() => Promise<boolean>} options.push sube el documento; true si el servidor lo guardó
 * @param {number} [options.delayMs] espera para agrupar cambios
 * @param {number[]} [options.retryDelays] esperas entre reintentos tras un fallo
 * @param {(fn: () => void, ms: number) => any} [options.schedule] setTimeout (inyectable en las pruebas)
 * @param {(timer: any) => void} [options.cancel] clearTimeout
 */
export function createUploader({
  name,
  label,
  gate,
  push,
  delayMs = PUSH_DELAY_MS,
  retryDelays = RETRY_DELAYS_MS,
  schedule = setTimeout,
  cancel = clearTimeout,
}) {
  registerSyncStore(name, label);
  let timer = null;
  let attempt = 0;
  let changes = 0; // cuántos cambios locales ha habido: la subida solo confirma los que llevaba

  function clear() {
    if (timer !== null) cancel(timer);
    timer = null;
  }

  async function upload() {
    clear();
    if (!gate.ready) return false;
    const sent = changes;
    try {
      if (!(await push())) return false; // la sesión cambió mientras se subía
    } catch (error) {
      console.warn(`No se pudo guardar ${label} en la cuenta:`, error?.message ?? error);
      setSyncState(name, "failed");
      if (error?.status !== 401 && attempt < retryDelays.length && timer === null) {
        timer = schedule(upload, retryDelays[attempt]);
        attempt += 1;
      }
      return false;
    }
    attempt = 0;
    if (sent === changes) setSyncState(name, "saved");
    return true;
  }

  /** Hubo un cambio local con la sesión abierta. Con `now` (al terminar la fusión inicial) se sube
      sin esperar: otro dispositivo que entre a la vez debe encontrar ya la copia fusionada. */
  function changed({ now = false } = {}) {
    changes += 1;
    if (syncState(name) !== "failed") setSyncState(name, "pending"); // el aviso de fallo sigue hasta subirlo
    if (!gate.ready) return;
    clear();
    timer = schedule(upload, now ? 0 : delayMs);
  }

  /** Al iniciar sesión: lo local aún no está en la cuenta hasta fusionarlo y subirlo. */
  function sessionStarted() {
    clear();
    attempt = 0;
    changes += 1;
    setSyncState(name, "pending");
  }

  /** Al cerrar o perder la sesión: ya no hay nada que subir a ninguna cuenta. */
  function sessionEnded() {
    clear();
    attempt = 0;
    setSyncState(name, "saved");
  }

  /** Sube ya lo pendiente. Devuelve si el servidor tiene todo lo de este almacén. */
  async function flush() {
    if (!gate.ready && !(await gate.sync())) return syncState(name) === "saved";
    if (syncState(name) === "saved") return true;
    await upload();
    return syncState(name) === "saved";
  }

  return {
    changed,
    flush,
    sessionStarted,
    sessionEnded,
    get state() {
      return syncState(name);
    },
  };
}
