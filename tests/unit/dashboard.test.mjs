import assert from "node:assert/strict";
import { test } from "node:test";
import {
  dailySeries,
  examSummary,
  lastPractice,
  MASTERY_STREAK,
  moduleProgress,
  latestActivity,
  parseServerDate,
  recurringErrors,
  safePercent,
  sectionFromRoute,
} from "../../frontend/js/dashboard-data.js";

test("la ruta elige la sección del panel y lo desconocido lleva al resumen", () => {
  assert.equal(sectionFromRoute("#/panel"), "resumen");
  assert.equal(sectionFromRoute("#/panel/logros"), "logros");
  assert.equal(sectionFromRoute("#/panel/perfil"), "perfil");
  assert.equal(sectionFromRoute("#/panel/<script>"), "resumen");
  assert.equal(sectionFromRoute("#/panelx"), "resumen");
});

test("las fechas sin zona de la API se leen como UTC", () => {
  assert.equal(parseServerDate("2026-10-19T10:00:00").toISOString(), "2026-10-19T10:00:00.000Z");
  assert.equal(parseServerDate("2026-10-19T10:00:00Z").toISOString(), "2026-10-19T10:00:00.000Z");
  assert.equal(parseServerDate("2026-10-19T12:00:00+02:00").toISOString(), "2026-10-19T10:00:00.000Z");
  assert.equal(parseServerDate(null), null);
  assert.equal(parseServerDate("no es una fecha"), null);
});

test("la serie diaria tiene todos los días y suma el curso PCAP y los conceptos", () => {
  const now = new Date(2026, 9, 19, 18, 0);
  const series = dailySeries({
    serverDaily: [
      { day: "2026-10-19", lessons_completed: 1, attempts: 3 },
      { day: "2026-01-01", lessons_completed: 9, attempts: 9 }, // fuera del rango
    ],
    learnLog: [{ at: new Date(2026, 9, 18, 9, 0).toISOString() }, { at: new Date(2026, 9, 19, 9, 0).toISOString() }, { at: "roto" }],
    days: 7,
    now,
  });
  assert.equal(series.length, 7);
  assert.equal(series[0].day, "2026-10-13");
  assert.deepEqual(series.at(-1), { day: "2026-10-19", lessons: 1, attempts: 3, concepts: 1, total: 5 });
  assert.equal(series.at(-2).total, 1);
  assert.equal(series.reduce((sum, d) => sum + d.total, 0), 6);
});

test("sin actividad, la serie existe pero está a cero (estado vacío, nada inventado)", () => {
  const series = dailySeries({ days: 30, now: new Date(2026, 9, 19) });
  assert.equal(series.length, 30);
  assert.ok(series.every((d) => d.total === 0));
});

test("simulacros: cuenta los de todos los cursos y la mejor nota, o null sin ninguno", () => {
  assert.deepEqual(examSummary({}), { count: 0, best: null });
  const summary = examSummary({
    learnExams: [{ correct: 8, total: 10 }, { correct: 0, total: 0 }],
    courseExams: [{ score: 65 }, { score: 72 }],
  });
  assert.deepEqual(summary, { count: 3, best: 80 });
});

test("errores recurrentes: solo los repetidos, de más a menos frecuentes", () => {
  const errors = {
    "a.uno": { n: 1, last: "2026-10-01T00:00:00Z", streak: 0 },
    "b.dos": { n: 4, last: "2026-10-01T00:00:00Z", streak: 0 },
    "c.tres": { n: 2, last: "2026-10-05T00:00:00Z", streak: 2 },
  };
  assert.deepEqual(recurringErrors(errors).map((e) => e.id), ["b.dos", "c.tres"]);
  assert.deepEqual(recurringErrors({}), []);
});

test("última actividad y última práctica", () => {
  assert.equal(lastPractice({ srs: {} }), null);
  assert.equal(lastPractice({ srs: { a: { last: "2026-10-01T10:00:00Z" }, b: { last: "2026-10-03T10:00:00Z" }, c: { last: 3 } } }), "2026-10-03T10:00:00Z");
  const newest = latestActivity([{ at: new Date("2026-10-01"), label: "a" }, null, { at: new Date("2026-10-05"), label: "b" }, { at: new Date("x") }]);
  assert.equal(newest.label, "b");
  assert.equal(latestActivity([]), null);
});

test("porcentajes solo con un denominador conocido", () => {
  assert.equal(safePercent(1, 3), 33);
  assert.equal(safePercent(1, 0), null);
  assert.equal(safePercent(1, undefined), null);
});

test("progreso por módulo: practicada no es lo mismo que dominada", () => {
  const modules = [
    { id: "0485", code: "0485", name: "Programación", course: 1, platformQuestions: 4, platformQuestionIds: { programacion: ["p1", "p2", "p3"], java: ["j1"] } },
    { id: "0484", code: "0484", name: "Bases de datos", course: 1, platformQuestions: 1, platformQuestionIds: { sql: ["s1"] } },
    { id: "0613", code: "0613", name: "Servidor", course: 2, platformQuestions: 0, platformQuestionIds: {} },
  ];
  const states = {
    // p1: dos aciertos seguidos (dominada) · p2: un acierto suelto · p3: falló la última · j1: sin responder
    programacion: { p1: [false, true, true], p2: [true], p3: [true, true, false] },
    sql: { s1: "dañado" },
  };
  const [prog, bd, ...rest] = moduleProgress(modules, (course) => states[course]);
  assert.deepEqual(prog, { id: "0485", code: "0485", name: "Programación", course: 1, total: 4, practiced: 3, mastered: 1 });
  assert.equal(bd.practiced, 0); // un historial que no es una lista no cuenta
  assert.deepEqual(rest, []); // un módulo sin preguntas en la plataforma no aparece
  assert.equal(MASTERY_STREAK, 2);
});
