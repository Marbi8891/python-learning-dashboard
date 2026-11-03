// SYNC-02: al fusionar dos dispositivos gana el historial de la respuesta más reciente, no el más
// largo. Cada historial guarda solo los 5 últimos intentos, así que con los dos llenos la regla
// antigua («el más largo; si empatan, el local») descartaba lo hecho en el otro dispositivo.
import assert from "node:assert/strict";
import { test } from "node:test";
import { mergePcap, newerHistory, pcap } from "../../frontend/js/pcap-store.js";
import { mergeLearning, recordAttempt } from "../../frontend/js/learn/mastery.js";
import { daysAgo, fresh, index, NOW } from "./helpers.mjs";

const AYER = "2026-11-02T10:00:00.000Z";
const HOY = "2026-11-03T10:00:00.000Z";

test("newerHistory: con fecha en las dos copias gana la más reciente aunque tengan la misma longitud", () => {
  const local = [true, true, true, true, true];
  const remote = [true, true, true, true, false];
  assert.equal(newerHistory(local, remote, AYER, HOY), remote);
  assert.equal(newerHistory(local, remote, HOY, AYER), local);
});

test("newerHistory: sin fecha en alguna copia se mantiene la regla anterior (más largo; empate, local)", () => {
  assert.deepEqual(newerHistory([true], [false, false], undefined, HOY), [false, false]);
  const local = [true, true];
  assert.equal(newerHistory(local, [false, false], AYER, undefined), local);
  assert.deepEqual(newerHistory(undefined, [false], undefined, undefined), [false]);
});

test("mergePcap: la respuesta hecha hoy en otro dispositivo no se pierde con los dos historiales llenos", () => {
  pcap.answers = { "oop-01": [true, true, true, true, true] };
  pcap.srs = { "oop-01": { box: 5, due: "2026-12-01", last: AYER } };
  mergePcap({
    answers: { "oop-01": [true, true, true, true, false] },
    srs: { "oop-01": { box: 1, due: "2026-11-04", last: HOY } },
  });
  assert.deepEqual(pcap.answers["oop-01"], [true, true, true, true, false]);
  assert.equal(pcap.srs["oop-01"].last, HOY, "el repaso también sigue a la más reciente");
});

test("mergePcap: si lo más reciente es lo local, se conserva", () => {
  pcap.answers = { "oop-01": [false, true] };
  pcap.srs = { "oop-01": { box: 2, due: "2026-11-06", last: HOY } };
  mergePcap({
    answers: { "oop-01": [true, true, true, true, true] },
    srs: { "oop-01": { box: 5, due: "2026-12-01", last: AYER } },
  });
  assert.deepEqual(pcap.answers["oop-01"], [false, true]);
});

test("mergeLearning: gana el intento más reciente y el total de intentos no baja", () => {
  const local = fresh();
  const remote = fresh();
  const ex = index.exercises.get("buc-01");
  for (let day = 9; day >= 4; day -= 1) recordAttempt(local, ex, { ok: true, error: null }, { now: daysAgo(day) });
  recordAttempt(remote, ex, { ok: false, error: null }, { now: NOW });
  mergeLearning(local, JSON.parse(JSON.stringify(remote)));
  assert.deepEqual(local.ex["buc-01"].h, [false]);
  assert.equal(local.ex["buc-01"].n, 6);
  assert.equal(local.ex["buc-01"].last, NOW.toISOString());
});
