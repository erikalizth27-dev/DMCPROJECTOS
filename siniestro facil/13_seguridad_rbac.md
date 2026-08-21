# Seguridad y RBAC — Backend

## Reglas generales

- Denegación por defecto.
- El backend valida rol, alcance y relación con el siniestro en cada operación.
- Un identificador válido no implica autorización para consultar el recurso.
- Consultas y descargas sensibles registran usuario, fecha, recurso, acción y resultado.
- Tokens, secretos, documentos completos y evidencia binaria no se escriben en logs.
- El proveedor de identidad y formato definitivo de claims están `POR CONFIRMAR`.
- La política se implementa independientemente del proveedor de identidad.
- Toda autorización evalúa dos condiciones: permiso del rol y alcance sobre el recurso.

## Matriz inicial

| Capacidad | Asegurado/reportante | Operador | Ajustador | Taller/grúa | Investigador fraude | Supervisor |
|---|---:|---:|---:|---:|---:|---:|
| Crear reporte | Sí | Sí | No | No; sólo aporta a casos con orden | No | Sí |
| Consultar vista del caso | Propio | Asignado/autorizado | Asignado | Alcance de orden | Autorizado | Sí |
| Adjuntar evidencia | Propio | Sí | Sí | Según orden | Sí | Sí |
| Cambiar estado | No | Según transición | Según transición | Estados propios | No | Sí |
| Registrar presupuesto | No | No | No | Taller autorizado | No | Sí |
| Revisar alertas | No | Resumen permitido | Resumen permitido | No | Sí | Sí |
| Consultar información ampliada | No | No | POR CONFIRMAR | No | Sí | Sí |
| Preparar solicitud de pago | No | Sí | Sí | No | No | Sí |
| Autorizar pago | No | No | No | No | No | Sí |
| Consultar auditoría completa | Propia limitada | Operativa | Operativa | Propia limitada | Investigación | Sí |
| Configurar política antifraude | No | No | No | No | Rol responsable | Sí |

## Controles verificables

- Autenticación obligatoria salvo endpoints técnicos expresamente públicos.
- Separación entre autorización para recomendar y autorización para decidir.
- Reautenticación o control reforzado para pagos y cambios de política: `POR CONFIRMAR`.
- Rate limiting y bloqueo por abuso: valores `POR CONFIRMAR`.
- La persona que prepara una solicitud de pago no puede autorizarla.
- El supervisor confirma rechazo de cobertura, reapertura y autorización de pago.

## Alcance de recursos

- Asegurado: únicamente sus propios casos.
- Operador y ajustador: casos asignados o autorizados.
- Taller: casos asociados a una orden válida.
- Investigador de fraude: casos autorizados para investigación.
- Supervisor: acceso transversal sujeto a auditoría.

## Implementación Sprint 0

La política ejecutable se encuentra en
`backend/src/siniestro_facil/domain/authorization.py` y cubre:

- creación y consulta de siniestros;
- evidencia y cambios de estado;
- presupuestos;
- alertas e información ampliada;
- preparación y autorización de pagos;
- reapertura de rechazos;
- confirmación de entrega;
- auditoría y política antifraude.

Las pruebas verifican acceso propio, acceso fuera de alcance, prohibición de
creación para taller, revisión de alertas, autorización exclusiva del supervisor
y separación entre preparador y autorizador del pago.
- Cifrado en tránsito obligatorio; gestión de llaves y cifrado en reposo dependen de la plataforma seleccionada.
