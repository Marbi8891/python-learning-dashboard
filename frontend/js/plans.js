/* Vista comercial Free / Pro / Academy. No activa pagos ni bloquea contenido. */
import { apiEnabled, request } from "./api.js";
import { openAccount } from "./account.js";
import { escapeHtml } from "./markdown.js";
import { state, subscribe as subscribeStore } from "./store.js";

let entitlements = [];
let entitlementStatus = "idle";
let entitlementError = "";

const dateLabel = (value) => {
  if (!value) return "Sin fecha de caducidad";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Fecha no disponible" : `Hasta ${new Intl.DateTimeFormat("es-ES", { dateStyle: "medium" }).format(date)}`;
};

function currentAccess() {
  if (!state.user) return { label: "Free", detail: "Estás usando PLD sin iniciar sesión. Tu progreso local sigue disponible en este navegador." };
  if (entitlementStatus === "loading") return { label: "Consultando cuenta…", detail: "Estamos comprobando los derechos asociados a tu cuenta." };
  if (entitlementStatus === "error") return { label: "No se pudo comprobar", detail: "No podemos confirmar tus derechos ahora. Tu acceso actual al contenido no cambia." };
  if (entitlements.length) return { label: "Acceso ampliado", detail: "Tu cuenta tiene derechos de acceso activos. Consulta el detalle más abajo." };
  return { label: "Free", detail: "Tu cuenta está en el plan gratuito. No hay derechos Pro activos registrados." };
}

function entitlementList() {
  if (!state.user) return "";
  if (entitlementStatus === "loading") return '<p class="plans__muted" role="status">Cargando derechos de acceso…</p>';
  if (entitlementStatus === "error") return `<p class="plans__notice" role="alert">${escapeHtml(entitlementError)} <button class="btn btn--ghost" type="button" data-plans-retry>Reintentar</button></p>`;
  if (!entitlements.length) return '<p class="plans__muted">No hay derechos adicionales activos en esta cuenta.</p>';
  return `<ul class="plans__entitlements">${entitlements.map((item) => `
    <li><span><strong>${escapeHtml(item.feature_key)}</strong><small>Inicio: ${escapeHtml(new Intl.DateTimeFormat("es-ES", { dateStyle: "medium" }).format(new Date(item.starts_at)))}</small></span><span>${escapeHtml(dateLabel(item.ends_at))}</span></li>`).join("")}</ul>`;
}

export function renderPlans() {
  const access = currentAccess();
  return `
    <header class="plans__hero">
      <p class="eyebrow">PLD · Cuenta y suscripción</p>
      <h1 class="profile-hero__title" id="plans-title" tabindex="-1">Planes de Python Learning Dashboard</h1>
      <p class="plans__intro">Empieza gratis y decide más adelante si necesitas herramientas de seguimiento y rutas avanzadas.</p>
      <div class="plans__current">
        <div><span class="plans__eyebrow">Tu acceso actual</span><strong>${escapeHtml(access.label)}</strong><p>${escapeHtml(access.detail)}</p></div>
        ${state.user ? '<span class="plans__account-state">Sesión iniciada</span>' : '<button class="btn btn--primary" type="button" data-plans-login>Iniciar sesión</button>'}
      </div>
    </header>

    <section class="plans__grid" aria-label="Comparación de planes">
      <article class="plans__card">
        <p class="plans__eyebrow">Para empezar</p><h2>Free</h2><p class="plans__price">0 € <small>/ siempre</small></p>
        <p>Aprende y practica con una ruta inicial gratuita.</p>
        <ul><li>Ruta introductoria</li><li>Ejercicios y consola pública</li><li>Cuenta y sincronización básica</li><li>Progreso esencial</li></ul>
        <a class="btn btn--ghost" href="#/aprender">Seguir aprendiendo</a>
      </article>
      <article class="plans__card plans__card--pro">
        <p class="plans__eyebrow">Para avanzar</p><h2>Pro</h2><p class="plans__price">7,99 € <small>/ mes · hipótesis</small></p>
        <p>La propuesta para quienes necesitan más práctica y seguimiento.</p>
        <ul><li>Itinerarios y contenidos avanzados</li><li>Seguimiento personal ampliado</li><li>Historial y análisis de aprendizaje</li><li>Planificación adaptativa avanzada</li></ul>
        <span class="plans__coming">Próximamente · sin contratación activa</span>
        <p class="plans__fine">Precio orientativo pendiente de validación. También se ha estudiado una opción anual de 59,99 €, todavía no aprobada.</p>
      </article>
      <article class="plans__card plans__card--academy">
        <p class="plans__eyebrow">Para centros</p><h2>Academy</h2><p class="plans__price">En preparación</p>
        <p>Herramientas para docentes y academias.</p>
        <ul><li>Grupos y alumnos</li><li>Asignación de actividades</li><li>Seguimiento por grupo</li><li>Panel docente</li></ul>
        <span class="plans__coming">Pendiente de desarrollo y validación</span>
      </article>
    </section>

    <section class="course-section plans__account" aria-labelledby="plans-rights-title">
      <div class="section-head"><h2 class="section-title" id="plans-rights-title">Derechos de tu cuenta</h2><span class="plans__muted">${state.user ? escapeHtml(state.user.email) : "Inicia sesión para consultar tus derechos"}</span></div>
      ${entitlementList()}
    </section>
    <p class="plans__footnote">Esta pantalla informa de los planes previstos. Todavía no hay pagos, renovación automática ni bloqueos comerciales. El contenido que ya es público seguirá accesible.</p>`;
}

export function initPlans() {
  document.querySelector("#plans-view")?.addEventListener("click", (event) => {
    if (event.target.closest("[data-plans-login]")) openAccount("login");
    if (event.target.closest("[data-plans-retry]")) openPlans({ force: true });
  });
}

export async function openPlans({ force = false } = {}) {
  if (!state.user) {
    entitlements = [];
    entitlementStatus = "idle";
    entitlementError = "";
    return;
  }
  if (!apiEnabled) return;
  if (entitlementStatus === "loading" || (entitlementStatus === "loaded" && !force)) return;
  entitlementStatus = "loading";
  entitlementError = "";
  const view = document.querySelector("#plans-view");
  if (view) view.innerHTML = renderPlans();
  try {
    const result = await request("GET", "/api/v1/users/me/entitlements");
    entitlements = Array.isArray(result) ? result : [];
    entitlementStatus = "loaded";
  } catch (error) {
    entitlementError = error.message || "No se pudieron consultar los derechos.";
    entitlementStatus = "error";
  }
  if (location.hash === "#/planes" && view) view.innerHTML = renderPlans();
}
