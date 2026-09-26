/* Configuración de despliegue del frontend.
   - apiUrl: URL del backend. Vacío = modo sin cuenta: todo funciona y el progreso se guarda
     solo en este navegador. En localhost se deja vacío y se usa http://127.0.0.1:8000.
   - contactEmail: a quién escribir si no hay recuperación de contraseña por email.
   - pyodideUrl (opcional): carpeta propia de Pyodide; por defecto, el CDN oficial (jsDelivr).
   Los valores ya definidos antes de cargar este archivo (por ejemplo, en los tests) se respetan. */
window.PLD_CONFIG = Object.assign(
  {
    apiUrl: ["localhost", "127.0.0.1"].includes(location.hostname) ? "" : "https://pld-api.onrender.com",
    contactEmail: "mrabehfathiprofesional@gmail.com",
  },
  window.PLD_CONFIG,
);
