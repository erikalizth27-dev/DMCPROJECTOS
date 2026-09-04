# Evidencia final — C7-PLAT-04 CI/CD

## Resultado

**C7-PLAT-04 aprobado.**

El pipeline controlado de Cloud Build completó todas sus etapas correctamente.

## Ejecución final

- Build ID: `e1e98b8a-6d78-4e0b-a7e9-4a1b469c8c91`.
- Inicio: `2026-09-04T02:00:46Z`.
- Duración: 5 minutos 30 segundos.
- Estado: `SUCCESS`.
- Imagen: `us-central1-docker.pkg.dev/project-77c17016-86bc-4fc4-a97/siniestro-facil/backend:753e6456c2db`.
- Commit: `753e6456c2dbf78c6036f31e6d6bd7200706ce8f`.

## Etapas aprobadas

1. `test`: compilación y suite completa.
2. `build`: construcción del contenedor.
3. `push`: publicación en Artifact Registry.
4. `configure-migration`: actualización del job migrador.
5. `migrate`: ejecución exclusiva de `alembic upgrade head`.
6. `deploy`: actualización de Cloud Run después de la migración.
7. `smoke`: liveness y readiness privados autenticados.

## Controles

- Identidad de despliegue dedicada.
- Identidades de runtime y migración separadas.
- Secretos no entregados a Cloud Build.
- Imagen etiquetada por commit.
- Migración bloqueante antes del despliegue.
- Smoke test autenticado mediante token con audiencia del servicio.
- Logs enviados a Cloud Logging.

## Incidentes corregidos

- Se amplió el contexto de construcción para incluir el contrato OpenAPI.
- Se escaparon las variables locales frente a las sustituciones de Cloud Build.
- Se habilitó la emisión de tokens mediante impersonación limitada.
- Se utilizó `python3` disponible en la imagen de Cloud SDK.

## Conclusión

El mecanismo de entrega es reproducible y quedó validado mediante una ejecución real. No se configuraron disparadores automáticos ni despliegue a producción.
