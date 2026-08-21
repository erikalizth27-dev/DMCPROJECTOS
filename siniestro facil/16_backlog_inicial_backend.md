# Backlog inicial backend para planning

## Sprint 0 — Especificación y plataforma

- Consolidar decisiones simuladas aprobadas en todas las SPEC.
- Fusionar el modelo físico PostgreSQL y sus pruebas.
- Aprobar contrato OpenAPI inicial.
- Aprobar matriz RBAC.
- Cerrar máquina de estados y reglas de reapertura.
- Definir proveedores de identidad, evidencia, mensajería, mapas y pagos.
- Preparar repositorio backend, CI y ambientes.

## Épica 1 — Registro y consulta

- HU-01, HU-03, HU-04, HU-06, HU-08, HU-10 y HU-28.
- Resultado: creación idempotente, detección de posibles duplicados y vista del caso según rol.

## Épica 2 — Cobertura, evidencia y asistencia

- HU-02, HU-05, HU-07, HU-09, HU-15 y HU-21.
- Resultado: validación de cobertura, evidencia inmutable y coordinación resiliente.

## Épica 3 — Operación, inspección y taller

- HU-11 a HU-20.
- Resultado: asignación, inspección, presupuesto, cambios y autorizaciones auditables.

## Épica 4 — Fraude y decisiones humanas

- HU-22 a HU-27 y HU-30.
- Resultado: señales, alertas reproducibles, relaciones y revisión humana.

## Épica 5 — Auditoría e indicadores

- HU-16, HU-24, HU-26, HU-29.
- Resultado: línea de tiempo, accesos sensibles e indicadores.

## Regla de priorización

Cada historia debe cumplir `10_definition_of_ready_backend.md` antes de comprometerse.

## Plan recomendado del piloto

- Duración del sprint: 2 semanas.
- Horizonte backend: 7 sprints / 14 semanas.
- Equipo recomendado: Product Owner o analista, líder técnico, dos desarrolladores backend, QA de automatización y especialista GCP/DevOps.

| Sprint | Resultado esperado |
|---|---|
| 0 | SPEC consolidadas, OpenAPI, RBAC, ambientes y CI/CD |
| 1 | Registro, consulta y deduplicación |
| 2 | Cobertura, estados y evidencias en Cloud Storage |
| 3 | Asistencia, proveedores, reintentos y Pub/Sub |
| 4 | Inspección, presupuestos y autorizaciones |
| 5 | Fraude, alertas, relaciones y revisión humana |
| 6 | Pagos, auditoría, indicadores, seguridad y estabilización |

La estimación final se recalibra con la capacidad real del equipo al terminar Sprint 0.
