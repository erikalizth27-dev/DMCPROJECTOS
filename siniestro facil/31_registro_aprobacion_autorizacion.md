# Registro de aprobación — AR-01, AR-02 y AR-03

## Decisión

El Product Owner aprobó explícitamente las recomendaciones `AR-01`, `AR-02` y
`AR-03` el 25 de agosto de 2026.

## Línea base aprobada

| ID | Decisión |
|---|---|
| AR-01 | Asegurado solicita asistencia en caso propio; operador/ajustador en caso asignado; supervisor transversal |
| AR-02 | Preparación y autorización de pago son comandos separados; sólo supervisor diferente del preparador autoriza |
| AR-03 | Operador/ajustador reciben resumen de alertas; investigador/supervisor reciben detalle |

## Contratos resultantes

- `POST /siniestros/{id}/asistencias` → `SOLICITAR_ASISTENCIA`.
- `POST /siniestros/{id}/solicitudes-pago` → `PREPARAR_PAGO`.
- `POST /solicitudes-pago/{id}/autorizacion` → `AUTORIZAR_PAGO`.
- Resumen de alerta: `id`, `severidad`, `estadoRevision`.
- Detalle de alerta: resumen más `tipo` y `detalle`.

## Artefactos actualizados

- `12_api_backend_openapi.yaml`
- `13_seguridad_rbac.md`
- `17_preguntas_abiertas_backend.md`
- `29_matriz_endpoint_rol.md`
- `backend/src/siniestro_facil/domain/authorization.py`
- `backend/src/siniestro_facil/api/schemas.py`
- pruebas de autorización, contratos y OpenAPI

## Validación pendiente

La compilación local es correcta y el OpenAPI fue validado como YAML con 11
rutas, 11 operaciones únicas y 14 esquemas. La suite actualizada debe ejecutarse
en Cloud Shell antes de cerrar el bloque.
