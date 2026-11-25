/* Itinerario profesional (DEC-012): documento `career` y cálculos puros. No toca el DOM ni localStorage
   (eso lo hace career-store.js), así que se prueba con node --test.

   El catálogo (frontend/data/career/<id>.json) lo genera scripts/career/build_career.py. Este archivo
   no mide de nuevo lo que ya mide el motor adaptativo: una competencia agrega el dominio de conceptos
   (mastery.js), la preparación de bloques de los cursos de DAW, la evaluación de su módulo y las
   evidencias de proyecto. Marcar una unidad como estudiada NO sube ninguna competencia.

   Documento (clave pld:career y /api/course-state/career):
   {
     v: 1, active: idItinerario | null, activeAt: ISO | null,
     roadmaps: { [idItinerario]: {
       startedAt: ISO | null,
       stages:      { [idEtapa]: { start: "AAAA-MM-DD" | null, months: 1-24 | null, at } },
       units:       { [idUnidad]: { status: "hecha" | "pendiente", at } },
       assessments: { [idEvaluación]: [ { score: 0-1, at } ] },                últimos ATTEMPTS
       evidence:    [ { id, project, criterion | null, kind, url | null, note, at, deleted? } ],
       criteria:    { [idCriterio]: { met: boolean, at } },
       checklists:  { [idElemento]: { done: boolean, at } },
       studyLog:    [ { id, d: "AAAA-MM-DD", min, module | null, at, deleted? } ]
     } }
   }
   Los borrados se quedan marcados (`deleted`) para que otro dispositivo no los resucite al fusionar.
   Los campos que esta versión no conoce se conservan (DEC-007). Los datos económicos NO van aquí
   (career-finance.js, solo en el navegador). */

import { addDays, daysBetween, isoDay } from "../srs.js";
import { FULL_COVERAGE } from "../pcap-store.js";
import { READY_SCORE } from "../learn/recommend.js";\nimport { cleanPracticeMap, mergePractice } from "./career-practice.js";

export const LIMITS = Object.freeze({ roadmaps: 5, evidence: 100, studyLog: 366, attempts: 10, note: 120, url: 240, minutes: 600 });
export const UNIT_STATUSES = Object.freeze(["hecha", "pendiente"]);
export const EVIDENCE_KINDS = Object.freeze(["repo", "pr", "commit", "tests", "demo", "docs", "deploy", "result"]);
/** Pesos de cada tipo de fuente en una competencia (se normalizan sobre los que la competencia declara). */
export const SOURCE_WEIGHTS = Object.freeze({ assessment: 0.4, practice: 0.3, project: 0.3 });
/** Una competencia está adquirida con este dominio, evidencias suficientes y, si las pide, proyecto. */
export const ACQUIRED = 0.7;
export const MIN_CONFIDENCE = 0.5;
/** Una evaluación aprobada caduca a efectos de repaso pasado este tiempo. */
export const ASSESSMENT_VALID_DAYS = 180;
/** Con un examen o entrega de DAW a esta distancia o menos, la ruta se pausa (DAW primero). */
export const DAW_PRIORITY_DAYS = 7;

const DAY = /^\d{4}-\d{2}-\d{2}$/;
const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const ID = /^[a-z0-9][a-z0-9.-]{0,60}$/;
const EXTRA_KEY = /^[a-zA-Z][a-zA-Z0-9]{0,30}$/;
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const isIso = (value) => typeof value === "string" && ISO.test(value);
const isId = (value) => typeof value === "string" && ID.test(value);
const later = (a, b) => ((a?.at ?? "") >= (b?.at ?? "") ? a : b);
const LEVEL_ORDER = ["fundamentos", "intermedio", "avanzado", "profesional"];

export const emptyCareer = () => ({ v: 1, active: null, activeAt: null, roadmaps: {} });
export const emptyRoadmap = () => ({ startedAt: null, stages: {}, units: {}, assessments: {}, evidence: [], criteria: {}, checklists: {}, studyLog: [], practice: {} });
const ROADMAP_KEYS = new Set(Object.keys(emptyRoadmap()));
const TOP_KEYS = new Set(Object.keys(emptyCareer()));

/* ---------- Validación de lo que llega de fuera ---------- */

/** URL https sin credenciales y con dominio, o null. Es lo único que se pinta como enlace. */
export function safeHttpsUrl(value) {
  if (typeof value !== "string" || !value.trim() || value.length > LIMITS.url) return null;
  let url;
  try {
    url = new URL(value.trim());
  } catch {
    return null;
  }
  if (url.protocol !== "https:" || url.username || url.password || !url.hostname.includes(".")) return null;
  return url.href.length <= LIMITS.url ? url.href : null;
}

const cleanText = (value, max) => (typeof value === "string" ? value.replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, max) : "");

function cleanMap(raw, clean) {
  const out = {};
  if (!isObject(raw)) return out;
  for (const [id, value] of Object.entries(raw)) {
    if (!isId(id) || !isObject(value)) continue;
    const item = clean(value);
    if (item) out[id] = item;
  }
  return out;
}

function cleanEvidence(raw) {
  if (!isObject(raw) || !isId(raw.id) || !isId(raw.project) || !EVIDENCE_KINDS.includes(raw.kind) || !isIso(raw.at)) return null;
  const url = safeHttpsUrl(raw.url);
  const note = cleanText(raw.note, LIMITS.note);
  const deleted = raw.deleted === true;
  if (!url && !note && !deleted) return null;
  return { id: raw.id, project: raw.project, criterion: isId(raw.criterion) ? raw.criterion : null, kind: raw.kind, url, note, at: raw.at, ...(deleted ? { deleted: true } : {}) };
}

function cleanStudy(raw) {
  if (!isObject(raw) || !isId(raw.id) || !DAY.test(raw.d ?? "") || !isIso(raw.at)) return null;
  if (!Number.isInteger(raw.min) || raw.min < 1 || raw.min > LIMITS.minutes) return null;
  return { id: raw.id, d: raw.d, min: raw.min, module: isId(raw.module) ? raw.module : null, at: raw.at, ...(raw.deleted === true ? { deleted: true } : {}) };
}

function extras(raw, known, into) {
  for (const [key, value] of Object.entries(raw)) if (!known.has(key) && EXTRA_KEY.test(key)) into[key] = value;
  return into;
}

function cleanRoadmap(raw) {
  const r = emptyRoadmap();
  if (!isObject(raw)) return r;
  extras(raw, ROADMAP_KEYS, r);
  r.startedAt = isIso(raw.startedAt) ? raw.startedAt : null;
  r.stages = cleanMap(raw.stages, (s) =>
    isIso(s.at)
      ? { start: typeof s.start === "string" && DAY.test(s.start) ? s.start : null, months: Number.isInteger(s.months) && s.months >= 1 && s.months <= 24 ? s.months : null, at: s.at }
      : null,
  );
  r.units = cleanMap(raw.units, (u) => (UNIT_STATUSES.includes(u.status) && isIso(u.at) ? { status: u.status, at: u.at } : null));
  if (isObject(raw.assessments)) {
    for (const [id, attempts] of Object.entries(raw.assessments)) {
      if (!isId(id) || !Array.isArray(attempts)) continue;
      const clean = attempts
        .filter((a) => isObject(a) && typeof a.score === "number" && a.score >= 0 && a.score <= 1 && isIso(a.at))
        .map((a) => ({ score: a.score, at: a.at }))
        .slice(-LIMITS.attempts);
      if (clean.length) r.assessments[id] = clean;
    }
  }
  r.evidence = (Array.isArray(raw.evidence) ? raw.evidence : []).map(cleanEvidence).filter(Boolean).slice(-LIMITS.evidence);
  r.criteria = cleanMap(raw.criteria, (c) => (typeof c.met === "boolean" && isIso(c.at) ? { met: c.met, at: c.at } : null));
  r.checklists = cleanMap(raw.checklists, (c) => (typeof c.done === "boolean" && isIso(c.at) ? { done: c.done, at: c.at } : null));
  r.studyLog = (Array.isArray(raw.studyLog) ? raw.studyLog : []).map(cleanStudy).filter(Boolean).slice(-LIMITS.studyLog);
  return r;
}

/** Valida un documento que llega de fuera (localStorage o la cuenta). Conserva los bloques que no conoce. */
export function cleanCareer(value) {
  const doc = emptyCareer();
  if (!isObject(value)) return doc;
  extras(value, TOP_KEYS, doc);
  doc.active = isId(value.active) ? value.active : null;
  doc.activeAt = isIso(value.activeAt) ? value.activeAt : null;
  if (isObject(value.roadmaps)) {
    for (const [id, raw] of Object.entries(value.roadmaps).slice(0, LIMITS.roadmaps)) if (isId(id)) doc.roadmaps[id] = cleanRoadmap(raw);
  }
  return doc;
}

/* ---------- Fusión con la cuenta ---------- */

const mergeMap = (mine, other) => {
  for (const [id, item] of Object.entries(other)) mine[id] = mine[id] ? later(mine[id], item) : item;
};

function mergeList(mine, other, max) {
  const byId = new Map(mine.map((item) => [item.id, item]));
  for (const item of other) byId.set(item.id, byId.has(item.id) ? later(byId.get(item.id), item) : item);
  return [...byId.values()].sort((a, b) => a.at.localeCompare(b.at)).slice(-max);
}

function mergeRoadmap(local, remote) {
  if (remote.startedAt && (!local.startedAt || remote.startedAt < local.startedAt)) local.startedAt = remote.startedAt;
  for (const field of ["stages", "units", "criteria", "checklists"]) mergeMap(local[field], remote[field]);
  for (const [id, attempts] of Object.entries(remote.assessments)) {
    const all = new Map([...(local.assessments[id] ?? []), ...attempts].map((a) => [a.at, a]));
    local.assessments[id] = [...all.values()].sort((a, b) => a.at.localeCompare(b.at)).slice(-LIMITS.attempts);
  }
  local.evidence = mergeList(local.evidence, remote.evidence, LIMITS.evidence);
  local.studyLog = mergeList(local.studyLog, remote.studyLog, LIMITS.studyLog);
  for (const [key, raw] of Object.entries(remote)) if (!(key in local)) local[key] = raw;
}

/** Fusiona la copia de la cuenta con la local sin perder nada: gana lo cambiado más tarde. */
export function mergeCareer(local, remote) {
  const other = cleanCareer(remote);
  if ((other.activeAt ?? "") > (local.activeAt ?? "")) {
    local.active = other.active;
    local.activeAt = other.activeAt;
  }
  for (const [id, roadmap] of Object.entries(other.roadmaps)) {
    if (local.roadmaps[id]) mergeRoadmap(local.roadmaps[id], roadmap);
    else if (Object.keys(local.roadmaps).length < LIMITS.roadmaps) local.roadmaps[id] = roadmap;
  }
  for (const [key, raw] of Object.entries(other)) if (!(key in local)) local[key] = raw;
  return local;
}

/* ---------- Cambios (los llama la interfaz; después, saveCareer) ---------- */

/** Itinerario activo; lo crea si no existe. Devuelve su progreso. */
export function enroll(doc, roadmapId, now = new Date()) {
  if (!isId(roadmapId)) return null;
  if (!doc.roadmaps[roadmapId] && Object.keys(doc.roadmaps).length >= LIMITS.roadmaps) return null;
  const progress = (doc.roadmaps[roadmapId] ??= emptyRoadmap());
  progress.startedAt ??= now.toISOString();
  if (doc.active !== roadmapId) Object.assign(doc, { active: roadmapId, activeAt: now.toISOString() });
  return progress;
}

/** Unidad estudiada o pendiente. Solo organiza: no cuenta como evidencia de ninguna competencia. */
export function setUnitStatus(progress, unitId, status, now = new Date()) {
  if (isId(unitId) && UNIT_STATUSES.includes(status)) progress.units[unitId] = { status, at: now.toISOString() };
}

/** Resultado (0-1) de la evaluación de un módulo, calculado por la corrección determinista. */
export function recordAssessment(progress, assessmentId, score, now = new Date()) {
  if (!isId(assessmentId) || typeof score !== "number" || !(score >= 0 && score <= 1)) return;
  const attempts = (progress.assessments[assessmentId] ??= []);
  attempts.push({ score, at: now.toISOString() });
  progress.assessments[assessmentId] = attempts.slice(-LIMITS.attempts);
}

let counter = 0;
const newId = (prefix, now) => `${prefix}-${now.getTime().toString(36)}-${(counter += 1).toString(36)}`;

/** Añade una evidencia (enlace https y/o nota). Devuelve la evidencia o null si no es válida. */
export function addEvidence(progress, { project, criterion = null, kind, url = null, note = "" }, now = new Date()) {
  const evidence = cleanEvidence({ id: newId("ev", now), project, criterion, kind, url, note, at: now.toISOString() });
  if (!evidence) return null;
  progress.evidence = [...progress.evidence, evidence].slice(-LIMITS.evidence);
  return evidence;
}

export function removeEvidence(progress, id, now = new Date()) {
  const evidence = progress.evidence.find((e) => e.id === id);
  if (evidence) Object.assign(evidence, { deleted: true, at: now.toISOString() });
}

export function setCriterion(progress, criterionId, met, now = new Date()) {
  if (isId(criterionId) && typeof met === "boolean") progress.criteria[criterionId] = { met, at: now.toISOString() };
}

export function setChecklistItem(progress, itemId, done, now = new Date()) {
  if (isId(itemId) && typeof done === "boolean") progress.checklists[itemId] = { done, at: now.toISOString() };
}

/** Mueve o alarga una etapa del plan. `null` vuelve al valor del catálogo. */
export function setStage(progress, stageId, { start = null, months = null } = {}, now = new Date()) {
  if (!isId(stageId)) return;
  const clean = cleanRoadmap({ stages: { [stageId]: { start, months, at: now.toISOString() } } }).stages[stageId];
  if (clean) progress.stages[stageId] = clean;
}

/** Apunta una sesión de estudio hecha (minutos reales, no un cronómetro). Devuelve la entrada o null. */
export function logStudy(progress, { day, minutes, module = null }, now = new Date()) {
  const entry = cleanStudy({ id: newId("st", now), d: day ?? isoDay(now), min: Math.round(Number(minutes)), module, at: now.toISOString() });
  if (!entry) return null;
  progress.studyLog = [...progress.studyLog, entry].slice(-LIMITS.studyLog);
  return entry;
}

export function removeStudy(progress, id, now = new Date()) {
  const entry = progress.studyLog.find((e) => e.id === id);
  if (entry) Object.assign(entry, { deleted: true, at: now.toISOString() });
}

/* ---------- Cálculos sobre el catálogo ---------- */

/** Índices del catálogo para los cálculos. */
export function indexRoadmap(roadmap) {
  const modules = new Map(roadmap.modules.map((m) => [m.id, m]));
  const units = new Map(roadmap.modules.flatMap((m) => m.units.map((u) => [u.id, { ...u, module: m.id }])));
  const criteria = new Map(roadmap.projects.flatMap((p) => p.criteria.map((c) => [c.id, { ...c, project: p.id }])));
  const checklists = new Map(Object.entries(roadmap.checklists));
  const moduleSkills = new Map(roadmap.modules.map((m) => [m.id, [...new Set(m.units.flatMap((u) => u.skills))]]));
  return { roadmap, modules, units, criteria, checklists, moduleSkills, skills: new Map(roadmap.skills.map((s) => [s.id, s])) };
}

/** Puntuación (0-1) de un bloque de curso: acierto × cobertura, con la cobertura del PCAP y los cursos. */
export const blockScore = (s) => (s && s.total && s.answered ? (s.rate ?? 0) * Math.min(1, s.answered / s.total / FULL_COVERAGE) : 0);

const latestAttempt = (progress, id) => progress.assessments[id]?.at(-1) ?? null;
const liveEvidence = (progress) => progress.evidence.filter((e) => !e.deleted);

/** Un criterio de proyecto solo cuenta si está marcado y tiene al menos una evidencia. */
export function criterionMet(progress, criterionId) {
  return progress.criteria[criterionId]?.met === true && liveEvidence(progress).some((e) => e.criterion === criterionId);
}

const checklistShare = (index, progress, name) => {
  const items = index.checklists.get(name) ?? [];
  return items.length ? items.filter((i) => progress.checklists[i.id]?.done).length / items.length : 0;
};

const mean = (values) => (values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0);

/**
 * Dominio de una competencia, explicable. `inputs` sale del motor adaptativo y de los cursos:
 *   concepts: Map(idConcepto → conceptStats de mastery.js)
 *   blocks:   Map("curso:bloque" → { answered, total, rate } de courseBlockStats)
 * Cada grupo de fuentes que declara la competencia (práctica, evaluación, proyecto) da 0-1; sin datos, 0.
 */
export function skillStats(index, progress, skillId, inputs = {}, now = new Date()) {
  const skill = index.skills.get(skillId);
  const { concepts: conceptIds, blocks: blockIds, assessments, criteria, checklists } = skill.sources;
  const groups = {};
  let review = false;

  if (conceptIds.length || blockIds.length) {
    const concepts = conceptIds.map((id) => inputs.concepts?.get(id));
    const blocks = blockIds.map((id) => inputs.blocks?.get(id));
    review ||= concepts.some((s) => s?.forgotten);
    groups.practice = {
      value: mean([...concepts.map((s) => s?.score ?? 0), ...blocks.map(blockScore)]),
      data: concepts.some((s) => s?.attempted > 0) || blocks.some((b) => b?.answered > 0),
    };
  }
  if (assessments.length) {
    const latest = assessments.map((id) => latestAttempt(progress, id));
    review ||= latest.some((a) => a && daysBetween(a.at, now) > ASSESSMENT_VALID_DAYS);
    groups.assessment = { value: mean(latest.map((a) => a?.score ?? 0)), data: latest.some(Boolean) };
  }
  if (criteria.length || checklists.length) {
    const values = [...criteria.map((id) => (criterionMet(progress, id) ? 1 : 0)), ...checklists.map((name) => checklistShare(index, progress, name))];
    groups.project = { value: mean(values), data: values.some((v) => v > 0) };
  }

  const defined = Object.keys(groups);
  const weight = defined.reduce((sum, g) => sum + SOURCE_WEIGHTS[g], 0);
  const score = defined.reduce((sum, g) => sum + SOURCE_WEIGHTS[g] * groups[g].value, 0) / weight;
  const withData = defined.filter((g) => groups[g].data);
  const confidence = withData.length / defined.length;
  const evaluated = withData.includes("practice") || withData.includes("assessment");
  const enough = confidence >= MIN_CONFIDENCE && evaluated;

  let status;
  if (!withData.length) status = "sin-evidencias";
  else if (!enough) status = "insuficiente";
  else if (score >= ACQUIRED && (!groups.project || groups.project.value > 0)) status = review ? "repasar" : "adquirida";
  else if (score >= 0.4) status = "progreso";
  else status = "aprendiendo";
  return { id: skillId, score, confidence, enough, status, review, groups };
}

export const allSkillStats = (index, progress, inputs = {}, now = new Date()) =>
  new Map([...index.skills.keys()].map((id) => [id, skillStats(index, progress, id, inputs, now)]));

/** Explicación en una frase de una competencia (para la interfaz). */
export function explainSkill(s) {
  if (s.status === "sin-evidencias") return "Sin evidencias todavía: estudiar las unidades no basta, hace falta practicar, evaluarse o demostrarlo en un proyecto.";
  const names = { practice: "práctica", assessment: "evaluación", project: "proyecto" };
  const parts = Object.entries(s.groups).map(([g, v]) => `${names[g]} ${Math.round(v.value * 100)} %`);
  if (!s.enough) parts.push("pocas evidencias para darla por adquirida");
  if (s.review) parts.push("toca repasar");
  return `${parts.join("; ")}.`;
}

/** ¿El módulo está listo para servir de base a otro? Completado o con sus competencias en READY_SCORE. */
function moduleReady(index, skills, status, moduleId) {
  if (status.get(moduleId)?.completed) return true;
  const values = index.moduleSkills.get(moduleId).map((id) => skills.get(id)?.score ?? 0);
  return mean(values) >= READY_SCORE;
}

/**
 * Estado de cada módulo: bloqueado (solo orientativo: se puede abrir igual), disponible, en-curso,
 * completado o repasar. Completado = unidades estudiadas + evaluación aprobada + criterios y listas del
 * proyecto cumplidos. La posición del módulo en la ruta no influye: solo sus prerrequisitos.
 */
export function moduleStatuses(index, progress, skills, now = new Date()) {
  const out = new Map();
  for (const m of index.roadmap.modules) {
    const done = m.units.filter((u) => progress.units[u.id]?.status === "hecha").length;
    const latest = latestAttempt(progress, m.assessment.id);
    const passed = Boolean(latest && latest.score >= m.assessment.pass);
    const criteria = m.project.criteria.filter((id) => criterionMet(progress, id)).length;
    const lists = m.project.checklists.every((name) => checklistShare(index, progress, name) === 1);
    const completed = done === m.units.length && passed && criteria === m.project.criteria.length && lists;
    const started =
      done > 0 ||
      Boolean(latest) ||
      m.project.criteria.some((id) => progress.criteria[id] || liveEvidence(progress).some((e) => e.criterion === id)) ||
      m.project.checklists.some((name) => checklistShare(index, progress, name) > 0);
    const stale = Boolean(latest && daysBetween(latest.at, now) > ASSESSMENT_VALID_DAYS);
    out.set(m.id, { id: m.id, units: { done, total: m.units.length }, assessment: { latest, passed, available: Boolean(m.assessment.bank) }, criteria: { met: criteria, total: m.project.criteria.length }, completed, started, stale });
  }
  for (const m of index.roadmap.modules) {
    const s = out.get(m.id);
    const missing = m.requires.filter((id) => !moduleReady(index, skills, out, id));
    const review = s.stale || index.moduleSkills.get(m.id).some((id) => skills.get(id)?.status === "repasar");
    s.missing = missing;
    s.status = s.completed ? (review ? "repasar" : "completado") : s.started ? "en-curso" : missing.length ? "bloqueado" : "disponible";
  }
  return out;
}

/** Cobertura (0-1) de cada puesto objetivo y qué falta, de mayor a menor cobertura. */
export function roleCoverage(index, skills) {
  return index.roadmap.roles
    .map((role) => {
      const items = Object.entries(role.skills).map(([id, target]) => ({ id, target, score: skills.get(id)?.score ?? 0 }));
      const coverage = mean(items.map((i) => Math.min(1, i.score / i.target)));
      const missing = items.filter((i) => i.score < i.target).sort((a, b) => b.target - b.score - (a.target - a.score));
      return { id: role.id, band: role.band, coverage, ready: missing.length === 0, missing };
    })
    .sort((a, b) => b.coverage - a.coverage);
}

function addMonths(day, months) {
  const [y, m, d] = day.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1 + months, 1));
  const last = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + 1, 0)).getUTCDate();
  date.setUTCDate(Math.min(d, last));
  return date.toISOString().slice(0, 10);
}

/** Plan de etapas con fechas: cada etapa empieza donde acaba la anterior salvo que se haya movido. */
export function stagePlan(index, progress, now = new Date()) {
  const today = isoDay(now);
  let cursor = progress.startedAt ? isoDay(new Date(progress.startedAt)) : today;
  return index.roadmap.stages.map((stage) => {
    const custom = progress.stages[stage.id];
    const start = custom?.start ?? cursor;
    const months = custom?.months ?? stage.months;
    const end = addMonths(start, months);
    cursor = end;
    return { id: stage.id, modules: stage.modules, start, end, months, custom: Boolean(custom), current: start <= today && today < end, past: end <= today };
  });
}

/** Horas de estudio apuntadas: total, por módulo y de los últimos 7 y 30 días. */
export function studyTotals(progress, now = new Date()) {
  const entries = progress.studyLog.filter((e) => !e.deleted);
  const since = (days) => addDays(now, -days + 1);
  const sum = (list) => list.reduce((total, e) => total + e.min, 0);
  const byModule = {};
  for (const e of entries) if (e.module) byModule[e.module] = (byModule[e.module] ?? 0) + e.min;
  return { minutes: sum(entries), byModule, last7: sum(entries.filter((e) => e.d >= since(7))), last30: sum(entries.filter((e) => e.d >= since(30))), days: new Set(entries.map((e) => e.d)).size };
}

/** Examen o entrega de DAW (del planificador) que pausa la ruta: el más cercano a DAW_PRIORITY_DAYS o menos. */
export function dawPriority(exams = []) {
  return exams.filter((e) => !e.deleted && e.days >= 0 && e.days <= DAW_PRIORITY_DAYS).sort((a, b) => a.days - b.days)[0] ?? null;
}

/**
 * Siguientes actividades de la ruta, cada una con su motivo. DAW va primero: con un examen o entrega en
 * DAW_PRIORITY_DAYS o menos (`exams` = upcomingExams del planificador) no se propone nada de la ruta.
 * Orden: módulos de la etapa actual y después el resto, sin los bloqueados. En cada módulo: practicar
 * los conceptos de una unidad ya estudiada que aún no cuentan, la siguiente unidad, la evaluación y el
 * proyecto.
 */
export function nextActivities(index, progress, { skills, modules, inputs = {}, exams = [], now = new Date(), limit = 3 } = {}) {
  const paused = dawPriority(exams);
  if (paused) return { paused, items: [] };
  const current = stagePlan(index, progress, now).find((s) => s.current)?.modules ?? [];
  const order = [...new Set([...current, ...index.roadmap.modules.map((m) => m.id)])];
  const items = [];
  for (const moduleId of order) {
    const m = index.modules.get(moduleId);
    const status = modules.get(moduleId);
    if (status.status === "bloqueado" || status.status === "completado") continue;
    const units = [...m.units].sort((a, b) => LEVEL_ORDER.indexOf(a.level) - LEVEL_ORDER.indexOf(b.level));
    for (const unit of units.filter((u) => progress.units[u.id]?.status === "hecha")) {
      const weak = unit.links.find((l) => l.kind === "concept" && (inputs.concepts?.get(l.id)?.score ?? 0) < READY_SCORE);
      if (weak) items.push({ kind: "practice", module: moduleId, unit: unit.id, concept: weak.id, why: `Has estudiado «${unit.title.es}», pero el concepto «${weak.id}» aún no llega al ${Math.round(READY_SCORE * 100)} %: practicarlo es lo que cuenta como evidencia.` });
    }
    const next = units.find((u) => progress.units[u.id]?.status !== "hecha");
    if (next) items.push({ kind: "unit", module: moduleId, unit: next.id, why: `Siguiente unidad de ${m.title.es} (nivel ${next.level}).` });
    else if (!status.assessment.passed && status.assessment.available) items.push({ kind: "assessment", module: moduleId, why: `Has estudiado todas las unidades de ${m.title.es}: falta aprobar su evaluación.` });
    const criterion = m.project.criteria.find((id) => !criterionMet(progress, id));
    if (criterion) items.push({ kind: "criterion", module: moduleId, criterion, project: index.criteria.get(criterion).project, why: `Demuéstralo en un proyecto real: «${index.criteria.get(criterion).title.es}».` });
    if (items.length >= limit) break;
  }
  return { paused: null, items: items.slice(0, limit) };
}

/** Competencias adquiridas y pendientes (para «Mi Carrera en IA»). */
export function skillSummary(skills) {
  const list = [...skills.values()];
  const acquired = list.filter((s) => s.status === "adquirida" || s.status === "repasar");
  return { acquired: acquired.map((s) => s.id), pending: list.filter((s) => !acquired.includes(s)).map((s) => s.id), total: list.length, progress: mean(list.map((s) => s.score)) };
}
