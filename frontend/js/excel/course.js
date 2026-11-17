/* Excel profesional en la web: panel del curso, unidades y práctica (P2 y P4.1: M01-M05).

   Rutas (app.js carga este módulo solo en ellas, así la portada y DAW no descargan el motor):
     #/academia/excel                      panel: avisos, progreso e itinerario de 25 módulos
     #/academia/excel/<unidad>             unidad: objetivos, teoría, ejemplos, guiado, caso…
     #/academia/excel/<unidad>/practica    ejercicios de la unidad: test, resultado y fórmula
     #/academia/excel/repaso               repaso espaciado de lo que toca hoy
   #/excel-academy[/…] es un alias: app.js lo reescribe a #/academia/excel[/…].

   El progreso es el documento del curso «excel» (course-store.js): las respuestas, el repaso, las
   unidades completadas y la última abierta se sincronizan con la cuenta como en DAW. Todo texto del
   JSON se escapa o se pinta con el Markdown seguro de markdown.js. */

import { ACADEMY_COURSES } from "../catalog.js";
import { courseState, dueQuestionIds, recordCourseAnswer, saveCourse } from "../course-store.js";
import { completeLesson, visitLesson } from "../lesson-progress.js";
import { escapeHtml, renderInline, renderMarkdown, safeUrl } from "../markdown.js";
import { notFoundHtml } from "../not-found.js";
import { courseSummary, TEST_KINDS, unitQuestions, unitStatus } from "./progress.js";
import { formatCell, gridHtml, mountFormulaExercise, mountResultExercise } from "./views.js";

const ID = "excel";
const BASE = "#/academia/excel";
const DATA = "data/academia/excel";
const $ = (selector) => document.querySelector(selector);
const root = () => $("#excel-view");
const t = (value) => (typeof value === "string" ? value : value?.es ?? "");
const info = ACADEMY_COURSES.find((course) => course.id === ID);
const hours = (h) => `${String(h).replace(".", ",")} h`;
/** «M01 a M05» o «M01 y M02»: los módulos que ya tienen contenido. */
const modulesLabel = (modules) => {
  const codes = modules.map((m) => m.title.slice(0, 3));
  return codes.length > 2 ? `${codes[0]} a ${codes.at(-1)}` : codes.join(" y ");
};
const percent = (value) => `${Math.round(value * 100)} %`;

/** Itinerario completo (doc original 07 §2). Tienen contenido los módulos que trae lessons.json. */
export const ITINERARY = [
  ["M01", "Fundamentos de Excel", 10],
  ["M02", "Fórmulas y funciones básicas", 8],
  ["M03", "Formato profesional y gestión de libros", 4],
  ["M04", "Funciones lógicas", 4],
  ["M05", "Agregación condicional", 4],
  ["M06", "Texto y limpieza de datos", 4],
  ["M07", "Fechas y horas", 4],
  ["M08", "Búsquedas clásicas", 4],
  ["M09", "Búsquedas modernas y matrices dinámicas", 5],
  ["M10", "Validación de datos", 4],
  ["M11", "Tablas estructuradas", 4],
  ["M12", "Ordenar, filtrar y segmentar", 3],
  ["M13", "Formato condicional", 3],
  ["M14", "Nombres y protección", 3],
  ["M15", "Excel administrativo", 6],
  ["M16", "Excel financiero y contable", 6],
  ["M17", "Tablas dinámicas", 5],
  ["M18", "Gráficos", 4],
  ["M19", "Paneles de control y reporting", 5],
  ["M20", "Power Query", 6],
  ["M21", "Automatización sin código: grabadora de macros", 2],
  ["M22", "VBA básico", 5],
  ["M23", "Repaso y preparación complementaria", 3],
  ["M24", "Proyectos 1 y 2: facturación y personal", 7],
  ["M25", "Proyectos 3 y 4: compras y control empresarial", 7],
].map(([code, title, h]) => ({ code, title, hours: h }));

const NOTICES = `
  <ul class="xl-notices" aria-label="Avisos">
    <li><strong>Sin afiliación.</strong> Python Learning Dashboard no está afiliado a Microsoft. Excel y Microsoft 365 son marcas de Microsoft.</li>
    <li><strong>Corrección formativa.</strong> La corrección se hace en tu navegador y sirve para aprender; no es una evaluación oficial.</li>
    <li><strong>Contenido fiscal educativo.</strong> Los ejemplos de IVA usan datos ficticios y no sustituyen el asesoramiento de un profesional.</li>
  </ul>`;

/* ---------- Datos ---------- */

let loading = null;

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function loadCourse() {
  loading ??= Promise.all([fetchJson(`${DATA}/bank.json`), fetchJson(`${DATA}/lessons.json`)]).then(([bank, { modules }]) => {
    const lessons = new Map();
    const order = [];
    for (const module of modules) {
      for (const lesson of module.lessons) {
        lessons.set(lesson.slug, { lesson, module, index: order.length });
        order.push(lesson.slug);
      }
    }
    const byId = new Map(bank.questions.map((q) => [q.id, q]));
    return { bank, modules, lessons, order, byId, all: order.map((slug) => lessons.get(slug).lesson) };
  });
  loading.catch(() => {
    loading = null; // se reintenta en la siguiente visita
  });
  return loading;
}

/* ---------- Piezas ---------- */

function meter(value, label) {
  const pct = Math.round((value ?? 0) * 100);
  return `<span class="meter" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuemin="0" aria-valuemax="100"
    aria-valuenow="${pct}"><span class="meter__fill" data-meter="${pct}"></span></span>`;
}

function statusOf(course, slug) {
  const { lesson } = course.lessons.get(slug);
  return unitStatus(unitQuestions(course.bank, slug), courseState(ID).answers, lesson.excel?.pass);
}

/** Etiquetas de estado de una unidad: con texto, no solo con color. */
function badges(course, slug) {
  const status = statusOf(course, slug);
  const done = courseState(ID).done?.[slug];
  const items = [];
  if (status.passed) items.push('<span class="xl-badge xl-badge--ok">✓ Superada</span>');
  if (done) items.push('<span class="xl-badge">Completada</span>');
  return items.join(" ");
}

const crumb = (extra = "") =>
  `<p class="daw-crumb"><a href="${BASE}">Excel profesional</a>${extra ? ` › ${extra}` : ""}</p>`;

/* ---------- Panel ---------- */

function renderPanel(course) {
  const progress = courseState(ID);
  const summary = courseSummary(course.all, course.bank, progress);
  const due = dueQuestionIds(ID, course.bank.questions.map((q) => q.id)).length;
  const last = course.lessons.get(progress.lastLesson?.slug);
  const pending = course.order.find((slug) => !progress.done?.[slug]);
  const resume = last && !progress.done?.[last.lesson.slug] ? last : course.lessons.get(pending);
  const started = Boolean(last) || summary.done > 0;
  const modules = new Map(course.modules.map((m) => [m.title.slice(0, 3), m]));
  const itinerary = ITINERARY.map((item) => {
    const module = modules.get(item.code);
    if (!module) {
      return `<li class="xl-module xl-module--soon">
          <h3 class="xl-module__title">${item.code} · ${escapeHtml(item.title)}</h3>
          <p class="xl-module__meta">${hours(item.hours)} · <span class="xl-badge">Próximamente</span></p>
        </li>`;
    }
    const units = module.lessons
      .map(
        (lesson) => `<li class="xl-unit">
            <a href="${BASE}/${lesson.slug}">${escapeHtml(lesson.title)}</a>
            <span class="xl-unit__meta">${hours(lesson.excel.hours)} · nivel ${lesson.excel.level} ·
              ${unitQuestions(course.bank, lesson.slug).length} ejercicios</span>
            ${badges(course, lesson.slug)}
          </li>`,
      )
      .join("");
    return `<li class="xl-module">
        <h3 class="xl-module__title">${escapeHtml(module.title)}</h3>
        <p class="xl-module__meta">${hours(item.hours)} · ${module.lessons.length} unidades · ${escapeHtml(module.summary)}</p>
        <ul class="xl-units">${units}</ul>
      </li>`;
  }).join("");
  const totalHours = course.all.reduce((sum, lesson) => sum + lesson.excel.hours, 0);
  return `
    <header class="course-hero">
      <p class="eyebrow">Academia · ${escapeHtml(info.subtitle)}</p>
      <h1 class="course-hero__title" id="xl-title" tabindex="-1">${escapeHtml(info.title)}</h1>
      <p class="course-hero__lead">Excel desde cero con ejercicios que se corrigen calculando, como Excel en español.
        Ya están ${modulesLabel(course.modules)}: ${summary.units} unidades, ${summary.questions} ejercicios y unas ${hours(totalHours)} de dedicación estimada.
        El resto del itinerario de ${ITINERARY.length} módulos llegará por partes.</p>
      <p class="daw-units" id="xl-units">${summary.done} de ${summary.units} unidades completadas · ${summary.passed} superadas ·
        ${summary.solved} de ${summary.questions} ejercicios bien resueltos</p>
      ${meter(summary.units ? summary.passed / summary.units : 0, "Unidades superadas")}
      <div class="course-hero__cta">
        ${
          resume
            ? `<a class="btn btn--primary btn--lg" href="${BASE}/${resume.lesson.slug}">${started ? "Continuar" : "Empezar"}: ${escapeHtml(resume.lesson.title)} →</a>`
            : ""
        }
        ${due ? `<a class="btn btn--ghost btn--lg" href="${BASE}/repaso">Repaso de hoy (${due})</a>` : ""}
      </div>
    </header>
    <section class="course-section" aria-labelledby="xl-notices-title">
      <h2 class="section-title" id="xl-notices-title">Antes de empezar</h2>
      ${NOTICES}
      <p class="readiness__note">Se toma como referencia Excel de Microsoft 365 en español de España. Para practicar fuera de la web
        sirve Excel para la web, gratuito con una cuenta de Microsoft. Si inicias sesión, el progreso se guarda en tu cuenta.</p>
    </section>
    <section class="course-section" aria-labelledby="xl-path-title">
      <h2 class="section-title" id="xl-path-title">Itinerario</h2>
      <p class="readiness__note">Una unidad está <strong>superada</strong> con al menos el 80 % del test bien (último intento) y sus
        ejercicios de fórmula obligatorios resueltos. <strong>Completada</strong> es la marca que pones tú al terminarla.</p>
      <ol class="xl-path">${itinerary}</ol>
    </section>
    <section class="course-section" aria-labelledby="xl-origin-title">
      <h2 class="section-title" id="xl-origin-title">De dónde sale este contenido</h2>
      <p>${escapeHtml(info.structure)} Las explicaciones, los casos y los ejercicios están escritos para la plataforma, con empresas y
        personas ficticias. Cada resultado lo comprueba el motor de fórmulas de PLD al generar el curso. Las fuentes de cada unidad
        solo se enlazan.</p>
    </section>`;
}

/* ---------- Unidad ---------- */

function exampleHtml(item) {
  if (!item.formula) {
    return `<article class="xl-example"><h3 class="xl-example__title">${escapeHtml(item.title)}</h3><p>${renderInline(item.text)}</p></article>`;
  }
  const grid = Object.keys(item.grid).length ? gridHtml(item.grid, { sheet: item.sheet, caption: `Datos del ejemplo: ${item.title}`, extraCells: item.cell ? [item.cell] : [] }) : "";
  const shown = typeof item.answer === "number" ? formatCell(item.answer) : item.answer;
  return `<article class="xl-example">
      <h3 class="xl-example__title">${escapeHtml(item.title)}</h3>
      ${grid}
      <p class="xl-exercise__formula">${item.cell ? `${escapeHtml(item.cell)}: ` : ""}<code>${escapeHtml(item.formula)}</code> → <strong>${escapeHtml(shown)}</strong></p>
      <p>${renderInline(item.explain)}</p>
    </article>`;
}

function renderUnit(course, slug) {
  const { lesson, module, index } = course.lessons.get(slug);
  const excel = lesson.excel;
  const prev = course.lessons.get(course.order[index - 1]);
  const next = course.lessons.get(course.order[index + 1]);
  const done = courseState(ID).done?.[slug];
  const status = statusOf(course, slug);
  const questions = unitQuestions(course.bank, slug);
  const requires = excel.requires
    .map((other) => course.lessons.get(other))
    .filter(Boolean)
    .map((other) => `<a href="${BASE}/${other.lesson.slug}">${escapeHtml(other.lesson.title)}</a>`);
  const list = (items, render) => items.map((item) => `<li>${render(item)}</li>`).join("");
  const guided = course.byId.get(excel.guided.question);
  const required = excel.pass.required.map((id) => escapeHtml(id));
  return `
    ${crumb(escapeHtml(module.title))}
    <header class="course-hero">
      <p class="eyebrow">Unidad ${index + 1} de ${course.order.length} · ${hours(excel.hours)} · nivel ${excel.level}</p>
      <h1 class="course-hero__title" id="xl-title" tabindex="-1">${escapeHtml(lesson.title)}</h1>
      <p>${badges(course, slug)}</p>
      ${requires.length ? `<p class="readiness__note">Antes conviene hacer: ${requires.join(", ")}.</p>` : ""}
      <div class="course-hero__cta"><a class="btn btn--primary" href="${BASE}/${slug}/practica">Practicar la unidad (${questions.length} ejercicios)</a></div>
    </header>
    ${excel.warning ? `<p class="xl-warning" role="note"><strong>Seguridad:</strong> ${escapeHtml(excel.warning)}</p>` : ""}
    <section class="course-section" aria-labelledby="xl-goals-title">
      <h2 class="section-title" id="xl-goals-title">Al terminar sabrás</h2>
      <ul class="daw-goals">${list(lesson.objectives, renderInline)}</ul>
    </section>
    <section class="course-section daw-theory" aria-label="Explicación">${renderMarkdown(lesson.theory)}</section>
    <section class="course-section" aria-labelledby="xl-examples-title">
      <h2 class="section-title" id="xl-examples-title">Ejemplos resueltos</h2>
      ${excel.examples.map(exampleHtml).join("")}
    </section>
    <section class="course-section" aria-labelledby="xl-guided-title">
      <h2 class="section-title" id="xl-guided-title">Ejercicio guiado</h2>
      <ol class="xl-steps">${list(excel.guided.steps, renderInline)}</ol>
      ${guided ? `<div class="xl-item" data-xl-question="${escapeHtml(guided.id)}"></div>` : ""}
    </section>
    <section class="course-section" aria-labelledby="xl-case-title">
      <h2 class="section-title" id="xl-case-title">${escapeHtml(excel.case.title)}</h2>
      ${renderMarkdown(excel.case.text)}
    </section>
    <section class="course-section" aria-labelledby="xl-mistakes-title">
      <h2 class="section-title" id="xl-mistakes-title">Errores frecuentes</h2>
      <ul class="daw-mistakes">${list(lesson.mistakes, (m) => `<strong>${renderInline(m.error)}</strong> ${renderInline(m.fix)}`)}</ul>
    </section>
    <section class="course-section" aria-labelledby="xl-summary-title">
      <h2 class="section-title" id="xl-summary-title">Resumen</h2>
      <ul>${list(lesson.summary, renderInline)}</ul>
    </section>
    <section class="course-section" aria-labelledby="xl-pass-title">
      <h2 class="section-title" id="xl-pass-title">Para superar la unidad</h2>
      <ul>
        <li>Test y resultados: al menos el ${percent(excel.pass.test)} bien con el último intento. Ahora: ${status.test.correct} de ${status.test.total}.</li>
        ${required.length ? `<li>Ejercicios de fórmula obligatorios resueltos: ${status.required.done} de ${status.required.total} (${required.join(", ")}).</li>` : ""}
      </ul>
      <p class="readiness__note" role="status">${status.passed ? "✓ Unidad superada." : "Todavía no está superada."}</p>
      <a class="btn btn--primary" href="${BASE}/${slug}/practica">Ir a los ejercicios</a>
    </section>
    ${
      lesson.assistant?.faq?.length
        ? `<section class="course-section" aria-labelledby="xl-faq-title"><h2 class="section-title" id="xl-faq-title">Dudas frecuentes</h2>
            ${lesson.assistant.faq.map((f) => `<details class="daw-faq"><summary>${renderInline(f.q)}</summary><p>${renderInline(f.a)}</p></details>`).join("")}</section>`
        : ""
    }
    <section class="course-section" aria-labelledby="xl-sources-title">
      <h2 class="section-title" id="xl-sources-title">Fuentes</h2>
      <ul>${list(lesson.sources, (s) => `<a href="${safeUrl(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.title)}</a>`)}</ul>
    </section>
    <section class="course-section daw-complete" aria-labelledby="xl-complete-title">
      <h2 class="section-title" id="xl-complete-title">¿Has terminado la unidad?</h2>
      ${
        done
          ? `<p class="daw-done" role="status" tabindex="-1">✓ Completada. Cuenta en tu progreso del curso.</p>`
          : `<button class="btn btn--primary" type="button" data-xl-complete="${escapeHtml(slug)}">Marcar la unidad como completada</button>
             <p class="readiness__note">Se guarda en este navegador y, con sesión, en tu cuenta.</p>`
      }
    </section>
    <nav class="daw-pager" aria-label="Unidades">
      ${prev ? `<a class="btn btn--ghost" href="${BASE}/${prev.lesson.slug}">← ${escapeHtml(prev.lesson.title)}</a>` : "<span></span>"}
      ${next ? `<a class="btn btn--ghost" href="${BASE}/${next.lesson.slug}">${escapeHtml(next.lesson.title)} →</a>` : "<span></span>"}
    </nav>`;
}

/* ---------- Práctica ---------- */

const KIND_LABEL = { choice: "Test", "formula-result": "¿Qué devuelve?", formula: "Escribe la fórmula" };

const lastText = (ok) => (ok ? "Último intento: bien" : "Último intento: todavía no");

function lastLabel(id) {
  const history = courseState(ID).answers[id];
  return history?.length ? lastText(history.at(-1)) : "";
}

function itemHtml(q, number) {
  const kind = q.kind ?? "choice";
  const label = lastLabel(q.id);
  return `<article class="xl-item" aria-labelledby="xl-q-${escapeHtml(q.id)}">
      <h3 class="xl-item__title" id="xl-q-${escapeHtml(q.id)}"><span class="quiz__num">${number}</span> ${KIND_LABEL[kind]}
        <span class="xl-item__id">${escapeHtml(q.id)}</span> <span class="xl-badge" data-xl-last${label ? "" : " hidden"}>${label}</span></h3>
      <div data-xl-question="${escapeHtml(q.id)}"></div>
    </article>`;
}

function statusLine(course, slug) {
  const status = statusOf(course, slug);
  const parts = [`Test y resultados: ${status.test.correct} de ${status.test.total} bien`];
  if (status.required.total) parts.push(`obligatorios: ${status.required.done} de ${status.required.total}`);
  parts.push(`fórmulas resueltas: ${status.formulas.done} de ${status.formulas.total}`);
  return `${parts.join(" · ")}. ${status.passed ? "✓ Unidad superada." : "Unidad sin superar todavía."}`;
}

function renderPractice(course, slug) {
  const { lesson, module } = course.lessons.get(slug);
  const questions = unitQuestions(course.bank, slug);
  const tests = questions.filter((q) => TEST_KINDS.has(q.kind ?? "choice"));
  const formulas = questions.filter((q) => q.kind === "formula");
  return `
    ${crumb(`${escapeHtml(module.title)} › <a href="${BASE}/${slug}">${escapeHtml(lesson.title)}</a>`)}
    <header class="course-hero">
      <p class="eyebrow">Práctica</p>
      <h1 class="course-hero__title" id="xl-title" tabindex="-1">${escapeHtml(lesson.title)}</h1>
      <p class="xl-status" id="xl-status" role="status" aria-live="polite">${statusLine(course, slug)}</p>
      <p class="readiness__note">La corrección se hace en tu navegador y sirve para aprender; no es una evaluación oficial.</p>
    </header>
    <section class="course-section" aria-labelledby="xl-test-title">
      <h2 class="section-title" id="xl-test-title">Test y resultados (${tests.length})</h2>
      ${tests.map((q, i) => itemHtml(q, i + 1)).join("")}
    </section>
    ${
      formulas.length
        ? `<section class="course-section" aria-labelledby="xl-formulas-title">
            <h2 class="section-title" id="xl-formulas-title">Escribe la fórmula (${formulas.length})</h2>
            ${formulas.map((q, i) => itemHtml(q, tests.length + i + 1)).join("")}
          </section>`
        : ""
    }
    <nav class="daw-pager" aria-label="Unidad">
      <a class="btn btn--ghost" href="${BASE}/${slug}">← Volver a la unidad</a>
      <a class="btn btn--ghost" href="${BASE}">Ver el itinerario</a>
    </nav>`;
}

function renderReview(course) {
  const due = new Set(dueQuestionIds(ID, course.bank.questions.map((q) => q.id)));
  const items = course.bank.questions.filter((q) => due.has(q.id)).slice(0, 15);
  return `
    ${crumb("Repaso de hoy")}
    <header class="course-hero">
      <p class="eyebrow">Repaso espaciado</p>
      <h1 class="course-hero__title" id="xl-title" tabindex="-1">Repaso de hoy</h1>
      <p class="course-hero__lead">${
        items.length
          ? `${items.length} ejercicios que toca repasar. Lo fallado vuelve al día siguiente y lo acertado, cada vez más espaciado.`
          : "Nada que repasar hoy. Lo fallado vuelve al día siguiente y lo acertado, cada vez más espaciado."
      }</p>
    </header>
    <section class="course-section" aria-label="Ejercicios del repaso">${items.map((q, i) => itemHtml(q, i + 1)).join("")}</section>
    <nav class="daw-pager" aria-label="Curso"><a class="btn btn--ghost" href="${BASE}">← Volver al curso</a></nav>`;
}

/** Monta en la página los ejercicios interactivos (cada uno en su contenedor). */
function mountQuestions(course, slug) {
  for (const container of root().querySelectorAll("[data-xl-question]")) {
    const q = course.byId.get(container.dataset.xlQuestion);
    if (!q) continue;
    const onResult = (ok) => {
      recordCourseAnswer(ID, q.id, ok);
      saveCourse(ID);
      const badge = container.closest(".xl-item")?.querySelector("[data-xl-last]");
      if (badge) {
        badge.textContent = lastText(ok);
        badge.hidden = false;
      }
      const status = $("#xl-status");
      if (status && slug) status.textContent = statusLine(course, slug);
    };
    if (q.kind === "formula") mountFormula(container, q, onResult);
    else if (q.kind === "formula-result") mountResult(container, q, onResult);
    else mountChoice(container, q, onResult);
  }
}

function withExplanation(container, explain, show) {
  let box = container.querySelector(".xl-explain");
  if (!box) {
    box = document.createElement("div");
    box.className = "quiz__feedback xl-explain";
    container.append(box);
  }
  box.hidden = !show;
  box.innerHTML = `<p>${renderInline(t(explain))}</p>`;
}

/** El enunciado se pinta aquí con el Markdown seguro (las vistas solo admiten texto plano). */
function statement(container, q) {
  const p = document.createElement("p");
  p.className = "xl-exercise__question";
  p.innerHTML = renderInline(t(q.q));
  container.prepend(p);
}

function mountFormula(container, q, onResult) {
  const question = { ...q.excel, id: q.id, q: "" };
  mountFormulaExercise(container, question, {
    onResult: (ok) => {
      onResult(ok);
      withExplanation(container, q.explain, ok);
    },
  });
  statement(container, q);
}

function mountResult(container, q, onResult) {
  const question = { ...q.excel, id: q.id, q: "" };
  mountResultExercise(container, question, {
    onResult: (ok) => {
      onResult(ok);
      withExplanation(container, q.explain, true);
    },
  });
  statement(container, q);
}

function mountChoice(container, q, onResult) {
  const name = `xl-choice-${q.id}`;
  const options = q.options
    .map((option, i) => `<label class="quiz__option" data-index="${i}"><input type="radio" name="${escapeHtml(name)}" value="${i}"> <span>${renderInline(t(option))}</span></label>`)
    .join("");
  container.innerHTML = `<form class="xl-exercise" novalidate>
      <fieldset class="quiz__q">
        <legend>${renderInline(t(q.q))}</legend>
        <div class="quiz__options">${options}</div>
      </fieldset>
      <div class="xl-exercise__actions"><button type="submit" class="btn btn--primary">Comprobar</button></div>
      <p class="xl-exercise__status" role="status" aria-live="polite" data-xl-status></p>
    </form>`;
  const form = container.querySelector("form");
  const status = container.querySelector("[data-xl-status]");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const chosen = form.querySelector("input:checked");
    status.textContent = "";
    if (!chosen) {
      status.dataset.state = "fail";
      status.textContent = "Elige una respuesta.";
      return;
    }
    const ok = q.answer.includes(Number(chosen.value));
    for (const option of form.querySelectorAll(".quiz__option")) delete option.dataset.correct;
    form.querySelector(`[data-index="${q.answer[0]}"]`).dataset.correct = "true";
    status.dataset.state = ok ? "ok" : "fail";
    const mark = document.createElement("strong");
    mark.textContent = ok ? "Correcto." : "Todavía no. La respuesta correcta está marcada.";
    status.append(mark);
    onResult(ok);
    withExplanation(container, q.explain, true);
  });
}

/* ---------- Rutas ---------- */

function parse(route) {
  const rest = route.slice(BASE.length).split("/").filter(Boolean).map(decodeURIComponent);
  return { slug: rest[0] ?? null, view: rest[1] ?? null, extra: rest.length > 2 };
}

let current = null;

async function render(route, { focus = false } = {}) {
  if (!current) root().innerHTML = `<p class="empty-state" id="xl-title" tabindex="-1">Cargando el curso…</p>`;
  try {
    current = await loadCourse();
  } catch {
    root().innerHTML = `<p class="empty-state" id="xl-title" tabindex="-1">No se pudo cargar el curso. Comprueba la conexión y recarga.</p>`;
    return;
  }
  if (location.hash !== route) return; // el alumno se fue mientras cargaba
  const { slug, view, extra } = parse(route);
  const known = slug && current.lessons.has(slug);
  let practice = null;
  if (!slug) {
    root().innerHTML = renderPanel(current);
  } else if (slug === "repaso" && !view) {
    root().innerHTML = renderReview(current);
    practice = "";
  } else if (known && !view && !extra) {
    if (visitLesson(courseState(ID), slug)) saveCourse(ID);
    root().innerHTML = renderUnit(current, slug);
    practice = slug;
  } else if (known && view === "practica" && !extra) {
    root().innerHTML = renderPractice(current, slug);
    practice = slug;
  } else {
    root().innerHTML = notFoundHtml({ titleId: "xl-title", route, what: known ? "esta página" : "esta unidad", back: { href: BASE, label: "Volver a Excel profesional" } });
  }
  if (practice !== null) mountQuestions(current, practice);
  document.title = `${slug && known ? `${current.lessons.get(slug).lesson.title} · ` : ""}Excel profesional · Python Learning Dashboard`;
  if (focus) $("#xl-title")?.focus();
}

function onClick(event) {
  const complete = event.target.closest("[data-xl-complete]");
  if (!complete) return;
  if (completeLesson(courseState(ID), complete.dataset.xlComplete)) saveCourse(ID);
  render(location.hash).then(() => $(".daw-complete .daw-done")?.focus());
}

let listening = false;

/** Muestra Excel profesional. */
export function openExcel(route, { moveFocus = true } = {}) {
  if (!listening) {
    root().addEventListener("click", onClick);
    listening = true;
  }
  return render(route, { focus: moveFocus });
}

/** Repinta el panel si está a la vista (al llegar el progreso de la cuenta). En las páginas con
    ejercicios no se repinta, para no borrar lo que el alumno esté escribiendo. */
export function refreshExcel() {
  if (location.hash === BASE) render(location.hash);
}
