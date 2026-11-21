/* Tutor IA: lógica sin DOM ni red (se prueba en tests/unit/ai-logic.test.mjs).

   El navegador solo envía la lección, la pregunta y, si el alumno lo pide, su código o su error.
   Nunca envía usuario, modelo, agente ni instrucciones: eso lo pone el servidor
   (docs/architecture/NEXARO_INTEGRATION_CONTRACT.md). */

export const AI_MODES = ["chat", "hint", "explain-error", "review-code"];

// Los mismos límites que valida el servidor (backend/app/schemas.py)
export const LIMITS = { question: 2000, code: 8000, error: 4000, turns: 6, turn: 2000 };
const DEFAULT_HINT_QUESTION = "Dame una pista del ejercicio";

export const STATUS_TEXT = {
  checking: "Comprobando el tutor IA…",
  available: "Tutor IA conectado.",
  unavailable: "El tutor IA no está disponible ahora mismo.",
  login: "Inicia sesión para preguntar al tutor IA.",
  error: "No se ha podido comprobar el tutor IA.",
};

/** Conversación de una lección: solo en memoria, se pierde al cambiar de lección o recargar. */
export function createConversation() {
  return { history: [], hintLevel: 0 };
}

const clip = (text, limit) => (typeof text === "string" ? text.slice(0, limit) : "");

/** Cuerpo de la petición de un modo, o `problem` con lo que falta para poder enviarla. */
export function buildRequest(mode, { lessonSlug, question = "", code = "", sendCode = false, error = "", locale = "es", conversation }) {
  const body = { lesson_slug: lessonSlug, locale: locale === "en" ? "en" : "es" };
  const asked = clip(question, LIMITS.question).trim();
  if (asked) body.question = asked;
  // Revisar código exige enviarlo: el botón lo dice. En los demás modos, solo si se marca la casilla
  const withCode = mode === "review-code" || sendCode;
  if (withCode && code.trim()) body.code = clip(code, LIMITS.code);

  if (mode === "chat") {
    if (!asked) return { problem: "Escribe tu pregunta." };
    body.history = conversation.history.slice(-LIMITS.turns);
  } else if (mode === "hint") {
    body.question = asked || DEFAULT_HINT_QUESTION;
    body.hint_level = Math.min(conversation.hintLevel + 1, 3);
  } else if (mode === "explain-error") {
    if (!error.trim()) return { problem: "Ejecuta tu código primero: no hay ningún error que explicar." };
    body.error = clip(error, LIMITS.error);
  } else if (mode === "review-code") {
    if (!body.code) return { problem: "Escribe tu código en la consola para que el tutor lo revise." };
  } else {
    return { problem: "Modo desconocido." };
  }
  return { body };
}

/** Recuerda la respuesta: turnos recientes del chat y nivel de la siguiente pista. */
export function remember(conversation, mode, question, answer) {
  if (mode === "chat") {
    conversation.history.push(
      { role: "user", content: clip(question.trim(), LIMITS.turn) },
      { role: "assistant", content: clip(answer, LIMITS.turn) },
    );
    conversation.history = conversation.history.slice(-LIMITS.turns);
  } else if (mode === "hint") {
    conversation.hintLevel = Math.min(conversation.hintLevel + 1, 3);
  }
}

/** Mensaje para el alumno a partir de un error de la API (sin detalles internos). */
export function errorText(error) {
  if (error?.name === "AbortError" || error?.name === "TimeoutError") {
    return "El tutor ha tardado demasiado. Vuelve a probar en un momento.";
  }
  switch (error?.status) {
    case 401:
      return STATUS_TEXT.login;
    case 404:
      return "El tutor IA no está disponible en este momento.";
    case 413:
    case 422:
      return "No se ha podido enviar: revisa que la pregunta o el código no sean demasiado largos.";
    case 0:
    case 429:
    case 503:
      // Mensajes genéricos de api.js o del servidor («El tutor está ocupado…»)
      return error.message;
    default:
      return "No se ha podido hablar con el tutor IA.";
  }
}
