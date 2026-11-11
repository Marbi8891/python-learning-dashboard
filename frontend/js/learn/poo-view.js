/* Módulo de POO: índice del módulo (#/poo) y página de unidad (#/teoria/<unidad>).

   Una unidad es un concepto del núcleo con campos propios (objetivos, lecciones con ejemplos y
   mini-quiz, ejercicios guiados y autónomos, autoevaluación, resumen, criterios de superación y
   currículo). El dominio, los errores y el repaso son los del motor adaptativo (mastery.js):
   completar una lección solo organiza el estudio y no cuenta como competencia demostrada.

   Funciones puras que devuelven HTML: los clics los atiende learn-app.js (data-learn="…"). */

import { activeErrors, allStats, sectionsDone } from "./mastery.js";
import { codeBlock, errorExplanation, escapeHtml, KIND_LABEL, meter, percent, renderInline, renderMarkdown, statusBadge } from "./ui.js";

const STATUS_TEXT = {
  verified: "Validada",
  proposed: "Propuesta de la plataforma, pendiente de validar",
  unassigned: "Sin correspondencia",
};

/** El módulo de POO de learning.json, o null si el contenido no lo trae. */
export const pooModule = (index) => (index.data.modules ?? []).find((m) => m.id === "poo") ?? null;

/** Unidades publicadas del módulo, en orden. */
export const availableUnits = (index) => (pooModule(index)?.units ?? []).filter((u) => u.available && index.concepts.has(u.id));

/** Título corto de un ejercicio para las listas: el texto en negrita del principio
    («**Ejercicio guiado: la clase `Alumno`.**») o, si no lo hay, la primera línea del enunciado. */
export function exerciseTitle(ex) {
  const bold = ex.q.match(/^\*\*(.+?)\*\*/);
  const first = bold ? bold[1].replace(/\.$/, "") : ex.q.split("\n")[0];
  return first.length > 140 ? `${first.slice(0, 137)}…` : first;
}

/** ¿Resuelto alguna vez? Para los criterios de superación basta con un acierto (okAt). */
const solved = (learning, id) => Boolean(learning.ex[id]?.okAt || learning.ex[id]?.h?.includes(true));

function exerciseList(index, learning, ids, group, concept) {
  const items = ids
    .map((id) => {
      const ex = index.exercises.get(id);
      const state = solved(learning, id) ? "✓ Resuelto" : learning.ex[id] ? "Intentado" : "Sin hacer";
      return `<li class="lx-unit-ex"><span class="lx-kind">${KIND_LABEL[ex.kind]}</span> ${renderInline(exerciseTitle(ex))} <span class="lx-muted">· ${state}</span></li>`;
    })
    .join("");
  const label = { guided: "Empezar el ejercicio guiado", autonomous: "Hacer los ejercicios autónomos", selfcheck: "Hacer la autoevaluación" }[group];
  return `<ul class="lx-unit-exlist">${items}</ul>
    <div class="lx-actions"><button class="btn btn--primary" type="button" data-learn="unit-practice" data-group="${group}" data-concept="${concept.id}">${label}</button></div>`;
}

function lessonHtml(concept, section, position, done) {
  const examples = section.examples
    .map((example, i) => {
      const lines = example.lines.map(([n, text]) => `<li><span class="lx-line-ref">Línea ${n}</span> ${renderInline(text)}</li>`).join("");
      const out = `lx-run-${position}-${i}`;
      return `
        <div class="lx-unit-example">
          ${codeBlock(example.code, { numbered: true, label: `Ejemplo ${i + 1} de la lección ${position + 1}` })}
          <ol class="lx-lines">${lines}</ol>
          <div class="lx-actions">
            <button class="btn btn--ghost" type="button" data-learn="run-example" data-concept="${concept.id}" data-section="${escapeHtml(section.id)}" data-example="${i}" aria-controls="${out}">▶ Ejecutar el ejemplo</button>
          </div>
          <p class="lx-note">Salida${example.output ? "" : " (no muestra nada)"}:</p>
          <pre class="lx-output" id="${out}" tabindex="0" aria-live="polite">${escapeHtml(example.output ?? "")}</pre>
        </div>`;
    })
    .join("");
  return `
    <article class="lx-unit-lesson" aria-labelledby="lx-lesson-${position}">
      <h3 class="lx-h4" id="lx-lesson-${position}">Lección ${position + 1}. ${renderInline(section.title)} ${done ? '<span class="lx-status" data-status="dominado">Completada</span>' : ""}</h3>
      <div class="prose">${renderMarkdown(section.theory)}</div>
      ${examples}
      <div class="lx-actions">
        <button class="btn btn--primary" type="button" data-learn="unit-quiz" data-concept="${concept.id}" data-section="${escapeHtml(section.id)}">Mini-quiz de la lección (3)</button>
        ${done ? "" : `<button class="btn btn--ghost" type="button" data-learn="section-done" data-concept="${concept.id}" data-section="${escapeHtml(section.id)}">Marcar la lección como completada</button>`}
      </div>
    </article>`;
}

function passHtml(index, learning, concept, s) {
  const required = concept.pass.required.map((id) => {
    const ok = solved(learning, id);
    return `<li data-done="${ok}">${ok ? "✓" : "○"} ${renderInline(exerciseTitle(index.exercises.get(id)))}</li>`;
  });
  const mastered = s.status === "dominado";
  return `
    <ul class="lx-list">${concept.pass.text.map((t) => `<li>${renderInline(t)}</li>`).join("")}</ul>
    <h3 class="lx-h4">Tu situación</h3>
    <ul class="lx-unit-pass">
      ${required.join("")}
      <li data-done="${mastered}">${mastered ? "✓" : "○"} Dominio de la unidad: ${s.attempted && s.enough ? percent(s.score) : "pocas evidencias todavía"} (se pide ${percent(concept.pass.minScore)} o más y que el motor la marque como dominada)</li>
    </ul>`;
}

function curriculumHtml(concept) {
  const rows = concept.curriculum
    .map(
      (m) => `<li><a href="#/daw/curriculo/${escapeHtml(m.ce.split("-")[0])}">${escapeHtml(m.ce)}</a> · <span class="lx-status" data-status="${m.status === "verified" ? "dominado" : "insuficiente"}">${STATUS_TEXT[m.status]}</span>
        <span class="lx-muted">${renderInline(m.note ?? "")} Revisada el ${escapeHtml(m.reviewed)}.</span></li>`,
    )
    .join("");
  return `<p class="lx-muted">Módulo 0485 Programación. Los criterios de evaluación son los del texto oficial (RD 405/2023); la relación con esta unidad es una propuesta de la plataforma para orientar el estudio y no es una programación didáctica oficial mientras no esté validada.</p>
    <ul class="lx-list">${rows}</ul>`;
}

/** Secciones y su orden en la página de una unidad (también es el índice «En esta página»). */
export function unitToc(concept) {
  return [
    ["lx-goals", "Objetivos"],
    ["lx-prior", "Conocimientos previos"],
    ["lx-expl", "Lecciones"],
    ["lx-key", "Conceptos importantes"],
    ["lx-example", "Ejemplo comentado"],
    ["lx-guided", "Ejercicios guiados"],
    ["lx-autonomous", "Ejercicios autónomos"],
    ["lx-errors", "Errores frecuentes"],
    ["lx-selfcheck", "Autoevaluación"],
    ["lx-summary", "Resumen"],
    ["lx-pass", "Criterios de superación"],
    ...(concept.curriculum?.length ? [["lx-curriculum", "Currículo DAW"]] : []),
  ];
}

/**
 * Cuerpo de la página de una unidad (sin la cabecera ni el paginador, que pone learn-app.js).
 * `lessons`: enlaces a las lecciones PCAP relacionadas, ya en HTML.
 */
export function unitBody(index, learning, concept, s, { lessons = "" } = {}) {
  const done = new Set(sectionsDone(learning, concept).map((d) => d.id));
  const example = concept.example;
  const lines = example.lines.map(([n, text]) => `<li><span class="lx-line-ref">Línea ${n}</span> ${renderInline(text)}</li>`).join("");
  const errors = concept.errors
    .map((error) => `<details class="lx-details"><summary>${renderInline(error.label)}</summary>${errorExplanation(error, { heading: "p" })}</details>`)
    .join("");
  const key = concept.key.map(([term, text]) => `<div><dt>${renderInline(term)}</dt><dd>${renderInline(text)}</dd></div>`).join("");
  const section = (id, title, html) => `<section class="lx-section" aria-labelledby="${id}"><h2 class="lx-section__title" id="${id}">${title}</h2>${html}</section>`;
  return [
    section("lx-goals", "Objetivos de aprendizaje", `<p>Al terminar la unidad sabrás:</p><ul class="lx-list">${concept.objectives.map((o) => `<li>${renderInline(o)}</li>`).join("")}</ul><p class="lx-muted">Cuándo se usa: ${renderInline(concept.when)}</p>`),
    section("lx-prior", "Conocimientos previos", `<p>${renderInline(concept.prior)}</p>`),
    section(
      "lx-expl",
      "Lecciones",
      `<p class="lx-muted">${done.size} de ${concept.sections.length} lecciones completadas. Completar una lección te ayuda a organizarte; lo que demuestra que la dominas son los ejercicios.</p>
       ${meter(done.size / concept.sections.length, "Lecciones completadas")}
       ${concept.sections.map((sec, i) => lessonHtml(concept, sec, i, done.has(sec.id))).join("")}
       ${lessons ? `<h3 class="lx-h4">Para practicar con la consola</h3><ul>${lessons}</ul>` : ""}`,
    ),
    section("lx-key", "Conceptos importantes", `<dl class="lx-key">${key}</dl>`),
    section(
      "lx-example",
      "Ejemplo comentado",
      `${codeBlock(example.code, { numbered: true, label: "Código de ejemplo" })}<ol class="lx-lines">${lines}</ol>
       ${example.output ? `<p class="lx-note">Salida:</p><pre class="lx-output" tabindex="0">${escapeHtml(example.output)}</pre>` : ""}`,
    ),
    section("lx-guided", "Ejercicios guiados", `<p class="lx-muted">Paso a paso, con pista y solución explicada al terminar.</p>${exerciseList(index, learning, concept.guided, "guided", concept)}`),
    section("lx-autonomous", "Ejercicios autónomos", `<p class="lx-muted">Sin pasos: aplica lo aprendido. Se corrigen con tests en tu navegador.</p>${exerciseList(index, learning, concept.autonomous, "autonomous", concept)}`),
    section("lx-errors", "Errores frecuentes", errors),
    section("lx-selfcheck", "Autoevaluación", `<p class="lx-muted">Preguntas para comprobar si has entendido la unidad.</p>${exerciseList(index, learning, concept.selfcheck, "selfcheck", concept)}`),
    section("lx-summary", "Resumen", `<ul class="lx-list">${concept.recap.map((t) => `<li>${renderInline(t)}</li>`).join("")}</ul>`),
    section("lx-pass", "Criterios de superación", passHtml(index, learning, concept, s)),
    concept.curriculum?.length ? section("lx-curriculum", "Relación con el currículo de DAW", curriculumHtml(concept)) : "",
  ].join("");
}

/** Miga de pan y posición de la unidad dentro del módulo. */
export function unitCrumb(index, concept) {
  const total = pooModule(index)?.units.length ?? 0;
  return `<p class="daw-crumb"><a href="#/teoria">Teoría</a> › <a href="#/poo">Módulo de POO</a> › Unidad ${concept.unit.number} de ${total}</p>`;
}

/** Ejercicios de un grupo de la unidad (mini-quiz de una lección, guiados, autónomos o autoevaluación). */
export function unitExercises(concept, { group = null, section = null } = {}) {
  if (section) return concept.sections.find((s) => s.id === section)?.quiz ?? [];
  return concept[group] ?? [];
}

/* ---------- Índice del módulo (#/poo) ---------- */

export function renderModule(index, learning, now = new Date()) {
  const module = pooModule(index);
  if (!module) return `<p class="empty-state" id="learn-title" tabindex="-1">El módulo de POO no está disponible.</p>`;
  const stats = allStats(index, learning, now);
  const units = availableUnits(index);
  const ids = new Set(units.map((u) => u.id));
  const lessonsTotal = units.reduce((n, u) => n + (index.concepts.get(u.id).sections?.length ?? 0), 0);
  const lessonsDone = units.reduce((n, u) => n + sectionsDone(learning, index.concepts.get(u.id)).length, 0);
  const exercises = [...index.exercises.values()].filter((e) => ids.has(e.concept));
  const tried = exercises.filter((e) => learning.ex[e.id]);
  const right = tried.filter((e) => learning.ex[e.id].h.at(-1) === true);
  const mastered = units.filter((u) => stats.get(u.id).status === "dominado");
  const due = units.filter((u) => stats.get(u.id).due);
  const errors = activeErrors(learning, now).filter((e) => ids.has(index.errors.get(e.id)?.concept));
  const last = learning.log.filter((l) => ids.has(index.exercises.get(l.ex)?.concept)).at(-1);
  const rows = module.units
    .map((u) => {
      if (!u.available || !index.concepts.has(u.id)) {
        return `<li class="lx-concept" data-available="false"><span class="lx-concept__link">Unidad ${u.number}. ${escapeHtml(u.title)}</span>
          <span class="lx-concept__summary lx-muted">En preparación</span></li>`;
      }
      const concept = index.concepts.get(u.id);
      const doneCount = sectionsDone(learning, concept).length;
      return `<li class="lx-concept"><a class="lx-concept__link" href="#/teoria/${u.id}">Unidad ${u.number}. ${escapeHtml(concept.title)}</a>
        <span class="lx-concept__summary">${renderInline(concept.summary)} <span class="lx-muted">· ${doneCount} de ${concept.sections.length} lecciones</span></span>
        <span class="lx-concept__status">${statusBadge(stats.get(u.id))}</span></li>`;
    })
    .join("");
  const errorItems = errors
    .map((e) => `<li>${renderInline(index.errors.get(e.id).label)} <button class="btn btn--ghost" type="button" data-learn="error" data-id="${escapeHtml(e.id)}">Practicar este error</button></li>`)
    .join("");
  return `
    <div class="lx-doc"><div class="lx-doc__main">
    <p class="daw-crumb"><a href="#/teoria">Teoría</a> › Módulo de POO</p>
    <header class="lx-head">
      <p class="eyebrow">Módulo · 0485 Programación</p>
      <h1 class="lx-title" id="learn-title" tabindex="-1">${escapeHtml(module.title)}</h1>
      <p class="lx-lead">${renderInline(module.summary)}</p>
      <p class="lx-muted">${units.length} de ${module.units.length} unidades publicadas. Las demás llegarán por fases.</p>
    </header>
    <section class="lx-section" aria-labelledby="lx-poo-units">
      <h2 class="lx-section__title" id="lx-poo-units">Unidades</h2>
      <ol class="lx-concepts">${rows}</ol>
    </section>
    <section class="lx-section" aria-labelledby="lx-poo-progress">
      <h2 class="lx-section__title" id="lx-poo-progress">Tu progreso en el módulo</h2>
      <dl class="lx-key">
        <div><dt>Lecciones completadas</dt><dd>${lessonsDone} de ${lessonsTotal} ${meter(lessonsTotal ? lessonsDone / lessonsTotal : 0, "Lecciones completadas del módulo")}</dd></div>
        <div><dt>Ejercicios practicados</dt><dd>${tried.length} de ${exercises.length}; ${right.length} bien en el último intento</dd></div>
        <div><dt>Unidades dominadas</dt><dd>${mastered.length ? mastered.map((u) => escapeHtml(index.concepts.get(u.id).title)).join(", ") : "Ninguna todavía"}</dd></div>
        <div><dt>Repaso pendiente</dt><dd>${due.length ? due.map((u) => `<a href="#/teoria/${u.id}">${escapeHtml(index.concepts.get(u.id).title)}</a>`).join(", ") : "Nada por hoy"}</dd></div>
        <div><dt>Última actividad</dt><dd>${last ? new Date(last.at).toLocaleDateString("es-ES", { day: "numeric", month: "long" }) : "Aún no has practicado el módulo"}</dd></div>
      </dl>
      <p class="lx-muted">Completar lecciones no equivale a dominar una unidad: el dominio lo calcula el motor con tus respuestas recientes.</p>
      ${errorItems ? `<h3 class="lx-h4">Errores que conviene corregir</h3><ul class="lx-list">${errorItems}</ul>` : ""}
    </section>
    </div></div>`;
}
