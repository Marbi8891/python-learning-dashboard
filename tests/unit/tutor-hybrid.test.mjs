// Tutor híbrido: modalidad en la petición, estado de la IA avanzada y motivos de rechazo.
import assert from "node:assert/strict";
import { test } from "node:test";

import { advancedStatus, MODES_PATH, readTaskResult, REASONS, sendMessageRequest, sourceLabel, withRemaining } from "../../frontend/js/tutor-protocol.js";

const MODES = {
  default: "free",
  free: { available: true, provider: "mock", simulated: true },
  advanced: {
    available: true,
    provider: "openai",
    simulated: false,
    daily_limit: 10,
    used_today: 3,
    remaining: 7,
    global_available: true,
    max_input_chars: 6000,
    max_output_tokens: 600,
  },
};

test("la modalidad gratuita no añade nada a la petición (compatible con clientes anteriores)", () => {
  const free = sendMessageRequest({ question: "Hola", mode: "free" }).params.message;
  assert.deepEqual(free.parts, [{ text: "Hola" }]);
  const byDefault = sendMessageRequest({ question: "Hola" }).params.message;
  assert.deepEqual(byDefault.parts, [{ text: "Hola" }]);
});

test("la IA avanzada se pide con mode y la explicación alternativa con alternative", () => {
  const { message } = sendMessageRequest({ question: "Explícamelo de otra forma", mode: "advanced", alternative: true }).params;
  assert.deepEqual(message.parts[1], { data: { alternative: true, mode: "advanced" } });
  // Un valor desconocido no se envía: el cliente no puede inventarse modalidades
  const odd = sendMessageRequest({ question: "Hola", mode: "premium" }).params.message;
  assert.deepEqual(odd.parts, [{ text: "Hola" }]);
  assert.equal(MODES_PATH, "/api/v1/tutor/modes");
});

test("la IA avanzada solo se puede elegir si el servidor la ofrece y queda cuota", () => {
  assert.deepEqual(advancedStatus(MODES), { selectable: true, simulated: false, text: "Te quedan 7 de 10 consultas hoy." });
  for (const modes of [null, undefined, {}, { advanced: { available: false } }]) {
    const status = advancedStatus(modes);
    assert.equal(status.selectable, false);
    assert.match(status.text, /^No disponible/);
  }
  const spent = advancedStatus({ advanced: { ...MODES.advanced, remaining: 0 } });
  assert.equal(spent.selectable, false);
  assert.match(spent.text, /Has usado tus 10 consultas de hoy/);
  const global = advancedStatus({ advanced: { ...MODES.advanced, global_available: false } });
  assert.equal(global.selectable, false);
  assert.match(global.text, /límite de uso de hoy para todos/);
  const simulated = advancedStatus({ advanced: { ...MODES.advanced, simulated: true } });
  assert.match(simulated.text, /^Modo de pruebas: respuestas simuladas, sin IA real\./);
});

test("la cuota se actualiza con la que dice la respuesta, solo si es de IA avanzada", () => {
  const after = withRemaining(MODES, { mode: "advanced", quota_remaining: 6 });
  assert.equal(after.advanced.remaining, 6);
  assert.equal(after.advanced.used_today, 4);
  assert.equal(MODES.advanced.remaining, 7); // no modifica el original
  assert.equal(withRemaining(MODES, { mode: "free" }), MODES);
  assert.equal(withRemaining(MODES, { mode: "advanced" }), MODES);
  assert.equal(withRemaining(null, { mode: "advanced", quota_remaining: 1 }), null);
  assert.equal(withRemaining(MODES, { mode: "advanced", quota_remaining: -3 }).advanced.remaining, 0);
});

test("si no se concede la IA avanzada, se explica y se ofrece el modo gratuito", () => {
  for (const code of ["advanced_unavailable", "advanced_limit_reached", "advanced_global_limit", "advanced_input_too_long"]) {
    const response = {
      result: {
        task: {
          contextId: "c",
          status: { state: "TASK_STATE_REJECTED", message: { parts: [{ text: "Motivo y respuesta gratuita" }], metadata: { reason: code } } },
        },
      },
    };
    const result = readTaskResult(response);
    assert.equal(result.reason, code);
    assert.equal(result.retry, false); // reintentar en avanzada no cambiaría nada
    assert.equal(result.text, "Motivo y respuesta gratuita");
    assert.match(result.label, /modo gratuito/);
    assert.equal(REASONS[code].offerFree, true);
  }
  const unknown = readTaskResult({ result: { task: { status: { state: "TASK_STATE_REJECTED", message: { metadata: { reason: "x" } } } } } });
  assert.equal(unknown.reason, null);
});

test("las respuestas de IA avanzada lo dicen", () => {
  assert.equal(
    sourceLabel({ source: "model", provider: "openai", model: "modelo", mode: "advanced" }),
    "Respuesta generada por IA avanzada (openai · modelo). Puede equivocarse: compruébalo en la consola.",
  );
});
