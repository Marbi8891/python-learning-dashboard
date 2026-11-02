/* «Página no encontrada» (NAV-01). La usan el enrutador general y las zonas con subrutas (DAW, PCAP)
   para que un enlace mal escrito o antiguo diga que no existe en vez de llevar a otra página. */

import { escapeHtml } from "./markdown.js";

/** Enlaces de vuelta comunes a todas las zonas. */
const INDEX_LINKS = [
  { href: "#/aprender", label: "¿Qué estudio ahora?" },
  { href: "#/portada", label: "Ir a la portada" },
];

/**
 * @param {object} options
 * @param {string} options.titleId id del <h1> (cada zona tiene el suyo para mover el foco)
 * @param {string} options.route la ruta pedida (se muestra escapada)
 * @param {string} [options.what] qué no existe: «esta página», «esta lección», «este curso»…
 * @param {{href: string, label: string}} [options.back] enlace principal para volver a la zona
 */
export function notFoundHtml({ titleId, route, what = "esta página", back = null }) {
  const links = (back ? [back, ...INDEX_LINKS] : INDEX_LINKS)
    .map((link, i) => `<a class="btn ${i === 0 ? "btn--primary" : "btn--ghost"}" href="${escapeHtml(link.href)}">${escapeHtml(link.label)}</a>`)
    .join("");
  return `
    <header class="course-hero not-found" data-not-found>
      <p class="eyebrow">Error 404</p>
      <h1 class="course-hero__title" id="${escapeHtml(titleId)}" tabindex="-1">No encontramos ${escapeHtml(what)}</h1>
      <p class="course-hero__lead">La dirección <code>${escapeHtml(route)}</code> no existe o ha cambiado de nombre.
        Tu progreso sigue guardado: puedes volver desde aquí.</p>
      <div class="course-hero__cta">${links}</div>
    </header>`;
}
