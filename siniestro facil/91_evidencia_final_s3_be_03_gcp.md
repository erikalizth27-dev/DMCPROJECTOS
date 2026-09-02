# Evidencia final S3-BE-03 — Pub/Sub y Cloud Tasks

## Contexto

- Fecha: 2 de septiembre de 2026.
- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Región: `us-central1`.
- Rama: `agent/sprint-3-backend`.
- Alembic: `20260902_02 (head)`.

## Regresión

- **201/201 pruebas aprobadas**.
- Tiempo reportado: 1.84 segundos.
- Cero fallos.
- Un aviso no bloqueante de Starlette TestClient.

## Pub/Sub real

- Suscripción temporal creada.
- Mensaje sintético publicado en `siniestro-asistencia-solicitudes`.
- Message ID: `21616234086078566`.
- Evento consumido y confirmado.
- Suscripción temporal eliminada.
- Dos mensajes sintéticos retirados de `siniestro-asistencia-worker`, incluyendo el generado por el intento previo.
- Mensajes no sintéticos no fueron confirmados.

## Cloud Tasks real

- Cola: `siniestro-asistencia-reintentos`.
- Tarea sintética programada a 300 segundos.
- Tarea recuperada y verificada.
- Tarea eliminada antes de su ejecución.
- No quedaron tareas temporales.

## Compatibilidad técnica

Cloud Tasks exige un `dispatchDeadline` entre 15 segundos y 30 minutos. Se configuró el mínimo técnico de 15 segundos. El timeout funcional aprobado de 10 segundos permanece en el trabajador para la llamada al proveedor.

## Resultado

```text
Publicación y consumo Pub/Sub: OK
Programación Cloud Tasks: OK
LIMPIEZA GCP: OK
VALIDACIÓN REAL S3-BE-03 COMPLETADA
```

## Cierre del incremento

- Outbox PostgreSQL validado.
- Publicación idempotente validada.
- Pub/Sub real validado.
- Cloud Tasks real validado.
- Dead letter configurado.
- Limpieza sin recursos ni mensajes sintéticos residuales.
- `S3-BE-03`: completado.
