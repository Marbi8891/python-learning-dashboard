/* Preferencias de aspecto: tema (auto/claro/oscuro), tamaño de letra y lectura
   (texto espaciado, contraste alto y sin animaciones).
   index.html las aplica antes de pintar la página; aquí se gestionan los cambios. */

const KEY = "pld:prefs";
const DEFAULTS = { theme: "auto", font: "normal", spacing: false, contrast: false, motion: false };
const systemReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const systemLight = window.matchMedia("(prefers-color-scheme: light)");
const $ = (selector) => document.querySelector(selector);

function load() {
  try {
    return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY)) };
  } catch {
    return { ...DEFAULTS };
  }
}

const prefs = load();

function apply() {
  const theme = prefs.theme === "auto" ? (systemLight.matches ? "light" : "dark") : prefs.theme;
  document.documentElement.dataset.theme = theme;
  const root = document.documentElement;
  root.dataset.font = prefs.font;
  toggleData(root, "spacing", prefs.spacing, "amplio");
  toggleData(root, "contrast", prefs.contrast, "alto");
  toggleData(root, "motion", prefs.motion, "reducido");
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "light" ? "#f6f4ef" : "#121417");
}

function toggleData(element, name, on, value) {
  if (on) element.dataset[name] = value;
  else delete element.dataset[name];
}

/** Sin animaciones si lo pide el sistema o si el alumno lo ha elegido en «Aspecto». */
export function prefersReducedMotion() {
  return document.documentElement.dataset.motion === "reducido" || systemReducedMotion.matches;
}

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(prefs));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
}

/** Preferencias actuales (para mostrarlas en el panel del alumno). */
export const currentPrefs = () => ({ ...prefs });

export function initPrefs() {
  apply();
  systemLight.addEventListener("change", () => {
    if (prefs.theme === "auto") apply();
  });

  const form = $("#appearance-form");
  $("#appearance-button").addEventListener("click", () => {
    form.elements.theme.value = prefs.theme;
    form.elements.font.value = prefs.font;
    for (const name of ["spacing", "contrast", "motion"]) form.elements[name].checked = prefs[name];
    $("#appearance-dialog").showModal();
  });
  $("#appearance-close").addEventListener("click", () => $("#appearance-dialog").close());
  form.addEventListener("change", () => {
    prefs.theme = form.elements.theme.value;
    prefs.font = form.elements.font.value;
    for (const name of ["spacing", "contrast", "motion"]) prefs[name] = form.elements[name].checked;
    save();
    apply();
  });
}
