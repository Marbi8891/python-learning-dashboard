// Control de versiones al subir el progreso: dos pestañas no se pisan.
import assert from "node:assert/strict";
import { test } from "node:test";
import { createDocSync, MAX_CONFLICT_RETRIES } from "../../frontend/js/doc-sync.js";

class Conflict extends Error {
  status = 409;
}

/** Servidor falso con la misma regla que el backend: PUT con versión vieja → 409. */
function fakeServer(initial = { data: {}, version: 0 }) {
  const server = { doc: structuredClone(initial), calls: [] };
  server.request = async (method, path, options) => {
    server.calls.push(method);
    if (method === "GET") return structuredClone(server.doc);
    const { data, version } = options.json;
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
