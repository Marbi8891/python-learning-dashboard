import { DEVOPS_COURSE } from "./devops-content.js";
import { courseState, recordCourseAnswer, saveCourse } from "./course-store.js";
import { completedCount, completeLesson, visitLesson } from "./lesson-progress.js";
import { escapeHtml, renderMarkdown, safeUrl } from "./markdown.js";

const COURSE_ID = "devops";
const root = () => document.querySelector("#devops-view");
const lessons = DEVOPS_COURSE.weeks.flatMap((week) => week.lessons.map((lesson) => ({ ...lesson, week })));
const order = lessons.map((lesson) => lesson.slug);
let listening = false;
let current = null;
let lastResult = null;

const progress = () => courseState(COURSE_ID);
const doneCount = () => completedCount(progress(), order);
const pct = () => Math.round((doneCount() / order.length) * 100);
const findLesson = (slug) => lessons.find((lesson) => lesson.slug === slug);

function progressBar(value, label) {
  return `<div class="devops-meter" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${value}">
    <span style="--devops-progress:${value}%"></span></div>`;
}

function renderCatalog() {
  const completed = doneCount();
  const weeks = DEVOPS_COURSE.weeks.map((week) => {
    const count = week.lessons.filter((lesson) => progress().done?.[lesson.slug]).length;
    return `
      <section class="devops-week" aria-labelledby="devops-${week.id}">
        <div class="devops-week__head">
          <div><p class="eyebrow">Itinerario · Primer mes</p><h2 id="devops-${week.id}">${escapeHtml(week.title)}</h2></div>
          <span class="devops-count">${count}/${week.lessons.length} completadas</span>
        </div>
        ${progressBar(Math.round((count / week.lessons.length) * 100), `Progreso de ${week.title}`)}
        <ol class="devops-lessons">
          ${week.lessons.map((lesson) => {
            const isDone = Boolean(progress().done?.[lesson.slug]);
            return `<li class="devops-lesson" data-completed="${isDone}">
              <span class="devops-lesson__status" aria-hidden="true">${isDone ? "✓" : "○"}</span>
              <div class="devops-lesson__body">
                <h3><a href="#/devops/leccion/${lesson.slug}">${escapeHtml(lesson.title)}</a></h3>
                <p>${escapeHtml(lesson.area)} · ${lesson.minutes} min</p>
              </div>
              <span class="devops-lesson__state">${isDone ? "Completada" : "Pendiente"}</span>
            </li>`;
          }).join("")}
        </ol>
      </section>`;
  }).join("");

  return `
    <header class="devops-hero">
      <p class="eyebrow">Python Learning Dashboard · Nuevo itinerario</p>
      <h1 class="course-hero__title" id="devops-title" tabindex="-1">Academia <em>DevOps</em></h1>
      <p class="course-hero__lead">Aprende a administrar Linux, trabajar con GitHub, operar contenedores Docker y automatizar tareas con Python.</p>
      <div class="devops-facts">
        <div><strong>9 meses</strong><span>Duración prevista</span></div>
        <div><strong>20 h/semana</strong><span>Ritmo del itinerario</span></div>
        <div><strong>4 semanas</strong><span>Contenido disponible</span></div>
      </div>
      <div class="devops-overall">
        <div class="devops-overall__label"><strong>Primer mes</strong><span>${completed} de ${order.length} lecciones · ${pct()} %</span></div>
        ${progressBar(pct(), "Progreso del primer mes")}
      </div>
    </header>
    <div class="devops-catalog">
      <div class="devops-catalog__intro"><h2>Plan de estudio</h2><p>Completa las lecciones y supera sus preguntas para registrar el progreso. Los laboratorios se realizan en tu máquina virtual; la web no ejecuta comandos en tu equipo.</p></div>
      ${weeks}
    </div>
    <section class="devops-project">
      <p class="eyebrow">Entrega del primer mes</p>
      <h2>SysMonitor</h2>
      <p>Desarrolla una herramienta Python que genere un informe del sistema. Añade pruebas, documentación y un Dockerfile. Guarda el proyecto en GitHub y utiliza un Pull Request para revisar los cambios.</p>
      <ul><li>Script Python con argumentos de terminal.</li><li>Pruebas automatizadas.</li><li>README con instrucciones de uso.</li><li>Dockerfile y ejecución reproducible.</li></ul>
    </section>`;
}

function renderLesson(lesson) {
  const index = order.indexOf(lesson.slug);
  const previous = lessons[index - 1];
  const next = lessons[index + 1];
  const done = Boolean(progress().done?.[lesson.slug]);
  const result = lastResult?.slug === lesson.slug ? lastResult : null;
  const quiz = lesson.quiz.map((question, i) => `
    <fieldset class="devops-question">
      <legend><span>${i + 1}.</span> ${escapeHtml(question.q)}</legend>
      <div class="devops-options">
        ${question.options.map((option, optionIndex) => `
          <label><input type="radio" name="q-${i}" value="${optionIndex}" ${result?.answers?.[i] === optionIndex ? "checked" : ""} ${result?.passed || done ? "disabled" : ""}>
            <span>${escapeHtml(option)}</span></label>`).join("")}
      </div>
      ${result ? `<p class="devops-explain" data-correct="${result.correct[i]}">${result.correct[i] ? "Correcto." : "Respuesta incorrecta."} ${escapeHtml(question.explain)}</p>` : ""}
    </fieldset>`).join("");

  const sources = lesson.sources.map((source) => `<li><a href="${safeUrl(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.title)}</a></li>`).join("");
  return `
    <p class="daw-crumb"><a href="#/devops">Academia DevOps</a> › <a href="#/devops">${escapeHtml(lesson.week.title)}</a></p>
    <header class="course-hero devops-lesson-hero">
      <p class="eyebrow">${escapeHtml(lesson.area)} · ${escapeHtml(lesson.week.title)}</p>
      <h1 class="course-hero__title" id="devops-title" tabindex="-1">${escapeHtml(lesson.title)}</h1>
      <p class="course-hero__lead">${lesson.minutes} minutos · ${done ? "Lección completada" : "Lección pendiente"}</p>
    </header>
    <article class="devops-content">
      <section class="course-section devops-theory"><h2 class="section-title">Teoría</h2><div class="prose">${renderMarkdown(lesson.theory)}</div></section>
      <section class="course-section"><h2 class="section-title">Ejemplo</h2><pre class="devops-code" tabindex="0"><code>${escapeHtml(lesson.example)}</code></pre><p class="readiness__note">Ejemplo orientativo. Ejecútalo en tu máquina virtual después de revisar cada comando.</p></section>
      <section class="course-section"><h2 class="section-title">Laboratorio</h2><p>${escapeHtml(lesson.task)}</p><div class="devops-deliverable"><strong>Entrega verificable</strong><p>${escapeHtml(lesson.deliverable)}</p></div></section>
      <section class="course-section"><h2 class="section-title">Comprueba lo aprendido</h2>
        ${result?.passed || done ? `<p class="devops-result devops-result--ok" role="status">Lección completada. El progreso se guarda en tu cuenta si has iniciado sesión.</p>` : result ? `<p class="devops-result devops-result--retry" role="status">Has acertado ${result.correct.filter(Boolean).length} de ${lesson.quiz.length}. Revisa las explicaciones e inténtalo de nuevo.</p>` : ""}
        <form id="devops-quiz" data-lesson="${lesson.slug}">
          ${quiz}
          ${result?.passed || done ? "" : '<button class="btn btn--primary" type="submit">Corregir respuestas</button>'}
        </form>
      </section>
      <section class="course-section devops-sources"><h2 class="section-title">Documentación</h2><ul>${sources}</ul></section>
    </article>
    <nav class="daw-pager" aria-label="Navegación de lecciones">
      ${previous ? `<a class="btn btn--ghost" href="#/devops/leccion/${previous.slug}">← ${escapeHtml(previous.title)}</a>` : '<a class="btn btn--ghost" href="#/devops">Volver al itinerario</a>'}
      <a class="btn btn--primary" href="${next ? `#/devops/leccion/${next.slug}` : "#/devops"}">${next ? "Siguiente lección →" : "Volver al itinerario"}</a>
    </nav>`;
}

function render(route, { focus = false } = {}) {
  const match = route.match(/^#\/devops(?:\/leccion\/([a-z0-9-]+))?$/);
  if (!match) {
    root().innerHTML = `<section class="course-section"><h1 id="devops-title" tabindex="-1">Ruta no encontrada</h1><p>La dirección de Academia DevOps no existe.</p><a href="#/devops">Volver al itinerario</a></section>`;
  } else if (!match[1]) {
    current = null;
    root().innerHTML = renderCatalog();
  } else {
    current = findLesson(match[1]) ?? null;
    if (!current) {
      root().innerHTML = `<section class="course-section"><h1 id="devops-title" tabindex="-1">Lección no encontrada</h1><a href="#/devops">Volver al itinerario</a></section>`;
    } else {
      if (visitLesson(progress(), current.slug)) saveCourse(COURSE_ID);
      root().innerHTML = renderLesson(current);
    }
  }
  if (focus) root().querySelector("#devops-title")?.focus();
  document.title = current ? `${current.title} · Academia DevOps` : "Academia DevOps · Python Learning Dashboard";
}

function onSubmit(event) {
  if (event.target.id !== "devops-quiz" || !current) return;
  event.preventDefault();
  const answers = current.quiz.map((_, i) => {
    const selected = event.target.querySelector(`input[name="q-${i}"]:checked`);
    return selected ? Number(selected.value) : -1;
  });
  const correct = current.quiz.map((question, i) => answers[i] === question.answer);
  current.quiz.forEach((question, i) => recordCourseAnswer(COURSE_ID, `devops-${current.slug}-q${i + 1}`, correct[i]));
  const passed = correct.every(Boolean);
  if (passed) completeLesson(progress(), current.slug);
  saveCourse(COURSE_ID);
  lastResult = { slug: current.slug, answers, correct, passed };
  render(location.hash, { focus: true });
}

export function openDevops(route, { moveFocus = true } = {}) {
  if (!listening) {
    root().addEventListener("submit", onSubmit);
    listening = true;
  }
  render(route, { focus: moveFocus });
}

export function refreshDevops() {
  if (location.hash.startsWith("#/devops")) render(location.hash);
}
