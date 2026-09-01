# Evidencia de línea base Sprint 2 — Cloud Shell

## Contexto

- Fecha: 28 de agosto de 2026.
- Rama: `agent/sprint-2-backend`.
- Proyecto GCP: `project-77c17016-86bc-4fc4-a97`.
- Instancia Cloud SQL: `dmcappasistidaia`.
- Base de datos: `DMCSINIESTROFACIL`.
- Usuario de aplicación: `siniestro_app`.
- Proxy: `127.0.0.1:5432`.

## Validación de conectividad

La conexión realizada con SQLAlchemy confirmó:

- acceso a `DMCSINIESTROFACIL`;
- usuario `siniestro_app`;
- privilegio `USAGE` sobre `siniestro_facil`;
- 26 tablas visibles;
- conexión Cloud SQL satisfactoria.

## Validación automatizada

Comandos ejecutados:

```bash
python -m compileall -q src tests alembic
python -m pytest -v
alembic current
```

Resultado:

```text
90 passed, 1 warning in 1.15s
20260828_02 (head)
SPRINT 2 — LÍNEA BASE VALIDADA
```

La advertencia corresponde a `StarletteDeprecationWarning` por la integración entre `starlette.testclient` y `httpx`; no produjo fallos y queda como deuda técnica no bloqueante.

## Conclusión

La rama de Sprint 2 parte de una línea base verde, conectada a Cloud SQL y con un único `head` de Alembic. No se aplicaron nuevas migraciones ni se modificó infraestructura durante esta validación.
