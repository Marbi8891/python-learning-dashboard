// Control de versiones al subir el progreso: dos pestañas no se pisan.
import assert from "node:assert/strict";
import { test } from "node:test";
import { createDocSync, MAX_CONFLICT_RETRIES } from "../../frontend/js/doc-sync.js";

class Conflict extends Error {
  status = 409;
}

class PreconditionRequired extends Error {
  status = 428;
}

/** Servidor falso con las mismas reglas que el backend: PUT con versión vieja → 409; sin versión,
    solo crea (versión 0): si el documento ya existe → 428 (PLD-003). */
function fakeServer(initial = { data: {}, version: 0 }) {
  const server = { doc: structuredClone(initial), calls: [] };
  server.request = async (method, path, options) => {
    server.calls.push(method);
    if (method === "GET") return structuredClone(server.doc);
    const { data, version } = options.json;
    if (version === null && server.doc.version > 0) throw new PreconditionRequired("428");
    if (version !== null && version !== server.doc.version) throw new Conflict("409");
    server.doc = { data: structuredClone(data), version: server.doc.version + 1 };
    return structuredClone(server.doc);
  };
  return server;
}

/** Una pestaña: su copia local (conjunto de respuestas) y su sincronización. */
function tab(server, { valid = () => true } = {}) {
  const local = { answers: [] };
  const merge = (remote) => {
    local.answers = [...new Set([...local.answers, ...(remote.data.answers ?? [])])].sort();
  };
  const sync = createDocSync({ path: "/api/pcap-state", request: (...args) => server.request(...args), data: () => local, merge, valid });
  return { local, sync, merge };
}

test("sube con la versión leída y adopta la nueva", async () => {
  const server = fakeServer();
  const a = tab(server);
  a.sync.adopt(await server.request("GET"));
  a.local.answers.push("q1");
  assert.equal(await a.sync.push(), true);
  assert.equal(a.sync.version, 1);
  assert.deepEqual(server.doc.data.answers, ["q1"]);
});

test("dos pestañas: la segunda recibe 409, fusiona y no borra lo de la primera", async () => {
  const server = fakeServer();
  const a = tab(server);
  const b = tab(server);
  a.sync.adopt(await server.request("GET"));
  b.sync.adopt(await server.request("GET"));
  a.local.answers.push("de-A");
  b.local.answers.push("de-B");
  await a.sync.push();
  assert.equal(await b.sync.push(), true);
  assert.deepEqual(server.doc.data.answers, ["de-A", "de-B"], "la cuenta conserva lo de las dos");
  assert.deepEqual(b.local.answers, ["de-A", "de-B"]);
  assert.equal(b.sync.version, 2);
  assert.deepEqual(server.calls, ["GET", "GET", "PUT", "PUT", "GET", "PUT"]);
});

test("si la sesión cambia mientras se resuelve el conflicto, no fusiona ni sube", async () => {
  const server = fakeServer({ data: { answers: ["otra-cuenta"] }, version: 5 });
  let alive = true;
  const b = tab(server, { valid: () => alive });
  b.sync.adopt({ version: 4 });
  const original = server.request;
  server.request = async (method, ...rest) => {
    if (method === "GET") alive = false; // se cierra sesión justo al releer
    return original(method, ...rest);
  };
  b.local.answers.push("mia");
  assert.equal(await b.sync.push(), false);
  assert.deepEqual(b.local.answers, ["mia"], "no mezcla la copia leída tras el cambio de sesión");
  assert.deepEqual(server.doc.data.answers, ["otra-cuenta"]);
});

test("tras varios conflictos seguidos se rinde y lanza el error (no hay bucle infinito)", async () => {
  const server = fakeServer();
  const a = tab(server);
  a.sync.adopt({ version: 0 });
  server.request = async (method) => {
    if (method === "GET") return { data: {}, version: 99 };
    throw new Conflict("409");
  };
  await assert.rejects(a.sync.push(), (error) => error.status === 409);
  assert.ok(MAX_CONFLICT_RETRIES >= 1);
});

test("otros errores (503, sin red) se lanzan sin releer", async () => {
  const server = fakeServer();
  const a = tab(server);
  a.sync.adopt({ version: 0 }); // ya leyó la cuenta: el 503 es del PUT
  let gets = 0;
  server.request = async (method) => {
    if (method === "GET") gets += 1;
    const error = new Error("Servidor despertando");
    error.status = 503;
    throw error;
  };
  await assert.rejects(a.sync.push(), (error) => error.status === 503);
  assert.equal(gets, 0);
});

// ---------- PLD-003: nunca se sube sin versión ----------

test("sin versión conocida, lee y fusiona la cuenta antes de subir (no la pisa)", async () => {
  const server = fakeServer({ data: { answers: ["de-otro-dispositivo"] }, version: 4 });
  const a = tab(server);
  a.local.answers.push("mia");
  assert.equal(a.sync.version, null);
  assert.equal(await a.sync.push(), true);
  assert.deepEqual(server.calls, ["GET", "PUT"], "lee antes de la primera subida");
  assert.deepEqual(server.doc.data.answers, ["de-otro-dispositivo", "mia"]);
  assert.equal(a.sync.version, 5);
});

test("ningún PUT sale con version null", async () => {
  const server = fakeServer({ data: { answers: ["x"] }, version: 2 });
  const sent = [];
  const original = server.request;
  server.request = async (method, path, options) => {
    if (method === "PUT") sent.push(options.json.version);
    return original(method, path, options);
  };
  const a = tab(server);
  a.local.answers.push("y");
  await a.sync.push();
  a.local.answers.push("z");
  await a.sync.push();
  assert.deepEqual(sent, [2, 3]);
});

test("si la sesión cambia mientras lee la versión, no fusiona ni sube", async () => {
  const server = fakeServer({ data: { answers: ["otra-cuenta"] }, version: 1 });
  let alive = true;
  const a = tab(server, { valid: () => alive });
  const original = server.request;
  server.request = async (method, ...rest) => {
    if (method === "GET") alive = false;
    return original(method, ...rest);
  };
  a.local.answers.push("mia");
  assert.equal(await a.sync.push(), false);
  assert.deepEqual(server.calls, ["GET"]);
  assert.deepEqual(a.local.answers, ["mia"]);
});

test("un 428 del servidor se trata como un conflicto: relee, fusiona y reintenta", async () => {
  const server = fakeServer({ data: { answers: ["remota"] }, version: 3 });
  const a = tab(server);
  a.sync.adopt({ version: 3 });
  let first = true;
  const original = server.request;
  server.request = async (method, path, options) => {
    if (method === "PUT" && first) {
      first = false;
      server.calls.push("PUT");
      throw new PreconditionRequired("428");
    }
    return original(method, path, options);
  };
  a.local.answers.push("local");
  assert.equal(await a.sync.push(), true);
  assert.deepEqual(server.calls, ["PUT", "GET", "PUT"]);
  assert.deepEqual(server.doc.data.answers, ["local", "remota"]);
});

test("reintento tras un fallo de red: sube con la versión que tenía, sin duplicar ni pisar", async () => {
  const server = fakeServer({ data: { answers: [] }, version: 1 });
  const a = tab(server);
  a.sync.adopt({ version: 1 });
  const original = server.request;
  let offline = true;
  server.request = async (method, path, options) => {
    if (offline && method === "PUT") {
      const error = new Error("Sin red");
      error.status = 0;
      throw error;
    }
    return original(method, path, options);
  };
  a.local.answers.push("q1");
  await assert.rejects(a.sync.push());
  assert.equal(a.sync.version, 1, "el fallo no cambia la versión leída");
  offline = false;
  a.local.answers.push("q2"); // cambio hecho sin conexión, antes del reintento
  assert.equal(await a.sync.push(), true);
  assert.deepEqual(server.doc, { data: { answers: ["q1", "q2"] }, version: 2 });
});

test("cambio durante una subida: el siguiente push lleva la versión nueva y no choca", async () => {
  const server = fakeServer({ data: { answers: [] }, version: 0 });
  const a = tab(server);
  a.sync.adopt({ version: 0 });
  a.local.answers.push("antes");
  const pending = a.sync.push();
  a.local.answers.push("durante"); // data() ya se leyó al empezar el PUT
  assert.equal(await pending, true);
  assert.equal(a.sync.version, 1);
  assert.equal(await a.sync.push(), true);
  assert.deepEqual(server.doc, { data: { answers: ["antes", "durante"] }, version: 2 });
  assert.deepEqual(server.calls, ["PUT", "PUT"], "sin 409 ni relecturas");
});
