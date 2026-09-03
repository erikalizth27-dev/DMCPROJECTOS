# Matriz de trazabilidad — Sprint 5 Backend

| Incremento | HU | Criterio verificable | RF | CU | Datos |
|---|---|---|---|---|---|
| S5-BE-01 | HU-22 | Alerta explicable y no equivalente a fraude confirmado | RF-19, RF-27 | CU-07 | alerta |
| S5-BE-01 | HU-23 | Señales visibles y origen diferenciado | RF-20 | CU-07 | senal_riesgo |
| S5-BE-01 | HU-26 | Versión, entradas y explicación reproducibles | RF-26 | CU-07, CU-09 | alerta, politica_alerta |
| S5-BE-02 | HU-22 | Confirmar, descartar o solicitar información con justificación | RF-21 | CU-07 | alerta, evento_linea_tiempo |
| S5-BE-02 | HU-24 | Detalle restringido y acceso sensible auditado | RF-23 | CU-09 | identidad_actor, evento_linea_tiempo |
| S5-BE-02 | HU-30 | Revisión humana de recomendación asistida | RF-27 | CU-07 | alerta, evento_linea_tiempo |
| S5-BE-03 | HU-25 | Relaciones visibles sin fusión de expedientes | RF-24, RF-25 | CU-08 | relacion_casos, siniestro |
| S5-BE-03 | HU-27 | Política configurable y versionada | RF-22, RF-26 | CU-07 | politica_alerta, alerta |

## Fuentes

- `01_historias_usuario.md`: HU-22 a HU-27 y HU-30.
- `02_criterios_aceptacion.md`: señales, revisión, acceso, relaciones y reproducibilidad.
- `03_requerimientos_funcionales.md`: RF-19 a RF-27.
- `05_casos_uso.md`: CU-07, CU-08 y CU-09.
- `07_modelo_logico.md`: alerta, senal_riesgo, politica_alerta y relacion_casos.
- `13_seguridad_rbac.md`: resumen operativo y detalle antifraude restringido.
- `14_flujos_reglas_backend.md`: tratamiento provisional por severidad y decisión humana.
- `16_backlog_inicial_backend.md`: resultado esperado de Sprint 5.
- `112_acta_cierre_sprint_4.md`: línea base y elementos diferidos.

## Decisiones requeridas

- S5-DEC-01: tratamiento provisional por severidad.
- S5-DEC-02: coincidencias normalizadas y revisión humana sin fusión.
- S5-DEC-03: adaptador determinístico simulado y reproducible.
