# Registro de aprobación S3-DEC-03

## Decisión

El 2 de septiembre de 2026, el Product Owner aprobó:

> Crear los recursos Pub/Sub propuestos en `project-77c17016-86bc-4fc4-a97` y utilizar Cloud Tasks para programar los reintentos de 30 segundos, 2 minutos y 5 minutos.

## Recursos aprobados

- Proyecto GCP: `project-77c17016-86bc-4fc4-a97`.
- Topic principal: `siniestro-asistencia-solicitudes`.
- Suscripción del trabajador: `siniestro-asistencia-worker`.
- Topic de mensajes fallidos: `siniestro-asistencia-dead-letter`.
- Suscripción de monitoreo: `siniestro-asistencia-dead-letter-monitor`.
- Cloud Tasks: programación de reintentos a 30, 120 y 300 segundos.
- Timeout por intento: 10 segundos.
- Escalamiento: después del tercer fallo.

## Controles

- El outbox PostgreSQL será la fuente transaccional de eventos.
- Pub/Sub transportará los eventos; Cloud Tasks programará la ejecución diferida.
- Los consumidores deberán ser idempotentes.
- La creación se realizará mediante comandos verificables en Cloud Shell.
- No se autorizan permisos IAM amplios ni despliegues adicionales.
- La fusión del PR de Sprint 3 requiere autorización explícita posterior.
