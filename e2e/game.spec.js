// Quiz, retos, XP, niveles, racha y logros.
const { test, expect, openLesson } = require("./fixtures");

test.describe.configure({ timeout: 120_000 });

const quizTab = (page) => page.getByRole("tab", { name: "Quiz" });

async function answers(page, slug) {
  const data = await page.evaluate(() => fetch("data/lessons.json").then((r) => r.json()));
  const lesson = data.modules.flatMap((m) => m.lessons).find((l) => l.slug === slug);
  return lesson.quiz.map((q) => q.answer);
}

async function toastSeen(page, text) {
  await expect(page.locator("#toast")).toContainText(text, { timeout: 15_000 });
}

test("quiz: exige responder todo, explica cada respuesta y premia el pleno", async ({ page }) => {
  await openLesson(page, "operadores");
  await quizTab(page).click();
  await expect(page.locator(".quiz__q")).toHaveCount(3);
  await page.getByRole("button", { name: "Comprobar respuestas" }).click();
  await expect(page.locator("#quiz-message")).toHaveText("Responde las 3 preguntas antes de comprobar.");

  const correct = await answers(page, "operadores");
  // Primer intento: falla la primera pregunta
  for (const [qi, answer] of correct.entries()) {
    const pick = qi === 0 ? (answer + 1) % 4 : answer;
    await page.locator(`input[name=q${qi}][value="${pick}"]`).check();
  }
  await page.getByRole("button", { name: "Comprobar respuestas" }).click();
  await expect(page.locator("#quiz-score")).toContainText("2/3");
  await expect(page.getByRole("button", { name: "Comprobar respuestas" })).toBeHidden();
  await expect(page.getByRole("button", { name: "Volver a intentarlo" })).toBeVisible();
  await expect(page.locator('.quiz__q[data-q="0"] .quiz__verdict')).toHaveText("✗ Incorrecto");
  await expect(page.locator('.quiz__q[data-q="0"] .quiz__feedback')).toContainText("división entera");
  await expect(page.locator("#xp-total")).toHaveText("20 XP");

  // Segundo intento: pleno → solo suma la diferencia (sin XP dobles) y desbloquea el logro
  await page.getByRole("button", { name: "Volver a intentarlo" }).click();
  for (const [qi, answer] of correct.entries()) await page.locator(`input[name=q${qi}][value="${answer}"]`).check();
  await page.getByRole("button", { name: "Comprobar respuestas" }).click();
  await expect(page.locator("#quiz-score")).toContainText("3/3");
  await expect(page.locator("#xp-total")).toHaveText("40 XP");
  await toastSeen(page, "Logro desbloqueado: Quiz perfecto");

  await page.reload();
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
  await quizTab(page).click();
  await expect(page.locator(".quiz__intro")).toContainText("Mejor resultado: 3/3");
  await expect(page.locator("#xp-total")).toHaveText("40 XP");
});

test("XP y nivel suben al completar lecciones", async ({ page }) => {
  await openLesson(page, "variables");
  await expect(page.locator("#xp-level")).toHaveText("Nivel 1 · Novato/a");
  for (const slug of ["variables", "tipos"]) {
    await page.locator(`.lesson[data-slug=${slug}]`).click();
    await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
    await page.getByRole("button", { name: "Marcar como completada" }).click();
  }
  await expect(page.locator("#xp-total")).toHaveText("100 XP");
  await expect(page.locator("#xp-level")).toHaveText("Nivel 2 · Aprendiz");
  await toastSeen(page, "Subes a nivel 2");
  await expect(page.locator("#xp-bar")).toHaveAttribute("aria-valuenow", "0");
});

test("logros de la consola: primer programa y cazador de bugs", async ({ page }) => {
  await openLesson(page, "variables");
  const editor = page.locator("#console-editor");
  await editor.fill("print(1 / 0)");
  await page.locator("#console-run").click();
  await expect(page.locator("#console-output")).toContainText("ZeroDivisionError", { timeout: 90_000 });
  await editor.fill("print(1 / 1)");
  await page.locator("#console-run").click();
  await toastSeen(page, "¡Hola, mundo!");
  await page.getByRole("button", { name: /Logros/ }).click();
  const dialog = page.locator("#badges-dialog");
  await expect(dialog.locator('.badge[data-unlocked="true"]')).toHaveCount(2);
  await expect(dialog.locator('.badge[data-unlocked="true"]').filter({ hasText: "Cazador/a de bugs" })).toBeVisible();
  await expect(page.locator("#badges-count")).toHaveText("2/13");
});

test("reto extra: se supera, suma XP según estrellas y lo celebra", async ({ page }) => {
  // Tests de prueba propios: el repositorio no contiene las soluciones reales
  await page.route("**/data/lessons.json", async (route) => {
    const data = await (await route.fetch()).json();
    const lesson = data.modules[0].lessons[0];
    lesson.challenge.checks = [{ stdin: "", test: "assert reto == 'ok', 'reto debe valer ok'" }];
    lesson.checks = [{ stdin: "", test: "assert x == 1, 'x debe ser 1'" }];
    await route.fulfill({ json: data });
  });
  await openLesson(page, "variables");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await expect(page.getByRole("heading", { name: "Reto extra: Tarjeta de presentación" })).toBeVisible();

  await page.getByRole("button", { name: "Cargar reto en la consola" }).click();
  await expect(page.locator("#console-editor")).toHaveValue(/ficha = \.\.\./);
  await page.locator("#console-editor").fill("reto = 'ok'");
  await page.getByRole("button", { name: "Comprobar reto" }).click();
  await expect(page.locator("#challenge-result")).toHaveAttribute("data-passed", "true", { timeout: 90_000 });
  await expect(page.locator("canvas.confetti")).toHaveCount(1);
  await expect(page.locator("#challenge-done")).toBeVisible();
  await expect(page.locator("#xp-total")).toHaveText("30 XP"); // reto de 1 estrella
  await toastSeen(page, "Retador/a");

  // Ejercicio superado a la primera: +50 lección +20 bonus
  await page.locator("#console-editor").fill("x = 1");
  await page.getByRole("button", { name: "Comprobar solución" }).click();
  await expect(page.locator("#check-result")).toHaveAttribute("data-passed", "true");
  await expect(page.locator("#xp-total")).toHaveText("100 XP");
});

test("sin confeti si el sistema pide reducir el movimiento", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.route("**/data/lessons.json", async (route) => {
    const data = await (await route.fetch()).json();
    data.modules[0].lessons[0].checks = [{ stdin: "", test: "assert True" }];
    await route.fulfill({ json: data });
  });
  await openLesson(page, "variables");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.locator("#console-editor").fill("pass");
  await page.getByRole("button", { name: "Comprobar solución" }).click();
  await expect(page.locator("#check-result")).toHaveAttribute("data-passed", "true", { timeout: 90_000 });
  await expect(page.locator("#toast")).toContainText("Ejercicio superado");
  await expect(page.locator("canvas.confetti")).toHaveCount(0);
});

test("racha de días seguidos y logro de constancia", async ({ page }) => {
  await page.addInitScript(() => {
    if (localStorage.getItem("pld:game")) return;
    const day = (offset) => {
      const d = new Date();
      d.setDate(d.getDate() - offset);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    };
    localStorage.setItem("pld:game", JSON.stringify({ days: [day(2), day(1)] }));
  });
  await openLesson(page, "variables");
  await expect(page.locator("#xp-streak")).toHaveText("Racha: 2 días"); // hoy aún sin actividad
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await expect(page.locator("#xp-streak")).toHaveText("Racha: 3 días");
  await toastSeen(page, "Constancia");
});
