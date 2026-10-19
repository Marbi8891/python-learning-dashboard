import assert from "node:assert/strict";
import { test } from "node:test";

import { A2A_VERSION, readTaskResult, sendMessageRequest, sourceLabel } from "../../frontend/js/tutor-protocol.js";

test("la petición lleva la pregunta como texto y solo los datos rellenados", () => {
  const body = sendMessageRequest({ question: "  ¿Por qué falla?  ", lessonSlug: "variables", code: "x = ", error: " " });
  assert.equal(body.jsonrpc, "2.0");
  assert.equal(body.method, "SendMessage");
  const { message } = body.params;
  assert.equal(message.role, "ROLE_USER");
  assert.ok(message.messageId);
  assert.deepEqual(message.parts, [{ text: "¿Por qué falla?" }, { data: { lesson_slug: "variables", code: "x = " } }]);
  assert.equal(message.contextId, undefined);
  assert.equal(A2A_VERSION, "1.0");
});

test("sin datos extra solo va el texto; la conversación sigue con su contextId", () => {
  const { message } = sendMessageRequest({ question: "Hola" }, { contextId: "ctx-1" }).params;
  assert.deepEqual(message.parts, [{ text: "Hola" }]);
  assert.equal(message.contextId, "ctx-1");
});

test("una tarea completada devuelve el texto del artefacto", () => {
  const response = {
    result: {
      task: {
        contextId: "ctx-1",
        status: { state: "TASK_STATE_COMPLETED" },
        artifacts: [{ parts: [{ text: "Explicación" }] }],
      },
    },
  };
  assert.deepEqual(readTaskResult(response), {
    state: "TASK_STATE_COMPLETED",
    label: "Respondida",
    text: "Explicación",
    contextId: "ctx-1",
    ok: true,
    retry: false,
    meta: {},
  });
});

test("la preferencia «paso a paso» viaja como dato", () => {
  const { message } = sendMessageRequest({ question: "Hola", gradual: true }).params;
  assert.deepEqual(message.parts, [{ text: "Hola" }, { data: { gradual: true } }]);
});

test("los metadatos dicen de dónde sale la respuesta y nunca la presentan como IA si no lo es", () => {
  const meta = { source: "simulated", provider: "mock", model: "mock", expects_answer: true };
  const response = { result: { task: { status: { state: "TASK_STATE_COMPLETED" }, artifacts: [{ parts: [{ text: "x" }], metadata: meta }] } } };
  assert.deepEqual(readTaskResult(response).meta, meta);
  assert.match(sourceLabel(meta), /^Tutor sin IA/);
  assert.doesNotMatch(sourceLabel(meta), /generada por IA/);
  assert.equal(sourceLabel({ source: "prepared" }), "Respuesta preparada por el tutor, sin IA.");
  assert.equal(
    sourceLabel({ source: "model", provider: "ollama", model: "qwen2.5-coder:7b" }),
    "Respuesta generada por IA (ollama · qwen2.5-coder:7b). Puede equivocarse: compruébalo en la consola.",
  );
  assert.equal(sourceLabel({ source: "model" }), "Respuesta generada por IA. Puede equivocarse: compruébalo en la consola.");
  assert.equal(sourceLabel(), "");
});

test("cada fallo explica su motivo y solo algunos se pueden reintentar (a mano)", () => {
  const failed = (state, reason) => ({
    result: { task: { status: { state, message: { parts: [{ text: "t" }], metadata: reason ? { reason } : {} } } } },
  });
  const down = readTaskResult(failed("TASK_STATE_FAILED", "provider_unavailable"));
  assert.equal(down.label, "El modelo de IA no está disponible ahora mismo");
  assert.equal(down.retry, true);
  assert.equal(readTaskResult(failed("TASK_STATE_FAILED", "provider_rate_limited")).retry, false);
  assert.equal(readTaskResult(failed("TASK_STATE_REJECTED", "limit_reached")).retry, false);
  assert.equal(readTaskResult(failed("TASK_STATE_FAILED")).retry, true); // servidor antiguo, sin motivo
  assert.equal(readTaskResult(failed("TASK_STATE_REJECTED")).retry, false);
  assert.equal(readTaskResult({ error: { code: 1 } }).retry, true);
});

test("una tarea rechazada muestra el mensaje del estado", () => {
  const response = {
    result: { task: { contextId: "c", status: { state: "TASK_STATE_REJECTED", message: { parts: [{ text: "No he podido leer" }] } } } },
  };
  const result = readTaskResult(response);
  assert.equal(result.ok, false);
  assert.equal(result.text, "No he podido leer");
  assert.equal(result.label, "El tutor no ha atendido la pregunta (mira su mensaje)");
});

test("los errores JSON-RPC y las respuestas raras no rompen la vista", () => {
  assert.equal(readTaskResult({ error: { code: -32009, message: "x" } }).state, "ERROR");
  assert.equal(readTaskResult({}).ok, false);
  assert.equal(readTaskResult(null).ok, false);
  assert.equal(readTaskResult({ result: { task: { status: { state: "RARO" } } } }).label, "Estado desconocido");
});
