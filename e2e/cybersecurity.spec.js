// Curso de ciberseguridad: el progreso se sincroniza con la cuenta. Antes solo vivía en el navegador y
// «Cerrar sesión» (que borra los datos de este navegador) lo perdía sin copia en ningún sitio.
const fs = require("node:fs");
const path = require("node:path");
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";
const PASSWORD = "contraseña-segura";
const course = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "frontend", "data", "cybersecurity", "course.json"), "utf8"));
const dialog = (page) => page.locator("#account-dialog");

async function account(request) {
  const email = uniqueEmail();
  await request.post(`${API}/api/v1/auth/register`, { data: { email, password: PASSWORD, display_name: "Ana", accept_privacy: true } });
  const login = await request.post(`${API}/api/v1/auth/login`, { form: { username: email, password: PASSWORD } });
  return { email, headers: { Authorization: `Bearer ${(await login.json()).access_token}` } };
}

async function login(page, email) {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
}

const savedDoc = async (request, headers) =>
  (await (await request.get(`${API}/api/v1/course-state/cybersecurity`, { headers })).json()).data;

test("una semana completada sigue en la cuenta después de cerrar sesión y volver a entrar", async ({ page, request }) => {
  const { email, headers } = await account(request);
  await page.goto("/#/ciberseguridad");
  await login(page, email);

  const week = course.weeks[0];
  await page.goto(`/#/ciberseguridad/${week.id}`);
  // La página de la semana repite id="cyber-title" (cabecera del curso y título de la semana): se busca por nombre
  await expect(page.getByRole("heading", { level: 1, name: week.title })).toBeVisible();
  for (const [i, question] of week.quiz.entries()) {
    await page.locator(`input[name="cyber-q-${i}"][value="${question.answer}"]`).check();
  }
  await page.getByRole("button", { name: "Corregir cuestionario" }).click();
  await expect(page.locator(".cyber-quiz-result")).toContainText("3/3");
  await page.getByRole("button", { name: "Marcar semana como completada" }).click();
  await expect(page.getByRole("button", { name: "Marcar como pendiente" })).toBeVisible();
  await expect.poll(async () => (await savedDoc(request, headers)).weeks?.[week.id]?.done).toBe(true);

  // Cerrar sesión sin conservar los datos: este navegador se queda sin el progreso…
  await page.locator("#account-button").click();
  await dialog(page).getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page.locator("#account-label")).toHaveText("Iniciar sesión");
  expect(await page.evaluate(() => localStorage.getItem("pld:cybersecurity:v1"))).toBeNull();

  // …y al volver a entrar lo trae la cuenta
  await page.goto("/#/ciberseguridad");
  await login(page, email);
  await expect(page.locator(".cyber-progress-label")).toHaveText("1 de 16 semanas completadas · 6%");
});

test("el progreso guardado con la versión anterior (solo en el navegador) se sube a la cuenta al entrar", async ({ page, request }) => {
  const { email, headers } = await account(request);
  await page.addInitScript(() => {
    if (!localStorage.getItem("pld:cybersecurity:v1")) {
      localStorage.setItem("pld:cybersecurity:v1", JSON.stringify({ completed: ["semana-01", "semana-02"], quizScores: { "semana-01": 3, "semana-02": 2 } }));
    }
  });
  await page.goto("/#/ciberseguridad");
  await expect(page.locator(".cyber-progress-label")).toHaveText("2 de 16 semanas completadas · 13%");
  await login(page, email);

  await expect.poll(async () => Object.keys((await savedDoc(request, headers)).weeks ?? {}).sort()).toEqual(["semana-01", "semana-02"]);
  const saved = await savedDoc(request, headers);
  expect(saved.quiz["semana-01"].score).toBe(3);
  expect(saved.completed).toBeUndefined();
});
