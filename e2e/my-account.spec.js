// «Mi cuenta» ampliada (ADR-0025): plan de estudio, progreso de todos los cursos, logros y
// certificados, perfil y seguridad. Contra el backend real.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";
const PASSWORD = "contraseña-e2e-123";

async function signIn(page, request) {
  const email = uniqueEmail();
  await request.post(`${API}/api/auth/register`, { data: { email, password: PASSWORD, display_name: "Ana", accept_privacy: true } });
  await page.goto("/#/inicio");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
  await page.goto("/#/cuenta");
  await expect(page.locator("#private-title")).toHaveText("Ana");
  return email;
}

test("plan de estudio: fecha de examen por curso y meta diaria que se guardan", async ({ page, request }) => {
  const email = await signIn(page, request);
  const date = page.getByLabel("Fecha del examen de Programación");
  const inTwentyDays = new Date(Date.now() + 20 * 86_400_000);
  const day = `${inTwentyDays.getFullYear()}-${String(inTwentyDays.getMonth() + 1).padStart(2, "0")}-${String(inTwentyDays.getDate()).padStart(2, "0")}`;
  await date.fill(day);
  await expect(page.locator("#toast")).toContainText("Fecha del examen guardada");
  await expect(page.getByRole("row", { name: /Programación/ })).toContainText("20 días");
  await expect(page.getByLabel("Fecha del examen de Programación")).toBeFocused(); // el foco no se pierde

  await page.getByLabel("Meta diaria").selectOption("30");
  await expect(page.locator("#toast")).toContainText("Meta diaria: 30 preguntas");
  // La sesión sigue tras recargar (cookie HttpOnly, ADR-0033): lo que se ve sale de la cuenta
  await page.reload();
  await expect(page.locator("#account-label")).toHaveText("Ana");
  await page.goto("/#/cuenta");
  await expect(page.getByLabel("Fecha del examen de Programación")).toHaveValue(day);
  await expect(page.getByLabel("Meta diaria")).toHaveValue("30");
});

test("progreso de todos los cursos, tema más flojo y certificados", async ({ page, request }) => {
  await page.addInitScript(() => {
    // Un curso con respuestas: 3 falladas en el primer bloque de Bases de datos
    localStorage.setItem("pld:course:sql", JSON.stringify({ answers: { "sql-01": [false], "sql-02": [false], "sql-03": [true] } }));
  });
  await signIn(page, request);
  const card = page.locator('[data-course-card="sql"]');
  await expect(card).toContainText("3 preguntas respondidas");
  await expect(card).toContainText("Dominio:");
  await expect(card).toContainText("Tu tema más flojo");
  await expect(page.locator('[data-course-card="programacion"]')).toContainText("Siguiente tema sin empezar");
  await expect(page.locator('[data-cert="sql"]')).toContainText("dominio");

  // Página del certificado de un curso sin terminar: dice qué falta
  await page.goto("/#/certificado/sql");
  await expect(page.locator("#certificate-title")).toHaveText("Certificado · Bases de datos");
  await expect(page.locator("#course-certificate")).toContainText("Un dominio del curso del 70 %");
});

test("perfil y seguridad: cambiar el nombre, la contraseña y ver la actividad", async ({ page, request }) => {
  const email = await signIn(page, request);
  await expect(page.locator("#account-activity")).toContainText("Inicio de sesión");

  await page.getByLabel("Nombre que se muestra").fill("Ana María");
  await page.getByRole("button", { name: "Guardar nombre" }).click();
  await expect(page.locator("#private-title")).toHaveText("Ana María");
  await expect(page.locator("#account-label")).toHaveText("Ana María");

  const form = page.locator("#password-form");
  await form.getByLabel("Contraseña actual").fill(PASSWORD);
  await form.getByLabel("Nueva contraseña (mínimo 8 caracteres)").fill("tortuga-azul-en-bici");
  await form.getByLabel("Repite la nueva").fill("otra-distinta-123");
  await form.getByRole("button", { name: "Cambiar contraseña" }).click();
  await expect(form.locator(".form-message")).toHaveText("Las dos contraseñas nuevas no coinciden.");

  await form.getByLabel("Repite la nueva").fill("tortuga-azul-en-bici");
  await form.getByRole("button", { name: "Cambiar contraseña" }).click();
  await expect(page.locator("#toast")).toContainText("Contraseña cambiada");
  // Esta sesión sigue abierta y la actividad lo refleja
  await expect(page.locator("#account-activity")).toContainText("Contraseña cambiada desde Mi cuenta");
  await expect(page.locator("#account-label")).toHaveText("Ana María");
  const old = await request.post(`${API}/api/auth/login`, { form: { username: email, password: PASSWORD } });
  expect(old.status()).toBe(401);
});

test("Mi cuenta sin infracciones WCAG", async ({ page, request }) => {
  await signIn(page, request);
  await expect(page.locator("#account-activity li").first()).toBeVisible();
  await expect(page.locator('[data-course-card="java"] [data-course-detail]')).toContainText("Dominio:");
  await page.waitForFunction(() => !document.querySelector("#toast.toast--visible"), null, { timeout: 20_000 });
  const results = await new AxeBuilder({ page }).include("#private-view").withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
});
