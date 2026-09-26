/* Preferencias de aspecto: tema (auto/claro/oscuro) y tamaño de letra.
   index.html las aplica antes de pintar la página; aquí se gestionan los cambios. */

const KEY = "pld:prefs";
const systemLight = window.matchMedia("(prefers-color-scheme: light)");
const $ = (selector) => document.querySelector(selector);

function load() {
  try {
    return { theme: "auto", font: "normal", ...JSON.parse(localStorage.getItem(KEY)) };
  } catch {
    return { theme: "auto", font: "normal" };
  }
}

const prefs = load();

function apply() {
  const theme = prefs.theme === "auto" ? (systemLight.matches ? "light" : "dark") : prefs.theme;
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.font = prefs.font;
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "light" ? "#f7f4ec" : "#0c0d10");
}

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(prefs));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
}

export function initPrefs() {
  apply();
  systemLight.addEventListener("change", () => {
    if (prefs.theme === "auto") apply();
  });

  const form = $("#appearance-form");
  $("#appearance-button").addEventListener("click", () => {
    form.elements.theme.value = prefs.theme;
    form.elements.font.value = prefs.font;
    $("#appearance-dialog").showModal();
  });
  $("#appearance-close").addEventListener("click", () => $("#appearance-dialog").close());
  form.addEventListener("change", () => {
    prefs.theme = form.elements.theme.value;
    prefs.font = form.elements.font.value;
    save();
    apply();
  });
}
