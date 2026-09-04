# Runbook de observabilidad — Ciclo 7

## Alcance

Este runbook cubre diagnóstico básico del ambiente piloto. No establece SLO, umbrales numéricos ni destinatarios de alertas.

## Servicio

- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Región: `us-central1`.
- Cloud Run: `siniestro-facil-backend-piloto`.
- Job migrador: `siniestro-facil-migrator-piloto`.

## Confirmar revisión activa

```bash
gcloud run services describe siniestro-facil-backend-piloto \
  --project=project-77c17016-86bc-4fc4-a97 \
  --region=us-central1 \
  --format="yaml(status.latestReadyRevisionName,status.url,status.conditions)"
```

## Consultar solicitudes por correlación

```bash
CORRELATION_ID="VALOR_AUTORIZADO"

gcloud logging read \
  "resource.type=\"cloud_run_revision\" AND jsonPayload.correlationId=\"${CORRELATION_ID}\"" \
  --project=project-77c17016-86bc-4fc4-a97 \
  --limit=50 \
  --order=desc
```

## Consultar errores HTTP

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND jsonPayload.event="http_request" AND jsonPayload.httpRequest.status>=500' \
  --project=project-77c17016-86bc-4fc4-a97 \
  --limit=50 \
  --order=desc
```

## Consultar job migrador

```bash
gcloud run jobs executions list \
  --job=siniestro-facil-migrator-piloto \
  --project=project-77c17016-86bc-4fc4-a97 \
  --region=us-central1
```

## Consultar Cloud Build

```bash
gcloud builds list \
  --project=project-77c17016-86bc-4fc4-a97 \
  --region=us-central1 \
  --limit=10
```

## Diagnóstico

1. Obtener el `correlationId` de la respuesta.
2. Identificar la revisión activa.
3. Consultar el evento HTTP estructurado.
4. Revisar salud y conectividad de Cloud SQL.
5. Revisar la última migración y el último build.
6. Escalar sin copiar secretos, cuerpos o datos sensibles.

## Alertas

Las alertas automáticas permanecen pendientes hasta aprobar:

- Condición observable.
- Ventana de evaluación.
- Umbral.
- Canal.
- Destinatario responsable.
