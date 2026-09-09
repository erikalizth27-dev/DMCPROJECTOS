import type {
  ApiError,
  CargaEvidenciaAutorizada,
  CrearSiniestro,
  EvidenciaRegistrada,
  LineaTiempoSiniestro,
  Siniestro,
  SolicitudCargaEvidencia,
} from "../types";

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

export function obtenerLineaTiempo(
  siniestroId: number,
  accessToken?: string,
  despuesDe = 0,
  cantidad = 20,
): Promise<LineaTiempoSiniestro> {
  const query = new URLSearchParams({
    despuesDe: String(despuesDe),
    cantidad: String(cantidad),
  });
  return request<LineaTiempoSiniestro>(
    `/siniestros/${siniestroId}/linea-tiempo?${query}`,
    {},
    accessToken,
  );
}

export function solicitarCargaEvidencia(
  siniestroId: number,
  payload: SolicitudCargaEvidencia,
  accessToken: string,
): Promise<CargaEvidenciaAutorizada> {
  return request<CargaEvidenciaAutorizada>(
    `/siniestros/${siniestroId}/evidencias/url-carga`,
    { method: "POST", body: JSON.stringify(payload) },
    accessToken,
  );
}

export async function cargarArchivoEvidencia(
  autorizacion: CargaEvidenciaAutorizada,
  archivo: File,
): Promise<void> {
  const response = await fetch(autorizacion.urlCarga, {
    method: "PUT",
    headers: { "Content-Type": autorizacion.tipoContenido },
    body: archivo,
  });
  if (!response.ok) {
    throw new ApiClientError("No fue posible cargar el archivo.", response.status);
  }
}

export function registrarEvidencia(
  siniestroId: number,
  payload: {
    tipoEvidencia: string;
    contenidoOriginalUri: string;
    hash: string;
    fuente: string;
    metadatos: Record<string, unknown>;
  },
  accessToken: string,
): Promise<EvidenciaRegistrada> {
  return request<EvidenciaRegistrada>(
    `/siniestros/${siniestroId}/evidencias`,
    {
      method: "POST",
      headers: { "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify(payload),
    },
    accessToken,
  );
}
