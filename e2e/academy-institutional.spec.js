const { test, expect } = require("./fixtures");

test.describe("PLD ACADEMY institutional workspace MVP", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/#/academy");
    await expect(page.locator("#academy-view")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Buenos días" })).toBeVisible();
  });

  test("opens the public Academy landing and enters the demo", async ({ page }) => {
    await page.goto("/#/academy-info");
    await expect(page.getByRole("heading", { name: /La programación, organizada para todo el centro/ })).toBeVisible();
    await page.getByRole("link", { name: "Explorar demo del centro" }).click();
    await expect(page.getByRole("heading", { name: "Buenos días" })).toBeVisible();
  });

  test("shows the center workspace and group overview", async ({ page }) => {
    await expect(page.getByText("Centro de Formación PLD", { exact: true })).toBeVisible();
    await expect(page.getByText("1.º DAW A", { exact: true }).first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Grupos" })).toBeVisible();
  });

  test("walks through the guided commercial demo", async ({ page }) => {
    await page.getByRole("button", { name: "Guía de demo" }).click();
    await expect(page.getByRole("heading", { name: "Una vista para dirección" })).toBeVisible();
    await page.getByRole("button", { name: "Siguiente" }).click();
    await expect(page.getByRole("heading", { name: "Organiza las clases" })).toBeVisible();
    await page.getByRole("button", { name: "Siguiente" }).click();
    await expect(page.getByRole("heading", { name: "Publica actividades" })).toBeVisible();
    await page.getByRole("button", { name: "Siguiente" }).click();
    await expect(page.getByRole("heading", { name: "Seguimiento del progreso" })).toBeVisible();
    await page.getByRole("button", { name: "Siguiente" }).click();
    await expect(page.getByRole("heading", { name: "Vista del alumnado" })).toBeVisible();
    await page.getByRole("button", { name: "Terminar" }).click();
    await expect(page.locator(".academy-tour")).not.toBeVisible();
  });

  test("creates a group and persists it in the demo workspace", async ({ page }) => {
    await page.getByRole("button", { name: "Grupos" }).click();
    await expect(page.getByRole("heading", { name: "Grupos" })).toBeVisible();
    await page.getByRole("button", { name: "＋ Crear grupo" }).click();
    await page.getByRole("heading", { name: "Crear grupo" }).waitFor();
    await page.locator("#academy-group-form [name=name]").fill("2.º DAW B");
    await page.locator("#academy-group-form [name=program]").fill("Desarrollo Web");
    await page.locator("#academy-group-form [name=subject]").fill("Entorno cliente");
    await page.locator("#academy-group-form [name=teacher]").fill("Docente Demo");
    await page.locator("#academy-group-form [name=students]").fill("22");
    await page.getByRole("button", { name: "Crear grupo", exact: true }).click();
    await expect(page.getByText("2.º DAW B", { exact: true })).toBeVisible();
    await page.reload();
    await page.getByRole("link", { name: /PLD ACADEMY/ }).click();
    await expect(page.getByRole("heading", { name: /La programación, organizada para todo el centro/ })).toBeVisible();
    await page.getByRole("link", { name: "Explorar demo del centro" }).click();
    await expect(page.getByRole("heading", { name: "Buenos días" })).toBeVisible();
    await page.getByRole("button", { name: "Grupos" }).click();
    await expect(page.getByText("2.º DAW B", { exact: true })).toBeVisible();
  });


  test("escapes hostile values restored from demo storage in every role view", async ({ page }) => {
    const hostile = '<img src=x onerror="window.__academyXss=1">';
    await page.addInitScript((value) => {
      localStorage.setItem("pld:academy:institutional-demo:v1", JSON.stringify({
        organization: { name: "Test Center", type: "Demo", academicYear: "2026" },
        groups: [{ id: "g-x", name: "Test Group", program: "DAW", subject: "Programming", teacher: "Teacher", students: value }],
        assignments: [{ id: "a-x", title: "Test Activity", groupId: "g-x", type: "Practice", due: "", completed: value, total: "1", status: "published" }],
        activityLog: []
      }));
    }, hostile);
    await page.goto("/#/academy");
    await expect(page.locator("#academy-view img")).toHaveCount(0);
    await expect(page.locator("#academy-view")).toContainText(hostile);
    await page.getByRole("button", { name: "Grupos" }).click();
    await page.locator("#academy-role").selectOption("teacher");
    await expect(page.locator("#academy-view img")).toHaveCount(0);
    await page.getByRole("button", { name: "Actividades" }).click();
    await expect(page.locator("#academy-view img")).toHaveCount(0);
    await page.locator("#academy-role").selectOption("student");
    await expect(page.locator("#academy-view img")).toHaveCount(0);
    expect(await page.evaluate(() => window.__academyXss)).toBeUndefined();
  });

  test("creates an activity and switches to teacher/student preview", async ({ page }) => {
    await page.getByRole("button", { name: "＋ Crear actividad" }).click();
    await page.locator("#academy-assignment-form [name=title]").fill("Repaso de funciones");
    await page.locator("#academy-assignment-form [name=groupId]").selectOption("g-dam1");
    await page.locator("#academy-assignment-form [name=type]").selectOption("Práctica");
    await page.locator("#academy-assignment-form [name=due]").fill("2026-12-08");
    await page.getByRole("button", { name: "Guardar actividad" }).click();
    await expect(page.getByText("Repaso de funciones", { exact: true })).toBeVisible();
    await page.locator("#academy-role").selectOption("teacher");
    await expect(page.getByRole("heading", { name: "Mis clases" })).toBeVisible();
    await page.locator("#academy-role").selectOption("student");
    await expect(page.getByRole("heading", { name: "Mi aprendizaje" })).toBeVisible();
    await expect(page.getByText("Repaso de funciones", { exact: true })).toBeVisible();
  });
});
