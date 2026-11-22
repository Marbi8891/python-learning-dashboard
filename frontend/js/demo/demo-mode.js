/* Modo demostración (docs/DEMO-ARCHITECTURE.md).

   Se entra con «?demo=1» en la dirección (botón «Probar la demo» de la portada). Desde ese momento,
   en esta pestaña:
   - todos los almacenes guardan en sessionStorage con el prefijo «pld-demo:» (`storage`), así que el
     progreso real del navegador (pld:* en localStorage) no se lee ni se escribe;
   - api.js no llama al servidor (ni sesiones, ni subidas, ni tutor IA).
   Cerrar la pestaña o «Salir de la demo» lo borra todo.

   Este módulo lo importan los almacenes: su `await` hace que lean ya los datos de Alex al cargarse.
   Fuera de la demo no descarga nada y `storage` es el localStorage de siempre. */

import { DEMO_FLAG, DEMO_PREFIX, PrefixedStorage, demoProfile, seedEntries } from "./demo-data.js";

const DATA_URL = "data/demo/alex.json";
const SEEDED = "seeded"; // clave (con prefijo) que dice que esta pestaña ya tiene a Alex

const inBrowser = typeof window !== "undefined" && typeof location !== "undefined";
let fixture = null;

function session() {
  try {
    return window.sessionStorage;
  } catch {
    return null; // almacenamiento bloqueado: sin demo
  }
}

async function loadFixture() {
  const response = await fetch(DATA_URL);
  if (!response.ok) throw new Error(`No se pudieron cargar los datos de la demo (HTTP ${response.status})`);
  return response.json();
}

function seed(store, data) {
  store.clear();
  for (const [key, value] of seedEntries(data)) store.setItem(key, value);
  store.setItem(SEEDED, "1");
  store.setItem(DEMO_FLAG.slice(DEMO_PREFIX.length), "1"); // clear() también borra la marca
}

async function start() {
  if (!inBrowser) return false;
  const backing = session();
  if (!backing) return false;
  const params = new URLSearchParams(location.search);
  const entering = params.get("demo") === "1";
  if (params.has("demo")) {
    params.delete("demo");
    const query = params.toString();
    history.replaceState(history.state, "", `${location.pathname}${query ? `?${query}` : ""}${location.hash}`);
  }
  if (!entering && backing.getItem(DEMO_FLAG) !== "1") return false;
  const store = new PrefixedStorage(backing, DEMO_PREFIX);
  try {
    fixture = await loadFixture();
    if (entering || store.getItem(SEEDED) !== "1") seed(store, fixture);
    backing.setItem(DEMO_FLAG, "1");
    return true;
  } catch (error) {
    console.warn("No se pudo abrir la demo:", error.message);
    store.clear();
    backing.removeItem(DEMO_FLAG);
    return false;
  }
}

/** ¿Está esta pestaña en modo demo? Se decide una vez, al cargar. */
export const isDemo = await start();

/** Almacén de los datos del alumno: localStorage normalmente; sessionStorage aparte en la demo. */
export const storage = isDemo ? new PrefixedStorage(session(), DEMO_PREFIX) : inBrowser ? safeLocalStorage() : undefined;

function safeLocalStorage() {
  try {
    return window.localStorage;
  } catch {
    return undefined; // los almacenes ya tratan el fallo de cada lectura y escritura
  }
}

/** Perfil ficticio y actividad de Alex (con fechas de hoy), o null fuera de la demo. */
export function demoData() {
  return isDemo && fixture ? demoProfile(fixture) : null;
}

/** Vuelve a dejar los datos de Alex como al entrar. */
export function resetDemo() {
  if (!isDemo) return;
  seed(storage, fixture);
  location.reload();
}

/** Sale de la demo: borra todo lo de la demo y vuelve a la portada en modo normal. */
export function exitDemo() {
  const backing = session();
  if (backing) {
    new PrefixedStorage(backing, DEMO_PREFIX).clear();
    backing.removeItem(DEMO_FLAG);
  }
  // Solo cambia el «#»: sin recargar, los almacenes seguirían con los datos de Alex en memoria
  history.replaceState(null, "", `${location.pathname}#/portada`);
  location.reload();
}

/** Dirección que abre la demo desde cualquier página. */
export const DEMO_ENTRY = "?demo=1#/panel";
