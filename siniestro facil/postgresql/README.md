# PostgreSQL — modelo físico y pruebas

Requisitos: PostgreSQL 14 o posterior y el cliente `psql`.

```bash
createdb siniestro_facil_test
psql -X -v ON_ERROR_STOP=1 -d siniestro_facil_test -f 01_schema.sql
psql -X -v ON_ERROR_STOP=1 -d siniestro_facil_test -f 02_test_constraints.sql
```

La prueba abre una transacción y ejecuta `ROLLBACK`; por ello no deja datos de prueba. Cada caso negativo verifica el `SQLSTATE` esperado: `23502` (`NOT NULL`), `23503` (FK), `23505` (`UNIQUE`), `23514` (`CHECK`) y `23000` (inmutabilidad de evidencia).

El DDL usa el esquema `siniestro_facil`. Para recrearlo desde cero en un entorno descartable:

```sql
DROP SCHEMA IF EXISTS siniestro_facil CASCADE;
```

Luego vuelva a ejecutar `01_schema.sql`.
