# Evidencia migración y regresión S2-BE-03

## Contexto

- Fecha: 1 de septiembre de 2026.
- Rama: `agent/sprint-2-backend`.
- Migración: `20260901_01`.
- Base: `DMCSINIESTROFACIL`.

## Migración

```text
Running upgrade 20260828_02 -> 20260901_01
20260901_01 (head)
```

## Seguridad posterior

```text
puede_crear: false
puede_referenciar evidencia: false
tabla: siniestro_facil.solicitud_evidencia_idempotente
```

Los permisos temporales `CREATE` y `REFERENCES` fueron revocados después de la migración.

## Regresión

```text
130 passed, 1 warning in 2.15s
S2-BE-03 — MIGRACIÓN Y REGRESIÓN: OK
```

## Conclusión

La migración quedó aplicada en un único head, el principio de mínimo privilegio fue restaurado y la suite completa continúa verde. Falta la prueba PostgreSQL final de persistencia, idempotencia, auditoría e inmutabilidad con rollback.
