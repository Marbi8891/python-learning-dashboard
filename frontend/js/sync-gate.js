/* Puerta de sincronización con la cuenta (AUD-001).

   Cada almacén que se guarda en la cuenta (PCAP, cursos de DAW, núcleo por conceptos y logros)
   sube su documento completo con un PUT, y el servidor lo guarda tal cual. Si se subiera antes de
   fusionar la copia de la cuenta, se borraría lo hecho en otro dispositivo. Por eso:

   - Hasta que la fusión inicial (GET + fusión) sale bien, `ready` es false y no se sube nada.
   - Si la fusión falla (el servidor está despertando, un 5xx, sin red), se reintenta con espera.
   - Al cerrar o cambiar de sesión se vuelve a cerrar la puerta.
   - La lectura (`load`) y la fusión (`merge`) van separadas: si la sesión cambia mientras se lee,
     la copia leída se descarta sin tocar los datos locales (no se mezcla la cuenta de otro usuario
     ni se vuelve a escribir en el navegador después de borrarlo al cerrar sesión).

   No depende del DOM ni de la API, para poder probarlo con node --test. */

export const RETRY_DELAYS_MS = [2_000, 10_000, 30_000, 60_000];

/**
 * @param {object} options
 * @param {string} options.name qué se sincroniza (para los avisos de la consola)
 * @param {() => Promise<any>} options.load trae la copia de la cuenta (no toca los datos locales)
 * @param {(remote: any) => void} options.merge fusiona esa copia con la local (solo si la sesión sigue)
 * @param {() => (void|Promise<void>)} options.onSynced sube el resultado y repinta
 * @param {() => boolean} options.active si hay sesión iniciada
 * @param {number[]} [options.delays] esperas entre reintentos
 * @param {(fn: () => void, ms: number) => any} [options.schedule] setTimeout (inyectable en las pruebas)
 * @param {(timer: any) => void} [options.cancel] clearTimeout
 */
export function createSyncGate({
  name,
  load,
  merge,
  onSynced,
  active,
  delays = RETRY_DELAYS_MS,
  schedule = setTimeout,
  cancel = clearTimeout,
}) {
  let ready = false;
  let running = null;
  let retryTimer = null;
  let attempt = 0;
  let session = 0; // cambia con cada inicio o cierre de sesión: invalida las fusiones antiguas

  async function attemptSync(current) {
    try {
      const remote = await load();
      if (current !== session || !active()) return false; // la sesión cambió mientras se leía
      merge(remote);
    } catch (error) {
      console.warn(`No se pudo sincronizar ${name}:`, error?.message ?? error);
      return false;
    }
    ready = true;
    attempt = 0;
    await onSynced();
    return true;
  }

  /** Intenta la fusión inicial ya (una sola a la vez). Devuelve si la puerta está abierta. */
  function sync() {
    if (ready) return Promise.resolve(true);
    if (!active()) return Promise.resolve(false);
    if (!running) {
      const current = session;
      running = attemptSync(current).finally(() => {
        if (current === session) running = null;
      });
    }
    return running;
  }

  async function syncWithRetry() {
    retryTimer = null;
    const current = session;
    const ok = await sync();
    if (ok || current !== session || !active() || attempt >= delays.length) return;
    retryTimer = schedule(syncWithRetry, delays[attempt]);
    attempt += 1;
  }

  /** Se llama en cada cambio de sesión: cierra la puerta y, si hay sesión, empieza a sincronizar. */
  function restart() {
    session += 1;
    ready = false;
    running = null;
    attempt = 0;
    if (retryTimer !== null) cancel(retryTimer);
    retryTimer = null;
    if (active()) return syncWithRetry();
    return Promise.resolve();
  }

  return {
    get ready() {
      return ready;
    },
    sync,
    restart,
  };
}
