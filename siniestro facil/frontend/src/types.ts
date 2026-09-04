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
