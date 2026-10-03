/* Cliente de la API del backend. Sin API configurada, la app funciona en modo local. */

const config = window.PLD_CONFIG ?? {};
const isLocalhost = ["localhost", "127.0.0.1"].includes(location.hostname);

export const API_URL = (config.apiUrl || (isLocalhost ? "http://127.0.0.1:8000" : "")).replace(/\/+$/, "");
export const apiEnabled = Boolean(API_URL);
export const API_V1_PREFIX = "/api/v1";

// Security by default: el token de acceso solo vive en memoria JavaScript.
// No se persiste en localStorage/sessionStorage, porque cualquier XSS podría leerlo.
let accessToken = null;

/** Despierta el servidor (el plan gratuito se duerme sin uso) y lee sus capacidades.
    Se lanza al cargar la página para que el alumno no espere al iniciar sesión. */
export const serverInfo = apiEnabled
  ? fetch(`${API_URL}${API_V1_PREFIX}/health`)
      .then((response) => response.json())
      .catch(() => null)
  : Promise.resolve(null);

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export function getToken() {
  return accessToken;
}

export function setToken(token) {
  accessToken = typeof token === "string" && token.length > 0 ? token : null;
}

// Mensajes en español para los errores de validación (422) de la API
const FIELD_MESSAGES = {
  email: "El email no es válido",
  password: "La contraseña debe tener entre 8 y 128 caracteres",
  new_password: "La contraseña debe tener entre 8 y 128 caracteres",
  display_name: "Escribe tu nombre (máximo 80 caracteres)",
  accept_privacy: "Debes aceptar la política de privacidad",
  token: "El enlace no es válido",
};

function formatDetail(detail, status) {
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => FIELD_MESSAGES[item.loc?.at(-1)] ?? item.msg);
    return [...new Set(messages)].join(". ");
  }
  return typeof detail === "string" ? detail : `Error ${status}`;
}

/** Llama a la API. Lanza ApiError con un mensaje listo para mostrar. */
export async function request(method, path, { json, form, auth = true } = {}) {
  if (!apiEnabled) throw new ApiError(0, "No hay servidor configurado");
  const headers = {};
  let body;
  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  } else if (form) {
    body = new URLSearchParams(form);
  }
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  const apiPath =
    path === "/api" || path === "/api/"
      ? API_V1_PREFIX
      : path.startsWith("/api/v1/")
        ? path
        : path.startsWith("/api/")
          ? API_V1_PREFIX + path.slice(4)
          : path;

  let response;
  try {
    response = await fetch(`${API_URL}${apiPath}`, { method, headers, body });
  } catch {
    throw new ApiError(0, "No se pudo conectar con el servidor. Inténtalo de nuevo en unos segundos.");
  }

  if (response.status === 401 && auth && token) {
    setToken(null);
    window.dispatchEvent(new CustomEvent("pld:session-expired"));
  }
  if (!response.ok) {
    let detail = null;
    try {
      detail = (await response.json()).detail;
    } catch {
      // respuesta sin JSON
    }
    throw new ApiError(response.status, formatDetail(detail, response.status));
  }
  return response.status === 204 ? null : response.json();
}
