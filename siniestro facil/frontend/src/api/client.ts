import type { ApiError, CrearSiniestro, Siniestro } from "../types";

const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "");

export class ApiClientError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly detail?: ApiError,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  accessToken?: string,
): Promise<T> {
  if (!baseUrl) {
    throw new ApiClientError(
      "La conexión con el servicio todavía no está configurada.",
      0,
    );
  }

  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");

  if (init.body) {
    headers.set("Content-Type", "application/json");
  }

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(`${baseUrl}${path}`, { ...init, headers });
  const body = await response.json().catch(() => undefined);

  if (!response.ok) {
    const detail = body as ApiError | undefined;
    throw new ApiClientError(
      detail?.mensaje ?? "No fue posible completar la solicitud.",
      response.status,
      detail,
    );
  }

  return body as T;
}

export function crearSiniestro(
  payload: CrearSiniestro,
  accessToken?: string,
): Promise<Siniestro> {
  return request<Siniestro>(
    "/siniestros",
    {
      method: "POST",
      headers: { "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify(payload),
    },
    accessToken,
  );
}

export function obtenerSiniestro(
  siniestroId: number,
  accessToken?: string,
): Promise<Siniestro> {
  return request<Siniestro>(`/siniestros/${siniestroId}`, {}, accessToken);
}
