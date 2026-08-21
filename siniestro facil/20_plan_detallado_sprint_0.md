# Plan detallado — Sprint 0 Backend Siniestro Fácil

## Propósito

Preparar la base funcional y técnica para que Sprint 1 comience con historias que cumplan la Definition of Ready. CI/CD, observabilidad y operación en GCP quedan fuera de este sprint.

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
5. Seguridad y auditoría funcional definidas.
6. Historias de Sprint 1 refinadas, estimadas y listas.

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
- Documentar la separación futura de ambientes `dev`, `test` y `prod`, sin implementarla en Sprint 0.
- Confirmar región de cómputo, datos, backups y evidencias.
- Diseñar conceptualmente la conexión Cloud Run–Cloud SQL con cuenta de servicio y mínimo privilegio.
- Diseñar buckets de Cloud Storage, versionado, retención y autorización de carga.
- Definir tópicos, suscripciones y dead-letter topics de Pub/Sub.
- Identificar procesos que utilizarán Cloud Tasks y Cloud Scheduler.
- Documentar el uso futuro de Secret Manager, Artifact Registry y Google Cloud Observability, sin configurarlos.
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
- Incorporar carga y validación de datos sintéticos.
- Documentar backup, restauración y recuperación `POR CONFIRMAR` con objetivos RPO/RTO.

### Entregables

- Modelo físico en `main`.
- Migración inicial reproducible.
- Suite de constraints aprobada.
- Datos sintéticos y validación.

### Responsable principal

Desarrollador backend, líder técnico y especialista GCP/DevOps.

## Frente 5 — Seguridad y privacidad

### Actividades

- Aprobar la matriz RBAC de `13_seguridad_rbac.md`.
- Seleccionar el mecanismo de identidad para usuarios finales e internos.
- Definir claims, roles y alcance de acceso a casos.
- Definir separación de funciones para pagos y decisiones sensibles.
- Diseñar cuentas de servicio por componente, sin configurarlas.
- Definir conceptualmente el manejo de secretos y rotación.
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
- Incorporar manejo uniforme de errores y `correlationId`.
- Preparar dobles de prueba para pólizas, talleres, mensajería, mapas y pagos.
- Establecer convenciones de código, ramas, commits y revisión.
- Configurar umbrales de calidad iniciales.

### Entregables

- Esqueleto del servicio ejecutándose localmente.
- Manejo uniforme de errores.
- Guía de desarrollo y contribución.

### Responsable principal

Desarrolladores backend y líder técnico.

## Frente 7 — Refinamiento de Sprint 1

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
| 6 | Esqueleto backend local | Estructura y convenciones preparadas |
| 7 | Contratos de Cloud Storage, Pub/Sub y adaptadores simulados | Interfaces documentadas |
| 8 | Seguridad, RBAC y auditoría funcional | Controles funcionales definidos |
| 9 | Refinamiento y estimación de Sprint 1 | Backlog listo |
| 10 | Revisión, demostración y retrospectiva | Criterios de salida evaluados |

## Criterios de aceptación de Sprint 0

- El PR #1 está fusionado o existe una decisión documentada que resuelve su dependencia.
- Las decisiones recomendadas están aprobadas o marcadas con responsable y fecha límite.
- OpenAPI pasa validación automática.
- El modelo PostgreSQL se despliega y sus pruebas finalizan correctamente en un ambiente de pruebas.
- El esqueleto del servicio se ejecuta localmente y no almacena credenciales en el repositorio.
- La arquitectura futura de conexión con Cloud SQL y Secret Manager está documentada.
- El modelo de auditoría funcional define actor, acción, fecha, recurso y resultado.
- Las historias comprometidas para Sprint 1 cumplen la Definition of Ready.

## Actividades explícitamente diferidas

No se realizarán durante Sprint 0:

- Configuración de Cloud Build o Cloud Deploy.
- Publicación de imágenes en Artifact Registry.
- Despliegue del backend en Cloud Run.
- Configuración de ambientes operativos GCP.
- Cloud Logging, Monitoring, Trace, paneles o alertas.
- Smoke tests de despliegue, promoción y rollback.

Estas actividades se planificarán cuando el equipo autorice iniciar la fase DevOps y operativa.

## Riesgos y bloqueos

- No aprobar las decisiones de negocio impide cerrar criterios de aceptación.
- Mantener el PR #1 sin fusionar crea divergencia entre documentación y base desplegada.
- Usar un solo proyecto GCP para todos los ambientes aumenta riesgo de mezcla de datos y permisos.
- No elegir mecanismo de identidad bloquea pruebas completas de RBAC.
- No disponer de APIs de pólizas obliga a mantener adaptadores simulados durante los primeros sprints.
