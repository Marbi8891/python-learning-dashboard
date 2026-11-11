const { test, expect, openLesson, watchClipboard } = require("./fixtures");

test("la portada del curso PCAP lleva a la primera lección pendiente y la barra lateral navega", async ({ page }) => {
  await openLesson(page);
  await page.getByRole("link", { name: "Curso PCAP" }).click();
  await expect(page).toHaveURL(/#\/inicio$/);
  await expect(page.locator("#home-title")).toContainText("Prepara el PCAP");
  await page.getByRole("link", { name: "Empezar la primera lección →" }).click();
  await expect(page).toHaveURL(/#\/leccion\/variables$/);
  await expect(page.locator("#lesson-title")).toHaveText("Variables y print()");
  await expect(page.locator(".lesson[data-slug]")).toHaveCount(27);

  await page.locator(".lesson[data-slug=tipos]").click();
  await expect(page).toHaveURL(/#\/leccion\/tipos$/);
  await expect(page.locator("#lesson-title")).toHaveText("Tipos de datos");
  await expect(page.locator(".lesson[data-slug=tipos]")).toHaveAttribute("aria-current", "page");
  await expect(page.locator("#panel-theory code.hljs")).toHaveCount(1); // resaltado de sintaxis
});

test("una lección que no existe dice que no existe y deja volver", async ({ page }) => {
  // Antes abría otra lección sin avisar (NAV-01)
  await openLesson(page, "no-existe");
  await expect(page).toHaveURL(/#\/leccion\/no-existe$/);
  await expect(page.locator("#notfound-title")).toHaveText("No encontramos esta lección");
  await expect(page.locator("#notfound-view")).toContainText("#/leccion/no-existe");
  await expect(page).toHaveTitle(/Página no encontrada/);
  await page.getByRole("link", { name: "Ver las lecciones del curso" }).click();
  await expect(page).toHaveURL(/#\/inicio$/);
  await expect(page.locator("#home-title")).toBeVisible();
  await page.goBack();
  await expect(page.locator("#notfound-title")).toBeVisible();
});

test("#/leccion/ sin nombre abre la lección por la que vas", async ({ page }) => {
  await openLesson(page);
  await page.goto("/#/leccion/");
  await expect(page).toHaveURL(/#\/leccion\/variables$/);
  await expect(page.locator("#lesson-title")).toHaveText("Variables y print()");
});

for (const [route, title, zone] of [
  ["#/no-existe", "#notfound-title", "#notfound-view"],
  ["#/pcapx", "#notfound-title", "#notfound-view"],
  ["#/pcap/no-existe", "#pcap-title", "#pcap-view"],
  ["#/pcap/practica/no-existe", "#pcap-title", "#pcap-view"],
  ["#/daw/no-existe", "#daw-title", "#daw-view"],
  ["#/daw/sql/leccion/no-existe", "#daw-title", "#daw-view"],
]) {
  test(`${route} muestra «no encontrada» sin cambiar la dirección`, async ({ page }) => {
    await page.goto(`/${route}`);
    await expect(page.locator(`${zone} [data-not-found]`)).toBeVisible();
    await expect(page.locator(title)).toContainText("No encontramos");
    expect(new URL(page.url()).hash).toBe(route);
    await expect(page.locator(zone).getByRole("link", { name: "¿Qué estudio ahora?" })).toBeVisible();
  });
}

test("la raíz sigue abriendo la portada", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/#\/portada$/);
});

test("sin lessons.json, la portada y «¿Qué estudio ahora?» funcionan y el curso PCAP lo explica", async ({ page }) => {
  // AUD-010: antes, si fallaba lessons.json, no se registraba el enrutador y no funcionaba nada
  await page.route("**/data/lessons.json", (route) => route.abort());
  await page.goto("/#/aprender");
  await expect(page.locator("#learn-title")).toBeVisible();
  await page.goto("/#/inicio");
  await expect(page.locator("#notfound-title")).toHaveText("No se pudo cargar el contenido");
  await page.locator("#notfound-view").getByRole("link", { name: "Cursos de DAW" }).click();
  await expect(page).toHaveURL(/#\/daw$/);
  await expect(page.locator("#learn-title")).toBeVisible(); // la Preparación DAW no usa lessons.json
});

test("pestañas accesibles con teclado", async ({ page }) => {
  await openLesson(page, "variables");
  const theory = page.getByRole("tab", { name: "Teoría y Ejemplos" });
  await theory.focus();
  await page.keyboard.press("ArrowRight");
  const practice = page.getByRole("tab", { name: "Práctica y Ejercicio" });
  await expect(practice).toBeFocused();
  await expect(practice).toHaveAttribute("aria-selected", "true");
  await expect(page.locator("#panel-practice")).toBeVisible();
  await expect(page.locator("#panel-theory")).toBeHidden();
});

test("el anillo de progreso y su porcentaje están superpuestos", async ({ page }) => {
  // Regresión: un selector CSS roto descolocaba el anillo
  await openLesson(page, "variables");
  const ring = await page.locator(".progress__ring").boundingBox();
  const value = await page.locator(".progress__value").boundingBox();
  const centerX = value.x + value.width / 2;
  const centerY = value.y + value.height / 2;
  expect(centerX).toBeGreaterThan(ring.x);
  expect(centerX).toBeLessThan(ring.x + ring.width);
  expect(centerY).toBeGreaterThan(ring.y);
  expect(centerY).toBeLessThan(ring.y + ring.height);
});

test("marcar como completada actualiza el progreso y persiste", async ({ page }) => {
  await openLesson(page, "variables");
  await expect(page.locator(".lesson[data-slug=operadores]")).toHaveAttribute("data-status", "locked");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await expect(page.locator("#progress-value")).toHaveText("13%");
  await expect(page.locator("#progress")).toHaveAttribute("aria-valuenow", "13");

  await page.reload();
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
  await expect(page.locator(".lesson[data-slug=variables]")).toHaveAttribute("data-status", "active");
  await page.locator(".lesson[data-slug=tipos]").click();
  await expect(page.locator(".lesson[data-slug=variables]")).toHaveAttribute("data-status", "completed");
  await expect(page.locator(".module[data-module=fundamentos] .module__count")).toHaveText("1/8");
});

test("copiar y «Abrir en PyCharm» muestran la guía y la descarga", async ({ page, browserName }) => {
  const clipboard = await watchClipboard(page, browserName);
  await openLesson(page, "variables");
  const code = await page.locator(".code-block pre code").first().textContent();
  expect(code).toContain('nombre = "Carlos"');

  // «Copiar al portapapeles»: la escritura real sale bien y la web lo confirma
  await page.getByRole("button", { name: "Copiar al portapapeles" }).click();
  await expect(page.locator("#toast")).toHaveText("Código copiado al portapapeles");
  expect(await clipboard.writes()).toEqual([code]);
  if (clipboard.read) expect(await clipboard.read()).toBe(code); // lo que hay de verdad en el portapapeles

  // «Abrir en PyCharm»: vuelve a copiar el ejemplo y enseña la guía con la descarga
  await page.getByRole("button", { name: "Abrir en PyCharm" }).click();
  await expect(page.locator("#pycharm-hint")).toBeVisible();
  expect(await clipboard.writes()).toEqual([code, code]);
  if (clipboard.read) expect(await clipboard.read()).toBe(code);
  await expect(page.locator("#toast")).not.toContainText("No se pudo copiar");

  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Descargar variables.py" }).click();
  expect((await download).suggestedFilename()).toBe("variables.py");
});

test("la teoría enlaza sus fuentes", async ({ page }) => {
  await openLesson(page, "funciones");
  const sources = page.locator(".sources a");
  expect(await sources.count()).toBeGreaterThan(0);
  await expect(sources.first()).toHaveAttribute("href", /^https:\/\//);
  await expect(sources.first()).toHaveAttribute("rel", /noopener/);
});
