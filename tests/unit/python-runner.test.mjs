// Botón «Detener» (PY-01): PythonRunner.stop() corta la ejecución en curso destruyendo el Worker.
// En Node no hay Web Workers: se sustituye por uno falso que se carga y nunca termina de ejecutar.
import assert from "node:assert/strict";
import { test } from "node:test";

const workers = [];
class FakeWorker {
  constructor() {
    this.terminated = false;
    this.messages = [];
    workers.push(this);
  }
  postMessage(message) {
    this.messages.push(message);
    if (message.type === "init" && FakeWorker.loads) queueMicrotask(() => this.onmessage({ data: { type: "ready" } }));
    // Los "run" no responden nunca: es un bucle infinito
  }
  terminate() {
    this.terminated = true;
  }
}
FakeWorker.loads = true;
globalThis.Worker = FakeWorker;

const { PythonRunner, StoppedError } = await import("../../frontend/js/python-runner.js");

const tick = () => new Promise((resolve) => setTimeout(resolve, 0));

test("sin nada en marcha, stop() no hace nada", () => {
  const runner = new PythonRunner({ indexURL: "x/" });
  assert.equal(runner.busy, false);
  assert.equal(runner.stop(), false);
});

test("stop() corta un bucle infinito, destruye el Worker y la siguiente ejecución crea otro", async () => {
  workers.length = 0;
  const statuses = [];
  const runner = new PythonRunner({ indexURL: "x/", timeoutMs: 60_000, onStatus: (s) => statuses.push(s) });
  const running = runner.run("while True: pass");
  await tick();
  assert.equal(runner.busy, true);
  assert.ok(workers[0].messages.some((m) => m.type === "run"));

  assert.equal(runner.stop(), true);
  await assert.rejects(running, StoppedError);
  assert.equal(workers[0].terminated, true);
  assert.equal(runner.busy, false);
  assert.equal(statuses.at(-1), "idle");

  runner.run("print(1)").catch(() => {});
  await tick();
  assert.equal(workers.length, 2, "la siguiente ejecución arranca un Worker nuevo");
  runner.stop();
});

test("también se puede detener mientras Pyodide se está cargando", async () => {
  workers.length = 0;
  FakeWorker.loads = false;
  try {
    const runner = new PythonRunner({ indexURL: "x/", timeoutMs: 60_000 });
    const running = runner.run("print(1)");
    await tick();
    assert.equal(runner.busy, true);
    assert.equal(runner.stop(), true);
    await assert.rejects(running, StoppedError);
    assert.equal(workers[0].terminated, true);
    assert.ok(!workers[0].messages.some((m) => m.type === "run"), "no llega a mandar el código");
  } finally {
    FakeWorker.loads = true;
  }
});
