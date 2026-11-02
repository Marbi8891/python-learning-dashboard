// Puerta de sincronización (AUD-001): no se sube nada a la cuenta hasta fusionar bien su copia.
import assert from "node:assert/strict";
import { test } from "node:test";
import { createSyncGate } from "../../frontend/js/sync-gate.js";

/** Planificador manual: guarda los temporizadores y los lanza cuando lo pide el test. */
function fakeClock() {
  const timers = [];
  return {
    timers,
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

function setup({ failures = 0, user = true } = {}) {
  const session = { user };
  const calls = { load: 0, merge: 0, synced: 0 };
  const clock = fakeClock();
  let left = failures;
  const gate = createSyncGate({
    name: "prueba",
    active: () => session.user,
    load: async () => {
      calls.load += 1;
      if (left > 0) {
        left -= 1;
        throw new Error("503");
      }
      return { data: {} };
    },
    merge: () => {
      calls.merge += 1;
    },
    onSynced: () => {
      calls.synced += 1;
    },
    delays: [10, 20],
    schedule: clock.schedule,
    cancel: clock.cancel,
  });
  return { gate, calls, clock, session };
}

const quiet = (fn) => async () => {
  const warn = console.warn;
  console.warn = () => {};
  try {
    await fn();
  } finally {
    console.warn = warn;
  }
};

test("cerrada hasta que la fusión inicial sale bien; entonces sube una vez", async () => {
  const { gate, calls } = setup();
  assert.equal(gate.ready, false);
  await gate.restart();
  assert.equal(gate.ready, true);
  assert.deepEqual(calls, { load: 1, merge: 1, synced: 1 });
});

test(
  "si la fusión falla sigue cerrada (no se sube nada) y reintenta con espera",
  quiet(async () => {
    const { gate, calls, clock } = setup({ failures: 2 });
    await gate.restart();
    assert.equal(gate.ready, false);
    assert.equal(calls.synced, 0, "con la fusión fallida no se puede subir el documento local");
    assert.equal(clock.pending()[0].ms, 10);
    await clock.fireNext();
    assert.equal(gate.ready, false);
    assert.equal(clock.pending()[0].ms, 20);
    await clock.fireNext();
    assert.equal(gate.ready, true);
    assert.deepEqual(calls, { load: 3, merge: 1, synced: 1 });
  }),
);

test(
  "deja de reintentar al agotar las esperas, pero sync() lo vuelve a intentar",
  quiet(async () => {
    const { gate, calls, clock } = setup({ failures: 3 });
    await gate.restart();
    await clock.fireNext();
    await clock.fireNext();
    assert.equal(clock.pending().length, 0);
    assert.equal(gate.ready, false);
    assert.equal(await gate.sync(), true); // p. ej. al cerrar sesión
    assert.deepEqual(calls, { load: 4, merge: 1, synced: 1 });
  }),
);

test("sin sesión no fusiona ni sube", async () => {
  const { gate, calls } = setup({ user: false });
  await gate.restart();
  assert.equal(await gate.sync(), false);
  assert.deepEqual(calls, { load: 0, merge: 0, synced: 0 });
});

test(
  "cerrar sesión cierra la puerta y cancela los reintentos",
  quiet(async () => {
    const { gate, clock, session } = setup({ failures: 1 });
    await gate.restart();
    assert.equal(clock.pending().length, 1);
    session.user = false;
    await gate.restart();
    assert.equal(clock.pending().length, 0);
    assert.equal(gate.ready, false);
  }),
);

test("una fusión que termina después de cerrar sesión no abre la puerta", async () => {
  const session = { user: true };
  let release;
  let synced = 0;
  const gate = createSyncGate({
    name: "prueba",
    active: () => session.user,
    load: () => new Promise((resolve) => (release = resolve)),
    merge: () => {},
    onSynced: () => {
      synced += 1;
    },
  });
  const first = gate.restart();
  session.user = false;
  await gate.restart();
  release();
  await first;
  assert.equal(gate.ready, false);
  assert.equal(synced, 0);
});

test("dos sync() a la vez hacen una sola fusión", async () => {
  const { gate, calls } = setup();
  await Promise.all([gate.sync(), gate.sync()]);
  assert.deepEqual(calls, { load: 1, merge: 1, synced: 1 });
});

test("la copia leída de una sesión que ya cambió no se fusiona con los datos locales", async () => {
  // Usuario A empieza a leer; cierra sesión y entra B antes de que llegue la respuesta de A.
  const session = { user: "A" };
  const local = [];
  const pending = [];
  const gate = createSyncGate({
    name: "prueba",
    active: () => Boolean(session.user),
    load: () => new Promise((resolve) => pending.push({ user: session.user, resolve })),
    merge: (remote) => local.push(remote),
    onSynced: () => {},
  });
  const first = gate.restart();
  session.user = "B";
  const second = gate.restart();
  pending[0].resolve("cuenta de A"); // llega tarde
  await first;
  assert.deepEqual(local, [], "la copia de A no debe tocar los datos locales de B");
  pending[1].resolve("cuenta de B");
  await second;
  assert.deepEqual(local, ["cuenta de B"]);
  assert.equal(gate.ready, true);
});

test(
  "un fallo al fusionar deja la puerta cerrada",
  quiet(async () => {
    const gate = createSyncGate({
      name: "prueba",
      active: () => true,
      load: async () => ({ data: "corrupto" }),
      merge: () => {
        throw new Error("formato inesperado");
      },
      onSynced: () => assert.fail("no debe subir"),
      delays: [],
    });
    await gate.restart();
    assert.equal(gate.ready, false);
  }),
);
