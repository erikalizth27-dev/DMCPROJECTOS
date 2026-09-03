# Primera entrega S5-BE-03 — relaciones exactas

## Alcance

- Detección exclusiva mediante valores presentes e iguales después de normalización.
- Normalización Unicode, mayúsculas y espacios.
- Criterios permitidos: accidente, teléfono, cuenta bancaria, taller y persona.
- Pares de siniestros ordenados canónicamente.
- Candidatos pendientes de revisión humana.
- Sin fusión de expedientes.
- Sin inferencia de valores ausentes o vacíos.
- Repetición idempotente y conflicto HTTP 409.
- Acceso restringido a investigador o supervisor.

## API

`POST /api/v1/siniestros/{id}/relaciones/detectar`

## Pruebas

- Diez pruebas de servicio.
- Cuatro pruebas de API.
- Total nuevo: **14 pruebas**.
- Total esperado: **335 pruebas**.

## Estado

Primera entrega publicada. Pendiente validación Cloud Shell y persistencia PostgreSQL.
