// Pruebas de navegador del entorno QA (Web Workers, carga de módulos, Pyodide).
// Solo necesitan la web estática: no arrancan el backend ni tocan servicios externos.
// Ejecutar: npm run test:frontend:browser   (o npx playwright test -c tests/frontend)
const path = require("node:path");
const { defineConfig, devices } = require("@playwright/test");

const PORT = Number(process.env.QA_FRONTEND_PORT || 5510);

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: "*.spec.js",
  timeout: 60_000,
  retries: 0, // una prueba inestable tiene que fallar, no esconderse con reintentos
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  outputDir: path.join(__dirname, "..", "..", "test-results", "qa-frontend"),
  use: { baseURL: `http://localhost:${PORT}`, locale: "es-ES", trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `python e2e/serve_frontend.py ${PORT}`,
    cwd: path.join(__dirname, "..", ".."),
    url: `http://localhost:${PORT}/index.html`,
    reuseExistingServer: !process.env.CI,
    stdout: "ignore", // el registro de peticiones del servidor estático no aporta nada
  },
});
