# Matriz endpoint–rol — Backend Siniestro Fácil

## Convenciones

- **Sí**: el rol tiene la acción en la política ejecutable.
- **Alcance**: además del rol, el recurso debe pertenecer al alcance autorizado.
- **No**: denegación por defecto.
- **PC**: `POR CONFIRMAR`; falta una acción o separación contractual.
- Supervisor conserva acceso transversal sujeto a auditoría.

## Matriz

| Método y endpoint | Acción RBAC | Asegurado | Operador | Ajustador | Taller | Investigador fraude | Supervisor | Observación |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `POST /siniestros` | `CREAR_SINIESTRO` | Sí | Sí | No | No | No | Sí | No requiere alcance previo porque crea el recurso |
| `GET /siniestros/{id}` | `CONSULTAR_SINIESTRO` | Alcance | Alcance | Alcance | Alcance | Alcance | Sí | Identificador válido no concede acceso |
| `POST /siniestros/{id}/estado` | `CAMBIAR_ESTADO` | No | Alcance | Alcance | Alcance | No | Sí | Cada rol sólo puede ejecutar transiciones permitidas |
| `POST /siniestros/{id}/evidencias` | `ADJUNTAR_EVIDENCIA` | Alcance | Alcance | Alcance | Alcance | Alcance | Sí | Taller únicamente bajo orden válida |
| `POST /siniestros/{id}/asistencias` | **PC** | PC | PC | PC | PC | No | PC | No existe acción equivalente en `Action` |
| `POST /siniestros/{id}/presupuestos` | `REGISTRAR_PRESUPUESTO` | No | No | No | Alcance | No | Sí | Taller autorizado para el caso |
| `GET /siniestros/{id}/alertas` | `CONSULTAR_INFORMACION_AMPLIADA` | No | No | PC | No | Alcance | Sí | Resumen de operador/ajustador y detalle visible siguen pendientes |
| `POST /alertas/{alertaId}/revision` | `REVISAR_ALERTA` | No | No | No | No | Alcance | Sí | Revisión humana obligatoria |
| `POST /siniestros/{id}/pagos` | **PC** | No | PC | PC | No | No | PC | Deben separarse `PREPARAR_PAGO` y `AUTORIZAR_PAGO` |
| `GET /siniestros/{id}/linea-tiempo` | `CONSULTAR_AUDITORIA` | Alcance | Alcance | Alcance | Alcance | Alcance | Sí | El detalle de la respuesta varía por rol |

## Respuesta HTTP de autorización

| Situación | HTTP | Comportamiento |
|---|---:|---|
| Token ausente, inválido o vencido | 401 | Respuesta `Error`, sin revelar datos del recurso |
| Rol sin permiso | 403 | Respuesta `Error` auditable |
| Recurso fuera del alcance | 404 | Evita confirmar la existencia del recurso |
| Regla de separación de funciones incumplida | 422 | Regla de negocio con `correlationId` |

## Bloqueos para aprobación

### AR-01 — Asistencia

Recomendación: agregar `SOLICITAR_ASISTENCIA`. Permitir a asegurado en caso
propio, operador/ajustador en caso asignado y supervisor. Taller, proveedor e
investigador no crean la solicitud.

### AR-02 — Pagos

Recomendación: sustituir el único `POST /siniestros/{id}/pagos` por dos comandos:

1. `POST /siniestros/{id}/solicitudes-pago`, acción `PREPARAR_PAGO`.
2. `POST /solicitudes-pago/{id}/autorizacion`, acción `AUTORIZAR_PAGO`.

El preparador y el autorizador deben ser usuarios diferentes; sólo supervisor
puede autorizar en el piloto.

### AR-03 — Alertas

Recomendación: operador y ajustador sólo reciben indicador/resumen; investigador
de fraude y supervisor reciben detalle. La lista exacta de campos visibles debe
aprobarse antes de implementar el serializador por rol.

## Trazabilidad

- Política: `13_seguridad_rbac.md`.
- Implementación: `backend/src/siniestro_facil/domain/authorization.py`.
- Contrato: `12_api_backend_openapi.yaml`.
- Preguntas abiertas: `17_preguntas_abiertas_backend.md`.
