# Primera entrega — C7-PLAT-01

## Resultado

Se incorporó la fundación del contenedor reproducible y seguro del backend.

## Artefactos

- `backend/Dockerfile`.
- `backend/.dockerignore`.
- `backend/tests/test_container_contract.py`.
- `backend/scripts/28_validate_container.sh`.

## Controles implementados

- Python 3.12.
- Usuario sin privilegios `10001:10001`.
- Arranque con Uvicorn y `exec` para preservar señales.
- Puerto configurable mediante `PORT`.
- Dependencias GCP incluidas mediante el extra `gcp`.
- Alembic incluido para la futura ejecución exclusiva de migraciones.
- Exclusión del archivo `.env`, repositorio Git, entorno virtual, pruebas y scripts.
- Validación de liveness, readiness y conexión a Cloud SQL.
- Comprobación de ausencia de `DATABASE_URL` en la configuración de la imagen.

## Migraciones

No se agregan migraciones de base de datos.

## Estado

Primera entrega implementada. Pendiente de validar en Cloud Shell:

1. Compilación.
2. Suite completa.
3. Construcción de la imagen.
4. Usuario no privilegiado.
5. Salud con Cloud SQL.
6. Alembic dentro del contenedor.
