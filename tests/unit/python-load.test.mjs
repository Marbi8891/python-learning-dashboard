// Carga de Python con conexiones lentas: aviso de descarga, aviso de que sigue y límite de tiempo.
import assert from "node:assert/strict";
import { mock, test } from "node:test";

globalThis.window ??= {};
globalThis.document ??= { querySelector: () => null }; // console.js busca su indicador al cargar

/** Worker falso: guarda los mensajes y deja que el test responda cuando quiera. */
class FakeWorker {
  static last = null;
  constructor() {
    this.sent = [];
    this.terminated = false;
    FakeWorker.last = this;
  }
  postMessage(message) {
    this.sent.push(message);
  }
  terminate() {
    this.terminated = true;
  }
}
globalThis.Worker = FakeWorker;

const { PythonRunner, isPythonCached } = await import("../../frontend/js/python-runner.js");
const { statusText, isSlowConnection } = await import("../../frontend/js/console.js");

test("avisa de que sigue descargando y se rinde con un error reintentable", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    const statuses = [];
    const runner = new PythonRunner({ onStatus: (s) => statuses.push(s), slowLoadMs: 1000, loadTimeoutMs: 5000 });
    const run = runner.run("print(1)");
    await Promise.resolve();
    assert.deepEqual(statuses, ["loading"]);
    mock.timers.tick(1000);
    assert.deepEqual(statuses, ["loading", "slow-loading"]);
    mock.timers.tick(4000);
    await assert.rejects(run, /no ha terminado de descargarse/);
    assert.equal(statuses.at(-1), "error");
    assert.ok(FakeWorker.last.terminated, "el Worker se descarta para poder reintentar");
  } finally {
    mock.timers.reset();
  }
});

test("si Python carga a tiempo no hay aviso de lentitud", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    const statuses = [];
    const runner = new PythonRunner({ onStatus: (s) => statuses.push(s), slowLoadMs: 1000, loadTimeoutMs: 5000 });
    runner.run("print(1)").catch(() => {});
    FakeWorker.last.onmessage({ data: { type: "ready" } });
    await new Promise((resolve) => setImmediate(resolve));
    mock.timers.tick(5000);
    assert.deepEqual(statuses.slice(0, 2), ["loading", "ready"]);
    assert.ok(!statuses.includes("slow-loading"));
  } finally {
    mock.timers.reset();
  }
});

test("sin la API de cachés, Python cuenta como no descargado", async () => {
  assert.equal(await isPythonCached(), false);
});

test("el texto de estado anuncia la descarga solo cuando la habrá", () => {
  assert.match(statusText("loading", { cached: false, slow: false }), /Descargando Python \(unos 10 MB/);
  assert.equal(statusText("loading", { cached: true, slow: false }), "Cargando Python…");
  assert.match(statusText("slow-loading", { cached: false, slow: false }), /Sigue descargando/);
  assert.equal(statusText("ready", { cached: false, slow: true }), "Python 3 listo");
  // En reposo, el tamaño solo se avisa si la conexión es lenta o hay ahorro de datos
  assert.equal(statusText("idle", { cached: false, slow: false }), "Python se carga al ejecutar por primera vez");
  assert.match(statusText("idle", { cached: false, slow: true }), /unos 10 MB/);
  assert.equal(statusText("idle", { cached: true, slow: true }), "Python se carga al ejecutar por primera vez");
});

test("detecta el ahorro de datos y las redes 2G", () => {
  assert.equal(isSlowConnection(undefined), false);
  assert.equal(isSlowConnection({ saveData: true }), true);
  assert.equal(isSlowConnection({ effectiveType: "2g" }), true);
  assert.equal(isSlowConnection({ effectiveType: "slow-2g" }), true);
  assert.equal(isSlowConnection({ effectiveType: "4g", saveData: false }), false);
});

test("Detener durante la descarga cancela los avisos y no rompe la siguiente carga", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    const statuses = [];
    const runner = new PythonRunner({ onStatus: (s) => statuses.push(s), slowLoadMs: 1000, loadTimeoutMs: 5000 });
    const first = runner.run("print(1)");
    await Promise.resolve();
    assert.equal(runner.stop(), true);
    await assert.rejects(first, /detenido/);
    const firstWorker = FakeWorker.last;
    assert.ok(firstWorker.terminated);

    // Nueva ejecución: su carga no debe verse afectada por los temporizadores de la anterior
    const second = runner.run("print(2)");
    second.catch(() => {});
    await Promise.resolve();
    const secondWorker = FakeWorker.last;
    mock.timers.tick(999);
    secondWorker.onmessage({ data: { type: "ready" } });
    await new Promise((resolve) => setImmediate(resolve));
    mock.timers.tick(4_100); // pasa el límite de 5 s de la primera carga, no el de ejecución
    assert.ok(!secondWorker.terminated, "el Worker nuevo sigue vivo");
    assert.ok(!statuses.includes("slow-loading"));
    assert.ok(!statuses.includes("error"));
    runner.stop();
  } finally {
    mock.timers.reset();
  }
});
