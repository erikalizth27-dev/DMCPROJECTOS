# Matriz de trazabilidad — Sprint 6 Backend

| Incremento | HU | Criterio verificable | RF | Datos |
|---|---|---|---|---|
| S6-BE-01 | HU-16 | El pago autorizado aparece en la línea de tiempo | RF-18 | pago, autorizacion, evento_linea_tiempo |
| S6-BE-01 | HU-27 | La política vigente puede bloquear temporalmente el pago | RF-22 | alerta, politica_alerta, pago |
| S6-BE-01 | Transversal RBAC | Preparador y autorizador son identidades distintas; solo supervisor autoriza | RF-23 | identidad_actor, usuario_interno, autorizacion |
| S6-BE-02 | HU-16 | Línea de tiempo completa con actor, cambio y fecha | RF-18 | evento_linea_tiempo |
| S6-BE-02 | HU-24 | Consulta sensible restringida y auditada | RF-23 | identidad_actor, evento_linea_tiempo |
| S6-BE-02 | HU-28 | Vista única interna del caso | RF-30 | siniestro y referencias del expediente |
| S6-BE-03 | HU-29 | Indicadores disponibles con período y procedencia | RF-29 | siniestro, asistencia, evento_linea_tiempo |
| Estabilización | Transversal | Tolerancia a integración no disponible | RF-32 | adaptadores y auditoría técnica |

## Fuentes

- `01_historias_usuario.md`: HU-16, HU-24, HU-27, HU-28 y HU-29.
- `02_criterios_aceptacion.md`: auditoría, acceso, indicadores y revisión humana.
- `03_requerimientos_funcionales.md`: RF-18, RF-22, RF-23, RF-29, RF-30 y RF-32.
- `07_modelo_logico.md`: pago, autorización, alerta, comunicación y evento de línea de tiempo.
- `13_seguridad_rbac.md`: preparación/autorización de pago, segregación y autenticación reciente pendiente.
- `16_backlog_inicial_backend.md`: resultado esperado del Sprint 6.
- `137_acta_cierre_sprint_5.md`: línea base y elementos diferidos.

## Vacíos preservados

- No se seleccionó proveedor de pagos en las entrevistas.
- No se definió el ciclo operativo completo ni los estados externos de una transferencia.
- No se definieron fuentes o fórmulas para satisfacción, costo operativo y pérdidas evitadas.
- No se definieron ventanas de agregación para indicadores.
- No se definió el umbral de autenticación reciente.
- No se definieron valores de rate limiting.

## Puertas de decisión

| Decisión | Impacto | Estado |
|---|---|---|
| S6-DEC-01 | Habilita fundación y pruebas del flujo de pago simulado | Aprobada |
| S6-DEC-02 | Delimita indicadores calculables y valores no disponibles | Aprobada |
| S6-DEC-03 | Delimita estabilización de seguridad sin cifras inventadas | Aprobada |

Evidencia de aprobación: `141_registro_aprobacion_s6_decisiones.md`.

## Evidencias S6-BE-01

- Fundaciones: `143_primera_entrega_fundaciones_sprint_6.md`.
- Validación de fundaciones: `144_evidencia_fundaciones_sprint_6_cloudshell.md`.
- Primera entrega: `145_primera_entrega_s6_be_01.md`.
- Validación inicial: `146_evidencia_primera_entrega_s6_be_01_cloudshell.md`.
- Persistencia PostgreSQL: `147_segunda_entrega_s6_be_01.md`.
- Migración y regresión Cloud SQL: `148_evidencia_migracion_s6_be_01_cloudsql.md`.
- Validación final PostgreSQL: `149_evidencia_final_s6_be_01_postgresql.md`.

## Evidencia de cierre heredada

- Sprint 5: `137_acta_cierre_sprint_5.md`.
- Commit base: `50c5de8852ef74297d4056c46f0146da9d9f857e`.
- Suite heredada: **342 pruebas**.
- Alembic heredado: `20260903_03 (head)`.


## Evidencias S6-BE-02

- Primera entrega: `150_primera_entrega_s6_be_02.md`.
- Validación inicial: `151_evidencia_primera_entrega_s6_be_02_cloudshell.md`.
- Persistencia PostgreSQL: `152_segunda_entrega_s6_be_02.md`.
- Regresión completa: `153_evidencia_regresion_s6_be_02_cloudshell.md`.
- Validador PostgreSQL: `backend/scripts/25_validate_s6_be_02_postgresql.py`.
- Validación final PostgreSQL: `154_evidencia_final_s6_be_02_postgresql.md`.
