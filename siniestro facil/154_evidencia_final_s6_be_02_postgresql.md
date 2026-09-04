# Evidencia final S6-BE-02 — PostgreSQL

## Entorno

- Fecha: 2026-09-03.
- Base: `DMCSINIESTROFACIL`.
- Esquema: `siniestro_facil`.
- Alembic: `20260903_04 (head)`.
- Script: `backend/scripts/25_validate_s6_be_02_postgresql.py`.

## Resultados

- Operador con asignación activa accedió al expediente.
- Detalle operativo visible.
- Detalle sensible redactado para el operador.
- Operador sin asignación recibió respuesta privada HTTP 404.
- Paginación estable por cursor.
- Supervisor recibió detalle completo.
- Consulta sensible registrada con la identidad del supervisor.
- Línea de tiempo obtenida sin duplicar ni modificar fuentes.

## Limpieza

La validación se ejecutó dentro de una transacción externa y terminó con rollback. Los eventos, auditoría, asignación, identidades y usuarios sintéticos fueron eliminados. No quedaron registros residuales.

## Conclusión

**S6-BE-02 PostgreSQL: OK.** El incremento queda completado con alcance, proyección por rol, protección de información sensible, paginación y auditoría persistente.
