# Estrategia de pruebas, observabilidad y entrega

## Capas de prueba

| Capa | Cobertura mínima |
|---|---|
| Unidad | Reglas de transición, deduplicación, severidad, permisos e idempotencia |
| Persistencia | PK, FK, UNIQUE, NOT NULL, CHECK, triggers y reglas de borrado |
| Integración | Base de datos, almacenamiento de evidencia y adaptadores externos simulados |
| Contrato | Validación de solicitudes y respuestas contra OpenAPI |
| Seguridad | Autorización por rol, acceso horizontal, datos sensibles y auditoría |
| Resiliencia | Timeout, reintento, duplicación de mensajes e indisponibilidad de terceros |
| Aceptación | Cada escenario Given/When/Then asociado a su HU |
| Rendimiento | SLA y volumen POR CONFIRMAR antes de fijar umbrales de aprobación |

## Observabilidad

- `correlationId` propagado en petición, logs, eventos y errores.
- Logs estructurados con operación, resultado, duración y actor pseudonimizado.
- Métricas: peticiones, latencia, errores, conflictos de idempotencia, transiciones, reintentos y cola pendiente.
- Trazas para solicitudes que cruzan adaptadores externos.
- Alertas operativas sin datos personales.
- Retención de logs, métricas y auditoría `POR CONFIRMAR`.

## CI/CD en Google Cloud — diferido

Esta sección describe una estrategia futura. Su implementación no forma parte de Sprint 0 ni del alcance actualmente autorizado.

1. Cloud Build valida formato y contrato OpenAPI.
2. Pruebas unitarias y análisis estático.
3. Pruebas con PostgreSQL compatible.
4. Aplicación de migraciones en una base efímera.
5. Pruebas de integración y seguridad.
6. Construcción de imagen inmutable y publicación en Artifact Registry.
7. Despliegue de una revisión de Cloud Run en ambiente no productivo.
8. Smoke tests y aprobación en Cloud Deploy o promoción controlada de la revisión.
9. Despliegue productivo y verificación en Cloud Monitoring.

Los secretos se obtienen de Secret Manager y no se almacenan en el repositorio ni en variables visibles del pipeline.
