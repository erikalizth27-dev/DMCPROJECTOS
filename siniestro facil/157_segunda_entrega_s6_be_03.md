# Segunda entrega S6-BE-03 — PostgreSQL

## Alcance implementado

- Repositorio PostgreSQL de hechos operativos.
- Validación persistente de identidad y rol supervisor.
- Selección determinística de un caso fuente dentro del período solicitado.
- Primera asistencia correlacionada al mismo siniestro.
- Primera decisión limitada a eventos trazables aprobados:
  - `decision_presupuesto_registrada`;
  - `pago_autorizado`.
- Resultado identifica `siniestroFuenteId` para evitar presentar una observación individual como agregado.
- Cuando no existe un caso o evento requerido, el indicador queda `no_disponible`.
- Endpoint conectado a PostgreSQL cuando existe `DATABASE_URL`.

## Límites preservados

No se calculan promedios, porcentajes, percentiles ni tendencias porque las entrevistas no definieron fórmulas de agregación. Tampoco se inventan fuentes para satisfacción, costo operativo, llamadas adicionales ni pérdidas evitadas.

## Pruebas añadidas

Se añadieron **6 pruebas estructurales** del repositorio PostgreSQL. Total esperado: **421 pruebas**.

## Migración

No se requiere migración. Se consultan las tablas existentes `siniestro`, `asistencia`, `evento_linea_tiempo`, `identidad_actor` y `usuario_interno`.
