/* «Mi Carrera en IA»: pantalla del itinerario profesional (DEC-012, Fase C).

   Rutas (app.js carga este módulo solo en ellas):
     #/carrera                 = #/carrera/resumen
     #/carrera/resumen         siguiente actividad, competencias, etapa actual y puestos más cercanos
     #/carrera/ruta            los 8 módulos con su estado y sus unidades
     #/carrera/competencias    las 32 competencias con su dominio explicado
     #/carrera/proyectos       proyectos reales y sus criterios (las evidencias se añaden en la Fase E)
     #/carrera/plan            plan de 36 meses: mover o alargar etapas
     #/carrera/objetivo        objetivo económico, SOLO en este navegador (career-finance.js)
     #/carrera/preparacion     listas de portfolio, entrevistas y negocio, y qué falta para cada puesto

   No calcula nada nuevo: todo sale de career-data.js (funciones puras) con el dominio de conceptos
   (mastery.js) y la práctica de los cursos de DAW. Marcar una unidad como estudiada organiza, pero no
   sube ninguna competencia. Todo texto del catálogo se escapa. */

import { language, locale } from "../i18n.js";
import { escapeHtml } from "../markdown.js";
import { notFoundHtml } from "../not-found.js";
import { courseBlockStats, loadCourseBank } from "../course-store.js";
import { focusSelector, keepForms } from "../form-keep.js";
import { learning, loadLearningContent } from "../learn/learn-store.js";
import { allStats } from "../learn/mastery.js";
import { upcomingExams } from "../learn/planner.js";
import { planner } from "../learn/planner-store.js";
import {
  allSkillStats,
  criterionMet,
  emptyRoadmap,
  enroll,
  explainSkill,
  indexRoadmap,
  moduleStatuses,
  nextActivities,
  roleCoverage,
  safeHttpsUrl,
  setChecklistItem,
  setStage,
  setUnitStatus,
  skillSummary,
  stagePlan,
} from "./career-data.js";
import { exportFinance, importFinance, projection, removeYear, setTargets, setYear } from "./career-finance.js";
import { financeChart, SERIES } from "./career-chart.js";
import { career, loadRoadmap, onCareerChange, saveCareer } from "./career-store.js";
import { clearFinance, loadFinance, saveFinance } from "./finance-store.js";
import { setPractice, practiceStats } from "./career-practice.js";

export const BASE = "#/carrera";
const DEFAULT_ROADMAP = "applied-ai-engineer";
export const SECTIONS = Object.freeze([
  { id: "resumen", label: "Resumen" },
  { id: "ruta", label: "Ruta" },
  { id: "competencias", label: "Competencias" },
  { id: "proyectos", label: "Proyectos" },
  { id: "plan", label: "Plan" },
  { id: "objetivo", label: "Objetivo" },
  { id: "preparacion", label: "Preparación" },
  { id: "practicas", label: "Prácticas de programación" },
]);

const MODULE_STATUS = {
  bloqueado: "Faltan requisitos (orientativo)",
  disponible: "Disponible",
  "en-curso": "En curso",
  completado: "Completado",
  repasar: "Toca repasar",
};
const SKILL_STATUS = {
  "sin-evidencias": "Sin evidencias",
  insuficiente: "Pocas evidencias",
  aprendiendo: "Aprendiendo",
  progreso: "En progreso",
  adquirida: "Adquirida",
  repasar: "Toca repasar",
};
const CHECKLIST_TITLES = { portfolio: "Portfolio", interview: "Entrevistas", business: "Negocio" };

const $ = (selector) => document.querySelector(selector);
const root = () => $("#career-view");
const lang = language === "en" ? "en" : "es";
const t = (value) => (typeof value === "string" ? value : (value?.[lang] ?? value?.es ?? ""));
const pct = (value) => Math.round((value ?? 0) * 100);
const MONEY = new Intl.NumberFormat(locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
const money = (n) => MONEY.format(n);
const MONTH = new Intl.DateTimeFormat(locale, { month: "long", year: "numeric" });
const monthOf = (day) => MONTH.format(new Date(`${day}T00:00:00`));

/* ---------- Datos ---------- */

let loading = null;
let data = null; // { catalog, index, learnIndex, resources, banks }

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

/** Catálogo y fuentes de las competencias. Si falla lo opcional (cursos, recursos), sigue sin ello. */
function loadData() {
  loading ??= (async () => {
    const catalog = await loadRoadmap(career.active ?? DEFAULT_ROADMAP);
    const index = indexRoadmap(catalog);
    const courses = [...new Set(catalog.skills.flatMap((s) => s.sources.blocks).map((id) => id.split(":")[0]))];
    const [learnIndex, resources, practiceCatalog, ...banks] = await Promise.all([
      loadLearningContent().catch(() => null),
      fetchJson("data/resources.json").then((r) => new Map((r.resources ?? []).map((item) => [item.id, item])), () => new Map()),
      fetchJson("data/career/programming-path-practice.json").catch(() => ({ activities: [] })),
      ...courses.map((id) => loadCourseBank(id).then((bank) => [id, bank], () => null)),
    ]);
    return { catalog, index, learnIndex, resources, practiceCatalog, banks: new Map(banks.filter(Boolean)) };
  })();
  loading.catch(() => {
    loading = null; // sin conexión: se reintenta la próxima vez
  });
  return loading;
}

/** Entradas de los cálculos: dominio de conceptos y práctica de los bloques de los cursos de DAW. */
function inputs() {
  const concepts = data.learnIndex ? allStats(data.learnIndex, learning) : new Map();
  const blocks = new Map();
  for (const [id, bank] of data.banks) {
    for (const [slug, stats] of Object.entries(courseBlockStats(id, bank))) blocks.set(`${id}:${slug}`, stats);
  }
  return { concepts, blocks };
}

const roadmapId = () => career.active ?? DEFAULT_ROADMAP;
/** Progreso del itinerario (sin guardar nada si aún no se ha empezado). */
const progressOf = () => career.roadmaps[roadmapId()] ?? emptyRoadmap();
/** Progreso del itinerario para escribir en él: si aún no se había empezado, se empieza ahora. */
const writable = () => enroll(career, roadmapId());

function compute() {
  const { index } = data;
  const progress = progressOf();
  const ins = inputs();
  const skills = allSkillStats(index, progress, ins);
  const modules = moduleStatuses(index, progress, skills);
  const plan = stagePlan(index, progress);
  const exams = upcomingExams(planner);
  return {
    progress,
    inputs: ins,
    skills,
    modules,
    plan,
    roles: roleCoverage(index, skills),
    next: nextActivities(index, progress, { skills, modules, inputs: ins, exams }),
    summary: skillSummary(skills),
  };
}

/* ---------- Piezas ---------- */

function meter(value, label) {
  const p = pct(value);
  return `<span class="meter" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${p}"><span class="meter__fill" data-meter="${p}"></span></span>`;
}

const badge = (text, kind) => `<span class="career-badge" data-kind="${escapeHtml(kind)}">${escapeHtml(text)}</span>`;
const skillTitle = (id) => t(data.index.skills.get(id)?.title) || id;
const moduleTitle = (id) => t(data.index.modules.get(id)?.title) || id;
const roleTitle = (id) => t(data.catalog.roles.find((r) => r.id === id)?.title) || id;
const projectOf = (id) => data.catalog.projects.find((p) => p.id === id);
const practicesFor = (unitId) => (data.practiceCatalog?.activities ?? []).filter((a) => a.unit === unitId);

function blockTitle(blockId) {
  const [course, slug] = blockId.split(":");
  const block = data.banks.get(course)?.exam.blocks.find((b) => b.slug === slug);
  return block ? t(block.title) : blockId;
}

/** Enlace de una unidad a contenido que ya existe en PLD (concepto, bloque de un curso o recurso). */
function linkHtml(link) {
  if (link.kind === "concept") {
    const title = data.learnIndex?.concepts.get(link.id)?.title ?? link.id;
    return `<a href="#/teoria/${encodeURIComponent(link.id)}">Teoría: ${escapeHtml(title)}</a>`;
  }
  if (link.kind === "block") {
    const [course, slug] = link.id.split(":");
    return `<a href="#/daw/${encodeURIComponent(course)}/practica/${encodeURIComponent(slug)}">Practicar: ${escapeHtml(blockTitle(link.id))}</a>`;
  }
  const resource = data.resources.get(link.id);
  const url = safeHttpsUrl(resource?.url);
  return url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(resource.title)}<span class="visually-hidden"> (se abre en otra pestaña)</span></a>` : escapeHtml(link.id);
}

function nav(section) {
  return `<nav class="dash-nav career-nav" aria-label="Secciones de Mi Carrera en IA"><ul>${SECTIONS.map(
    (s) => `<li><a href="${BASE}/${s.id}"${s.id === section ? ' aria-current="page"' : ""}>${s.label}</a></li>`,
  ).join("")}</ul></nav>`;
}

function hero(state, section) {
  const { catalog } = data;
  const current = state.plan.find((s) => s.current);
  const completed = [...state.modules.values()].filter((m) => m.status === "completado" || m.status === "repasar").length;
  const started = Boolean(career.roadmaps[roadmapId()]?.startedAt);
  return `<header class="course-hero career-hero">
      <p class="eyebrow">Itinerario profesional</p>
      <h1 class="course-hero__title" id="career-title" tabindex="-1">Mi Carrera en IA</h1>
      <p class="course-hero__lead"><strong>${escapeHtml(t(catalog.title))}.</strong> ${escapeHtml(t(catalog.specialization))}</p>
      <dl class="career-facts">
        <div><dt>Competencias adquiridas</dt><dd>${state.summary.acquired.length} de ${state.summary.total}</dd></div>
        <div><dt>Módulos completados</dt><dd>${completed} de ${catalog.modules.length}</dd></div>
        <div><dt>Etapa actual</dt><dd>${current ? escapeHtml(t(catalog.stages.find((s) => s.id === current.id).title)) : "—"}</dd></div>
      </dl>
      ${started ? "" : `<p class="career-start">Aún no has empezado el itinerario. Puedes verlo entero; al empezarlo, el plan de 36 meses arranca hoy.</p><button class="btn btn--primary" type="button" data-career-action="enroll">Empezar el itinerario</button>`}
    </header>${nav(section)}`;
}

/* ---------- Secciones ---------- */

function activityHtml(item) {
  if (item.kind === "unit") return `<a href="${BASE}/ruta#u-${escapeHtml(item.unit)}">${escapeHtml(t(data.index.units.get(item.unit).title))}</a>`;
  if (item.kind === "practice") return linkHtml({ kind: "concept", id: item.concept });
  if (item.kind === "criterion") return `<a href="${BASE}/proyectos#c-${escapeHtml(item.criterion)}">${escapeHtml(t(data.index.criteria.get(item.criterion).title))}</a>`;
  return `<a href="${BASE}/ruta#m-${escapeHtml(item.module)}">Evaluación de ${escapeHtml(moduleTitle(item.module))}</a>`;
}

function renderSummary(state) {
  const { next, roles } = state;
  const activities = next.paused
    ? `<p class="career-note" role="note"><strong>DAW primero.</strong> Tienes «${escapeHtml(next.paused.title)}» ${next.paused.days === 0 ? "hoy" : next.paused.days === 1 ? "mañana" : `dentro de ${next.paused.days} días`}: la ruta no propone nada hasta entonces. <a href="#/aprender">Ir a lo de hoy</a></p>`
    : next.items.length
      ? `<ol class="career-list">${next.items.map((item) => `<li>${activityHtml(item)}<p class="career-muted">${escapeHtml(item.why)}</p></li>`).join("")}</ol>`
      : `<p class="empty-state">No hay ninguna actividad pendiente con los requisitos cumplidos.</p>`;
  const top = roles
    .slice(0, 3)
    .map((r) => `<li><span class="career-row"><strong>${escapeHtml(roleTitle(r.id))}</strong><span>${pct(r.coverage)} %</span></span>${meter(r.coverage, `Cobertura de ${roleTitle(r.id)}`)}</li>`)
    .join("");
  return `<section class="course-section" aria-labelledby="career-next-title">
      <h2 class="section-title" id="career-next-title">Siguiente actividad</h2>${activities}
    </section>
    <section class="course-section" aria-labelledby="career-skills-title">
      <h2 class="section-title" id="career-skills-title">Competencias</h2>
      <p>${state.summary.acquired.length} de ${state.summary.total} adquiridas · dominio medio ${pct(state.summary.progress)} %</p>
      ${meter(state.summary.progress, "Dominio medio de las competencias")}
      <p class="readiness__note">Una competencia sube con práctica, evaluación y proyectos reales. <strong>Marcar una unidad como estudiada no suma nada.</strong> Las evaluaciones de los módulos llegan con su contenido (Fase D).</p>
    </section>
    <section class="course-section" aria-labelledby="career-roles-title">
      <h2 class="section-title" id="career-roles-title">Puestos más cercanos</h2>
      <ul class="career-list">${top}</ul>
      <p class="readiness__note">Cobertura de las competencias que pide cada puesto. No es una probabilidad de encontrar empleo. <a href="${BASE}/preparacion">Ver qué falta</a></p>
    </section>`;
}

function renderRoute(state) {
  const { catalog } = data;
  const units = state.progress.units;
  const levels = new Map(catalog.levels.map((l) => [l.id, t(l.title)]));
  const items = catalog.modules
    .map((m) => {
      const s = state.modules.get(m.id);
      const missing = s.missing.length ? `<p class="career-muted">Requiere: ${s.missing.map(moduleTitle).map(escapeHtml).join(", ")}. Puedes abrirlo igual: solo deja de recomendarse.</p>` : "";
      const list = m.units
        .map((u) => {
          const done = units[u.id]?.status === "hecha";
          return `<li class="career-unit" id="u-${escapeHtml(u.id)}">
              <label class="career-check"><input type="checkbox" data-career-unit="${escapeHtml(u.id)}"${done ? " checked" : ""}> <strong>${escapeHtml(t(u.title))}</strong></label>
              <span class="career-muted">${escapeHtml(levels.get(u.level) ?? u.level)}${u.pending ? " · contenido propio en preparación" : ""}</span>
              ${u.objectives.length ? `<ul class="career-objectives">${u.objectives.map((o) => `<li>${escapeHtml(t(o))}</li>`).join("")}</ul>` : ""}
              ${u.links.length ? `<p class="career-links">${u.links.map(linkHtml).join(" · ")}</p>` : ""}
            </li>`;
        })
        .join("");
      const assessment = s.assessment.available
        ? s.assessment.passed
          ? "Evaluación aprobada"
          : "Evaluación pendiente"
        : "Evaluación: llega con el contenido del módulo (Fase D)";
      return `<li class="career-module" id="m-${escapeHtml(m.id)}">
          <h3 class="career-module__title">${escapeHtml(m.id.toUpperCase())} · ${escapeHtml(t(m.title))} ${badge(MODULE_STATUS[s.status], s.status)}</h3>
          <p>${escapeHtml(t(m.summary))}</p>${missing}
          <p class="career-row"><span>${s.units.done} de ${s.units.total} unidades estudiadas</span><span>${escapeHtml(assessment)}</span></p>
          ${meter(s.units.total ? s.units.done / s.units.total : 0, `Unidades estudiadas de ${t(m.title)}`)}
          <details class="career-details" id="units-${escapeHtml(m.id)}"><summary>Unidades (${m.units.length})</summary><ul class="career-units">${list}</ul></details>
        </li>`;
    })
    .join("");
  return `<section class="course-section" aria-labelledby="career-route-title">
      <h2 class="section-title" id="career-route-title">Programming Path · 17 módulos</h2>
      <p class="readiness__note">Marca las unidades que ya has estudiado para organizarte. Para que cuenten, practica sus conceptos, aprueba la evaluación del módulo y demuéstralo en un proyecto.</p>
      <ol class="career-modules">${items}</ol>
    </section>`;
}

function renderPractices(unit, progress) {
  const activities = practicesFor(unit.id);
  if (!activities.length) return "";
  const stats = practiceStats(activities, progress);
  const cards = activities.map((a) => {
    const saved = progress[a.id] ?? {};
    const escList = (items) => items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    return `<details class="career-practice" id="practice-${escapeHtml(a.id)}">
      <summary><span class="career-row"><strong>${escapeHtml(a.title)}</strong>${badge(saved.done ? "Completada" : "Pendiente", saved.done ? "completado" : "disponible")}</span>
        <span class="career-muted">${escapeHtml(a.level)} · ${Number(a.estimated_hours) || 0} h · ${escapeHtml(a.type)}</span></summary>
      <p>${escapeHtml(a.description)}</p>
      ${a.tasks?.length ? `<h4>Qué hacer</h4><ol>${escList(a.tasks)}</ol>` : ""}
      ${a.deliverables?.length ? `<h4>Entregables</h4><ul>${escList(a.deliverables)}</ul>` : ""}
      ${a.acceptance?.length ? `<h4>Criterios de aceptación</h4><ul>${escList(a.acceptance)}</ul>` : ""}
      <form class="career-practice-form" data-career-practice="${escapeHtml(a.id)}">
        <label class="career-check"><input type="checkbox" name="done"${saved.done ? " checked" : ""}> Marcar como completada</label>
        <label>Enlace a la evidencia (GitHub, demo, documentación)
          <input type="url" name="url" maxlength="240" placeholder="https://..." value="${escapeHtml(saved.url ?? "")}">
        </label>
        <label>Notas / evidencia
          <textarea name="note" maxlength="1000" rows="3" placeholder="Qué implementaste, decisiones y resultados">${escapeHtml(saved.note ?? "")}</textarea>
        </label>
        <button class="btn btn--secondary" type="submit">Guardar práctica</button>
        <p class="form-message" role="status">${saved.at ? `Guardado: ${escapeHtml(new Date(saved.at).toLocaleDateString(locale))}` : "Aún no guardada"}</p>
      </form>
    </details>`;
  }).join("");
  return `<section class="career-practices" aria-label="Prácticas de la unidad">
    <p class="career-muted">Prácticas de brechas curriculares: ${stats.done} de ${stats.total} completadas</p>
    ${meter(stats.ratio, `Prácticas completadas de ${t(unit.title)}`)}
    ${cards}
  </section>`;
}

function renderPracticeCatalog(state) {
  const activities = data.practiceCatalog?.activities ?? [];
  const progress = state.progress.practice ?? {};
  const stats = practiceStats(activities, progress);
  const moduleNames = { m4: "Python intermedio y profesional", m6: "Algoritmos y estructuras de datos", m8: "Frontend moderno", m9: "Bases de datos y SQL", m10: "Backend y APIs", m11: "Ingeniería de software", m12: "Java y programación empresarial", m13: "Linux, redes y sistemas", m14: "DevOps, CI/CD y cloud", m15: "Seguridad en el desarrollo", m16: "IA y Machine Learning aplicado", m17: "Especialización y nivel experto" };
  const grouped = new Map();
  for (const activity of activities) {
    const modules = grouped.get(activity.module) ?? new Map();
    const units = modules.get(activity.unit) ?? [];
    units.push(activity); modules.set(activity.unit, units); grouped.set(activity.module, modules);
  }
  const sections = [...grouped.entries()].map(([moduleId, units]) => {
    const moduleActivities = [...units.values()].flat();
    const moduleStats = practiceStats(moduleActivities, progress);
    const unitHtml = [...units.entries()].map(([unitId, unitActivities]) => `<section class="career-practice-unit"><h4>${escapeHtml(unitId)}</h4>${renderPracticeCards(unitActivities, progress)}</section>`).join("");
    return `<details class="career-module" id="practice-module-${escapeHtml(moduleId)}"><summary><h3 class="career-module__title">${escapeHtml(moduleId.toUpperCase())} · ${escapeHtml(moduleNames[moduleId] ?? moduleId)} <span class="career-muted">${moduleStats.done}/${moduleStats.total} completadas</span></h3></summary>${meter(moduleStats.ratio, `Prácticas completadas de ${moduleId}`)}${unitHtml}</details>`;
  }).join("");
  return `<section class="course-section" aria-labelledby="career-practices-title"><h2 class="section-title" id="career-practices-title">Prácticas de programación</h2><p>Retos añadidos para cubrir brechas del currículo. El progreso y las evidencias se guardan en el mismo documento Career y se sincronizan con tu cuenta si has iniciado sesión.</p><p class="career-row"><strong>${stats.done} de ${stats.total} completadas</strong><span>${Math.round(stats.ratio * 100)} %</span></p>${meter(stats.ratio, "Progreso de prácticas")}${sections || '<p class="empty-state">No hay prácticas disponibles en el catálogo.</p>'}</section>`;
}

function renderPracticeCards(activities, progress) {
  const cards = activities.map((a) => {
    const saved = progress[a.id] ?? {};
    const escList = (items) => items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    return `<details class="career-practice" id="practice-${escapeHtml(a.id)}"><summary><span class="career-row"><strong>${escapeHtml(a.title)}</strong>${badge(saved.done ? "Completada" : "Pendiente", saved.done ? "completado" : "disponible")}</span><span class="career-muted">${escapeHtml(a.level)} · ${Number(a.estimated_hours) || 0} h · ${escapeHtml(a.type)}</span></summary><p>${escapeHtml(a.description)}</p>${a.tasks?.length ? `<h4>Qué hacer</h4><ol>${escList(a.tasks)}</ol>` : ""}${a.deliverables?.length ? `<h4>Entregables</h4><ul>${escList(a.deliverables)}</ul>` : ""}${a.acceptance?.length ? `<h4>Criterios de aceptación</h4><ul>${escList(a.acceptance)}</ul>` : ""}<form class="career-practice-form" data-career-practice="${escapeHtml(a.id)}"><label class="career-check"><input type="checkbox" name="done"${saved.done ? " checked" : ""}> Marcar como completada</label><label>Enlace a la evidencia (GitHub, demo, documentación)<input type="url" name="url" maxlength="240" placeholder="https://..." value="${escapeHtml(saved.url ?? "")}"></label><label>Notas / evidencia<textarea name="note" maxlength="1000" rows="3" placeholder="Qué implementaste, decisiones y resultados">${escapeHtml(saved.note ?? "")}</textarea></label><button class="btn btn--secondary" type="submit">Guardar práctica</button><p class="form-message" role="status">${saved.at ? `Guardado: ${escapeHtml(new Date(saved.at).toLocaleDateString(locale))}` : "Aún no guardada"}</p></form></details>`;
  }).join("");
  return `<div class="career-practices">${cards}</div>`;
}
function renderSkills(state) {
  const groups = data.catalog.categories
    .map((c) => {
      const skills = data.catalog.skills.filter((s) => s.category === c.id);
      if (!skills.length) return "";
      const rows = skills
        .map((s) => {
          const stats = state.skills.get(s.id);
          return `<li><span class="career-row"><strong>${escapeHtml(t(s.title))}</strong>${badge(SKILL_STATUS[stats.status], stats.status)}</span>
              ${meter(stats.score, `Dominio de ${t(s.title)}`)}
              <p class="career-muted">${pct(stats.score)} % · ${escapeHtml(explainSkill(stats))}</p></li>`;
        })
        .join("");
      return `<h3 class="career-subtitle">${escapeHtml(t(c.title))}</h3><ul class="career-list">${rows}</ul>`;
    })
    .join("");
  return `<section class="course-section" aria-labelledby="career-skill-list-title">
      <h2 class="section-title" id="career-skill-list-title">Competencias</h2>
      <p class="readiness__note">Dominio de 0 a 100 %: evaluación (40 %), práctica (30 %) y proyecto (30 %), sobre las fuentes que declara cada competencia. «Adquirida» pide al menos un 70 % y evidencias suficientes.</p>
      ${groups}
    </section>`;
}

function renderProjects(state) {
  const items = data.catalog.projects
    .map((p) => {
      const repo = safeHttpsUrl(p.repo);
      const criteria = p.criteria
        .map((c) => {
          const met = criterionMet(state.progress, c.id);
          return `<li id="c-${escapeHtml(c.id)}"><span class="career-row"><span>${escapeHtml(t(c.title))}</span>${badge(met ? "Cumplido" : "Pendiente", met ? "completado" : "disponible")}</span>
              <span class="career-muted">${escapeHtml(moduleTitle(c.module))} · ${c.skills.map(skillTitle).map(escapeHtml).join(", ")}</span></li>`;
        })
        .join("");
      return `<li class="career-module"><h3 class="career-module__title">${escapeHtml(t(p.title))}</h3>
          <p>${escapeHtml(t(p.description))}</p>
          ${repo ? `<p><a href="${escapeHtml(repo)}" target="_blank" rel="noopener noreferrer">Repositorio<span class="visually-hidden"> (se abre en otra pestaña)</span></a></p>` : '<p class="career-muted">Sin repositorio enlazado.</p>'}
          <ul class="career-list">${criteria}</ul></li>`;
    })
    .join("");
  return `<section class="course-section" aria-labelledby="career-projects-title">
      <h2 class="section-title" id="career-projects-title">Proyectos reales</h2>
      <p class="readiness__note">Un criterio solo cuenta cuando está marcado <strong>y</strong> tiene una evidencia (PR, tests, demo…). Añadir evidencias desde aquí llega en la Fase E.</p>
      <ul class="career-modules">${items}</ul>
    </section>`;
}

function renderPlan(state) {
  const { catalog } = data;
  const started = Boolean(career.roadmaps[roadmapId()]?.startedAt);
  const rows = state.plan
    .map((s) => {
      const stage = catalog.stages.find((x) => x.id === s.id);
      const when = s.current ? badge("Etapa actual", "en-curso") : s.past ? badge("Terminada", "completado") : "";
      return `<li class="career-module">
          <h3 class="career-module__title">${escapeHtml(t(stage.title))} ${when}</h3>
          <p>${escapeHtml(monthOf(s.start))} – ${escapeHtml(monthOf(s.end))} · ${s.months} meses · ${s.modules.map(moduleTitle).map(escapeHtml).join(", ")}</p>
          ${
            started
              ? `<form class="career-form" id="stage-${escapeHtml(s.id)}" data-career-stage="${escapeHtml(s.id)}">
              <label>Empieza <input type="date" name="start" value="${escapeHtml(s.start)}" required></label>
              <label>Meses <input type="number" name="months" min="1" max="24" step="1" value="${s.months}" required></label>
              <button class="btn btn--ghost" type="submit">Guardar</button>
              ${s.custom ? `<button class="btn btn--ghost" type="button" data-career-action="reset-stage" data-stage="${escapeHtml(s.id)}">Volver al plan original</button>` : ""}
            </form>`
              : ""
          }
        </li>`;
    })
    .join("");
  return `<section class="course-section" aria-labelledby="career-plan-title">
      <h2 class="section-title" id="career-plan-title">Plan de 36 meses</h2>
      <p class="readiness__note">Plan orientativo: cada etapa empieza donde acaba la anterior. Si mueves o alargas una, las siguientes se desplazan.${started ? "" : " Empieza el itinerario para poder ajustarlo."}</p>
      <p class="visually-hidden" role="status" id="career-plan-status"></p>
      <ol class="career-modules">${rows}</ol>
    </section>`;
}

function financeTable(rows, target) {
  if (!rows.length) return `<p class="empty-state">Aún no has metido ningún año.</p>`;
  const body = rows
    .map(
      (r) => `<tr><th scope="row">${r.year}</th><td>${money(r.salary)}</td><td>${money(r.revenue)}</td><td>${money(r.expenses)}</td><td>${money(r.profit)}</td><td>${money(r.combined)}</td>
        <td>${target === null ? "—" : r.reached ? "Alcanzado" : `Faltan ${money(r.gap)}`}</td>
        <td><button class="btn btn--ghost btn--sm" type="button" data-career-action="remove-year" data-year="${r.year}">Quitar ${r.year}</button></td></tr>`,
    )
    .join("");
  return `<div class="career-table-wrap" tabindex="0" role="region" aria-labelledby="career-table-caption"><table class="career-table">
      <caption id="career-table-caption">Datos por año (antes de impuestos)</caption>
      <thead><tr><th scope="col">Año</th><th scope="col">Salario bruto</th><th scope="col">Facturación</th><th scope="col">Gastos</th><th scope="col">Beneficio</th><th scope="col">Combinado</th><th scope="col">Objetivo</th><th scope="col"><span class="visually-hidden">Acciones</span></th></tr></thead>
      <tbody>${body}</tbody></table></div>`;
}

function renderGoal() {
  const finance = loadFinance();
  const rows = projection(finance);
  const target = finance.targets?.combined ?? null;
  const chart = financeChart(rows, { target, money });
  const legend = SERIES.map((s) => `<li><span class="cc-key ${s.css}" aria-hidden="true"></span>${escapeHtml(s.label)}</li>`).join("") + (target === null ? "" : `<li><span class="cc-key cc-target" aria-hidden="true"></span>Objetivo combinado</li>`);
  const bands = data.catalog.salary.bands.map((b) => `<li>${escapeHtml(t(b.title))}: ${b.max === null ? `${money(b.min)} o más` : `${money(b.min)} – ${money(b.max)}`}</li>`).join("");
  const thisYear = new Date().getFullYear();
  return `<section class="course-section" aria-labelledby="career-goal-title">
      <h2 class="section-title" id="career-goal-title">Objetivo económico</h2>
      <p class="career-note" role="note"><strong>Solo en este navegador.</strong> Estos datos no se suben a tu cuenta ni se ven en otro dispositivo. Cerrar sesión no los borra. Haz una copia con «Exportar».</p>
      <form class="career-form" id="career-targets" data-career-form="targets">
        <label>Objetivo de ingreso combinado anual (€) <input type="number" name="combined" min="0" max="10000000" step="1" inputmode="numeric" value="${finance.targets?.combined ?? ""}"></label>
        <label>Salario bruto objetivo (€) <input type="number" name="salary" min="0" max="10000000" step="1" inputmode="numeric" value="${finance.targets?.salary ?? ""}"></label>
        <button class="btn btn--primary" type="submit">Guardar objetivo</button>
        <p class="form-message" role="status"></p>
      </form>
      <h3 class="career-subtitle">Un año (real o previsto)</h3>
      <form class="career-form" id="career-year" data-career-form="year">
        <label>Año <input type="number" name="year" min="2000" max="2099" step="1" inputmode="numeric" value="${thisYear}" required></label>
        <label>Salario bruto (€) <input type="number" name="salary" min="0" max="10000000" step="1" inputmode="numeric" value="0" required></label>
        <label>Facturación sin IVA (€) <input type="number" name="revenue" min="0" max="10000000" step="1" inputmode="numeric" value="0" required></label>
        <label>Gastos del negocio (€) <input type="number" name="expenses" min="0" max="10000000" step="1" inputmode="numeric" value="0" required></label>
        <button class="btn btn--primary" type="submit">Guardar año</button>
        <p class="form-message" role="status"></p>
      </form>
      <p class="readiness__note">Beneficio = facturación − gastos (incluida la cuota de autónomo). Combinado = salario bruto + beneficio. Nunca se suma la facturación al salario. Sin IRPF: depende de tu situación.</p>
      ${chart ? `<figure class="career-chart" tabindex="0" aria-label="Gráfica de la evolución económica (se puede desplazar)">${chart}<figcaption><ul class="cc-legend">${legend}</ul></figcaption></figure>` : rows.length ? `<p class="career-muted">Con dos años o más verás la evolución en una gráfica.</p>` : ""}
      ${financeTable(rows, target)}
      <h3 class="career-subtitle">Bandas salariales del itinerario</h3>
      <ul class="career-list">${bands}</ul>
      <p class="readiness__note">${escapeHtml(t(data.catalog.salary.source))}</p>
      <h3 class="career-subtitle">Copia de seguridad</h3>
      <div class="career-actions">
        <button class="btn btn--ghost" type="button" data-career-action="export-finance">Exportar mis datos económicos (JSON)</button>
        <label class="btn btn--ghost career-file">Importar desde un archivo JSON <input type="file" accept="application/json,.json" data-career-import class="visually-hidden"></label>
        <button class="btn btn--danger" type="button" data-career-action="clear-finance">Borrar mis datos económicos</button>
      </div>
      <p class="form-message" role="status" id="career-finance-status"></p>
    </section>`;
}

function renderPreparation(state) {
  const { catalog } = data;
  const lists = Object.entries(catalog.checklists)
    .map(
      ([name, items]) => `<h3 class="career-subtitle">${escapeHtml(CHECKLIST_TITLES[name] ?? name)}</h3><ul class="career-list">${items
        .map((i) => `<li><label class="career-check"><input type="checkbox" data-career-check="${escapeHtml(i.id)}"${state.progress.checklists[i.id]?.done ? " checked" : ""}> ${escapeHtml(t(i.title))}</label></li>`)
        .join("")}</ul>`,
    )
    .join("");
  const roles = state.roles
    .map((r) => {
      const missing = r.missing.slice(0, 5).map((m) => `<li>${escapeHtml(skillTitle(m.id))}: ${pct(m.score)} % de ${pct(m.target)} %</li>`).join("");
      return `<li><span class="career-row"><strong>${escapeHtml(roleTitle(r.id))}</strong><span>${pct(r.coverage)} %</span></span>${meter(r.coverage, `Cobertura de ${roleTitle(r.id)}`)}
          ${r.ready ? "<p>Tienes el nivel que pide en todas sus competencias.</p>" : `<p class="career-muted">Lo que más falta:</p><ul class="career-objectives">${missing}</ul>`}</li>`;
    })
    .join("");
  return `<section class="course-section" aria-labelledby="career-checklists-title">
      <h2 class="section-title" id="career-checklists-title">Listas de comprobación</h2>${lists}
    </section>
    <section class="course-section" aria-labelledby="career-role-list-title">
      <h2 class="section-title" id="career-role-list-title">Puestos objetivo</h2>
      <ul class="career-list">${roles}</ul>
    </section>`;
}

const RENDER = { resumen: renderSummary, ruta: renderRoute, competencias: renderSkills, proyectos: renderProjects, plan: renderPlan, objetivo: renderGoal, preparacion: renderPreparation, practicas: renderPracticeCatalog };

/* ---------- Rutas ---------- */

/** Sección de la ruta, "resumen" para #/carrera y null si no existe. */
export function sectionOf(route) {
  const rest = route.slice(BASE.length).split("#")[0];
  if (rest === "" || rest === "/") return "resumen";
  const id = rest.replace(/^\//, "");
  return Object.hasOwn(RENDER, id) ? id : null;
}

function html(section) {
  if (!section) return notFoundHtml({ titleId: "career-title", route: location.hash, what: "esta sección", back: { href: BASE, label: "Volver a Mi Carrera en IA" } });
  const state = compute();
  return `${hero(state, section)}${RENDER[section](state)}`;
}

async function render(route, { focus = false } = {}) {
  if (!data) root().innerHTML = `<p class="empty-state" id="career-title" tabindex="-1">Cargando el itinerario…</p>`;
  try {
    data = await loadData();
  } catch {
    root().innerHTML = `<div class="course-section"><h1 class="section-title" id="career-title" tabindex="-1">No se pudo cargar el itinerario</h1><p>Comprueba la conexión y vuelve a intentarlo.</p><button class="btn btn--primary" type="button" data-career-action="retry">Reintentar</button></div>`;
    if (focus) $("#career-title")?.focus();
    return;
  }
  if (location.hash !== route) return; // el alumno se fue mientras cargaba
  const section = sectionOf(route);
  root().innerHTML = html(section);
  const label = SECTIONS.find((s) => s.id === section)?.label;
  document.title = `${label && section !== "resumen" ? `${label} · ` : ""}Mi Carrera en IA · Python Learning Dashboard`;
  // #/carrera/ruta#u-<unidad>: con rutas por hash el navegador no baja solo hasta el elemento
  const target = route.split("#")[2] && root().querySelector(`#${CSS.escape(route.split("#")[2])}`);
  if (target) {
    target.closest("details")?.setAttribute("open", "");
    target.scrollIntoView({ block: "start" });
    if (focus) (target.querySelector("input, a") ?? target).focus({ preventScroll: true });
  } else if (focus) $("#career-title")?.focus();
}

/** Repinta la sección a la vista sin perder el foco, lo que se esté escribiendo ni las listas abiertas. */
function repaint() {
  const container = root();
  if (!data || container.hidden || !location.hash.startsWith(BASE)) return;
  const focused = focusSelector(container);
  const open = [...container.querySelectorAll("details[open][id]")].map((d) => d.id);
  keepForms(container, () => {
    container.innerHTML = html(sectionOf(location.hash));
  });
  for (const id of open) container.querySelector(`#${CSS.escape(id)}`)?.setAttribute("open", "");
  if (focused) container.querySelector(focused)?.focus({ preventScroll: true });
}

/* ---------- Acciones ---------- */

function say(selector, text, ok = true) {
  const box = root().querySelector(selector);
  if (!box) return;
  box.textContent = text;
  if (ok) box.dataset.ok = "true";
  else delete box.dataset.ok;
}

/** Importe entero de un campo; vacío = null (sin objetivo). */
function euros(value) {
  if (value === "" || value === null) return null;
  const n = Number(value);
  return Number.isInteger(n) ? n : NaN;
}

function download(text, name) {
  const url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

let confirmClear = false;

function onClick(event) {
  const button = event.target.closest("[data-career-action]");
  if (!button) return;
  const action = button.dataset.careerAction;
  if (action === "retry") return render(location.hash, { focus: true });
  if (action === "enroll") {
    writable();
    saveCareer();
    return $("#career-title")?.focus();
  }
  if (action === "reset-stage") {
    setStage(writable(), button.dataset.stage, { start: null, months: null });
    return saveCareer();
  }
  if (action === "export-finance") {
    download(exportFinance(loadFinance()), `pld-datos-economicos-${new Date().toISOString().slice(0, 10)}.json`);
    return say("#career-finance-status", "Archivo descargado. Guárdalo en un sitio seguro.");
  }
  if (action === "remove-year") {
    const finance = loadFinance();
    removeYear(finance, button.dataset.year);
    saveFinance(finance);
    repaint();
    return say("#career-finance-status", `Año ${button.dataset.year} quitado.`);
  }
  if (action === "clear-finance") {
    if (!confirmClear) {
      confirmClear = true;
      button.textContent = "Pulsa otra vez para borrarlos: no se pueden recuperar";
      return;
    }
    confirmClear = false;
    clearFinance();
    repaint();
    return say("#career-finance-status", "Datos económicos borrados de este navegador.");
  }
}

function onChange(event) {
  const input = event.target;
  if (input.matches("[data-career-unit]")) {
    setUnitStatus(writable(), input.dataset.careerUnit, input.checked ? "hecha" : "pendiente");
    saveCareer();
  } else if (input.matches("[data-career-check]")) {
    setChecklistItem(writable(), input.dataset.careerCheck, input.checked);
    saveCareer();
  } else if (input.matches("[data-career-import]")) {
    const file = input.files?.[0];
    if (!file) return;
    file.text().then((text) => {
      const finance = loadFinance();
      const result = importFinance(finance, text);
      if (result.ok) saveFinance(finance);
      repaint();
      say("#career-finance-status", result.ok ? `Importado: ${result.years} año(s). No se ha borrado nada de lo que ya había.` : result.error, result.ok);
    });
  }
}

function onSubmit(event) {
  const form = event.target;
  if (form.matches("[data-career-stage]")) {
    event.preventDefault();
    const fields = new FormData(form);
    setStage(writable(), form.dataset.careerStage, { start: fields.get("start"), months: Number(fields.get("months")) });
    saveCareer();
    say("#career-plan-status", "Etapa guardada. Las siguientes se han desplazado.");
    return;
  }
  const practiceId = form.dataset.careerPractice;
  if (practiceId) {
    event.preventDefault();
    const fields = new FormData(form);
    const url = String(fields.get("url") ?? "").trim();
    const note = String(fields.get("note") ?? "").trim();
    if (url && !safeHttpsUrl(url)) return say(`#practice-${practiceId} .form-message`, "El enlace debe ser HTTPS, sin credenciales y con dominio válido.", false);
    const progress = writable();
    if (!setPractice(progress, practiceId, { done: fields.get("done") === "on", url, note })) return say(`#practice-${practiceId} .form-message`, "No se pudo guardar la práctica.", false);
    saveCareer();
    repaint();
    return say(`#practice-${practiceId} .form-message`, "Práctica guardada y sincronizable con tu cuenta.");
  }
  const kind = form.dataset.careerForm;
  if (!kind) return;
  event.preventDefault();
  const fields = new FormData(form);
  const finance = loadFinance();
  let message;
  if (kind === "targets") {
    const combined = euros(fields.get("combined"));
    const salary = euros(fields.get("salary"));
    if (Number.isNaN(combined) || Number.isNaN(salary)) return say(`#${form.id} .form-message`, "Los importes son euros enteros.", false);
    setTargets(finance, { combined, salary });
    message = "Objetivo guardado en este navegador.";
  } else {
    const year = fields.get("year");
    const ok = setYear(finance, year, { salary: euros(fields.get("salary")), revenue: euros(fields.get("revenue")), expenses: euros(fields.get("expenses")) });
    if (!ok) return say(`#${form.id} .form-message`, "Revisa el año (2000-2099) y que los importes sean euros enteros entre 0 y 10.000.000.", false);
    message = `Año ${year} guardado en este navegador.`;
  }
  saveFinance(finance);
  form.reset();
  root().innerHTML = html(sectionOf(location.hash)); // lo ha pedido el alumno: la vista nueva manda
  root().querySelector(`#${form.id} button[type=submit]`)?.focus();
  say(`#${form.id} .form-message`, message);
}

/* ---------- Entrada ---------- */

let listening = false;

/** Muestra «Mi Carrera en IA». */
export function openCareer(route, { moveFocus = true } = {}) {
  if (!listening) {
    const view = root();
    view.addEventListener("click", onClick);
    view.addEventListener("change", onChange);
    view.addEventListener("submit", onSubmit);
    onCareerChange(repaint); // cambios propios y lo que llega de la cuenta
    listening = true;
  }
  confirmClear = false;
  return render(route, { focus: moveFocus });
}

/** Repinta si está a la vista (al llegar el progreso de la cuenta o de los cursos). */
export function refreshCareer() {
  repaint();
}
