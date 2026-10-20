/* Portada pública (#/portada): presenta el producto, sus funciones reales y lleva a la app.

     #/portada              inicio de la portada
     #/portada/<sección>    la misma página, desplazada a esa sección (enlaces del menú)

   Todo el texto es fijo o sale de data/learning.json y data/lessons.json (contenido del propio
   repositorio): no se pinta nada que venga del usuario ni de la red. La demostración usa un
   concepto y un ejercicio reales del temario; lo que es un ejemplo se dice en la propia página. */

import { apiEnabled } from "./api.js";
import { openAccount } from "./account.js";
import { DAW_COURSES } from "./course-store.js";
import { pythonRunner } from "./console.js";
import { TimeoutError } from "./python-runner.js";
import { escapeHtml, renderInline } from "./markdown.js";
import { codeBlock, highlight } from "./learn/ui.js";
import { loadLearningContent } from "./learn/learn-store.js";
import { INTERVAL_DAYS } from "./learn/mastery.js";
import { state, subscribe } from "./store.js";

export const LANDING_ROUTE = "#/portada";
export const LANDING_TITLE = "Python Learning Dashboard · Aprende programación entendiendo lo que haces";
const REPO_URL = "https://github.com/Marbi8891/python-learning-dashboard";

// Concepto y ejercicio reales de la demostración (data/learning.json)
const DEMO_CONCEPT = "bucles";
const DEMO_EXERCISE = "buc-01";

/** Secciones con ruta propia: #/portada/<id>. El orden es el del menú. */
const NAV = [
  { id: "funcionalidades", label: "Funcionalidades" },
  { id: "como-funciona", label: "Cómo funciona" },
  { id: "temario", label: "Temario" },
  { id: "tecnologia", label: "Tecnología" },
];
const SECTIONS = new Set(["demo", "codefeed", "preguntas", ...NAV.map((n) => n.id)]);

const $ = (selector) => document.querySelector(selector);
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

export const isLandingRoute = (hash) => hash === LANDING_ROUTE || hash.startsWith(`${LANDING_ROUTE}/`);

/* ---------- Iconos (trazo de 1,8 px como los del menú de la app) ---------- */

const PATHS = {
  plan: "M12 3v4M12 17v4M3 12h4M17 12h4M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8",
  book: "M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2zM4 21V5M8 7h7M8 11h7",
  code: "M8 7l-5 5l5 5M16 7l5 5l-5 5M14 4l-4 16",
  play: "M7 4v16l13-8z",
  chart: "M4 20V10M10 20V4M16 20v-7M22 20H2",
  exam: "M4 5h7v14H4zM13 5h7v14h-7",
  chat: "M4 5h16v11H9l-5 4zM8 9h8M8 12h5",
  user: "M12 4a4 4 0 1 0 0 8a4 4 0 1 0 0-8M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7",
  sliders: "M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0M14 4v4M8 10v4M16 16v4",
  timer: "M9 3h6M12 3v3M5 13a7 7 0 1 0 14 0a7 7 0 1 0-14 0M12 13l3-2",
  layers: "M12 3l9 5l-9 5l-9-5zM3 13l9 5l9-5",
  server: "M4 4h16v6H4zM4 14h16v6H4zM8 7h.01M8 17h.01",
  database: "M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3s-3.6 3-8 3s-8-1.3-8-3zM4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
  shield: "M12 3l8 3v6c0 4.5-3.4 8.3-8 9c-4.6-.7-8-4.5-8-9V6z",
  git: "M6 3v12M18 9a3 3 0 1 0 0-6a3 3 0 0 0 0 6zM6 21a3 3 0 1 0 0-6a3 3 0 0 0 0 6zM18 9a9 9 0 0 1-9 9",
  phone: "M7 2h10a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1zM11 18h2",
  video: "M3 6h12v12H3zM15 10l6-3v10l-6-3",
  menu: "M3 6h18M3 12h18M3 18h18",
  close: "M6 6l12 12M18 6L6 18",
  theme: "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18M12 3v18",
  arrow: "M5 12h14M13 6l6 6l-6 6",
  check: "M5 12l5 5l9-10",
};

const icon = (name, size = 20) =>
  `<svg class="lp-icon" viewBox="0 0 24 24" width="${size}" height="${size}" aria-hidden="true" focusable="false"><path d="${PATHS[name]}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

/* ---------- Contenido ---------- */

/** Funciones que ya existen en la app. `tag` avisa de lo que depende de una cuenta o del servidor. */
const FEATURES = [
  {
    icon: "plan",
    title: "Plan de estudio diario",
    href: "#/aprender",
    link: "Ver qué estudio hoy",
    text: "Responde a «¿qué estudio ahora?» con un plan corto ajustado al tiempo que tienes: primero los repasos que tocan, después tus errores recientes y, cuando la base está firme, contenido nuevo.",
    solves: "Evita perder tiempo decidiendo qué hacer o saltar a temas para los que aún te falta base.",
  },
  {
    icon: "book",
    title: "Teoría por conceptos",
    href: "#/teoria",
    link: "Abrir la teoría",
    text: "Cada concepto tiene una explicación corta, un ejemplo comentado línea a línea con su salida real, cuándo usarlo y los errores más habituales.",
    solves: "Entiendes por qué funciona el código, no solo qué escribir.",
  },
  {
    icon: "code",
    title: "Ejercicios con explicación del error",
    href: "#/practicar",
    link: "Ir a practicar",
    text: "Seis tipos de ejercicio: elegir, predecir la salida, completar, ordenar líneas, encontrar el error y escribir programas. Se corrigen al momento y, si fallas, te explican qué falla y cómo evitarlo.",
    solves: "Un fallo se convierte en una explicación concreta en lugar de un simple «incorrecto».",
  },
  {
    icon: "play",
    title: "Python en tu navegador",
    href: "#/leccion/variables",
    link: "Probar la consola",
    text: "Una consola de Python que se ejecuta en tu propio navegador, sin instalar nada. Los ejercicios de escribir programas se comprueban con casos de prueba.",
    solves: "Puedes experimentar con el código en cualquier ordenador, también en uno del centro.",
  },
  {
    icon: "chart",
    title: "Progreso y repaso espaciado",
    href: "#/progreso",
    link: "Ver mi progreso",
    text: `Ves cuánto dominas cada concepto y cuándo toca repasarlo: cada concepto vuelve a los ${INTERVAL_DAYS.slice(1).join(", ").replace(/, (\d+)$/, " y $1")} días.`,
    solves: "Lo que aprendiste hace semanas no se olvida sin que te des cuenta.",
  },
  {
    icon: "exam",
    title: "Preparación de Programación de DAW",
    href: "#/daw",
    link: "Ver la preparación DAW",
    text: "Las competencias del módulo con avisos de qué reforzar antes de avanzar, actividades tipo examen y simulacros cronometrados que se corrigen al final.",
    solves: "Practicas en condiciones parecidas a las del examen y sabes qué te falta.",
  },
  {
    icon: "chat",
    title: "Tutor Python",
    href: "#/tutor",
    link: "Abrir el tutor",
    tag: "Requiere cuenta y que el servidor lo tenga activado",
    text: "Explica conceptos y errores, revisa tu código y da pistas sin resolver el ejercicio por ti. Según la configuración del servidor responde un modelo de IA (por defecto, uno gratuito que se ejecuta con Ollama) o un tutor sin IA basado en el contenido revisado, y cada respuesta indica su origen.",
    solves: "Resuelves dudas concretas sobre tu código sin que te den la solución hecha.",
  },
  {
    icon: "user",
    title: "Cuenta opcional y panel del alumno",
    href: "#/panel",
    link: "Abrir mi panel",
    tag: "Opcional",
    text: "Sin registrarte, el progreso se guarda en este navegador. Con una cuenta (email o Google) se guarda también en el servidor y tienes un panel con tu resumen, tus cursos y la opción de descargar tus datos.",
    solves: "Continúas en otro dispositivo sin perder lo que has hecho.",
  },
  {
    icon: "sliders",
    title: "Adaptado a tu nivel y a tu forma de leer",
    href: "#/bienvenida",
    link: "Ver la presentación guiada",
    text: "Una prueba de nivel coloca tu punto de partida si ya sabes algo. Puedes elegir tema claro u oscuro y tres tamaños de letra.",
    solves: "No repites lo que ya sabes y lees con comodidad.",
  },
];

const STEPS = [
  {
    title: "Elige por dónde empezar",
    text: "Entra en «Aprender» y sigue el primer paso del plan, o haz la prueba de nivel si ya sabes algo de Python.",
    href: "#/aprender",
    link: "Aprender",
  },
  {
    title: "Estudia el concepto",
    text: "Lee la explicación, sigue el ejemplo línea a línea y ejecútalo en tu navegador para ver su salida.",
    href: "#/teoria",
    link: "Teoría",
  },
  {
    title: "Practica y resuelve dudas",
    text: "Haz los ejercicios: se corrigen al momento y cada error trae su explicación y un nuevo intento. Si tienes cuenta y el tutor está activo, pregúntale.",
    href: "#/practicar",
    link: "Practicar",
  },
  {
    title: "Revisa tu progreso y sigue",
    text: "Mira qué dominas y qué toca repasar. El plan de mañana ya tiene en cuenta lo que hiciste hoy.",
    href: "#/progreso",
    link: "Progreso",
  },
];

const TECH = [
  {
    icon: "layers",
    title: "Web: HTML, CSS y JavaScript",
    text: "Módulos de JavaScript sin framework ni paso de compilación. Se publica en GitHub Pages y, tras la primera visita, funciona sin conexión gracias a un service worker.",
  },
  {
    icon: "play",
    title: "Pyodide",
    text: "Python compilado a WebAssembly. Ejecuta tu código en un Web Worker de tu navegador, con límite de tiempo para que un bucle infinito no bloquee la página.",
  },
  {
    icon: "server",
    title: "Python y FastAPI",
    text: "La API de cuentas, progreso, panel y tutor. Contraseñas con Argon2, sesión en una cookie HttpOnly y límites de peticiones. Está preparada para desplegarse en Render.",
  },
  {
    icon: "database",
    title: "PostgreSQL",
    text: "Guarda las cuentas y el progreso sincronizado, con migraciones de Alembic. En local y en las pruebas se usa SQLite.",
  },
  {
    icon: "chat",
    title: "Tutor con A2A",
    text: "El tutor es un agente del protocolo A2A dentro del mismo backend. Por defecto usa un modelo local y gratuito con Ollama, o un modo sin IA; no hay ningún servicio de pago activado.",
  },
  {
    icon: "shield",
    title: "Git, GitHub y pruebas",
    text: "Cada cambio pasa por GitHub Actions: pruebas del backend con pytest, pruebas de extremo a extremo con Playwright, auditoría de accesibilidad con axe-core y análisis de seguridad.",
  },
];

const CODEFEED = [
  "Vídeos breves de programación con el código explicado en pantalla.",
  "Subtítulos y transcripción en todos los vídeos.",
  "Una pregunta rápida al final para comprobar lo que has entendido.",
  "Organizados por lenguaje y dificultad.",
  "Conectados con tu progreso: el plan podría proponerte un vídeo del concepto que te cuesta.",
];

/* ---------- Plantilla ---------- */

function headerHtml() {
  const links = NAV.map((n) => `<li><a href="${LANDING_ROUTE}/${n.id}" data-lp-section="${n.id}">${n.label}</a></li>`).join("");
  return `
    <header class="lp-header">
      <div class="lp-header__inner lp-wrap">
        <a class="lp-brand" href="${LANDING_ROUTE}" aria-label="Python Learning Dashboard: inicio de la portada">
          <span class="brand__logo" aria-hidden="true">Py</span>
          <span class="lp-brand__name">Python Learning <span>Dashboard</span></span>
        </a>
        <button class="lp-menu-toggle" id="lp-menu-toggle" type="button" aria-expanded="false" aria-controls="lp-nav">
          ${icon("menu", 22)}<span>Menú</span>
        </button>
        <nav class="lp-nav" id="lp-nav" aria-label="Portada">
          <ul class="lp-nav__links">${links}</ul>
          <div class="lp-nav__actions">
            <button class="lp-icon-button" type="button" data-lp-appearance aria-label="Aspecto: tema y tamaño de letra">${icon("theme")}</button>
            <button class="lp-btn lp-btn--ghost" type="button" data-lp-login hidden>Iniciar sesión</button>
            <a class="lp-btn lp-btn--ghost" href="#/panel" data-lp-panel hidden>Mi panel</a>
            <a class="lp-btn lp-btn--primary" href="#/aprender">Empezar a aprender</a>
          </div>
        </nav>
      </div>
    </header>`;
}

/** Ventana de producto del hero: piezas reales de la app con datos de ejemplo. */
function heroVisual(concept) {
  const code = concept?.example?.code ?? 'for i in range(1, 4):\n    print("vuelta", i)';
  const output = concept?.example?.output?.trim() ?? "vuelta 1\nvuelta 2\nvuelta 3";
  const trap = concept?.errors?.find((e) => e.id === "bucles.range-fin");
  return `
    <figure class="lp-window" aria-labelledby="lp-window-caption">
      <div class="lp-window__bar" aria-hidden="true"><span></span><span></span><span></span><p>Teoría · ${escapeHtml(concept?.title ?? "Bucles")}</p></div>
      <div class="lp-window__body">
        <pre class="lp-code" aria-label="Ejemplo de código del concepto"><code>${highlight(code)}</code></pre>
        <div class="lp-out"><span class="lp-out__label">Salida</span><pre>${escapeHtml(output)}</pre></div>
        ${
          trap
            ? `<div class="lp-window__note"><p class="lp-chip">Error habitual</p><p>${renderInline(trap.label)}</p></div>`
            : ""
        }
        <div class="lp-window__progress">
          <div class="lp-window__progress-head"><span>Bucles</span><span>En progreso · 60 %</span></div>
          <span class="lp-meter" aria-hidden="true"><span style="--value: 60%"></span></span>
          <p>Próximo repaso: dentro de 3 días</p>
        </div>
      </div>
      <figcaption class="lp-window__caption" id="lp-window-caption">Vista de demostración: el código y el error son del temario real; el progreso es un ejemplo.</figcaption>
    </figure>`;
}

function heroHtml(concept) {
  return `
    <section class="lp-hero" aria-labelledby="lp-title">
      <div class="lp-wrap lp-hero__grid">
        <div class="lp-hero__text">
          <p class="lp-eyebrow">Python, Programación de DAW y PCAP</p>
          <h1 class="lp-hero__title" id="lp-title" tabindex="-1">Aprende programación <em>entendiendo</em> lo que haces</h1>
          <p class="lp-hero__lead">Practica con ejercicios que se corrigen al momento, resuelve dudas con el tutor y sigue tu progreso en una plataforma diseñada para aprender programación paso a paso.</p>
          <div class="lp-actions">
            <a class="lp-btn lp-btn--primary lp-btn--lg" href="#/aprender">Empezar a aprender ${icon("arrow", 18)}</a>
            <a class="lp-btn lp-btn--ghost lp-btn--lg" href="${LANDING_ROUTE}/como-funciona" data-lp-section="como-funciona">Descubrir cómo funciona</a>
          </div>
          <ul class="lp-facts" aria-label="Condiciones de uso">
            <li>${icon("check", 16)} Gratuito y sin publicidad</li>
            <li>${icon("check", 16)} Sin registro para empezar</li>
            <li>${icon("check", 16)} Código abierto (MIT)</li>
          </ul>
        </div>
        ${heroVisual(concept)}
      </div>
    </section>`;
}

/** Opciones del ejercicio: la respuesta correcta y las trampas del propio ejercicio, en orden fijo. */
const demoOptions = (exercise) => {
  const traps = Object.keys(exercise.traps);
  return [traps[0], exercise.expect, ...traps.slice(1)];
};

/** Demostración con un concepto y un ejercicio reales del temario. */
function demoHtml(index) {
  const concept = index?.concepts.get(DEMO_CONCEPT);
  const exercise = index?.exercises.get(DEMO_EXERCISE);
  if (!concept || !exercise) {
    return `
      <section class="lp-section" id="lp-demo" aria-labelledby="lp-demo-title">
        <div class="lp-wrap">
          <h2 class="lp-section__title" id="lp-demo-title" tabindex="-1">Así se estudia un concepto</h2>
          <p class="lp-muted">No se ha podido cargar el ejemplo. Puedes verlo directamente en <a href="#/teoria">la teoría</a>.</p>
        </div>
      </section>`;
  }
  const notes = (concept.example.lines ?? [])
    .map(([line, text]) => `<li><span class="lp-line">Línea ${line}</span> ${renderInline(text)}</li>`)
    .join("");
  const radios = demoOptions(exercise)
    .map((value, i) => `<label class="lp-option"><input type="radio" name="lp-answer" value="${i}"> <code>${escapeHtml(value)}</code></label>`)
    .join("");
  const range = concept.errors.find((e) => e.id === "bucles.range-fin");
  return `
    <section class="lp-section" id="lp-demo" aria-labelledby="lp-demo-title">
      <div class="lp-wrap">
        <header class="lp-section__head">
          <p class="lp-eyebrow">Demostración</p>
          <h2 class="lp-section__title" id="lp-demo-title" tabindex="-1">Así se estudia un concepto</h2>
          <p class="lp-section__lead">El concepto, el ejemplo y el ejercicio son los del temario real. Puedes ejecutar el código y responder: aquí no se guarda nada en tu progreso.</p>
        </header>
        <ol class="lp-demo" data-lp-demo>
          <li class="lp-demo__step">
            <p class="lp-demo__n">1 · Concepto</p>
            <h3>${escapeHtml(concept.title)}</h3>
            <p>${renderInline(concept.summary)}</p>
            <p class="lp-muted"><strong>Cuándo usarlo:</strong> ${renderInline(concept.when)}</p>
          </li>
          <li class="lp-demo__step lp-demo__step--wide">
            <p class="lp-demo__n">2 · Ejemplo comentado</p>
            <div class="lp-demo__split">
              <div>
                ${codeBlock(concept.example.code, { label: "Ejemplo del concepto", numbered: true })}
                <button class="lp-btn lp-btn--ghost" type="button" data-lp-run>${icon("play", 16)} Ejecutar en tu navegador</button>
                <pre class="lp-run-output" data-lp-output role="status" tabindex="0" hidden></pre>
              </div>
              <ul class="lp-notes" aria-label="Explicación línea a línea">${notes}</ul>
            </div>
          </li>
          <li class="lp-demo__step">
            <p class="lp-demo__n">3 · Una duda y su explicación</p>
            <div class="lp-chat">
              <p class="lp-chat__msg lp-chat__msg--user"><span class="visually-hidden">Alumno:</span>¿Por qué <code>range(1, 5)</code> no llega al 5?</p>
              <div class="lp-chat__msg lp-chat__msg--tutor"><span class="visually-hidden">Explicación:</span>
                <p>${renderInline(range?.why ?? "")}</p>
                <p><strong>Para pensarlo:</strong> ${renderInline(range?.think ?? "")}</p>
              </div>
            </div>
            <p class="lp-note">Ejemplo ilustrativo, no es una conversación real: el texto es la explicación de este error en el temario. En el tutor real cada respuesta indica si la ha escrito un modelo de IA o el modo sin IA.</p>
          </li>
          <li class="lp-demo__step">
            <p class="lp-demo__n">4 · Ejercicio</p>
            <form class="lp-quiz" data-lp-quiz>
              <fieldset>
                <legend>${escapeHtml(exercise.q)}</legend>
                ${codeBlock(exercise.code, { label: "Código del ejercicio" })}
                <div class="lp-options">${radios}</div>
              </fieldset>
              <button class="lp-btn lp-btn--primary" type="submit">Comprobar</button>
              <div class="lp-feedback" data-lp-feedback role="status" aria-live="polite"></div>
            </form>
          </li>
          <li class="lp-demo__step">
            <p class="lp-demo__n">5 · Progreso</p>
            <h3>Dominio y repaso</h3>
            <dl class="lp-mastery">
              <div><dt>Bucles</dt><dd><span class="lp-meter" aria-hidden="true"><span style="--value: 60%"></span></span> En progreso · 60 %</dd></div>
              <div><dt>Condicionales</dt><dd><span class="lp-meter" aria-hidden="true"><span style="--value: 100%"></span></span> Dominado · 100 %</dd></div>
              <div><dt>Funciones</dt><dd><span class="lp-meter" aria-hidden="true"><span style="--value: 0%"></span></span> Sin empezar · 0 %</dd></div>
            </dl>
            <ol class="lp-days" aria-label="Días de repaso de un concepto">${INTERVAL_DAYS.map((d) => `<li>${d === 0 ? "Hoy" : d === 1 ? "1 día" : `${d} días`}</li>`).join("")}</ol>
            <p class="lp-note">Datos de ejemplo. Tu progreso real aparece en <a href="#/progreso">Progreso</a>.</p>
          </li>
        </ol>
      </div>
    </section>`;
}

function featuresHtml() {
  const cards = FEATURES.map(
    (f) => `
      <li class="lp-feature">
        <span class="lp-feature__icon">${icon(f.icon, 22)}</span>
        <h3>${f.title}</h3>
        ${f.tag ? `<p class="lp-chip">${f.tag}</p>` : ""}
        <p>${f.text}</p>
        <p class="lp-feature__solves"><strong>Para qué te sirve:</strong> ${f.solves}</p>
        <a class="lp-link" href="${f.href}">${f.link} ${icon("arrow", 16)}</a>
      </li>`,
  ).join("");
  return `
    <section class="lp-section lp-section--alt" id="lp-funcionalidades" aria-labelledby="lp-funcionalidades-title">
      <div class="lp-wrap">
        <header class="lp-section__head">
          <p class="lp-eyebrow">Funcionalidades</p>
          <h2 class="lp-section__title" id="lp-funcionalidades-title" tabindex="-1">Lo que ya puedes usar</h2>
          <p class="lp-section__lead">Todo lo que aparece aquí está disponible en la versión actual. Cuando algo depende de una cuenta o de la configuración del servidor, se indica.</p>
        </header>
        <ul class="lp-features">${cards}</ul>
      </div>
    </section>`;
}

function stepsHtml() {
  const items = STEPS.map(
    (s, i) => `
      <li class="lp-step">
        <span class="lp-step__n" aria-hidden="true">${i + 1}</span>
        <h3><span class="visually-hidden">Paso ${i + 1}: </span>${s.title}</h3>
        <p>${s.text}</p>
        <a class="lp-link" href="${s.href}">${s.link} ${icon("arrow", 16)}</a>
      </li>`,
  ).join("");
  return `
    <section class="lp-section" id="lp-como-funciona" aria-labelledby="lp-como-funciona-title">
      <div class="lp-wrap">
        <header class="lp-section__head">
          <p class="lp-eyebrow">Cómo funciona</p>
          <h2 class="lp-section__title" id="lp-como-funciona-title" tabindex="-1">Un recorrido en cuatro pasos</h2>
          <p class="lp-section__lead">Así es un día normal de estudio. Si prefieres verlo dentro de la app, tienes <a href="#/bienvenida">la presentación guiada</a>.</p>
        </header>
        <ol class="lp-steps">${items}</ol>
      </div>
    </section>`;
}

function catalogHtml(index, content) {
  const areas = (index?.areas ?? [])
    .map((area) => {
      const titles = (index.data.concepts ?? []).filter((c) => c.area === area.id).map((c) => `<li><a href="#/teoria/${escapeHtml(c.id)}">${escapeHtml(c.title)}</a></li>`);
      return `
        <div class="lp-area">
          <h3>${escapeHtml(area.title)} <span class="lp-count">${titles.length} conceptos</span></h3>
          <p class="lp-muted">${escapeHtml(area.summary)}</p>
          <ul>${titles.join("")}</ul>
        </div>`;
    })
    .join("");
  const concepts = index?.concepts.size;
  const exercises = index?.exercises.size;
  const lessons = content?.order?.length;
  const courses = DAW_COURSES.map((c) => `<li><a href="#/daw/${escapeHtml(c.id)}">${escapeHtml(c.title)}</a> <span class="lp-muted">${escapeHtml(c.subtitle)}</span></li>`).join("");
  return `
    <section class="lp-section lp-section--alt" id="lp-temario" aria-labelledby="lp-temario-title">
      <div class="lp-wrap">
        <header class="lp-section__head">
          <p class="lp-eyebrow">Temario</p>
          <h2 class="lp-section__title" id="lp-temario-title" tabindex="-1">Qué puedes estudiar</h2>
          <p class="lp-section__lead">${concepts && exercises ? `${concepts} conceptos de programación en Python con ${exercises} ejercicios, ` : "Conceptos de programación en Python con sus ejercicios, "}ordenados de las variables a los ficheros y la programación orientada a objetos.</p>
        </header>
        <div class="lp-areas">${areas}</div>
        <div class="lp-courses">
          <div>
            <h3>Cursos de DAW</h3>
            <p class="lp-muted">Lecciones y bancos de preguntas de otros módulos del ciclo.</p>
            <ul>${courses}</ul>
          </div>
          <div>
            <h3>Certificación PCAP</h3>
            <p class="lp-muted">${lessons ? `Curso de ${lessons} lecciones` : "Curso por lecciones"} con teoría, consola y quiz, y simulacros del examen. El certificado que genera la web no es oficial.</p>
            <ul>
              <li><a href="#/inicio">Curso PCAP</a></li>
              <li><a href="#/pcap">Examen PCAP</a></li>
            </ul>
          </div>
        </div>
      </div>
    </section>`;
}

function codefeedHtml() {
  return `
    <section class="lp-section" id="lp-codefeed" aria-labelledby="lp-codefeed-title">
      <div class="lp-wrap lp-codefeed">
        <div>
          <p class="lp-eyebrow">En desarrollo</p>
          <h2 class="lp-section__title" id="lp-codefeed-title" tabindex="-1">CodeFeed: microlecciones en vídeo</h2>
          <p class="lp-chip lp-chip--plan">${icon("timer", 16)} Propuesta: todavía no está disponible</p>
          <p class="lp-section__lead">Una sección para aprender con vídeos cortos de programación. Aún no hay ningún vídeo publicado ni una fecha comprometida.</p>
          <p class="lp-muted">Solo se publicarán vídeos originales o con una licencia verificada que permita usarlos.</p>
        </div>
        <div class="lp-codefeed__plan">
          <h3>Qué incluye la propuesta</h3>
          <ul class="lp-list">${CODEFEED.map((item) => `<li>${icon("video", 18)} ${item}</li>`).join("")}</ul>
        </div>
      </div>
    </section>`;
}

function techHtml() {
  const items = TECH.map(
    (t) => `
      <li class="lp-tech">
        <span class="lp-feature__icon">${icon(t.icon, 22)}</span>
        <h3>${t.title}</h3>
        <p>${t.text}</p>
      </li>`,
  ).join("");
  return `
    <section class="lp-section lp-section--alt" id="lp-tecnologia" aria-labelledby="lp-tecnologia-title">
      <div class="lp-wrap">
        <header class="lp-section__head">
          <p class="lp-eyebrow">Tecnología</p>
          <h2 class="lp-section__title" id="lp-tecnologia-title" tabindex="-1">Cómo está construido</h2>
          <p class="lp-section__lead">Un proyecto de código abierto hecho con herramientas gratuitas. Esto es lo que hace cada pieza.</p>
        </header>
        <ul class="lp-techs">${items}</ul>
        <p class="lp-actions"><a class="lp-btn lp-btn--ghost" href="${REPO_URL}">${icon("git", 18)} Ver el código en GitHub</a></p>
      </div>
    </section>`;
}

function faqHtml(index) {
  const concepts = index?.concepts.size;
  const faqs = [
    [
      "¿Qué es Python Learning Dashboard?",
      "Una web gratuita para aprender a programar en Python por conceptos, con teoría, ejercicios corregidos, repaso espaciado y preparación del módulo de Programación de DAW y del examen PCAP. Es un proyecto educativo personal, no una academia ni un servicio comercial.",
    ],
    [
      "¿Necesito saber programar para empezar?",
      `No. La ruta empieza por cómo plantear un problema y por las variables${concepts ? `, y avanza por ${concepts} conceptos` : ""}. Si ya sabes algo, la prueba de nivel coloca tu punto de partida.`,
    ],
    [
      "¿Cómo funciona el tutor de IA?",
      "Necesitas una cuenta y que el servidor tenga el tutor activado. Según su configuración responde un modelo de IA que se ejecuta con Ollama o un tutor sin IA basado en el contenido revisado del curso, y cada respuesta dice cuál ha sido. No ejecuta tu código en el servidor y la conversación no se guarda en tu cuenta. Una respuesta de IA puede equivocarse: compruébala en la consola.",
    ],
    [
      "¿Puedo seguir mi progreso?",
      "Sí. Sin cuenta, el progreso se guarda en tu navegador. Con cuenta, se guarda también en el servidor, se sincroniza entre dispositivos y tienes un panel con tu resumen.",
    ],
    [
      "¿Qué lenguajes de programación están disponibles?",
      "Python es el lenguaje principal: teoría, ejercicios y consola. Los cursos de DAW incluyen además SQL, JavaScript y Java, con preguntas y ejercicios; ese código no se ejecuta en la web.",
    ],
    [
      "¿Puedo utilizar la plataforma desde el móvil?",
      "Sí, la web se adapta a móviles y tabletas y se puede instalar como aplicación. El repositorio incluye también una app Android que se instala desde GitHub (no está en Google Play).",
    ],
    [
      "¿Cómo se gestionan mis datos?",
      'Sin cuenta, tu progreso se guarda solo en tu navegador. Con cuenta se guardan además tu nombre, tu email y tu progreso en el servidor; la contraseña se guarda como un hash Argon2, que no permite leerla, y la sesión va en una cookie que JavaScript no puede leer. Puedes descargar tus datos desde tu panel. El detalle, incluido cómo borrar tu cuenta, está en la <a href="privacidad.html">política de privacidad</a>.',
    ],
    ["¿El proyecto es gratuito?", "Sí. No tiene publicidad, suscripciones ni pagos."],
    [
      "¿Puedo consultar el código fuente?",
      `Sí. Está en <a href="${REPO_URL}">GitHub</a> con licencia MIT.`,
    ],
  ];
  const items = faqs
    .map(([q, a]) => `<details class="lp-faq__item"><summary>${q}</summary><p>${a}</p></details>`)
    .join("");
  return `
    <section class="lp-section" id="lp-preguntas" aria-labelledby="lp-preguntas-title">
      <div class="lp-wrap lp-faq">
        <header class="lp-section__head">
          <p class="lp-eyebrow">Preguntas frecuentes</p>
          <h2 class="lp-section__title" id="lp-preguntas-title" tabindex="-1">Lo que suele preguntarse</h2>
        </header>
        <div>${items}</div>
      </div>
    </section>`;
}

function ctaHtml() {
  return `
    <section class="lp-cta" aria-labelledby="lp-cta-title">
      <div class="lp-wrap lp-cta__inner">
        <h2 class="lp-cta__title" id="lp-cta-title">Empieza por un concepto. Avanza practicando.</h2>
        <p>Elige tu siguiente tema, prueba los ejemplos y construye tu aprendizaje paso a paso.</p>
        <a class="lp-btn lp-btn--primary lp-btn--lg" href="#/aprender">Entrar en Python Learning Dashboard ${icon("arrow", 18)}</a>
      </div>
    </section>`;
}

function footerHtml() {
  const email = window.PLD_CONFIG?.contactEmail;
  return `
    <footer class="lp-footer">
      <div class="lp-wrap lp-footer__grid">
        <div>
          <p class="lp-brand"><span class="brand__logo" aria-hidden="true">Py</span><span class="lp-brand__name">Python Learning <span>Dashboard</span></span></p>
          <p class="lp-muted">Proyecto educativo y gratuito. No está afiliado a Python Institute.</p>
        </div>
        <nav aria-label="Enlaces del pie">
          <h2 class="lp-footer__title">Aplicación</h2>
          <ul>
            <li><a href="#/aprender">Entrar en la aplicación</a></li>
            <li><a href="#/teoria">Teoría</a></li>
            <li><a href="#/daw">Preparación DAW</a></li>
          </ul>
        </nav>
        <nav aria-label="Proyecto">
          <h2 class="lp-footer__title">Proyecto</h2>
          <ul>
            <li><a href="${REPO_URL}">Repositorio en GitHub</a></li>
            <li><a href="${REPO_URL}/tree/main/docs">Documentación</a></li>
            <li><a href="${REPO_URL}/blob/main/LICENSE">Licencia MIT</a></li>
          </ul>
        </nav>
        <nav aria-label="Información legal">
          <h2 class="lp-footer__title">Legal y contacto</h2>
          <ul>
            <li><a href="privacidad.html">Política de privacidad</a></li>
            <li><a href="aviso-legal.html">Aviso legal</a></li>
            ${email ? `<li><a href="mailto:${escapeHtml(email)}">Contacto</a></li>` : ""}
          </ul>
        </nav>
      </div>
    </footer>`;
}

function pageHtml(index, content) {
  const concept = index?.concepts.get(DEMO_CONCEPT);
  return `
    ${headerHtml()}
    <main class="lp-main" id="landing-main" tabindex="-1">
      ${heroHtml(concept)}
      ${demoHtml(index)}
      ${featuresHtml()}
      ${stepsHtml()}
      ${catalogHtml(index, content)}
      ${codefeedHtml()}
      ${techHtml()}
      ${faqHtml(index)}
      ${ctaHtml()}
    </main>
    ${footerHtml()}`;
}

/* ---------- Comportamiento ---------- */

let rendered = false;
let exerciseData = null; // { exercise, concept, options }

function setMenu(open) {
  const toggle = $("#lp-menu-toggle");
  if (!toggle) return;
  toggle.setAttribute("aria-expanded", String(open));
  $("#landing-view").classList.toggle("lp-menu-open", open);
}

function updateAccount() {
  const login = $("[data-lp-login]");
  if (!login) return;
  login.hidden = !apiEnabled || Boolean(state.user);
  $("[data-lp-panel]").hidden = !state.user;
}

function checkAnswer(form) {
  const feedback = form.querySelector("[data-lp-feedback]");
  const choice = form.elements["lp-answer"].value;
  if (choice === "") {
    feedback.innerHTML = "<p>Elige una respuesta.</p>";
    return;
  }
  const { exercise, concept, options } = exerciseData;
  const answer = options[Number(choice)];
  if (answer === exercise.expect) {
    feedback.dataset.result = "ok";
    feedback.innerHTML = `<p class="lp-feedback__title">${icon("check", 18)} Correcto</p><p>${renderInline(exercise.explain)}</p>`;
    return;
  }
  // Igual que en la app: cada respuesta trampa apunta a un error concreto del concepto
  const error = concept.errors.find((e) => e.id === exercise.traps[answer]);
  feedback.dataset.result = "error";
  feedback.innerHTML = `
    <p class="lp-feedback__title">${icon("close", 18)} No es correcto: ${renderInline(error?.label ?? "revisa el código")}</p>
    ${error ? `<p><strong>Por qué:</strong> ${renderInline(error.why)}</p><p><strong>Cómo evitarlo:</strong> ${renderInline(error.avoid)}</p>` : ""}
    <p>Vuelve a intentarlo.</p>`;
}

async function runDemo(button) {
  const output = button.parentElement.querySelector("[data-lp-output]");
  output.hidden = false;
  button.disabled = true;
  output.textContent = "Cargando Python en tu navegador (solo la primera vez, unos segundos)…";
  try {
    const result = await pythonRunner.run(exerciseData.concept.example.code, "");
    const text = [result.output, result.error].filter(Boolean).join("\n");
    output.textContent = `Salida real (Python en tu navegador):\n${text || "(El programa no ha mostrado nada)"}`;
  } catch (error) {
    output.textContent =
      error instanceof TimeoutError ? error.message : `No se pudo ejecutar: ${error.message}. Revisa tu conexión y vuelve a intentarlo.`;
  } finally {
    button.disabled = false;
  }
}

function bind(view) {
  view.addEventListener("click", (event) => {
    const target = event.target.closest("a, button");
    if (!target) return;
    if (target.id === "lp-menu-toggle") {
      setMenu(target.getAttribute("aria-expanded") !== "true");
      return;
    }
    if (target.matches("[data-lp-login]")) openAccount();
    else if (target.matches("[data-lp-appearance]")) $("#appearance-button").click();
    else if (target.matches("[data-lp-run]")) runDemo(target);
    else if (target.matches("[data-lp-section]") && location.hash === target.getAttribute("href")) {
      // El mismo enlace dos veces no cambia el hash: se desplaza igualmente
      event.preventDefault();
      scrollToSection(target.dataset.lpSection, { moveFocus: true });
    }
    if (target.closest("#lp-nav")) setMenu(false);
  });
  view.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && $("#lp-menu-toggle")?.getAttribute("aria-expanded") === "true") {
      setMenu(false);
      $("#lp-menu-toggle").focus();
    }
  });
  view.addEventListener("submit", (event) => {
    if (!event.target.matches("[data-lp-quiz]")) return;
    event.preventDefault();
    checkAnswer(event.target);
  });
  subscribe(updateAccount);
}

function scrollToSection(section, { moveFocus }) {
  const behavior = reducedMotion.matches ? "auto" : "smooth";
  if (!SECTIONS.has(section)) {
    window.scrollTo({ top: 0, behavior: "auto" });
    if (moveFocus) $("#lp-title")?.focus({ preventScroll: true });
    return;
  }
  const target = $(`#lp-${section}`);
  target?.scrollIntoView({ behavior, block: "start" });
  if (moveFocus) target?.querySelector(".lp-section__title")?.focus({ preventScroll: true });
}

/** Muestra la portada (la pinta la primera vez) y se desplaza a la sección de la ruta. */
export async function openLanding(hash, { content, moveFocus = true } = {}) {
  const view = $("#landing-view");
  if (!rendered) {
    const index = await loadLearningContent().catch(() => null);
    if (!isLandingRoute(location.hash)) return; // el usuario ya se ha ido a otra parte
    view.innerHTML = pageHtml(index, content);
    const exercise = index?.exercises.get(DEMO_EXERCISE);
    if (exercise) {
      exerciseData = { exercise, concept: index.concepts.get(DEMO_CONCEPT), options: demoOptions(exercise) };
    }
    bind(view);
    rendered = true;
  }
  updateAccount();
  setMenu(false);
  view.hidden = false;
  document.body.dataset.page = "landing";
  document.title = LANDING_TITLE;
  scrollToSection(hash.slice(LANDING_ROUTE.length + 1), { moveFocus });
}

export function closeLanding() {
  const view = $("#landing-view");
  if (view.hidden) return;
  view.hidden = true;
  delete document.body.dataset.page;
}
