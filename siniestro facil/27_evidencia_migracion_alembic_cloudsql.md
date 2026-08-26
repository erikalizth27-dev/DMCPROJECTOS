# Evidencia — Migración Alembic Sprint 0 en Cloud SQL

## Resultado

**APROBADO**. La revisión Alembic `20260825_01` fue aplicada y validada en
Cloud SQL desde Google Cloud Shell.

## Destino validado

| Elemento | Valor |
|---|---|
| Proyecto GCP | `project-77c17016-86bc-4fc4-a97` |
| Instancia Cloud SQL | `dmcappasistidaia` |
| Base PostgreSQL | `DMCSINIESTROFACIL` |
| Esquema | `siniestro_facil` |
| Revisión aplicada | `20260825_01` |

## Ejecución registrada

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 20260825_01,
      Ajustes de modelado acordados para Sprint 0.
OK: migración aplicada y revisión 20260825_01 validada.
```

## Validaciones satisfechas

- El proyecto, la instancia y la base coincidieron exactamente con la SPEC.
- La instancia se encontraba disponible para conexión.
- Alembic utilizó DDL transaccional de PostgreSQL.
- La ejecución terminó sin excepción.
- `alembic current` confirmó la revisión `20260825_01`.
- La contraseña no se imprimió ni se almacenó en GitHub.
- El proxy, `PGPASSWORD` y `DATABASE_URL` fueron limpiados al finalizar.

## Artefactos relacionados

- `backend/alembic/versions/20260825_01_sprint0_modelado.py`
- `backend/scripts/01_migrate_cloudsql.sh`
- `postgresql/06_validate_migration_sprint0.sql`

## Alcance

Esta evidencia acredita la aplicación de la migración y el control de versión
de Alembic. No acredita todavía la ejecución posterior de todas las pruebas
funcionales de constraints ni la suite backend completa.
