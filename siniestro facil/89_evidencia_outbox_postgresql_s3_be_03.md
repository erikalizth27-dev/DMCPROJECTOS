# Evidencia PostgreSQL del outbox S3-BE-03

## Contexto

- Fecha: 2 de septiembre de 2026.
- Proyecto GCP: `project-77c17016-86bc-4fc4-a97`.
- Base: `DMCSINIESTROFACIL`.
- Esquema: `siniestro_facil`.
- Alembic: `20260902_02 (head)`.
- Script: `backend/scripts/07_validate_s3_be_03_outbox_postgresql.py`.

## Privilegios

- Tabla y secuencia propiedad de `siniestro_migrator`.
- `siniestro_app` conserva `SELECT`, `INSERT` y `UPDATE`.
- `siniestro_app` no puede `DELETE`.
- `siniestro_app` no puede crear objetos en el esquema.
- `siniestro_app` no pertenece al rol migrador.

## Resultado

La ejecución confirmó:

- Inserción transaccional: OK.
- Reclamación mediante `FOR UPDATE SKIP LOCKED`: OK.
- Reintento después de fallo: OK.
- Conflicto de `message_id`: OK.
- Confirmación idempotente de publicación: OK.
- Estado e intentos persistidos correctamente.
- Rollback ejecutado.
- Cero registros residuales.

Resultado final:

```text
S3-BE-03 OUTBOX POSTGRESQL: OK
VALIDACIÓN OUTBOX S3-BE-03 COMPLETADA
```

## Incidencia corregida

La primera ejecución utilizó sesiones sin savepoints y una excepción esperada revirtió la transacción externa. El script fue corregido con `join_transaction_mode="create_savepoint"` y la repetición resultó exitosa. No fue un defecto del esquema ni del repositorio.

## Pendiente

- Publicador real de Pub/Sub.
- Programador real de Cloud Tasks.
- Integración entre outbox, publicación y programación diferida.
- Validación de extremo a extremo.
