# Validador integral — Sprint 6

## Script

`backend/scripts/27_validate_sprint6.sh`

## Secuencia

1. Compilación de `src`, `tests` y `alembic`.
2. Suite completa.
3. Confirmación de Alembic `20260903_04 (head)`.
4. Verificación de que Git no rastrea `.env`, claves privadas o contenedores de certificados.
5. Validación PostgreSQL S6-BE-01.
6. Validación PostgreSQL S6-BE-02.
7. Validación PostgreSQL S6-BE-03.

Los validadores PostgreSQL usan transacciones externas, rollback y comprobación de ausencia de residuos.

## Ejecución

```bash
bash scripts/27_validate_sprint6.sh
```

## Resultado esperado

```text
SPRINT 6 — VALIDACIÓN INTEGRAL COMPLETADA
```
