# Evidencia final S2-BE-03 — PostgreSQL

## Resultado

La validación final de S2-BE-03 se ejecutó correctamente desde Google Cloud Shell contra Cloud SQL.

- Fecha: 2026-09-01.
- Rama: `agent/sprint-2-backend`.
- Script: `backend/scripts/04_validate_s2_be_03_postgresql.py`.
- Base: `DMCSINIESTROFACIL`.
- Usuario de aplicación: `siniestro_app`.
- Migración vigente: `20260901_01 (head)`.

## Controles aprobados

- Selección de un siniestro real para la prueba.
- Registro de evidencia y persistencia de URI y SHA-256.
- Auditoría creada dentro de la misma transacción.
- Repetición con la misma clave idempotente devuelve el mismo resultado.
- Cambio de carga con la misma clave produce conflicto HTTP 409.
- PostgreSQL impide modificar la evidencia original.
- Rollback de toda la prueba sintética.
- Ausencia de evidencia, auditoría, idempotencia e identidad residuales.

## Salida confirmada

```text
Siniestro probado: 4
Evidencia registrada: 23
URI y SHA-256 persistidos: OK
Auditoría atómica: OK
Repetición idempotente: OK
Conflicto idempotente: HTTP 409 — OK
Inmutabilidad PostgreSQL: OK
S2-BE-03 PostgreSQL: OK
ROLLBACK ejecutado
Evidencia sintética eliminada: OK
Auditoría sintética eliminada: OK
Idempotencia sintética eliminada: OK
Identidad sintética eliminada: OK
Limpieza validada: sin registros residuales
VALIDACIÓN FINAL S2-BE-03 COMPLETADA
```

## Conclusión

S2-BE-03 cumple sus verificaciones de persistencia, integridad, idempotencia, auditoría, inmutabilidad y limpieza. El incremento queda completado y Sprint 2 alcanza 85%.
