/* Recorrido guiado por el menú real: resalta cada opción y explica para qué sirve.

   Accesible: el globo es un diálogo no modal que recibe el foco; Escape o «Saltar» lo cierran
   y el foco vuelve al botón que lo abrió. En el móvil abre el menú lateral durante el recorrido.
   Si el alumno pulsa una opción resaltada, el recorrido termina y la navegación sigue normal. */

const STEPS = [
  ['[data-nav="aprender"]', "Aprender", "Empieza aquí cada día: te dice qué estudiar ahora, con tus repasos y errores primero."],
  ['[data-nav="teoria"]', "Teoría", "Todos los conceptos explicados, con un ejemplo línea a línea y los errores habituales."],
  ['[data-nav="practicar"]', "Practicar", "Ejercicios por concepto o por tipo, y tus errores pendientes para corregirlos."],
  ['[data-nav="daw"]', "DAW", "La preparación del examen de Programación: competencias, actividades tipo examen y simulacros."],
  ['[data-nav="progreso"]', "Progreso", "Cuánto dominas cada concepto y cuándo te toca repasarlo."],
  ["#account-button", "Tu cuenta (opcional)", "Inicia sesión para guardar el progreso en tu cuenta y seguir en el móvil."],
  ["#appearance-button", "Aspecto", "Cambia entre modo claro y oscuro."],
  ['.sidebar__footer a[href="#/bienvenida"]', "Presentación", "Si quieres volver a ver el mapa de la web, está aquí."],
];

const GAP = 12;
const visible = (el) => el && !el.closest("[hidden]") && el.getClientRects().length > 0;

let tour = null;

function isMobileMenu() {
  return window.matchMedia("(max-width: 900px)").matches;
}

function setMobileMenu(open) {
  if (document.body.classList.contains("nav-open") !== open) document.querySelector("#menu-toggle")?.click();
}

function render() {
  const { steps, i, pop } = tour;
  const [, title, text] = steps[i];
  const last = i === steps.length - 1;
  pop.innerHTML = `
    <p class="tour-pop__step">Paso ${i + 1} de ${steps.length}</p>
    <h2 class="tour-pop__title" id="tour-title" tabindex="-1">${title}</h2>
    <p class="tour-pop__text" id="tour-text">${text}</p>
    <div class="tour-pop__actions">
      ${i > 0 ? '<button class="btn btn--ghost" type="button" data-tour="prev">Anterior</button>' : ""}
      <button class="btn btn--primary" type="button" data-tour="${last ? "end" : "next"}">${last ? "Terminar" : "Siguiente"}</button>
      ${last ? "" : '<button class="tour-pop__skip" type="button" data-tour="end">Saltar recorrido</button>'}
    </div>`;
  place();
  pop.querySelector("#tour-title").focus({ preventScroll: true });
}

/** Coloca el resalte sobre la opción y el globo al lado (o arriba/abajo en el móvil). */
function place() {
  const { steps, i, ring, pop } = tour;
  const target = document.querySelector(steps[i][0]);
  target.scrollIntoView({ block: "nearest" });
  const r = target.getBoundingClientRect();
  Object.assign(ring.style, { top: `${r.top - 4}px`, left: `${r.left - 4}px`, width: `${r.width + 8}px`, height: `${r.height + 8}px` });

  const w = pop.offsetWidth;
  const h = pop.offsetHeight;
  const vw = document.documentElement.clientWidth;
  const vh = window.innerHeight;
  let top;
  let left;
  if (r.right + GAP + w <= vw - GAP) {
    left = r.right + GAP; // a la derecha de la opción (escritorio)
    top = Math.min(Math.max(r.top + r.height / 2 - h / 2, GAP), vh - h - GAP);
  } else {
    left = Math.max(GAP, (vw - w) / 2); // móvil: arriba o abajo, sin tapar la opción
    top = r.top + r.height / 2 < vh / 2 ? vh - h - GAP : GAP;
  }
  Object.assign(pop.style, { top: `${top}px`, left: `${left}px` });
}

function go(i) {
  tour.i = i;
  render();
}

function onClick(event) {
  const action = event.target.closest("[data-tour]")?.dataset.tour;
  if (action === "next") go(tour.i + 1);
  else if (action === "prev") go(tour.i - 1);
  else if (action === "end") endTour();
}

function onKeydown(event) {
  if (event.key !== "Escape") return;
  event.stopPropagation(); // que el menú móvil no gestione también este Escape
  endTour();
}

const onHashChange = () => endTour({ restoreFocus: false });
const onMove = () => tour && place();

const MENU_SLIDE_MS = 250; // la transición del menú móvil dura 200 ms (sidebar.css)
const onBackdrop = () => endTour();

export function startTour(trigger) {
  if (tour) return;
  const openedMenu = isMobileMenu() && !document.body.classList.contains("nav-open");
  if (openedMenu) setMobileMenu(true);
  const steps = STEPS.filter(([selector]) => visible(document.querySelector(selector)));
  if (!steps.length) return;

  const ring = document.createElement("div");
  ring.className = "tour-ring";
  ring.setAttribute("aria-hidden", "true");
  const pop = document.createElement("div");
  pop.className = "tour-pop";
  pop.setAttribute("role", "dialog");
  pop.setAttribute("aria-labelledby", "tour-title");
  pop.setAttribute("aria-describedby", "tour-text");
  document.body.append(ring, pop);

  tour = { steps, i: 0, ring, pop, trigger, openedMenu };
  pop.addEventListener("click", onClick);
  window.addEventListener("keydown", onKeydown, true);
  window.addEventListener("hashchange", onHashChange);
  window.addEventListener("resize", onMove);
  window.addEventListener("scroll", onMove, true);
  document.querySelector("#sidebar-backdrop")?.addEventListener("click", onBackdrop);
  document.body.classList.add("tour-on");
  // Con el menú móvil recién abierto se espera a que termine de entrar para medir bien
  if (openedMenu) setTimeout(() => tour && render(), MENU_SLIDE_MS);
  else render();
}

export function endTour({ restoreFocus = true } = {}) {
  if (!tour) return;
  const { ring, pop, trigger, openedMenu } = tour;
  tour = null;
  ring.remove();
  pop.remove();
  window.removeEventListener("keydown", onKeydown, true);
  window.removeEventListener("hashchange", onHashChange);
  window.removeEventListener("resize", onMove);
  window.removeEventListener("scroll", onMove, true);
  document.querySelector("#sidebar-backdrop")?.removeEventListener("click", onBackdrop);
  document.body.classList.remove("tour-on");
  if (openedMenu) setMobileMenu(false);
  if (restoreFocus) (trigger?.isConnected ? trigger : document.querySelector("#learn-title"))?.focus();
}
