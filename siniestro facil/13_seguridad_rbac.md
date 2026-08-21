# Seguridad y RBAC — Backend

## Reglas generales

- Denegación por defecto.
- El backend valida rol, alcance y relación con el siniestro en cada operación.
- Un identificador válido no implica autorización para consultar el recurso.
- Consultas y descargas sensibles registran usuario, fecha, recurso, acción y resultado.
- Tokens, secretos, documentos completos y evidencia binaria no se escriben en logs.
- El proveedor de identidad y formato definitivo de claims están `POR CONFIRMAR`.

## Matriz inicial

| Capacidad | Asegurado/reportante | Operador | Ajustador | Taller/grúa | Investigador fraude | Supervisor |
|---|---:|---:|---:|---:|---:|---:|
| Crear reporte | Sí | Sí | No | POR CONFIRMAR | No | Sí |
| Consultar vista del caso | Propio | Asignado/autorizado | Asignado | Alcance de orden | Autorizado | Sí |
| Adjuntar evidencia | Propio | Sí | Sí | Según orden | Sí | Sí |
| Cambiar estado | No | Según transición | Según transición | Estados propios | No | Sí |
| Registrar presupuesto | No | No | No | Taller autorizado | No | Sí |
| Revisar alertas | No | Resumen permitido | Resumen permitido | No | Sí | Sí |
| Consultar información ampliada | No | No | POR CONFIRMAR | No | Sí | Sí |
| Autorizar pago | No | POR CONFIRMAR | POR CONFIRMAR | No | No | Sí |
| Consultar auditoría completa | Propia limitada | Operativa | Operativa | Propia limitada | Investigación | Sí |
| Configurar política antifraude | No | No | No | No | Rol responsable | Sí |

## Controles verificables

- Autenticación obligatoria salvo endpoints técnicos expresamente públicos.
- Separación entre autorización para recomendar y autorización para decidir.
- Reautenticación o control reforzado para pagos y cambios de política: `POR CONFIRMAR`.
- Rate limiting y bloqueo por abuso: valores `POR CONFIRMAR`.
- Cifrado en tránsito obligatorio; gestión de llaves y cifrado en reposo dependen de la plataforma seleccionada.

