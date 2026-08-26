# Flujos y reglas backend

## Registro de siniestro

1. Validar identidad del actor.
2. Recibir número de póliza o documento, placa, fecha, ubicación, tipo de evento y contacto.
3. Verificar alcance del piloto.
4. Buscar posibles duplicados por placa y día del evento.
5. Si existe coincidencia, devolver conflicto revisable; el operador decide vincular o crear otro caso.
6. Crear el caso en `reportado` y registrar evento de línea de tiempo.

## Transiciones de estado

Toda transición exige rol autorizado, motivo, versión actual del caso y evento de auditoría.

| Origen | Destinos inicialmente permitidos | Condición |
|---|---|---|
| reportado | validando_cobertura, rechazado | Rechazo requiere confirmación humana |
| validando_cobertura | asistencia_coordinada, evidencia_pendiente, en_evaluacion, rechazado | Según cobertura y necesidad de asistencia |
| asistencia_coordinada | evidencia_pendiente, en_evaluacion | Solicitud registrada |
| evidencia_pendiente | en_evaluacion | Checklist obligatorio completo |
| en_evaluacion | inspeccion_programada, presupuesto_recibido, observado, rechazado | Evidencia suficiente |
| inspeccion_programada | presupuesto_recibido, observado | Inspección registrada |
| presupuesto_recibido | autorizado, observado, rechazado | Decisión humana |
| autorizado | en_reparacion, indemnizado | Según modalidad del caso |
| en_reparacion | listo_para_entrega, observado | Confirmación del taller |
| listo_para_entrega | cerrado | Entrega confirmada, mecanismo POR CONFIRMAR |
| indemnizado | cerrado | Pago confirmado |
| observado | evidencia_pendiente, en_evaluacion, presupuesto_recibido, rechazado | Resolución de observación |
| rechazado | en_evaluacion, cerrado | Reapertura exclusiva de supervisor, con motivo y auditoría |

## Asistencia

- Persistir la solicitud antes de contactar al proveedor.
- Esperar 10 minutos, reintentar una vez y, tras otros 10 minutos, escalar al siguiente proveedor disponible.
- Los valores proceden del cierre simulado y requieren confirmación para producción.
- Cada intento se registra como aceptado, rechazado o sin respuesta.

## Alertas y pagos

- Una alerta no equivale a fraude confirmado.
- Crítica: bloquea pago hasta revisión humana.
- Alta: deriva a investigación antes de continuar.
- Media/baja: aumenta prioridad sin detener el flujo.
- Rechazo de cobertura, confirmación de fraude y autorización de pago requieren decisión humana.
- El operador o ajustador crea una solicitud de pago mediante un comando idempotente.
- Un supervisor distinto del preparador autoriza la solicitud mediante un segundo comando idempotente.
- Todo pago emitido referencia la solicitud y su autorización humana.

## Presupuestos

- La vigencia predeterminada es 30 días calendario desde la recepción.
- El taller puede declarar una vigencia distinta y ésta prevalece si es válida.
- Un presupuesto vencido pasa a `observado` y requiere confirmación o actualización; nunca se autoriza automáticamente.

## Participación de taller y corredor en el piloto

- No crean directamente un expediente.
- Pueden aportar información a un caso existente cuando tengan una orden o referencia válida.
- Si comunican un caso nuevo, un operador busca duplicados y registra el expediente conservando el canal de origen.

## Entrega y cierre

- El taller registra `listo_para_entrega`.
- El asegurado confirma la recepción mediante la aplicación, enlace seguro o código de un solo uso.
- El backend registra actor, fecha y medio y cambia el caso a `cerrado`.
- Si no puede confirmarse digitalmente, un operador adjunta evidencia y un supervisor autoriza el cierre manual.

## Idempotencia y concurrencia

- Crear siniestro, solicitar asistencia, registrar evidencia, revisar alerta, preparar pago y autorizar pago requieren `Idempotency-Key`.
- Misma clave y mismo contenido devuelve el resultado previo.
- Misma clave con contenido diferente devuelve conflicto.
- Cambios de estado deben indicar la versión conocida del caso; una versión desactualizada devuelve HTTP 409 y no modifica datos.
- Un cambio exitoso incrementa `siniestro.version` atómicamente.

## Persistencia de asignaciones

- Cada siniestro tiene como máximo una asignación activa.
- Reasignar finaliza la asignación vigente y crea otra con responsable, fechas y motivo.
- `siguientePaso` se deriva del estado, rol, evidencias y acciones abiertas; no se almacena.
