# Evidencia final S4-BE-01 — PostgreSQL

## Contexto

- Fecha: 2 de septiembre de 2026.
- Entorno: Google Cloud Shell y Cloud SQL PostgreSQL.
- Rama: `agent/sprint-4-backend`.
- Script: `backend/scripts/09_validate_s4_be_01_postgresql.py`.

## Resultado

La validación seleccionó el siniestro 4 y creó datos sintéticos exclusivamente dentro de una transacción reversible.

- Inspección sintética: 11.
- Transición: `en_evaluacion -> inspeccion_programada`.
- Versión: `0 -> 1`.
- Persistencia de inspección: **OK**.
- Auditoría atómica: **OK**.
- Consulta con alcance: **OK**.
- Conflicto de versión desactualizada: **HTTP 409 — OK**.
- Rollback: **ejecutado**.

## Limpieza comprobada

- Estado y versión originales restaurados.
- Inspección sintética eliminada.
- Auditoría sintética eliminada.
- Asignación sintética eliminada.
- Identidad y usuario sintéticos eliminados.
- Registros residuales: **0**.

## Evidencia complementaria

- Regresión: **233/233 pruebas aprobadas en 2.28 segundos**.
- Alembic: `20260902_02 (head)`.
- Advertencia conocida: deprecación de Starlette TestClient con httpx; no afecta el resultado funcional.

## Conclusión

S4-BE-01 cumple programación y consulta de inspección, RBAC por asignación, transición válida, concurrencia, control de versión y auditoría atómica sobre PostgreSQL. El incremento queda completado.
