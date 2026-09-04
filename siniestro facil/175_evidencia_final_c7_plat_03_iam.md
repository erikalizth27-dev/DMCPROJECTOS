# Evidencia final — C7-PLAT-03 IAM y Secret Manager

## Resultado

**C7-PLAT-03 aprobado.**

Las identidades de runtime y migración quedaron separadas, con secretos independientes y acceso funcional a Cloud SQL.

## Runtime

- Cuenta: `siniestro-backend-piloto@project-77c17016-86bc-4fc4-a97.iam.gserviceaccount.com`.
- Secreto: `siniestro-database-url-piloto:1`.
- Acceso al secreto: exclusivo para la cuenta de runtime.
- Validación: readiness de Cloud Run aprobado.

## Migración

- Cuenta: `siniestro-migrator-piloto@project-77c17016-86bc-4fc4-a97.iam.gserviceaccount.com`.
- Rol PostgreSQL: `siniestro_migrator`.
- Secreto: `siniestro-migrator-database-url-piloto:1`.
- Acceso al secreto: exclusivo para la cuenta migradora.
- Cloud Run Job: `siniestro-facil-migrator-piloto`.
- Ejecución validada: `siniestro-facil-migrator-piloto-rsq88`.
- Resultado: ejecución completada correctamente.

## Privilegios PostgreSQL verificados

- `rolcanlogin = true`.
- `rolsuper = false`.
- `rolcreatedb = false`.
- `rolcreaterole = false`.
- Propietario de `siniestro_facil.alembic_version`: `siniestro_migrator`.
- Permisos Alembic: SELECT, INSERT, UPDATE y DELETE.
- Permisos del esquema: USAGE y CREATE.

## Incidente controlado

La primera ejecución alcanzó PostgreSQL pero falló por falta de acceso a `alembic_version`. Esto confirmó que la conexión, el secreto y la identidad GCP eran válidos.

Se transfirió la propiedad de la tabla de versión al rol migrador y se concedieron permisos explícitos. La ejecución posterior finalizó exitosamente.

## Controles

- No se compartieron contraseñas.
- Los valores de los secretos no se registraron en GitHub.
- Runtime no utiliza la credencial migradora.
- Migración no utiliza la credencial de runtime.
- No se otorgaron privilegios de superusuario, creación de bases o creación de roles.
