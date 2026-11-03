// Subida con estado y reintentos (SYNC-01 y SYNC-04): nada pasa a «guardado» sin que el servidor
// lo confirme, un fallo se reintenta y cerrar sesión sabe qué falta por subir.
import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";
import { createUploader } from "../../frontend/js/uploader.js";
import { failedStores, resetSyncStatus, unsavedStores } from "../../frontend/js/sync-status.js";

function fakeClock() {
  const timers = [];
  return {
    schedule: (fn, ms) => {
      const timer = { fn, ms, cancelled: false };
      timers.push(timer);
      return timer;
    },
    cancel: (timer) => {
      timer.cancelled = true;
    },
    async fireNext() {
      const timer = timers.find((t) => !t.cancelled && !t.fired);
      timer.fired = true;
      await timer.fn();
    },
    pending: () => timers.filter((t) => !t.cancelled && !t.fired),
  };
}

/** `responses`: lo que hace el servidor en cada subida ("ok", "503", "401" o una función). */
function setup({ ready = true, gateSync = async () => false, responses = [] } = {}) {
  const clock = fakeClock();
  const gate = { ready, sync: gateSync };
  const calls = { push: 0 };
  const queue = [...responses];
  const uploader = createUploader({
    name: "pcap",
    label: "la preparación del PCAP",
    gate,
    push: async () => {
      calls.push += 1;
      const next = queue.shift() ?? "ok";
      if (typeof next === "function") return next();
      if (next === "ok") return true;
      const error = new Error(`HTTP ${next}`);
      error.status = Number(next);
      throw error;
    },
    delayMs: 5,
    retryDelays: [10, 20],
    schedule: clock.schedule,
    cancel: clock.cancel,
  });
  return { clock, gate, calls, uploader };
}

beforeEach(() => {
  resetSyncStatus();
  console.warn = () => {}; // los avisos de fallo son esperados aquí
});

test("un cambio queda pendiente hasta que el servidor lo confirma", async () => {
  const { clock, calls, uploader } = setup();
  uploader.changed();
  assert.deepEqual(unsavedStores(), ["la preparación del PCAP"]);
  await clock.fireNext();
  assert.equal(calls.push, 1);
  assert.equal(uploader.state, "saved");
  assert.deepEqual(unsavedStores(), []);
});

test("si la subida falla queda «con fallo» y se reintenta con espera (SYNC-04)", async () => {
  const { clock, calls, uploader } = setup({ responses: ["503", "503", "ok"] });
  uploader.changed();
  await clock.fireNext();
  assert.equal(uploader.state, "failed");
  assert.deepEqual(failedStores(), ["la preparación del PCAP"]);
  assert.equal(clock.pending()[0].ms, 10);
  await clock.fireNext();
  assert.equal(clock.pending()[0].ms, 20);
  await clock.fireNext();
  assert.equal(calls.push, 3);
  assert.equal(uploader.state, "saved");
  assert.deepEqual(failedStores(), []);
});

test("los reintentos automáticos se acaban; lo pendiente sigue marcado", async () => {
  const { clock, uploader } = setup({ responses: ["503", "503", "503"] });
  uploader.changed();
  await clock.fireNext();
  await clock.fireNext();
  await clock.fireNext();
  assert.equal(clock.pending().length, 0);
  assert.equal(uploader.state, "failed");
});

test("con la sesión caducada (401) no se reintenta", async () => {
  const { clock, uploader } = setup({ responses: ["401"] });
  uploader.changed();
  await clock.fireNext();
  assert.equal(uploader.state, "failed");
  assert.equal(clock.pending().length, 0);
});

test("un cambio hecho mientras se subía sigue pendiente aunque la subida salga bien", async () => {
  let uploader;
  const ctx = setup({
    responses: [
      () => {
        uploader.changed(); // el alumno responde otra pregunta mientras viaja la petición
        return true;
      },
    ],
  });
  uploader = ctx.uploader;
  uploader.changed();
  await ctx.clock.fireNext();
  assert.equal(uploader.state, "pending");
  await ctx.clock.fireNext();
  assert.equal(uploader.state, "saved");
});

test("flush sube ya lo pendiente y dice si quedó guardado (SYNC-01)", async () => {
  const ok = setup();
  ok.uploader.changed();
  assert.equal(await ok.uploader.flush(), true);
  assert.equal(ok.calls.push, 1);

  resetSyncStatus();
  const failing = setup({ responses: ["503"] });
  failing.uploader.changed();
  assert.equal(await failing.uploader.flush(), false);
  assert.deepEqual(unsavedStores(), ["la preparación del PCAP"]);
});

test("al iniciar sesión lo local está pendiente; si la fusión inicial no sale, flush devuelve false", async () => {
  const { calls, uploader } = setup({ ready: false, gateSync: async () => false });
  uploader.sessionStarted();
  assert.equal(await uploader.flush(), false);
  assert.equal(calls.push, 0, "sin fusionar no se sube nada (AUD-001)");
  assert.deepEqual(unsavedStores(), ["la preparación del PCAP"]);
});

test("si la fusión inicial sale bien al cerrar sesión, flush sube el resultado", async () => {
  let ctx;
  ctx = setup({
    ready: false,
    gateSync: async () => {
      ctx.gate.ready = true;
      ctx.uploader.changed(); // onSynced de la puerta
      return true;
    },
  });
  ctx.uploader.sessionStarted();
  assert.equal(await ctx.uploader.flush(), true);
  assert.equal(ctx.calls.push, 1);
  assert.equal(ctx.clock.pending().length, 0, "no queda otra subida programada");
});

test("sin cambios no se sube nada al cerrar sesión", async () => {
  const { calls, uploader } = setup();
  assert.equal(await uploader.flush(), true);
  assert.equal(calls.push, 0);
});

test("al terminar la sesión no queda nada pendiente ni programado", async () => {
  const { clock, uploader } = setup({ responses: ["503"] });
  uploader.changed();
  await clock.fireNext();
  uploader.sessionEnded();
  assert.equal(uploader.state, "saved");
  assert.equal(clock.pending().length, 0);
});
