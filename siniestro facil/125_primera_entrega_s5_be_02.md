# Primera entrega S5-BE-02 — revisión humana

## Alcance

- Revisión de alertas por investigador antifraude o supervisor.
- Decisiones permitidas:
  - confirmar;
  - descartar;
  - solicitar información.
- Justificación humana obligatoria.
- La alerta pendiente no se acepta como decisión.
- Control optimista mediante versión esperada.
- Repetición idempotente y conflicto HTTP 409.
- Endpoint autenticado:
  `PATCH /api/v1/siniestros/{id}/alertas/{alertaId}/revision`.

## Seguridad

- Operador y otros roles sin permiso no pueden registrar una revisión.
- La respuesta conserva el sujeto revisor en el contrato de aplicación.
- Ninguna decisión automática confirma fraude.

## Pruebas

- Diez casos de servicio, contando las tres decisiones parametrizadas.
- Cuatro casos de API.
- Total nuevo: **14 pruebas**.
- Total esperado de la suite: **314 pruebas**.

## Estado

Primera entrega publicada. Quedan pendientes persistencia PostgreSQL, auditoría de revisión y auditoría de accesos sensibles.
