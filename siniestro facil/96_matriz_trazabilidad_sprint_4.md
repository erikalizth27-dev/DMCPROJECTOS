# Matriz de trazabilidad — Sprint 4 Backend

| Incremento | HU | Criterio verificable | RF | CU | Datos |
|---|---|---|---|---|---|
| S4-BE-01 | HU-17 | Derivar y programar revisión especializada | RF-11, RF-18 | CU-05 | inspeccion, asignacion_siniestro |
| S4-BE-01 | HU-18 | Programar inspección y cambiar estado | RF-11, RF-18 | CU-05 | inspeccion, siniestro, evento_linea_tiempo |
| S4-BE-02 | HU-14 | Consultar vigencia del presupuesto | RF-15 | CU-05 | presupuesto |
| S4-BE-02 | HU-19 | Recibir orden, diagnóstico y presupuesto | RF-15, RF-18 | CU-05 | inspeccion, presupuesto, proveedor |
| S4-BE-03 | HU-13 | Registrar autorización formal | RF-14, RF-18 | CU-06 | autorizacion, evento_linea_tiempo |
| S4-BE-03 | HU-20 | Registrar observaciones, alternativas y ampliaciones | RF-16, RF-18 | CU-05, CU-06 | cambio_presupuesto, autorizacion |

## Fuentes

- `01_historias_usuario.md`: HU-13, HU-14 y HU-17 a HU-20.
- `02_criterios_aceptacion.md`: inspección, vigencia, diagnóstico, autorización y cambios.
- `03_requerimientos_funcionales.md`: RF-11, RF-14, RF-15, RF-16 y RF-18.
- `05_casos_uso.md`: CU-05 y CU-06.
- `16_backlog_inicial_backend.md`: resultado esperado de Sprint 4.
- `93_acta_cierre_sprint_3.md`: elementos expresamente diferidos a Sprint 4.

## Decisiones aprobadas

- S4-DEC-01: vigencia de 15 días calendario y nueva versión después del vencimiento.
- S4-DEC-02: operador o ajustador asignado observa; supervisor aprueba o rechaza.
- S4-DEC-03: no se aplican umbrales monetarios diferenciados durante el piloto.

## Evidencia

- `97_registro_aprobacion_s4_decisiones.md`.
- `101_evidencia_regresion_s4_be_01.md`: 233/233 pruebas aprobadas.
- `102_evidencia_final_s4_be_01_postgresql.md`: persistencia, concurrencia, auditoría y rollback validados.
- `104_evidencia_regresion_s4_be_02.md`: 250/250 pruebas aprobadas.
- `105_evidencia_migracion_s4_be_02_cloudsql.md`: migración `20260902_03` validada.
- `106_evidencia_final_s4_be_02_postgresql.md`: presupuesto, inspección, idempotencia y auditoría validados.
- `110_evidencia_final_s4_be_03_postgresql.md`: roles, decisiones formales, idempotencia, auditoría y rollback validados.
- `111_evidencia_validacion_integral_sprint_4.md`: compilación, regresión, Alembic y tres validaciones PostgreSQL completadas.
