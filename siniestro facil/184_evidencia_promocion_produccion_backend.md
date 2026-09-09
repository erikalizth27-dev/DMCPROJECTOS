# Evidencia — Promoción Docker del backend a producción

## Resultado

- Estado: **despliegue productivo validado**.
- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Región: `us-central1`.
- Servicio: `siniestro-facil-backend-prod`.
- Exposición: privada.
- Base aislada: `DMCSINIESTROFACIL_PROD`.
- Esquema: `siniestro_facil`.

## Modelo y migración

- El modelo físico base se aplicó desde `postgresql/01_schema.sql`.
- Alembic se ejecutó mediante el job Docker `siniestro-facil-migrator-prod`.
- Ejecución aprobada: `siniestro-facil-migrator-prod-h9r68`.
- Identidad migradora: `siniestro-migrator-prod`.
- Runtime y migración usan identidades y secretos independientes.
- Revisión Alembic validada: `20260903_04`.
- Tablas del modelo físico base: 22.
- Tablas finales registradas después de las migraciones: 36.

## Incidente controlado

La primera ejecución, `siniestro-facil-migrator-prod-485zm`, falló porque la revisión inicial de Alembic presupone la existencia del modelo físico base y la base de producción contenía únicamente el esquema vacío. No se produjo una migración parcial debido al DDL transaccional.

Se aplicó `postgresql/01_schema.sql` con 22 tablas y se repitió el job. La segunda ejecución finalizó correctamente.

## Imagen y revisión

- Imagen del backend desplegada por digest: `us-central1-docker.pkg.dev/project-77c17016-86bc-4fc4-a97/siniestro-facil/backend@sha256:e95b167ecea3a815d69da15b1ff8890bff515d0de825f3cfb25fda5a7bb2d8cd`.
- Imagen del migrador fijada por digest: `us-central1-docker.pkg.dev/project-77c17016-86bc-4fc4-a97/siniestro-facil/backend@sha256:e3744b7bbc52295b0db75a8a712348404cd294495212a13f61b46967c75bfa50`.
- Ejecución final: `siniestro-facil-migrator-prod-wbmft`.
- Resultado final: `EXECUTION_SUCCEEDED`.
- Finalización: `2026-09-09T14:32:09.586274Z`.
- Revisión: `siniestro-facil-backend-prod-00001-dg8`.
- Tráfico: 100% a la revisión lista.
- Cuenta de runtime: `siniestro-backend-prod@project-77c17016-86bc-4fc4-a97.iam.gserviceaccount.com`.

## Validación autenticada

- Acceso sin autenticación a `/health/live`: `HTTP 403`.
- Después de la migración, ambos endpoints permanecieron saludables.
- `/health/live` autenticado: `status=ok`, versión `0.1.0`, `HTTP 200`.
- `/health/ready` autenticado: `status=ready`, sin errores, `HTTP 200`.
- Secretos: referenciados desde Secret Manager; ningún valor se registró en GitHub.

## Conclusión

La promoción controlada del backend Docker al ambiente de producción quedó ejecutada y validada. Los pendientes de autenticación final de usuarios, escalado, SLO, alertas y ambientes adicionales permanecen fuera de esta promoción por decisión del Product Owner.
