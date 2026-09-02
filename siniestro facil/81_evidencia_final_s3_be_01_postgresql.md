# Evidencia final S3-BE-01 — PostgreSQL

## Resultado

La validación final de S3-BE-01 se ejecutó correctamente en Google Cloud Shell contra Cloud SQL.

- Fecha: 2026-09-02.
- Rama: `agent/sprint-3-backend`.
- Script: `backend/scripts/05_validate_s3_be_01_postgresql.py`.
- Base: `DMCSINIESTROFACIL`.
- Usuario runtime: `siniestro_app`.
- Migración: `20260902_01 (head)`.

## Validaciones aprobadas

- Siniestro utilizado: 4.
- Proveedor utilizado: 2.
- Asistencia sintética: 12.
- Persistencia y referencia externa.
- Auditoría atómica de solicitud y envío.
- Repetición idempotente sin segundo despacho.
- Conflicto HTTP 409 con igual clave y otro contenido.
- Rollback de toda la prueba.
- Ausencia de asistencia, auditoría, idempotencia e identidad residuales.

## Salida confirmada

```text
Persistencia y referencia externa: OK
Auditoría atómica: OK
Repetición idempotente: OK
Despacho simulado único: OK
Conflicto idempotente: HTTP 409 — OK
S3-BE-01 PostgreSQL: OK
ROLLBACK ejecutado
Limpieza validada: sin registros residuales
VALIDACIÓN FINAL S3-BE-01 COMPLETADA
```

## Seguridad operativa

- La migración fue ejecutada con usuario administrativo.
- `siniestro_app` no recibió propiedad ni DDL.
- El runtime recibió solamente permisos DML sobre la tabla idempotente nueva y uso de la secuencia existente.
- La contraseña administrativa no se guardó en `.env`.

## Conclusión

S3-BE-01 cumple creación, consulta, persistencia, privacidad, auditoría e idempotencia. El incremento queda completado y Sprint 3 alcanza 40%.
