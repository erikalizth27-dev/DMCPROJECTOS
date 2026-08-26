# Matriz endpoint–rol — Backend Siniestro Fácil

## Convenciones

- **Sí**: el rol tiene la acción en la política ejecutable.
- **Alcance**: además del rol, el recurso debe pertenecer al alcance autorizado.
- **No**: denegación por defecto.
- **Aprobado**: decisión funcional confirmada el 25 de agosto de 2026.
- Supervisor conserva acceso transversal sujeto a auditoría.

## Matriz

| Método y endpoint | Acción RBAC | Asegurado | Operador | Ajustador | Taller | Investigador fraude | Supervisor | Observación |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `POST /siniestros` | `CREAR_SINIESTRO` | Sí | Sí | No | No | No | Sí | No requiere alcance previo porque crea el recurso |
| `GET /siniestros/{id}` | `CONSULTAR_SINIESTRO` | Alcance | Alcance | Alcance | Alcance | Alcance | Sí | Identificador válido no concede acceso |
| `POST /siniestros/{id}/estado` | `CAMBIAR_ESTADO` | No | Alcance | Alcance | Alcance | No | Sí | Cada rol sólo puede ejecutar transiciones permitidas |
| `POST /siniestros/{id}/evidencias` | `ADJUNTAR_EVIDENCIA` | Alcance | Alcance | Alcance | Alcance | Alcance | Sí | Taller únicamente bajo orden válida |
| `POST /siniestros/{id}/asistencias` | `SOLICITAR_ASISTENCIA` | Alcance | Alcance | Alcance | No | No | Sí | AR-01 aprobada |
| `POST /siniestros/{id}/presupuestos` | `REGISTRAR_PRESUPUESTO` | No | No | No | Alcance | No | Sí | Taller autorizado para el caso |
| `GET /siniestros/{id}/alertas` | `CONSULTAR_ALERTA_RESUMEN` / `CONSULTAR_INFORMACION_AMPLIADA` | No | Alcance | Alcance | No | Alcance | Sí | Operador/ajustador: resumen; investigador/supervisor: detalle |
| `POST /alertas/{alertaId}/revision` | `REVISAR_ALERTA` | No | No | No | No | Alcance | Sí | Revisión humana obligatoria |
| `POST /siniestros/{id}/solicitudes-pago` | `PREPARAR_PAGO` | No | Alcance | Alcance | No | No | Sí | Crea solicitud; no autoriza |
| `POST /solicitudes-pago/{id}/autorizacion` | `AUTORIZAR_PAGO` | No | No | No | No | No | Sí | Supervisor diferente del preparador |
| `GET /siniestros/{id}/linea-tiempo` | `CONSULTAR_AUDITORIA` | Alcance | Alcance | Alcance | Alcance | Alcance | Sí | El detalle de la respuesta varía por rol |

## Respuesta HTTP de autorización

| Situación | HTTP | Comportamiento |
|---|---:|---|
| Token ausente, inválido o vencido | 401 | Respuesta `Error`, sin revelar datos del recurso |
| Rol sin permiso | 403 | Respuesta `Error` auditable |
| Recurso fuera del alcance | 404 | Evita confirmar la existencia del recurso |
| Regla de separación de funciones incumplida | 422 | Regla de negocio con `correlationId` |

## Decisiones aprobadas

### AR-01 — Asistencia

**Aprobada el 25 de agosto de 2026.** Se agrega `SOLICITAR_ASISTENCIA`. Permitir a asegurado en caso
propio, operador/ajustador en caso asignado y supervisor. Taller, proveedor e
investigador no crean la solicitud.

### AR-02 — Pagos

**Aprobada el 25 de agosto de 2026.** Se sustituye el único comando por:

1. `POST /siniestros/{id}/solicitudes-pago`, acción `PREPARAR_PAGO`.
2. `POST /solicitudes-pago/{id}/autorizacion`, acción `AUTORIZAR_PAGO`.

El preparador y el autorizador deben ser usuarios diferentes; sólo supervisor
puede autorizar en el piloto.

### AR-03 — Alertas

**Aprobada el 25 de agosto de 2026.** Operador y ajustador reciben indicador/resumen; investigador
de fraude y supervisor reciben detalle. El resumen contiene `id`, `severidad` y `estadoRevision`; el detalle agrega `tipo` y `detalle`.

## Trazabilidad

- Política: `13_seguridad_rbac.md`.
- Implementación: `backend/src/siniestro_facil/domain/authorization.py`.
- Contrato: `12_api_backend_openapi.yaml`.
- Preguntas abiertas: `17_preguntas_abiertas_backend.md`.
