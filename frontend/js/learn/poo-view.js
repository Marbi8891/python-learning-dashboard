/* Módulo de POO: índice del módulo (#/poo) y página de unidad (#/teoria/<unidad>).

   Una unidad es un concepto del núcleo con campos propios (objetivos, lecciones con ejemplos y
   mini-quiz, ejercicios guiados y autónomos, autoevaluación, resumen, criterios de superación y
   currículo). El dominio, los errores y el repaso son los del motor adaptativo (mastery.js):
   completar una lección solo organiza el estudio y no cuenta como competencia demostrada.

   Funciones puras que devuelven HTML: los clics los atiende learn-app.js (data-learn="…"). */

import { activeErrors, allStats, QUIZ_PASS, quizResult, sectionsDone } from "./mastery.js";
import { codeBlock, errorExplanation, escapeHtml, KIND_LABEL, meter, percent, renderInline, renderMarkdown, statusBadge } from "./ui.js";
import { safeUrl } from "../markdown.js";

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
  const label = {
    guided: "Empezar el ejercicio guiado",
    autonomous: "Hacer el ejercicio principal",
    extras: "Hacer las prácticas adicionales",
    selfcheck: "Hacer la autoevaluación",
  }[group];
  return `<ul class="lx-unit-exlist">${items}</ul>
    <div class="lx-actions"><button class="btn btn--primary" type="button" data-learn="unit-practice" data-group="${group}" data-concept="${concept.id}">${label}</button></div>`;
}

/** El cuestionario no lista sus 15 preguntas (se verían las respuestas al leerlas): solo el botón. */
/** Aciertos necesarios para aprobar un cuestionario de `total` preguntas (70 %: 11 de 15, 21 de 30). */
export const needed = (total) => Math.ceil(total * QUIZ_PASS - 1e-9);

/** Línea con la nota guardada de un cuestionario: mejor nota, último intento y si está superado. */
export function quizStatusHtml(result) {
  if (!result) return '<p class="lx-muted">Aún no lo has hecho.</p>';
  const passed = Boolean(result.passedAt);
  return `<p><span class="lx-status" data-status="${passed ? "dominado" : "insuficiente"}">${passed ? "Superado" : "Sin superar"}</span>
    Mejor nota: <strong>${result.best} de ${result.total}</strong> (${percent(result.best / result.total)}). Último intento: ${result.last} de ${result.total}.</p>`;
}

/** Preguntas del banco de la unidad cuya última respuesta fue incorrecta (para repasarlas). */
export const failedBank = (learning, concept) => (concept.bank ?? []).filter((id) => learning.ex[id]?.h.at(-1) === false);

function bankHtml(learning, concept) {
  const total = concept.bank.length;
  const failed = failedBank(learning, concept);
  return `<p class="lx-muted">${total} preguntas tipo test de toda la unidad, de nivel básico, intermedio y avanzado. Cada respuesta se corrige al momento y, si fallas, verás por qué tu opción no es correcta. La nota es la del primer intento: se supera con ${needed(total)} aciertos o más (${percent(QUIZ_PASS)}). Puedes repetirlo cuando quieras; se guarda tu mejor nota.</p>
    ${quizStatusHtml(quizResult(learning, concept.id))}
    <div class="lx-actions">
      <button class="btn btn--primary" type="button" data-learn="unit-practice" data-group="bank" data-concept="${concept.id}">Empezar el cuestionario (${total} preguntas)</button>
      ${failed.length ? `<button class="btn btn--ghost" type="button" data-learn="bank-review" data-concept="${concept.id}">Repasar las ${failed.length} preguntas falladas</button>` : ""}
    </div>
    ${failed.length ? '<p class="lx-muted">El repaso de las falladas no cambia tu nota: sirve para fijar lo que fallaste. El motor también te volverá a proponer la unidad en su fecha de repaso.</p>' : ""}`;
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
  const quiz = concept.bank?.length ? quizResult(learning, concept.id) : null;
  const quizPassed = Boolean(quiz?.passedAt);
  const quizText = concept.bank?.length ? `Sacar ${needed(concept.bank.length)} de ${concept.bank.length} o más (${percent(QUIZ_PASS)}) en el cuestionario de la unidad.` : "";
  const quizItem = concept.bank?.length
    ? `<li data-done="${quizPassed}">${quizPassed ? "✓" : "○"} Cuestionario de la unidad: ${quiz ? `mejor nota ${quiz.best} de ${quiz.total}` : "sin hacer"} (se piden ${needed(concept.bank.length)} aciertos)</li>`
    : "";
  return `
    <ul class="lx-list">${concept.pass.text.map((t) => `<li>${renderInline(t)}</li>`).join("")}${quizText ? `<li>${quizText}</li>` : ""}</ul>
    <h3 class="lx-h4">Tu situación</h3>
    <ul class="lx-unit-pass">
      ${required.join("")}
      ${quizItem}
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

/** Buenas prácticas de la unidad: qué hacer y por qué. */
function practicesHtml(concept) {
  return `<ul class="lx-list">${concept.practices.map((p) => `<li>${renderInline(p.text)} <span class="lx-muted">${renderInline(p.why)}</span></li>`).join("")}</ul>`;
}

/** Referencias bibliográficas: solo fuentes del catálogo cerrado del módulo; las no comprobadas lo dicen. */
function referencesHtml(index, concept) {
  const sources = pooModule(index)?.sources ?? {};
  const rows = concept.references
    .map((r) => {
      const source = sources[r.source];
      if (!source) return "";
      const status =
        r.status === "verified"
          ? `<span class="lx-status" data-status="dominado">Comprobada</span> <span class="lx-muted">por ${escapeHtml(r.by)} el ${escapeHtml(r.date)}</span>`
          : '<span class="lx-status" data-status="insuficiente">Pendiente de comprobación</span>';
      return `<li><a href="${safeUrl(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.title)}</a>, apartado «${renderInline(r.section)}». ${status}
        <span class="lx-muted">Respalda: ${r.supports.map((t) => renderInline(t)).join("; ")}.</span></li>`;
    })
    .join("");
  return `<p class="lx-muted">Fuentes oficiales de Python. «Pendiente de comprobación» significa que una persona todavía no ha revisado que el apartado citado diga eso.</p>
    <ul class="lx-list">${rows}</ul>`;
}

/** Tipos de relación del diagrama de clases y cómo se leen en voz alta. */
const RELATION_TEXT = { asociacion: "asociación", agregacion: "agregación", composicion: "composición", herencia: "herencia" };

/** Punto del borde de la caja `b` por el que sale la recta hacia (x, y). */
function edgePoint(b, x, y) {
  const dx = x - b.cx;
  const dy = y - b.cy;
  const t = Math.min(dx ? b.w / 2 / Math.abs(dx) : Infinity, dy ? b.h / 2 / Math.abs(dy) : Infinity);
  return [b.cx + dx * t, b.cy + dy * t];
}

/**
 * Diagrama de clases en SVG (dibujo) más la misma información en texto: el SVG es una imagen con
 * título y descripción, y la lista de relaciones es lo que lee un lector de pantalla o quien amplía.
 */
export function diagramHtml(diagram) {
  const W = 210;
  const PITCH_X = 240;
  const PITCH_Y = 140;
  const LINE = 18;
  const boxes = new Map(
    diagram.classes.map((c) => {
      const h = 34 + LINE * c.members.length;
      return [c.id, { ...c, w: W, h, x: c.col * PITCH_X + 10, y: c.row * PITCH_Y + 10, cx: c.col * PITCH_X + 10 + W / 2, cy: c.row * PITCH_Y + 10 + h / 2 }];
    }),
  );
  const width = Math.max(...[...boxes.values()].map((b) => b.x + b.w)) + 10;
  const height = Math.max(...[...boxes.values()].map((b) => b.y + b.h)) + 10;
  const lines = diagram.relations
    .map((r) => {
      const a = boxes.get(r.from);
      const b = boxes.get(r.to);
      const [x1, y1] = edgePoint(a, b.cx, b.cy);
      const [x2, y2] = edgePoint(b, a.cx, a.cy);
      const start = r.kind === "composicion" ? ' marker-start="url(#lx-uml-filled)"' : r.kind === "agregacion" ? ' marker-start="url(#lx-uml-hollow)"' : "";
      const end = r.kind === "herencia" ? ' marker-end="url(#lx-uml-arrow)"' : "";
      return `<line class="lx-uml__rel" data-kind="${escapeHtml(r.kind)}" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"${start}${end}/>`;
    })
    .join("");
  const rects = [...boxes.values()]
    .map(
      (b) => `<g class="lx-uml__class"><rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="6"/>
        <text class="lx-uml__name" x="${b.cx}" y="${b.y + 21}" text-anchor="middle">${escapeHtml(b.name)}</text>
        <line class="lx-uml__sep" x1="${b.x}" y1="${b.y + 30}" x2="${b.x + b.w}" y2="${b.y + 30}"/>
        ${b.members.map((m, i) => `<text class="lx-uml__member" x="${b.x + 10}" y="${b.y + 47 + i * LINE}">${escapeHtml(m)}</text>`).join("")}</g>`,
    )
    .join("");
  const names = new Map(diagram.classes.map((c) => [c.id, c.name]));
  const items = diagram.relations
    .map((r) => `<li><strong>${escapeHtml(names.get(r.from))} → ${escapeHtml(names.get(r.to))}</strong> (${RELATION_TEXT[r.kind] ?? escapeHtml(r.kind)}): ${renderInline(r.text)}</li>`)
    .join("");
  return `<figure class="lx-uml">
      <svg class="lx-uml__svg" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="lx-uml-title lx-uml-desc">
        <title id="lx-uml-title">${escapeHtml(diagram.title)}</title>
        <desc id="lx-uml-desc">${escapeHtml(diagram.summary)}</desc>
        <defs>
          <marker id="lx-uml-filled" viewBox="0 0 12 10" refX="0" refY="5" markerWidth="12" markerHeight="10" orient="auto"><path class="lx-uml__mark-filled" d="M0 5 L6 0 L12 5 L6 10 Z"/></marker>
          <marker id="lx-uml-hollow" viewBox="0 0 12 10" refX="0" refY="5" markerWidth="12" markerHeight="10" orient="auto"><path class="lx-uml__mark-hollow" d="M0 5 L6 0 L12 5 L6 10 Z"/></marker>
          <marker id="lx-uml-arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path class="lx-uml__mark-hollow" d="M0 0 L10 5 L0 10 Z"/></marker>
        </defs>
        ${rects}${lines}
      </svg>
      <figcaption class="lx-muted">${renderInline(diagram.summary)} Rombo relleno: composición; rombo hueco: agregación; línea sola: asociación.</figcaption>
    </figure>
    <h3 class="lx-h4">Relaciones del diagrama</h3>
    <ul class="lx-list">${items}</ul>`;
}

/** Rúbrica del proyecto: criterio, puntos y qué se mira. */
function rubricHtml(concept) {
  const cell = (label, html) => `<td role="cell" data-label="${label}">${html}</td>`;
  const rows = concept.rubric
    .map((r) => `<tr role="row"><th scope="row" role="rowheader">${renderInline(r.criterion)}</th>${cell("Puntos", r.points)}${cell("Qué se valora", renderInline(r.text))}</tr>`)
    .join("");
  const total = concept.rubric.reduce((sum, r) => sum + r.points, 0);
  return `<p class="lx-muted">Para que valores tu proyecto, o para que lo valore tu profesor, sobre ${total} puntos. La funcionalidad la comprueban los tests del ejercicio principal.</p>
    <div class="table-wrap" tabindex="0"><table class="lx-table lx-table--reflow" role="table" aria-labelledby="lx-rubric">
      <thead role="rowgroup"><tr role="row"><th scope="col" role="columnheader">Criterio</th><th scope="col" role="columnheader">Puntos</th><th scope="col" role="columnheader">Qué se valora</th></tr></thead>
      <tbody role="rowgroup">${rows}</tbody>
    </table></div>`;
}

/** Secciones y su orden en la página de una unidad (también es el índice «En esta página»). */
export function unitToc(concept) {
  return [
    ["lx-goals", "Objetivos"],
    ["lx-prior", "Conocimientos previos"],
    ["lx-expl", "Lecciones"],
    ["lx-key", "Conceptos importantes"],
    ["lx-example", "Ejemplo comentado"],
    ...(concept.diagram ? [["lx-diagram", "Diagrama de clases"]] : []),
    ["lx-guided", "Ejercicios guiados"],
    ["lx-autonomous", "Ejercicio principal"],
    ...(concept.rubric?.length ? [["lx-rubric", "Rúbrica"]] : []),
    ...(concept.extras?.length ? [["lx-extras", "Prácticas adicionales"]] : []),
    ...(concept.challenges?.length ? [["lx-challenges", "Retos de ampliación"]] : []),
    ["lx-errors", "Errores frecuentes"],
    ...(concept.practices?.length ? [["lx-practices", "Buenas prácticas"]] : []),
    ["lx-selfcheck", "Autoevaluación"],
    ...(concept.bank?.length ? [["lx-bank", "Cuestionario de la unidad"]] : []),
    ["lx-summary", "Resumen"],
    ["lx-pass", "Criterios de superación"],
    ...(concept.curriculum?.length ? [["lx-curriculum", "Currículo DAW"]] : []),
    ...(concept.references?.length ? [["lx-references", "Referencias"]] : []),
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
    concept.diagram ? section("lx-diagram", "Diagrama de clases", diagramHtml(concept.diagram)) : "",
    section("lx-guided", "Ejercicios guiados", `<p class="lx-muted">Paso a paso, con pista y solución explicada al terminar.</p>${exerciseList(index, learning, concept.guided, "guided", concept)}`),
    section("lx-autonomous", "Ejercicio principal", `<p class="lx-muted">Sin pasos: aplica lo aprendido. Se corrige con tests en tu navegador y es necesario para superar la unidad.</p>${exerciseList(index, learning, concept.autonomous, "autonomous", concept)}`),
    concept.rubric?.length ? section("lx-rubric", "Rúbrica de evaluación", rubricHtml(concept)) : "",
    concept.extras?.length ? section("lx-extras", "Prácticas adicionales", `<p class="lx-muted">Más ejercicios de código para seguir practicando. No son obligatorios.</p>${exerciseList(index, learning, concept.extras, "extras", concept)}`) : "",
    concept.challenges?.length
      ? section("lx-challenges", "Retos de ampliación", `<p class="lx-muted">Ideas para seguir con el proyecto por tu cuenta. No tienen tests ni cuentan para superar la unidad.</p><ol class="lx-list">${concept.challenges.map((t) => `<li>${renderInline(t)}</li>`).join("")}</ol>`)
      : "",
    section("lx-errors", "Errores frecuentes", errors),
    concept.practices?.length ? section("lx-practices", "Buenas prácticas", practicesHtml(concept)) : "",
    section("lx-selfcheck", "Autoevaluación", `<p class="lx-muted">Preguntas para comprobar si has entendido la unidad.</p>${exerciseList(index, learning, concept.selfcheck, "selfcheck", concept)}`),
    concept.bank?.length
      ? section("lx-bank", "Cuestionario de la unidad", bankHtml(learning, concept))
      : "",
    section("lx-summary", "Resumen", `<ul class="lx-list">${concept.recap.map((t) => `<li>${renderInline(t)}</li>`).join("")}</ul>`),
    section("lx-pass", "Criterios de superación", passHtml(index, learning, concept, s)),
    concept.curriculum?.length ? section("lx-curriculum", "Relación con el currículo de DAW", curriculumHtml(concept)) : "",
    concept.references?.length ? section("lx-references", "Referencias bibliográficas", referencesHtml(index, concept)) : "",
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

/** Id del resultado de la evaluación final en el progreso (quizzes). */
export const FINAL_ID = "poo-final";

/** Evaluación final: 3 preguntas por unidad publicada (una de cada nivel), sin corrección hasta el final. */
function finalHtml(index, learning, units) {
  const total = units.length * 3;
  if (!total) return "";
  const passedUnits = units.filter((u) => quizResult(learning, u.id)?.passedAt).length;
  return `
    <section class="lx-section" aria-labelledby="lx-poo-final">
      <h2 class="lx-section__title" id="lx-poo-final">Evaluación final del módulo</h2>
      <p>${total} preguntas del banco, 3 de cada unidad (una básica, una intermedia y una avanzada), elegidas al azar cada vez. Como en un examen, la corrección se ve al terminar. Se supera con ${needed(total)} aciertos o más (${percent(QUIZ_PASS)}).</p>
      <p class="lx-muted">Conviene hacerla cuando hayas superado los cuestionarios de las unidades (llevas ${passedUnits} de ${units.length}). Sin tiempo límite; las que dejes sin responder cuentan como falladas.</p>
      ${quizStatusHtml(quizResult(learning, FINAL_ID))}
      <div class="lx-actions"><button class="btn btn--primary" type="button" data-learn="poo-final">Empezar la evaluación final (${total} preguntas)</button></div>
    </section>`;
}

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
      <p class="lx-muted">${units.length === module.units.length ? `Las ${units.length} unidades están publicadas.` : `${units.length} de ${module.units.length} unidades publicadas. Las demás llegarán por fases.`}</p>
    </header>
    <section class="lx-section" aria-labelledby="lx-poo-units">
      <h2 class="lx-section__title" id="lx-poo-units">Unidades</h2>
      <ol class="lx-concepts">${rows}</ol>
    </section>
    ${finalHtml(index, learning, units)}
    <section class="lx-section" aria-labelledby="lx-poo-progress">
      <h2 class="lx-section__title" id="lx-poo-progress">Tu progreso en el módulo</h2>
      <dl class="lx-key">
        <div><dt>Lecciones completadas</dt><dd>${lessonsDone} de ${lessonsTotal} ${meter(lessonsTotal ? lessonsDone / lessonsTotal : 0, "Lecciones completadas del módulo")}</dd></div>
        <div><dt>Ejercicios practicados</dt><dd>${tried.length} de ${exercises.length}; ${right.length} bien en el último intento</dd></div>
        <div><dt>Cuestionarios superados</dt><dd>${units.filter((u) => quizResult(learning, u.id)?.passedAt).length} de ${units.length}</dd></div>
        <div><dt>Unidades dominadas</dt><dd>${mastered.length ? mastered.map((u) => escapeHtml(index.concepts.get(u.id).title)).join(", ") : "Ninguna todavía"}</dd></div>
        <div><dt>Repaso pendiente</dt><dd>${due.length ? due.map((u) => `<a href="#/teoria/${u.id}">${escapeHtml(index.concepts.get(u.id).title)}</a>`).join(", ") : "Nada por hoy"}</dd></div>
        <div><dt>Última actividad</dt><dd>${last ? new Date(last.at).toLocaleDateString("es-ES", { day: "numeric", month: "long" }) : "Aún no has practicado el módulo"}</dd></div>
      </dl>
      <p class="lx-muted">Completar lecciones no equivale a dominar una unidad: el dominio lo calcula el motor con tus respuestas recientes.</p>
      ${errorItems ? `<h3 class="lx-h4">Errores que conviene corregir</h3><ul class="lx-list">${errorItems}</ul>` : ""}
    </section>
    </div></div>`;
}
