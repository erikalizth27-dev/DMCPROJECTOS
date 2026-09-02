# Backlog refinado — Sprint 3 Backend

## Objetivo

Coordinar asistencia asociada a un siniestro, conservar el historial de interacción con proveedores y tolerar ausencia de respuesta mediante procesamiento asíncrono e idempotente.

## Alcance propuesto

### S3-BE-01 — Solicitar y consultar asistencia

| Campo | Definición |
|---|---|
| Historias | HU-07, HU-21 |
| Requisitos | RF-06, RF-17, RF-18 |
| Caso de uso | CU-02 |
| Datos | asistencia, proveedor, evento_linea_tiempo |
| Dependencia | S3-DEC-01 |

Criterios:

- Crear la solicitud vinculada a un siniestro visible para el actor.
- Persistir proveedor, tipo, estado y trazabilidad disponible.
- Registrar el evento inicial de auditoría en la misma transacción.
- Aplicar RBAC, idempotencia y control de versión cuando modifique el siniestro.
- Permitir consultar el estado sin exponer datos de otro caso.

### S3-BE-02 — Registrar respuesta y reasignar

| Campo | Definición |
|---|---|
| Historias | HU-12, HU-15, HU-21 |
| Requisitos | RF-12, RF-17, RF-18 |
| Casos de uso | CU-02, CU-04 |
| Datos | asistencia, proveedor, asignacion_siniestro, comunicacion, evento_linea_tiempo |
| Dependencia | Reglas existentes de historial y una asignación activa |

Criterios:

- Registrar respuesta aceptada, rechazada o sin respuesta.
- Finalizar la asignación activa antes de crear otra.
- Conservar proveedor anterior, fechas y razón del cambio.
- Impedir más de una asignación activa.
- Auditar respuesta y reasignación atómicamente.

### S3-BE-03 — Reintentar y escalar con Pub/Sub

| Campo | Definición |
|---|---|
| Historias | HU-15, HU-21 |
| Requisitos | RF-17, RF-18, RF-32 |
| Arquitectura | Pub/Sub, consumidor idempotente y dead-letter topic |
| Datos | asistencia, comunicacion, evento_linea_tiempo |
| Dependencias | S3-DEC-01 y S3-DEC-02 |

Criterios:

- Persistir el comando local antes de comunicarse externamente.
- Publicar un identificador estable para tolerar reentrega.
- Evitar efectos duplicados al consumir el mismo evento.
- Registrar cada intento y su resultado.
- Escalar o reasignar según la política aprobada.
- Enviar fallos permanentes a una ruta de dead letter sin perder trazabilidad.

## Fuera de alcance

- Integración productiva con un proveedor no seleccionado.
- Inspecciones, presupuestos y autorizaciones de Sprint 4.
- Fraude y alertas de Sprint 5.
- Pagos e indicadores de Sprint 6.
- CI/CD, Cloud Run operativo y observabilidad productiva.

## Definition of Ready

| Incremento | Estado | Condición pendiente |
|---|---|---|
| S3-BE-01 | Listo | S3-DEC-01 aprobada |
| S3-BE-02 | Listo | Reutiliza reglas ya materializadas de asignación e historial |
| S3-BE-03 | Listo | S3-DEC-01 y S3-DEC-02 aprobadas |
