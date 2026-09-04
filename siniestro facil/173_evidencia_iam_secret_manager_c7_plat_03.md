# Evidencia — Identidades y secreto de runtime C7-PLAT-03

## Resultado

Se crearon identidades separadas para la ejecución del backend y las migraciones del ambiente piloto.

## Identidades

- Runtime: `siniestro-backend-piloto@project-77c17016-86bc-4fc4-a97.iam.gserviceaccount.com`.
- Migración: `siniestro-migrator-piloto@project-77c17016-86bc-4fc4-a97.iam.gserviceaccount.com`.
- Estado reportado: habilitadas.
- Ambas identidades son independientes.

## Secret Manager

- Secreto: `siniestro-database-url-piloto`.
- Versión: `1`.
- Estado: `enabled`.
- Creación reportada: `2026-09-04T01:09:16Z`.
- Replicación: administrada por el servicio según la decisión aprobada.
- El valor no fue mostrado ni registrado en GitHub.

## Política aplicada

La función `roles/secretmanager.secretAccessor` fue concedida únicamente a la cuenta de runtime sobre este secreto específico.

La cuenta migradora no recibió acceso al secreto del usuario de ejecución. Su conexión y secreto independientes se configurarán con la etapa exclusiva de migraciones.

## Estado

- Identidad runtime: creada.
- Identidad migradora: creada.
- Secreto runtime: creado y versionado.
- Acceso mínimo al secreto: validado.
- Despliegue Cloud Run: pendiente.
