# Primera entrega S6-BE-03 — Indicadores verificables

## Alcance implementado

- Servicio de indicadores operativos restringido al supervisor.
- Período de consulta obligatorio, sin ventana temporal inventada.
- Tiempo hasta primera asistencia calculado solo con creación del siniestro y primera asistencia.
- Tiempo hasta decisión calculado solo con un evento de decisión trazable.
- Ausencia de eventos representada como `no_disponible`, nunca como cero.
- Satisfacción, costo operativo y pérdidas evitadas por fraude explícitamente no disponibles.
- Casos sin llamadas adicionales no calculado por falta de definición y fuente aprobada.
- Cada resultado conserva período, fuentes, disponibilidad y razón.
- Endpoint autenticado `GET /api/v1/indicadores/operativos`.

## Pruebas añadidas

- Cálculos con eventos completos.
- Eventos faltantes sin conversión a cero.
- Tres indicadores sin fuente explícitamente no disponibles.
- Restricción a supervisor.
- Validación del período.
- Contrato HTTP, período obligatorio y autenticación.

Total añadido: **10 pruebas**. Total esperado: **415 pruebas**.

## Pendiente

La segunda entrega conectará las fuentes PostgreSQL aprobadas y será validada contra Cloud SQL. No se requiere migración para esta primera entrega.
