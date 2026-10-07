// Cuenta de usuario contra el backend REAL (lo arranca playwright.config.js).
const { request: playwrightRequest } = require("@playwright/test");
const { test, expect, uniqueEmail, openLesson } = require("./fixtures");

const PASSWORD = "contraseña-e2e-123";
const dialog = (page) => page.locator("#account-dialog");

async function register(page, email, name = "Ana") {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await dialog(page).getByRole("link", { name: "Crea una" }).click();
  const form = page.locator("#register-form");
  await form.getByLabel("Nombre").fill(name);
  await form.getByLabel("Email").fill(email);
  await form.getByLabel(/Contraseña/).fill(PASSWORD);
  await form.getByLabel(/acepto la/).check();
  await form.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#account-label")).toHaveText(name);
}

/** Consulta la API como el usuario. El token de la web va en una cookie HttpOnly (no se puede
    leer desde la página), así que el test inicia sesión por su cuenta. */
async function apiAs(page, path, email) {
  const login = await page.request.post("http://127.0.0.1:8000/api/v1/auth/login", { form: { username: email, password: PASSWORD } });
  const { access_token: token } = await login.json();
  const response = await page.request.get(`http://127.0.0.1:8000${path}`, { headers: { Authorization: `Bearer ${token}` } });
  return response.json();
}

test("registro, sincronización del progreso local, cierre e inicio de sesión", async ({ page }) => {
  await openLesson(page, "variables");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click(); // progreso sin cuenta

  const email = uniqueEmail();
  await register(page, email);
  // se subió al servidor (la fusión es asíncrona: se espera en vez de leer una sola vez)
  await expect.poll(async () => (await apiAs(page, "/api/v1/progress", email)).map((p) => p.lesson_slug)).toEqual(["variables"]);

  await page.locator(".lesson[data-slug=tipos]").click();
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await expect.poll(async () => (await apiAs(page, "/api/v1/progress", email)).length).toBe(2);

  await page.locator("#account-button").click();
  await dialog(page).getByRole("button", { name: "Cerrar sesión" }).click();
  // Cerrar sesión borra los datos del navegador y recarga (ADR-0022): el aviso sale ya recargada
  await expect(page.locator("#toast")).toContainText("Sesión cerrada");
  await expect(page.locator("#account-label")).toHaveText("Iniciar sesión");

  await page.evaluate(() => localStorage.removeItem("pld:completed")); // otro dispositivo
  await page.reload();
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await dialog(page).getByLabel("Email").first().fill(email);
  await dialog(page).locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await dialog(page).getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
  await expect(page.locator(".module[data-module=fundamentos] .module__count")).toHaveText("2/8");
});

test("errores de validación y credenciales en español", async ({ page }) => {
  await openLesson(page);
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await dialog(page).locator("#login-form").getByLabel("Email").fill("nadie@example.com");
  await dialog(page).locator("#login-form").getByLabel("Contraseña").fill("incorrecta-123");
  await dialog(page).getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-message")).toHaveText("Email o contraseña incorrectos");
});

test("la sesión va en una cookie HttpOnly: sigue al recargar y JavaScript no ve el token", async ({ page }) => {
  // ADR-0033: ni en el almacenamiento ni en document.cookie; solo la API puede leerla y borrarla
  await openLesson(page, "variables");
  await register(page, uniqueEmail(), "Luis");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  const sessionCookie = async () => (await page.context().cookies()).find((c) => c.name === "__Host-pld_session");
  // Particionada (CHIPS): solo vale cuando la API se usa desde esta web
  expect(await sessionCookie()).toMatchObject({ httpOnly: true, secure: true, sameSite: "None", partitionKey: "http://localhost" });
  await page.reload();
  await expect(page.locator("#account-label")).toHaveText("Luis");
  const visible = await page.evaluate(
    () => JSON.stringify({ ...localStorage }) + JSON.stringify({ ...sessionStorage }) + document.cookie,
  );
  expect(visible).not.toMatch(/eyJ[\w-]+\.[\w-]+\./); // ningún JWT al alcance de un script
  await page.locator(".lesson[data-slug=tipos]").click();
  await expect(page.locator(".lesson[data-slug=variables]")).toHaveAttribute("data-status", "completed");

  await page.locator("#account-button").click();
  await dialog(page).getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page.locator("#toast")).toContainText("Sesión cerrada");
  expect(await sessionCookie()).toBeUndefined(); // la API la borró
  await page.reload();
  await expect(page.locator("#account-label")).toHaveText("Iniciar sesión");
});

test("si el navegador bloquea la cookie, se entra igual con el token solo en memoria", async ({ page }) => {
  // Como Safari con las cookies de terceros: la respuesta del login llega sin Set-Cookie
  // La petición sale desde un contexto aparte: route.fetch() guardaría la cookie en el del navegador
  const outside = await playwrightRequest.newContext();
  await page.route("http://127.0.0.1:8000/api/v1/auth/login", async (route) => {
    const response = await outside.fetch(route.request());
    const headers = { ...response.headers() };
    delete headers["set-cookie"];
    await route.fulfill({ response, headers });
  });
  await openLesson(page, "variables");
  const email = uniqueEmail();
  await register(page, email, "Eva");
  expect(await page.context().cookies()).toEqual([]);
  // La sesión funciona (se sincroniza el progreso) y, como antes, recargar la cierra
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await expect.poll(async () => (await apiAs(page, "/api/v1/progress", email)).length).toBe(1);
  await page.reload();
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
  await expect(page.locator("#account-label")).toHaveText("Iniciar sesión");
});

test("exportar datos y eliminar la cuenta (RGPD)", async ({ page }) => {
  await openLesson(page);
  const email = uniqueEmail();
  await register(page, email);
  await page.locator("#account-button").click();

  const download = page.waitForEvent("download");
  await dialog(page).getByRole("button", { name: "Descargar mis datos (JSON)" }).click();
  const file = await download;
  expect(file.suggestedFilename()).toBe("mis-datos-python-learning.json");
  const exported = JSON.parse(require("node:fs").readFileSync(await file.path(), "utf8"));
  expect(exported.user.email).toBe(email);

  await dialog(page).getByText("Eliminar mi cuenta").click();
  const form = page.locator("#delete-form");
  await form.getByLabel("Confirma con tu contraseña").fill("incorrecta-123");
  await form.getByRole("button", { name: "Eliminar definitivamente" }).click();
  await expect(page.locator("#account-message")).toHaveText("Contraseña incorrecta");

  await form.getByLabel("Confirma con tu contraseña").fill(PASSWORD);
  await form.getByRole("button", { name: "Eliminar definitivamente" }).click();
  await expect(page.locator("#toast")).toContainText("se han borrado");
  await expect(page.locator("#account-label")).toHaveText("Iniciar sesión");
});

test("recuperar contraseña: solicitud y enlace no válido", async ({ page }) => {
  await openLesson(page);
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await dialog(page).getByRole("link", { name: "¿Has olvidado tu contraseña?" }).click();
  await page.locator("#forgot-form").getByLabel("Correo electrónico").fill("nadie@example.com");
  await page.locator("#forgot-form").getByRole("button", { name: "Enviar instrucciones" }).click();
  await expect(page.locator("#account-message")).toContainText("Si el email está registrado");

  await page.goto(`/#/restablecer?token=${"x".repeat(43)}`);
  await expect(dialog(page)).toBeVisible();
  await expect(page).toHaveURL(/#\/aprender$/); // el token no se queda en la URL
  const form = page.locator("#reset-form");
  await expect(form).toContainText("Entre 8 y 128 caracteres"); // requisitos visibles
  await form.getByLabel("Nueva contraseña", { exact: true }).fill("nueva-contraseña-456");
  await form.getByLabel("Repite la nueva contraseña").fill("nueva-contraseña-456");
  await form.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.locator("#account-message")).toContainText("no es válido o ha caducado");

  // Desde el error se puede pedir otro enlace
  await form.getByRole("link", { name: "Pedir un enlace nuevo" }).click();
  await expect(page.locator("#forgot-form")).toBeVisible();
});

test("recuperar contraseña: las dos contraseñas deben coincidir", async ({ page }) => {
  let called = false;
  await page.route("**/api/v1/auth/password-reset/confirm", (route) => {
    called = true;
    return route.fulfill({ status: 204 });
  });
  await page.goto(`/#/restablecer?token=${"x".repeat(43)}`);
  const form = page.locator("#reset-form");
  await form.getByLabel("Nueva contraseña", { exact: true }).fill("nueva-contraseña-456");
  await form.getByLabel("Repite la nueva contraseña").fill("otra-distinta-789");
  await form.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.locator("#account-message")).toHaveText("Las dos contraseñas no coinciden.");
  expect(called).toBe(false); // ni siquiera se llama a la API
});

test("recuperar contraseña: un enlace incompleto lleva a pedir otro", async ({ page }) => {
  await page.goto("/#/restablecer");
  await expect(page.locator("#forgot-form")).toBeVisible();
  await expect(page.locator("#account-message")).toContainText("no es válido o ha caducado");
});

test("recuperar contraseña: tras el cambio se vuelve al login", async ({ page }) => {
  await page.route("**/api/v1/auth/password-reset/confirm", (route) => route.fulfill({ status: 204 }));
  await page.goto(`/#/restablecer?token=${"x".repeat(43)}`);
  const form = page.locator("#reset-form");
  await form.getByLabel("Nueva contraseña", { exact: true }).fill("nueva-contraseña-456");
  await form.getByLabel("Repite la nueva contraseña").fill("nueva-contraseña-456");
  await form.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.locator("#account-message")).toHaveText(
    "Tu contraseña se ha actualizado correctamente. Ya puedes iniciar sesión.",
  );
  await expect(page.locator("#login-form")).toBeVisible();
  await expect(form.getByLabel("Nueva contraseña", { exact: true })).toHaveValue(""); // no se queda en el DOM
});

test("sin email en el servidor, la recuperación ofrece el contacto", async ({ page }) => {
  await page.route("**/api/v1/health", (route) => route.fulfill({ json: { status: "ok", email: false } }));
  await openLesson(page);
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await dialog(page).getByRole("link", { name: "¿Has olvidado tu contraseña?" }).click();
  const form = page.locator("#forgot-form");
  await expect(form).toContainText("La recuperación por email aún no está activa");
  await expect(form.getByRole("link", { name: /@/ })).toHaveAttribute("href", /^mailto:/);
  await expect(form.getByRole("button", { name: "Enviar instrucciones" })).toBeHidden();
});

test("un servidor lento avisa de que se está despertando", async ({ page }) => {
  await page.route("**/api/v1/auth/login", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 5000));
    await route.continue();
  });
  await openLesson(page);
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill("nadie@example.com");
  await page.locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-message")).toContainText("El servidor se está despertando");
  await expect(page.locator("#account-message")).not.toContainText("despertando", { timeout: 15_000 });
});
