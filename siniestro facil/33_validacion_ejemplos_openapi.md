# Validación — Ejemplos OpenAPI

## Resultado estático

**APROBADO**. El contrato OpenAPI `0.2.0-draft` fue parseado correctamente y
los ejemplos sintéticos requeridos están presentes.

## Cobertura

| Grupo | Cantidad | Resultado |
|---|---:|---|
| Ejemplos de comandos | 8 | OK |
| Ejemplos de errores reutilizables | 5 | OK |
| Rutas | 11 | OK |
| Operaciones únicas | 11 | OK |
| Esquemas | 14 | OK |

## Comandos con ejemplo

- Crear siniestro.
- Registrar evidencia.
- Cambiar estado.
- Solicitar asistencia.
- Registrar presupuesto.
- Revisar alerta.
- Preparar solicitud de pago.
- Autorizar solicitud de pago.

## Errores con ejemplo

- `401` no autenticado.
- `403` prohibido.
- `404` no encontrado o no visible.
- `409` conflicto.
- `422` regla de negocio.

## Seguridad de los ejemplos

- Todos los valores se identifican como sintéticos.
- Se utiliza el dominio reservado `example.invalid`.
- No se incluyen tokens, contraseñas, secretos ni datos personales reales.
- Los errores conservan `correlationId` y no revelan detalles internos.

## Automatización

`backend/tests/test_openapi_spec.py` comprueba presencia de ejemplos en los ocho
comandos y cinco respuestas, además de rechazar las cadenas `password` y
`secret`. La suite ampliada esperada pasa de 41 a 42 pruebas y debe ejecutarse en
Cloud Shell.
