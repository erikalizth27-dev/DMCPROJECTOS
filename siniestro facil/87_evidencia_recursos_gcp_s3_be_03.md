# Evidencia de recursos GCP para S3-BE-03

## Contexto

- Fecha: 2 de septiembre de 2026.
- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Región de Cloud Tasks: `us-central1`.
- Decisión aplicable: `S3-DEC-03`.
- Ejecución: Google Cloud Shell.

## Pub/Sub

La verificación confirmó las siguientes suscripciones:

### Trabajador de asistencia

- Nombre: `siniestro-asistencia-worker`.
- Topic: `siniestro-asistencia-solicitudes`.
- Estado: `ACTIVE`.
- Ack deadline: 60 segundos.
- Retención de mensajes: 604800 segundos (7 días).
- Dead letter topic: `siniestro-asistencia-dead-letter`.
- Máximo de entregas antes de dead letter: 5.

### Monitoreo de mensajes fallidos

- Nombre: `siniestro-asistencia-dead-letter-monitor`.
- Topic: `siniestro-asistencia-dead-letter`.
- Estado: `ACTIVE`.
- Ack deadline: 60 segundos.
- Retención de mensajes: 604800 segundos (7 días).

## Cloud Tasks

La verificación confirmó:

- Cola: `siniestro-asistencia-reintentos`.
- Región: `us-central1`.
- Estado: `RUNNING`.
- Máximo de intentos automáticos de la cola: 1.
- Máximo de despachos concurrentes: 10.
- Máximo de despachos por segundo: 5.
- Burst máximo: 10.

El valor `maxAttempts: 1` evita que Cloud Tasks introduzca reintentos adicionales. La aplicación programará explícitamente los intentos aprobados a 30, 120 y 300 segundos.

## Resultado

- Transporte principal disponible.
- Ruta dead letter configurada y verificada mediante `deadLetterPolicy`.
- Cola de programación diferida disponible.
- No se registraron errores de permisos en la salida compartida.
- Recursos alineados con `S3-DEC-03`.

## Pendiente

- Implementar outbox transaccional PostgreSQL.
- Implementar adaptadores reales de Pub/Sub y Cloud Tasks.
- Validar publicación, consumo idempotente y escalamiento de extremo a extremo.
