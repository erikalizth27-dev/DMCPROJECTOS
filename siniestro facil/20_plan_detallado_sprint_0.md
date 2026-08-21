# Plan detallado — Sprint 0 Backend Siniestro Fácil

## Propósito

Preparar la base funcional, técnica y operativa para que Sprint 1 comience con historias que cumplan la Definition of Ready, ambientes GCP utilizables y un flujo de entrega verificable.

## Duración y equipo

- Duración: 2 semanas / 10 días laborables.
- Product Owner o analista de negocio.
- Líder técnico / arquitecto.
- Dos desarrolladores backend.
- Especialista QA y automatización.
- Especialista GCP/DevOps.

Sprint 0 no entrega funcionalidad de negocio completa a usuarios finales. Entrega la plataforma, contratos y decisiones necesarias para desarrollar con seguridad.

## Objetivos de salida

1. Especificaciones funcionales consolidadas y sin contradicciones bloqueantes.
2. Arquitectura GCP aprobada para el piloto.
3. Contrato OpenAPI inicial validado.
4. Modelo físico PostgreSQL y pruebas disponibles en `main`.
5. Ambientes de desarrollo y pruebas preparados en GCP.
6. Pipeline CI/CD mínimo funcionando.
7. Seguridad, auditoría y observabilidad definidas.
8. Historias de Sprint 1 refinadas, estimadas y listas.

## Frente 1 — Consolidación SDD

### Actividades

- Revisar `01_historias_usuario.md` a `09_especificacion_despliegue_gcp.md`.
- Propagar las decisiones de `cierre_de_brechas.md` y `19_decisiones_recomendadas_piloto.md`.
- Eliminar marcas `[Pendiente]` que ya tengan respuesta aprobada.
- Mantener como preguntas únicamente las dependencias reales externas.
- Crear matriz de trazabilidad HU → criterio → RF → CU → endpoint → prueba.
- Identificar historias que todavía no cumplen la Definition of Ready.

### Entregables

- SPEC funcionales coherentes.
- Registro de decisiones aprobado.
- Matriz de trazabilidad.
- Lista de historias bloqueadas y causa.

### Responsable principal

Product Owner/analista, con revisión del líder técnico y QA.

## Frente 2 — Arquitectura Google Cloud

### Actividades

- Confirmar Cloud Run como plataforma del backend del piloto.
- Definir proyectos o separación de ambientes `dev`, `test` y `prod`.
- Confirmar región de cómputo, datos, backups y evidencias.
- Diseñar conexión Cloud Run–Cloud SQL con cuenta de servicio y mínimo privilegio.
- Diseñar buckets de Cloud Storage, versionado, retención y autorización de carga.
- Definir tópicos, suscripciones y dead-letter topics de Pub/Sub.
- Identificar procesos que utilizarán Cloud Tasks y Cloud Scheduler.
- Definir uso de Secret Manager, Artifact Registry y Google Cloud Observability.
- Elaborar diagrama de arquitectura y registro de decisiones.

### Entregables

- Arquitectura GCP aprobada.
- Inventario de recursos por ambiente.
- Modelo de cuentas de servicio e IAM.
- Diagrama de despliegue y flujos asíncronos.
- Estimación inicial de costos del piloto.

### Responsable principal

Líder técnico y especialista GCP/DevOps.

## Frente 3 — Contrato API

### Actividades

- Revisar las 10 rutas iniciales de `12_api_backend_openapi.yaml`.
- Completar cuerpos de solicitud y respuesta faltantes.
- Definir paginación, filtros, ordenamiento y límites.
- Definir catálogo de errores y códigos de negocio.
- Definir versión optimista para cambios de estado.
- Confirmar operaciones que requieren `Idempotency-Key`.
- Asociar cada endpoint con roles autorizados y criterios de aceptación.
- Incorporar ejemplos sintéticos que no contengan datos personales reales.
- Automatizar validación del OpenAPI en CI.

### Entregables

- OpenAPI válido y revisado.
- Catálogo de errores.
- Matriz endpoint–rol–historia–prueba.
- Política de versionado del API.

### Responsable principal

Líder técnico y desarrolladores backend, con validación de QA.

## Frente 4 — Datos y migraciones

### Actividades

- Revisar y fusionar el PR #1 del modelo físico.
- Confirmar correspondencia entre las 22 entidades lógicas y tablas PostgreSQL.
- Ejecutar DDL y pruebas de constraints en una base de pruebas.
- Definir convención y herramienta de migraciones sin compartir credenciales.
- Definir usuario de runtime separado del usuario de migraciones.
- Validar conexión desde Cloud Run a Cloud SQL.
- Incorporar carga y validación de datos sintéticos.
- Documentar backup, restauración y recuperación `POR CONFIRMAR` con objetivos RPO/RTO.

### Entregables

- Modelo físico en `main`.
- Migración inicial reproducible.
- Suite de constraints aprobada.
- Datos sintéticos y validación.
- Evidencia de conexión Cloud Run–Cloud SQL en ambiente no productivo.

### Responsable principal

Desarrollador backend, líder técnico y especialista GCP/DevOps.

## Frente 5 — Seguridad y privacidad

### Actividades

- Aprobar la matriz RBAC de `13_seguridad_rbac.md`.
- Seleccionar el mecanismo de identidad para usuarios finales e internos.
- Definir claims, roles y alcance de acceso a casos.
- Definir separación de funciones para pagos y decisiones sensibles.
- Configurar cuentas de servicio por componente.
- Definir manejo de secretos y rotación.
- Definir datos prohibidos en logs.
- Diseñar auditoría de consultas y descargas sensibles.
- Preparar casos de prueba contra acceso horizontal y escalamiento de privilegios.

### Entregables

- Matriz RBAC aprobada.
- Modelo de identidad y autorización.
- Política de secretos.
- Casos de prueba de seguridad.

### Responsable principal

Líder técnico, especialista GCP/DevOps y QA, con aprobación del Product Owner.

## Frente 6 — Esqueleto backend y calidad

### Actividades

- Crear la estructura inicial del backend después de seleccionar lenguaje y framework.
- Incorporar configuración por ambiente.
- Implementar endpoint técnico de salud sin acceso a datos sensibles.
- Incorporar manejo uniforme de errores y `correlationId`.
- Configurar logs estructurados y trazas.
- Preparar dobles de prueba para pólizas, talleres, mensajería, mapas y pagos.
- Establecer convenciones de código, ramas, commits y revisión.
- Configurar umbrales de calidad iniciales.

### Entregables

- Servicio mínimo ejecutándose localmente y en Cloud Run `dev`.
- Health check.
- Manejo de errores y observabilidad base.
- Guía de desarrollo y contribución.

### Responsable principal

Desarrolladores backend y líder técnico.

## Frente 7 — CI/CD y operación

### Actividades

- Configurar Cloud Build para validación, pruebas y construcción.
- Publicar imágenes inmutables en Artifact Registry.
- Ejecutar pruebas PostgreSQL en un entorno aislado.
- Desplegar automáticamente en Cloud Run `dev`.
- Definir promoción controlada hacia `test` y `prod`.
- Configurar smoke tests posteriores al despliegue.
- Crear panel y alertas técnicas mínimas en Cloud Monitoring.
- Documentar rollback a una revisión anterior.

### Entregables

- Pipeline ejecutado correctamente desde un pull request.
- Imagen en Artifact Registry.
- Revisión desplegada en Cloud Run `dev`.
- Smoke test y rollback demostrados.
- Panel técnico inicial.

### Responsable principal

Especialista GCP/DevOps con apoyo de backend y QA.

## Frente 8 — Refinamiento de Sprint 1

### Actividades

- Seleccionar HU-01, HU-03, HU-04, HU-06, HU-08, HU-10 y HU-28 como candidatas.
- Dividir historias demasiado grandes en incrementos verticales.
- Confirmar dependencias y orden de implementación.
- Asociar criterios de aceptación y pruebas.
- Estimar esfuerzo con el equipo.
- Definir objetivo de Sprint 1 y capacidad disponible.
- Verificar individualmente la Definition of Ready.

### Entregables

- Sprint Backlog 1 priorizado y estimado.
- Objetivo de Sprint 1.
- Historias listas con criterios, contrato, datos y pruebas.

### Responsable principal

Product Owner y equipo completo.

## Secuencia sugerida de 10 días

| Día | Actividad dominante | Resultado |
|---:|---|---|
| 1 | Kickoff, alcance y decisiones pendientes | Objetivo y responsables confirmados |
| 2 | Consolidación SDD y cierre de contradicciones | SPEC funcionales alineadas |
| 3 | Arquitectura GCP e IAM | Diagrama y recursos definidos |
| 4 | OpenAPI, errores e idempotencia | Contrato API revisado |
| 5 | Modelo físico, migraciones y pruebas | Persistencia validada |
| 6 | Esqueleto backend y conexión Cloud SQL | Servicio mínimo operativo |
| 7 | Cloud Storage, Pub/Sub y adaptadores simulados | Integraciones base preparadas |
| 8 | CI/CD, seguridad y observabilidad | Pipeline y controles funcionando |
| 9 | Refinamiento y estimación de Sprint 1 | Backlog listo |
| 10 | Revisión, demostración y retrospectiva | Criterios de salida evaluados |

## Criterios de aceptación de Sprint 0

- El PR #1 está fusionado o existe una decisión documentada que resuelve su dependencia.
- Las decisiones recomendadas están aprobadas o marcadas con responsable y fecha límite.
- OpenAPI pasa validación automática.
- El modelo PostgreSQL se despliega y sus pruebas finalizan correctamente en un ambiente de pruebas.
- El servicio mínimo se despliega en Cloud Run y responde al health check.
- Cloud Run accede a Cloud SQL sin usar el usuario administrador.
- Los secretos se leen desde Secret Manager.
- Un pull request ejecuta automáticamente validaciones y pruebas.
- Logs y trazas contienen `correlationId` y no contienen datos sensibles.
- Las historias comprometidas para Sprint 1 cumplen la Definition of Ready.

## Riesgos y bloqueos

- No aprobar las decisiones de negocio impide cerrar criterios de aceptación.
- Mantener el PR #1 sin fusionar crea divergencia entre documentación y base desplegada.
- Usar un solo proyecto GCP para todos los ambientes aumenta riesgo de mezcla de datos y permisos.
- No elegir mecanismo de identidad bloquea pruebas completas de RBAC.
- No disponer de APIs de pólizas obliga a mantener adaptadores simulados durante los primeros sprints.
