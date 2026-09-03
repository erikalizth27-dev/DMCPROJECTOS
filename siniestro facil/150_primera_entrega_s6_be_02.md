# Primera entrega S6-BE-02 — Línea de tiempo y auditoría

## Alcance implementado

- Contrato de consulta de línea de tiempo por siniestro.
- Orden y continuidad mediante cursor por identificador de evento.
- Cantidad opcional solicitada por el consumidor, sin imponer un umbral de negocio no aprobado.
- Inclusión de actor, fecha, tipo de evento y detalle permitido.
- Nivel de detalle por rol: limitado, operativo, investigación o completo.
- Redacción uniforme de eventos sensibles para roles sin acceso ampliado.
- Registro explícito de acceso cuando investigador o supervisor consulta eventos sensibles.
- Respuesta privada 404 cuando el expediente no existe o queda fuera del alcance.
- Endpoint autenticado `GET /api/v1/siniestros/{id}/linea-tiempo`.

## Pruebas añadidas

- Proyección operativa con detalle sensible restringido.
- Acceso completo del supervisor auditado.
- Acceso de investigación auditado.
- Cursor y cantidad solicitada.
- Respuesta privada fuera de alcance.
- Validaciones de parámetros.
- Contrato HTTP y autenticación obligatoria.

Total añadido: **12 pruebas**. Total esperado: **398 pruebas**.

## Sin migración

Esta entrega reutiliza `evento_linea_tiempo`. La conexión PostgreSQL, el alcance persistente y la escritura atómica de la auditoría de consulta se completarán en la segunda entrega de S6-BE-02.
