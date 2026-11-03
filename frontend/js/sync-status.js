/* Qué parte del progreso está ya guardada en la cuenta (SYNC-01 y SYNC-04).

   Cada almacén que se sincroniza (lecciones, PCAP, cada curso, núcleo por conceptos y logros) tiene
   uno de estos estados:
   - "saved": el servidor confirmó la última copia (o no hay sesión: no hay nada que subir).
   - "pending": hay cambios locales que todavía no ha confirmado el servidor.
   - "failed": la última subida falló; se reintentará.

   Cerrar sesión borra el progreso de este navegador, así que antes se comprueba aquí que no quede
   nada sin confirmar. No depende del DOM, para poder probarlo con node --test. */

const entries = new Map(); // nombre → { label, state }
const listeners = new Set();

function emit() {
  for (const listener of listeners) listener();
}

/** Da de alta un almacén con el nombre que verá el alumno (p. ej. «la preparación del PCAP»). */
export function registerSyncStore(name, label) {
  if (!entries.has(name)) entries.set(name, { label, state: "saved" });
}

export function setSyncState(name, state) {
  const entry = entries.get(name);
  if (!entry || entry.state === state) return;
  entry.state = state;
  emit();
}

export const syncState = (name) => entries.get(name)?.state ?? "saved";

/** Almacenes con cambios que el servidor aún no ha confirmado (pendientes o con fallo). */
export const unsavedStores = () =>
  [...entries.values()].filter((entry) => entry.state !== "saved").map((entry) => entry.label);

/** Almacenes cuya última subida falló. */
export const failedStores = () =>
  [...entries.values()].filter((entry) => entry.state === "failed").map((entry) => entry.label);

export function onSyncStateChange(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Solo para las pruebas. */
export function resetSyncStatus() {
  entries.clear();
  listeners.clear();
}
