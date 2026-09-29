/* Service worker: la web funciona sin conexión después de la primera visita (ver ADR-0010).
   - Archivos de la web: primero la red (siempre la versión nueva) y, sin conexión, la copia guardada.
   - Pyodide (Python en el navegador): primero la copia guardada; sus URL llevan la versión y no cambian.
   - API del backend: nunca se guarda (datos personales y siempre actuales). */

const VERSION = "v3";
const SITE_CACHE = `pld-site-${VERSION}`;
const PYODIDE_CACHE = "pld-pyodide"; // se conserva entre versiones: son ~10 MB inmutables
const SHELL = ["./", "index.html", "config.js", "js/analytics.js", "manifest.webmanifest", "favicon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(SITE_CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SITE_CACHE && k !== PYODIDE_CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

async function networkFirst(request) {
  const cache = await caches.open(SITE_CACHE);
  try {
    const response = await fetch(request);
    if (response.ok) cache.put(request, response.clone());
    return response;
  } catch (error) {
    const cached = await cache.match(request, { ignoreSearch: true });
    if (cached) return cached;
    if (request.mode === "navigate") return (await cache.match("index.html")) ?? Response.error();
    throw error;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(PYODIDE_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) cache.put(request, response.clone());
  return response;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.pathname.startsWith("/api/") || url.pathname.includes("/api/")) return; // API: sin caché
  if (url.origin === self.location.origin) {
    event.respondWith(networkFirst(request));
  } else if (url.pathname.includes("pyodide")) {
    event.respondWith(cacheFirst(request));
  }
});
