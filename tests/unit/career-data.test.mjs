import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import {
  addEvidence,
  allSkillStats,
  blockScore,
  cleanCareer,
  criterionMet,
  dawPriority,
  emptyCareer,
  enroll,
  explainSkill,
  indexRoadmap,
  LIMITS,
  logStudy,
  mergeCareer,
  moduleStatuses,
  nextActivities,
  recordAssessment,
  removeEvidence,
  removeStudy,
  roleCoverage,
  safeHttpsUrl,
  setChecklistItem,
  setCriterion,
  setStage,
  setUnitStatus,
  skillStats,
  skillSummary,
  stagePlan,
  studyTotals,
} from "../../frontend/js/career/career-data.js";
import { allStats, recordAttempt } from "../../frontend/js/learn/mastery.js";
import { exercisesOf, fresh, index as learnIndex } from "./helpers.mjs";

const ROADMAP = JSON.parse(readFileSync(new URL("../../frontend/data/career/applied-ai-engineer.json", import.meta.url), "utf8"));
const index = indexRoadmap(ROADMAP);
const NOW = new Date("2026-11-18T10:00:00");
const RID = "applied-ai-engineer";
const copy = (value) => JSON.parse(JSON.stringify(value));
const at = (iso) => new Date(iso);

function start(now = NOW) {
  const doc = emptyCareer();
  return { doc, progress: enroll(doc, RID, now) };
}

/** Estadísticas de concepto con la forma de conceptStats (solo los campos que se leen). */
const concept = (score, extra = {}) => ({ score, attempted: score > 0 ? 4 : 0, forgotten: false, ...extra });
const statsOf = (progress, inputs = {}, now = NOW) => allSkillStats(index, progress, inputs, now);

/* ---------- Leer no es dominar ---------- */

test("estudiar todas las unidades no sube ninguna competencia ni completa ningún módulo", () => {
  const { progress } = start();
  for (const unit of index.units.keys()) setUnitStatus(progress, unit, "hecha", NOW);
  const skills = statsOf(progress);
  for (const s of skills.values()) {
    assert.equal(s.score, 0, s.id);
    assert.equal(s.status, "sin-evidencias", s.id);
  }
  const modules = moduleStatuses(index, progress, skills, NOW);
  for (const m of modules.values()) assert.equal(m.completed, false, m.id);
  assert.match(explainSkill(skills.get("py-oop")), /estudiar las unidades no basta/);
  assert.deepEqual(skillSummary(skills).acquired, []);
});

/* ---------- Dominio de una competencia ---------- */

test("una competencia agrega práctica, evaluación y proyecto con sus pesos", () => {
  const { progress } = start();
  const inputs = { concepts: new Map([["poo", concept(1)]]), blocks: new Map() };
  // práctica: poo = 1 y tres bloques sin datos = 0 → 0,25
  let s = skillStats(index, progress, "py-oop", inputs, NOW);
  assert.equal(s.groups.practice.value, 0.25);
  assert.equal(s.status, "insuficiente", "solo una de tres fuentes con datos");

  recordAssessment(progress, "m1", 0.9, NOW);
  s = skillStats(index, progress, "py-oop", inputs, NOW);
  assert.ok(Math.abs(s.score - (0.3 * 0.25 + 0.4 * 0.9) / 1) < 1e-9);
  assert.equal(s.enough, true);
  assert.equal(s.status, "progreso");
});

test("un criterio de proyecto solo cuenta marcado y con una evidencia viva", () => {
  const { progress } = start();
  setCriterion(progress, "npa-servicio-tests", true, NOW);
  assert.equal(criterionMet(progress, "npa-servicio-tests"), false, "marcado sin evidencia");
  const ev = addEvidence(progress, { project: "nexaro-personal-ai", criterion: "npa-servicio-tests", kind: "pr", url: "https://github.com/x/y/pull/3" }, NOW);
  assert.equal(criterionMet(progress, "npa-servicio-tests"), true);
  removeEvidence(progress, ev.id, NOW);
  assert.equal(criterionMet(progress, "npa-servicio-tests"), false, "evidencia borrada");
});

test("adquirida exige dominio, evidencias suficientes y, si la pide, demostración en un proyecto", () => {
  const { progress } = start();
  const blocks = new Map(["programacion:prog-ut4", "programacion:prog-ut5", "programacion:prog-ut6"].map((b) => [b, { answered: 10, total: 10, rate: 1 }]));
  const inputs = { concepts: new Map([["poo", concept(1)]]), blocks };
  recordAssessment(progress, "m1", 1, NOW);
  let s = skillStats(index, progress, "py-oop", inputs, NOW);
  assert.equal(s.score, 0.7);
  assert.equal(s.status, "progreso", "sin proyecto no está adquirida aunque llegue al 70 %");

  setCriterion(progress, "npa-servicio-tests", true, NOW);
  addEvidence(progress, { project: "nexaro-personal-ai", criterion: "npa-servicio-tests", kind: "tests", note: "tests del servicio de memoria" }, NOW);
  s = skillStats(index, progress, "py-oop", inputs, NOW);
  assert.equal(s.score, 1);
  assert.equal(s.status, "adquirida");
  assert.deepEqual(skillSummary(new Map([["py-oop", s]])).acquired, ["py-oop"]);

  // Con el concepto olvidado o la evaluación caducada, toca repasar
  inputs.concepts.set("poo", concept(1, { forgotten: true }));
  assert.equal(skillStats(index, progress, "py-oop", inputs, NOW).status, "repasar");
});

test("una evaluación de hace más de 180 días marca repaso", () => {
  const { progress } = start();
  recordAssessment(progress, "m3", 1, at("2026-01-01T10:00:00"));
  const s = skillStats(index, progress, "ml-foundations", {}, NOW);
  assert.equal(s.review, true);
  assert.equal(s.status, "repasar");
  assert.match(explainSkill(s), /toca repasar/);
});

test("la puntuación de un bloque usa la cobertura de los cursos de DAW", () => {
  assert.equal(blockScore(undefined), 0);
  assert.equal(blockScore({ answered: 0, total: 10, rate: null }), 0);
  assert.equal(blockScore({ answered: 5, total: 10, rate: 1 }), 1, "con la mitad respondida, cobertura completa");
  assert.equal(blockScore({ answered: 2, total: 10, rate: 0.5 }), 0.2);
});

test("reutiliza el dominio real del motor adaptativo 2.0 (mastery.js)", () => {
  const learning = fresh();
  for (const e of exercisesOf("poo")) recordAttempt(learning, e, { ok: true, error: null }, { now: NOW });
  const concepts = allStats(learnIndex, learning, NOW);
  const { progress } = start();
  const s = skillStats(index, progress, "py-oop", { concepts }, NOW);
  assert.ok(s.groups.practice.value > 0 && s.groups.practice.data);
  assert.equal(s.groups.practice.value, concepts.get("poo").score / 4);
});

test("las listas de comprobación cuentan como proyecto en las competencias profesionales", () => {
  const { progress } = start();
  for (const item of index.checklists.get("portfolio")) setChecklistItem(progress, item.id, true, NOW);
  recordAssessment(progress, "m8", 0.8, NOW);
  const s = skillStats(index, progress, "portfolio-presence", {}, NOW);
  assert.equal(s.groups.project.value, 1);
  assert.equal(s.status, "adquirida");
});

/* ---------- Módulos: prerrequisitos y estados ---------- */

test("al empezar, M1, M8 están disponibles y los demás bloqueados por sus prerrequisitos", () => {
  const { progress } = start();
  const modules = moduleStatuses(index, progress, statsOf(progress), NOW);
  assert.equal(modules.get("m1").status, "disponible");
  assert.equal(modules.get("m8").status, "disponible", "no depende de su posición en la ruta");
  assert.equal(modules.get("m2").status, "bloqueado");
  assert.deepEqual(modules.get("m4").missing, ["m1", "m3"]);
});

test("un módulo se desbloquea cuando la base está lista aunque no esté completada", () => {
  const { progress } = start();
  // Python fuerte (base de M2 y M3) pero IA floja: M4 sigue bloqueado por M3
  const concepts = new Map(["poo", "tipos", "listas", "tuplas-conjuntos", "diccionarios", "excepciones", "validacion", "modulos", "funciones", "depuracion", "archivos", "recorridos"].map((c) => [c, concept(1)]));
  recordAssessment(progress, "m1", 0.85, NOW);
  const skills = statsOf(progress, { concepts });
  const modules = moduleStatuses(index, progress, skills, NOW);
  assert.equal(modules.get("m2").status, "disponible");
  assert.equal(modules.get("m3").status, "disponible");
  assert.equal(modules.get("m4").status, "bloqueado");
  assert.deepEqual(modules.get("m4").missing, ["m3"]);
});

test("completado = unidades + evaluación aprobada + proyecto; empezado = en curso", () => {
  const { progress } = start();
  const m3 = index.modules.get("m3");
  setUnitStatus(progress, m3.units[0].id, "hecha", NOW);
  let modules = moduleStatuses(index, progress, statsOf(progress), NOW);
  assert.equal(modules.get("m3").status, "en-curso", "un bloqueado empezado se ve en curso");

  for (const u of m3.units) setUnitStatus(progress, u.id, "hecha", NOW);
  recordAssessment(progress, "m3", 0.6, NOW);
  modules = moduleStatuses(index, progress, statsOf(progress), NOW);
  assert.equal(modules.get("m3").assessment.passed, false, "0,6 < aprobado 0,7");
  recordAssessment(progress, "m3", 0.8, NOW);
  setCriterion(progress, "npa-comparativa-modelos", true, NOW);
  addEvidence(progress, { project: "nexaro-personal-ai", criterion: "npa-comparativa-modelos", kind: "result", note: "qwen2.5:3b frente a llama3.2:3b" }, NOW);
  modules = moduleStatuses(index, progress, statsOf(progress), NOW);
  assert.equal(modules.get("m3").completed, true);
  assert.equal(modules.get("m3").status, "completado");
  assert.equal(moduleStatuses(index, progress, statsOf(progress, {}, at("2027-08-01T10:00:00")), at("2027-08-01T10:00:00")).get("m3").status, "repasar");
});

test("M8 se completa con las listas de portfolio y negocio", () => {
  const { progress } = start();
  const m8 = index.modules.get("m8");
  for (const u of m8.units) setUnitStatus(progress, u.id, "hecha", NOW);
  recordAssessment(progress, "m8", 0.9, NOW);
  for (const item of index.checklists.get("portfolio")) setChecklistItem(progress, item.id, true, NOW);
  assert.equal(moduleStatuses(index, progress, statsOf(progress), NOW).get("m8").completed, false, "falta la propuesta comercial");
  for (const item of index.checklists.get("business")) setChecklistItem(progress, item.id, true, NOW);
  assert.equal(moduleStatuses(index, progress, statsOf(progress), NOW).get("m8").completed, true);
});

/* ---------- Puestos ---------- */

test("cobertura de puestos: ordenada y con lo que falta, de mayor a menor distancia", () => {
  const { progress } = start();
  const skills = statsOf(progress);
  const roles = roleCoverage(index, skills);
  assert.equal(roles.length, ROADMAP.roles.length);
  assert.ok(roles.every((r) => r.coverage === 0 && !r.ready));
  const fake = new Map([...skills].map(([id, s]) => [id, { ...s, score: 1 }]));
  fake.set("sql", { score: 0.3 });
  const junior = roleCoverage(index, fake).find((r) => r.id === "python-backend-developer");
  assert.deepEqual(junior.missing.map((m) => m.id), ["sql"]);
  assert.equal(junior.band, "junior");
  assert.equal(roleCoverage(index, fake)[0].coverage, 1);
});

/* ---------- Plan de 36 meses ---------- */

test("plan: seis etapas encadenadas que suman 36 meses y se pueden mover y alargar", () => {
  const { progress } = start(at("2026-12-01T10:00:00"));
  let plan = stagePlan(index, progress, NOW);
  assert.equal(plan.length, 6);
  assert.equal(plan[0].start, "2026-12-01");
  assert.equal(plan.at(-1).end, "2029-12-01");
  assert.equal(plan[0].current, false, "aún no ha empezado");

  setStage(progress, "s1", { months: 9 }, NOW); // DAW se alarga
  plan = stagePlan(index, progress, NOW);
  assert.equal(plan[1].start, "2027-09-01", "las siguientes se desplazan");
  assert.equal(plan.at(-1).end, "2030-03-01");
  setStage(progress, "s3", { start: "2028-06-01" }, NOW);
  plan = stagePlan(index, progress, NOW);
  assert.equal(plan[2].start, "2028-06-01");
  assert.equal(plan[3].start, "2028-12-01");
  assert.equal(stagePlan(index, progress, at("2027-01-10T10:00:00"))[0].current, true);

  setStage(progress, "s1", { months: 99 }, NOW); // fuera de rango: vuelve al catálogo
  assert.equal(stagePlan(index, progress, NOW)[0].months, 6);
});

test("plan: un fin de mes se ajusta al último día del mes de destino", () => {
  const { progress } = start(at("2027-08-31T10:00:00"));
  assert.equal(stagePlan(index, progress, NOW)[0].end, "2028-02-29");
});

/* ---------- Siguiente actividad y prioridad de DAW ---------- */

const plannerExam = (days) => ({ id: `ex-${days}`, title: "Programación", date: "2026-12-01", kind: "examen", days });

test("con un examen o entrega de DAW a 7 días o menos, la ruta no propone nada", () => {
  const { progress } = start();
  const skills = statsOf(progress);
  const modules = moduleStatuses(index, progress, skills, NOW);
  const paused = nextActivities(index, progress, { skills, modules, exams: [plannerExam(20), plannerExam(5)], now: NOW });
  assert.equal(paused.paused.days, 5);
  assert.deepEqual(paused.items, []);
  assert.equal(dawPriority([plannerExam(8)]), null);
  assert.equal(dawPriority([{ ...plannerExam(2), deleted: true }]), null);
  const free = nextActivities(index, progress, { skills, modules, exams: [plannerExam(8)], now: NOW });
  assert.equal(free.paused, null);
  assert.ok(free.items.length > 0);
});

test("siguiente actividad: la etapa actual primero, sin módulos bloqueados, y cada una con su motivo", () => {
  const { progress } = start(at("2026-11-01T10:00:00"));
  const skills = statsOf(progress);
  const modules = moduleStatuses(index, progress, skills, NOW);
  const { items } = nextActivities(index, progress, { skills, modules, now: NOW, limit: 10 });
  assert.deepEqual(items.slice(0, 2).map((i) => [i.kind, i.module, i.unit ?? i.criterion]), [
    ["unit", "m1", "m1.poo"],
    ["criterion", "m1", "npa-servicio-tests"],
  ]);
  assert.ok(items.every((i) => i.why && !["m2", "m3", "m4"].includes(i.module)), "M2-M4 están bloqueados");
  assert.ok(items.some((i) => i.module === "m8"), "M8 está en la etapa 1");
});

test("una unidad estudiada cuyo concepto no llega a READY_SCORE propone practicarlo", () => {
  const { progress } = start();
  setUnitStatus(progress, "m1.poo", "hecha", NOW);
  const inputs = { concepts: new Map([["poo", concept(0.3)]]) };
  const skills = statsOf(progress, inputs);
  const modules = moduleStatuses(index, progress, skills, NOW);
  const [first, second] = nextActivities(index, progress, { skills, modules, inputs, now: NOW }).items;
  assert.equal(first.kind, "practice");
  assert.equal(first.concept, "poo");
  assert.match(first.why, /practicarlo es lo que cuenta/);
  assert.equal(second.unit, "m1.errores", "y después la siguiente unidad por nivel");
});

test("sin unidades pendientes propone la evaluación solo si existe su banco", () => {
  const roadmap = copy(ROADMAP);
  roadmap.modules.find((m) => m.id === "m1").assessment.bank = "m1";
  const idx = indexRoadmap(roadmap);
  const { progress } = start();
  for (const u of idx.modules.get("m1").units) setUnitStatus(progress, u.id, "hecha", NOW);
  const inputs = { concepts: new Map([...learnIndex.concepts.keys()].map((c) => [c, concept(1)])) };
  const skills = allSkillStats(idx, progress, inputs, NOW);
  const modules = moduleStatuses(idx, progress, skills, NOW);
  const items = nextActivities(idx, progress, { skills, modules, inputs, now: NOW }).items;
  assert.equal(items[0].kind, "assessment");
  assert.equal(items[0].module, "m1");
  // Con el banco aún sin crear (catálogo real, Fase D), no se propone
  const real = nextActivities(index, progress, { skills, modules: moduleStatuses(index, progress, skills, NOW), inputs, now: NOW }).items;
  assert.ok(!real.some((i) => i.kind === "assessment"));
});

/* ---------- Horas de estudio ---------- */

test("horas de estudio apuntadas: total, por módulo y recientes; las borradas no cuentan", () => {
  const { progress } = start();
  logStudy(progress, { day: "2026-11-18", minutes: 45, module: "m1" }, NOW);
  logStudy(progress, { day: "2026-11-10", minutes: 30, module: "m8" }, NOW);
  const old = logStudy(progress, { day: "2026-09-01", minutes: 60 }, NOW);
  assert.equal(logStudy(progress, { day: "2026-11-18", minutes: 0 }, NOW), null);
  assert.equal(logStudy(progress, { day: "ayer", minutes: 10 }, NOW), null);
  assert.deepEqual(studyTotals(progress, NOW), { minutes: 135, byModule: { m1: 45, m8: 30 }, last7: 45, last30: 75, days: 3 });
  removeStudy(progress, old.id, NOW);
  assert.equal(studyTotals(progress, NOW).minutes, 75);
});

/* ---------- Validación ---------- */

test("solo pasan enlaces https sin credenciales y con dominio", () => {
  assert.equal(safeHttpsUrl("https://github.com/Marbi8891/repo"), "https://github.com/Marbi8891/repo");
  for (const bad of ["javascript:alert(1)", "http://github.com", "https://user:pass@github.com", "https://localhost/x", "data:text/html,<b>", "", null, `https://a.com/${"x".repeat(300)}`]) {
    assert.equal(safeHttpsUrl(bad), null, String(bad));
  }
});

test("una evidencia necesita enlace o nota, tipo y proyecto válidos", () => {
  const { progress } = start();
  assert.equal(addEvidence(progress, { project: "jobradar", kind: "demo" }, NOW), null);
  assert.equal(addEvidence(progress, { project: "jobradar", kind: "magia", note: "x" }, NOW), null);
  assert.equal(addEvidence(progress, { project: "Job Radar", kind: "demo", note: "x" }, NOW), null);
  const local = addEvidence(progress, { project: "jobradar", kind: "demo", url: "javascript:alert(1)", note: " demo local\u0000 " }, NOW);
  assert.deepEqual([local.url, local.note], [null, "demo local"], "sin URL peligrosa y sin caracteres de control");
});

test("limpieza: tipos y formatos esperados, topes y campos desconocidos conservados", () => {
  const raw = {
    v: 1,
    active: "<img src=x>",
    future: { a: 1 },
    roadmaps: {
      [RID]: {
        startedAt: "no",
        nuevoBloque: [1],
        units: { "m1.poo": { status: "hecha", at: "2026-11-18T10:00:00.000Z" }, "m1.x": { status: "leida", at: "2026-11-18T10:00:00.000Z" }, "<b>": { status: "hecha", at: "2026-11-18T10:00:00.000Z" } },
        assessments: { m1: [{ score: 2, at: "2026-11-18T10:00:00.000Z" }, { score: 0.5, at: "2026-11-18T10:00:00.000Z" }], m2: "x" },
        evidence: Array.from({ length: LIMITS.evidence + 20 }, (_, i) => ({ id: `ev-${i}`, project: "jobradar", kind: "pr", url: "https://github.com/a/b", at: "2026-11-18T10:00:00.000Z" })),
        criteria: { "jr-conectores": { met: "sí", at: "2026-11-18T10:00:00.000Z" } },
        studyLog: [{ id: "st-1", d: "2026-11-18", min: 9999, at: "2026-11-18T10:00:00.000Z" }],
        stages: { s1: { start: "mañana", months: 9, at: "2026-11-18T10:00:00.000Z" } },
      },
      "Otro Itinerario": {},
    },
  };
  const doc = cleanCareer(raw);
  assert.equal(doc.active, null);
  assert.deepEqual(doc.future, { a: 1 });
  const r = doc.roadmaps[RID];
  assert.deepEqual(Object.keys(doc.roadmaps), [RID]);
  assert.equal(r.startedAt, null);
  assert.deepEqual(r.nuevoBloque, [1]);
  assert.deepEqual(Object.keys(r.units), ["m1.poo"]);
  assert.deepEqual(r.assessments, { m1: [{ score: 0.5, at: "2026-11-18T10:00:00.000Z" }] });
  assert.equal(r.evidence.length, LIMITS.evidence);
  assert.equal(r.evidence[0].id, "ev-20", "se conservan las más recientes");
  assert.deepEqual(r.criteria, {});
  assert.deepEqual(r.studyLog, []);
  assert.deepEqual(r.stages, { s1: { start: null, months: 9, at: "2026-11-18T10:00:00.000Z" } });
  assert.deepEqual(cleanCareer("basura"), emptyCareer());
  assert.deepEqual(cleanCareer({ roadmaps: [] }), emptyCareer());
});

test("el documento más grande posible cabe en el límite del servidor (200 kB en JSON ASCII)", () => {
  const { doc, progress } = start();
  const note = "ñ".repeat(LIMITS.note);
  const url = `https://github.com/${"a".repeat(LIMITS.url - 30)}`;
  for (let i = 0; i < LIMITS.evidence; i += 1) addEvidence(progress, { project: "nexaro-personal-ai", criterion: "npa-producto", kind: "deploy", url, note }, NOW);
  for (let i = 0; i < LIMITS.studyLog; i += 1) logStudy(progress, { day: "2026-11-18", minutes: 600, module: "m4" }, NOW);
  for (const u of index.units.keys()) setUnitStatus(progress, u, "pendiente", NOW);
  for (const m of index.modules.keys()) for (let i = 0; i < LIMITS.attempts; i += 1) recordAssessment(progress, m, 0.123456789, NOW);
  for (const c of index.criteria.keys()) setCriterion(progress, c, true, NOW);
  for (const items of index.checklists.values()) for (const item of items) setChecklistItem(progress, item.id, true, NOW);
  for (const s of ROADMAP.stages) setStage(progress, s.id, { start: "2026-12-01", months: 12 }, NOW);
  assert.equal(progress.evidence.length, LIMITS.evidence);
  // Python mide con json.dumps (ASCII): cada carácter no ASCII ocupa 6 bytes (ñ)
  const size = JSON.stringify(doc).replace(/[^\x00-\x7f]/g, "\\u0000").length;
  assert.ok(size < 200_000, `${size} bytes`);
});

/* ---------- Fusión ---------- */

test("fusión: gana lo más reciente, los borrados no resucitan y no se pierde nada", () => {
  const a = start(at("2026-11-10T10:00:00"));
  const b = start(at("2026-11-01T10:00:00"));
  setUnitStatus(a.progress, "m1.poo", "hecha", at("2026-11-18T10:00:00"));
  setUnitStatus(b.progress, "m1.poo", "pendiente", at("2026-11-17T10:00:00"));
  setUnitStatus(b.progress, "m1.git", "hecha", at("2026-11-17T10:00:00"));
  recordAssessment(a.progress, "m1", 0.5, at("2026-11-15T10:00:00"));
  recordAssessment(b.progress, "m1", 0.8, at("2026-11-16T10:00:00"));
  const ev = addEvidence(a.progress, { project: "jobradar", kind: "demo", note: "demo" }, at("2026-11-15T10:00:00"));
  const remote = copy(b.doc);
  remote.roadmaps[RID].evidence.push({ ...ev });
  removeEvidence(a.progress, ev.id, at("2026-11-18T11:00:00"));
  remote.extra = "de otra versión";

  const merged = mergeCareer(a.doc, remote);
  const r = merged.roadmaps[RID];
  assert.equal(r.startedAt, at("2026-11-01T10:00:00").toISOString(), "se conserva el inicio más antiguo");
  assert.equal(r.units["m1.poo"].status, "hecha");
  assert.equal(r.units["m1.git"].status, "hecha");
  assert.deepEqual(r.assessments.m1.map((x) => x.score), [0.5, 0.8]);
  assert.equal(r.evidence.find((e) => e.id === ev.id).deleted, true, "el borrado local gana a la copia antigua");
  assert.equal(merged.extra, "de otra versión");
  // Fusionar otra vez lo mismo no cambia nada
  assert.deepEqual(mergeCareer(copy(merged), copy(merged)), merged);
});

test("fusión: el itinerario activo lo decide el cambio más reciente y llegan itinerarios nuevos", () => {
  const local = emptyCareer();
  enroll(local, RID, at("2026-11-01T10:00:00"));
  const remote = emptyCareer();
  enroll(remote, "otro-itinerario", at("2026-11-02T10:00:00"));
  mergeCareer(local, remote);
  assert.equal(local.active, "otro-itinerario");
  assert.deepEqual(Object.keys(local.roadmaps).sort(), [RID, "otro-itinerario"]);
});

test("enroll: no admite ids inválidos ni más itinerarios del tope", () => {
  const doc = emptyCareer();
  assert.equal(enroll(doc, "No Válido", NOW), null);
  for (let i = 0; i < LIMITS.roadmaps; i += 1) assert.ok(enroll(doc, `r${i}`, NOW));
  assert.equal(enroll(doc, "uno-mas", NOW), null);
  assert.ok(enroll(doc, "r0", NOW), "uno que ya existe sí");
  assert.equal(doc.active, "r0");
});
