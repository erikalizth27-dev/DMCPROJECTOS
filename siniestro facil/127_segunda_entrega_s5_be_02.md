# Segunda entrega S5-BE-02 — persistencia PostgreSQL

## Alcance

- Versión optimista física en `alerta`.
- Idempotencia persistente de una decisión por alerta.
- Bloqueo de fila antes de revisar.
- Justificación y estado humano almacenados.
- Auditoría atómica de la revisión.
- Auditoría separada de consultas con detalle antifraude.
- Recuperación segura ante carreras de idempotencia.

## Migración

- Revisión: `20260903_02`.
- Anterior: `20260903_01`.
- Tabla: `solicitud_revision_alerta_idempotente`.
- Script administrativo:
  `backend/scripts/18_apply_s5_alert_review_migration_admin.sql`.
- Privilegios mínimos para `siniestro_app`.

## Pruebas

- Siete verificaciones nuevas.
- Total esperado: **321 pruebas**.

## Estado

Segunda entrega publicada. Pendiente aplicar migración, ejecutar regresión y validar PostgreSQL con rollback.
