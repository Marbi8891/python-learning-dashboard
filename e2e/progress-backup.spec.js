const fs = require("node:fs");
const { test, expect } = require("./fixtures");

// Copia de seguridad del progreso sin cuenta: exportar, borrar el navegador e importar (se fusiona).
test("exporta el progreso, lo importa en un navegador vacío y lo fusiona sin borrar nada", async ({ page }, testInfo) => {
  await page.addInitScript(() => {
    if (sessionStorage.getItem("e2e-seeded")) return;
    sessionStorage.setItem("e2e-seeded", "1");
    localStorage.setItem("pld:completed", JSON.stringify(["variables", "bucles"]));
    localStorage.setItem("pld:game", JSON.stringify({ days: ["2026-10-20"], read: ["variables"] }));
  });
  await page.goto("/#/perfil");
  const exportButton = page.getByRole("button", { name: "Exportar mi progreso" });
  await expect(exportButton).toBeVisible();
  const [download] = await Promise.all([page.waitForEvent("download"), exportButton.click()]);
  expect(download.suggestedFilename()).toMatch(/^progreso-python-learning-\d{4}-\d{2}-\d{2}\.json$/);
  const path = testInfo.outputPath("progreso.json");
  await download.saveAs(path);
  const file = JSON.parse(fs.readFileSync(path, "utf8"));
  expect(file).toMatchObject({ format: "pld-progress", version: 1 });
  expect(file.data.completed.sort()).toEqual(["bucles", "variables"]);

  // Otro navegador: solo tiene una lección distinta
  await page.evaluate(() => {
    localStorage.clear();
    localStorage.setItem("pld:completed", JSON.stringify(["funciones"]));
  });
  await page.reload();
  await page.getByLabel(/Importar una copia/).setInputFiles(path);
  await expect(page.getByText(/Progreso importado y fusionado/)).toBeVisible();
  const completed = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:completed")).sort());
  expect(completed).toEqual(["bucles", "funciones", "variables"]);
});

test("un archivo que no es una copia del progreso se rechaza con un mensaje accesible", async ({ page }) => {
  await page.goto("/#/perfil");
  await page.getByLabel(/Importar una copia/).setInputFiles({ name: "otro.json", mimeType: "application/json", buffer: Buffer.from('{"hola": 1}') });
  await expect(page.locator("#progress-import-message")).toHaveText(/no es una copia del progreso/);
  await expect(page.locator("#progress-import-message")).toHaveAttribute("role", "status");
});
