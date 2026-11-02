/* Antes de pintar la página (script clásico y síncrono, sin parpadeo):
   - tema, tamaño de letra y preferencias de lectura guardados;
   - defensa contra clickjacking: GitHub Pages no permite la cabecera X-Frame-Options ni
     frame-ancestors en la CSP de <meta>, así que si otra web nos mete en un marco no se muestra
     nada. */
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
  if (prefs.spacing) document.documentElement.dataset.spacing = "amplio";
  if (prefs.contrast) document.documentElement.dataset.contrast = "alto";
  if (prefs.motion) document.documentElement.dataset.motion = "reducido";
  // Otro idioma: se oculta la página hasta traducirla (i18n.js), como mucho 2 s
  if (prefs.lang && prefs.lang !== "es") {
    document.documentElement.lang = prefs.lang;
    document.documentElement.dataset.i18nPending = "";
    setTimeout(function () {
      delete document.documentElement.dataset.i18nPending;
    }, 2000);
  }
})();
