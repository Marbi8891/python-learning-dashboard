/* Mensajes A2A 1.0 del Tutor Python (JSON-RPC), sin nada del DOM: se prueban con node --test.
   Formato del agente: la pregunta va como texto y, aparte, un objeto con la lección, el código y
   el error (solo los campos que el alumno rellena). Ver docs/a2a.md. */

export const TUTOR_PATH = "/a2a/python-tutor";
// Tutor híbrido: qué modalidades ofrece el servidor y la cuota que le queda al alumno
export const MODES_PATH = "/api/v1/tutor/modes";
export const A2A_VERSION = "1.0";

export const STATE_LABELS = {
  TASK_STATE_SUBMITTED: "Pregunta enviada",
  TASK_STATE_WORKING: "El tutor está pensando…",
  TASK_STATE_COMPLETED: "Respondida",
  TASK_STATE_REJECTED: "El tutor no ha atendido la pregunta (mira su mensaje)",
  TASK_STATE_FAILED: "El tutor no ha podido responder",
  TASK_STATE_CANCELED: "Consulta cancelada",
};

/** Cuerpo JSON-RPC de SendMessage. `contextId` mantiene la conversación entre preguntas.
    `gradual`: el alumno prefiere la explicación paso a paso (un paso por respuesta).
    `alternative`: pide otra forma de explicar el tema actual.
    `mode`: «advanced» pide la IA avanzada; el servidor decide si la concede. La gratuita no se
    envía: así la petición es la misma que la de los clientes anteriores (y la app Android). */
export function sendMessageRequest(
  { question, lessonSlug = "", code = "", error = "", gradual = false, alternative = false, mode = "free" },
  { contextId = null, id = 1 } = {},
) {
  const data = Object.fromEntries(
    Object.entries({ lesson_slug: lessonSlug, code, error }).filter(([, value]) => value.trim() !== ""),
  );
  if (gradual) data.gradual = true;
  if (alternative) data.alternative = true;
  if (mode === "advanced") data.mode = "advanced";
  const parts = [{ text: question.trim() }];
  if (Object.keys(data).length) parts.push({ data });
  const message = { messageId: crypto.randomUUID(), role: "ROLE_USER", parts };
  if (contextId) message.contextId = contextId;
  return { jsonrpc: "2.0", id, method: "SendMessage", params: { message } };
}

/* Motivo de un fallo (metadatos del mensaje de estado): qué ve el alumno y si tiene sentido
   reintentar. Nunca se reintenta solo: lo decide el alumno con el botón «Reintentar». */
export const REASONS = {
  provider_unavailable: { label: "El modelo de IA no está disponible ahora mismo", retry: true },
  provider_timeout: { label: "El modelo de IA ha tardado demasiado en responder", retry: true },
  provider_rate_limited: { label: "El servicio de IA ha llegado a su límite de uso por ahora", retry: false },
  limit_reached: { label: "Has llegado a tu límite de consultas al tutor por ahora", retry: false },
  invalid_input: { label: "El tutor no ha podido leer tu mensaje", retry: false },
  error: { label: "Error temporal del tutor", retry: true },
  // IA avanzada no concedida: el mensaje trae la respuesta gratuita y se ofrece seguir en ese modo
  advanced_unavailable: { label: "La IA avanzada no está disponible: te he respondido en modo gratuito", retry: false, offerFree: true },
  advanced_limit_reached: { label: "Has usado tus consultas de IA avanzada de hoy: te he respondido en modo gratuito", retry: false, offerFree: true },
  advanced_global_limit: { label: "La IA avanzada ha llegado a su límite de hoy: te he respondido en modo gratuito", retry: false, offerFree: true },
  advanced_input_too_long: { label: "Mensaje demasiado largo para la IA avanzada: te he respondido en modo gratuito", retry: false, offerFree: true },
};

/** Lee la respuesta JSON-RPC: estado de la tarea, texto que mostrar, conversación y metadatos. */
export function readTaskResult(response) {
  const failure = (label) => ({ state: "ERROR", reason: null, label, text: "", contextId: null, ok: false, retry: true, meta: {} });
  if (response?.error) return failure("Error de comunicación con el tutor");
  const task = response?.result?.task;
  if (!task) return failure("Respuesta inesperada del tutor");
  const state = task.status?.state ?? "ERROR";
  const fromParts = (parts = []) => parts.filter((part) => typeof part.text === "string").map((part) => part.text).join("\n\n");
  const answer = fromParts(task.artifacts?.flatMap((artifact) => artifact.parts ?? []));
  const text = answer || fromParts(task.status?.message?.parts);
  const code = task.status?.message?.metadata?.reason ?? null;
  const reason = REASONS[code];
  const ok = state === "TASK_STATE_COMPLETED";
  return {
    state,
    reason: reason ? code : null,
    label: reason?.label ?? STATE_LABELS[state] ?? "Estado desconocido",
    text,
    contextId: task.contextId ?? null,
    ok,
    retry: !ok && (reason ? reason.retry : state === "TASK_STATE_FAILED"),
    meta: task.artifacts?.[0]?.metadata ?? {},
  };
}

/** De dónde sale una respuesta, en palabras: nunca se presenta como IA lo que no lo es. */
export function sourceLabel(meta = {}) {
  if (meta.source === "model") {
    const where = [meta.provider, meta.model].filter(Boolean).join(" · ");
    const mode = meta.mode === "advanced" ? "IA avanzada" : "IA";
    return `Respuesta generada por ${mode}${where ? ` (${where})` : ""}. Puede equivocarse: compruébalo en la consola.`;
  }
  if (meta.source === "simulated") return "Tutor sin IA: respuesta preparada con reglas y contenido revisado del curso.";
  if (meta.source === "prepared") return "Respuesta preparada por el tutor, sin IA.";
  return "";
}

/** Estado de la IA avanzada para el selector, a partir de GET /api/v1/tutor/modes (o null si no
    se ha podido leer). `selectable`: se puede elegir ahora. Nunca la da por disponible si el
    servidor no lo dice. */
export function advancedStatus(modes) {
  const advanced = modes?.advanced;
  if (!advanced?.available) {
    return { selectable: false, simulated: false, text: "No disponible: este servidor no tiene activada la IA avanzada." };
  }
  const { remaining, daily_limit: limit, global_available: globalAvailable, simulated } = advanced;
  const test = simulated ? "Modo de pruebas: respuestas simuladas, sin IA real. " : "";
  if (globalAvailable === false) {
    return { selectable: false, simulated, text: `${test}Ha llegado a su límite de uso de hoy para todos los alumnos. Vuelve mañana.` };
  }
  if (!(remaining > 0)) {
    return { selectable: false, simulated, text: `${test}Has usado tus ${limit} consultas de hoy. Vuelve mañana o sigue en el modo gratuito.` };
  }
  return { selectable: true, simulated, text: `${test}Te quedan ${remaining} de ${limit} consultas hoy.` };
}

/** Actualiza la cuota con la que dice la última respuesta de IA avanzada. */
export function withRemaining(modes, meta = {}) {
  if (!modes?.advanced?.available || meta.mode !== "advanced" || typeof meta.quota_remaining !== "number") return modes;
  const remaining = Math.max(0, Math.trunc(meta.quota_remaining));
  return { ...modes, advanced: { ...modes.advanced, remaining, used_today: modes.advanced.daily_limit - remaining } };
}
