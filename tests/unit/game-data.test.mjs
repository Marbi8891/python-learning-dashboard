import assert from "node:assert/strict";
import { test } from "node:test";
import { cleanGame, emptyGame, mergeGame } from "../../frontend/js/game-data.js";

test("limpia lo que llega de fuera: tipos, ids y notas válidas", () => {
  const clean = cleanGame({
    quiz: { variables: 3, tipos: 7, "<img>": 2, bucles: "3" },
    passed: ["variables", "variables", "<script>", 5],
    days: ["2026-10-19", "2026-10-18", "ayer"],
    flags: { firstRun: true, bugHunter: "sí" },
    badges: ["hola-mundo"],
    extra: "se descarta",
  });
  assert.deepEqual(clean.quiz, { variables: 3 });
  assert.deepEqual(clean.passed, ["variables"]);
  assert.deepEqual(clean.days, ["2026-10-18", "2026-10-19"]);
  assert.deepEqual(clean.flags, { firstRun: true, bugHunter: false, lastRunFailed: false });
  assert.equal("extra" in clean, false);
  assert.deepEqual(cleanGame(null), emptyGame());
  assert.deepEqual(cleanGame([1, 2]), emptyGame());
});

test("fusiona sin perder nada de ningún dispositivo", () => {
  const local = cleanGame({ quiz: { variables: 1, tipos: 3 }, days: ["2026-10-18"], badges: ["hola-mundo"], flags: { lastRunFailed: true } });
  mergeGame(local, {
    quiz: { variables: 3, tipos: 2, bucles: 0 },
    days: ["2026-10-19", "2026-10-18"],
    badges: ["retador"],
    challenges: ["listas"],
    flags: { bugHunter: true, lastRunFailed: false },
  });
  assert.deepEqual(local.quiz, { variables: 3, tipos: 3, bucles: 0 });
  assert.deepEqual(local.days, ["2026-10-18", "2026-10-19"]);
  assert.deepEqual(local.badges, ["hola-mundo", "retador"]);
  assert.deepEqual(local.challenges, ["listas"]);
  assert.equal(local.flags.bugHunter, true);
  assert.equal(local.flags.lastRunFailed, true, "la última ejecución es la de este navegador");
});

test("fusionar con una copia vacía o dañada no cambia nada", () => {
  const local = cleanGame({ passed: ["variables"], days: ["2026-10-19"] });
  const before = structuredClone(local);
  mergeGame(local, undefined);
  mergeGame(local, "basura");
  assert.deepEqual(local, before);
});
