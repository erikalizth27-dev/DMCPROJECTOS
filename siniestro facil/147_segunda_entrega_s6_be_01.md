# Segunda entrega S6-BE-01 — PostgreSQL

## Alcance implementado

- Repositorio PostgreSQL de preparación y autorización de pagos.
- Validación de identidad interna y asignación activa.
- Autorización exclusiva del supervisor.
- Separación persistente entre preparador y autorizador.
- Bloqueo optimista por versión.
- Revalidación transaccional de alertas críticas pendientes.
- Autorización formal vinculada al pago.
- Auditoría e idempotencia dentro de la misma transacción.
- Recuperación segura ante carreras de idempotencia.
- API conectada a PostgreSQL cuando existe `DATABASE_URL`.

## Migración

- Revisión: `20260903_04`.
- Revisión anterior: `20260903_03`.
- Agrega a `pago`:
  - `id_usuario_prepara`, nullable para preservar registros históricos.
  - `version`, con valor inicial 0.
- Crea:
  - `solicitud_preparacion_pago_idempotente`.
  - `solicitud_autorizacion_pago_idempotente`.
- Incluye downgrade reversible.
- Script administrativo: `23_apply_s6_payment_migration_admin.sql`.

## Pruebas añadidas

- Siete verificaciones estructurales del repositorio PostgreSQL.
- Una verificación de estructura Alembic.
- Total nuevo: **8 pruebas**.
- Total esperado: **386 pruebas**.

## Controles

- El pago permanece simulado.
- `transferencia_realizada` permanece en falso.
- La identidad del preparador se conserva.
- La alerta crítica se comprueba dentro de la transacción de autorización.
- No se autoriza un pago histórico que carezca de preparador identificable.

## Pendiente

- Compilar y ejecutar la regresión.
- Aplicar la migración en Cloud SQL con usuario administrador.
- Ejecutar una validación PostgreSQL con rollback y ausencia de residuos.
