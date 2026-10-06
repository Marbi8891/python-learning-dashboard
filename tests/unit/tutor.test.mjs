import assert from "node:assert/strict";
import { test } from "node:test";

import { A2A_VERSION, readTaskResult, sendMessageRequest } from "../../frontend/js/tutor-protocol.js";

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
  });
});

test("una tarea rechazada muestra el mensaje del estado", () => {
  const response = {
    result: { task: { contextId: "c", status: { state: "TASK_STATE_REJECTED", message: { parts: [{ text: "No he podido leer" }] } } } },
  };
  const result = readTaskResult(response);
  assert.equal(result.ok, false);
  assert.equal(result.text, "No he podido leer");
  assert.equal(result.label, "El tutor no ha podido leer la pregunta");
});

test("los errores JSON-RPC y las respuestas raras no rompen la vista", () => {
  assert.equal(readTaskResult({ error: { code: -32009, message: "x" } }).state, "ERROR");
  assert.equal(readTaskResult({}).ok, false);
  assert.equal(readTaskResult(null).ok, false);
  assert.equal(readTaskResult({ result: { task: { status: { state: "RARO" } } } }).label, "Estado desconocido");
});
