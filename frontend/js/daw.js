/* Cursos de DAW en la web: Programación, Bases de datos, Entornos, JavaScript y Java.
   Lee los JSON de data/courses/<id>/.

   Rutas (#/daw es la Preparación DAW, en learn/daw-prep.js):
     #/daw/cursos                           catálogo
     #/daw/curriculo[/<módulo>]             currículo oficial (curriculum.js)
     #/daw/<curso>                          panel del curso: bloques, acierto y lecciones
     #/daw/<curso>/leccion/<lección>        teoría, ejemplo, ejercicio, mini-quiz, reto y dudas
     #/daw/<curso>/practica/<bloque|repaso> tanda de práctica (test, completar el hueco y ordenar líneas) */

import hljs from "../vendor/highlight/core.min.js";
import java from "../vendor/highlight/java.min.js";
import javascript from "../vendor/highlight/javascript.min.js";
import sql from "../vendor/highlight/sql.min.js";
import {
  courseBlockStats,
  courseReadiness,
  courseState,
  DAW_COURSES,
  dueQuestionIds,
  recordCourseAnswer,
  saveCourse,
} from "./course-store.js";
import { completedCount, completeLesson, visitLesson } from "./lesson-progress.js";
import { loadCurriculum, renderCurriculum } from "./curriculum.js";
import { escapeHtml, renderInline, renderMarkdown, safeUrl } from "./markdown.js";
import { notFoundHtml } from "./not-found.js";

for (const [name, language] of Object.entries({ java, javascript, sql })) {
  if (!hljs.getLanguage(name)) hljs.registerLanguage(name, language);
}

const PRACTICE_SIZE = 10;
const REVIEW_SIZE = 15;
const $ = (selector) => document.querySelector(selector);
const root = () => $("#daw-view");

const loaded = new Map(); // id -> Promise<datos del curso>
let session = null; // tanda de práctica en curso

const t = (value) => (typeof value === "string" ? value : value?.es ?? "");
const md = (text) => renderInline(t(text));
const percent = (value) => `${Math.round(value * 100)} %`;
const same = (a, b) => a.length === b.length && a.every((x) => b.includes(x));
const normalize = (code) => code.replace(/\s+/g, "").replace(/;$/, "");
const courseInfo = (id) => DAW_COURSES.find((c) => c.id === id);

function shuffle(list) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

/** Orden estable para cada pregunta de ordenar (y nunca ya resuelto), como en la app. */
function stableShuffle(id, count) {
  let seed = [...id].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
  const indices = [...Array(count).keys()];
  for (let i = count - 1; i > 0; i -= 1) {
    seed = (seed * 1103515245 + 12345) >>> 0;
    const j = seed % (i + 1);
    [indices[i], indices[j]] = [indices[j], indices[i]];
  }
  return indices.every((v, i) => v === i) ? indices.reverse() : indices;
}

function code(source, lang) {
  if (!source) return "";
  const html = hljs.getLanguage(lang) ? hljs.highlight(source, { language: lang }).value : escapeHtml(source);
  return `<pre class="quiz__code" tabindex="0" aria-label="Código"><code>${html}</code></pre>`;
}

function meter(value, label) {
  const pct = Math.round((value ?? 0) * 100);
  return `<span class="meter" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuemin="0" aria-valuemax="100"
    aria-valuenow="${pct}"><span class="meter__fill" style="--value: ${pct}%"></span></span>`;
}

/* ---------- Datos ---------- */

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// Recursos complementarios del ciclo: si no cargan, el curso funciona igual (sin la lista)
let resourcesLoading = null;
function loadResources() {
  resourcesLoading ??= fetchJson("data/resources.json")
    .then((data) => data.resources ?? [])
    .catch(() => {
      resourcesLoading = null; // se reintenta en la siguiente visita
      return [];
    });
  return resourcesLoading;
}

function loadCourse(id) {
  if (!loaded.has(id)) {
    const promise = Promise.all([
      fetchJson(`data/courses/${id}/bank.json`),
      fetchJson(`data/courses/${id}/lessons.json`),
      loadResources(),
    ]).then(
      ([bank, { modules }, resources]) => {
        const lessons = new Map();
        const order = [];
        for (const module of modules) {
          for (const lesson of module.lessons) {
            lessons.set(lesson.slug, { lesson, module, index: order.length });
            order.push(lesson.slug);
          }
        }
        const info = courseInfo(id);
        return { id, info, bank, modules, lessons, order, resources: resources.filter((r) => r.modules?.includes(info.module)) };
      },
    );
    promise.catch(() => loaded.delete(id)); // se reintenta en la siguiente visita
    loaded.set(id, promise);
  }
  return loaded.get(id);
}

/* ---------- Correcciones (mismas reglas que la app) ---------- */

const kind = (q) => q.kind ?? "choice";

function isComplete(q, answer) {
  if (kind(q) === "fill") return answer.text.trim() !== "";
  if (kind(q) === "order") return answer.order.length === q.lines.length;
  return q.answer.length > 1 ? answer.selected.length === q.answer.length : answer.selected.length > 0;
}

function isCorrect(q, answer) {
  if (kind(q) === "fill") return q.accept.some((ok) => normalize(ok) === normalize(answer.text));
  // Se comparan los textos: si dos líneas son iguales, da igual cuál vaya primero
  if (kind(q) === "order") return answer.order.length === q.lines.length && answer.order.every((i, k) => q.lines[i] === q.lines[k]);
  return same(answer.selected, q.answer);
}

const missing = (q) =>
  kind(q) === "fill"
    ? "Escribe lo que va en el hueco."
    : kind(q) === "order"
      ? "Coloca todas las líneas."
      : q.answer.length > 1
        ? `Elige ${q.answer.length} respuestas.`
        : "Elige una respuesta.";

/* ---------- Catálogo ---------- */

/** Lenguaje en que se escribe el código de cada curso (se ve en el catálogo). */
const LANG_LABEL = { python: "Python", sql: "SQL", javascript: "JavaScript", java: "Java" };

function renderCatalog() {
  const cards = DAW_COURSES.map((course) => {
    const answers = Object.values(courseState(course.id).answers);
    const right = answers.filter((h) => h.at(-1)).length;
    const progress = answers.length
      ? `${answers.length} preguntas respondidas · ${percent(right / answers.length)} de acierto`
      : "Sin empezar";
    return `
      <li class="daw-card" data-started="${answers.length > 0}">
        <div>
          <h2 class="daw-card__title"><a href="#/daw/${course.id}">${escapeHtml(course.title)}</a></h2>
          <p class="daw-card__subtitle">${escapeHtml(course.subtitle)}</p>
        </div>
        <p class="daw-card__lang">${LANG_LABEL[course.lang] ?? escapeHtml(course.lang)}</p>
        <p class="daw-card__progress">${progress}</p>
      </li>`;
  }).join("");
  return `
    <p class="daw-crumb"><a href="#/daw">Preparación DAW</a></p>
    <header class="course-hero">
      <p class="eyebrow">Ciclo DAW</p>
      <h1 class="course-hero__title" id="daw-title" tabindex="-1">Cursos de <em>DAW</em></h1>
      <p class="course-hero__lead">Teoría, ejercicios de escribir código y práctica por bloques. Si inicias sesión,
        el progreso se guarda en tu cuenta.</p>
      <div class="course-hero__cta"><a class="btn btn--ghost" href="#/daw/curriculo">Ver el currículo oficial del ciclo</a></div>
    </header>
    <ul class="daw-grid">${cards}</ul>`;
}

/* ---------- Recursos complementarios ---------- */

const ACCESS_LABEL = {
  accesible: "Accesible",
  descargable: "Descargable",
  registro: "Necesita registro",
  pago: "De pago",
  "licencia-no-identificada": "Licencia no identificada",
  obsoleto: "Obsoleto",
  "no-disponible": "No disponible",
  "no-verificado": "Sin verificar",
};

function resourcesHtml(resources, title, id) {
  if (!resources.length) return "";
  const items = resources
    .map(
      (r) => `<li class="daw-resource">
        <a href="${safeUrl(r.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(r.title)}</a>
        <span class="daw-resource__meta">${escapeHtml(r.author)} · ${escapeHtml(r.lang === "en" ? "En inglés" : "En español")} ·
          ${escapeHtml(ACCESS_LABEL[r.access] ?? r.access)}</span>
        <span class="daw-resource__desc">${escapeHtml(r.description)}</span>
        <span class="daw-resource__meta">Licencia: ${escapeHtml(r.license)}</span>
      </li>`,
    )
    .join("");
  return `<section class="course-section" aria-labelledby="${id}">
      <h2 class="section-title" id="${id}">${title}</h2>
      <ul class="daw-resources">${items}</ul>
      <p class="readiness__note">Material externo que la plataforma solo enlaza. Licencias revisadas el
        ${escapeHtml(resources[0].checked ?? "")}; compruébalas antes de reutilizar nada.</p>
    </section>`;
}

/* ---------- Panel de un curso ---------- */

function renderPanel(course) {
  const { bank, modules, lessons } = course;
  const stats = courseBlockStats(course.id, bank);
  const score = courseReadiness(stats, bank.exam.blocks);
  const due = dueQuestionIds(course.id, bank.questions.map((q) => q.id)).length;
  const progress = courseState(course.id);
  const completed = completedCount(progress, course.order);
  const last = lessons.get(progress.lastLesson?.slug);
  const pending = course.order.find((slug) => !progress.done?.[slug]);
  const blocks = bank.exam.blocks
    .map((b) => {
      const s = stats[b.slug];
      const module = modules.find((m) => m.slug === b.slug);
      const lessonLinks = (module?.lessons ?? [])
        .map((l) => {
          const done = progress.done?.[l.slug];
          return `<li${done ? ' class="is-done"' : ""}><a href="#/daw/${course.id}/leccion/${l.slug}">${escapeHtml(l.title)}</a>${
            done ? ' <span class="daw-done">✓ Completada</span>' : ""
          }</li>`;
        })
        .join("");
      return `
        <li class="block-row">
          <div class="block-row__head">
            <span class="block-row__name">${escapeHtml(t(b.title))}</span>
            <span class="block-row__weight">${b.weight} % · ${b.items} preguntas</span>
          </div>
          ${meter(s.rate, `Acierto en ${t(b.title)}`)}
          <div class="block-row__foot">
            <span>${s.answered ? `${percent(s.rate)} de acierto · ${s.answered} respondidas` : "Sin datos todavía"}</span>
            <span class="block-row__actions"><a class="btn btn--ghost" href="#/daw/${course.id}/practica/${b.slug}">Practicar</a></span>
          </div>
          ${lessonLinks ? `<ul class="daw-lessons" aria-label="Teoría de ${escapeHtml(t(b.title))}">${lessonLinks}</ul>` : ""}
        </li>`;
    })
    .join("");
  const first = lessons.get(course.order[0]);
  // Continuar: la última lección abierta si no está completada; si no, la primera pendiente
  const resume = last && !progress.done?.[last.lesson.slug] ? last : lessons.get(pending);
  return `
    <p class="daw-crumb"><a href="#/daw">Preparación DAW</a> › <a href="#/daw/cursos">Cursos de DAW</a></p>
    <header class="course-hero">
      <p class="eyebrow">${escapeHtml(course.info.subtitle)}</p>
      <h1 class="course-hero__title" id="daw-title" tabindex="-1">${escapeHtml(course.info.title)}</h1>
      <p class="course-hero__lead">${course.order.length} lecciones · ${bank.questions.length} preguntas, con las respuestas de código
        comprobadas ejecutando el código.</p>
      <p class="daw-units" id="daw-units">${completed} de ${course.order.length} lecciones completadas</p>
      ${meter(course.order.length ? completed / course.order.length : 0, "Lecciones completadas")}
      <div class="course-hero__cta">
        ${
          resume && (last || completed)
            ? `<a class="btn btn--primary btn--lg" href="#/daw/${course.id}/leccion/${resume.lesson.slug}">Continuar: ${escapeHtml(resume.lesson.title)} →</a>`
            : first
              ? `<a class="btn btn--primary btn--lg" href="#/daw/${course.id}/leccion/${first.lesson.slug}">Empezar por la teoría →</a>`
              : ""
        }
        ${due ? `<a class="btn btn--ghost btn--lg" href="#/daw/${course.id}/practica/repaso">Repaso de hoy (${due})</a>` : ""}
      </div>
    </header>
    <section class="course-section" aria-labelledby="daw-blocks-title">
      <h2 class="section-title" id="daw-blocks-title">Tu dominio: ${score} %</h2>
      <p class="readiness__note">Acierto de cada bloque ponderado por su peso. Orientativo.</p>
      <ul class="block-list">${blocks}</ul>
    </section>
    ${resourcesHtml(course.resources, "Recursos complementarios", "daw-resources-title")}
    ${originHtml(course.info)}`;
}

/** De dónde sale cada parte del curso (Fase D, 6.1): nada propio se presenta como oficial. */
function originHtml(info) {
  return `<section class="course-section" aria-labelledby="daw-origin-title">
      <h2 class="section-title" id="daw-origin-title">De dónde sale este contenido</h2>
      <p>${escapeHtml(info.structure)}</p>
      <dl class="daw-origin">
        <dt>Texto oficial</dt>
        <dd>Solo los resultados de aprendizaje y los criterios de evaluación, copiados literalmente del BOE en el
          <a href="#/daw/curriculo/${escapeHtml(info.module)}">currículo del módulo ${escapeHtml(info.module)}</a>.</dd>
        <dt>Resumen propio</dt>
        <dd>Los objetivos de cada lección. Cuando citan un RA, la relación la propone la plataforma: no es oficial.</dd>
        <dt>Explicaciones y ejemplos</dt>
        <dd>Escritos para la plataforma.</dd>
        <dt>Ejercicios y preguntas</dt>
        <dd>Creados para la plataforma, con las respuestas de código comprobadas al ejecutarlas. Son práctica: no son evaluaciones del centro.</dd>
        <dt>Recursos de terceros</dt>
        <dd>Las fuentes y los recursos complementarios solo se enlazan, con su autor y su licencia.</dd>
      </dl>
    </section>`;
}

/* ---------- Lección ---------- */

function quizHtml(lesson, lang) {
  if (!lesson.quiz?.length) return "";
  const items = lesson.quiz
    .map((item, n) => {
      const options = item.options
        .map((option, i) => {
          const text = item.code ? `<code class="opt-code">${escapeHtml(option)}</code>` : `<span>${renderInline(option)}</span>`;
          return `<label class="quiz__option" data-index="${i}"><input type="radio" name="daw-quiz-${n}" value="${i}"> ${text}</label>`;
        })
        .join("");
      return `
        <fieldset class="quiz__q" data-answer="${item.answer}">
          <legend><span class="quiz__num">${n + 1}</span> ${renderInline(item.q)}</legend>
          ${code(item.code, lang)}
          <div class="quiz__options">${options}</div>
          <div class="quiz__feedback" hidden><p>${renderInline(item.explain)}</p></div>
        </fieldset>`;
    })
    .join("");
  return `
    <section class="course-section" aria-labelledby="daw-quiz-title">
      <h2 class="section-title" id="daw-quiz-title">Comprueba lo que has leído</h2>
      <form class="daw-quiz" id="daw-quiz">${items}
        <button class="btn btn--primary" type="submit">Corregir</button>
        <p class="quiz__message" id="daw-quiz-result" role="status"></p>
      </form>
    </section>`;
}

function renderLesson(course, slug) {
  const entry = course.lessons.get(slug);
  const { lesson, module, index } = entry;
  const lang = course.info.lang;
  const prev = course.lessons.get(course.order[index - 1]);
  const next = course.lessons.get(course.order[index + 1]);
  const challenge = lesson.challenge;
  const faq = (lesson.assistant?.faq ?? [])
    .map((f) => `<details class="daw-faq"><summary>${renderInline(f.q)}</summary><p>${renderInline(f.a)}</p></details>`)
    .join("");
  const objectives = (lesson.objectives ?? []).map((o) => `<li>${renderInline(o)}</li>`).join("");
  const mistakes = (lesson.mistakes ?? [])
    .map((m) => `<li><strong>${renderInline(m.error)}</strong> ${renderInline(m.fix)}</li>`)
    .join("");
  const summary = (lesson.summary ?? []).map((item) => `<li>${renderInline(item)}</li>`).join("");
  const done = courseState(course.id).done?.[lesson.slug];
  const sources = (lesson.sources ?? [])
    .map((s) => `<li><a href="${safeUrl(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.title)}</a></li>`)
    .join("");
  return `
    <p class="daw-crumb"><a href="#/daw">Preparación DAW</a> › <a href="#/daw/${course.id}">${escapeHtml(course.info.title)}</a> ›
      ${escapeHtml(module.title)}</p>
    <header class="course-hero">
      <p class="eyebrow">Lección ${index + 1} de ${course.order.length}</p>
      <h1 class="course-hero__title" id="daw-title" tabindex="-1">${escapeHtml(lesson.title)}</h1>
      ${done ? '<p class="daw-done">✓ Lección completada</p>' : ""}
    </header>
    ${
      objectives
        ? `<section class="course-section" aria-labelledby="daw-goals-title">
            <h2 class="section-title" id="daw-goals-title">Al terminar sabrás</h2><ul class="daw-goals">${objectives}</ul>
            ${
              /\bRA ?\d/.test(lesson.objectives.join(" "))
                ? `<p class="readiness__note">Resumen propio de la plataforma. Los RA y criterios citados están, con su texto oficial, en el
                    <a href="#/daw/curriculo/${escapeHtml(course.info.module)}">currículo del módulo ${escapeHtml(course.info.module)}</a>.</p>`
                : ""
            }</section>`
        : ""
    }
    <section class="course-section daw-theory" aria-label="Teoría">${renderMarkdown(lesson.theory)}</section>
    <section class="course-section" aria-labelledby="daw-example-title">
      <h2 class="section-title" id="daw-example-title">Ejemplo</h2>
      ${code(lesson.example_code, lang)}
      <p class="readiness__note">${escapeHtml(courseTryHint(course.id))}</p>
    </section>
    <section class="course-section" aria-labelledby="daw-exercise-title">
      <h2 class="section-title" id="daw-exercise-title">Ejercicio</h2>
      ${renderMarkdown(lesson.exercise)}
      ${code(lesson.starter, lang)}
      ${lesson.assistant?.hint ? `<details class="daw-faq"><summary>Pista</summary><p>${renderInline(lesson.assistant.hint)}</p></details>` : ""}
      ${
        lesson.solution
          ? `<details class="daw-faq daw-solution-box"><summary>Ver una solución explicada</summary>
              ${code(lesson.solution.code, lesson.solution.lang ?? lang)}${renderMarkdown(lesson.solution.explain)}</details>`
          : ""
      }
    </section>
    ${
      mistakes
        ? `<section class="course-section" aria-labelledby="daw-mistakes-title">
            <h2 class="section-title" id="daw-mistakes-title">Errores frecuentes</h2><ul class="daw-mistakes">${mistakes}</ul></section>`
        : ""
    }
    ${
      summary
        ? `<section class="course-section" aria-labelledby="daw-summary-title">
            <h2 class="section-title" id="daw-summary-title">Resumen</h2><ul>${summary}</ul></section>`
        : ""
    }
    ${quizHtml(lesson, lang)}
    ${
      challenge
        ? `<section class="course-section" aria-labelledby="daw-challenge-title">
            <h2 class="section-title" id="daw-challenge-title">Reto: ${escapeHtml(challenge.title)}
              <span class="daw-stars" aria-label="Dificultad ${challenge.stars} de 3">${"★".repeat(challenge.stars)}${"☆".repeat(3 - challenge.stars)}</span></h2>
            ${renderMarkdown(challenge.exercise)}
            ${code(challenge.starter, lang)}
            <details class="daw-faq"><summary>Pista del reto</summary><p>${renderInline(challenge.hint)}</p></details>
          </section>`
        : ""
    }
    ${faq ? `<section class="course-section" aria-labelledby="daw-faq-title"><h2 class="section-title" id="daw-faq-title">Dudas frecuentes</h2>${faq}</section>` : ""}
    ${resourcesHtml(
      course.resources.filter((r) => r.lessons?.includes(`${course.id}/${lesson.slug}`)),
      "Recursos complementarios",
      "daw-lesson-resources-title",
    )}
    ${sources ? `<section class="course-section" aria-labelledby="daw-sources-title"><h2 class="section-title" id="daw-sources-title">Fuentes</h2><ul>${sources}</ul></section>` : ""}
    <section class="course-section daw-complete" aria-labelledby="daw-complete-title">
      <h2 class="section-title" id="daw-complete-title">¿Has terminado la lección?</h2>
      ${
        done
          ? `<p class="daw-done" role="status" tabindex="-1">✓ Completada. Cuenta en tu progreso del curso.</p>`
          : `<button class="btn btn--primary" type="button" data-daw-complete="${escapeHtml(lesson.slug)}">Marcar la lección como completada</button>
             <p class="readiness__note">Se guarda en este navegador y, con sesión, en tu cuenta.</p>`
      }
    </section>
    <nav class="daw-pager" aria-label="Lecciones">
      ${prev ? `<a class="btn btn--ghost" href="#/daw/${course.id}/leccion/${prev.lesson.slug}">← ${escapeHtml(prev.lesson.title)}</a>` : "<span></span>"}
      <a class="btn btn--primary" href="#/daw/${course.id}/practica/${module.slug}">Practicar este bloque</a>
      ${next ? `<a class="btn btn--ghost" href="#/daw/${course.id}/leccion/${next.lesson.slug}">${escapeHtml(next.lesson.title)} →</a>` : "<span></span>"}
    </nav>`;
}

const TRY = {
  programacion: "Para probarlo, pégalo en un archivo .py y ejecútalo con «python archivo.py» o en PyCharm.",
  entornos: "Para probarlo, pégalo en un archivo .py y ejecútalo con «python archivo.py».",
  marcas: "Para probarlo, pégalo en un archivo .py y ejecútalo con «python archivo.py». Los fragmentos de XML, HTML o JSON se pueden comprobar con el validador del W3C o con xmllint.",
  sql: "Para probarlo, cópialo en tu gestor de bases de datos (MySQL Workbench, DBeaver, SQLite…).",
  js: "Para probarlo, pégalo en la consola del navegador (F12) o ejecútalo con Node.",
  java: "Para probarlo, guárdalo en Main.java y ejecuta «java Main.java», o pégalo en tu IDE.",
};
const courseTryHint = (id) => TRY[id] ?? "";

/* ---------- Práctica ---------- */

function startPractice(course, slug) {
  const { answers } = courseState(course.id);
  let items;
  if (slug === "repaso") {
    const due = new Set(dueQuestionIds(course.id, course.bank.questions.map((q) => q.id)));
    items = shuffle(course.bank.questions.filter((q) => due.has(q.id))).slice(0, REVIEW_SIZE);
  } else {
    const pool = course.bank.questions.filter((q) => q.block === slug);
    const failed = shuffle(pool.filter((q) => answers[q.id]?.at(-1) === false));
    const fresh = shuffle(pool.filter((q) => !answers[q.id]));
    const rest = shuffle(pool.filter((q) => answers[q.id]?.at(-1) === true));
    items = [...failed, ...fresh, ...rest].slice(0, PRACTICE_SIZE);
  }
  session = {
    course: course.id,
    block: slug,
    items: items.map((q) => ({ q, answer: { selected: [], text: "", order: [] } })),
    index: 0,
    checked: false,
    correct: 0,
    combo: 0,
  };
}

function choiceHtml(q, answer, reveal) {
  const type = q.answer.length > 1 ? "checkbox" : "radio";
  return `<div class="quiz__options">${q.options
    .map(
      (option, i) => `
      <label class="quiz__option"${reveal && q.answer.includes(i) ? ' data-correct="true"' : ""}>
        <input type="${type}" name="daw-option" value="${i}"${answer.selected.includes(i) ? " checked" : ""}${reveal ? " disabled" : ""}>
        ${typeof option === "string" ? `<code class="opt-code">${escapeHtml(option)}</code>` : `<span>${md(option)}</span>`}
      </label>`,
    )
    .join("")}</div>`;
}

function fillHtml(q, answer, reveal, lang) {
  const wrong = reveal && !isCorrect(q, answer);
  return `
    ${code(q.code, lang)}
    <label class="daw-fill">Lo que va en <code>___</code>
      <input type="text" id="daw-fill" value="${escapeHtml(answer.text)}" autocomplete="off" autocapitalize="off"
        spellcheck="false"${reveal ? " disabled" : ""}>
    </label>
    ${wrong ? `<p class="daw-solution">Solución: <code>${escapeHtml(q.accept[0])}</code></p>` : ""}`;
}

function orderHtml(q, answer, reveal, lang) {
  const context = (q.code ?? "___").split("\n");
  const slot = context.findIndex((line) => line.trim() === "___");
  const before = slot >= 0 ? context.slice(0, slot).join("\n") : "";
  const after = slot >= 0 ? context.slice(slot + 1).join("\n") : "";
  const line = (i, action, label) =>
    `<li><button class="daw-line" type="button" data-daw="${action}" data-line="${i}" aria-label="${escapeHtml(label)}"${reveal ? " disabled" : ""}>
      <code>${escapeHtml(q.lines[i])}</code></button></li>`;
  const placed = answer.order.map((i, n) => line(i, "remove", `Línea ${n + 1}: ${q.lines[i].trim()}. Pulsa para quitarla.`)).join("");
  const available = stableShuffle(q.id, q.lines.length)
    .filter((i) => !answer.order.includes(i))
    .map((i) => line(i, "add", `${q.lines[i].trim()}. Pulsa para añadirla al final.`))
    .join("");
  const wrong = reveal && !isCorrect(q, answer);
  return `
    ${before ? code(before, lang) : ""}
    <p class="daw-order__label">Tu programa · pulsa una línea para quitarla</p>
    <ol class="daw-order" data-result="${reveal ? (wrong ? "ko" : "ok") : ""}">${placed || '<li class="daw-order__empty">Pulsa las líneas de abajo en orden.</li>'}</ol>
    ${after ? code(after, lang) : ""}
    ${available ? `<p class="daw-order__label">Líneas disponibles · pulsa para añadir</p><ul class="daw-order daw-order--pool">${available}</ul>` : ""}
    ${wrong ? `<p class="daw-solution">Solución:</p>${code(q.lines.join("\n"), lang)}` : ""}`;
}

function practiceQuestionHtml(course, item, number, reveal) {
  const { q, answer } = item;
  const lang = course.info.lang;
  const result = reveal ? (isCorrect(q, answer) ? "ok" : "ko") : null;
  const body =
    kind(q) === "fill"
      ? fillHtml(q, answer, reveal, lang)
      : kind(q) === "order"
        ? orderHtml(q, answer, reveal, lang)
        : `${code(q.code, lang)}${choiceHtml(q, answer, reveal)}`;
  const lesson = course.lessons.get(q.lesson);
  return `
    <fieldset class="quiz__q exam-q"${result ? ` data-result="${result}"` : ""}>
      <legend><span class="quiz__num">${number}</span> ${md(q.q)}</legend>
      ${body}
      ${
        reveal
          ? `<div class="quiz__feedback" tabindex="-1"><p class="quiz__verdict">${result === "ok" ? "¡Correcto!" : "No es correcta."}</p>
              <p>${md(q.explain)}</p>
              ${result === "ko" && lesson ? `<p class="study-links"><a href="#/daw/${course.id}/leccion/${q.lesson}">Repasar la teoría: ${escapeHtml(lesson.lesson.title)}</a></p>` : ""}</div>`
          : ""
      }
    </fieldset>`;
}

function renderPractice(course) {
  const block = course.bank.exam.blocks.find((b) => b.slug === session.block);
  const name = session.block === "repaso" ? "Repaso de hoy" : t(block.title);
  const head = `
    <p class="daw-crumb"><a href="#/daw">Preparación DAW</a> › <a href="#/daw/${course.id}">${escapeHtml(course.info.title)}</a></p>
    <div class="exam-bar">
      <span class="exam-bar__title" id="daw-title" tabindex="-1">Práctica · ${escapeHtml(name)}</span>
      <span>Pregunta ${Math.min(session.index + 1, session.items.length)} de ${session.items.length}</span>
      <span class="combo" data-hot="${session.combo >= 3}" aria-live="polite">Racha: ${session.combo}</span>
    </div>`;
  if (!session.items.length) {
    return `${head}<section class="course-section practice-end"><h2 class="section-title">Nada que repasar hoy</h2>
      <p>Las preguntas falladas vuelven al día siguiente, y las acertadas, cada vez más espaciadas.</p>
      <a class="btn btn--ghost" href="#/daw/${course.id}">Volver al curso</a></section>`;
  }
  if (session.index >= session.items.length) {
    return `${head}
      <section class="course-section practice-end">
        <h2 class="section-title">${session.correct} de ${session.items.length} correctas</h2>
        <p>Tu mejor racha en este curso: ${courseState(course.id).bestCombo} aciertos seguidos.</p>
        <div class="course-hero__cta">
          ${session.block === "repaso" ? "" : `<button class="btn btn--primary" type="button" data-daw="again">Otra tanda de ${escapeHtml(name)}</button>`}
          <a class="btn btn--ghost" href="#/daw/${course.id}">Volver al curso</a>
        </div>
      </section>`;
  }
  const item = session.items[session.index];
  return `${head}
    <form class="exam-form" id="daw-practice">
      ${practiceQuestionHtml(course, item, session.index + 1, session.checked)}
      <div class="exam-actions">
        ${
          session.checked
            ? `<button class="btn btn--primary" type="button" data-daw="next">${session.index + 1 < session.items.length ? "Siguiente →" : "Ver resultado"}</button>`
            : `<button class="btn btn--primary" type="submit">Comprobar</button>`
        }
      </div>
      <p class="quiz__message" id="daw-message" role="alert"></p>
    </form>`;
}

function check() {
  const item = session.items[session.index];
  if (!isComplete(item.q, item.answer)) {
    $("#daw-message").textContent = missing(item.q);
    return false;
  }
  const ok = isCorrect(item.q, item.answer);
  const course = courseState(session.course);
  recordCourseAnswer(session.course, item.q.id, ok);
  session.checked = true;
  session.correct += ok;
  session.combo = ok ? session.combo + 1 : 0;
  course.bestCombo = Math.max(course.bestCombo, session.combo);
  saveCourse(session.course);
  return true;
}

/* ---------- Pintado y eventos ---------- */

let current = null; // datos del curso a la vista

function parse(route) {
  const [, , id, view, arg] = route.split("/").map(decodeURIComponent); // "#/daw/<id>/<view>/<arg>"
  return { id, view, arg };
}

const DAW_BACK = { href: "#/daw", label: "Ver los cursos de DAW" };

async function render(route, { focus = false } = {}) {
  const { id, view, arg } = parse(route);
  if (id === "curriculo") {
    current = null;
    await renderCurriculumRoute(route, view);
  } else if (!id || id === "cursos") {
    current = null;
    root().innerHTML = renderCatalog();
  } else if (!courseInfo(id)) {
    current = null;
    root().innerHTML = notFoundHtml({ titleId: "daw-title", route, what: "este curso", back: DAW_BACK });
  } else {
    if (current?.id !== id) root().innerHTML = `<p class="empty-state" id="daw-title" tabindex="-1">Cargando el curso…</p>`;
    try {
      current = await loadCourse(id);
    } catch {
      root().innerHTML = `<p class="empty-state" id="daw-title" tabindex="-1">No se pudo cargar el curso. Comprueba la conexión y recarga.</p>`;
      return;
    }
    if (location.hash !== route) return; // el alumno se fue mientras cargaba
    if (view === "leccion" && current.lessons.has(arg)) {
      if (visitLesson(courseState(id), arg)) saveCourse(id); // «Continuar» en el panel del curso
      root().innerHTML = renderLesson(current, arg);
    } else if (view === "practica" && (arg === "repaso" || current.bank.exam.blocks.some((b) => b.slug === arg))) {
      if (session?.course !== id || session.block !== arg) startPractice(current, arg);
      root().innerHTML = renderPractice(current);
    } else if (view) {
      // #/daw/<curso>/<algo que no existe>: lección, bloque o sección mal escritos
      root().innerHTML = notFoundHtml({ titleId: "daw-title", route, back: { href: `#/daw/${id}`, label: "Volver al curso" } });
    } else {
      root().innerHTML = renderPanel(current);
    }
  }
  if (focus) $("#daw-title")?.focus();
}

async function renderCurriculumRoute(route, moduleId) {
  root().innerHTML = `<p class="empty-state" id="daw-title" tabindex="-1">Cargando el currículo…</p>`;
  try {
    const data = await loadCurriculum();
    if (location.hash === route) root().innerHTML = renderCurriculum(data, moduleId);
  } catch {
    root().innerHTML = `<p class="empty-state" id="daw-title" tabindex="-1">No se pudo cargar el currículo. Comprueba la conexión y recarga.</p>`;
  }
}

const rerender = (focus = false) => render(location.hash, { focus });

function onClick(event) {
  const complete = event.target.closest("[data-daw-complete]");
  if (complete && current) {
    if (completeLesson(courseState(current.id), complete.dataset.dawComplete)) saveCourse(current.id);
    rerender().then(() => $(".daw-complete .daw-done")?.focus());
    return;
  }
  const target = event.target.closest("[data-daw]");
  if (!target || !session) return;
  const item = session.items[session.index];
  switch (target.dataset.daw) {
    case "add":
    case "remove": {
      const line = Number(target.dataset.line);
      item.answer.order = target.dataset.daw === "add" ? [...item.answer.order, line] : item.answer.order.filter((i) => i !== line);
      rerender().then(() => $(".daw-line:not([disabled])")?.focus());
      break;
    }
    case "next":
      session.index += 1;
      session.checked = false;
      rerender(true);
      break;
    case "again":
      startPractice(current, session.block);
      rerender(true);
      break;
    default:
      break;
  }
}

function onChange(event) {
  const input = event.target;
  if (input.name === "daw-option" && session) {
    const form = input.closest("form");
    session.items[session.index].answer.selected = [...form.querySelectorAll('input[name="daw-option"]:checked')].map((i) => Number(i.value));
  }
}

function onInput(event) {
  if (event.target.id === "daw-fill" && session) session.items[session.index].answer.text = event.target.value;
}

function onSubmit(event) {
  if (event.target.id === "daw-practice") {
    event.preventDefault();
    if (check()) rerender().then(() => $(".quiz__feedback")?.focus());
  } else if (event.target.id === "daw-quiz") {
    event.preventDefault();
    const fieldsets = [...event.target.querySelectorAll("fieldset")];
    let right = 0;
    for (const fieldset of fieldsets) {
      const answer = Number(fieldset.dataset.answer);
      const chosen = fieldset.querySelector("input:checked");
      const ok = chosen && Number(chosen.value) === answer;
      right += ok ? 1 : 0;
      fieldset.dataset.result = ok ? "ok" : "ko";
      fieldset.querySelector(`[data-index="${answer}"]`).dataset.correct = "true";
      fieldset.querySelector(".quiz__feedback").hidden = false;
    }
    $("#daw-quiz-result").textContent = `${right} de ${fieldsets.length} correctas.`;
  }
}

let listening = false;

/** Muestra la zona de cursos de DAW. */
export function openDaw(route, { moveFocus = true } = {}) {
  if (!listening) {
    root().addEventListener("click", onClick);
    root().addEventListener("change", onChange);
    root().addEventListener("input", onInput);
    root().addEventListener("submit", onSubmit);
    listening = true;
  }
  return render(route, { focus: moveFocus });
}

/** Repinta si está a la vista (p. ej. al llegar el progreso de la cuenta), salvo en mitad de una tanda. */
export function refreshDaw() {
  const practicing = session && session.index < session.items.length && location.hash.includes("/practica/");
  if (location.hash.startsWith("#/daw") && !practicing) render(location.hash);
}
