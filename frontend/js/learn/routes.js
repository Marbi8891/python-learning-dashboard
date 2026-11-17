/* Rutas del núcleo educativo (Aprender, Teoría, Practicar, Progreso, sesiones y Preparación DAW).
   Van aparte de learn-app.js para que el enrutador (app.js) sepa a qué zona va una ruta sin
   descargar la zona entera (carga diferida, AUD-024). */

export const LEARN_ROUTES = ["#/bienvenida", "#/aprender", "#/teoria", "#/poo", "#/practicar", "#/progreso", "#/sesion"];

/** ¿La ruta es del núcleo educativo? `#/daw` es la Preparación DAW; `#/daw/<curso>` sigue en daw.js. */
export const isLearnRoute = (hash) => hash === "#/daw" || LEARN_ROUTES.some((r) => hash === r || hash.startsWith(`${r}/`));

/** Clave del menú principal para una ruta del núcleo. */
export function learnNavKey(hash) {
  if (hash.startsWith("#/bienvenida")) return "bienvenida"; // ninguna entrada del menú
  if (hash.startsWith("#/teoria") || hash.startsWith("#/poo")) return "teoria";
  if (hash.startsWith("#/practicar")) return "practicar";
  if (hash.startsWith("#/progreso")) return "progreso";
  if (hash.startsWith("#/daw")) return "daw";
  return "aprender";
}
