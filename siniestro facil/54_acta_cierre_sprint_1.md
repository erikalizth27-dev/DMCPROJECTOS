# Acta de cierre — Sprint 1 Backend

## Estado

**Sprint 1 cerrado al 100% en la rama `agent/sprint-1-backend`.**

La fusión a `main` no forma parte de este cierre y requiere autorización
explícita del Product Owner.

## Compromiso completado

| Incremento | Puntos | Resultado |
|---|---:|---|
| S1-BE-01 — Registrar siniestro | 8 | Completado |
| S1-BE-02 — Detectar posible duplicado | 5 | Completado |
| S1-BE-03 — Consultar vista inicial | 5 | Completado |
| **Total** | **18** | **Completado** |

## Entregables

- Registro idempotente mediante `POST /api/v1/siniestros`.
- Persistencia atómica de siniestro, auditoría e idempotencia.
- Conflicto revisable por coincidencia de placa y día.
- Concurrencia serializada sin fusión automática.
- Consulta `GET /api/v1/siniestros/{siniestroId}`.
- RBAC y alcance resueltos desde PostgreSQL.
- Privacidad uniforme para recurso inexistente o no visible.
- Auditoría del acceso transversal del supervisor.
- Migraciones `20260828_01` y `20260828_02` aplicadas.

## Evidencia

- S1-BE-01: 77/77 pruebas y validación Cloud SQL.
- S1-BE-02: 81/81 pruebas y conflicto integrado sin residuos.
- S1-BE-03: 90/90 pruebas y alcance/auditoría integrados sin residuos.
- Validación final: 90/90 pruebas en 1.12 s.
- Resultado: `SPRINT 1 VALIDACIÓN INTEGRAL: OK`.

## Seguridad

- `.env` permanece fuera de Git y con permisos locales restrictivos.
- El backend no almacena JWT, secretos ni credenciales.
- Los permisos temporales de migración fueron retirados y verificados.
- El usuario de aplicación conserva privilegios operativos mínimos.

## Alcance diferido

- Integración real con pólizas; continúa el adaptador aprobado S1-DEC-01.
- Decisión humana posterior sobre posibles duplicados.
- Orden válida para habilitar consulta del taller.
- Adaptador criptográfico definitivo de Identity Platform.
- CI/CD, observabilidad y despliegue operativo de servicios en GCP.

## Cierre

Los criterios de éxito del sprint se cumplieron, los 18 puntos comprometidos
fueron completados y la rama queda lista para revisión mediante Pull Request.
