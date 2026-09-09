export type EstadoSiniestro =
  | "reportado"
  | "validando_cobertura"
  | "asistencia_coordinada"
  | "evidencia_pendiente"
  | "en_evaluacion"
  | "inspeccion_programada"
  | "presupuesto_recibido"
  | "autorizado"
  | "observado"
  | "rechazado"
  | "en_reparacion"
  | "listo_para_entrega"
  | "indemnizado"
  | "cerrado";

export interface CrearSiniestro {
  numeroPoliza?: string;
  numeroDocumento?: string;
  placa: string;
  fechaEvento: string;
  ubicacionEvento: string;
  tipoEvento: string;
  medioContacto: string;
}

export interface Siniestro {
  id: number;
  estadoActual: EstadoSiniestro;
  fechaEvento: string;
  tipoEvento: string;
  siguientePaso?: string;
}

export interface ApiError {
  codigo: string;
  mensaje: string;
  correlationId: string;
  detalles?: string[];
}

export interface EventoLineaTiempo {
  id: number;
  tipoEvento: string;
  actorId?: string | null;
  fecha: string;
  detalle: Record<string, unknown>;
  nivelDetalle: string;
}

export interface LineaTiempoSiniestro {
  siniestroId: number;
  nivelDetalle: string;
  eventos: EventoLineaTiempo[];
  siguienteCursor?: number | null;
}

export type TipoContenidoEvidencia =
  | "image/jpeg"
  | "image/png"
  | "application/pdf";

export interface SolicitudCargaEvidencia {
  nombreArchivo: string;
  tipoContenido: TipoContenidoEvidencia;
  tamanoBytes: number;
}

export interface CargaEvidenciaAutorizada {
  urlCarga: string;
  contenidoOriginalUri: string;
  expiraEn: string;
  tipoContenido: TipoContenidoEvidencia;
}

export interface EvidenciaRegistrada {
  id: number;
  siniestroId: number;
  tipoEvidencia: string;
  contenidoOriginalUri: string;
  hash: string;
  fechaRecepcion: string;
  versionDerivadaDe?: number | null;
}
