// Zona de examen PCAP: panel, simulacro cronometrado, práctica por bloque, fichas y gamificación.
const { test, expect } = require("./fixtures");

const openPcap = async (page, route = "") => {
  await page.goto(`/#/pcap${route}`);
  await expect(page.locator("#pcap-title")).toBeVisible();
};

/** Guarda un estado inicial de la preparación antes de cargar la página. */
const seedPcap = (page, state) =>
  page.addInitScript((value) => localStorage.setItem("pld:pcap", JSON.stringify(value)), state);

test("el panel muestra los 5 bloques con su peso y la preparación a cero", async ({ page }) => {
  await openPcap(page);
  await expect(page.locator("#pcap-title")).toContainText("Prepara el examen PCAP");
  await expect(page.getByRole("link", { name: "Examen PCAP" })).toHaveAttribute("aria-current", "page");
  await expect(page.locator(".block-row")).toHaveCount(5);
  await expect(page.locator(".block-row").nth(3)).toContainText("34 % del examen");
  await expect(page.locator(".readiness__score")).toContainText("0 %");
  await expect(page.locator(".empty-state")).toContainText("ningún simulacro");
});

test("simulacro: 40 preguntas, marcar, saltar, terminar y revisar", async ({ page }) => {
  await openPcap(page, "/simulacro");
  await page.getByRole("button", { name: "Empezar el simulacro" }).click();
  await expect(page.getByRole("timer")).toHaveText(/^6[45]:\d\d$/);
  await expect(page.locator(".exam-grid__item")).toHaveCount(40);

  await page.locator(".exam-q input").first().check();
  await expect(page.locator('[data-go="0"]')).toHaveAttribute("data-state", /answered/);
  await page.getByRole("button", { name: "Siguiente →" }).click();
  await expect(page.locator("#pcap-title")).toHaveText("Pregunta 2 de 40");
  await page.getByRole("button", { name: "Marcar para revisar" }).click();
  await expect(page.locator('[data-go="1"]')).toHaveAttribute("data-state", /flagged/);
  await page.locator('[data-go="39"]').click();
  await expect(page.locator("#pcap-title")).toHaveText("Pregunta 40 de 40");

  await page.locator(".exam-form").getByRole("button", { name: "Terminar examen" }).click();
  await expect(page.locator("#exam-confirm")).toContainText("Te quedan 39 preguntas sin responder");
  await page.getByRole("button", { name: "Sí, terminar" }).click();
  await expect(page.locator("#pcap-title")).toContainText("No aprobado");
  await expect(page.locator(".review-item")).toHaveCount(40);
  await page.getByLabel("Ver solo las falladas").check();
  await expect(page.locator('.review-item[data-ok="true"]').first()).toBeHidden();

  await page.getByRole("link", { name: "Volver al panel" }).click();
  await expect(page.locator(".history tbody tr")).toHaveCount(1);
  await expect(page.locator("#badges-count")).toHaveText(/^1\/20$/); // «Primer simulacro»
});

test("al acabarse el tiempo el simulacro se corrige solo", async ({ page }) => {
  await page.clock.install();
  await openPcap(page, "/simulacro");
  await page.getByRole("button", { name: "Empezar el simulacro" }).click();
  await page.clock.fastForward(65 * 60 * 1000 + 1000);
  await expect(page.locator("#pcap-title")).toContainText("%");
  await expect(page.locator(".review-item")).toHaveCount(40);
});

test("práctica: repite primero lo fallado, «elige dos» limita la selección y cuenta la racha", async ({ page }) => {
  await seedPcap(page, { answers: { "str-06": [false] } });
  await openPcap(page, "/practica/strings");
  const options = page.locator(".exam-q input");
  await expect(page.locator(".exam-q legend")).toContainText("(Elige dos.)"); // str-06 va primero
  await options.nth(0).check();
  await options.nth(1).check();
  await options.nth(2).click(); // la tercera no se deja marcar
  await expect(page.locator(".exam-q input:checked")).toHaveCount(2);

  await page.getByRole("button", { name: "Comprobar" }).click();
  await expect(page.locator(".quiz__verdict")).toBeVisible();
  await expect(page.locator(".exam-q input:disabled")).toHaveCount(await options.count());
  for (let i = 1; i < 10; i += 1) {
    await page.getByRole("button", { name: "Siguiente →" }).click();
    await page.locator(".exam-q input").first().check();
    await page.getByRole("button", { name: "Comprobar" }).click();
  }
  await page.getByRole("button", { name: "Ver resultado" }).click();
  await expect(page.locator(".practice-end")).toContainText("de 10 correctas");
});

test("el idioma de las preguntas se recuerda", async ({ page }) => {
  await openPcap(page, "/practica/poo");
  await page.getByLabel("English (como el examen)").check();
  await expect(page.locator(".exam-q legend")).not.toContainText("¿");
  await page.reload();
  await expect(page.getByLabel("English (como el examen)")).toBeChecked();
});

test("fichas: ver respuesta y marcar como sabida", async ({ page }) => {
  await openPcap(page, "/fichas/poo");
  await expect(page.locator(".chip[aria-current=page]")).toHaveText("Programación orientada a objetos");
  await page.getByRole("button", { name: "Ver respuesta" }).click();
  await expect(page.locator("#card-back")).toBeFocused();
  await page.getByRole("button", { name: "Lo sé →" }).click();
  await expect(page.locator("#pcap-view .course-hero__lead")).toContainText("1 de 48 fichas dominadas");
});

test("la preparación da XP y logros", async ({ page }) => {
  const exam = { date: "2026-09-20T10:00:00Z", correct: 34, total: 40, score: 85, seconds: 3000, blocks: {} };
  await seedPcap(page, { answers: { "str-01": [true], "oop-01": [true] }, exams: [exam], bestCombo: 10 });
  await openPcap(page);
  // 2 preguntas × 5 XP + 1 simulacro aprobado × 50 XP
  await expect(page.locator("#xp-total")).toHaveText("60 XP");
  await page.getByRole("button", { name: /Logros/ }).click();
  for (const name of ["Primer simulacro", "Aprobado", "Con nota", "En racha"]) {
    await expect(page.locator('.badge[data-unlocked="true"]', { hasText: name })).toBeVisible();
  }
});
