# Primera entrega de estabilización — Sprint 6

## Controles reforzados

- `DATABASE_URL` queda excluida de la representación textual de configuración.
- Los errores de validación ya no devuelven el valor de entrada ni el contexto interno de Pydantic.
- Los errores conservan código estable, campos afectados y correlation ID.
- Matriz RBAC verificada para autorización exclusiva de pagos por supervisor.
- Redacción de información sensible comprobada.
- Adaptador de pagos comprobado como simulado y sin transferencia monetaria.
- No se agregaron umbrales de autenticación reciente ni rate limiting.

## Pruebas

Se añadieron **7 pruebas de seguridad y estabilización**. Total esperado: **428 pruebas**.

## Migración

No se requiere migración.
