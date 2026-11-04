import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import {
  cleanCareer,
  cleanRepoUrl,
  emptyCareer,
  emptySignals,
  enroll,
  mergeCareer,
  overview,
  phaseStates,
  projectProgress,
  saveProject,
  setMonths,
  setUnitDone,
  skillMastery,
} from "../../frontend/js/career/career-data.js";

const read = (name) => JSON.parse(readFileSync(new URL(`../../frontend/data/career/${name}`, import.meta.url), "utf8"));
const index = read("index.json");
const roadmap = read("python-backend-junior.json");
const RM = roadmap.id;
const NOW = new Date("2026-11-05T10:00:00Z");
const later = (minutes) => new Date(NOW.getTime() + minutes * 60_000);
const copy = (value) => JSON.parse(JSON.stringify(value));
const phase = (id) => roadmap.phases.find((p) => p.id === id);
const project = (id) => roadmap.projects.find((p) => p.id === id);
const skill = (id) => roadmap.skills.find((s) => s.id === id);

/** Señales con todo lo de estas competencias dominado (o con el dominio y la evidencia que se pidan). */
function signalsFor(skillIds, { score = 1, confidence = 1, forgotten = false, rate = 1, answered = 20, total = 20 } = {}) {
  const signals = emptySignals();
  for (const id of skillIds) {
    for (const c of skill(id).sources.concepts) signals.concepts.set(c, { score, confidence, forgotten });
    for (const b of skill(id).sources.blocks) signals.blocks.set(b, { rate, answered, total });
  }
  return signals;
}

/** Estudia todas las unidades de la fase y entrega su proyecto completo. */
function finishPhase(doc, id) {
  for (const unit of phase(id).units) setUnitDone(doc, RM, unit.id, true, NOW);
  const p = phase(id).project && project(phase(id).project);
  if (p) saveProject(doc, RM, p, { repo: "https://github.com/alumno/proyecto", checks: Object.fromEntries(p.criteria.map((c) => [c.id, true])) }, NOW);
}

test("career: el catálogo generado tiene el itinerario Backend Junior con 8 fases", () => {
  assert.equal(index.default, RM);
  assert.deepEqual(index.roadmaps.map((r) => r.id), [RM]);
  assert.equal(roadmap.phases.length, 8);
  assert.equal(roadmap.months, 8);
  for (const p of roadmap.phases) for (const req of p.requires) assert.ok(phase(req), `${p.id} → ${req}`);
});

test("career: cleanCareer descarta datos no válidos y conserva los campos que no conoce", () => {
  assert.deepEqual(cleanCareer(null), emptyCareer());
  assert.deepEqual(cleanCareer([1, 2]), emptyCareer());
  const doc = cleanCareer({
    v: 1,
    futuro: { x: 1 },
    active: RM,
    roadmaps: {
      [RM]: {
        enrolledAt: "2026-11-01T09:00:00.000Z",
        months: 99,
        extra: true,
        units: { "fund-control": { done: true, at: "2026-11-02T09:00:00.000Z" }, "MAL ID": { done: true, at: "2026-11-02T09:00:00.000Z" }, "fund-poo": { done: "sí", at: "x" } },
        projects: { "mini-proyecto": { repo: "javascript:alert(1)", checks: { clases: true, colecciones: "sí" }, at: "2026-11-03T09:00:00.000Z" } },
      },
      "sin-fecha": { units: {} },
      "../malo": { enrolledAt: "2026-11-01T09:00:00.000Z" },
    },
  });
  assert.deepEqual(doc.futuro, { x: 1 }, "campos de versiones futuras");
  assert.deepEqual(Object.keys(doc.roadmaps), [RM]);
  const rm = doc.roadmaps[RM];
  assert.equal(rm.extra, true);
  assert.equal(rm.months, null, "fuera de 1-36: la del itinerario");
  assert.deepEqual(Object.keys(rm.units), ["fund-control"]);
  assert.deepEqual(rm.projects["mini-proyecto"], { repo: "", checks: { clases: true }, at: "2026-11-03T09:00:00.000Z" });
  assert.equal(doc.active, RM);
  assert.equal(cleanCareer({ active: "otro", roadmaps: {} }).active, null, "activo que no existe");
});

test("career: solo se aceptan enlaces https sin credenciales", () => {
  assert.equal(cleanRepoUrl("https://github.com/alumno/api"), "https://github.com/alumno/api");
  for (const bad of ["http://github.com/a", "javascript:alert(1)", "https://usuario:clave@github.com/a", "https://localhost/x", "github.com/a", `https://a.com/${"x".repeat(400)}`, 42]) {
    assert.equal(cleanRepoUrl(bad), "", String(bad));
  }
});

test("career: enroll conserva el progreso y setMonths solo admite 1-36 meses", () => {
  const doc = emptyCareer();
  enroll(doc, RM, NOW);
  setUnitDone(doc, RM, "fund-control", true, NOW);
  enroll(doc, RM, later(5));
  assert.equal(doc.roadmaps[RM].units["fund-control"].done, true);
  assert.equal(doc.roadmaps[RM].enrolledAt, NOW.toISOString());
  setMonths(doc, RM, 12, NOW);
  assert.equal(doc.roadmaps[RM].months, 12);
  setMonths(doc, RM, 0, NOW);
  assert.equal(doc.roadmaps[RM].months, null);
  assert.throws(() => enroll(doc, "../x", NOW));
});

test("career: la fusión entre dispositivos gana lo cambiado más tarde y no pierde nada", () => {
  const a = emptyCareer();
  enroll(a, RM, NOW);
  setUnitDone(a, RM, "fund-control", true, NOW);
  setUnitDone(a, RM, "fund-funciones", true, later(10));
  const b = copy(a);
  setUnitDone(b, RM, "fund-control", false, later(20)); // desmarcada más tarde en el otro dispositivo
  setUnitDone(b, RM, "fund-funciones", false, later(1)); // desmarcada antes que el «hecha» de a
  setUnitDone(b, RM, "fund-poo", true, later(2));
  b.futuro = 1;
  mergeCareer(a, b);
  const units = a.roadmaps[RM].units;
  assert.equal(units["fund-control"].done, false);
  assert.equal(units["fund-funciones"].done, true);
  assert.equal(units["fund-poo"].done, true);
  assert.equal(a.futuro, 1);
  const c = emptyCareer();
  mergeCareer(c, a);
  assert.deepEqual(c.roadmaps, a.roadmaps, "un documento vacío recibe todo");
});

test("career: el bloqueo depende de los prerrequisitos, no de la posición", () => {
  const doc = emptyCareer();
  const enrollment = enroll(doc, RM, NOW);
  let { phases } = phaseStates(roadmap, enrollment);
  assert.equal(phases.get("fundamentals").status, "available");
  for (const id of ["professional-python", "databases", "frontend", "backend", "career"]) assert.equal(phases.get(id).status, "locked", id);
  assert.deepEqual(phases.get("backend").missing, ["professional-python", "databases"]);

  finishPhase(doc, "fundamentals");
  ({ phases } = phaseStates(roadmap, enrollment, signalsFor(phase("fundamentals").skills)));
  assert.equal(phases.get("fundamentals").status, "completed");
  for (const id of ["professional-python", "databases", "frontend"]) assert.equal(phases.get(id).status, "available", id);
  // Frontend (6.ª) está disponible aunque Backend (4.ª) siga bloqueada
  assert.equal(phases.get("backend").status, "locked");
  assert.equal(phases.get("testing").status, "locked");
});

test("career: completar el contenido no es dominar (needs_review sin evidencias)", () => {
  const doc = emptyCareer();
  const enrollment = enroll(doc, RM, NOW);
  finishPhase(doc, "fundamentals");
  const { phases, skills } = phaseStates(roadmap, enrollment);
  const fundamentals = phases.get("fundamentals");
  assert.equal(fundamentals.percent, 100, "todo el contenido estudiado");
  assert.equal(fundamentals.status, "needs_review", "pero sin evidencias de dominio");
  assert.ok(fundamentals.weak.includes("py-basics"));
  assert.equal(skills.get("py-basics").percent, 0);
  // needs_review cuenta como prerrequisito cumplido: no se bloquea lo siguiente por olvidar
  assert.equal(phases.get("databases").status, "available");
});

test("career: una competencia que se olvida pasa la fase a needs_review", () => {
  const doc = emptyCareer();
  const enrollment = enroll(doc, RM, NOW);
  finishPhase(doc, "fundamentals");
  const forgetting = signalsFor(phase("fundamentals").skills);
  forgetting.concepts.set("bucles", { score: 0.9, confidence: 1, forgotten: true });
  const { phases, skills } = phaseStates(roadmap, enrollment, forgetting);
  assert.equal(skills.get("py-basics").forgotten, true);
  assert.equal(skills.get("py-basics").ready, false);
  assert.equal(phases.get("fundamentals").status, "needs_review");
});

test("career: dominio de una competencia = valor × evidencia de cada fuente", () => {
  const s = skill("py-basics"); // 6 conceptos y 2 bloques
  const none = skillMastery(s, { roadmap, enrollment: null });
  assert.deepEqual([none.percent, none.confidence, none.level, none.enough], [0, 0, 0, false]);

  const full = skillMastery(s, { roadmap, enrollment: null, signals: signalsFor(["py-basics"]) });
  assert.deepEqual([full.percent, full.confidence, full.level, full.ready], [100, 1, 3, true]);

  // Mucho acierto con poca evidencia: no se da por firme
  const thin = skillMastery(s, { roadmap, enrollment: null, signals: signalsFor(["py-basics"], { confidence: 0.2, answered: 1 }) });
  assert.equal(thin.enough, false);
  assert.equal(thin.ready, false);
  assert.ok(thin.percent < 30);

  // Un bloque con la mitad de sus preguntas respondidas ya cuenta entero (como la preparación del PCAP)
  const half = skillMastery(skill("sql-queries"), { roadmap, enrollment: null, signals: signalsFor(["sql-queries"], { rate: 0.7, answered: 10, total: 20 }) });
  assert.equal(half.percent, 70);
  assert.equal(half.level, 2);
  assert.ok(half.ready);

  // Las fuentes que faltan cuentan como 0: la mitad de las fuentes perfectas = 50 %
  const partial = emptySignals();
  for (const c of s.sources.concepts.slice(0, 4)) partial.concepts.set(c, { score: 1, confidence: 1 });
  assert.equal(skillMastery(s, { roadmap, enrollment: null, signals: partial }).percent, 50);
});

test("career: un proyecto cuenta como evidencia solo con enlace y criterios cumplidos", () => {
  const doc = emptyCareer();
  const enrollment = enroll(doc, RM, NOW);
  const api = project("api-rest");
  saveProject(doc, RM, api, { repo: "", checks: { crud: true, inventado: true } }, NOW);
  assert.deepEqual(enrollment.projects["api-rest"].checks, { crud: true }, "criterios que no existen se ignoran");
  assert.equal(skillMastery(skill("fastapi"), { roadmap, enrollment }).confidence, 0, "sin enlace no hay evidencia");
  saveProject(doc, RM, api, { repo: "https://github.com/alumno/api", checks: { crud: true, auth: true } }, NOW);
  const progress = projectProgress(api, enrollment.projects["api-rest"]);
  assert.deepEqual([progress.done, progress.total, progress.delivered], [2, 5, false]);
  const fastapi = skillMastery(skill("fastapi"), { roadmap, enrollment });
  assert.equal(fastapi.percent, 40);
  assert.equal(fastapi.sources[0].selfAssessed, true, "se marca como autoevaluación");
});

test("career: resumen y siguiente actividad deterministas", () => {
  const doc = emptyCareer();
  const enrollment = enroll(doc, RM, NOW);
  const start = overview(roadmap, enrollment);
  assert.equal(start.active, "fundamentals");
  assert.deepEqual(start.next, { kind: "unit", phase: "fundamentals", id: phase("fundamentals").units[0].id, reason: "next-unit" });
  assert.equal(start.percent, 0);
  assert.deepEqual(overview(roadmap, enrollment), start, "mismos datos, mismo resultado");

  for (const unit of phase("fundamentals").units) setUnitDone(doc, RM, unit.id, true, NOW);
  assert.deepEqual(overview(roadmap, enrollment).next, { kind: "project", phase: "fundamentals", id: "mini-proyecto", reason: "project-pending" });

  finishPhase(doc, "fundamentals");
  const weak = signalsFor(phase("fundamentals").skills);
  weak.concepts.set("poo", { score: 0.1, confidence: 1 });
  for (const b of skill("py-oop").sources.blocks) weak.blocks.set(b, { rate: 0.1, answered: 20, total: 20 });
  const review = overview(roadmap, enrollment, weak);
  assert.equal(review.active, "fundamentals");
  assert.deepEqual(review.next, { kind: "skill", phase: "fundamentals", id: "py-oop", reason: "skill-weak" });

  const done = overview(roadmap, enrollment, signalsFor(phase("fundamentals").skills));
  assert.deepEqual(done.completed, ["fundamentals"]);
  assert.equal(done.active, "professional-python", "la primera disponible por orden");
  assert.ok(done.percent > 0 && done.percent < 100);
});
