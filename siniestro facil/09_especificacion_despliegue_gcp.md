# Especificación de despliegue — Google Cloud SQL

## Propósito

Esta especificación identifica el destino autorizado para desplegar el modelo físico PostgreSQL de **Siniestro Fácil**. No contiene contraseñas, tokens, certificados ni otros secretos.

## Identificación del entorno

| Recurso | Valor |
|---|---|
| Proveedor | Google Cloud Platform (GCP) |
| Nombre visible del proyecto | `My First Project` |
| Project ID | `project-77c17016-86bc-4fc4-a97` |
| Project number | `112296734690` |
| Servicio | Cloud SQL for PostgreSQL |
| Instancia Cloud SQL | `dmcappasistidaia` |
| Región | `us-central1` |
| Versión del motor | `POSTGRES_18` |
| Estado verificado | `RUNNABLE` |
| Connection name | `project-77c17016-86bc-4fc4-a97:us-central1:dmcappasistidaia` |
| Base de datos | `DMCSINIESTROFACIL` |
| Esquema de aplicación | `siniestro_facil` |

> **Sensibilidad a mayúsculas:** el nombre de la base debe utilizarse exactamente como `DMCSINIESTROFACIL`. La instancia correcta es `dmcappasistidaia`; no confundirla con `dmcappasistidoia`.

## Artefactos de despliegue

| Artefacto | Ruta |
|---|---|
| Modelo lógico de referencia | `siniestro facil/07_modelo_logico.md` |
| Modelo físico documentado | `siniestro facil/08_modelo_fisico.md` |
| DDL PostgreSQL | `siniestro facil/postgresql/01_schema.sql` |
| Pruebas de constraints | `siniestro facil/postgresql/02_test_constraints.sql` |
| Guía de ejecución | `siniestro facil/postgresql/README.md` |

El archivo `07_modelo_logico.md` es una especificación documental y **no se ejecuta**. El artefacto desplegable es `01_schema.sql`.

## Variables operativas

```bash
export GCP_PROJECT_ID="project-77c17016-86bc-4fc4-a97"
export CLOUDSQL_INSTANCE="dmcappasistidaia"
export CLOUDSQL_DATABASE="DMCSINIESTROFACIL"
export INSTANCE_CONNECTION_NAME="project-77c17016-86bc-4fc4-a97:us-central1:dmcappasistidaia"
```

## Validaciones previas

```bash
gcloud projects describe "$GCP_PROJECT_ID" \
  --format='table(name,projectId,projectNumber,lifecycleState)'

gcloud sql instances describe "$CLOUDSQL_INSTANCE" \
  --project="$GCP_PROJECT_ID" \
  --format='yaml(name,databaseVersion,region,state,connectionName)'

gcloud sql databases list \
  --project="$GCP_PROJECT_ID" \
  --instance="$CLOUDSQL_INSTANCE" \
  --filter="name=$CLOUDSQL_DATABASE" \
  --format='table(name,charset,collation)'
```

## Conexión

```bash
gcloud sql connect "$CLOUDSQL_INSTANCE" \
  --project="$GCP_PROJECT_ID" \
  --user=postgres \
  --database="$CLOUDSQL_DATABASE"
```

La contraseña se introduce únicamente en el prompt seguro de Cloud Shell. No debe almacenarse en este repositorio ni enviarse por chat.

En `psql`, ejecutar cada instrucción por separado:

```sql
\conninfo

SELECT current_database() AS base_actual,
       current_user AS usuario_actual,
       version();
```

## Criterio antes del despliegue

```sql
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'siniestro_facil';

SELECT count(*) AS tablas_existentes
FROM information_schema.tables
WHERE table_schema = 'siniestro_facil'
  AND table_type = 'BASE TABLE';
```

Si existen tablas en `siniestro_facil`, no se debe ejecutar el DDL inicial sin preparar y revisar una migración. La última verificación registrada encontró la base de datos conectada y **cero tablas** en ese esquema.

## Despliegue y pruebas

Desde `psql`:

```sql
\set ON_ERROR_STOP on
\i '/home/erikalizth27/DMCPROJECTOS/siniestro facil/postgresql/01_schema.sql'
\i '/home/erikalizth27/DMCPROJECTOS/siniestro facil/postgresql/02_test_constraints.sql'
```

Las pruebas terminan con `ROLLBACK` y no deben dejar datos de prueba.

## Criterios de aceptación

- La conexión reporta la base `DMCSINIESTROFACIL`.
- La instancia está en estado `RUNNABLE`.
- El esquema `siniestro_facil` contiene 22 tablas base después del despliegue.
- El DDL finaliza sin errores con `ON_ERROR_STOP`.
- Todas las pruebas emiten mensajes `OK`.
- La suite de pruebas finaliza con `ROLLBACK`.
- Ningún secreto queda registrado en GitHub.
