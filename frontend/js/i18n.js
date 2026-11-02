/* Idioma de la interfaz, sin frameworks.

   - El español es el idioma original: está escrito en el HTML y en el JavaScript, sin claves.
   - Para otro idioma se descarga i18n/<idioma>.json (solo entonces) y se traduce el DOM:
     cada texto o atributo cuyo contenido completo coincida con una entrada del diccionario se
     sustituye. Un MutationObserver traduce también lo que pintan las vistas después.
   - Entradas con huecos: «Racha: {n} días» → «Streak: {n} days» (los huecos van por nombre).
   - Nunca se traduce el código (pre, code, textarea, kbd, samp) ni lo marcado con translate="no".
   - El código lleva translate="no" en cualquier idioma: así el traductor del navegador puede
     traducir las lecciones a cualquier idioma sin estropear los programas. */


const PREFS_KEY = "pld:prefs";
const SUGGEST_KEY = "pld:lang-suggested";

export const LANGUAGES = { es: "Español", en: "English" };
const LOCALES = { es: "es-ES", en: "en-GB" };
const SKIP = new Set(["SCRIPT", "STYLE", "PRE", "CODE", "TEXTAREA", "KBD", "SAMP", "svg"]);
const ATTRIBUTES = ["aria-label", "title", "placeholder", "alt"];
const CODE_SELECTOR = "pre, code, kbd, samp, textarea";
const CONTENT_SELECTOR = ".prose"; // texto de las lecciones: sigue en español

function readPrefs() {
  try {
    return JSON.parse(localStorage.getItem(PREFS_KEY)) ?? {};
  } catch {
    return {};
  }
}

/** Idioma elegido en «Aspecto» (el español si no se eligió ninguno). */
export function chosenLanguage(prefs = readPrefs()) {
  return Object.hasOwn(LANGUAGES, prefs.lang) ? prefs.lang : "es";
}

export const language = chosenLanguage();
/** Locale para Intl y toLocaleDateString: las fechas siguen al idioma de la interfaz. */
export const locale = LOCALES[language];

/* ---------- Diccionario ---------- */

const exact = new Map();
const patterns = [];

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Carga un diccionario { "texto en español": "translation" }. Devuelve cuántas entradas tiene. */
export function loadDictionary(entries) {
  exact.clear();
  patterns.length = 0;
  for (const [source, target] of Object.entries(entries)) {
    if (source.startsWith("//")) continue; // comentarios del JSON
    if (!/\{\w+\}/.test(source)) {
      exact.set(source, target);
      continue;
    }
    const names = [];
    const body = source
      .split(/(\{\w+\})/)
      .map((part) => {
        const hole = part.match(/^\{(\w+)\}$/);
        if (!hole) return escapeRegExp(part);
        names.push(hole[1]);
        return "(.+?)";
      })
      .join("");
    patterns.push({ regex: new RegExp(`^${body}$`, "s"), names, target });
  }
  return exact.size + patterns.length;
}

/** Traduce un texto completo; null si no hay traducción. Respeta los espacios de alrededor. */
export function translate(text) {
  const key = text.trim().replace(/\s+/g, " ");
  if (!key) return null;
  let result = exact.get(key);
  if (result === undefined) {
    for (const { regex, names, target } of patterns) {
      const match = key.match(regex);
      if (!match) continue;
      result = target.replace(/\{(\w+)\}/g, (hole, name) => {
        const index = names.indexOf(name);
        // El hueco también se traduce si es un texto conocido (p. ej. el nombre de un nivel)
        return index === -1 ? hole : (exact.get(match[index + 1]) ?? match[index + 1]);
      });
      break;
    }
  }
  if (result === undefined || result === key) return null;
  const lead = text.match(/^\s*/)[0];
  const trail = text.match(/\s*$/)[0];
  return lead + result + trail;
}

/** Para textos que no pasan por el DOM (por ejemplo, document.title). */
export function t(text) {
  return translate(text) ?? text;
}

/* ---------- Traducción del DOM ---------- */

function skipped(element) {
  return !element || SKIP.has(element.nodeName) || element.closest?.('[translate="no"], [data-i18n-skip]');
}

function translateTextNode(node) {
  if (skipped(node.parentElement)) return;
  const result = translate(node.nodeValue);
  if (result !== null) node.nodeValue = result;
}

function translateAttributes(element) {
  if (element.closest('[translate="no"], [data-i18n-skip]')) return;
  for (const name of ATTRIBUTES) {
    const value = element.getAttribute(name);
    if (value === null) continue;
    const result = translate(value);
    if (result !== null) element.setAttribute(name, result);
  }
  if (element.nodeName === "INPUT" && ["button", "submit"].includes(element.type) && element.value) {
    const result = translate(element.value);
    if (result !== null) element.value = result;
  }
}

/** Marca el código para que ningún traductor (el nuestro o el del navegador) lo cambie y, con la
    interfaz en otro idioma, marca las lecciones (aún en español) con lang="es" (WCAG 3.1.2). */
function protectCode(root) {
  if (root.nodeType !== 1) return;
  const mark = (selector, name, value) => {
    if (root.matches(selector)) root.setAttribute(name, value);
    for (const element of root.querySelectorAll(selector)) element.setAttribute(name, value);
  };
  mark(CODE_SELECTOR, "translate", "no");
  if (language !== "es") mark(CONTENT_SELECTOR, "lang", "es");
}

export function translateTree(root, { translateTexts = true } = {}) {
  if (root.nodeType === 3) {
    if (translateTexts) translateTextNode(root);
    return;
  }
  if (root.nodeType !== 1 && root.nodeType !== 9) return;
  protectCode(root.nodeType === 9 ? root.documentElement : root);
  if (!translateTexts) return;
  const element = root.nodeType === 9 ? root.documentElement : root;
  if (skipped(element) && element !== document.documentElement) return;
  translateAttributes(element);
  for (const child of element.querySelectorAll("*")) translateAttributes(child);
  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) translateTextNode(node);
}

function observe(translateTexts) {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "childList") {
        for (const node of mutation.addedNodes) translateTree(node, { translateTexts });
      } else if (!translateTexts) {
        continue;
      } else if (mutation.type === "characterData") {
        translateTextNode(mutation.target);
      } else if (mutation.type === "attributes" && ATTRIBUTES.includes(mutation.attributeName)) {
        translateAttributes(mutation.target);
      }
    }
  });
  const options = { subtree: true, childList: true };
  // En español solo se vigila qué se añade (para proteger el código); en otro idioma, todo
  if (translateTexts) Object.assign(options, { characterData: true, attributes: true, attributeFilter: ATTRIBUTES });
  observer.observe(document.documentElement, options);
}

/* ---------- Sugerencia de idioma ---------- */

/** ¿El navegador habla español? Si no, se ofrece la interfaz en inglés una vez. */
export function prefersSpanish(languages = navigator.languages ?? [navigator.language]) {
  return languages.some((code) => String(code).toLowerCase().startsWith("es"));
}

export function setLanguage(lang) {
  const prefs = readPrefs();
  prefs.lang = lang;
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
  } catch {
    // sin almacenamiento: no se puede recordar
  }
  location.reload();
}

function suggestEnglish() {
  try {
    if (readPrefs().lang || localStorage.getItem(SUGGEST_KEY) || prefersSpanish()) return;
  } catch {
    return;
  }
  const banner = document.createElement("aside");
  banner.className = "lang-banner";
  banner.setAttribute("aria-label", "Language");
  banner.lang = "en";
  banner.innerHTML = `
    <p>This site is in Spanish. You can switch the interface to English; lessons can be translated with your browser's translate option.</p>
    <div class="lang-banner__actions">
      <button class="btn btn--primary" type="button" data-lang="en">Use English</button>
      <button class="btn btn--ghost" type="button" data-lang="es" lang="es">Seguir en español</button>
    </div>`;
  banner.addEventListener("click", (event) => {
    const button = event.target.closest("[data-lang]");
    if (!button) return;
    try {
      localStorage.setItem(SUGGEST_KEY, "1");
    } catch {
      // sin almacenamiento
    }
    if (button.dataset.lang === "en") setLanguage("en");
    else banner.remove();
  });
  document.querySelector(".skip-link")?.after(banner);
}

/* ---------- Arranque ---------- */

let started = null;

/** Prepara la interfaz en el idioma elegido. En español solo protege el código. */
export function initI18n() {
  started ??= (async () => {
    const root = document.documentElement;
    root.lang = language;
    try {
      if (language !== "es") {
        const response = await fetch(`i18n/${language}.json`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        loadDictionary(await response.json());
        document.getElementById("lang-note")?.removeAttribute("hidden");
        translateTree(document);
        document.title = t(document.title);
      } else {
        translateTree(document, { translateTexts: false });
      }
      observe(language !== "es");
    } catch {
      // Sin diccionario la web sigue en español: mejor eso que una página a medias
      root.lang = "es";
      translateTree(document, { translateTexts: false });
      observe(false);
    } finally {
      delete root.dataset.i18nPending;
    }
    suggestEnglish();
  })();
  return started;
}
