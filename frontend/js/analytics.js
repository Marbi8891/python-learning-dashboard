/* Analítica opcional sin cookies (GoatCounter). Solo se activa si config.js define `goatcounter`.
   Cuenta visitas por página (la app usa rutas con #) y respeta «No rastrear» y Global Privacy Control.
   Nunca envía lo que va tras «?» en la ruta: ahí viaja, por ejemplo, el token de restablecer la
   contraseña (ADR-0022). */
(function () {
  var code = (window.PLD_CONFIG || {}).goatcounter;
  var local = ["localhost", "127.0.0.1"].indexOf(location.hostname) !== -1;
  if (!code || local || navigator.doNotTrack === "1" || navigator.globalPrivacyControl) return;

  window.goatcounter = { no_onload: true };
  var script = document.createElement("script");
  script.async = true;
  script.src = "https://gc.zgo.at/count.js";
  script.dataset.goatcounter = "https://" + code + ".goatcounter.com/count";
  script.onload = function () {
    var count = function () {
      window.goatcounter.count({ path: location.pathname + location.hash.split("?")[0] });
    };
    count();
    window.addEventListener("hashchange", count);
  };
  document.head.appendChild(script);
})();
