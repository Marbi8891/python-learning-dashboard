import assert from "node:assert/strict";
import { test } from "node:test";
import {
  acceptanceRate,
  addExam,
  cleanPlanner,
  emptyPlanner,
  HISTORY_DAYS,
  mergePlanner,
  plannerHistory,
  postponedYesterday,
  removeExam,
  setMinutes,
  setTaskStatus,
  todayTasks,
  upcomingExams,
} from "../../frontend/js/learn/planner.js";

const NOW = new Date("2026-11-04T10:00:00");
const at = (iso) => new Date(iso);
const copy = (value) => JSON.parse(JSON.stringify(value));

test("planner: completar, posponer, rechazar y deshacer una tarea de hoy", () => {
  const p = emptyPlanner();
  setTaskStatus(p, "variables", "hecha", NOW);
  setTaskStatus(p, "bucles", "pospuesta", NOW);
  setTaskStatus(p, "tipos", "rechazada", NOW);
  assert.deepEqual(Object.fromEntries(Object.entries(todayTasks(p, NOW)).map(([k, v]) => [k, v.status])), {
    variables: "hecha",
    bucles: "pospuesta",
    tipos: "rechazada",
  });
  setTaskStatus(p, "tipos", null, NOW);
  assert.equal(todayTasks(p, NOW).tipos, undefined, "deshecha: vuelve a pendiente");
  assert.deepEqual([...postponedYesterday(p, at("2026-11-05T09:00:00"))], ["bucles"]);
});

test("planner: tiempo disponible limitado a 15-180 minutos", () => {
  const p = emptyPlanner();
  setMinutes(p, 1000, NOW);
  assert.equal(p.minutes, 180);
  setMinutes(p, "x", NOW);
  assert.equal(p.minutes, 45);
  assert.equal(p.minutesAt, NOW.toISOString());
});

test("planner: exámenes y entregas próximos, del más cercano al más lejano", () => {
  const p = emptyPlanner();
  addExam(p, { title: "Programación", module: "0485", date: "2026-12-15" }, NOW);
  const near = addExam(p, { title: "Práctica XML", module: "0373", date: "2026-11-10", kind: "entrega" }, NOW);
  addExam(p, { title: "Pasado", module: "0485", date: "2026-10-01" }, NOW);
  assert.equal(addExam(p, { title: "Sin fecha", date: "mañana" }, NOW), null);
  const list = upcomingExams(p, NOW);
  assert.deepEqual(list.map((e) => [e.title, e.days, e.kind]), [
    ["Práctica XML", 6, "entrega"],
    ["Programación", 41, "examen"],
  ]);
  removeExam(p, near.id, NOW);
  assert.equal(upcomingExams(p, NOW).length, 1);
});

test("planner: historial por día y porcentaje de recomendaciones aceptadas", () => {
  const p = emptyPlanner();
  setTaskStatus(p, "variables", "hecha", at("2026-11-03T10:00:00"));
  setTaskStatus(p, "bucles", "rechazada", at("2026-11-03T10:00:00"));
  setTaskStatus(p, "tipos", "hecha", NOW);
  const history = plannerHistory(p, NOW, 2);
  assert.deepEqual(history, [
    { day: "2026-11-04", hecha: 1, pospuesta: 0, rechazada: 0 },
    { day: "2026-11-03", hecha: 1, pospuesta: 0, rechazada: 1 },
  ]);
  assert.equal(acceptanceRate(p), 2 / 3);
  assert.equal(acceptanceRate(emptyPlanner()), null);
});

test("planner: solo guarda los últimos días", () => {
  const p = emptyPlanner();
  setTaskStatus(p, "variables", "hecha", at("2026-09-01T10:00:00"));
  setTaskStatus(p, "bucles", "hecha", NOW);
  assert.deepEqual(Object.keys(p.days), ["2026-11-04"]);
  assert.equal(HISTORY_DAYS, 30);
});

test("planner: cleanPlanner descarta lo manipulado y conserva lo válido y lo desconocido", () => {
  const p = cleanPlanner({
    minutes: 9999,
    exams: [{ id: "<x>", date: "2026-12-01" }, { id: "e1", title: "<b>Prog</b>", module: "drop table", date: "2026-12-01", kind: "raro" }],
    days: { "2026-11-04": { variables: { status: "hecha", at: NOW.toISOString() }, mal: { status: "borrar", at: "x" } }, ayer: {} },
    futuro: { x: 1 },
  });
  assert.equal(p.minutes, 180);
  assert.equal(p.exams.length, 1);
  assert.deepEqual([p.exams[0].module, p.exams[0].kind], [null, "examen"]);
  assert.deepEqual(Object.keys(p.days), ["2026-11-04"]);
  assert.deepEqual(Object.keys(p.days["2026-11-04"]), ["variables"]);
  assert.deepEqual(p.futuro, { x: 1 });
  assert.deepEqual(cleanPlanner(null), emptyPlanner());
});

test("planner: la fusión entre dispositivos no pierde nada y respeta lo más reciente", () => {
  const a = emptyPlanner();
  const b = emptyPlanner();
  setMinutes(a, 30, at("2026-11-04T08:00:00"));
  setMinutes(b, 60, at("2026-11-04T09:00:00"));
  const exam = addExam(a, { title: "Programación", module: "0485", date: "2026-12-15" }, NOW);
  addExam(b, { title: "BD", module: "0484", date: "2026-12-20" }, NOW);
  setTaskStatus(a, "variables", "hecha", at("2026-11-04T08:00:00"));
  setTaskStatus(b, "variables", null, at("2026-11-04T09:00:00")); // deshecha más tarde en el otro
  setTaskStatus(b, "bucles", "pospuesta", NOW);
  const bWithDeleted = copy(b);
  bWithDeleted.exams.push({ ...exam, deleted: true, at: at("2026-11-04T11:00:00").toISOString() });
  mergePlanner(a, bWithDeleted);
  assert.equal(a.minutes, 60);
  assert.deepEqual(upcomingExams(a, NOW).map((e) => e.title), ["BD"], "el borrado del otro dispositivo se respeta");
  assert.equal(todayTasks(a, NOW).variables, undefined);
  assert.equal(todayTasks(a, NOW).bucles.status, "pospuesta");
  const again = copy(a);
  mergePlanner(a, copy(bWithDeleted));
  assert.deepEqual(a, again, "fusionar dos veces da lo mismo");
});
