/* Antes de pintar la página (script clásico y síncrono, sin parpadeo):
   - tema y tamaño de letra guardados;
   - defensa contra clickjacking: GitHub Pages no permite la cabecera X-Frame-Options ni
     frame-ancestors en la CSP de <meta>, así que si otra web nos mete en un marco no se muestra
     nada (ADR-0022). */
(function () {
  if (window.top !== window.self) {
    document.documentElement.style.display = "none";
    return;
  }
  var prefs = {};
  try {
    prefs = JSON.parse(localStorage.getItem("pld:prefs")) || {};
  } catch (e) {
    // sin almacenamiento: tema automático
  }
  var theme = prefs.theme || "auto";
  if (theme === "auto") theme = matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  document.documentElement.dataset.theme = theme;
  document.documentElement.dataset.font = prefs.font || "normal";
})();
