# Estado actual — Sprint 0 Backend

## Avance general

**80% completado**.

El porcentaje se calcula sobre los siete frentes definidos en `20_plan_detallado_sprint_0.md`. No incluye CI/CD, observabilidad ni operación GCP, porque fueron retirados expresamente del alcance.

| Frente | Avance | Evidencia | Pendiente principal |
|---|---:|---|---|
| 1. Consolidación SDD | 72% | SPEC backend, decisiones recomendadas y cinco decisiones de modelado documentadas | Aprobar las decisiones provisionales y propagarlas al resto de las SPEC |
| 2. Diseño de arquitectura GCP | 70% | Arquitectura, topología y servicios documentados | Confirmar Cloud Run, identidad, regiones y separación de ambientes |
| 3. Contrato OpenAPI | 72% | OpenAPI 3.1 válido y matriz endpoint–rol trazada a la política ejecutable | Resolver AR-01, AR-02 y AR-03; completar respuestas y ejemplos |
| 4. Datos y migraciones | 100% | 22 tablas desplegadas, constraints probados, datos sintéticos y revisión Alembic `20260825_01` aplicada y validada en Cloud SQL | Fusionar PR #1 y conservar la evidencia como línea base |
| 5. Seguridad, RBAC y auditoría | 72% | Política ejecutable por rol y alcance, separación de pagos y 9 pruebas específicas | Aprobar proveedor de identidad, claims y detalle visible por rol |
| 6. Esqueleto backend local | 100% | Python/FastAPI, configuración, dominio, contratos, RBAC, readiness positivo/negativo, Alembic y suite 30/30 | Mantener compilación y pruebas verdes ante cambios |
| 7. Refinamiento de Sprint 1 | 75% | Seis incrementos verticales, trazabilidad y propuestas concretas para los cinco vacíos | Aprobar las propuestas y estimar con la capacidad real del equipo |

Promedio ponderado y redondeado: **80%**.

## Completado

- Plan y alcance de Sprint 0.
- Arquitectura backend y GCP documentada.
- Contrato OpenAPI ampliado y validado con 10 operaciones y 12 esquemas.
- Contratos Pydantic para siniestros, estados, evidencias, asistencia, presupuestos, alertas y pagos.
- Cinco pruebas adicionales de validación de contratos aprobadas localmente.
- Política RBAC ejecutable y nueve pruebas de autorización y separación de funciones.
- Backlog de Sprint 1 refinado en seis incrementos verticales.
- Matriz de trazabilidad Sprint 1 con cinco vacíos explícitos.
- Cinco decisiones de modelado propuestas y documentadas para aprobación.
- Modelo lógico actualizado con relación del reportante, versión optimista y asignaciones.
- Migración PostgreSQL incremental idempotente y validación posterior preparadas.
- Alembic formalizado con revisión inicial, downgrade explícito y dos pruebas estructurales.
- Revisión `20260825_01` aplicada y confirmada en Cloud SQL mediante `alembic current`.
- Esqueleto Python 3.12/FastAPI.
- Configuración por ambiente sin secretos en GitHub.
- Manejo uniforme de errores y `correlationId`.
- Máquina de estados inicial.
- Reapertura exclusiva por supervisor.
- Confirmación humana para rechazos.
- Validación de idempotencia.
- Modelo PostgreSQL desplegado con 22 tablas.
- Datos sintéticos cargados.
- Readiness integrado con Cloud SQL y esquema `siniestro_facil`.
- Prueba positiva de readiness HTTP 200 registrada.
- Compilación y suite backend completa aprobadas en Cloud Shell: 30/30 pruebas.
- Dos escenarios negativos de readiness aprobados con HTTP 503.
- Matriz endpoint–rol creada con tres decisiones de autorización explícitas.

## Pendiente para llegar a 100%

1. Fusionar PR #1 o resolver formalmente su dependencia.
2. Propagar las cinco decisiones ya materializadas al resto de criterios y contratos.
3. Resolver AR-01, AR-02 y AR-03; completar y aprobar OpenAPI.
4. Aprobar RBAC e identidad.
5. Mantener Alembic como mecanismo obligatorio para las próximas migraciones.
6. Descomponer y estimar las historias de Sprint 1.
7. Verificar la Definition of Ready de cada historia comprometida.

## Pull requests relacionados

- PR #1: modelo físico PostgreSQL; abierto, borrador y fusionable.
- PR #2: especificaciones e implementación Sprint 0; abierto, borrador y fusionable.
