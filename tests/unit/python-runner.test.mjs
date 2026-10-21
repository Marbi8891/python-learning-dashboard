import assert from "node:assert/strict";
import { test } from "node:test";
import { PythonRunner, StoppedError, TimeoutError } from "../../frontend/js/python-runner.js";

/** Worker falso: responde «ready» al iniciarse y deja las ejecuciones sin terminar (como un bucle infinito). */
class FakeWorker {
  static created = [];
  constructor() {
    this.terminated = false;
    this.messages = [];
    FakeWorker.created.push(this);
  }
  postMessage(message) {
    this.messages.push(message);
    if (message.type === "init") queueMicrotask(() => this.onmessage({ data: { type: "ready" } }));
  }
  terminate() {
    this.terminated = true;
  }
}
globalThis.Worker = FakeWorker;

const lastWorker = () => FakeWorker.created.at(-1);
const tick = () => new Promise((resolve) => setTimeout(resolve, 0));

test("Detener corta la ejecución, destruye el Worker y la siguiente vuelve a crearlo", async () => {
  const statuses = [];
  const runner = new PythonRunner({ timeoutMs: 60_000, onStatus: (s) => statuses.push(s) });
  assert.equal(runner.stop(), false, "sin nada en marcha no hay nada que detener");

  const running = runner.run("while True:\n    pass");
  await tick();
  const first = lastWorker();
  assert.equal(runner.busy, true);
  assert.equal(runner.stop(), true);
  await assert.rejects(running, StoppedError);
  assert.equal(first.terminated, true);
  assert.equal(runner.busy, false);
  assert.equal(statuses.at(-1), "idle");

  const again = runner.run("print('sigo vivo')");
  await tick();
  const second = lastWorker();
  assert.notEqual(second, first, "Python empieza limpio");
  const { id } = second.messages.find((m) => m.type === "run");
  second.onmessage({ data: { id, result: { output: "sigo vivo\n" } } });
  assert.deepEqual(await again, { output: "sigo vivo\n" });
});

test("el límite de tiempo sigue siendo un error distinto de detener", async () => {
  const runner = new PythonRunner({ timeoutMs: 20 });
  await assert.rejects(runner.run("while True:\n    pass"), (error) => error instanceof TimeoutError && !(error instanceof StoppedError));
  assert.equal(lastWorker().terminated, true);
  assert.equal(runner.busy, false);
});
