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

## Vacíos detectados

1. El modelo `reportante` no contiene la relación declarada del tercero con el asegurado.
2. `siniestro` no tiene una columna explícita de versión para concurrencia optimista.
3. El siguiente paso visible no está materializado; debe derivarse de estado y reglas o modelarse.
4. La asignación del caso no está materializada en una entidad específica, aunque HU-11/HU-12 exigen historial.
5. La auditoría de consultas sensibles requiere definir retención y detalle permitido.

Estos vacíos deben resolverse antes de comprometer los incrementos afectados.
