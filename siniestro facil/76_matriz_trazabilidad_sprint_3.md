# Matriz de trazabilidad — Sprint 3 Backend

| Incremento | HU | Criterio verificable | RF | CU | Datos / plataforma |
|---|---|---|---|---|---|
| S3-BE-01 | HU-07 | Registrar solicitud y resultado de asistencia | RF-06, RF-18 | CU-02 | asistencia, proveedor, evento_linea_tiempo |
| S3-BE-01 | HU-21 | Registrar aceptación, rechazo o falta de respuesta | RF-17 | CU-02 | asistencia, comunicacion |
| S3-BE-02 | HU-12 | Reasignar conservando responsable, fechas y razón | RF-12, RF-18 | CU-04 | asignacion_siniestro |
| S3-BE-02 | HU-15 | Reasignar sin bloquear al asegurado | RF-17 | CU-02, CU-04 | proveedor, asistencia |
| S3-BE-03 | HU-15 | Reintentar o escalar ante falta de respuesta | RF-17, RF-32 | CU-02 | Pub/Sub, outbox, dead letter |
| S3-BE-03 | HU-21 | Procesar la respuesta de manera idempotente | RF-17, RF-18 | CU-02 | consumidor idempotente, auditoría |

## Fuentes

- `01_historias_usuario.md`: HU-07, HU-12, HU-15 y HU-21.
- `02_criterios_aceptacion.md`: resultados de asistencia, respuestas e historial.
- `03_requerimientos_funcionales.md`: RF-06, RF-12, RF-17, RF-18 y RF-32.
- `05_casos_uso.md`: CU-02 y CU-04.
- `11_arquitectura_backend.md`: persistencia previa, reintento e idempotencia.
- `18_arquitectura_gcp.md`: Pub/Sub, Cloud Tasks y dead-letter topics.
- `16_backlog_inicial_backend.md`: resultado esperado del Sprint 3.

## Vacíos controlados

- El proveedor externo no está seleccionado.
- Los SLA simulados del piloto no están aprobados.
- El número de reintentos, backoff, timeout y umbral de escalamiento no están definidos.
