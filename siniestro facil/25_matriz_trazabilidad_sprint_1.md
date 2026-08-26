# Matriz de trazabilidad — Sprint 1 Backend

| Incremento | HU | Criterio de aceptación | RF | CU | Endpoint | Datos principales | Pruebas |
|---|---|---|---|---|---|---|---|
| S1-BE-01 | HU-01 | Reporte completo desde el teléfono | RF-01, RF-02 | CU-01 | POST /siniestros | asegurado, reportante, siniestro | API, integración, idempotencia |
| S1-BE-01 | HU-03 | Creación con datos mínimos | RF-01, RF-04, RF-31 | CU-01 | POST /siniestros | poliza, vehiculo, siniestro | contrato, reglas, persistencia |
| S1-BE-01 | HU-08 | Registro y validación inicial | RF-03, RF-04 | CU-01 | POST /siniestros | poliza, vehiculo, reportante | integración y rollback |
| S1-BE-02 | HU-10 | Identificación del mismo accidente | RF-13 | CU-01 | POST /siniestros | siniestro, vehiculo | duplicidad y concurrencia |
| S1-BE-03 | HU-06 | Estado actual y siguiente paso | RF-09, RF-10 | CU-01 | GET /siniestros/{id} | siniestro | API, RBAC, privacidad |
| S1-BE-03 | HU-28 | Vista única según rol | RF-23, RF-30 | CU-09 | GET /siniestros/{id} | núcleo del caso | RBAC y auditoría |
| S1-BE-04 | HU-04 | Reportante diferente del asegurado | RF-02 | CU-01 | POST /siniestros | reportante, asegurado | reglas y seguridad |
| S1-BE-05 | HU-08 | Estado posterior a validación inicial | RF-09, RF-18 | CU-01 | POST /siniestros/{id}/estado | siniestro, evento_linea_tiempo | transición y concurrencia |
| S1-BE-06 | HU-16 | Línea de tiempo auditable | RF-18 | CU-09 | GET /siniestros/{id}/linea-tiempo | evento_linea_tiempo | auditoría y privacidad |

## Reglas de trazabilidad

- Un cambio de contrato actualiza OpenAPI, modelo Pydantic y prueba asociada.
- Un cambio de regla actualiza criterio de aceptación, dominio y prueba.
- Un cambio de datos actualiza modelo lógico, físico, migración y prueba de constraint.
- Ningún incremento se marca terminado si pierde el vínculo con su HU y RF.

## Resolución de vacíos

| ID | Resolución | Estado |
|---|---|---|
| DM-01 | `reportante.relacion_asegurado` con catálogo y regla titular/no titular | Materializada |
| DM-02 | `siniestro.version` para concurrencia optimista y HTTP 409 | Materializada |
| DM-03 | `siguientePaso` derivado; no persistido | Materializada |
| DM-04 | `asignacion_siniestro` e índice de una asignación activa | Materializada |
| DM-05 | Retención recomendada de auditoría por cinco años | Pendiente de aprobación |

## Vacíos funcionales restantes

1. La relación declarada del tercero no demuestra por sí sola que esté autorizado.
2. La integración real con el sistema de pólizas requiere API o adaptador.
3. La regla de deduplicación por placa y día sigue siendo provisional.
4. DM-05 requiere aprobación regulatoria/funcional antes de fijar retención.

Los incrementos afectados conservan estas condiciones en su Definition of Ready.
