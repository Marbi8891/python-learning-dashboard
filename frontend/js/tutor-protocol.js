/* Mensajes A2A 1.0 del Tutor Python (JSON-RPC), sin nada del DOM: se prueban con node --test.
   Formato del agente: la pregunta va como texto y, aparte, un objeto con la lección, el código y
   el error (solo los campos que el alumno rellena). Ver docs/a2a.md. */

export const TUTOR_PATH = "/a2a/python-tutor";
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
    `gradual`: el alumno prefiere la explicación paso a paso (un paso por respuesta). */
export function sendMessageRequest({ question, lessonSlug = "", code = "", error = "", gradual = false }, { contextId = null, id = 1 } = {}) {
  const data = Object.fromEntries(
    Object.entries({ lesson_slug: lessonSlug, code, error }).filter(([, value]) => value.trim() !== ""),
  );
  if (gradual) data.gradual = true;
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
};

/** Lee la respuesta JSON-RPC: estado de la tarea, texto que mostrar, conversación y metadatos. */
export function readTaskResult(response) {
  const failure = (label) => ({ state: "ERROR", label, text: "", contextId: null, ok: false, retry: true, meta: {} });
  if (response?.error) return failure("Error de comunicación con el tutor");
  const task = response?.result?.task;
  if (!task) return failure("Respuesta inesperada del tutor");
  const state = task.status?.state ?? "ERROR";
  const fromParts = (parts = []) => parts.filter((part) => typeof part.text === "string").map((part) => part.text).join("\n\n");
  const answer = fromParts(task.artifacts?.flatMap((artifact) => artifact.parts ?? []));
  const text = answer || fromParts(task.status?.message?.parts);
  const reason = REASONS[task.status?.message?.metadata?.reason];
  const ok = state === "TASK_STATE_COMPLETED";
  return {
    state,
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
    return `Respuesta generada por IA${where ? ` (${where})` : ""}. Puede equivocarse: compruébalo en la consola.`;
  }
  if (meta.source === "simulated") return "Tutor sin IA: respuesta preparada con reglas y contenido revisado del curso.";
  if (meta.source === "prepared") return "Respuesta preparada por el tutor, sin IA.";
  return "";
}
