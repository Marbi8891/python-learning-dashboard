/* Bienvenida (#/bienvenida): presentación de la web como un mapa con paradas.

   El alumno avanza parada a parada (Aprender → Teoría → Practicar → Repasar → DAW) con
   «Anterior» / «Siguiente» o pulsando una parada. Al final puede empezar, hacer la prueba
   de nivel o ver el recorrido por el menú real (tour.js). */

import { markWelcomeSeen } from "./learn-store.js";
import { startTour } from "../tour.js";
import { codeBlock, escapeHtml } from "./ui.js";

const STOPS = [
  {
    label: "Aprender",
    title: "Tu punto de partida cada día",
    href: "#/aprender",
    go: "Ver qué estudio hoy",
    text: "Al entrar, la web te dice qué estudiar ahora y en qué orden: primero los repasos que tocan hoy, después tus errores recientes, luego lo importante para DAW y, cuando la base está firme, contenido nuevo.",
    example: () => `
      <ol class="lx-map__mock" aria-label="Ejemplo de plan de hoy">
        <li><span class="lx-map__tag">Repasar</span> Bucles</li>
        <li><span class="lx-map__tag">Corregir</span> El orden de la asignación</li>
        <li><span class="lx-map__tag">Nuevo</span> Funciones</li>
      </ol>`,
  },
  {
    label: "Teoría",
    title: "Entiende antes de practicar",
    href: "#/teoria",
    go: "Ver la teoría",
    text: "22 conceptos de programación, de las variables a los ficheros. Cada uno con una explicación corta, un ejemplo comentado línea a línea con su salida real, cuándo usarlo y los errores habituales.",
    example: () => `
      ${codeBlock('edad = 17\nif edad >= 18:\n    print("Adulto")\nelse:\n    print("Menor")', { label: "Ejemplo de la teoría" })}
      <p class="lx-map__out"><span>Salida:</span> <code>Menor</code></p>`,
  },
  {
    label: "Practicar",
    title: "Inténtalo y aprende del error",
    href: "#/practicar",
    go: "Ir a practicar",
    text: "Seis tipos de ejercicio: elegir, predecir la salida, completar, ordenar, encontrar el error y escribir programas. Se corrige al momento; si fallas, te explica qué falla, por qué y cómo evitarlo, y lo vuelves a intentar con uno parecido.",
    example: () => `
      ${codeBlock('print("Total: " + 5)', { label: "Ejercicio con un error" })}
      <p class="lx-map__fix"><strong>Qué falla:</strong> no se puede sumar texto y un número. <strong>Cómo evitarlo:</strong> conviértelo antes con <code>str(5)</code>.</p>`,
  },
  {
    label: "Repasar",
    title: "Que no se te olvide",
    href: "#/progreso",
    go: "Ver mi progreso",
    text: "Cada concepto vuelve cuando toca: al día siguiente y a los 3, 7, 14 y 30 días. En Progreso ves cuánto dominas cada concepto y cuándo es su próximo repaso.",
    example: () => `
      <ol class="lx-map__days" aria-label="Días de repaso">
        ${["Hoy", "1 día", "3 días", "7 días", "14 días", "30 días"].map((d) => `<li>${d}</li>`).join("")}
      </ol>`,
  },
  {
    label: "DAW",
    title: "La meta: el examen de Programación",
    href: "#/daw",
    go: "Ver la preparación DAW",
    text: "Las competencias del módulo con avisos como «Necesitas reforzar Bucles antes de pasar a Funciones», actividades tipo examen y simulacros cronometrados que se corrigen al final, como en el examen.",
    example: () => `
      <p class="lx-map__note">Necesitas reforzar <strong>Bucles</strong> antes de pasar a <strong>Funciones</strong>.</p>`,
  },
];

let stop = 0;

function stopsHtml() {
  return STOPS.map((s, i) => {
    const state = i < stop ? "done" : i === stop ? "current" : "next";
    return `
      <li class="lx-map__stop" data-state="${state}">
        <button class="lx-map__dot" type="button" data-learn="map-stop" data-stop="${i}" aria-controls="lx-map-panel"${i === stop ? ' aria-current="step"' : ""}>
          <span class="lx-map__n" aria-hidden="true">${i + 1}</span>
          <span class="lx-map__label"><span class="visually-hidden">Parada ${i + 1}: </span>${s.label}</span>
        </button>
      </li>`;
  }).join("");
}

function panelHtml() {
  const s = STOPS[stop];
  const last = stop === STOPS.length - 1;
  const next = last
    ? `<a class="btn btn--primary" href="#/aprender">Empezar desde cero</a>
       <button class="btn btn--ghost" type="button" data-learn="diagnostic">Prueba de nivel</button>`
    : `<button class="btn btn--primary" type="button" data-learn="map-next">Siguiente: ${STOPS[stop + 1].label}</button>`;
  return `
    <p class="lx-map__step">Parada ${stop + 1} de ${STOPS.length} · ${s.label}</p>
    <h3 class="lx-map__title" id="lx-map-stop-title" tabindex="-1">${s.title}</h3>
    <p class="lx-map__text">${s.text}</p>
    <div class="lx-map__example">${s.example()}</div>
    <div class="lx-actions lx-map__nav">
      ${stop > 0 ? '<button class="btn btn--ghost" type="button" data-learn="map-prev">Anterior</button>' : ""}
      ${next}
      <a class="lx-map__go" href="${s.href}">${escapeHtml(s.go)}</a>
    </div>
    ${last ? '<p class="lx-muted lx-map__end">¿Quieres ver dónde está cada cosa? <button class="lx-link" type="button" data-learn="tour">Haz el recorrido por el menú</button>.</p>' : ""}`;
}

export function renderWelcome() {
  markWelcomeSeen();
  stop = 0;
  return `
    <section class="lx-welcome" aria-labelledby="learn-title">
      <p class="eyebrow">Bienvenido/a</p>
      <h1 class="lx-welcome__title" id="learn-title" tabindex="-1">Aprende Python entendiendo lo que haces</h1>
      <p class="lx-welcome__lead">Y prepara la parte de programación de <strong>DAW</strong> con teoría clara, ejercicios corregidos al momento y la explicación de cada error.</p>
      <div class="lx-actions lx-welcome__cta">
        <a class="btn btn--primary btn--lg" href="#/aprender">Empezar desde cero</a>
        <button class="btn btn--ghost btn--lg" type="button" data-learn="diagnostic">Ya sé algo: prueba de nivel</button>
      </div>
      <p class="lx-muted">Gratis y sin registrarte: tu progreso se guarda en este navegador. Con una cuenta opcional, también en el móvil.</p>
    </section>
    <section class="lx-section lx-map" aria-labelledby="lx-map-title">
      <div class="lx-map__head">
        <h2 class="lx-section__title" id="lx-map-title">El mapa: un recorrido en 5 paradas</h2>
        <button class="btn btn--ghost" type="button" data-learn="tour">Recorrido por el menú</button>
      </div>
      <ol class="lx-map__route" id="lx-map-route">${stopsHtml()}</ol>
      <div class="lx-map__panel" id="lx-map-panel" role="region" aria-labelledby="lx-map-stop-title">${panelHtml()}</div>
    </section>
    <p class="lx-muted">¿Preparas la certificación PCAP? Tienes también <a href="#/inicio">el curso completo de certificación</a>.</p>`;
}

/** Repinta solo el mapa (no la página) y lleva el foco al título de la parada. */
function goTo(next, { focus = "title" } = {}) {
  stop = Math.max(0, Math.min(STOPS.length - 1, next));
  document.querySelector("#lx-map-route").innerHTML = stopsHtml();
  document.querySelector("#lx-map-panel").innerHTML = panelHtml();
  if (focus === "dot") document.querySelector(`[data-stop="${stop}"]`)?.focus();
  else document.querySelector("#lx-map-stop-title")?.focus();
}

/** Clics del mapa. Devuelve true si los ha gestionado. */
export function onWelcomeClick(target) {
  switch (target.dataset.learn) {
    case "map-stop":
      goTo(Number(target.dataset.stop), { focus: "dot" });
      return true;
    case "map-next":
      goTo(stop + 1);
      return true;
    case "map-prev":
      goTo(stop - 1);
      return true;
    case "tour":
      startTour(target);
      return true;
    default:
      return false;
  }
}

/** Flechas izquierda/derecha entre paradas cuando el foco está en una. */
export function onWelcomeKeydown(event) {
  const dot = event.target.closest?.(".lx-map__dot");
  if (!dot || (event.key !== "ArrowRight" && event.key !== "ArrowLeft")) return;
  event.preventDefault();
  goTo(stop + (event.key === "ArrowRight" ? 1 : -1), { focus: "dot" });
}
