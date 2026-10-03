/* Portada: ficha del curso (qué aprenderás, temario, requisitos) con «Continuar donde lo dejaste». */

import { courseTotals, formatDuration, lessonMinutes, stars } from "./course.js";
import { game, levelInfo, streak } from "./game.js";
import { escapeHtml } from "./markdown.js";
import { state } from "./store.js";

const HOW = [
  ["Aprende", "Teoría breve y un ejemplo que ejecutas en la consola, siempre a mano."],
  ["Practica", "Resuelve el ejercicio y pulsa «Comprobar»: los tests te dicen si está bien."],
  ["Comprueba", "Mini-quiz de 3 preguntas. Cada respuesta te explica el porqué."],
];

const INCLUDES = [
  "Python 3 real ejecutándose en tu navegador",
  "Corrección automática de cada ejercicio",
  "Errores de Python explicados en español",
  "Asistente con pistas en cada lección",
  "Progreso sincronizado con una cuenta opcional",
];

const pad = (n) => String(n).padStart(2, "0");

/** "Python, de cero a profesional" → "Python, <em>de cero a profesional</em>" */
function titleHtml(title) {
  const [head, ...rest] = title.split(", ");
  return rest.length ? `${escapeHtml(head)}, <em>${escapeHtml(rest.join(", "))}</em>` : escapeHtml(title);
}

function lessonStatus(slug, nextSlug) {
  if (state.completed.has(slug)) return { key: "done", label: "Completada", icon: "✓" };
  if (slug === nextSlug) return { key: "current", label: "Siguiente", icon: "▸" };
  return { key: "todo", label: "Pendiente", icon: "" };
}

function renderCta(content, next, done, total) {
  if (done === 0 && game.read.length === 0) {
    return `<a class="btn btn--primary btn--lg" href="#/leccion/${next.slug}">Empezar la primera lección →</a>
      <a class="btn btn--ghost btn--lg" href="#/pcap">Ver el examen PCAP</a>
      <span class="course-hero__note">Unos 15 minutos por lección</span>`;
  }
  if (done === total) {
    return `<a class="btn btn--primary btn--lg" href="#/leccion/${content.order[0]}">Repasar desde el principio</a>
      <a class="btn btn--ghost btn--lg" href="#/pcap">Hacer un simulacro</a>`;
  }
  return `<a class="btn btn--primary btn--lg" href="#/leccion/${next.slug}">Continuar: ${escapeHtml(next.title)} →</a>
    <a class="btn btn--ghost btn--lg" href="#/pcap">Examen PCAP</a>`;
}

function renderProgress(done, total) {
  if (done === 0 && game.read.length === 0) return "";
  const percent = Math.round((done / total) * 100);
  const level = levelInfo();
  const days = streak();
  return `
    <section class="course-progress" aria-labelledby="home-progress-title">
      <div class="course-progress__head">
        <h2 class="course-progress__title" id="home-progress-title">Tu progreso</h2>
        <span class="course-progress__value">${percent} %</span>
      </div>
      <div class="meter" role="progressbar" aria-label="Progreso del curso" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${percent}">
        <span class="meter__fill" style="--value: ${percent}%"></span>
      </div>
      <ul class="course-progress__facts">
        <li><strong>${done}/${total}</strong> lecciones</li>
        <li><strong>Nivel ${level.number}</strong> ${escapeHtml(level.name)}</li>
        <li><strong>${level.xp}</strong> XP</li>
        <li><strong>${days}</strong> ${days === 1 ? "día" : "días"} de racha</li>
      </ul>
    </section>`;
}

function renderSyllabus(content, nextSlug) {
  const currentModule = content.lessons.get(nextSlug)?.module.slug;
  return content.modules
    .map((module, i) => {
      const finished = module.lessons.filter((l) => state.completed.has(l.slug)).length;
      const minutes = module.lessons.reduce((sum, l) => sum + lessonMinutes(l), 0);
      const lessons = module.lessons
        .map((lesson) => {
          const status = lessonStatus(lesson.slug, nextSlug);
          const star = stars(lesson.challenge.stars);
          const index = content.lessons.get(lesson.slug).index + 1;
          return `
            <li class="syllabus__lesson" data-status="${status.key}">
              <span class="syllabus__num" aria-hidden="true">${status.icon || pad(index)}</span>
              <a class="syllabus__link" href="#/leccion/${lesson.slug}">${escapeHtml(lesson.title)}<span class="visually-hidden"> (${status.label})</span></a>
              <span class="syllabus__meta">
                <span class="syllabus__stars" title="Reto: ${star.label}"><span aria-hidden="true">${star.visual}</span><span class="visually-hidden">Reto de ${star.label}.</span></span>
                ${lessonMinutes(lesson)} min
              </span>
            </li>`;
        })
        .join("");
      return `
        <details class="syllabus__module"${module.slug === currentModule ? " open" : ""}>
          <summary>
            <span class="syllabus__eyebrow">Módulo ${pad(i + 1)}</span>
            <span class="syllabus__title">${escapeHtml(module.title)}</span>
            <span class="syllabus__summary">${escapeHtml(module.summary ?? "")}</span>
            <span class="syllabus__info">${module.lessons.length} lecciones · ≈ ${formatDuration(minutes)} · ${finished}/${module.lessons.length} completadas</span>
          </summary>
          <ol class="syllabus__lessons">${lessons}</ol>
        </details>`;
    })
    .join("");
}

/**
 * @param {object} content  { course, modules, order, lessons }
 * @param {string} nextSlug lección por la que continuar
 */
export function renderHome(content, nextSlug) {
  const course = content.course;
  const totals = courseTotals(content);
  const done = state.completed.size;
  const next = content.lessons.get(nextSlug);
  const greeting = state.user ? `Hola, ${escapeHtml(state.user.display_name)} · ` : "";
  const answered = Object.keys(pcap.answers).length;
  const exams = pcap.exams.length;
  const lastExam = pcap.exams.at(-1);
  const bestExam = exams ? Math.max(...pcap.exams.map((exam) => exam.score)) : null;
  const moduleDone = next.module.lessons.filter((lesson) => state.completed.has(lesson.slug)).length;
  const modulePercent = Math.round((moduleDone / next.module.lessons.length) * 100);

  return `
    <header class="course-hero">
      <p class="eyebrow">${greeting}Ruta Python · ${escapeHtml(course.level)}</p>
      <h1 class="course-hero__title" id="home-title" tabindex="-1">${titleHtml(course.title)}</h1>
      <p class="course-hero__lead">${escapeHtml(course.tagline)}</p>
    </header>

    <section class="home-continue" aria-labelledby="continue-title">
      <p class="home-continue__label">Continúa donde lo dejaste</p>
      <h2 class="home-continue__title" id="continue-title">${escapeHtml(next.title)}</h2>
      <p class="home-continue__meta">${escapeHtml(next.module.title)} · Lección ${next.index + 1} de ${totals.lessons}</p>
      <div class="home-continue__progress">
        <div class="progress-bar" role="progressbar" aria-label="Progreso del módulo actual" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${modulePercent}"><span class="progress-bar__fill" style="--value: ${modulePercent}%"></span></div>
        <strong>${modulePercent}%</strong>
      </div>
      <div class="home-continue__action"><a class="btn btn--primary btn--lg" href="#/leccion/${next.slug}">${done === totals.lessons ? "Repasar desde el principio" : done === 0 && game.read.length === 0 ? "Empezar primera lección" : "Continuar"} →</a></div>
    </section>

    <div class="home-secondary-grid">
      ${renderProgress(done, totals.lessons)}
      <section class="home-panel home-pcap" aria-labelledby="home-pcap-title">
        <div class="home-panel__head"><h2 class="home-panel__title" id="home-pcap-title">Preparación PCAP</h2><a class="home-panel__meta" href="#/pcap">Abrir PCAP →</a></div>
        <dl class="home-pcap__stats">
          <div><dt>Preguntas respondidas</dt><dd>${answered}</dd></div>
          <div><dt>Simulacros</dt><dd>${exams}</dd></div>
          <div><dt>Último simulacro</dt><dd>${lastExam ? `${lastExam.score} %` : "—"}</dd></div>
          <div><dt>Mejor simulacro</dt><dd>${bestExam === null ? "—" : `${bestExam} %`}</dd></div>
        </dl>
        <a class="btn btn--secondary" href="#/pcap">${lastExam ? "Continuar preparación" : "Empezar preparación PCAP"}</a>
      </section>
    </div>

    <section class="course-section" aria-labelledby="home-activity-title">
      <div class="section-head"><h2 class="section-title" id="home-activity-title">Actividad reciente</h2><p class="section-head__meta">${done} lecciones completadas</p></div>
      <ul class="home-activity">
        ${game.read.slice(-4).reverse().map((slug) => { const lesson = content.lessons.get(slug); return lesson ? `<li><span>${escapeHtml(lesson.title)}</span><span class="home-activity__muted">Teoría revisada</span></li>` : ""; }).join("") || `<li><span>Aún no hay actividad</span><span class="home-activity__muted">Empieza una lección</span></li>`}
      </ul>
    </section>

    <section class="course-section" aria-labelledby="home-syllabus-title">
      <div class="section-head"><h2 class="section-title" id="home-syllabus-title">Ruta Python</h2><p class="section-head__meta">${content.modules.length} módulos · ${totals.lessons} lecciones · ≈ ${formatDuration(totals.minutes)}</p></div>
      <div class="syllabus">${renderSyllabus(content, nextSlug)}</div>
    </section>

    <section class="course-section" aria-labelledby="home-how-title">
      <h2 class="section-title" id="home-how-title">Cómo funciona una lección</h2>
      <ol class="how-list">${HOW.map(([title, text], i) => `<li class="how"><span class="how__num" aria-hidden="true">${pad(i + 1)}</span><h3>${title}</h3><p>${text}</p></li>`).join("")}</ol>
    </section>

    <section class="course-section course-columns" aria-label="Qué incluye y requisitos">
      <div><h2 class="section-title">Incluye</h2><ul class="checklist">${INCLUDES.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>
      <div><h2 class="section-title">Requisitos</h2><ul class="checklist checklist--plain">${course.requirements.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>
    </section>`;
}
