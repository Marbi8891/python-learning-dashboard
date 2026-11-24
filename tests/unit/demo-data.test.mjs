import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { DEMO_PREFIX, PrefixedStorage, daysBetween, demoProfile, localDay, seedEntries, shiftDates, shiftText, storageKeys } from "../../frontend/js/demo/demo-data.js";
import { cleanGame } from "../../frontend/js/game-data.js";
import { cleanLearning } from "../../frontend/js/learn/mastery.js";
import { cleanPlanner } from "../../frontend/js/learn/planner.js";
import { cleanProgress } from "../../frontend/js/progress-guard.js";
import { cleanCyber } from "../../frontend/js/cybersecurity-data.js";

const fixture = JSON.parse(readFileSync(new URL("../../frontend/data/demo/alex.json", import.meta.url), "utf-8"));

/** Almacén en memoria con la interfaz de Storage (length, key, getItem…). */
function memoryStorage(initial = {}) {
  const map = new Map(Object.entries(initial));
  return {
    get length() {
      return map.size;
    },
    key: (i) => [...map.keys()][i] ?? null,
    getItem: (k) => (map.has(k) ? map.get(k) : null),
    setItem: (k, v) => map.set(k, String(v)),
    removeItem: (k) => map.delete(k),
    dump: () => Object.fromEntries(map),
  };
}

test("las claves de la demo van aparte de las reales y las cubre la política de privacidad", () => {
  assert.ok(DEMO_PREFIX.startsWith("pld:")); // la política de privacidad describe todas las claves pld:
  const backing = new Map();
  const fake = { getItem: (k) => backing.get(k) ?? null, setItem: (k, v) => backing.set(k, String(v)), removeItem: (k) => backing.delete(k), key: (i) => [...backing.keys()][i] ?? null, get length() { return backing.size; } };
  new PrefixedStorage(fake, DEMO_PREFIX).setItem("pld:completed", "[]");
  assert.deepEqual([...backing.keys()], [`${DEMO_PREFIX}pld:completed`]); // nunca la clave real «pld:completed»
});

test("daysBetween cuenta días de calendario, también al cambiar de hora", () => {
  assert.equal(daysBetween("2026-11-20", "2026-11-22"), 2);
  assert.equal(daysBetween("2026-11-20", "2026-11-18"), -2);
  assert.equal(daysBetween("2026-03-28", "2026-03-30"), 2); // cambio de hora en Europa
});

test("shiftText desplaza días y fechas con hora, y deja igual el resto", () => {
  assert.equal(shiftText("2026-11-20", 3), "2026-11-23");
  assert.equal(shiftText("2026-12-30", 5), "2027-01-04");
  assert.equal(shiftText("2026-11-20T18:00:00.000Z", -1), "2026-11-19T18:00:00.000Z");
  assert.equal(shiftText("variables", 3), "variables");
  assert.equal(shiftText("2026-11-20Tbasura", 3), "2026-11-20Tbasura");
});

test("shiftDates desplaza valores y claves de objeto con forma de día", () => {
  const shifted = shiftDates({ days: { "2026-11-20": { at: "2026-11-20T18:00:00.000Z" } }, list: ["2026-11-19", 4, null, true] }, 2);
  assert.deepEqual(shifted, { days: { "2026-11-22": { at: "2026-11-22T18:00:00.000Z" } }, list: ["2026-11-21", 4, null, true] });
});

test("la siembra lleva el día de referencia a hoy: la racha termina hoy", () => {
  const now = new Date(2027, 1, 10, 12);
  const entries = Object.fromEntries(seedEntries(fixture, now));
  const game = JSON.parse(entries["pld:game"]);
  assert.equal(game.days.at(-1), localDay(now));
  assert.ok(game.days.includes(localDay(new Date(2027, 1, 5, 12)))); // 6 días seguidos
});

test("la siembra es determinista: el mismo día da exactamente lo mismo", () => {
  const now = new Date(2026, 11, 1, 9);
  assert.deepEqual(seedEntries(fixture, now), seedEntries(fixture, new Date(2026, 11, 1, 22)));
});

test("la siembra rechaza datos sin el formato esperado", () => {
  assert.throws(() => seedEntries({}), /formato/);
  assert.throws(() => seedEntries({ anchor: "ayer", storage: {} }), /formato/);
});

test("los datos de Alex pasan intactos por la limpieza de cada almacén", () => {
  const s = fixture.storage;
  assert.deepEqual(cleanGame(s["pld:game"]).days, s["pld:game"].days);
  assert.deepEqual(cleanGame(s["pld:game"]).quiz, s["pld:game"].quiz);
  const learn = cleanLearning(s["pld:learn"]);
  assert.deepEqual(Object.keys(learn.ex).sort(), Object.keys(s["pld:learn"].ex).sort());
  assert.deepEqual(Object.keys(learn.concepts).sort(), Object.keys(s["pld:learn"].concepts).sort());
  assert.equal(learn.log.length, s["pld:learn"].log.length);
  assert.deepEqual(cleanPlanner(s["pld:planner"]).days, s["pld:planner"].days);
  assert.equal(cleanProgress(s["pld:pcap"]).exams.length, 1);
  assert.deepEqual(cleanProgress(s["pld:course:js"]).done, s["pld:course:js"].done);
  assert.deepEqual(cleanCyber(s["pld:cybersecurity:v1"]).weeks, s["pld:cybersecurity:v1"].weeks);
});

test("los datos de Alex se presentan como ficticios y no llevan datos personales", () => {
  assert.equal(fixture.profile.display_name, "Alex Developer");
  assert.equal(fixture.profile.fictional, true);
  assert.match(fixture.notice, /ficticios/);
  assert.doesNotMatch(JSON.stringify(fixture), /@|email|password|token/i);
  for (const key of Object.keys(fixture.storage)) assert.ok(key.startsWith("pld:"), key);
});

test("demoProfile lleva las fechas del perfil y la actividad a hoy", () => {
  const now = new Date(2026, 10, 25, 12);
  const { profile, feed } = demoProfile(fixture, now);
  assert.equal(profile.display_name, "Alex Developer");
  assert.equal(feed[0].at.slice(0, 10), "2026-11-25");
});

test("PrefixedStorage guarda con prefijo y no toca las demás claves", () => {
  const backing = memoryStorage({ "pld:game": "real", otra: "x" });
  const demo = new PrefixedStorage(backing, DEMO_PREFIX);
  demo.setItem("pld:game", "ficticio");
  assert.equal(demo.getItem("pld:game"), "ficticio");
  assert.equal(backing.getItem("pld:game"), "real");
  assert.deepEqual(demo.keys(), ["pld:game"]);
  assert.equal(demo.length, 1);
  assert.equal(demo.key(0), "pld:game");
  assert.deepEqual(storageKeys(demo), ["pld:game"]);
  demo.removeItem("pld:game");
  demo.setItem("a", 1);
  demo.clear();
  assert.deepEqual(backing.dump(), { "pld:game": "real", otra: "x" });
});

test("storageKeys también lee las claves de un almacén normal", () => {
  assert.deepEqual(storageKeys({ a: "1", b: "2" }), ["a", "b"]);
});

import { demoDashboard } from "../../frontend/js/demo/demo-data.js";
import { estimatedStudyMinutes, formatMinutes } from "../../frontend/js/dashboard-data.js";

test("demoDashboard construye la misma forma que /api/v1/dashboard", () => {
  const modules = [
    { slug: "m1", title: "Uno", lessons: [{ slug: "a", title: "A" }, { slug: "b", title: "B" }] },
    { slug: "m2", title: "Dos", lessons: [{ slug: "c", title: "C" }] },
  ];
  const feed = [
    { kind: "attempt", lesson_slug: "b", lesson_title: "B", passed: false, at: "2026-11-20T18:00:00.000Z" },
    { kind: "lesson_completed", lesson_slug: "a", lesson_title: "A", passed: null, at: "2026-11-19T18:00:00.000Z" },
    { kind: "attempt", lesson_slug: "a", lesson_title: "A", passed: true, at: "2026-11-19T17:50:00.000Z" },
  ];
  const data = demoDashboard({ profile: { display_name: "Alex Developer", created_at: "2026-10-21T10:00:00.000Z" }, feed, completed: new Set(["a"]), modules, now: new Date("2026-11-20T19:00:00Z") });
  assert.deepEqual(Object.keys(data).sort(), ["daily", "exercises", "generated_at", "lessons", "synced", "user"]);
  assert.equal(data.user.email, "");
  assert.deepEqual(data.lessons.next_lesson, { slug: "b", title: "B" });
  assert.equal(data.lessons.total, 3);
  assert.equal(data.lessons.completed, 1);
  assert.deepEqual(data.lessons.modules.map((m) => m.completed), [1, 0]);
  assert.deepEqual(data.exercises, { attempts: 2, passed: 1, lessons_tried: 2, lessons_passed: 1, last_attempt_at: "2026-11-20T18:00:00.000Z" });
  assert.equal(data.daily.reduce((n, d) => n + d.attempts, 0), 2);
  assert.ok(data.daily[0].day < data.daily.at(-1).day);
});

test("el tiempo estimado cuenta 15 minutos por tarea hecha en 30 días, y null si no hay ninguna", () => {
  const now = new Date(2026, 10, 20, 12);
  const planner = {
    days: {
      "2026-11-20": { a: { status: "hecha" }, b: { status: "pospuesta" } },
      "2026-11-19": { c: { status: "hecha" }, d: { status: "hecha" } },
      "2026-10-01": { e: { status: "hecha" } }, // fuera de los 30 días
    },
  };
  assert.deepEqual(estimatedStudyMinutes(planner, now), { minutes: 45, tasks: 3 });
  assert.equal(estimatedStudyMinutes({ days: {} }, now), null);
  assert.equal(estimatedStudyMinutes(undefined, now), null);
  assert.equal(formatMinutes(45), "45 min");
  assert.equal(formatMinutes(120), "2 h");
  assert.equal(formatMinutes(135), "2 h 15 min");
});
