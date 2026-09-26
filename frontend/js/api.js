/* Cliente de la API del backend. Sin API configurada, la app funciona en modo local. */

const config = window.PLD_CONFIG ?? {};
const isLocalhost = ["localhost", "127.0.0.1"].includes(location.hostname);

export const API_URL = (config.apiUrl || (isLocalhost ? "http://127.0.0.1:8000" : "")).replace(/\/+$/, "");
export const apiEnabled = Boolean(API_URL);

const TOKEN_KEY = "pld:token";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Sin almacenamiento (modo privado): la sesión dura hasta recargar la página.
  }
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

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { method, headers, body });
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
