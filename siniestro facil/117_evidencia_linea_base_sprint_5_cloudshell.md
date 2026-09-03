# Evidencia de línea base — Sprint 5 Cloud Shell

## Fecha y entorno

- Fecha: 3 de septiembre de 2026.
- Rama: `agent/sprint-5-backend`.
- Proyecto GCP: `project-77c17016-86bc-4fc4-a97`.
- Base: `DMCSINIESTROFACIL`.
- Python: 3.12.3.
- Pytest: 8.4.2.

## Comandos

```bash
python -m compileall -q src tests alembic scripts
python -m pytest -v
alembic current
```

## Resultado

- Compilación: aprobada.
- Pruebas: **270/270 aprobadas**.
- Duración: **2.79 segundos**.
- Fallos: cero.
- Alembic: `20260902_05 (head)`.
- Advertencias: una advertencia deprecada de Starlette sobre `httpx`; no bloqueante.

## Conclusión

La línea base heredada de Sprint 4 está estable y habilita el desarrollo de las fundaciones antifraude de Sprint 5.
