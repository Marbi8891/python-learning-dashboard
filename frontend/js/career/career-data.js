/* Career Roadmap: documento de progreso y cálculo puro (docs/CAREER_ROADMAP_ARCHITECTURE.md §4).
   No toca el DOM ni localStorage (eso lo hace career-store.js), así que se prueba con node --test.

   El catálogo (frontend/data/career/<id>.json) se genera con scripts/career/build_career.py.
   El dominio NO se mide de nuevo: se agrega lo que ya mide la plataforma (señales):
     concepts: Map<idConcepto, { score, confidence, forgotten }>   ← learn/mastery.js (conceptStats)
     blocks:   Map<"curso:bloque", { rate, answered, total }>       ← pcap-store.js (blockStats)
   y las entregas de proyectos que guarda este documento.

   Documento (clave pld:career y /api/course-state/career):
   {
     v: 1,
     active: idItinerario | null, activeAt: ISO | null,
     roadmaps: { [idItinerario]: {
       enrolledAt: ISO, months: 1-36 | null, monthsAt: ISO | null,
       units: { [idUnidad]: { done: bool, at: ISO } },
       projects: { [idProyecto]: { repo: "https://…" | "", checks: { [idCriterio]: true }, at: ISO } }
     } }
   }
   Los bloques y campos que no conoce se conservan (DEC-007). */

import { MIN_CONFIDENCE } from "../learn/mastery.js";
import { READY_SCORE } from "../learn/recommend.js";
import { blockCoverage } from "../pcap-store.js";

export const PHASE_STATUSES = Object.freeze(["locked", "available", "in_progress", "completed", "needs_review"]);
export { READY_SCORE };
const MAX_ROADMAPS = 10;
const MAX_ITEMS = 300; // unidades o proyectos por itinerario
const MAX_URL = 300;

const ID = /^[a-z0-9][a-z0-9-]{0,48}$/;
const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const EPOCH = "1970-01-01T00:00:00.000Z";
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const isIso = (value) => typeof value === "string" && ISO.test(value);
const stamp = (now) => now.toISOString();
const later = (a, b) => ((a?.at ?? "") >= (b?.at ?? "") ? a : b);

export const emptyCareer = () => ({ v: 1, active: null, activeAt: null, roadmaps: {} });
const emptyEnrollment = (now) => ({ enrolledAt: stamp(now), months: null, monthsAt: null, units: {}, projects: {} });

/** Enlace a un repositorio o demo: solo https y sin credenciales; si no vale, cadena vacía. */
export function cleanRepoUrl(value) {
  if (typeof value !== "string") return "";
  const url = value.trim();
  if (url.length > MAX_URL || !/^https:\/\//i.test(url)) return "";
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" && !parsed.username && !parsed.password && parsed.hostname.includes(".") ? url : "";
  } catch {
    return "";
  }
}

const clampMonths = (value) => (Number.isInteger(value) && value >= 1 && value <= 36 ? value : null);

function keepUnknown(target, source, pattern = /^[a-zA-Z][a-zA-Z0-9]{0,30}$/) {
  for (const [key, raw] of Object.entries(source)) if (!(key in target) && pattern.test(key)) target[key] = raw;
}

function cleanEnrollment(raw) {
  if (!isObject(raw) || !isIso(raw.enrolledAt)) return null;
  const out = { enrolledAt: raw.enrolledAt, months: clampMonths(raw.months), monthsAt: isIso(raw.monthsAt) ? raw.monthsAt : null, units: {}, projects: {} };
  keepUnknown(out, raw);
  if (isObject(raw.units)) {
    for (const [id, unit] of Object.entries(raw.units).slice(0, MAX_ITEMS)) {
      if (ID.test(id) && isObject(unit) && typeof unit.done === "boolean" && isIso(unit.at)) out.units[id] = { done: unit.done, at: unit.at };
    }
  }
  if (isObject(raw.projects)) {
    for (const [id, project] of Object.entries(raw.projects).slice(0, MAX_ITEMS)) {
      if (!ID.test(id) || !isObject(project) || !isIso(project.at)) continue;
      const checks = {};
      if (isObject(project.checks)) for (const [c, ok] of Object.entries(project.checks).slice(0, 30)) if (ID.test(c) && ok === true) checks[c] = true;
      out.projects[id] = { repo: cleanRepoUrl(project.repo), checks, at: project.at };
    }
  }
  return out;
}

/** Valida un documento que llega de fuera (localStorage o la cuenta). Conserva los campos que no conoce. */
export function cleanCareer(value) {
  const doc = emptyCareer();
  if (!isObject(value)) return doc;
  keepUnknown(doc, value);
  if (isObject(value.roadmaps)) {
    for (const [id, raw] of Object.entries(value.roadmaps).slice(0, MAX_ROADMAPS)) {
      const clean = ID.test(id) ? cleanEnrollment(raw) : null;
      if (clean) doc.roadmaps[id] = clean;
    }
  }
  if (typeof value.active === "string" && doc.roadmaps[value.active]) {
    doc.active = value.active;
    doc.activeAt = isIso(value.activeAt) ? value.activeAt : EPOCH;
  }
  return doc;
}

/** Fusiona la copia de la cuenta en la local sin perder nada: gana lo cambiado más tarde. Modifica `local`. */
export function mergeCareer(local, remoteValue) {
  const remote = cleanCareer(remoteValue);
  keepUnknown(local, remote);
  for (const [id, theirs] of Object.entries(remote.roadmaps)) {
    const ours = local.roadmaps[id];
    if (!ours) {
      local.roadmaps[id] = theirs;
      continue;
    }
    keepUnknown(ours, theirs);
    if (theirs.enrolledAt < ours.enrolledAt) ours.enrolledAt = theirs.enrolledAt;
    if ((theirs.monthsAt ?? "") > (ours.monthsAt ?? "")) Object.assign(ours, { months: theirs.months, monthsAt: theirs.monthsAt });
    for (const field of ["units", "projects"]) {
      for (const [key, entry] of Object.entries(theirs[field])) ours[field][key] = later(ours[field][key], entry);
    }
  }
  if (remote.active && (remote.activeAt ?? "") > (local.activeAt ?? "")) {
    local.active = remote.active;
    local.activeAt = remote.activeAt;
  }
  return local;
}

/** Empieza un itinerario (o lo vuelve a activar si ya estaba). El progreso anterior se conserva. */
export function enroll(doc, roadmapId, now = new Date()) {
  if (!ID.test(roadmapId)) throw new Error(`Itinerario no válido: ${roadmapId}`);
  doc.roadmaps[roadmapId] ??= emptyEnrollment(now);
  doc.active = roadmapId;
  doc.activeAt = stamp(now);
  return doc.roadmaps[roadmapId];
}

/** Duración orientativa elegida por el alumno (1-36 meses; null = la del itinerario). Nunca bloquea. */
export function setMonths(doc, roadmapId, months, now = new Date()) {
  const enrollment = doc.roadmaps[roadmapId];
  if (!enrollment) return;
  enrollment.months = clampMonths(months);
  enrollment.monthsAt = stamp(now);
}

/** Marca una unidad como estudiada (o la desmarca). Estudiada no es lo mismo que dominada. */
export function setUnitDone(doc, roadmapId, unitId, done, now = new Date()) {
  const enrollment = doc.roadmaps[roadmapId];
  if (!enrollment || !ID.test(unitId)) return;
  enrollment.units[unitId] = { done: Boolean(done), at: stamp(now) };
}

/** Guarda la entrega de un proyecto: enlace al repositorio y criterios que el alumno da por cumplidos. */
export function saveProject(doc, roadmapId, project, { repo = "", checks = {} } = {}, now = new Date()) {
  const enrollment = doc.roadmaps[roadmapId];
  if (!enrollment) return null;
  const valid = new Set(project.criteria.map((c) => c.id));
  const clean = {};
  for (const [id, ok] of Object.entries(checks)) if (ok === true && valid.has(id)) clean[id] = true;
  enrollment.projects[project.id] = { repo: cleanRepoUrl(repo), checks: clean, at: stamp(now) };
  return enrollment.projects[project.id];
}

/* ---------- Cálculo ---------- */

/** Señales vacías (sin progreso en el resto de la plataforma). */
export const emptySignals = () => ({ concepts: new Map(), blocks: new Map() });

/** Estado de la entrega de un proyecto: parte de los criterios cumplidos y si hay enlace válido. */
export function projectProgress(project, submission) {
  const total = project.criteria.length;
  const done = submission ? project.criteria.filter((c) => submission.checks[c.id]).length : 0;
  const repo = submission?.repo ?? "";
  return { done, total, ratio: total ? done / total : 0, repo, delivered: Boolean(repo) && done === total };
}

/**
 * Dominio de una competencia (0-100) a partir de sus fuentes. Cada fuente da un valor v (0-1) y una
 * evidencia e (0-1):
 *   concepto   v = dominio del motor 2.0 (ya con retención)   e = confianza del motor
 *   bloque     v = acierto del bloque                         e = cobertura del bloque (blockCoverage)
 *   proyecto   v = criterios cumplidos / criterios            e = 1 si hay enlace válido y algún criterio, si no 0
 *   score      = Σ v·e / n        confidence = Σ e / n        (n = número de fuentes)
 * Una fuente sin evidencias cuenta como 0: no haber practicado algo no es dominarlo.
 */
export function skillMastery(skill, { roadmap, enrollment, signals = emptySignals() }) {
  const sources = [];
  for (const id of skill.sources.concepts) {
    const s = signals.concepts.get(id);
    sources.push({ kind: "concept", ref: id, value: s?.score ?? 0, evidence: s?.confidence ?? 0, forgotten: Boolean(s?.forgotten) });
  }
  for (const ref of skill.sources.blocks) {
    const s = signals.blocks.get(ref);
    sources.push({ kind: "block", ref, value: s?.rate ?? 0, evidence: s ? blockCoverage(s) : 0, forgotten: false });
  }
  for (const id of skill.sources.projects) {
    const project = roadmap.projects.find((p) => p.id === id);
    const progress = projectProgress(project, enrollment?.projects[id]);
    sources.push({ kind: "project", ref: id, value: progress.ratio, evidence: progress.repo && progress.done ? 1 : 0, forgotten: false, selfAssessed: true });
  }
  const n = sources.length;
  const score = n ? sources.reduce((sum, s) => sum + s.value * s.evidence, 0) / n : 0;
  const confidence = n ? sources.reduce((sum, s) => sum + s.evidence, 0) / n : 0;
  const enough = confidence >= MIN_CONFIDENCE;
  const forgotten = sources.some((s) => s.forgotten);
  const percent = Math.round(score * 100);
  return {
    id: skill.id,
    score,
    percent,
    confidence,
    enough,
    forgotten,
    ready: enough && score >= READY_SCORE && !forgotten,
    level: confidence === 0 ? 0 : levelOf(score),
    target: skill.target,
    sources,
  };
}

/** Nivel 1-3 a partir del dominio (los mismos cortes que el nivel objetivo de los ejercicios). */
export const levelOf = (score) => (score < 0.4 ? 1 : score < 0.8 ? 2 : 3);

/** Dominio de todas las competencias del itinerario. */
export const allSkills = (roadmap, enrollment, signals) => new Map(roadmap.skills.map((skill) => [skill.id, skillMastery(skill, { roadmap, enrollment, signals })]));

/**
 * Estado de cada fase. El bloqueo depende de sus prerrequisitos (`requires`), nunca de su posición:
 *   locked        algún prerrequisito no está completado (completed o needs_review)
 *   completed     todas sus unidades estudiadas, el proyecto entregado y sus competencias firmes
 *   needs_review  unidades y proyecto hechos, pero alguna competencia no está firme o se está olvidando
 *   in_progress   hay alguna unidad estudiada, entrega o evidencia en sus competencias
 *   available     nada de lo anterior
 * El porcentaje es de contenido estudiado: no es dominio (para eso, `skills`).
 */
export function phaseStates(roadmap, enrollment, signals = emptySignals()) {
  const skills = allSkills(roadmap, enrollment, signals);
  const states = new Map();
  const projects = new Map(roadmap.projects.map((p) => [p.id, p]));
  const visit = (phase) => {
    if (states.has(phase.id)) return states.get(phase.id);
    const units = phase.units.map((u) => ({ id: u.id, done: Boolean(enrollment?.units[u.id]?.done), pending: u.pending }));
    const unitsDone = units.filter((u) => u.done).length;
    const project = phase.project ? projectProgress(projects.get(phase.project), enrollment?.projects[phase.project]) : null;
    const phaseSkills = phase.skills.map((id) => skills.get(id));
    const missing = phase.requires.filter((id) => !["completed", "needs_review"].includes(visit(roadmap.phases.find((p) => p.id === id)).status));
    let status;
    if (missing.length) status = "locked";
    else if (unitsDone === units.length && (!project || project.delivered)) status = phaseSkills.every((s) => s.ready) ? "completed" : "needs_review";
    else if (unitsDone || project?.done || phaseSkills.some((s) => s.confidence > 0)) status = "in_progress";
    else status = "available";
    const state = {
      id: phase.id,
      status,
      missing,
      unitsDone,
      unitsTotal: units.length,
      percent: units.length ? Math.round((unitsDone / units.length) * 100) : 0,
      units,
      project,
      weak: phaseSkills.filter((s) => !s.ready).map((s) => s.id),
    };
    states.set(phase.id, state);
    return state;
  };
  for (const phase of roadmap.phases) visit(phase);
  return { phases: states, skills };
}

/**
 * Resumen y siguiente actividad, con su motivo. Fase activa: la primera en curso o a revisar; si no
 * hay, la primera disponible. Dentro de ella: la primera unidad sin estudiar, luego el proyecto y, si
 * todo está hecho, la competencia más débil. (Sprint 6: la ordenará recommend.js.)
 */
export function overview(roadmap, enrollment, signals = emptySignals()) {
  const { phases, skills } = phaseStates(roadmap, enrollment, signals);
  const list = roadmap.phases.map((p) => phases.get(p.id));
  const unitsTotal = list.reduce((sum, p) => sum + p.unitsTotal, 0);
  const unitsDone = list.reduce((sum, p) => sum + p.unitsDone, 0);
  const active = list.find((p) => p.status === "in_progress" || p.status === "needs_review") ?? list.find((p) => p.status === "available") ?? null;
  let next = null;
  if (active) {
    const phase = roadmap.phases.find((p) => p.id === active.id);
    const unit = phase.units.find((u) => !enrollment?.units[u.id]?.done);
    if (unit) next = { kind: "unit", phase: phase.id, id: unit.id, reason: "next-unit" };
    else if (active.project && !active.project.delivered) next = { kind: "project", phase: phase.id, id: phase.project, reason: "project-pending" };
    else if (active.weak.length) {
      const weakest = [...active.weak].sort((a, b) => skills.get(a).score - skills.get(b).score || a.localeCompare(b))[0];
      next = { kind: "skill", phase: phase.id, id: weakest, reason: skills.get(weakest).forgotten ? "skill-forgotten" : "skill-weak" };
    }
  }
  const measured = [...skills.values()].filter((s) => s.enough);
  return {
    unitsDone,
    unitsTotal,
    percent: unitsTotal ? Math.round((unitsDone / unitsTotal) * 100) : 0,
    completed: list.filter((p) => p.status === "completed").map((p) => p.id),
    active: active?.id ?? null,
    next,
    skillsReady: [...skills.values()].filter((s) => s.ready).map((s) => s.id),
    skillsPending: [...skills.values()].filter((s) => !s.ready).map((s) => s.id),
    skillsMeasured: measured.length,
    phases,
    skills,
  };
}
