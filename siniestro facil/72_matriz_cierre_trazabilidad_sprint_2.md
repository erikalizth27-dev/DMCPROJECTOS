# Matriz de cierre y trazabilidad — Sprint 2 Backend

| Incremento | Resultado | API principal | Persistencia | Evidencia | Estado |
|---|---|---|---|---|---|
| S2-BE-01 | Verificación de cobertura y deducible | Verificación de cobertura del siniestro | cobertura, siniestro, evento_linea_tiempo | `61`, `62`, `63` | Completado |
| S2-BE-02 | Transición auditable con concurrencia optimista | Cambio de estado del siniestro | siniestro, evento_linea_tiempo | `58`, `59` | Completado |
| S2-BE-03 | Registro de evidencia inmutable e idempotente | POST /api/v1/siniestros/{id}/evidencias | evidencia, solicitud_evidencia_idempotente, evento_linea_tiempo | `65` a `70` | Completado |
| Sprint 2 | Integración completa | Contratos API preservados | PostgreSQL y Cloud Storage | `71_evidencia_validacion_integral_sprint_2.md` | Validado |

## Decisiones

| Decisión | Resolución | Estado |
|---|---|---|
| S2-DEC-01 | Continuar temporalmente con adaptador simulado de pólizas | Aprobada |
| S2-DEC-02 | Bucket en us-central1, acceso uniforme, PAP, versionado y sin retention lock | Aprobada |

## Criterios transversales comprobados

- RBAC y privacidad por alcance.
- Auditoría atómica.
- Idempotencia persistente.
- Control de versión y HTTP 409.
- SHA-256 e inmutabilidad de evidencia.
- Rollback y limpieza sin residuos sintéticos.
- Migración Alembic `20260901_01 (head)`.
- Suite integral: 130/130 pruebas aprobadas.
