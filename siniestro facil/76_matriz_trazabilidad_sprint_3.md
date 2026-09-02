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

## Estado de cierre

| Incremento | Resultado | Evidencia principal |
|---|---|---|
| S3-BE-01 | Cumplido | `81_evidencia_final_s3_be_01_postgresql.md` |
| S3-BE-02 | Cumplido | `84_evidencia_final_s3_be_02_postgresql.md` |
| S3-BE-03 | Cumplido | `91_evidencia_final_s3_be_03_gcp.md` |
| Sprint 3 integral | Cumplido | `92_evidencia_validacion_integral_sprint_3.md` |

## Decisiones aplicadas

- S3-DEC-01: adaptador simulado de proveedores durante Sprint 3.
- S3-DEC-02: tres intentos, esperas 30/120/300 segundos, timeout funcional de 10 segundos y escalamiento tras el tercer fallo.
- S3-DEC-03: Pub/Sub para transporte y Cloud Tasks para programación diferida.
- Cloud Tasks usa un dispatch deadline técnico de 15 segundos por restricción de la plataforma; el timeout funcional del proveedor permanece en 10 segundos.

## Vacíos diferidos

- Selección e integración productiva con un proveedor real.
- Endpoint operativo desplegado para el worker de Cloud Tasks.
- CI/CD, observabilidad y operación productiva.

