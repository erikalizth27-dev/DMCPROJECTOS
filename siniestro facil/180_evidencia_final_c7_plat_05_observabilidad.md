# Evidencia final — C7-PLAT-05 Observabilidad

## Resultado

**C7-PLAT-05 aprobado.**

Los logs HTTP estructurados fueron desplegados y validados en Cloud Run.

## Despliegue

- Build: `d565c93b-db05-4f74-b6f8-5e13a04f1ac2`.
- Estado: `SUCCESS`.
- Imagen: `backend:d5993f9b1b27`.
- Revisión validada: `siniestro-facil-backend-piloto-00005-h5f`.

## Evento validado

- `correlationId`: `c7-observability-validation`.
- Evento: `http_request`.
- Severidad: `INFO`.
- Método: `GET`.
- Ruta: `/health/live`.
- Estado HTTP: `200`.
- Latencia reportada: `0.001991s`.
- Marca de tiempo: `2026-09-04T02:50:54.674925Z`.

## Integración con Cloud Logging

Cloud Logging promovió correctamente:

- `severity` al campo superior de severidad.
- `httpRequest` al campo HTTP estructurado.
- Los campos propios permanecieron en `jsonPayload`.

## Protección de información

La búsqueda no detectó:

- Authorization.
- Password.
- DATABASE_URL.
- Token.
- Request body.
- Response body.

## Alertas

No se definieron umbrales, SLO ni destinatarios. Estos valores permanecen pendientes de datos y aprobación, conforme C7-DEC-06.

## Runbook

El procedimiento de consulta y diagnóstico está documentado en `179_runbook_observabilidad_ciclo_7.md`.
