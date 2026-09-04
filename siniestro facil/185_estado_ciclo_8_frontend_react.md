# Estado Ciclo 8 — Frontend React

## Objetivo

Construir el frontend de Siniestro Fácil en React, con trazabilidad directa a historias de usuario, criterios de aceptación y OpenAPI.

## Primera entrega

- Rama: `agent/ciclo-8-frontend-react`.
- Stack: React, TypeScript y Vite.
- Superficie responsive para teléfono y escritorio.
- Reporte de siniestro con los campos exactos de `CrearSiniestro`.
- Regla de póliza o documento aplicada en cliente.
- Consulta de caso por identificador.
- Presentación del estado y siguiente paso.
- Estados de carga, error y éxito.
- Cliente HTTP tipado.
- Ningún secreto ni token persistido.

## Trazabilidad

| Elemento | Fuente |
|---|---|
| Reportar desde teléfono | HU-01 |
| Datos mínimos | HU-03 |
| Estado y siguiente paso | HU-06 |
| Payload y respuestas | `12_api_backend_openapi.yaml` |
| Autenticación pendiente | `13_seguridad_rbac.md` y cierre del Ciclo 7 |

## Pendientes de validación

- Instalar dependencias y generar el lockfile.
- Ejecutar `npm run typecheck`.
- Ejecutar `npm run build`.
- Validar integración contra backend local.
- Definir autenticación del navegador antes de integrar producción.
