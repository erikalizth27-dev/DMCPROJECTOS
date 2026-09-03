# Evidencia final S6-BE-01 — PostgreSQL

## Entorno

- Fecha: 2026-09-03.
- Base: `DMCSINIESTROFACIL`.
- Esquema: `siniestro_facil`.
- Migración: `20260903_04 (head)`.
- Script: `backend/scripts/24_validate_s6_be_01_postgresql.py`.

## Resultados

- Pago preparado con identidad y alcance válidos.
- Operación confirmada como simulada y sin transferencia monetaria.
- Repetición idempotente de preparación sin duplicados.
- Conflicto por reutilización incompatible de clave: HTTP 409.
- Operador impedido de autorizar: HTTP 403.
- Autorización realizada por un supervisor distinto del preparador.
- Segregación de funciones confirmada.
- Versión optimista actualizada de 0 a 1.
- Repetición idempotente de autorización confirmada.
- Autorización formal persistida.
- Alerta crítica pendiente bloqueó un segundo pago: HTTP 409.
- Auditoría e idempotencia persistidas atómicamente.

## Limpieza

La prueba se ejecutó dentro de una transacción externa y finalizó con rollback. Se confirmó la eliminación de:

- pagos y autorización sintéticos;
- alerta y política sintéticas;
- eventos de auditoría y solicitudes idempotentes;
- identidades, usuarios y asignación sintéticos.

## Conclusión

**S6-BE-01 PostgreSQL: OK.** El incremento queda completado con persistencia, RBAC, alcance, segregación, control de alertas críticas, concurrencia, idempotencia, auditoría y ausencia de residuos.
