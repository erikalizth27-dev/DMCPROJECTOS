# Evidencia PostgreSQL S2-BE-02 — Transiciones de estado

## Contexto

- Fecha: 28 de agosto de 2026.
- Rama: `agent/sprint-2-backend`.
- Incremento: `S2-BE-02`.
- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Instancia: `dmcappasistidaia`.
- Base: `DMCSINIESTROFACIL`.
- Esquema: `siniestro_facil`.

## Escenario ejecutado

Se seleccionó el siniestro 4 en estado `reportado` y versión 0. Dentro de una transacción exterior se creó una identidad sintética de supervisor y se invocó el repositorio PostgreSQL real.

## Resultado

```text
Siniestro seleccionado: 4
Estado original: reportado
Versión original: 0
Supervisor sintético creado: 13
Transición validada: reportado -> validando_cobertura
Versión validada: 0 -> 1
Auditoría atómica: OK
Conflicto de versión desactualizada: STATE-VERSION-CONFLICT / HTTP 409 — OK
S2-BE-02 PostgreSQL: OK
ROLLBACK ejecutado
Estado original restaurado: OK
Versión original restaurada: OK
Auditoría sintética eliminada: OK
Identidad sintética eliminada: OK
Limpieza validada: sin registros residuales
VALIDACIÓN S2-BE-02 COMPLETADA
```

## Controles confirmados

- Máquina de estados aplicada.
- Incremento atómico de versión.
- Conflicto HTTP 409 ante versión desactualizada.
- Evento de auditoría en la misma transacción.
- Restauración del estado y versión originales.
- Eliminación de identidad y auditoría sintéticas.
- Cero registros residuales.

## Conclusión

`S2-BE-02` cumple sus criterios técnicos y queda completado. La prueba no requirió migraciones ni dejó cambios permanentes en Cloud SQL.
