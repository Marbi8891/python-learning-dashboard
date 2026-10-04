import assert from "node:assert/strict";
import { test } from "node:test";
import { buildExam, competencyAdvice, competencyStats, examByCompetency, examMinutes, examReadiness } from "../../frontend/js/learn/exam.js";
import { allStats, markRead, recordAttempt } from "../../frontend/js/learn/mastery.js";
import { exercisesOf, fresh, index, NOW, seeded } from "./helpers.mjs";

const master = (state, concept) => {
  for (const e of exercisesOf(concept)) recordAttempt(state, e, { ok: true, error: null }, { now: NOW });
};

test("las competencias de DAW cubren todos los conceptos salvo POO y sus pesos suman 100", () => {
  const ids = index.data.daw.flatMap((c) => c.concepts);
  assert.equal(new Set(ids).size, ids.length);
  assert.deepEqual([...ids].sort(), index.path.filter((id) => id !== "poo").sort());
  assert.equal(index.data.daw.reduce((s, c) => s + c.weight, 0), 100);
});

test("competencyStats: dominio ponderado y conceptos más flojos", () => {
  const state = fresh();
  master(state, "variables");
  master(state, "tipos");
  const [fund] = competencyStats(index, null, state);
  assert.equal(fund.mastered, 2);
  assert.ok(fund.score > 0 && fund.score < 1);
  assert.equal(fund.weakest.length, 2);
  assert.ok(!fund.weakest.includes("variables"));
  assert.equal(fund.started, true);
});

test("competencyAdvice: con Fundamentos flojo, pide reforzarlo antes de Programación y de Lógica", () => {
  const state = fresh();
  master(state, "variables");
  recordAttempt(state, exercisesOf("funciones")[0], { ok: true, error: null }, { now: NOW });
  const advice = competencyAdvice(index, competencyStats(index, allStats(index, state, NOW)));
  assert.deepEqual(advice.map((a) => a.before), ["programacion", "logica"]);
  assert.deepEqual(advice[0].concepts, competencyStats(index, allStats(index, state, NOW))[0].weakest);
  assert.match(advice[0].text, /^Necesitas reforzar .+ antes de pasar a Programación\.$/);
});

test("competencyAdvice: sin avisos cuando la base está firme (ni antes de empezar)", () => {
  assert.deepEqual(competencyAdvice(index, competencyStats(index, null, fresh())), []);
  const state = fresh();
  for (const id of index.data.daw[0].concepts) master(state, id);
  recordAttempt(state, exercisesOf("funciones")[0], { ok: false, error: null }, { now: NOW });
  const comps = competencyStats(index, allStats(index, state, NOW));
  assert.ok(comps[0].score >= 0.99);
  assert.deepEqual(competencyAdvice(index, comps), []);
  assert.ok(examReadiness(comps) > 0.3);
});

test("buildExam (todo el temario): tamaño, sin repetidos, reparto por competencias y 1-2 problemas de código", () => {
  for (let seed = 1; seed <= 20; seed += 1) {
    const exam = buildExam(index, fresh(), { scope: "all", size: 12, random: seeded(seed) });
    assert.equal(exam.length, 12);
    assert.equal(new Set(exam.map((e) => e.id)).size, 12);
    assert.ok(exam.every((e) => e.daw));
    const code = exam.filter((e) => e.kind === "code").length;
    assert.ok(code >= 1 && code <= 2, `seed ${seed}: ${code} problemas de código`);
    for (const competency of index.data.daw) {
      const n = exam.filter((e) => competency.concepts.includes(e.concept)).length;
      assert.ok(n >= 2, `seed ${seed}: ${competency.id} tiene ${n}`);
    }
    assert.deepEqual(exam.map((e) => e.level), [...exam.map((e) => e.level)].sort(), "de sencillo a completo");
  }
});

test("buildExam (lo estudiado): solo conceptos empezados o leídos; vacío si no hay ninguno", () => {
  assert.deepEqual(buildExam(index, fresh(), { scope: "studied" }), []);
  const state = fresh();
  markRead(state, "bucles", NOW);
  recordAttempt(state, exercisesOf("condicionales")[0], { ok: true, error: null }, { now: NOW });
  const exam = buildExam(index, state, { scope: "studied", random: seeded(4) });
  assert.ok(exam.length > 0);
  assert.ok(exam.every((e) => ["bucles", "condicionales"].includes(e.concept)));
});

test("examMinutes y examByCompetency", () => {
  assert.equal(examMinutes([{ kind: "code" }, { kind: "output" }, { kind: "choice" }]), 16);
  const byComp = examByCompetency(index, { concepts: { bucles: [1, 2], funciones: [0, 1], trazado: [2, 2] } });
  assert.deepEqual(
    byComp.map((c) => [c.id, c.ok, c.total]),
    [["fundamentos", 1, 2], ["programacion", 0, 1], ["logica", 2, 2]],
  );
});

test("prueba de nivel: un ejercicio rápido por concepto, sin código ni POO", async () => {
  const { buildDiagnostic } = await import("../../frontend/js/learn/exam.js");
  const list = buildDiagnostic(index, { random: seeded(2) });
  assert.equal(list.length, index.path.length - 1);
  assert.deepEqual(list.map((e) => e.concept), index.path.filter((id) => id !== "poo"));
  assert.ok(list.every((e) => e.kind !== "code" && e.kind !== "order"));
});
