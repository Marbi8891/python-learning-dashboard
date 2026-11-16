// Excel profesional, fase P0: el curso está registrado en el catálogo (familia academia) y su
// progreso se fusiona y sincroniza con la cuenta como el de cualquier curso, sin aparecer todavía en
// la web ni entre los cursos de DAW.
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";

test("el progreso de Excel profesional se fusiona con la cuenta en los dos sentidos", async ({ page, request }) => {
  const email = uniqueEmail();
  const password = "contraseña-e2e-123";
  await request.post(`${API}/api/v1/auth/register`, { data: { email, password, display_name: "Ana", accept_privacy: true } });
  const login = await request.post(`${API}/api/v1/auth/login`, { form: { username: email, password } });
  const headers = { Authorization: `Bearer ${(await login.json()).access_token}` };
  // Otro dispositivo ya había completado una unidad
  await request.put(`${API}/api/v1/course-state/excel`, {
    headers,
    data: { data: { done: { "xl1-interfaz": "2026-11-15T10:00:00.000Z" } } },
  });
  // Y en este navegador, sin sesión, se completó otra
  await page.addInitScript(() => {
    if (!localStorage.getItem("pld:course:excel")) {
      localStorage.setItem("pld:course:excel", JSON.stringify({ done: { "xl1-datos": "2026-11-16T09:00:00.000Z" } }));
    }
  });

  await page.goto("/#/daw/cursos");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(password);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");

  // La cuenta recibe lo de este navegador sin perder lo del otro dispositivo
  await expect
    .poll(async () => Object.keys((await (await request.get(`${API}/api/v1/course-state/excel`, { headers })).json()).data.done ?? {}).sort())
    .toEqual(["xl1-datos", "xl1-interfaz"]);
  // Y el navegador, lo de la cuenta
  const local = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:course:excel")));
  expect(Object.keys(local.done).sort()).toEqual(["xl1-datos", "xl1-interfaz"]);
});

test("Excel profesional no aparece entre los cursos de DAW", async ({ page }) => {
  await page.goto("/#/daw/cursos");
  await expect(page.locator(".daw-card")).toHaveCount(6);
  await expect(page.locator("#daw-view")).not.toContainText("Excel");
});
