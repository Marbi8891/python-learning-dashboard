/* De quién es el progreso guardado en este navegador (AUTH-02).

   Al cerrar sesión con todo guardado, el progreso se borra del navegador. Pero queda en él cuando la
   sesión caduca o cuando el alumno elige conservar lo que no se pudo subir (SYNC-01). Si después
   entra OTRA cuenta en el mismo equipo (un aula), la fusión inicial subiría a esa cuenta el progreso
   de la primera. Para evitarlo se apunta el dueño (`pld:owner`, el id de la cuenta):

   - Sin dueño (progreso sin cuenta o de antes de este cambio): se fusiona con la cuenta que entra,
     como siempre.
   - Mismo dueño: se fusiona.
   - Otro dueño: no se mezcla ni se borra. Se aparta en `pld:stash:<id>` y, si la cuenta que entra
     tenía algo apartado, se recupera. Cuando la primera cuenta vuelva a entrar, recuperará lo suyo.

   No depende del DOM: el almacenamiento se inyecta para poder probarlo con node --test. */

export const OWNER_KEY = "pld:owner";
export const STASH_PREFIX = "pld:stash:";

// Claves de pld: que no son progreso de nadie
const NOT_PROGRESS = new Set(["pld:prefs", "pld:session", OWNER_KEY, "pld:flash", "pld:lang-suggested"]);

export const isProgressKey = (key) => key.startsWith("pld:") && !NOT_PROGRESS.has(key) && !key.startsWith(STASH_PREFIX);

const keysOf = (storage) => {
  const keys = [];
  for (let i = 0; i < storage.length; i += 1) keys.push(storage.key(i));
  return keys;
};

/**
 * Prepara el progreso local para la cuenta `userId` que acaba de entrar.
 * @returns {{swapped: boolean}} swapped = se apartó o recuperó progreso: hay que recargar la página
 *   para que la app lea el progreso que ahora corresponde.
 */
export function claimLocalProgress(userId, storage) {
  const me = String(userId);
  const owner = storage.getItem(OWNER_KEY);
  const progress = keysOf(storage).filter(isProgressKey);
  const stashed = storage.getItem(STASH_PREFIX + me);
  const foreign = owner !== null && owner !== me && progress.length > 0;
  storage.setItem(OWNER_KEY, me);
  if (!foreign && stashed === null) return { swapped: false };
  let swapped = foreign;

  if (foreign) {
    // Lo de la otra cuenta se aparta entero (sumado a lo que ya tuviera apartado) y se quita de aquí
    const previous = JSON.parse(storage.getItem(STASH_PREFIX + owner) ?? "{}");
    const saved = Object.fromEntries(progress.map((key) => [key, storage.getItem(key)]));
    storage.setItem(STASH_PREFIX + owner, JSON.stringify({ ...previous, ...saved }));
    for (const key of progress) storage.removeItem(key);
  }
  if (stashed !== null) {
    // Se recupera lo apartado de esta cuenta. Si aquí hay progreso sin cuenta en la misma clave, no se
    // pisa: esa parte sigue apartada y se recuperará la próxima vez que no choque.
    const left = {};
    for (const [key, value] of Object.entries(JSON.parse(stashed))) {
      if (!isProgressKey(key)) continue;
      if (storage.getItem(key) === null) {
        storage.setItem(key, value);
        swapped = true;
      } else left[key] = value;
    }
    if (Object.keys(left).length) storage.setItem(STASH_PREFIX + me, JSON.stringify(left));
    else storage.removeItem(STASH_PREFIX + me);
  }
  // Solo hace falta recargar si cambió algo (si todo lo apartado choca, no se recarga en bucle)
  return { swapped };
}
