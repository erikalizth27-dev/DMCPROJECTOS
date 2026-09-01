# Evidencia PostgreSQL S2-BE-01 — Cobertura y deducible

## Contexto

- Fecha: 28 de agosto de 2026.
- Rama: `agent/sprint-2-backend`.
- Incremento: `S2-BE-01`.
- Decisión: `S2-DEC-01` aprobada.
- Base: `DMCSINIESTROFACIL`.
- Adaptador: simulado.

## Resultado

```text
Conflicto de versión: HTTP 409 — OK
Siniestro probado: 4
Póliza simulada: SYN-20260820-POL-0001
Deducible: 525.00
Estado: reportado -> validando_cobertura
Versión: 0 -> 1
Persistencia de cobertura: OK
Auditoría atómica: OK
S2-BE-01 PostgreSQL: OK
ROLLBACK ejecutado
Estado y versión restaurados: OK
Cobertura restaurada: OK
Auditoría sintética eliminada: OK
Identidad sintética eliminada: OK
Limpieza validada: sin registros residuales
VALIDACIÓN S2-BE-01 COMPLETADA
```

## Controles confirmados

- Consulta de póliza mediante el adaptador simulado aprobado.
- Deducible `525.00` obtenido y persistido.
- Estado actualizado de `reportado` a `validando_cobertura`.
- Versión incrementada de 0 a 1.
- Auditoría `cobertura_verificada` registrada atómicamente.
- Conflicto HTTP 409 ante versión desactualizada.
- Sin rechazo automático.
- Rollback completo y cero registros residuales.

## Conclusión

`S2-BE-01` cumple sus criterios técnicos y queda completado. No se aplicaron migraciones ni cambios permanentes en Cloud SQL.
