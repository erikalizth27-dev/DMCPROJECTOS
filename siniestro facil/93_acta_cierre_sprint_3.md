# Acta de cierre Sprint 3 — Backend Siniestro Fácil

## Estado

Sprint 3 cerrado al **100%** el 2 de septiembre de 2026.

## Objetivo alcanzado

Implementar la coordinación de asistencia del siniestro, registrar respuestas y reasignaciones de proveedores y tolerar fallos mediante procesamiento asíncrono, idempotente y auditable.

## Incrementos completados

### S3-BE-01 — Solicitar y consultar asistencia

- Solicitud vinculada al siniestro.
- Adaptador simulado de proveedor.
- API, RBAC e idempotencia.
- Persistencia y auditoría atómicas.
- Consulta con control de alcance.
- Validación PostgreSQL con rollback.

### S3-BE-02 — Registrar respuesta y reasignar

- Respuestas aceptada, rechazada y sin respuesta.
- Reasignación con historial preservado.
- Control optimista de intento.
- Proveedor anterior, proveedor nuevo y motivo auditados.
- Límite de tres intentos.
- Validación PostgreSQL con rollback.

### S3-BE-03 — Reintentar y escalar

- Política 30/120/300 segundos.
- Timeout funcional de 10 segundos.
- Escalamiento después del tercer fallo.
- Outbox PostgreSQL con `SKIP LOCKED`.
- Publicación Pub/Sub idempotente.
- Dead letter configurado.
- Cloud Tasks para programación diferida.
- Validación real y limpieza de recursos sintéticos.

## Evidencia técnica

- Regresión final: **201/201 pruebas aprobadas**.
- Alembic: `20260902_02 (head)`.
- Cloud SQL: validado.
- Pub/Sub: publicación y consumo reales aprobados.
- Cloud Tasks: creación, consulta y eliminación aprobadas.
- Auditoría, idempotencia, concurrencia y rollback aprobados.
- Evidencia integral: `92_evidencia_validacion_integral_sprint_3.md`.

## Recursos GCP aprobados

- Topic: `siniestro-asistencia-solicitudes`.
- Suscripción: `siniestro-asistencia-worker`.
- Dead letter topic: `siniestro-asistencia-dead-letter`.
- Suscripción dead letter: `siniestro-asistencia-dead-letter-monitor`.
- Cola: `siniestro-asistencia-reintentos`.
- Región: `us-central1`.

## Decisiones

- S3-DEC-01, S3-DEC-02 y S3-DEC-03: aprobadas y aplicadas.
- El dispatch deadline técnico de Cloud Tasks es 15 segundos por restricción de GCP; el timeout funcional permanece en 10 segundos.

## Alcance diferido

- Proveedor externo real.
- Worker desplegado productivamente.
- CI/CD.
- Observabilidad productiva.
- Operación productiva y alertamiento.
- Elementos funcionales de Sprint 4 y posteriores.

## Condición de fusión

La rama `agent/sprint-3-backend` queda lista para revisión. Su fusión en `main` requiere autorización explícita del Product Owner.
