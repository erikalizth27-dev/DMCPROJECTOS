# Evidencia de cierre técnico — S1-BE-03

## Resultado

S1-BE-03 — Consultar vista inicial del siniestro quedó validado en Google
Cloud Shell el 28 de agosto de 2026.

## Migración y seguridad

- Migración aplicada: `20260828_02 (head)`.
- Tabla técnica: `siniestro_facil.identidad_actor`.
- Resolución de identidad: `subject` + `tenant_id`.
- El modelo no almacena JWT, secretos ni credenciales.
- Permisos temporales `CREATE` y `REFERENCES`: retirados y verificados.

## Suite automatizada

```text
collected 90 items
90 passed, 1 warning in 1.20s
```

La advertencia de transición de `starlette.testclient` no produjo fallos ni
afectó los criterios del incremento.

## Prueba integrada con Cloud SQL

```text
Asegurado — caso propio: OK
Asegurado — caso ajeno oculto: OK
Operador — asignación activa: OK
Taller — sin orden válida: OK
Supervisor — acceso transversal: OK
Auditoría sensible: OK
Limpieza validada: sin identidades residuales
S1-BE-03 PostgreSQL: OK
```

## Privacidad y auditoría

- El servicio no diferencia externamente un recurso inexistente de uno fuera
  del alcance autorizado.
- El supervisor se resuelve contra PostgreSQL y su consulta transversal crea
  un evento `consulta_sensible` con sujeto, organización, acción y resultado.
- No se registra el token.
- Las asociaciones, asignaciones, usuarios y eventos sintéticos creados para
  la prueba fueron eliminados al finalizar.

## Conclusión

S1-BE-03 está técnicamente completado. Los tres incrementos comprometidos
están implementados y Sprint 1 alcanza 85%.
