// Módulo de POO: índice #/poo, página de unidad con sus apartados, ejemplos ejecutables con
// Pyodide, lecciones completadas, mini-quiz con el motor de sesiones y accesibilidad (WCAG 2.2 AA).
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect } = require("./fixtures");

async function audit(page) {
  await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"), null, { timeout: 20_000 });
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
}

const SECTIONS = [
  "Objetivos de aprendizaje",
  "Conocimientos previos",
  "Lecciones",
  "Conceptos importantes",
  "Ejemplo comentado",
  "Ejercicios guiados",
  "Ejercicio principal",
  "Prácticas adicionales",
  "Errores frecuentes",
  "Buenas prácticas",
  "Autoevaluación",
  "Cuestionario de la unidad",
  "Resumen",
  "Criterios de superación",
  "Relación con el currículo de DAW",
  "Referencias bibliográficas",
];

test("índice del módulo: 10 unidades, las publicadas enlazadas y el progreso explicado", async ({ page }) => {
  await page.goto("/#/poo");
  await expect(page.locator("#learn-title")).toHaveText("Programación orientada a objetos con Python");
  await expect(page).toHaveTitle(/^Módulo de POO · /);
  await expect(page.locator(".lx-concepts > li")).toHaveCount(10);
  await expect(page.getByRole("link", { name: /^Unidad 2\. Creación de clases y objetos/ })).toHaveAttribute("href", "#/teoria/poo");
  await expect(page.getByRole("link", { name: /^Unidad 1\. Fundamentos de la programación orientada a objetos/ })).toHaveAttribute("href", "#/teoria/poo-fundamentos");
  await expect(page.getByRole("link", { name: /^Unidad 3\. Atributos y métodos/ })).toHaveAttribute("href", "#/teoria/poo-atributos-metodos");
  await expect(page.getByRole("link", { name: /^Unidad 8\. Métodos especiales de Python/ })).toHaveAttribute("href", "#/teoria/poo-metodos-especiales");
  await expect(page.getByRole("link", { name: /^Unidad 10\. Proyecto final: gestión de una biblioteca/ })).toHaveAttribute("href", "#/teoria/poo-proyecto");
  // Las 10 unidades están publicadas: ninguna sale «en preparación»
  await expect(page.locator(".lx-concepts a.lx-concept__link")).toHaveCount(10);
  await expect(page.locator('[data-available="false"]')).toHaveCount(0);
  await expect(page.getByText("Las 10 unidades están publicadas.")).toBeVisible();
  await expect(page.getByText("Completar lecciones no equivale a dominar")).toBeVisible();
  // En el menú se marca Teoría
  await expect(page.locator('[data-nav="teoria"][aria-current="page"]').first()).toBeVisible();
  await audit(page);
  // Desde Teoría se llega al índice
  await page.goto("/#/teoria");
  await page.getByRole("link", { name: "Índice del módulo de POO: unidades y progreso" }).click();
  await expect(page).toHaveURL(/#\/poo$/);
});

test("la Unidad 2 sigue en #/teoria/poo con todos sus apartados y el currículo como propuesta", async ({ page }) => {
  await page.goto("/#/teoria/poo");
  await expect(page.locator("#learn-title")).toHaveText("Creación de clases y objetos");
  await expect(page.locator(".daw-crumb")).toContainText("Unidad 2 de 10");
  for (const name of SECTIONS) await expect(page.getByRole("heading", { level: 2, name })).toBeVisible();
  await expect(page.locator(".lx-toc__list li")).toHaveCount(SECTIONS.length);
  await expect(page.locator("#lx-curriculum").locator("..")).toContainText("pendiente de validar");
  await expect(page.locator("#lx-curriculum").locator("..")).not.toContainText("Validada");
  await audit(page);
});

for (const [id, number, title] of [
  ["poo-fundamentos", 1, "Fundamentos de la programación orientada a objetos"],
  ["poo-atributos-metodos", 3, "Atributos y métodos"],
  ["poo-encapsulacion", 4, "Encapsulación y propiedades"],
  ["poo-herencia", 5, "Herencia"],
  ["poo-polimorfismo", 6, "Polimorfismo"],
  ["poo-composicion", 7, "Composición y relaciones entre objetos"],
  ["poo-metodos-especiales", 8, "Métodos especiales de Python"],
  ["poo-diseno", 9, "Diseño y buenas prácticas"],
  ["poo-proyecto", 10, "Proyecto final: gestión de una biblioteca"],
]) {
  test(`la Unidad ${number} tiene sus apartados, su posición en el módulo y pasa axe`, async ({ page }) => {
    await page.goto(`/#/teoria/${id}`);
    await expect(page.locator("#learn-title")).toHaveText(title);
    await expect(page.locator(".daw-crumb")).toContainText(`Unidad ${number} de 10`);
    for (const name of SECTIONS) await expect(page.getByRole("heading", { level: 2, name })).toBeVisible();
    await expect(page.locator("#lx-curriculum").locator("..")).toContainText("pendiente de validar");
    await audit(page);
  });
}

test("el proyecto final muestra el diagrama de clases, la rúbrica y los retos", async ({ page }) => {
  await page.goto("/#/teoria/poo-proyecto");
  for (const name of ["Diagrama de clases", "Rúbrica de evaluación", "Retos de ampliación"]) {
    await expect(page.getByRole("heading", { level: 2, name })).toBeVisible();
  }
  const diagram = page.getByRole("img", { name: "Diagrama de clases del proyecto biblioteca" });
  await expect(diagram).toBeVisible();
  await expect(diagram.locator(".lx-uml__class")).toHaveCount(5);
  await expect(page.getByText(/Biblioteca → Prestamo \(composición\)/)).toBeVisible();
  const rubric = page.getByRole("table", { name: "Rúbrica de evaluación" });
  await expect(rubric.getByRole("row")).toHaveCount(6);
  await expect(page.locator(".lx-toc__list")).toContainText("Diagrama de clases");
  await audit(page);
});

test("completar una lección se guarda, no cuenta como dominio y el mini-quiz abre una sesión de 3", async ({ page }) => {
  await page.goto("/#/teoria/poo");
  await expect(page.getByText("0 de 4 lecciones completadas")).toBeVisible();
  await page.getByRole("button", { name: "Marcar la lección como completada" }).first().click();
  await expect(page.getByText("1 de 4 lecciones completadas")).toBeVisible();
  await expect(page.getByRole("heading", { name: /Lección 1\./ })).toContainText("Completada");
  // El foco no se pierde al repintar (WCAG 2.4.3)
  await expect(page.getByRole("button", { name: "Mini-quiz de la lección (3)" }).first()).toBeFocused();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:learn")));
  expect(Object.keys(saved.sections)).toEqual(["poo.definir"]);
  await page.reload();
  await expect(page.getByText("1 de 4 lecciones completadas")).toBeVisible();
  await expect(page.locator(".lx-badges")).not.toContainText("Dominado");
  await page.getByRole("button", { name: "Mini-quiz de la lección (3)" }).first().click();
  await expect(page).toHaveURL(/#\/sesion$/);
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 1 de 3");
  await expect(page.locator(".lx-session-bar")).toContainText("Mini-quiz: Definir una clase y crear objetos");
});

test("el cuestionario de la unidad abre 15 preguntas y explica por qué la opción elegida es incorrecta", async ({ page }) => {
  await page.goto("/#/teoria/poo-fundamentos");
  // Las referencias se presentan como pendientes de comprobación, nunca como comprobadas
  const references = page.locator("#lx-references").locator("..");
  await expect(references).toContainText("Pendiente de comprobación");
  await expect(references).not.toContainText("Comprobada");
  await expect(references.getByRole("link").first()).toHaveAttribute("href", /^https:\/\/docs\.python\.org\/es\/3\//);
  await page.getByRole("button", { name: "Empezar el cuestionario (15 preguntas)" }).click();
  await expect(page).toHaveURL(/#\/sesion$/);
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 1 de 15");
  await expect(page.locator(".lx-session-bar")).toContainText("Cuestionario de la unidad");
  // Primera pregunta (poo1-01): se elige un distractor
  await page.getByText("La POO hace que el programa se ejecute más rápido").click();
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  const feedback = page.locator(".lx-feedback");
  await expect(feedback).toContainText("No es correcto");
  await expect(feedback.getByRole("heading", { name: "Por qué tu opción no es correcta" })).toBeVisible();
  await expect(feedback).toContainText("Usar clases no hace el programa más rápido");
  // Tiene nota: un fallo no añade nuevos intentos al final
  await expect(feedback).not.toContainText("volverás a intentarlo");
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 1 de 15");
  await audit(page);
});

test("la nota del cuestionario se guarda y la unidad ofrece repasar las falladas", async ({ page }) => {
  await page.goto("/#/teoria/poo-fundamentos");
  const bank = await page.evaluate(async () => {
    const data = await (await fetch("/data/learning.json")).json();
    return data.concepts.find((c) => c.id === "poo-fundamentos").bank;
  });
  await page.evaluate((ids) => {
    const at = new Date().toISOString();
    const ex = Object.fromEntries(ids.map((id, i) => [id, { h: [i >= 2], last: at, n: 1 }]));
    localStorage.setItem("pld:learn", JSON.stringify({ v: 1, ex, concepts: {}, errors: {}, log: [], exams: [], quizzes: { "poo-fundamentos": { best: 13, total: 15, last: 13, at, passedAt: at } } }));
  }, bank);
  await page.reload();
  const section = page.locator("#lx-bank").locator("..");
  await expect(section).toContainText("Superado");
  await expect(section).toContainText("Mejor nota: 13 de 15");
  await expect(page.locator("#lx-pass").locator("..")).toContainText("Cuestionario de la unidad: mejor nota 13 de 15");
  await page.getByRole("button", { name: "Repasar las 2 preguntas falladas" }).click();
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 1 de 2");
  await expect(page.locator(".lx-session-bar")).toContainText("Repaso de las preguntas falladas");
});

test("la evaluación final: 30 preguntas sin corrección hasta el final y nota guardada", async ({ page }) => {
  await page.goto("/#/poo");
  const final = page.locator("#lx-poo-final").locator("..");
  await expect(final).toContainText("Se supera con 21 aciertos o más (70 %)");
  await expect(final).toContainText("Aún no lo has hecho");
  await page.getByRole("button", { name: "Empezar la evaluación final (30 preguntas)" }).click();
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 1 de 30");
  await page.locator("#lx-form input[name=lx-choice]").first().check();
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  // Sin corrección: pasa directamente a la siguiente pregunta
  await expect(page.locator(".lx-feedback")).toHaveCount(0);
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 2 de 30");
  await page.getByRole("button", { name: "Terminar la evaluación" }).click();
  await expect(page.locator("#lx-summary-title")).toContainText(/de 30 correctos · \d+ %/);
  await expect(page.locator(".lx-summary")).toContainText("Sin superar");
  await expect(page.locator(".lx-summary")).toContainText("Sin responder: 29 (cuentan como fallos)");
  await expect(page.locator(".lx-reviews > li")).toHaveCount(30);
  await audit(page);
  await page.goto("/#/poo");
  await expect(final).toContainText(/Mejor nota: [01] de 30/);
});

test("los ejemplos se ejecutan con Pyodide en el navegador", async ({ page }) => {
  test.slow(); // la primera carga de Python tarda
  await page.goto("/#/teoria/poo");
  const output = page.locator("#lx-run-0-0");
  await output.evaluate((node) => {
    node.textContent = "";
  });
  await page.getByRole("button", { name: "▶ Ejecutar el ejemplo" }).first().click();
  await expect(output).toHaveText("Alumno\nFalse\nTrue", { timeout: 90_000 });
});

test("el ejercicio guiado muestra el resultado esperado y se corrige con los tests", async ({ page }) => {
  test.slow();
  await page.goto("/#/teoria/poo");
  await page.getByRole("button", { name: "Empezar el ejercicio guiado" }).click();
  await expect(page).toHaveURL(/#\/sesion$/);
  await expect(page.getByText("Resultado esperado")).toBeVisible();
  await page.getByRole("button", { name: "Comprobar con los tests" }).click();
  await expect(page.locator(".lx-feedback")).toBeVisible({ timeout: 90_000 });
  await expect(page.locator(".check")).toContainText("Falla la prueba 1 de 3");
  await expect(page.locator(".lx-feedback")).toContainText("Olvida `self`".replace(/`/g, ""));
});

test.describe("en el móvil", () => {
  test.use({ viewport: { width: 360, height: 740 } });
  test("la unidad y el índice caben sin desplazamiento horizontal", async ({ page }) => {
    for (const route of ["/#/poo", "/#/teoria/poo", "/#/teoria/poo-fundamentos", "/#/teoria/poo-atributos-metodos", "/#/teoria/poo-polimorfismo", "/#/teoria/poo-composicion", "/#/teoria/poo-metodos-especiales", "/#/teoria/poo-diseno", "/#/teoria/poo-proyecto"]) {
      await page.goto(route);
      await page.locator("#learn-title").waitFor();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      expect(overflow, route).toBeLessThanOrEqual(0);
      await audit(page);
    }
  });
});
