// Tests end-to-end: levantan el frontend (puerto 5500) y el backend real (puerto 8000).
// Requisitos: dependencias del backend instaladas (pip install -r backend/requirements-dev.txt).
// Ejecutar: npm run test:e2e
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: "http://localhost:5500",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "python -m http.server 5500 --directory frontend",
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
