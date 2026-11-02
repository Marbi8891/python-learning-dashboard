// Idiomas (F3): diccionario por texto original, huecos, y que la interfaz fija esté completa.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { chosenLanguage, loadDictionary, prefersSpanish, t, translate } from "../../frontend/js/i18n.js";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");
const english = JSON.parse(read("../../frontend/i18n/en.json"));

test("traduce textos completos y conserva los espacios de alrededor", () => {
  loadDictionary({ Ejecutar: "Run", "Código Python": "Python code" });
  assert.equal(translate("Ejecutar"), "Run");
  assert.equal(translate("\n   Ejecutar  "), "\n   Run  ");
  assert.equal(translate("Código\n      Python"), "Python code");
  assert.equal(translate("Ejecutar ahora"), null, "solo textos completos: no se trocean frases");
  assert.equal(t("sin traducción"), "sin traducción");
});

test("los huecos se rellenan y también se traducen si son textos conocidos", () => {
  loadDictionary({
    "Racha: {n} días": "Streak: {n} days",
    "Nivel {n} · {name}": "Level {n} · {name}",
    "{xp} XP para «{name}»": "{xp} XP to “{name}”",
    "Novato/a": "Newbie",
    "// comentario": "se ignora",
  });
  assert.equal(translate("Racha: 12 días"), "Streak: 12 days");
  assert.equal(translate("Nivel 1 · Novato/a"), "Level 1 · Newbie");
  assert.equal(translate("Nivel 4 · Pythonista"), "Level 4 · Pythonista");
  assert.equal(translate("40 XP para «Novato/a»"), "40 XP to “Newbie”");
  assert.equal(translate("// comentario"), null);
});

test("el idioma elegido solo puede ser uno de los disponibles", () => {
  assert.equal(chosenLanguage({}), "es");
  assert.equal(chosenLanguage({ lang: "en" }), "en");
  assert.equal(chosenLanguage({ lang: "xx" }), "es");
});

test("se ofrece el inglés solo a navegadores que no están en español", () => {
  assert.equal(prefersSpanish(["es-ES", "en"]), true);
  assert.equal(prefersSpanish(["en-US", "es-MX"]), true);
  assert.equal(prefersSpanish(["ar", "fr-FR"]), false);
});

/** Textos visibles y atributos de accesibilidad de index.html, como los ve i18n.js. */
function interfaceStrings(html) {
  const body = html.slice(html.indexOf("<body"));
  const cleaned = body
    .replace(/<(script|style|pre|code|textarea|kbd|samp|svg)\b[\s\S]*?<\/\1>/g, "<i></i>")
    .replace(/<[^>]+translate="no"[^>]*>[\s\S]*?<\/[a-z]+>/g, "<i></i>");
  const strings = new Set();
  for (const [, , value] of cleaned.matchAll(/\b(aria-label|title|placeholder|alt)="([^"]+)"/g)) strings.add(value);
  for (const [, text] of cleaned.matchAll(/>([^<>]+)</g)) {
    const value = text.replace(/\s+/g, " ").trim();
    if (/[A-Za-zÁ-ú]/.test(value)) strings.add(value);
  }
  return strings;
}

test("toda la interfaz fija de index.html tiene traducción al inglés", () => {
  // Nombres propios y textos que se reescriben al cargar
  const same = new Set(["Python Learning", "Py", "Dashboard", "DAW", "0 XP", "main.py"]);
  loadDictionary(english);
  const missing = [...interfaceStrings(read("../../frontend/index.html"))].filter(
    (text) => !same.has(text) && !Object.hasOwn(english, text) && translate(text) === null,
  );
  assert.deepEqual(missing, []);
});

test("el diccionario no tiene traducciones vacías salvo las intencionadas", () => {
  const empty = Object.entries(english).filter(([key, value]) => !key.startsWith("//") && value === "");
  assert.deepEqual(empty.map(([key]) => key), ["· Language"]);
});
