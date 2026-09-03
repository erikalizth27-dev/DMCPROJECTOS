# Evidencia final S6-BE-03 — PostgreSQL

## Entorno

- Fecha: 2026-09-03.
- Base: `DMCSINIESTROFACIL`.
- Esquema: `siniestro_facil`.
- Alembic: `20260903_04 (head)`.
- Script: `backend/scripts/26_validate_s6_be_03_postgresql.py`.

## Resultados

- Siniestro fuente identificado explícitamente.
- Tiempo hasta primera asistencia: 300 segundos.
- Tiempo hasta decisión: 1200 segundos.
- Período y fuentes conservados.
- Indicadores sin fuente aprobada presentados como `no_disponible`.
- Ausencia de datos no convertida a cero.
- Supervisor sin identidad persistida rechazado con HTTP 403.
- Operador rechazado con HTTP 403.
- Período sin casos presentado como `no_disponible`.

## Limpieza

La prueba terminó con rollback. El siniestro, asistencia, decisión, proveedor, identidad y usuario sintéticos fueron eliminados. No quedaron residuos.

## Conclusión

**S6-BE-03 PostgreSQL: OK.** El incremento queda completado sin fórmulas, fuentes ni agregaciones inventadas.
