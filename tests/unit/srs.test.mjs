import assert from "node:assert/strict";
import { test } from "node:test";
import { canAdvance, INTERVAL_DAYS, isDue, schedule, scheduleAnswer } from "../../frontend/js/srs.js";

const NOW = new Date("2026-10-04T10:00:00");
const day = (iso) => new Date(`${iso}T10:00:00`);

test("srs: un elemento nuevo sube a la caja 1 (mañana) al acertar", () => {
  assert.deepEqual(scheduleAnswer(undefined, true, NOW), { box: 1, due: "2026-10-05", last: NOW.toISOString() });
});

test("srs: acertar cuando toca recorre los intervalos 1, 3, 7, 14 y 30 días", () => {
  let item = null;
  let now = NOW;
  const boxes = [];
  for (let i = 0; i < 6; i += 1) {
    item = scheduleAnswer(item, true, now);
    boxes.push(item.box);
    now = day(item.due);
  }
  assert.deepEqual(boxes, [1, 2, 3, 4, 5, 5]);
  assert.deepEqual(INTERVAL_DAYS, [0, 1, 3, 7, 14, 30]);
});

test("srs: acertar antes de tiempo no comprime el repaso (AUD-004)", () => {
  let item = scheduleAnswer(null, true, NOW);
  for (let i = 0; i < 5; i += 1) item = scheduleAnswer(item, true, NOW);
  assert.equal(item.box, 1);
  assert.equal(item.due, "2026-10-05");
  assert.equal(canAdvance(item, NOW), false);
  assert.equal(canAdvance(item, day("2026-10-05")), true);
});

test("srs: fallar vuelve a la caja 1 aunque no tocara repasar", () => {
  const item = { box: 4, due: "2026-10-20", last: NOW.toISOString() };
  assert.deepEqual(scheduleAnswer(item, false, NOW), { box: 1, due: "2026-10-05", last: NOW.toISOString() });
});

test("srs: «regular» mantiene la caja (al menos 1) y reprograma solo si tocaba", () => {
  assert.equal(schedule({ box: 3, due: "2026-10-04" }, "keep", NOW).box, 3);
  assert.equal(schedule({ box: 3, due: "2026-10-04" }, "keep", NOW).due, "2026-10-11");
  assert.equal(schedule({ box: 0, due: null }, "keep", NOW).box, 1);
  assert.deepEqual(schedule({ box: 3, due: "2026-10-09" }, "keep", NOW).due, "2026-10-09");
});

test("srs: no modifica el elemento recibido y tolera datos raros", () => {
  const item = Object.freeze({ box: 2, due: "2026-10-01" });
  assert.equal(schedule(item, "up", NOW).box, 3);
  assert.equal(schedule({ box: 99, due: null }, "up", NOW).box, 5);
  assert.equal(schedule({ box: "x" }, "up", NOW).box, 1);
  assert.equal(isDue({ due: "2026-10-04" }, NOW), true);
  assert.equal(isDue({ due: null }, NOW), false);
});
