# Estado Sprint 3 — Backend Siniestro Fácil

## Estado general

- Avance: **15% — fundaciones validadas**.
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

- **S3-DEC-01 — APROBADA:** usar temporalmente un adaptador simulado de proveedor.
- **S3-DEC-02 — APROBADA:** 3 intentos; esperas de 30 s, 2 min y 5 min; timeout de 10 s; escalamiento tras el tercer fallo.

## Restricciones

- El adaptador simulado aprobado no sustituye la selección futura de un proveedor real.
- No se crean tópicos, suscripciones ni recursos GCP sin pasos explícitos y validación previa.
- No se inventan SLA, timeouts ni cantidades de reintentos.
- No se fusiona el PR de Sprint 3 sin autorización explícita del Product Owner.

## Avance de fundaciones

- Dominio y transiciones de asistencia definidos.
- Política de reintentos configurable y sin valores predeterminados.
- Contratos de aplicación y repositorio definidos.
- Adaptador externo deshabilitado hasta aprobar S3-DEC-01.
- Transporte idempotente en memoria para pruebas; no es Pub/Sub real.
- Diez pruebas nuevas publicadas.
- Validación Cloud Shell: **140/140 pruebas aprobadas**.
- Alembic: `20260901_01 (head)`.
- Evidencia: `77_evidencia_fundaciones_sprint_3_cloudshell.md`.
- Estado de fundaciones: **completado**.

## Registro de aprobación

- S3-DEC-01 y S3-DEC-02 aprobadas el 2 de septiembre de 2026.
- Evidencia: `78_registro_aprobacion_s3_decisiones.md`.
- S3-BE-01, S3-BE-02 y S3-BE-03 quedan habilitados para desarrollo.
