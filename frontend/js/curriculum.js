/* Currículo oficial de DAW en Castilla y León: lee data/curriculum/daw-cyl.json.

   Rutas (las pinta daw.js):
     #/daw/curriculo            módulos por curso, con horas y estado
     #/daw/curriculo/<código>   resultados de aprendizaje, criterios y contenidos de un módulo

   El JSON lo genera scripts/curriculum/build_curriculum.py a partir del BOE y del BOCYL.
   Aquí solo se muestra: no se añade ni se interpreta nada. */

import { DAW_COURSES } from "./course-store.js";
import { escapeHtml, safeUrl } from "./markdown.js";

const DATA_URL = "data/curriculum/daw-cyl.json";
const COURSES = [
  { course: 1, title: "Primer curso" },
  { course: 2, title: "Segundo curso" },
  { course: null, title: "Sin curso indicado en la orden" },
];

let loading = null;

/** Descarga el catálogo una vez. Si falla, se vuelve a intentar en la siguiente visita. */
export function loadCurriculum() {
  if (!loading) {
    loading = fetch(DATA_URL).then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    });
    loading.catch(() => (loading = null));
  }
  return loading;
}

/** Módulos agrupados por curso, en el orden de la orden. Los grupos vacíos no aparecen. */
export function modulesByCourse(modules) {
  return COURSES.map(({ course, title }) => ({ course, title, modules: modules.filter((m) => m.course === course) })).filter(
    (group) => group.modules.length,
  );
}

const courseTitle = (id) => DAW_COURSES.find((c) => c.id === id)?.title ?? id;
const moduleHref = (m) => `#/daw/curriculo/${encodeURIComponent(m.id)}`;
const label = (m) => (m.code ? `${m.code} · ${m.name}` : m.name);

function platformLinks(module) {
  if (!module.platformCourses.length) return "—";
  const links = module.platformCourses.map((id) => `<a href="#/daw/${encodeURIComponent(id)}">${escapeHtml(courseTitle(id))}</a>`);
  return `${links.join(", ")} (${module.platformQuestions} preguntas)`;
}

function statusText(module) {
  return module.status === "oficial" ? `${module.learningOutcomes.length} RA oficiales` : "RA pendientes";
}

function sourceLink(data, ref) {
  const source = data.sources.find((s) => s.id === ref?.split("#")[0]);
  return source ? `<a href="${safeUrl(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.title)}</a>` : "";
}

function notice(data) {
  return `<p class="curr-notice" role="note">${escapeHtml(data.notice)}</p>`;
}

/* ---------- Índice ---------- */

function renderIndex(data) {
  const groups = modulesByCourse(data.modules)
    .map(
      (group) => `
      <section class="course-section" aria-labelledby="curr-course-${group.course ?? "none"}">
        <h2 class="section-title" id="curr-course-${group.course ?? "none"}">${escapeHtml(group.title)}</h2>
        <div class="table-wrap">
          <table class="history curr-table">
            <caption class="visually-hidden">Módulos de ${escapeHtml(group.title.toLowerCase())}</caption>
            <thead><tr><th scope="col">Módulo</th><th scope="col">Horas</th><th scope="col">Horas por semana</th>
              <th scope="col">Estado</th><th scope="col">En la plataforma</th></tr></thead>
            <tbody>${group.modules
              .map(
                (m) => `
              <tr>
                <th scope="row"><a href="${moduleHref(m)}">${escapeHtml(label(m))}</a></th>
                <td>${m.hours}</td>
                <td>${m.weeklyHours ?? "—"}</td>
                <td><span class="curr-status curr-status--${m.status}">${statusText(m)}</span></td>
                <td>${platformLinks(m)}</td>
              </tr>`,
              )
              .join("")}</tbody>
          </table>
        </div>
      </section>`,
    )
    .join("");
  return `
    <p class="daw-crumb"><a href="#/daw">Preparación DAW</a> › <a href="#/daw/cursos">Cursos de DAW</a></p>
    <header class="course-hero">
      <p class="eyebrow">${escapeHtml(data.cycle.region)} · ${data.cycle.hours} horas</p>
      <h1 class="course-hero__title" id="daw-title" tabindex="-1">Currículo oficial de <em>DAW</em></h1>
      <p class="course-hero__lead">Los módulos de ${escapeHtml(data.cycle.name)}, con sus resultados de aprendizaje y
        criterios de evaluación tal como los publica la normativa.</p>
    </header>
    ${notice(data)}
    ${groups}
    <section class="course-section" aria-labelledby="curr-sources-title">
      <h2 class="section-title" id="curr-sources-title">Fuentes</h2>
      <ul class="curr-sources">${data.sources
        .map((s) => `<li>${sourceLink(data, s.id)}: ${escapeHtml(s.what)}.</li>`)
        .join("")}</ul>
    </section>`;
}

/* ---------- Un módulo ---------- */

function outcomesHtml(module) {
  return module.learningOutcomes
    .map(
      (ra) => `
      <details class="daw-faq">
        <summary>RA${ra.number}. ${escapeHtml(ra.text)}</summary>
        <p class="curr-label">Criterios de evaluación (${ra.criteria.length}):</p>
        <ul class="curr-criteria">${ra.criteria.map((c) => `<li><span class="curr-letter">${escapeHtml(c.letter)})</span> ${escapeHtml(c.text)}</li>`).join("")}</ul>
      </details>`,
    )
    .join("");
}

function contentsHtml(module) {
  return module.contents
    .map(
      (block) => `
      <details class="daw-faq">
        <summary>${escapeHtml(block.title)}</summary>
        <ul>${block.items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </details>`,
    )
    .join("");
}

function renderModule(data, module) {
  const facts = [
    ["Curso", module.course ? `${module.course}º` : "No indicado"],
    ["Horas en Castilla y León", module.hours],
    ["Horas por semana", module.weeklyHours ?? "—"],
    ["Horas mínimas estatales", module.stateMinHours ?? "—"],
    ["Créditos ECTS", module.ects ?? "—"],
  ]
    .map(([term, value]) => `<div><dt>${term}</dt><dd>${escapeHtml(String(value))}</dd></div>`)
    .join("");
  const official = module.status === "oficial";
  const pendingSource = sourceLink(data, module.outcomesSource);
  return `
    <p class="daw-crumb"><a href="#/daw">Preparación DAW</a> › <a href="#/daw/curriculo">Currículo oficial</a></p>
    <header class="course-hero">
      <p class="eyebrow">${module.code ? `Módulo ${escapeHtml(module.code)}` : "Módulo optativo"}</p>
      <h1 class="course-hero__title" id="daw-title" tabindex="-1">${escapeHtml(module.name)}</h1>
    </header>
    <dl class="curr-facts">${facts}</dl>
    ${module.note ? `<p class="curr-notice" role="note">${escapeHtml(module.note)}</p>` : ""}
    <p>Cursos de la plataforma que lo trabajan: ${platformLinks(module)}.</p>
    ${notice(data)}
    ${
      official
        ? `<section class="course-section" aria-labelledby="curr-ra-title">
            <h2 class="section-title" id="curr-ra-title">Resultados de aprendizaje (${module.learningOutcomes.length})</h2>
            ${outcomesHtml(module)}
          </section>
          <section class="course-section" aria-labelledby="curr-contents-title">
            <h2 class="section-title" id="curr-contents-title">Contenidos básicos</h2>
            ${contentsHtml(module)}
          </section>
          ${module.contribution ? `<p class="curr-muted">${escapeHtml(module.contribution)}</p>` : ""}
          <p class="curr-muted">Fuente: ${sourceLink(data, module.outcomesSource)}. Horas y curso: ${sourceLink(data, module.source)}.</p>`
        : `<p class="empty-state">Los resultados de aprendizaje de este módulo todavía no se han incorporado al catálogo${
            pendingSource ? `. Están en ${pendingSource}` : ""
          }.</p>
          <p class="curr-muted">Horas y curso: ${sourceLink(data, module.source)}.</p>`
    }`;
}

/** HTML de la ruta `#/daw/curriculo[/<id>]`. */
export function renderCurriculum(data, id) {
  if (!id) return renderIndex(data);
  const module = data.modules.find((m) => m.id === id);
  if (module) return renderModule(data, module);
  return `
    <p class="daw-crumb"><a href="#/daw/curriculo">Currículo oficial</a></p>
    <p class="empty-state" id="daw-title" tabindex="-1">No hay ningún módulo «${escapeHtml(id)}» en el catálogo.
      <a href="#/daw/curriculo">Ver todos los módulos</a></p>`;
}
