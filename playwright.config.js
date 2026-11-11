// Tests end-to-end: levantan el frontend (puerto 5500) y el backend real (puerto 8000).
// Requisitos: dependencias del backend instaladas (pip install -r backend/requirements-dev.txt).
// Ejecutar: npm run test:e2e
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  // En CI se reintenta una vez para guardar la traza del fallo, pero una prueba que solo pasa al
  // reintentar («flaky») hace fallar el trabajo: los reintentos diagnostican, no esconden fallos
  retries: process.env.CI ? 1 : 0,
  failOnFlakyTests: Boolean(process.env.CI),
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: "http://localhost:5500",
    // La web es en español: un navegador en otro idioma vería el aviso para cambiar a inglés
    locale: "es-ES",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    // Safari (EVO-13): solo con PW_WEBKIT=1, que es como lo lanza el trabajo «webkit» de CI
    ...(process.env.PW_WEBKIT ? [{ name: "webkit", use: { ...devices["Desktop Safari"] } }] : []),
  ],
  webServer: [
    {
      command: "python e2e/serve_frontend.py 5500",
      url: "http://localhost:5500/index.html",
      reuseExistingServer: !process.env.CI,
    },
    {
      command: "python ../e2e/start_backend.py",
      cwd: "backend",
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
});
