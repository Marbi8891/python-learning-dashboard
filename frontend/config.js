

/* Configuración de despliegue del frontend.
   - apiUrl: URL del backend.
   - contactEmail: correo de contacto.
   - googleClientId: ID público del cliente OAuth de Google.
   - goatcounter: código de analítica.
   - serviceWorker: funcionamiento sin conexión.
*/
window.PLD_CONFIG = Object.assign(
  {
    apiUrl: ["localhost", "127.0.0.1"].includes(location.hostname)
      ? ""
      : "https://pld-api.onrender.com",
    contactEmail: "mrabehfathiprofesional@gmail.com",
    googleClientId: "1077939677647-34gdevneop8c6019g80l3lop6ubdfb41.apps.googleusercontent.com",
    goatcounter: "",
    serviceWorker: !["localhost", "127.0.0.1"].includes(location.hostname),
  },
  window.PLD_CONFIG,
);
