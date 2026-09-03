# Segunda entrega S5-BE-03 — persistencia PostgreSQL

## Alcance

- Persistencia de candidatos en `relacion_casos`.
- Valor normalizado y estado pendiente de revisión conservados.
- Unicidad por par canónico y criterio.
- Verificación de existencia de todos los siniestros.
- Auditoría atómica sin fusión automática.
- Idempotencia persistente y recuperación ante carreras.
- API conectada a PostgreSQL con `DATABASE_URL`.

## Migración

- Revisión: `20260903_03`.
- Anterior: `20260903_02`.
- Tabla: `solicitud_relacion_casos_idempotente`.
- Script: `backend/scripts/20_apply_s5_case_relations_migration_admin.sql`.

## Pruebas

- Siete verificaciones nuevas.
- Total esperado: **342 pruebas**.

## Estado

Persistencia publicada. Pendiente migración, regresión y validación PostgreSQL con rollback.
