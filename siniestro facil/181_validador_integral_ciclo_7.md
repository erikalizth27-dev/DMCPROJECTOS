# Validador integral — C7-PLAT-06

## Script

`backend/scripts/30_validate_cycle7.sh`

## Cobertura

1. Compilación, suite completa y Alembic.
2. Cloud Run listo y sin miembros públicos.
3. Liveness y readiness mediante invocación autenticada.
4. Registro estructurado correlacionado en Cloud Logging.
5. Ausencia de campos sensibles en el registro.
6. Separación entre secretos de runtime y migración.
7. Disponibilidad del Cloud Run Job migrador.
8. Existencia de una construcción exitosa.

## Mutaciones

El script no modifica infraestructura ni base de datos. Únicamente genera solicitudes de salud autenticadas y archivos temporales locales, eliminados al finalizar.

## Pendientes

- Ejecutar desde Cloud Shell con `.env` cargado y Cloud SQL Proxy activo para la comprobación local de Alembic.
- Registrar la evidencia obtenida.
- Completar acta de cierre y PR.
