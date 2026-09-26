/* Configuración de despliegue del frontend.
   - apiUrl: URL del backend (por ejemplo "https://pld-api.onrender.com").
     Vacío = modo sin cuenta: todo funciona y el progreso se guarda solo en este navegador.
     En localhost se usa automáticamente http://127.0.0.1:8000.
   - pyodideUrl (opcional): carpeta propia de Pyodide; por defecto, el CDN oficial (jsDelivr).
   Los valores ya definidos antes de cargar este archivo (por ejemplo, en los tests) se respetan. */
window.PLD_CONFIG = Object.assign(
  {
    apiUrl: "",
  },
  window.PLD_CONFIG,
);
