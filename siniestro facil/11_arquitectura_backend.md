# Arquitectura Backend — Especificación inicial

## Alcance y restricción de plataforma

Toda la solución se desarrolla y opera en Google Cloud. La línea base del piloto utiliza servicios administrados para reducir operación: Cloud Run, Cloud SQL for PostgreSQL, Cloud Storage, Pub/Sub, Secret Manager y Google Cloud Observability. No se selecciona todavía lenguaje ni framework.

## Principios

- El backend es la autoridad sobre estados, autorizaciones, pagos y trazabilidad.
- Las decisiones sensibles requieren confirmación humana.
- Las integraciones externas no controlan la transacción principal.
- La evidencia original es inmutable; las versiones derivadas permanecen vinculadas.
- Todo cambio de estado y acceso sensible genera un evento de auditoría.
- Los comandos con efecto económico o externo deben ser idempotentes.

## Módulos lógicos

| Módulo | Responsabilidad | Requisitos principales |
|---|---|---|
| Identidad y acceso | Autenticar y autorizar por rol y necesidad | RF-23; RNF-01, RNF-08, RNF-09 |
| Pólizas y cobertura | Consultar póliza, vehículo, cobertura y deducible | RF-03, RF-05 |
| Siniestros | Registrar, consultar, deduplicar y gestionar estados | RF-01, RF-02, RF-04, RF-09, RF-13, RF-30, RF-31 |
| Evidencias | Registrar metadatos, URI, hash y derivaciones | RF-07, RF-08, RF-25, RF-28 |
| Asignación y asistencia | Asignar casos y coordinar proveedores | RF-06, RF-11, RF-12, RF-17 |
| Inspección y talleres | Programar inspecciones y gestionar presupuestos | RF-15, RF-16 |
| Autorizaciones y pagos | Registrar aprobación humana y evitar duplicados | RF-14; RNF-04, RNF-05 |
| Riesgo y fraude | Señales, alertas, políticas y relaciones | RF-19 a RF-28 |
| Comunicaciones | Registrar comunicaciones y estado visible | RF-10, RF-18 |
| Auditoría | Línea de tiempo y accesos sensibles | RF-18, RF-26; RNF-02, RNF-09 |
| Indicadores | Métricas operativas y de negocio | RF-29 |

## Patrón de interacción

- Operaciones simples: petición síncrona con resultado inmediato.
- Procesos con terceros: solicitud persistida, procesamiento asíncrono, reintento controlado y consulta de estado.
- Archivos: el cliente solicita autorización de carga; el binario se almacena fuera del núcleo relacional y el backend registra URI, hash y metadatos.
- Eventos: cada consumidor debe tolerar reentrega; el identificador del evento evita efectos duplicados.

## Consistencia transaccional

- La creación del siniestro y su evento inicial se confirman en una misma transacción.
- Un pago `emitido` requiere autorización humana persistida.
- Una relación entre casos no propaga estados, pagos ni decisiones.
- La comunicación con sistemas externos ocurre después de persistir el comando local.

## Mapeo inicial a Google Cloud

| Capacidad | Servicio GCP inicial |
|---|---|
| API backend | Cloud Run |
| Base transaccional | Cloud SQL for PostgreSQL, base `DMCSINIESTROFACIL` |
| Evidencias | Cloud Storage con versionado y políticas de retención |
| Procesamiento asíncrono | Pub/Sub |
| Tareas programadas y reintentos controlados | Cloud Tasks / Cloud Scheduler según el flujo |
| Secretos | Secret Manager |
| Identidad de cargas | IAM Service Accounts y Workload Identity |
| Imágenes de contenedor | Artifact Registry |
| Construcción | Cloud Build |
| Despliegue progresivo | Cloud Deploy o revisiones de Cloud Run |
| Logs, métricas, trazas y alertas | Cloud Logging, Monitoring y Trace |
| Protección perimetral | HTTPS Load Balancer y Cloud Armor, si la exposición pública lo requiere |

## Dependencias

El modelo físico ejecutable y sus pruebas se encuentran en el PR #1. Esta especificación depende de su fusión en `main`.
