/* Pantalla de inicio: bienvenida, «Continuar donde lo dejaste», resumen y módulos. */

import { BADGES, game, levelInfo, streak } from "./game.js";
import { escapeHtml } from "./markdown.js";
import { state } from "./store.js";

const HOW = [
  ["Aprende", "Lee la teoría y prueba el ejemplo en la consola, que está siempre a mano."],
  ["Practica", "Escribe tu solución al ejercicio y pulsa «Comprobar»: los tests te dicen si está bien."],
  ["Comprueba", "Responde el mini-quiz. Cada respuesta te explica el porqué."],
];

/**
 * @param {object} content  { modules, order, lessons }
 * @param {string} nextSlug lección por la que continuar
 */
export function renderHome(content, nextSlug) {
  const total = content.order.length;
  const done = state.completed.size;
  const next = content.lessons.get(nextSlug);
  const level = levelInfo();
  const days = streak();
  const name = state.user ? `, ${escapeHtml(state.user.display_name)}` : "";
  const firstVisit = done === 0 && game.read.length === 0;

  const cta = firstVisit
    ? `<a class="btn btn--primary btn--lg" href="#/leccion/${next.slug}">Empezar la primera lección →</a>
       <span class="home__cta-note">Unos 15 minutos por lección. No necesitas instalar nada.</span>`
    : done === total
      ? `<a class="btn btn--primary btn--lg" href="#/leccion/${content.order[0]}">Repasar desde el principio</a>
         <span class="home__cta-note">¡Has completado el curso! Prueba los retos ★★★ que te falten.</span>`
      : `<a class="btn btn--primary btn--lg" href="#/leccion/${next.slug}">Continuar: ${escapeHtml(next.title)} →</a>
         <span class="home__cta-note">${escapeHtml(next.module.title)}</span>`;

  const modules = content.modules
    .map((module) => {
      const count = module.lessons.length;
      const finished = module.lessons.filter((l) => state.completed.has(l.slug)).length;
      const target = module.lessons.find((l) => !state.completed.has(l.slug)) ?? module.lessons[0];
      const percent = Math.round((finished / count) * 100);
      return `
        <li>
          <a class="module-card" href="#/leccion/${target.slug}">
            <h3>${escapeHtml(module.title)}</h3>
            <span class="module-card__meta">${finished} de ${count} lecciones</span>
            <span class="module-card__bar" style="--done: ${percent}%" role="img" aria-label="${percent} % completado"></span>
            <span class="module-card__go">${finished === count ? "Repasar" : finished ? "Seguir" : "Empezar"} →</span>
          </a>
        </li>`;
    })
    .join("");

  return `
    <div class="home__hero">
      <h1 id="home-title" tabindex="-1">¡Hola${name}! Aprende Python paso a paso</h1>
      <p>Lecciones cortas con ejemplos que puedes ejecutar aquí mismo, ejercicios que se corrigen solos y un asistente que te da pistas cuando te atascas.</p>
      <div class="home__cta">${cta}</div>
    </div>

    <section aria-labelledby="home-stats-title">
      <h2 class="home__section-title" id="home-stats-title">Tu progreso</h2>
      <div class="home__stats">
        <div class="stat"><span class="stat__value">${done}/${total}</span><span class="stat__label">lecciones completadas</span></div>
        <div class="stat"><span class="stat__value">Nivel ${level.number}</span><span class="stat__label">${escapeHtml(level.name)} · ${level.xp} XP</span></div>
        <div class="stat"><span class="stat__value">${days} ${days === 1 ? "día" : "días"}</span><span class="stat__label">de racha</span></div>
        <div class="stat"><span class="stat__value">${game.badges.length}/${BADGES.length}</span><span class="stat__label">logros</span></div>
      </div>
    </section>

    <section aria-labelledby="home-how-title">
      <h2 class="home__section-title" id="home-how-title">Cómo funciona cada lección</h2>
      <ol class="home__how">
        ${HOW.map(
          ([title, text], i) => `
          <li class="how"><span class="how__num" aria-hidden="true">${i + 1}</span><h3>${title}</h3><p>${text}</p></li>`,
        ).join("")}
      </ol>
    </section>

    <section aria-labelledby="home-modules-title">
      <h2 class="home__section-title" id="home-modules-title">Módulos</h2>
      <ul class="home__modules">${modules}</ul>
    </section>`;
}
