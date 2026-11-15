/* Hitos verificados (#109): simulacros del PCAP que elige, cronometra y corrige el servidor.

   El resto del progreso (lecciones, aciertos, simulacros locales, XP) lo calcula este navegador y
   es orientativo: se puede borrar o cambiar desde las herramientas del navegador. Lo verificado
   solo sale de la API, nunca de lo guardado en el navegador. */

import { apiEnabled, request } from "./api.js";
import { state } from "./store.js";

let summary = null; // { pass_mark, best_score, passed, exams: [...] } de la cuenta
let loading = null;

/** ¿Se puede hacer un simulacro verificado? Hace falta cuenta y servidor. */
export const canVerify = () => apiEnabled && Boolean(state.user);

/** Lo último que dijo el servidor, o null sin cuenta o sin respuesta todavía. */
export const verifiedSummary = () => (canVerify() ? summary : null);

/** Pide al servidor los simulacros verificados y avisa con `pld:verified` cuando llegan. */
export function refreshVerified() {
  if (!canVerify()) {
    summary = null;
    return Promise.resolve(null);
  }
  loading ??= request("GET", "/api/verified")
    .then((data) => {
      summary = data;
      window.dispatchEvent(new CustomEvent("pld:verified"));
      return data;
    })
    .catch(() => null)
    .finally(() => {
      loading = null;
    });
  return loading;
}

/** Empieza un simulacro en el servidor: devuelve { id, question_ids, deadline }. */
export const startVerifiedExam = () => request("POST", "/api/verified/pcap-exams");

/** Entrega las respuestas ({ idPregunta: [opciones] }) y devuelve la nota que pone el servidor. */
export async function submitVerifiedExam(id, answers) {
  const result = await request("POST", `/api/verified/pcap-exams/${id}/answers`, { json: { answers } });
  refreshVerified();
  return result;
}

/** Texto de una línea sobre lo verificado, para el panel y el certificado. */
export function verifiedLine() {
  const s = verifiedSummary();
  if (!canVerify()) return "Inicia sesión para que el servidor corrija tus simulacros y quede un aprobado verificado.";
  if (!s) return "Comprobando tus simulacros verificados…";
  if (!s.exams.length) return "Aún no tienes simulacros verificados por el servidor.";
  return s.passed
    ? `Simulacro aprobado y verificado por el servidor: mejor nota ${s.best_score} %.`
    : `Simulacros verificados por el servidor: mejor nota ${s.best_score} % (se aprueba con ${s.pass_mark} %).`;
}
