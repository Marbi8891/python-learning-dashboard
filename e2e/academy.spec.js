// Estética de academia: ficha del curso, temario, cabecera de lección y «Mi aprendizaje».
const { test, expect, openLesson } = require("./fixtures");

test("la portada es la ficha del curso con su temario", async ({ page }) => {
  await openLesson(page);
  await expect(page.locator("#home-title")).toHaveText("Python, de cero a profesional");
  await expect(page.locator(".course-facts")).toContainText("45 preguntas · 15 retos");
  await expect(page.locator(".outcomes li")).toHaveCount(6);
  await expect(page.locator(".syllabus__module")).toHaveCount(4);
  await expect(page.locator(".syllabus__lesson")).toHaveCount(15);
  // Solo el módulo por el que vas está desplegado, con la siguiente lección marcada
  await expect(page.locator(".syllabus__module[open]")).toHaveCount(1);
  await expect(page.locator('.syllabus__lesson[data-status="current"]')).toContainText("Variables y print()");
  await expect(page.getByRole("link", { name: "El curso" })).toHaveAttribute("aria-current", "page");

  await page.locator(".syllabus__module").nth(3).locator("summary").click();
  await page.getByRole("link", { name: /APIs web con Flask/ }).click();
  await expect(page).toHaveURL(/#\/leccion\/flask$/);
  await expect(page.locator("#lesson-crumb")).toHaveText("Módulo 4 · Especialización — Lección 15 de 15");
  await expect(page.locator("#lesson-meta")).toContainText("min");
  await expect(page.getByRole("link", { name: "El curso" })).not.toHaveAttribute("aria-current", "page");
});

test("«Mi aprendizaje» refleja lecciones, quizzes y actividad", async ({ page }) => {
  await openLesson(page, "variables");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await page.getByRole("tab", { name: "Quiz" }).click();
  for (let qi = 0; qi < 3; qi += 1) await page.locator(`input[name=q${qi}]`).first().check();
  await page.getByRole("button", { name: "Comprobar respuestas" }).click();

  await page.getByRole("link", { name: "Mi aprendizaje" }).first().click();
  await expect(page).toHaveURL(/#\/perfil$/);
  await expect(page.locator("#profile-title")).toHaveText("Mi aprendizaje");
  await expect(page.locator(".kpi").first()).toContainText("1/15");
  await expect(page.locator(".module-progress").first()).toContainText("1/4");
  await expect(page.getByRole("img", { name: /1 día con actividad/ })).toBeVisible();
  const first = page.locator(".history tbody tr").first();
  await expect(first).toHaveAttribute("data-done", "true");
  await expect(first.locator("td").nth(2)).toHaveText(/^[0-3]\/3$/);
  await expect(page.locator(".history tbody tr")).toHaveCount(15);

  // La portada ya ofrece continuar y enlaza al perfil
  await page.getByRole("link", { name: "El curso" }).click();
  await expect(page.getByRole("link", { name: "Continuar: Tipos de datos →" })).toBeVisible();
});
