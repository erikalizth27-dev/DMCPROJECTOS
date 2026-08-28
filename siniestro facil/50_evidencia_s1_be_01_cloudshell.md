# Evidencia de cierre técnico — S1-BE-01

## Resultado

S1-BE-01 — Registrar siniestro quedó validado en Google Cloud Shell el
28 de agosto de 2026.

## Entorno

- Proyecto GCP: `project-77c17016-86bc-4fc4-a97`.
- Instancia Cloud SQL: `dmcappasistidaia`.
- Base de datos: `DMCSINIESTROFACIL`.
- Esquema: `siniestro_facil`.
- Usuario de aplicación: `siniestro_app`.
- Python: 3.12.3.
- Pytest: 8.4.2.

## Base de datos

- Conexión mediante Cloud SQL Auth Proxy: correcta.
- Acceso al esquema: confirmado.
- Tablas visibles antes de la migración: 24.
- Migración aplicada: `20260828_01 (head)`.
- Tabla incorporada: `siniestro_facil.solicitud_idempotente`.
- Permisos temporales `CREATE` y `REFERENCES`: retirados después de migrar.
- Archivo `.env`: permisos `600` e ignorado por Git.

## Validación automatizada

```text
collected 77 items
77 passed, 1 warning in 0.99s
```

La advertencia corresponde a la transición futura de
`starlette.testclient` desde `httpx` hacia `httpx2`; no produjo fallos ni
afectó los criterios de aceptación del incremento.

## Capacidades verificadas

- Validación de póliza, documento, placa y vigencia.
- Endpoint `POST /api/v1/siniestros`.
- Persistencia PostgreSQL del siniestro.
- Evento inicial de auditoría en la misma transacción.
- Idempotencia persistente y conflicto ante contenido diferente.
- Rollback transaccional ante errores.
- Preservación de todas las pruebas de Sprint 0 y fundaciones de Sprint 1.

## Conclusión

S1-BE-01 está técnicamente completado. Sprint 1 alcanza 45% y queda
habilitado el inicio de S1-BE-02.
