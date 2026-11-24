/* Datos económicos del itinerario profesional en este navegador (DEC-012, D3 y opción C).

   Nunca se suben a la cuenta. La lógica está en career-finance.js (funciones puras); aquí solo se lee,
   guarda y borra la clave FINANCE_KEY. Cerrar sesión no la borra (LOCAL_ONLY_KEYS de local-owner.js),
   así que account.js pregunta aquí si hay algo para avisar de que se queda en el navegador. */

import { cleanFinance, FINANCE_KEY } from "./career-finance.js";
import { storage } from "../demo/demo-mode.js";

/** Documento económico guardado (vacío si no hay o si está dañado). */
export function loadFinance() {
  try {
    return cleanFinance(JSON.parse(storage.getItem(FINANCE_KEY)));
  } catch {
    return cleanFinance(null);
  }
}

export function saveFinance(doc) {
  try {
    storage.setItem(FINANCE_KEY, JSON.stringify(doc));
    return true;
  } catch {
    return false; // sin almacenamiento: dura hasta recargar
  }
}

/** ¿Hay datos económicos en este navegador? (objetivo o algún año) */
export function hasFinance() {
  const doc = loadFinance();
  return Boolean(doc.targets) || Object.keys(doc.years).length > 0;
}

/** Borra los datos económicos de este navegador. No hay copia en la cuenta: no se pueden recuperar. */
export function clearFinance() {
  try {
    storage.removeItem(FINANCE_KEY);
  } catch {
    // sin almacenamiento: no había nada guardado
  }
}
