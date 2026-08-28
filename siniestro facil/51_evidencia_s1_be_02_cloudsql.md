# Evidencia de cierre técnico — S1-BE-02

## Resultado

S1-BE-02 — Detectar posible duplicado quedó validado en Google Cloud Shell
el 28 de agosto de 2026.

## Regla validada

- Coincidencia: misma placa y mismo día del evento.
- Resultado: HTTP 409 con código `POSSIBLE-DUPLICATE`.
- Privacidad: la respuesta no expone el identificador del caso coincidente.
- Decisión: revisión humana posterior.
- Exclusiones: no fusionar, eliminar ni descartar automáticamente.

## Suite automatizada

```text
collected 81 items
81 passed, 1 warning in 1.01s
```

La advertencia de transición de `starlette.testclient` no produjo fallos ni
afectó los criterios de aceptación.

## Prueba integrada con Cloud SQL

```text
Conflicto validado: POSSIBLE-DUPLICATE / HTTP 409
Caso sintético eliminado: 15
Limpieza validada: sin registros residuales
S1-BE-02 PostgreSQL: OK
```

La prueba utilizó el usuario `siniestro_app`, la base
`DMCSINIESTROFACIL` y el esquema `siniestro_facil`. El caso se creó con
datos sintéticos, se comprobó el conflicto y se eliminó al finalizar.

## Concurrencia

La persistencia utiliza un bloqueo transaccional de PostgreSQL derivado de
placa y fecha. Después de adquirirlo vuelve a comprobar la idempotencia y
la existencia de un caso para ese día. Esto evita que dos solicitudes
concurrentes creen expedientes paralelos.

## Conclusión

S1-BE-02 está técnicamente completado. Sprint 1 alcanza 65% y queda
habilitado el inicio de S1-BE-03.
