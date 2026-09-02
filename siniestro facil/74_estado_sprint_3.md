# Estado Sprint 3 — Backend Siniestro Fácil

## Estado general

- Avance: **5% — rama y alcance trazable preparados**.
- Rama: `agent/sprint-3-backend`.
- Punto de partida: `main` en `d2b4b9f06dd9738ba47e8744d32f2277e2b3bbd1`.
- Duración de referencia: 2 semanas.
- Objetivo: asistencia, proveedores, reintentos y procesamiento asíncrono con Pub/Sub.
- Línea base heredada: **130/130 pruebas aprobadas** y Alembic `20260901_01 (head)`.

## Distribución porcentual

| Fase | Resultado | Peso | Acumulado |
|---|---|---:|---:|
| Preparación | Rama, alcance, trazabilidad y decisiones | 5% | 5% |
| Fundaciones | Contratos de proveedor, persistencia y outbox | 10% | 15% |
| S3-BE-01 | Solicitar y consultar asistencia | 25% | 40% |
| S3-BE-02 | Respuesta del proveedor y reasignación | 20% | 60% |
| S3-BE-03 | Reintentos, escalamiento y Pub/Sub | 25% | 85% |
| Integración | PostgreSQL, Pub/Sub y pruebas integrales | 10% | 95% |
| Cierre | Evidencias, trazabilidad, acta y PR | 5% | 100% |

## Incrementos propuestos

- **S3-BE-01:** registrar una solicitud de asistencia vinculada al siniestro y consultar su estado.
- **S3-BE-02:** registrar respuesta aceptada, rechazada o sin respuesta; reasignar conservando historial y motivo.
- **S3-BE-03:** publicar el comando persistido, consumirlo idempotentemente y ejecutar reintento o escalamiento controlado.

## Decisiones pendientes

- **S3-DEC-01:** aprobar un adaptador simulado de proveedor mientras no exista proveedor externo seleccionado.
- **S3-DEC-02:** aprobar SLA y política de reintentos simulados únicamente para el piloto.

## Restricciones

- No se integra un proveedor real sin selección y credenciales autorizadas.
- No se crean tópicos, suscripciones ni recursos GCP sin pasos explícitos y validación previa.
- No se inventan SLA, timeouts ni cantidades de reintentos.
- No se fusiona el PR de Sprint 3 sin autorización explícita del Product Owner.
