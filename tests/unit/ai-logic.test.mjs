import assert from "node:assert/strict";
import { test } from "node:test";
import { AI_MODES, buildRequest, createConversation, errorText, LIMITS, remember, STATUS_TEXT } from "../../frontend/js/ai/ai-logic.js";

const base = (changes = {}) => ({ lessonSlug: "variables", conversation: createConversation(), ...changes });

test("los modos son los cuatro del servidor", () => {
  assert.deepEqual(AI_MODES, ["chat", "hint", "explain-error", "review-code"]);
});

test("el cuerpo nunca lleva usuario, modelo, agente ni instrucciones", () => {
  for (const mode of AI_MODES) {
    const { body } = buildRequest(mode, base({ question: "¿Por qué?", code: "x = 1", sendCode: true, error: "NameError" }));
    for (const field of ["user_id", "model", "agent_id", "system", "temperature", "messages"]) {
      assert.equal(field in body, false, `${mode} no debe enviar ${field}`);
    }
    assert.equal(body.lesson_slug, "variables");
  }
});

test("chat: exige pregunta y envía el historial reciente", () => {
  assert.equal(buildRequest("chat", base({ question: "   " })).problem, "Escribe tu pregunta.");
  const conversation = createConversation();
  for (let i = 0; i < 5; i += 1) remember(conversation, "chat", `pregunta ${i}`, `respuesta ${i}`);
  const { body } = buildRequest("chat", base({ question: " ¿Y ahora? ", conversation }));
  assert.equal(body.question, "¿Y ahora?");
  assert.equal(body.history.length, LIMITS.turns);
  assert.deepEqual(body.history.at(-1), { role: "assistant", content: "respuesta 4" });
  assert.equal(body.history[0].role, "user", "el historial empieza por una pregunta");
});

test("el código solo viaja si se marca la casilla (o al pedir una revisión)", () => {
  const code = "precio = 2";
  assert.equal("code" in buildRequest("chat", base({ question: "¿Qué?", code })).body, false);
  assert.equal(buildRequest("chat", base({ question: "¿Qué?", code, sendCode: true })).body.code, code);
  assert.equal("code" in buildRequest("hint", base({ code })).body, false);
  assert.equal(buildRequest("review-code", base({ code })).body.code, code);
  assert.match(buildRequest("review-code", base({ code: "  \n" })).problem, /Escribe tu código/);
});

test("pista: pregunta por defecto y niveles de 1 a 3", () => {
  const conversation = createConversation();
  const levels = [];
  for (let i = 0; i < 4; i += 1) {
    levels.push(buildRequest("hint", base({ conversation })).body.hint_level);
    remember(conversation, "hint", "", "pista");
  }
  assert.deepEqual(levels, [1, 2, 3, 3]);
  assert.equal(buildRequest("hint", base()).body.question, "Dame una pista del ejercicio");
  assert.deepEqual(conversation.history, [], "las pistas no se añaden al historial del chat");
});

test("explicar un error exige haber ejecutado el código con error", () => {
  assert.match(buildRequest("explain-error", base()).problem, /Ejecuta tu código primero/);
  const { body } = buildRequest("explain-error", base({ error: "NameError: name 'x' is not defined" }));
  assert.equal(body.error, "NameError: name 'x' is not defined");
  assert.equal("question" in body, false, "la pregunta es optativa");
});

test("se recorta a los límites del servidor", () => {
  const long = "x".repeat(20_000);
  const { body } = buildRequest("explain-error", base({ question: long, code: long, sendCode: true, error: long }));
  assert.equal(body.question.length, LIMITS.question);
  assert.equal(body.code.length, LIMITS.code);
  assert.equal(body.error.length, LIMITS.error);
  const conversation = createConversation();
  remember(conversation, "chat", long, long);
  assert.ok(conversation.history.every((turn) => turn.content.length <= LIMITS.turn));
});

test("idioma: solo español o inglés", () => {
  assert.equal(buildRequest("hint", base({ locale: "en" })).body.locale, "en");
  assert.equal(buildRequest("hint", base({ locale: "fr" })).body.locale, "es");
});

test("modo desconocido", () => {
  assert.equal(buildRequest("borrar", base()).problem, "Modo desconocido.");
});

test("mensajes de error sin detalles internos", () => {
  assert.equal(errorText({ status: 401 }), STATUS_TEXT.login);
  assert.match(errorText({ status: 404 }), /no está disponible/);
  assert.match(errorText({ status: 422 }), /demasiado largos/);
  assert.match(errorText({ status: 413 }), /demasiado largos/);
  assert.equal(errorText({ status: 429, message: "El tutor está ocupado." }), "El tutor está ocupado.");
  assert.equal(errorText({ status: 503, message: "El tutor no responde." }), "El tutor no responde.");
  assert.equal(errorText({ status: 0, message: "Sin conexión." }), "Sin conexión.");
  assert.match(errorText({ name: "TimeoutError" }), /tardado demasiado/);
  assert.match(errorText({ name: "AbortError" }), /tardado demasiado/);
  assert.equal(errorText({ status: 500, message: "Traceback secreto" }), "No se ha podido hablar con el tutor IA.");
  assert.equal(errorText(undefined), "No se ha podido hablar con el tutor IA.");
});
