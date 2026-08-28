# Estado Sprint 2 — Backend Siniestro Fácil

## Estado general

- Avance: **40% confirmado**
- Rama: `agent/sprint-2-backend`
- Punto de partida: `main` después del cierre de Sprint 1 (`bfc1356`)
- Duración de referencia: 2 semanas
- Estado: S2-BE-02 validado automáticamente; prueba controlada PostgreSQL pendiente
- Validación inicial: **90/90 pruebas**, Alembic `20260828_02 (head)`
- Evidencia: `57_evidencia_linea_base_sprint_2_cloudshell.md`

## Objetivo

Entregar cobertura, transiciones de estado y gestión de evidencia inmutable, manteniendo trazabilidad, idempotencia, concurrencia optimista y privacidad por rol.

## Distribución porcentual

| Fase | Resultado | Peso | Acumulado |
|---|---|---:|---:|
| Preparación | Rama, alcance, trazabilidad y decisiones abiertas | 5% | 5% |
| Fundaciones | Contratos, modelos y pruebas base | 10% | 15% |
| S2-BE-01 | Verificación de cobertura y deducible | 20% | 35% |
| S2-BE-02 | Transiciones de estado auditables | 25% | 60% |
| S2-BE-03 | Evidencia inmutable y metadatos | 25% | 85% |
| Integración | PostgreSQL, almacenamiento y pruebas integrales | 10% | 95% |
| Cierre | Evidencias, acta y PR listo para revisión | 5% | 100% |

## Incrementos propuestos

### S2-BE-01 — Cobertura y deducible

- Consultar cobertura aplicable y deducible.
- Mantener temporalmente el adaptador simulado si la API real aún no existe.
- Registrar el resultado en la línea de tiempo.
- No producir un rechazo definitivo sin decisión humana.

### S2-BE-02 — Transiciones de estado

- Exigir rol autorizado, motivo y versión conocida del siniestro.
- Aplicar la máquina de estados aprobada.
- Incrementar `siniestro.version` atómicamente.
- Responder HTTP 409 ante versión desactualizada.
- Registrar cada transición en auditoría.

### S2-BE-03 — Evidencia inmutable

- Registrar evidencia vinculada al siniestro.
- Conservar hash, metadatos, fecha, fuente y referencia al objeto.
- Preservar el original y diferenciar versiones derivadas.
- Aplicar idempotencia, RBAC y auditoría de accesos sensibles.
- Integrar Cloud Storage solamente después de aprobar bucket, región y retención.

## Avance de S2-BE-02

- Caso de uso de transición implementado.
- Endpoint `POST /api/v1/siniestros/{siniestroId}/estado` implementado.
- RBAC, alcance privado, versión esperada y auditoría atómica incorporados.
- Ocho pruebas unitarias y API añadidas.
- Validación automática: **98/98 pruebas aprobadas**.
- Evidencia: `58_evidencia_pruebas_s2_be_02_cloudshell.md`.
- Pendiente: ejecutar escenario controlado contra PostgreSQL.

## Decisiones pendientes para Definition of Ready

- **S2-DEC-01:** confirmar si continúa el adaptador simulado de pólizas durante Sprint 2 o proporcionar la API real.
- **S2-DEC-02:** aprobar bucket, región y política de retención de Cloud Storage para evidencias.

## Línea base de calidad

La validación inicial del Sprint 2 aprobó **90/90 pruebas** y confirmó Alembic en `20260828_02 (head)`. Sprint 2 debe preservar esas pruebas y añadir pruebas unitarias, API, persistencia e integración para cada incremento.

## Restricciones

- No se ejecutan migraciones ni cambios en GCP sin validación previa y pasos explícitos en Cloud Shell.
- No se almacenan secretos en Git.
- El PR de Sprint 2 no se fusiona sin autorización explícita del Product Owner.
