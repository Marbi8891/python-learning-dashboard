/* «Mi cuenta»: área privada. Solo muestra datos de la persona con sesión iniciada.
   La gestión de datos (descargar, cerrar sesión, borrar) vive en el diálogo de cuenta. */

import { examsPassed, pcap, questionsMastered } from "./pcap-store.js";
import { escapeHtml } from "./markdown.js";
import { levelInfo, streak } from "./game.js";
import { state } from "./store.js";

const MEMBER_SINCE = new Intl.DateTimeFormat("es-ES", { month: "long", year: "numeric" });

const initials = (name) =>
  name
    .split(/\s+/)
    .map((word) => word.match(/\p{L}/u)?.[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

/** Sin sesión no hay datos privados que mostrar: solo la invitación a entrar. */
function signedOut(apiEnabled) {
  return `
    <header class="profile-hero">
      <p class="eyebrow">Mi cuenta</p>
      <h1 class="profile-hero__title" id="private-title" tabindex="-1">Tu área privada</h1>
      <p class="profile-hero__note">${
        apiEnabled
          ? "Inicia sesión para ver tu cuenta y sincronizar tu progreso en todos tus dispositivos."
          : "Esta versión funciona sin cuenta: tu progreso se guarda solo en este navegador."
      }</p>
      ${apiEnabled ? `<p><button class="btn btn--primary" type="button" data-open-account>Iniciar sesión o crear cuenta</button></p>` : ""}
    </header>`;
}

/** @param {object} content { order, lessons }  @param {boolean} apiEnabled */
export function renderPrivate(content, apiEnabled) {
  const user = state.user;
  if (!user) return signedOut(apiEnabled);

  const total = content.order.length;
  const done = state.completed.size;
  const next = content.order.find((slug) => !state.completed.has(slug));
  const level = levelInfo();
  const days = streak();
  const since = MEMBER_SINCE.format(new Date(user.created_at));

  return `
    <header class="profile-hero">
      <p class="eyebrow">Mi cuenta</p>
      <div class="account-card">
        <span class="account-card__avatar" aria-hidden="true">${escapeHtml(initials(user.display_name))}</span>
        <div>
          <h1 class="profile-hero__title" id="private-title" tabindex="-1">${escapeHtml(user.display_name)}</h1>
          <p class="account-card__meta">${escapeHtml(user.email)} · miembro desde ${since}</p>
        </div>
      </div>
    </header>

    <section class="course-section" aria-labelledby="private-summary-title">
      <h2 class="section-title" id="private-summary-title">Resumen</h2>
      <dl class="kpis">
        <div class="kpi"><dt>Lecciones</dt><dd>${done}<small>/${total}</small></dd></div>
        <div class="kpi"><dt>Nivel</dt><dd>${level.number}<small> · ${level.xp} XP</small></dd></div>
        <div class="kpi"><dt>Racha actual</dt><dd>${days}<small> ${days === 1 ? "día" : "días"}</small></dd></div>
        <div class="kpi"><dt>Simulacros aprobados</dt><dd>${examsPassed()}<small>/${pcap.exams.length}</small></dd></div>
      </dl>
      <p class="account-card__meta">${questionsMastered()} preguntas del examen dominadas.
        <a href="#/perfil">Ver todo mi aprendizaje</a> · <a href="#/pcap">Ir al examen PCAP</a></p>
      ${
        next
          ? `<p><a class="btn btn--primary" href="#/leccion/${next}">Continuar: ${escapeHtml(content.lessons.get(next).title)}</a></p>`
          : `<p class="empty-state">Has completado todas las lecciones.</p>`
      }
    </section>

    <section class="course-section" aria-labelledby="private-data-title">
      <h2 class="section-title" id="private-data-title">Mis datos y privacidad</h2>
      <p>Tu progreso y tus ejercicios se guardan en tu cuenta, en servidores de la UE. Puedes descargar todos tus datos, cerrar sesión o borrar la cuenta cuando quieras.</p>
      <p>
        <button class="btn btn--ghost" type="button" data-open-account>Gestionar mi cuenta</button>
        <a href="privacidad.html">Política de privacidad</a>
      </p>
    </section>`;
}
