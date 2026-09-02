# Estado Sprint 3 — Backend Siniestro Fácil

## Estado general

- Avance: **78% — fundación del outbox publicada, pendiente de validación**.
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
- **S3-DEC-03 — APROBADA:** Pub/Sub para transporte, Cloud Tasks para programación diferida y recursos nominales en `project-77c17016-86bc-4fc4-a97`.

## Restricciones

- El adaptador simulado aprobado no sustituye la selección futura de un proveedor real.
- Los recursos GCP aprobados se crean únicamente mediante comandos explícitos, privilegios mínimos y validación posterior.
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

- S3-DEC-01, S3-DEC-02 y S3-DEC-03 aprobadas el 2 de septiembre de 2026.
- Evidencias: `78_registro_aprobacion_s3_decisiones.md` y `86_registro_aprobacion_s3_dec_03.md`.
- S3-BE-01, S3-BE-02 y S3-BE-03 quedan habilitados para desarrollo.

## Avance de S3-BE-01

- S3-DEC-01 y S3-DEC-02 aplicadas.
- Adaptador simulado determinista habilitado.
- Servicio de solicitud de asistencia implementado.
- Consulta de asistencia con ocultamiento de recursos fuera de alcance.
- RBAC e idempotencia incorporados.
- Repetición idéntica evita un segundo despacho.
- Conflicto de clave con contenido diferente devuelve HTTP 409 en el contrato de aplicación.
- Diez pruebas nuevas publicadas.
- Validación Cloud Shell: **150/150 pruebas aprobadas**.
- Evidencia: `79_evidencia_primera_entrega_s3_be_01.md`.
- Pendiente: endpoint API, persistencia PostgreSQL, auditoría atómica y validación con rollback.

## Segunda entrega de S3-BE-01

- Endpoints POST y GET de asistencia implementados.
- Repositorio PostgreSQL con alcance por identidad.
- Solicitud, auditoría e idempotencia persistidas en una transacción.
- Estado de envío, referencia externa y auditoría actualizados atómicamente.
- Modelos Asistencia y SolicitudAsistenciaIdempotente añadidos.
- Migración Alembic `20260902_01` añadida y todavía no aplicada.
- Ocho pruebas nuevas publicadas.
- Validación Cloud Shell: **158/158 pruebas aprobadas**.
- Alembic heads: `20260902_01 (head)`.
- Evidencia: `80_evidencia_segunda_entrega_s3_be_01.md`.
- Próximo paso: aplicar la migración con identidad administrativa y validar rollback.

## Cierre de S3-BE-01

- Migración `20260902_01` aplicada.
- Runtime con privilegios mínimos.
- Validación PostgreSQL y rollback aprobados.
- Persistencia, referencia externa y dos eventos de auditoría comprobados.
- Repetición idempotente sin segundo despacho.
- Conflicto de contenido HTTP 409 comprobado.
- Limpieza sin registros residuales.
- Evidencia: `81_evidencia_final_s3_be_01_postgresql.md`.
- Estado del incremento: **completado**.

## Primera entrega de S3-BE-02

- Respuestas aceptada, rechazada y sin respuesta implementadas.
- Transiciones terminales protegidas.
- Conflicto HTTP 409 ante intento esperado desactualizado.
- Reasignación permitida solamente tras rechazo o falta de respuesta.
- Proveedor nuevo obligatorio y diferente.
- Historial preservado mediante una nueva solicitud.
- Número de intento incrementado.
- Límite de tres intentos aplicado según S3-DEC-02.
- Diez pruebas nuevas publicadas.
- Validación Cloud Shell: **168/168 pruebas aprobadas**.
- Alembic: `20260902_01 (head)`.
- Evidencia: `82_evidencia_primera_entrega_s3_be_02.md`.
- Pendiente: API, repositorio PostgreSQL, auditoría y rollback.

## Segunda entrega de S3-BE-02

- Endpoint de respuesta del proveedor implementado.
- Endpoint de reasignación implementado.
- Bloqueo de fila `FOR UPDATE` aplicado.
- Intento esperado validado dentro de la transacción.
- Respuesta y auditoría persistidas atómicamente.
- Reasignación crea una solicitud nueva y conserva la anterior.
- Proveedor nuevo validado contra PostgreSQL.
- Auditoría conserva proveedores anterior/nuevo, intento y motivo.
- Siete pruebas API/repositorio nuevas publicadas.
- Validación Cloud Shell: **175/175 pruebas aprobadas**.
- Alembic: `20260902_01 (head)`.
- Evidencia: `83_evidencia_segunda_entrega_s3_be_02.md`.
- No requiere una migración adicional.
- Pendiente: validación PostgreSQL mediante rollback.

## Cierre de S3-BE-02

- Respuesta aceptada, rechazada y sin respuesta implementadas.
- Conflicto de intento HTTP 409 validado.
- Reasignación conserva el intento anterior y crea uno nuevo.
- Proveedor anterior/nuevo y motivo auditados.
- Validación PostgreSQL con rollback aprobada.
- Limpieza sin registros residuales.
- Evidencia: `84_evidencia_final_s3_be_02_postgresql.md`.
- Estado del incremento: **completado**.

## Primera entrega de S3-BE-03

- Política de 3 intentos, esperas 30/120/300 s y timeout 10 s codificada.
- Reintento del intento 1 al 2 y del 2 al 3 implementado.
- Escalamiento después del tercer fallo implementado.
- Contrato de mensaje compatible con Pub/Sub definido.
- Event ID y ordering key incluidos.
- Publicación y consumo idempotentes implementados.
- Reentrega con contenido diferente rechazada.
- Ruta dead letter idempotente implementada.
- Dobles en memoria; todavía no se crean recursos GCP.
- Catorce pruebas nuevas publicadas.
- Validación Cloud Shell: **189/189 pruebas aprobadas**.
- Alembic: `20260902_01 (head)`.
- Evidencia: `85_evidencia_primera_entrega_s3_be_03.md`.
- Recursos GCP de S3-DEC-03 creados y verificados: dos topics, dos suscripciones y una cola Cloud Tasks.
- Suscripciones Pub/Sub en estado `ACTIVE`.
- Cola `siniestro-asistencia-reintentos` en estado `RUNNING` y `maxAttempts: 1`.
- Evidencia: `87_evidencia_recursos_gcp_s3_be_03.md`.
- Pendiente: outbox PostgreSQL, adaptadores reales de Pub/Sub/Cloud Tasks y validación extremo a extremo.


## Segunda entrega de S3-BE-03 — fundación outbox

- Modelo `EventoOutbox` incorporado.
- Migración Alembic `20260902_02` publicada y todavía no aplicada.
- Repositorio PostgreSQL con reclamación `FOR UPDATE SKIP LOCKED`.
- Estados pendiente, publicando, publicado y fallido definidos.
- Confirmación idempotente de `pubsub_message_id`.
- Registro controlado de fallos y límite de lote.
- Cinco pruebas nuevas publicadas.
- Resultado esperado: **194/194 pruebas aprobadas**.
- Pendiente: validación Cloud Shell antes de aplicar la migración.
