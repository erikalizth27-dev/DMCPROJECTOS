# Matriz de trazabilidad — Ciclo 7 Plataforma

| Incremento | Necesidad | Evidencia esperada |
|---|---|---|
| C7-PLAT-01 | Ejecución reproducible y segura | Imagen construida, usuario no privilegiado y pruebas de salud |
| C7-PLAT-02 | Backend disponible en GCP | Revisión de Cloud Run, Cloud SQL y smoke tests |
| C7-PLAT-03 | Protección de configuración e identidad | IAM mínimo, Secret Manager y ausencia de secretos rastreados |
| C7-PLAT-04 | Entrega repetible y migración segura | Pipeline verde, imagen por commit y ejecución única de Alembic |
| C7-PLAT-05 | Diagnóstico y respuesta operativa | Logs correlacionados, métricas, alertas y runbook |
| C7-PLAT-06 | Confirmación integral del piloto | Pruebas de aceptación, limpieza, evidencias y acta |

## Fuentes heredadas

- `09_especificacion_despliegue_gcp.md`.
- `13_seguridad_rbac.md`.
- `41_politica_migraciones_alembic.md`.
- `164_acta_cierre_sprint_6.md`.
- Validadores integrales y PostgreSQL de los Sprints 1–6.

## Infraestructura existente

- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Región de los recursos existentes: `us-central1`.
- Cloud SQL: `dmcappasistidaia`.
- Base: `DMCSINIESTROFACIL`.
- Bucket de evidencias: `project-77c17016-86bc-4fc4-a97-siniestro-evidencias`.
- Pub/Sub y Cloud Tasks creados durante Sprint 3.

## Controles transversales

- Autenticación obligatoria.
- RBAC y alcance persistente.
- Segregación de funciones.
- Auditoría con identidad y correlación.
- Redacción de información sensible.
- Idempotencia y concurrencia optimista.
- Migraciones separadas del runtime.

## Vacíos que requieren decisión

- Región y nombre definitivo de Cloud Run.
- Mecanismo de autenticación perimetral.
- Ambientes requeridos.
- Recursos, escalado y concurrencia.
- Tecnología del pipeline.
- Umbrales y destinatarios de alertas.
