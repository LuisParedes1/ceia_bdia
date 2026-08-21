export type Session = {
  user_id: string;
  tenant_id: string;
  tenant_name: string;
  role: "admin" | "member" | "viewer";
  capabilities: string[];
};

const baseUrl = import.meta.env.VITE_API_URL ?? "/api";
const csrf = () =>
  document.cookie
    .split("; ")
    .find((part) => part.startsWith("csrf_token="))
    ?.split("=")[1];

const legacyMessages: Record<string, string> = {
  "authentication required": "Se requiere autenticación.",
  "CSRF validation failed": "Falló la validación de seguridad de la solicitud.",
  "select a tenant first": "Primero seleccioná un espacio de trabajo.",
  "role is not permitted": "Tu rol no tiene permiso para realizar esta acción.",
  "email is already registered": "El correo electrónico ya está registrado.",
  "invalid credentials":
    "El correo electrónico o la contraseña no son válidos.",
  "an active tenant membership is required":
    "Se requiere una membresía activa en un espacio de trabajo.",
  "invalid or expired recovery token":
    "El código de recuperación no es válido o venció.",
  "role must be admin, member, or viewer":
    "El rol debe ser administración, integrante o consulta.",
  "user is already attached to another tenant":
    "La persona ya pertenece a otro espacio de trabajo.",
};

const statusMessages: Record<number, string> = {
  400: "La solicitud no es válida.",
  401: "Se requiere autenticación.",
  403: "No tenés permiso para realizar esta acción.",
  404: "No se encontró el recurso solicitado.",
  409: "No se pudo completar la solicitud por un conflicto.",
  422: "Los datos enviados no son válidos.",
  429: "Se realizaron demasiadas solicitudes. Intentá nuevamente más tarde.",
};

const genericMessage = "No se pudo completar la solicitud.";
const internalError = "Ocurrió un error interno. Intentá nuevamente más tarde.";

function statusMessage(status: number): string {
  return status >= 500
    ? internalError
    : (statusMessages[status] ?? genericMessage);
}

type ValidationIssue = { loc?: unknown; type?: unknown; msg?: unknown };

function validationMessage(issue: ValidationIssue): string {
  const location = Array.isArray(issue.loc) ? issue.loc : [];
  const field = location.at(-1);
  const type = typeof issue.type === "string" ? issue.type : "";
  if (type === "missing") return "Este campo es obligatorio.";
  if (field === "email") return "Ingresá un correo electrónico válido.";
  if (field === "password" || type === "string_too_short") {
    return "La contraseña debe tener al menos 8 caracteres.";
  }
  return "Los datos enviados no son válidos.";
}

export function apiErrorMessage(
  detail: unknown,
  fallback = genericMessage,
): string {
  if (typeof detail === "string") {
    if (legacyMessages[detail]) return legacyMessages[detail];
    if (
      detail.startsWith("Se ") ||
      detail.startsWith("Falló ") ||
      detail.startsWith("Primero ") ||
      detail.startsWith("Tu ") ||
      detail.startsWith("El ") ||
      detail.startsWith("La ") ||
      detail.startsWith("Los ") ||
      detail.startsWith("No ") ||
      detail.startsWith("Ocurrió ")
    )
      return detail;
    return fallback;
  }
  if (Array.isArray(detail)) {
    const issue = detail.find(
      (item): item is ValidationIssue =>
        typeof item === "object" && item !== null,
    );
    if (issue) return validationMessage(issue);
  }
  return fallback;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = init.method ?? "GET";
  const headers: Record<string, string> = {};
  new Headers(init.headers).forEach((value, key) => {
    headers[key] = value;
  });
  if (init.body) headers["content-type"] = "application/json";
  if (method !== "GET") headers["x-csrf-token"] = csrf() ?? "";

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...init,
      credentials: "include",
      headers,
    });
  } catch {
    throw new Error("La API no está disponible.");
  }

  if (!response.ok) {
    const fallback = statusMessage(response.status);
    let detail: unknown;
    try {
      detail = ((await response.json()) as { detail?: unknown }).detail;
    } catch {
      // Non-JSON error responses use only the trusted status fallback.
    }
    throw new Error(apiErrorMessage(detail, fallback));
  }
  return response.json() as Promise<T>;
}

export const getSession = () => request<Session>("/auth/session");
export const login = (email: string, password: string) =>
  request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
export const register = (
  email: string,
  password: string,
  tenant_name: string,
) =>
  request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, tenant_name }),
  });
export const requestRecovery = (email: string) =>
  request("/auth/recovery/request", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
export const confirmRecovery = (token: string, password: string) =>
  request("/auth/recovery/confirm", {
    method: "POST",
    body: JSON.stringify({ token, password }),
  });
export const logout = () => request("/auth/logout", { method: "POST" });
export type MemberRole = "admin" | "member" | "viewer";
export type MemberStatus = "active" | "inactive";
export type Member = {
  user_id: string;
  email: string;
  role: MemberRole;
  status: MemberStatus;
  password_setup_required: boolean;
};
export type MembersQuery = {
  page: number;
  per_page: number;
  search: string;
  role: "" | MemberRole;
  status: "" | MemberStatus;
  sort: string;
};
export type MembersResponse = {
  items: Member[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
};
export const getMembers = (query: MembersQuery) => {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query))
    params.set(key, String(value));
  return request<MembersResponse>(`/members?${params.toString()}`);
};
export const createMember = (email: string, role: MemberRole) =>
  request("/members", {
    method: "POST",
    body: JSON.stringify({ email, role }),
  });
