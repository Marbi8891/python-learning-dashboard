// Sincronización del progreso de los cursos entre dos sesiones abiertas a la vez con la misma cuenta.
const { test, expect, uniqueEmail, openLesson } = require("./fixtures");

const PASSWORD = "contraseña-e2e-123";
const API = "http://127.0.0.1:8000";

/** Preguntas que el servidor tiene guardadas del curso (inicia sesión por su cuenta: el token de la web va en una cookie HttpOnly). */
async function serverAnswers(request, email) {
  const login = await request.post(`${API}/api/v1/auth/login`, { form: { username: email, password: PASSWORD } });
  const { access_token: token } = await login.json();
  const response = await request.get(`${API}/api/v1/course-state/sql`, { headers: { Authorization: `Bearer ${token}` } });
  const { data } = await response.json();
  return Object.keys(data?.answers ?? {}).sort();
}

/** Responde una pregunta del curso de Bases de datos como lo hace la app y la guarda. */
async function answer(page, questionId) {
  await page.evaluate(async (id) => {
    const store = await import("/js/course-store.js");
    store.recordCourseAnswer("sql", id, true);
    store.saveCourse("sql");
  }, questionId);
}

test("dos sesiones de la misma cuenta no se pisan el progreso de un curso", async ({ browser, request }) => {
  const email = uniqueEmail();
  const first = await (await browser.newContext()).newPage();
  const second = await (await browser.newContext()).newPage();

  // Al iniciar sesión cada sesión sube su copia a los 1,5 s. Se espera a que termine para que esa subida
  // no coincida con la de la respuesta: dos subidas en el mismo instante son una carrera que solo cerraría
  // un control de concurrencia en el servidor (ver docs/IMPROVEMENT_PLAN.md).
  const loginPush = (page) =>
    page.waitForResponse((r) => r.request().method() === "PUT" && r.url().endsWith("/course-state/sql"));

  await openLesson(first, "variables");
  await first.getByRole("button", { name: "Iniciar sesión" }).click();
  await first.locator("#account-dialog").getByRole("link", { name: "Crea una" }).click();
  const form = first.locator("#register-form");
  await form.getByLabel("Nombre").fill("Ana");
  await form.getByLabel("Email").fill(email);
  await form.getByLabel(/Contraseña/).fill(PASSWORD);
  await form.getByLabel(/acepto la/).check();
  const firstPush = loginPush(first);
  await form.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(first.locator("#account-label")).toHaveText("Ana");
  await firstPush;

  // La segunda sesión se abre antes de que la primera guarde nada: no conoce lo que ella responda después.
  await openLesson(second, "variables");
  await second.getByRole("button", { name: "Iniciar sesión" }).click();
  const login = second.locator("#account-dialog").locator("#login-form");
  await login.getByLabel("Email").fill(email);
  await login.getByLabel("Contraseña").fill(PASSWORD);
  const secondPush = loginPush(second);
  await second.locator("#account-dialog").getByRole("button", { name: "Entrar" }).click();
  await expect(second.locator("#account-label")).toHaveText("Ana");
  await secondPush;

  await answer(first, "bd-01");
  await expect.poll(() => serverAnswers(request, email)).toEqual(["bd-01"]);

  await answer(second, "bd-02");
  // El servidor conserva las dos: la segunda sesión fusiona con la cuenta antes de subir.
  await expect.poll(() => serverAnswers(request, email), { timeout: 15_000 }).toEqual(["bd-01", "bd-02"]);
});
