# Estado actual — Sprint 0 Backend

## Avance general

**99% completado**.

El porcentaje se calcula sobre los siete frentes definidos en `20_plan_detallado_sprint_0.md`. No incluye CI/CD, observabilidad ni operación GCP, porque fueron retirados expresamente del alcance.

| Frente | Avance | Evidencia | Pendiente principal |
|---|---:|---|---|
| 1. Consolidación SDD | 100% | DM-01 a DM-05 aprobadas y propagadas a criterios, reglas, seguridad, backlog y trazabilidad | Aplicar control de cambios a futuras decisiones |
| 2. Diseño de arquitectura GCP | 85% | Identity Platform para personas e IAM para servicios aprobados; arquitectura completamente GCP | Confirmar regiones y separación de ambientes |
| 3. Contrato OpenAPI | 100% | OpenAPI 0.2.0-draft aprobado por Product Owner; 11 operaciones, 14 esquemas, 13 ejemplos y 4 pruebas | Aplicar control formal de cambios a futuras versiones |
| 4. Datos y migraciones | 100% | PR #1 fusionado en main; 22 tablas, constraints, datos sintéticos y Alembic validados | Conservar la evidencia y usar Alembic para cambios futuros |
| 5. Seguridad, RBAC y auditoría | 100% | RBAC, Identity Platform/IAM, claims mínimos, alcance y controles aprobados | Mantener trazabilidad y denegación por defecto |
| 6. Esqueleto backend local | 100% | Contrato de claims, configuración y suite completa 53/53 aprobados en Cloud Shell | Mantener la línea base verde |
| 7. Refinamiento de Sprint 1 | 95% | S1-BE-01, S1-BE-02 y S1-BE-03 comprometidas por 18 puntos; trazabilidad y alcance registrados | Resolver las dos condiciones pendientes de DoR |

Promedio ponderado y redondeado: **99%**.

## Completado

- Plan y alcance de Sprint 0.
- Arquitectura backend y GCP documentada.
- Contrato OpenAPI ampliado y validado con 11 operaciones y 14 esquemas.
- Contratos Pydantic para siniestros, estados, evidencias, asistencia, presupuestos, alertas y pagos.
- Nueve pruebas de contratos Pydantic aprobadas en Cloud Shell.
- Política RBAC ejecutable y catorce pruebas de autorización y separación de funciones.
- Backlog de Sprint 1 refinado en seis incrementos verticales.
- Matriz de trazabilidad Sprint 1 con cinco vacíos explícitos.
- Cinco decisiones de modelado aprobadas, documentadas y trazadas.
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
- Línea base anterior de 30/30 pruebas preservada.
- Nueva suite posterior a AR-01/02/03 aprobada en Cloud Shell: 41/41 pruebas.
- Dos escenarios negativos de readiness aprobados con HTTP 503.
- Matriz endpoint–rol creada y AR-01, AR-02 y AR-03 aprobadas.
- Pagos separados en preparación/autorización y alertas modeladas por nivel de detalle.
- OpenAPI validado con 11 rutas, 11 operaciones únicas y 14 esquemas.
- Ocho ejemplos de comandos y cinco ejemplos de error agregados sin datos reales.
- Suite con ejemplos OpenAPI aprobada en Cloud Shell: 42/42 pruebas.
- Contrato OpenAPI 0.2.0-draft aprobado formalmente por el Product Owner.
- ID-01 a ID-06 aprobadas y propagadas a configuración, seguridad y OpenAPI.
- Contrato de claims verificados implementado con once pruebas nuevas.
- Suite de identidad y backend aprobada en Cloud Shell: 53/53 pruebas.
- Plan de cierre controlado de la dependencia PR #1 documentado.
- PR #1 fusionado en `main` mediante squash; dependencia de PR #2 cerrada.
- DM-01 a DM-05 aprobadas y propagadas a criterios, reglas, seguridad, backlog y trazabilidad.
- DM-05 fija retención de auditoría por cinco años desde el cierre, sin eliminación automática y con revisión normativa previa a producción.
- Alembic formalizado como política obligatoria para cambios incrementales.
- Compromiso de Sprint 1 aprobado: S1-BE-01, S1-BE-02 y S1-BE-03 por 18 puntos.

## Pendiente para llegar a 100%

1. Aprobar o rechazar el adaptador simulado de pólizas para S1-BE-01.
2. Aprobar o reemplazar la regla provisional de duplicidad por placa y fecha para S1-BE-02.

## Pull requests relacionados

- PR #1: modelo físico PostgreSQL; fusionado en `main` (`cede25b5`).
- PR #2: especificaciones e implementación Sprint 0; abierto, borrador y fusionable.
