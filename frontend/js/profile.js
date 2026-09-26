/* «Mi aprendizaje»: nivel, estadísticas, progreso por módulo, actividad, logros e historial por lección. */

import { stars } from "./course.js";
import { BADGES, game, levelInfo, streak, today } from "./game.js";
import { escapeHtml } from "./markdown.js";
import { state } from "./store.js";

const WEEKS = 12;
const DAY_NAMES = new Intl.DateTimeFormat("es-ES", { weekday: "long", day: "numeric", month: "long" });

/** Lista de logros (la usan el perfil y la vitrina). */
export function badgesHtml() {
  return BADGES.map((badge) => {
    const unlocked = game.badges.includes(badge.id);
    return `
      <li class="badge" data-unlocked="${unlocked}">
        <span class="badge__icon" aria-hidden="true">${escapeHtml(badge.icon)}</span>
        <span class="badge__text">
          <strong>${escapeHtml(badge.name)}</strong>
          <span>${escapeHtml(badge.goal)}</span>
          <span class="visually-hidden">${unlocked ? "(Conseguido)" : "(Pendiente)"}</span>
        </span>
      </li>`;
  }).join("");
}

/** Últimas 12 semanas, de lunes a domingo, con los días de actividad marcados. */
function activityHtml() {
  const active = new Set(game.days);
  const now = new Date();
  const start = new Date(now);
  start.setDate(now.getDate() - ((now.getDay() + 6) % 7) - (WEEKS - 1) * 7); // lunes de hace 11 semanas
  const cells = [];
  let count = 0;
  for (const cursor = new Date(start); cursor <= now; cursor.setDate(cursor.getDate() + 1)) {
    const on = active.has(today(cursor));
    if (on) count += 1;
    cells.push(`<span class="activity__day" data-active="${on}" title="${DAY_NAMES.format(cursor)}: ${on ? "con actividad" : "sin actividad"}"></span>`);
  }
  const label = `${count} ${count === 1 ? "día" : "días"} con actividad en las últimas ${WEEKS} semanas`;
  return `
    <div class="activity" role="img" aria-label="${label}">${cells.join("")}</div>
    <p class="activity__legend"><span class="activity__day" data-active="true" aria-hidden="true"></span> Día con actividad · ${label}</p>`;
}

function historyRows(content) {
  return content.order
    .map((slug, i) => {
      const lesson = content.lessons.get(slug);
      const exercise = game.firstTry.includes(slug)
        ? "✓ a la primera"
        : game.passed.includes(slug) || state.completed.has(slug)
          ? "✓"
          : game.tried.includes(slug)
            ? "En curso"
            : "—";
      const quiz = game.quiz[slug] === undefined ? "—" : `${game.quiz[slug]}/3`;
      const star = stars(lesson.challenge.stars);
      const challenge = game.challenges.includes(slug)
        ? `<span aria-hidden="true">${star.visual}</span><span class="visually-hidden">Superado, ${star.label}</span>`
        : "—";
      return `
        <tr data-done="${state.completed.has(slug)}">
          <th scope="row"><a href="#/leccion/${slug}"><span class="history__num">${String(i + 1).padStart(2, "0")}</span>${escapeHtml(lesson.title)}</a></th>
          <td>${game.read.includes(slug) || state.completed.has(slug) ? "✓" : "—"}</td>
          <td>${exercise}</td>
          <td>${quiz}</td>
          <td class="history__stars">${challenge}</td>
        </tr>`;
    })
    .join("");
}

/** @param {object} content { modules, order, lessons } */
export function renderProfile(content) {
  const total = content.order.length;
  const done = state.completed.size;
  const level = levelInfo();
  const days = streak();
  const answered = Object.values(game.quiz).reduce((sum, best) => sum + best, 0);
  const questions = total * 3;
  const title = state.user ? escapeHtml(state.user.display_name) : "Mi aprendizaje";

  const modules = content.modules
    .map((module) => {
      const finished = module.lessons.filter((l) => state.completed.has(l.slug)).length;
      const percent = Math.round((finished / module.lessons.length) * 100);
      return `
        <li class="module-progress">
          <span class="module-progress__name">${escapeHtml(module.title)}</span>
          <span class="module-progress__count">${finished}/${module.lessons.length}</span>
          <span class="meter" role="progressbar" aria-label="${escapeHtml(module.title)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${percent}">
            <span class="meter__fill" style="--value: ${percent}%"></span>
          </span>
        </li>`;
    })
    .join("");

  return `
    <header class="profile-hero">
      <p class="eyebrow">${state.user ? "Mi aprendizaje" : "Tu progreso en este navegador"}</p>
      <h1 class="profile-hero__title" id="profile-title" tabindex="-1">${title}</h1>
      <div class="level-card">
        <span class="level-card__badge" aria-hidden="true">${level.number}</span>
        <div class="level-card__body">
          <p class="level-card__name">Nivel ${level.number} · ${escapeHtml(level.name)}</p>
          <div class="meter meter--gold" role="progressbar" aria-label="Progreso hacia el siguiente nivel" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${level.progress}">
            <span class="meter__fill" style="--value: ${level.progress}%"></span>
          </div>
          <p class="level-card__next">${level.xp} XP · ${level.next ? `${level.next.xp - level.xp} XP para «${escapeHtml(level.next.name)}»` : "Nivel máximo"}</p>
        </div>
      </div>
      ${state.user ? "" : `<p class="profile-hero__note">Crea una cuenta o inicia sesión para guardar tus lecciones completadas en todos tus dispositivos.</p>`}
    </header>

    <section class="course-section" aria-labelledby="profile-stats-title">
      <h2 class="section-title" id="profile-stats-title">En cifras</h2>
      <dl class="kpis">
        <div class="kpi"><dt>Lecciones</dt><dd>${done}<small>/${total}</small></dd></div>
        <div class="kpi"><dt>Aciertos en quizzes</dt><dd>${answered}<small>/${questions}</small></dd></div>
        <div class="kpi"><dt>Retos superados</dt><dd>${game.challenges.length}<small>/${total}</small></dd></div>
        <div class="kpi"><dt>Racha actual</dt><dd>${days}<small> ${days === 1 ? "día" : "días"}</small></dd></div>
      </dl>
    </section>

    <div class="course-columns">
      <section class="course-section" aria-labelledby="profile-modules-title">
        <h2 class="section-title" id="profile-modules-title">Por módulo</h2>
        <ul class="module-progress-list">${modules}</ul>
      </section>
      <section class="course-section" aria-labelledby="profile-activity-title">
        <h2 class="section-title" id="profile-activity-title">Actividad</h2>
        ${activityHtml()}
      </section>
    </div>

    <section class="course-section" aria-labelledby="profile-badges-title">
      <div class="section-head">
        <h2 class="section-title" id="profile-badges-title">Logros</h2>
        <p class="section-head__meta">${game.badges.length} de ${BADGES.length} conseguidos</p>
      </div>
      <ul class="badges__list badges__list--grid">${badgesHtml()}</ul>
    </section>

    <section class="course-section" aria-labelledby="profile-history-title">
      <h2 class="section-title" id="profile-history-title">Historial por lección</h2>
      <div class="table-wrap" tabindex="0" role="region" aria-labelledby="profile-history-title">
        <table class="history">
          <thead><tr><th scope="col">Lección</th><th scope="col">Teoría</th><th scope="col">Ejercicio</th><th scope="col">Quiz</th><th scope="col">Reto</th></tr></thead>
          <tbody>${historyRows(content)}</tbody>
        </table>
      </div>
    </section>`;
}
