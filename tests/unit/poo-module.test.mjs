// Módulo de POO: estructura del índice, lecciones completadas en el progreso y vistas.
import assert from "node:assert/strict";
import { test } from "node:test";
import { allStats, cleanLearning, markSection, mergeLearning, recordAttempt, sectionsDone } from "../../frontend/js/learn/mastery.js";
import { availableUnits, exerciseTitle, pooModule, renderModule, unitBody, unitExercises, unitToc } from "../../frontend/js/learn/poo-view.js";
import { errorsTested } from "../../frontend/js/learn/answers.js";
import { exercisesForError, similarExercise } from "../../frontend/js/learn/recommend.js";
import { fresh, index, NOW } from "./helpers.mjs";

const unit2 = index.concepts.get("poo");
const LESSON = unit2.sections[0].id;

test("el módulo tiene 10 unidades numeradas y la Unidad 2 es el concepto poo de siempre", () => {
  const module = pooModule(index);
  assert.equal(module.units.length, 10);
  assert.deepEqual(module.units.map((u) => u.number), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  assert.deepEqual(unit2.unit, { module: "poo", number: 2 });
  assert.ok(availableUnits(index).some((u) => u.id === "poo"));
  // Las unidades publicadas existen como conceptos; las demás no rompen nada
  for (const u of module.units) assert.equal(u.available, index.concepts.has(u.id));
});

test("cada unidad publicada tiene los once apartados y ejercicios de su propio concepto", () => {
  for (const { id } of availableUnits(index)) {
    const unit = index.concepts.get(id);
    assert.equal(unitToc(unit).length >= 11, true);
    for (const field of ["objectives", "prior", "key", "sections", "guided", "autonomous", "selfcheck", "recap", "pass", "errors"]) {
      assert.ok(unit[field]?.length ?? Object.keys(unit[field] ?? {}).length, `${id}: falta ${field}`);
    }
    for (const section of unit.sections) {
      assert.equal(unitExercises(unit, { section: section.id }).length, 3);
      for (const ex of unitExercises(unit, { section: section.id })) assert.equal(index.exercises.get(ex).concept, id);
    }
    for (const mapping of unit.curriculum) {
      assert.ok(["verified", "proposed", "unassigned"].includes(mapping.status));
      assert.ok(mapping.source && /^\d{4}-\d{2}-\d{2}$/.test(mapping.reviewed));
    }
  }
});

test("completar una lección se guarda una vez, sobrevive a la limpieza y no cuenta para el dominio", () => {
  const state = fresh();
  markSection(state, LESSON, NOW);
  markSection(state, LESSON, new Date("2026-12-01T10:00:00Z"));
  assert.equal(state.sections[LESSON], NOW.toISOString());
  assert.deepEqual(sectionsDone(state, unit2), [{ id: LESSON, at: NOW.toISOString() }]);
  const clean = cleanLearning(JSON.parse(JSON.stringify(state)));
  assert.deepEqual(clean.sections, state.sections);
  const stats = allStats(index, clean, NOW).get("poo");
  assert.equal(stats.attempted, 0);
  assert.notEqual(stats.status, "dominado");
});

test("la limpieza descarta lecciones con id o fecha no válidos y no crea el bloque si está vacío", () => {
  const clean = cleanLearning({ v: 1, sections: { "<script>": "2026-01-01T00:00:00Z", "poo.x": "ayer" } });
  assert.equal("sections" in clean, false);
  assert.equal("sections" in cleanLearning(null), false);
});

test("al fusionar con la cuenta, las lecciones se unen y gana la primera fecha", () => {
  const local = fresh();
  markSection(local, "poo.definir", new Date("2026-11-10T10:00:00Z"));
  const remote = fresh();
  markSection(remote, "poo.definir", new Date("2026-11-09T10:00:00Z"));
  markSection(remote, "poo.estado", new Date("2026-11-11T10:00:00Z"));
  mergeLearning(local, remote);
  assert.deepEqual(local.sections, { "poo.definir": "2026-11-09T10:00:00.000Z", "poo.estado": "2026-11-11T10:00:00.000Z" });
  mergeLearning(local, fresh()); // una copia vacía no borra nada
  assert.equal(Object.keys(local.sections).length, 2);
});

test("un fallo en la unidad deja el error activo y el motor propone otro ejercicio que lo trabaja", () => {
  const state = fresh();
  const ex = index.exercises.get("poo-14");
  recordAttempt(state, ex, { ok: false, error: "poo.olvida-self" }, { now: NOW });
  const similar = similarExercise(index, ex, "poo.olvida-self");
  assert.ok(similar, "debe haber otro ejercicio para el error poo.olvida-self");
  assert.equal(similar.concept, "poo");
  assert.ok(errorsTested(similar).includes("poo.olvida-self"), "el ejercicio propuesto detecta ese mismo error");
  // Cada error típico nuevo de la unidad se puede practicar con más de un ejercicio
  for (const id of ["poo.olvida-self", "poo.clase-objeto", "poo.init-mal-escrito", "poo.alias-copia"]) {
    assert.ok(exercisesForError(index, id).length >= 2, `${id}: pocos ejercicios para practicarlo`);
  }
});

test("las vistas muestran las correspondencias como propuesta y el aviso de que completar no es dominar", () => {
  const state = fresh();
  const html = unitBody(index, state, unit2, allStats(index, state, NOW).get("poo"));
  assert.match(html, /pendiente de validar/);
  assert.doesNotMatch(html, /Validada/);
  assert.match(html, /lo que demuestra que la dominas son los ejercicios/);
  for (const [id] of unitToc(unit2)) assert.match(html, new RegExp(`id="${id}"`));
  const module = renderModule(index, state, NOW);
  assert.match(module, /En preparación/);
  assert.match(module, /href="#\/teoria\/poo"/);
  assert.match(module, /Completar lecciones no equivale a dominar/);
});

test("los ejercicios de la unidad tienen un título corto legible en las listas", () => {
  assert.equal(exerciseTitle(index.exercises.get("poo-11")), "Ejercicio guiado: la clase `Alumno`");
  assert.equal(exerciseTitle(index.exercises.get("poo-03")), index.exercises.get("poo-03").q);
});
