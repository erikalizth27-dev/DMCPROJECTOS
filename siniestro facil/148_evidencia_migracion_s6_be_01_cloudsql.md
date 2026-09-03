# Evidencia de migración S6-BE-01 — Cloud SQL

## Resultado

- Fecha de validación: 2026-09-03.
- Base: `DMCSINIESTROFACIL`.
- Esquema: `siniestro_facil`.
- Migración aplicada: `20260903_04 (head)`.
- Suite ejecutada: `python -m pytest -q`.
- Resultado: **386 pruebas aprobadas**.
- Advertencias: una advertencia conocida de deprecación de Starlette; no bloqueante.

## Objetos confirmados

- Columna `pago.id_usuario_prepara`.
- Columna `pago.version`.
- Tabla `solicitud_preparacion_pago_idempotente`.
- Tabla `solicitud_autorizacion_pago_idempotente`.

## Conclusión

La migración de pagos y la regresión completa quedaron validadas en Cloud SQL. No se reportaron fallos funcionales. Queda pendiente la validación transaccional real de S6-BE-01 con rollback y comprobación de ausencia de residuos.
