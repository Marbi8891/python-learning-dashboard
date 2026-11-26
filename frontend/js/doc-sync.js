/* Subida de un documento de progreso con control de versiones (dos pestañas sin pisarse).

   El servidor guarda el documento entero. Cada subida dice qué versión de la cuenta leyó la app
   (`version`). Si otra pestaña o dispositivo guardó entre medias, el servidor responde 409: se
   vuelve a leer la cuenta, se fusiona con la copia local (nunca se pierde lo de ninguno de los dos)
   y se reintenta con la versión nueva.

   Nunca se sube sin versión (PLD-003): si aún no se conoce (no se ha leído la cuenta), primero se lee
   y se fusiona. El servidor responde 428 a un guardado sin versión de un documento que ya existe; se
   trata igual que un 409 (releer, fusionar y reintentar).

   No depende del DOM: `request` se inyecta para poder probarlo con node --test. */

export const MAX_CONFLICT_RETRIES = 3;
/** Respuestas que significan «vuelve a leer la cuenta y fusiona»: 409 Conflict y 428 Precondition Required. */
const REREAD_STATUSES = new Set([409, 428]);

/**
 * @param {object} options
 * @param {string} options.path ruta de la API del documento
 * @param {(method: string, path: string, options?: object) => Promise<any>} options.request
 * @param {() => object} options.data el documento local que se sube
 * @param {(remote: {data: object, version: number}) => void} options.merge fusiona la copia de la cuenta con la local
 * @param {() => boolean} options.valid si se puede seguir (la sesión no ha cambiado)
 */
export function createDocSync({ path, request, data, merge, valid }) {
  let version = null;

  function adopt(remote) {
    version = Number.isInteger(remote?.version) ? remote.version : null;
  }

  /** Sube el documento. Devuelve true si quedó guardado; lanza el error si no es un conflicto. */
  async function push() {
    if (!valid()) return false;
    if (version === null && !(await reread())) return false; // sin versión no se sube: se lee antes
    for (let attempt = 0; ; attempt += 1) {
      if (!valid()) return false;
      try {
        adopt(await request("PUT", path, { json: { data: data(), version } }));
        return true;
      } catch (error) {
        if (!REREAD_STATUSES.has(error?.status) || attempt >= MAX_CONFLICT_RETRIES) throw error;
      }
      // Otra pestaña guardó antes: se trae su versión y se fusiona antes de reintentar
      if (!(await reread())) return false;
    }
  }

  /** Trae la copia de la cuenta, la fusiona con la local y adopta su versión. False si la sesión cambió. */
  async function reread() {
    const remote = await request("GET", path);
    if (!valid()) return false;
    merge(remote);
    adopt(remote);
    return true;
  }

  return {
    adopt,
    push,
    get version() {
      return version;
    },
  };
}
