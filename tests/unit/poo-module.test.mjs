// Módulo de POO: estructura del índice, lecciones completadas en el progreso y vistas.
import assert from "node:assert/strict";
import { test } from "node:test";
import { allStats, cleanLearning, markSection, mergeLearning, recordAttempt, sectionsDone } from "../../frontend/js/learn/mastery.js";
import { availableUnits, exerciseTitle, pooModule, renderModule, unitBody, unitExercises, unitToc } from "../../frontend/js/learn/poo-view.js";
import { errorsTested, grade } from "../../frontend/js/learn/answers.js";
import { feedbackHtml } from "../../frontend/js/learn/ui.js";
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
  assert.match(module, /Las 10 unidades están publicadas/);
  assert.doesNotMatch(module, /En preparación/);
  assert.match(module, /href="#\/teoria\/poo"/);
  assert.match(module, /Completar lecciones no equivale a dominar/);
  // Una unidad sin publicar sale «en preparación», sin enlace, y el recuento lo dice
  const pending = structuredClone(pooModule(index));
  pending.units[9].available = false;
  const partial = { ...index, data: { ...index.data, modules: [pending] } };
  const html2 = renderModule(partial, state, NOW);
  assert.match(html2, /9 de 10 unidades publicadas/);
  assert.match(html2, /En preparación/);
  assert.doesNotMatch(html2, /href="#\/teoria\/poo-proyecto"/);
});

test("los ejercicios de la unidad tienen un título corto legible en las listas", () => {
  assert.equal(exerciseTitle(index.exercises.get("poo-11")), "Ejercicio guiado: la clase `Alumno`");
  assert.equal(exerciseTitle(index.exercises.get("poo-03")), index.exercises.get("poo-03").q);
});

test("cada unidad publicada muestra sus buenas prácticas, el cuestionario de 15, las prácticas adicionales y sus referencias", () => {
  for (const { id } of availableUnits(index)) {
    const unit = index.concepts.get(id);
    const html = unitBody(index, fresh(), unit, allStats(index, fresh(), NOW).get(id));
    const toc = unitToc(unit).map(([anchor]) => anchor);
    for (const anchor of ["lx-practices", "lx-bank", "lx-references"]) {
      assert.ok(toc.includes(anchor), `${id}: falta ${anchor} en el índice`);
      assert.ok(html.includes(`id="${anchor}"`), `${id}: falta la sección ${anchor}`);
    }
    assert.equal(unitExercises(unit, { group: "bank" }).length, 15);
    assert.ok(html.includes('data-group="bank"'), `${id}: el cuestionario se puede empezar`);
    if (unit.extras?.length) assert.ok(html.includes('data-group="extras"'), `${id}: prácticas adicionales`);
    // Ninguna referencia sin comprobar se presenta como comprobada
    const pending = unit.references.filter((r) => r.status === "pending").length;
    assert.equal(html.split("Pendiente de comprobación</span>").length - 1, pending);
  }
});

test("al fallar una pregunta del banco, la corrección explica por qué la opción elegida es incorrecta", () => {
  const q = index.exercises.get("poo1-15");
  const wrong = q.options.findIndex((_, i) => i !== q.answer);
  const result = grade(q, { choice: wrong });
  assert.equal(result.ok, false);
  assert.equal(result.why, q.options[wrong].why);
  assert.ok(feedbackHtml(q, result).includes("Por qué tu opción no es correcta"));
  assert.ok(!feedbackHtml(q, grade(q, { choice: q.answer })).includes("Por qué tu opción no es correcta"));
});

test("el proyecto final muestra el diagrama de clases accesible, la rúbrica y los retos", () => {
  const project = index.concepts.get("poo-proyecto");
  const toc = unitToc(project).map(([id]) => id);
  for (const id of ["lx-diagram", "lx-rubric", "lx-challenges"]) assert.ok(toc.includes(id), id);
  // El diagrama va después del ejemplo y la rúbrica después del ejercicio principal
  assert.ok(toc.indexOf("lx-diagram") > toc.indexOf("lx-example"));
  assert.ok(toc.indexOf("lx-rubric") > toc.indexOf("lx-autonomous"));
  const html = unitBody(index, fresh(), project, allStats(index, fresh(), NOW).get("poo-proyecto"));
  // SVG como imagen con título y descripción, y las relaciones también en texto
  assert.match(html, /<svg class="lx-uml__svg"[^>]*role="img" aria-labelledby="lx-uml-title lx-uml-desc"/);
  assert.match(html, /<title id="lx-uml-title">Diagrama de clases del proyecto biblioteca<\/title>/);
  assert.equal((html.match(/<g class="lx-uml__class">/g) ?? []).length, project.diagram.classes.length);
  assert.equal((html.match(/<line class="lx-uml__rel"/g) ?? []).length, project.diagram.relations.length);
  assert.match(html, /data-kind="composicion"[^>]*marker-start="url\(#lx-uml-filled\)"/);
  assert.match(html, /data-kind="agregacion"[^>]*marker-start="url\(#lx-uml-hollow\)"/);
  assert.match(html, /Biblioteca → Prestamo<\/strong> \(composición\)/);
  assert.match(html, /sobre 100 puntos/);
  assert.equal((html.match(/data-label="Puntos"/g) ?? []).length, project.rubric.length);
  assert.ok(html.includes("Multas por retraso"));
  // Las unidades sin estos apartados no los muestran
  const unit2Toc = unitToc(unit2).map(([id]) => id);
  for (const id of ["lx-diagram", "lx-rubric", "lx-challenges"]) assert.equal(unit2Toc.includes(id), false);
});

test("el diagrama escapa los nombres de las clases", () => {
  const diagram = {
    title: "T",
    summary: "S",
    classes: [
      { id: "a", name: "<img src=x>", col: 0, row: 0, members: ["<b>"] },
      { id: "b", name: "B", col: 1, row: 0, members: [] },
    ],
    relations: [{ from: "a", to: "b", kind: "asociacion", text: "rel" }],
  };
  const html = unitBody(index, fresh(), { ...index.concepts.get("poo-proyecto"), diagram }, allStats(index, fresh(), NOW).get("poo-proyecto"));
  assert.equal(html.includes("<img src=x>"), false);
  assert.ok(html.includes("&lt;img src=x&gt;"));
});
