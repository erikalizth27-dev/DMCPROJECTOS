# Primera entrega — C7-PLAT-05 Observabilidad

## Resultado

Se incorporó la base de logs HTTP estructurados y seguros para Cloud Logging.

## Campos operativos

- Severidad.
- Tipo de evento.
- `correlationId`.
- Método HTTP.
- Ruta sin query string.
- Código de estado.
- Latencia.

## Exclusiones

Los registros HTTP no incluyen:

- Cuerpo de solicitud o respuesta.
- Query string.
- Cabeceras.
- Tokens o credenciales.
- `DATABASE_URL`.
- Contraseñas.
- Detalles sensibles de fraude.
- Texto de excepciones internas.

## Comportamiento

- Una línea JSON por solicitud.
- Severidad `INFO` para respuestas controladas.
- Severidad `ERROR` para excepciones no controladas.
- Correlation ID validado antes de incluirse.
- Latencia basada en reloj monotónico.

## Estado

Implementación inicial completada. Pendiente de validar suite, desplegar mediante el pipeline y confirmar `jsonPayload` en Cloud Logging.
