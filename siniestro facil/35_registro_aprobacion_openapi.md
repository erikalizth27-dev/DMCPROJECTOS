# Registro de aprobación — OpenAPI 0.2.0-draft

## Decisión

El Product Owner aprobó explícitamente el contrato OpenAPI `0.2.0-draft` el 25
de agosto de 2026.

## Línea base aprobada

| Elemento | Valor |
|---|---:|
| Rutas | 11 |
| Operaciones únicas | 11 |
| Esquemas | 14 |
| Ejemplos de comandos | 8 |
| Ejemplos de errores | 5 |
| Pruebas OpenAPI | 4 |
| Suite backend | 42/42 aprobadas |

## Decisiones contractuales incluidas

- Asistencia autorizada según rol y alcance (`AR-01`).
- Preparación y autorización de pagos separadas (`AR-02`).
- Resumen y detalle de alertas según rol (`AR-03`).
- Confirmación humana explícita para autorizar pagos.
- Concurrencia optimista mediante `version` al cambiar estado.
- Idempotencia obligatoria en comandos con efectos.
- Errores reutilizables `401`, `403`, `404`, `409` y `422`.
- Ejemplos exclusivamente sintéticos y sin secretos.

## Artefactos de evidencia

- `12_api_backend_openapi.yaml`.
- `29_matriz_endpoint_rol.md`.
- `33_validacion_ejemplos_openapi.md`.
- `34_evidencia_suite_openapi_cloudshell.md`.
- `backend/tests/test_openapi_spec.py`.

## Control de cambios

Cualquier modificación posterior de rutas, operaciones, cuerpos, códigos de
respuesta, reglas de autorización o esquemas requiere:

1. Actualizar OpenAPI y los contratos Pydantic.
2. Mantener trazabilidad con HU, RF y criterios de aceptación.
3. Actualizar o agregar pruebas.
4. Registrar una nueva versión contractual para aprobación.

## Pendiente externo al contrato

El proveedor de identidad y el formato definitivo de claims continúan
pendientes. Su definición no modifica esta aprobación mientras respete la
matriz endpoint–rol y el esquema Bearer JWT del contrato.
