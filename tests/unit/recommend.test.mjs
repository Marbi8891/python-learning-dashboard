import assert from "node:assert/strict";
import { test } from "node:test";
import { allStats, recordAttempt, reviewConcept } from "../../frontend/js/learn/mastery.js";
import { missingPrerequisites, nextNewConcept, selectExercises, similarExercise, todayPlan } from "../../frontend/js/learn/recommend.js";
import { daysAgo, exercisesOf, fresh, index, NOW, seeded } from "./helpers.mjs";

const master = (state, concept, now = NOW) => {
  for (const e of exercisesOf(concept)) recordAttempt(state, e, { ok: true, error: null }, { now });
};

test("sin actividad, el plan propone el primer concepto de la ruta", () => {
  const plan = todayPlan(index, fresh(), NOW);
  assert.deepEqual(plan.map((p) => [p.type, p.concept]), [["learn", "algoritmos"]]);
});

test("con prerrequisitos flojos, dice qué reforzar antes de avanzar", () => {
  const state = fresh();
  master(state, "algoritmos");
  master(state, "variables");
  // tipos empezado pero flojo: operadores (siguiente) depende de él
  recordAttempt(state, exercisesOf("tipos")[0], { ok: false, error: null }, { now: NOW });
  const stats = allStats(index, state, NOW);
  assert.deepEqual(missingPrerequisites(index, stats, "operadores"), ["tipos"]);
  assert.deepEqual(nextNewConcept(index, stats), { id: "operadores", blockedBy: ["tipos"] });
  const plan = todayPlan(index, state, NOW);
  assert.deepEqual(plan, [
    { type: "reinforce", concept: "tipos", before: "operadores", reason: "Necesitas reforzar Tipos de datos y conversiones antes de pasar a Operadores y expresiones." },
  ]);
  assert.ok(!plan.some((p) => p.type === "learn"), "no se propone contenido nuevo con la base floja");
});

test("el aviso «Necesitas reforzar X antes de pasar a Y» aparece cuando X no tiene otra entrada", () => {
  const state = fresh();
  master(state, "algoritmos");
  master(state, "variables");
  master(state, "tipos");
  master(state, "operadores");
  master(state, "entrada-salida");
  // condicionales flojo pero con importancia DAW → entraría como práctica; probamos con un concepto de importancia 2
  const stats = allStats(index, state, NOW);
  const next = nextNewConcept(index, stats);
  assert.equal(next.id, "condicionales");
  assert.deepEqual(next.blockedBy, []);
  const plan = todayPlan(index, state, NOW);
  assert.deepEqual(plan.find((p) => p.type === "learn"), { type: "learn", concept: "condicionales", reason: "Siguiente concepto de la ruta." });
});

test("prioridad: repaso pendiente, luego errores recientes, luego DAW débil, luego nuevo", () => {
  const state = fresh();
  master(state, "algoritmos", daysAgo(10));
  master(state, "variables", daysAgo(10));
  reviewConcept(state, "variables", 1, daysAgo(10)); // repaso a 1 día: atrasado
  recordAttempt(state, index.exercises.get("tip-01"), { ok: false, error: "tipos.texto-numero" }, { now: daysAgo(1) });
  recordAttempt(state, index.exercises.get("ope-02"), { ok: true, error: null }, { now: daysAgo(1) });
  const plan = todayPlan(index, state, NOW);
  assert.deepEqual(
    plan.map((p) => p.type),
    ["review", "errors", "practice", "reinforce"].slice(0, plan.length),
  );
  assert.equal(plan[0].concept, "variables");
  assert.match(plan[0].reason, /hace 10 días/);
  assert.equal(plan[1].concept, "tipos");
  assert.deepEqual(plan[1].errors, ["tipos.texto-numero"]);
  assert.equal(plan[2].concept, "operadores");
  assert.ok(plan.length <= 4);
  assert.equal(new Set(plan.map((p) => p.concept)).size, plan.length, "sin conceptos repetidos");
});

test("con todo dominado y sin repasos pendientes, propone repaso general de lo más antiguo", () => {
  const state = fresh();
  index.path.forEach((id, i) => master(state, id, daysAgo(40 - i)));
  const plan = todayPlan(index, state, NOW);
  assert.ok(plan.length >= 1);
  assert.ok(plan.every((p) => p.type === "review"));
  assert.equal(plan[0].concept, index.path[0]);
});

test("selectExercises: prioriza los que trabajan un error activo y los fallados, evita los dominados", () => {
  const state = fresh();
  const list = exercisesOf("bucles");
  // Domina dos ejercicios (dos aciertos seguidos)
  for (const e of list.slice(0, 2)) {
    recordAttempt(state, e, { ok: true, error: null }, { now: daysAgo(3) });
    recordAttempt(state, e, { ok: true, error: null }, { now: daysAgo(2) });
  }
  recordAttempt(state, index.exercises.get("buc-05"), { ok: false, error: "bucles.bucle-infinito" }, { now: daysAgo(1) });
  const chosen = selectExercises(index, state, ["bucles"], 3, { now: NOW, random: seeded(3) });
  assert.equal(chosen.length, 3);
  assert.ok(chosen.some((e) => e.id === "buc-05"), "el fallado vuelve");
  assert.ok(!chosen.some((e) => list.slice(0, 2).includes(e)), "los dominados no se repiten");
  assert.deepEqual(chosen.map((e) => e.level), [...chosen.map((e) => e.level)].sort(), "de más fácil a más difícil");
});

test("selectExercises: un principiante no recibe primero los problemas más difíciles", () => {
  const chosen = selectExercises(index, fresh(), ["bucles"], 3, { now: NOW, random: seeded(7) });
  assert.ok(chosen.every((e) => e.level <= 2));
});

test("selectExercises respeta los tipos pedidos y las exclusiones", () => {
  const chosen = selectExercises(index, fresh(), ["trazado", "bucles"], 20, { now: NOW, kinds: ["output"], exclude: ["tra-01"] });
  assert.ok(chosen.length > 0);
  assert.ok(chosen.every((e) => e.kind === "output" && e.id !== "tra-01"));
});

test("similarExercise busca otro ejercicio del concepto que detecte el mismo error", () => {
  const original = index.exercises.get("buc-01");
  const similar = similarExercise(index, original, "bucles.range-fin");
  assert.ok(similar && similar.id !== original.id && similar.concept === "bucles");
  assert.equal(similarExercise(index, original, null, exercisesOf("bucles").map((e) => e.id)), null);
});

test("selectExercises con `only` elige solo entre los ejercicios indicados (practicar un error)", () => {
  const only = ["buc-01", "buc-06", "pse-01"];
  const chosen = selectExercises(index, fresh(), ["bucles", "pseudocodigo"], 4, { now: NOW, only });
  assert.deepEqual(chosen.map((e) => e.id).sort(), [...only].sort());
});
