/* Mensajes A2A 1.0 del Tutor Python (JSON-RPC), sin nada del DOM: se prueban con node --test.
   Formato del agente: la pregunta va como texto y, aparte, un objeto con la lección, el código y
   el error (solo los campos que el alumno rellena). Ver docs/a2a.md. */

export const TUTOR_PATH = "/a2a/python-tutor";
export const A2A_VERSION = "1.0";

export const STATE_LABELS = {
  TASK_STATE_SUBMITTED: "Pregunta enviada",
  TASK_STATE_WORKING: "El tutor está pensando…",
  TASK_STATE_COMPLETED: "Respondida",
  TASK_STATE_REJECTED: "El tutor no ha podido leer la pregunta",
  TASK_STATE_FAILED: "El tutor no ha podido responder",
  TASK_STATE_CANCELED: "Consulta cancelada",
};

/** Cuerpo JSON-RPC de SendMessage. `contextId` mantiene la conversación entre preguntas. */
export function sendMessageRequest({ question, lessonSlug = "", code = "", error = "" }, { contextId = null, id = 1 } = {}) {
  const data = Object.fromEntries(
    Object.entries({ lesson_slug: lessonSlug, code, error }).filter(([, value]) => value.trim() !== ""),
  );
  const parts = [{ text: question.trim() }];
  if (Object.keys(data).length) parts.push({ data });
  const message = { messageId: crypto.randomUUID(), role: "ROLE_USER", parts };
  if (contextId) message.contextId = contextId;
  return { jsonrpc: "2.0", id, method: "SendMessage", params: { message } };
}

/** Lee la respuesta JSON-RPC: estado de la tarea, texto que mostrar y conversación. */
export function readTaskResult(response) {
  if (response?.error) {
    return { state: "ERROR", label: "Error de comunicación con el tutor", text: "", contextId: null, ok: false };
  }
  const task = response?.result?.task;
  if (!task) return { state: "ERROR", label: "Respuesta inesperada del tutor", text: "", contextId: null, ok: false };
  const state = task.status?.state ?? "ERROR";
  const fromParts = (parts = []) => parts.filter((part) => typeof part.text === "string").map((part) => part.text).join("\n\n");
  const answer = fromParts(task.artifacts?.flatMap((artifact) => artifact.parts ?? []));
  const text = answer || fromParts(task.status?.message?.parts);
  return {
    state,
    label: STATE_LABELS[state] ?? "Estado desconocido",
    text,
    contextId: task.contextId ?? null,
    ok: state === "TASK_STATE_COMPLETED",
  };
}
