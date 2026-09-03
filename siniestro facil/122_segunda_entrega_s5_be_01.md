# Segunda entrega S5-BE-01 — persistencia PostgreSQL

## Alcance entregado

- Persistencia transaccional de señales y alertas antifraude.
- Resolución obligatoria de la política mediante su versión exacta.
- Registro de modelo o regla, datos de origen y explicación.
- Auditoría atómica de cada evaluación, incluso cuando no produce alertas.
- Idempotencia persistente para resultados con cero, una o varias alertas.
- Recuperación ante solicitudes concurrentes con la misma clave.
- Consulta de alertas con unión a la política versionada.
- Selección automática del repositorio PostgreSQL cuando `DATABASE_URL` está configurada.

## Migración

- Revisión: `20260903_01`.
- Revisión anterior: `20260902_05`.
- Tabla: `siniestro_facil.solicitud_evaluacion_fraude_idempotente`.
- Script administrativo: `backend/scripts/16_apply_s5_fraud_migration_admin.sql`.
- La cuenta `siniestro_app` recibe solamente `SELECT, INSERT` sobre la tabla nueva.

## Pruebas

- Se añadieron siete verificaciones.
- Total esperado: **300 pruebas**.
- La validación real de Cloud SQL se documentará después de aplicar la migración y ejecutar rollback de los datos sintéticos.

## Estado

Segunda entrega publicada. No constituye todavía el cierre de S5-BE-01.
