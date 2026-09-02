# Registro de aprobación — S3-DEC-01 y S3-DEC-02

## Aprobación

El Product Owner aprobó el 2 de septiembre de 2026:

> Utilizar temporalmente un adaptador simulado de proveedores y, para el piloto, realizar tres intentos con esperas de 30 segundos, 2 minutos y 5 minutos, timeout de 10 segundos y escalamiento después del tercer fallo.

## S3-DEC-01 — Proveedor simulado

- Estado: **APROBADA**.
- Alcance: Sprint 3 y piloto.
- El adaptador simulado sustituye temporalmente una integración real no seleccionada.
- No se afirma compatibilidad con ningún proveedor productivo.
- La integración real requerirá una decisión y credenciales separadas.

## S3-DEC-02 — Reintentos simulados

- Estado: **APROBADA**.
- Máximo: 3 intentos.
- Esperas: 30 segundos, 2 minutos y 5 minutos.
- Timeout por intento: 10 segundos.
- Escalamiento: después del tercer fallo.
- Uso: validación funcional del piloto; no constituye un SLA productivo.

## Controles

- Cada intento conserva identificador idempotente y resultado.
- Un reintento no duplica efectos.
- La solicitud local se persiste antes de la llamada externa.
- Los fallos permanentes conservan trazabilidad.
- Cualquier cambio de valores requiere una nueva decisión registrada.

## Documentos afectados

- `74_estado_sprint_3.md`.
- `75_backlog_sprint_3_refinado.md`.
- `76_matriz_trazabilidad_sprint_3.md`.
