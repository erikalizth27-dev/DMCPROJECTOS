# Estado Sprint 4 — Backend Siniestro Fácil

## Estado general

- Avance: **63% — regresión S4-BE-02 aprobada; pendiente migración Cloud SQL**.
- Rama: `agent/sprint-4-backend`.
- Punto de partida: `main` en `2d4cc89b498d9ba11fa41f4926fc7110f5b0a6e8`.
- Duración de referencia: 2 semanas.
- Objetivo: inspección, presupuestos y autorizaciones auditables.
- Línea base heredada: **201/201 pruebas aprobadas** y Alembic `20260902_02 (head)`.

## Distribución porcentual

| Fase | Resultado | Peso | Acumulado |
|---|---|---:|---:|
| Preparación | Rama, alcance, trazabilidad y decisiones | 5% | 5% |
| Fundaciones | Contratos, modelos y persistencia | 10% | 15% |
| S4-BE-01 | Programar y consultar inspección | 25% | 40% |
| S4-BE-02 | Orden, diagnóstico y presupuesto | 25% | 65% |
| S4-BE-03 | Autorizar, observar y registrar cambios | 20% | 85% |
| Integración | PostgreSQL y pruebas integrales | 10% | 95% |
| Cierre | Evidencias, acta y PR | 5% | 100% |

## Incrementos propuestos

- **S4-BE-01:** programar una inspección y consultar su estado aplicando RBAC, concurrencia y auditoría.
- **S4-BE-02:** entregar la orden al taller y registrar diagnóstico, presupuesto y vigencia.
- **S4-BE-03:** registrar formalmente aprobación, observación o rechazo y conservar cambios posteriores auditables.

## Decisiones pendientes

- **S4-DEC-01 — APROBADA:** vigencia de 15 días calendario; al vencer se presenta una nueva versión.
- **S4-DEC-02 — APROBADA:** operador o ajustador asignado observa; supervisor aprueba o rechaza.
- **S4-DEC-03 — APROBADA:** sin umbrales monetarios diferenciados durante el piloto; toda decisión queda registrada y auditada.

## Restricciones

- Se aplica la vigencia aprobada de 15 días; no se inventan monedas ni umbrales.
- No se habilita reparación, pago o cierre del siniestro dentro de Sprint 4.
- No se integra un taller externo real sin autorización posterior.
- No se fusiona el PR sin autorización explícita del Product Owner.


## Registro de aprobación

- S4-DEC-01, S4-DEC-02 y S4-DEC-03 aprobadas el 2 de septiembre de 2026.
- Evidencia: `97_registro_aprobacion_s4_decisiones.md`.
- S4-BE-01, S4-BE-02 y S4-BE-03 quedan habilitados para desarrollo.


## Primera entrega de fundaciones

- Modelos SQLAlchemy de inspección, presupuesto, autorización y cambio de presupuesto.
- Mapeo limitado a las columnas existentes en el modelo físico.
- Vigencia de 15 días calendario codificada.
- Presupuesto válido durante su fecha final y vencido al día siguiente.
- Operador o ajustador asignado puede observar.
- Solo supervisor puede aprobar o rechazar.
- Ausencia de umbrales monetarios preservada.
- Doce pruebas nuevas publicadas.
- Validación Cloud Shell: **213/213 pruebas aprobadas**.
- Alembic: `20260902_02 (head)`.
- Evidencia: `98_evidencia_primera_fundacion_sprint_4.md`.
- Pendiente: contratos y repositorios.


## Segunda entrega de fundaciones

- Contratos de contexto, inspección y presupuesto definidos.
- Repositorio PostgreSQL base incorporado.
- Operador o ajustador requiere asignación activa.
- Supervisor conserva acceso transversal.
- Taller limitado a presupuestos asociados con su proveedor.
- Consultas ocultan recursos inexistentes o fuera de alcance.
- Cinco pruebas nuevas publicadas.
- Validación Cloud Shell: **218/218 pruebas aprobadas**.
- Alembic: `20260902_02 (head)`.
- Evidencia: `99_evidencia_fundaciones_sprint_4.md`.
- Estado de fundaciones: **completado**.
- No requiere migración adicional.


## Primera entrega de S4-BE-01

- Caso de uso para programar inspección implementado.
- Consulta de inspección implementada.
- Operador y ajustador habilitados.
- Roles no autorizados rechazados.
- Motivo y fecha con zona horaria obligatorios.
- Versión incrementada en el contrato.
- Endpoint POST de programación.
- Endpoint GET de consulta.
- Recurso inexistente o ajeno ocultado con HTTP 404.
- Repositorio temporal en memoria; todavía no es persistencia final.
- Diez pruebas nuevas publicadas.
- Validación Cloud Shell: **228/228 pruebas aprobadas en 2.21 segundos**.
- Evidencia: `100_evidencia_primera_entrega_s4_be_01.md`.
- Pendiente: PostgreSQL, asignación real, bloqueo, auditoría y rollback.


## Segunda entrega de S4-BE-01

- Repositorio PostgreSQL de programación y consulta incorporado.
- Identidad interna y asignación activa verificadas antes de escribir.
- Siniestro bloqueado mediante `SELECT ... FOR UPDATE`.
- Versión esperada comprobada; conflicto responde HTTP 409.
- Transición a `inspeccion_programada` validada por la máquina de estados.
- Inspección, cambio de estado, incremento de versión y auditoría comparten una transacción.
- Consultas fuera de alcance o con relación incorrecta permanecen ocultas.
- Dependencia API conectada automáticamente a PostgreSQL cuando existe `DATABASE_URL`.
- Cinco pruebas nuevas publicadas.
- Validación Cloud Shell: **233/233 pruebas aprobadas en 2.28 segundos**.
- Evidencia: `101_evidencia_regresion_s4_be_01.md`.
- Script de validación Cloud SQL: `backend/scripts/09_validate_s4_be_01_postgresql.py`.
- Validación PostgreSQL: **completada**, con rollback y cero registros residuales.
- Evidencia final: `102_evidencia_final_s4_be_01_postgresql.md`.
- Estado de S4-BE-01: **completado**.


## Primera entrega de S4-BE-02

- Caso de uso para presentar presupuesto y diagnóstico implementado.
- Acceso de escritura limitado al rol taller.
- Siniestro, inspección y versión validados en el contrato.
- Vigencia calculada con la regla aprobada de 15 días calendario.
- Estado inicial del presupuesto: `recibido`.
- Estado resultante del siniestro: `presupuesto_recibido`.
- Consulta del presupuesto sin revelar relaciones ajenas.
- Endpoints POST de presentación y GET de consulta.
- No se agregaron monto, moneda ni umbrales inexistentes en las especificaciones.
- Repositorio temporal en memoria; PostgreSQL e idempotencia quedan para la segunda entrega.
- Diez pruebas nuevas publicadas.
- Validación Cloud Shell: **243/243 pruebas aprobadas en 2.34 segundos**.
- Evidencia: `103_evidencia_primera_entrega_s4_be_02.md`.
- Pendiente: persistencia PostgreSQL, vínculo con inspección, identidad de proveedor, bloqueo, idempotencia, auditoría y rollback.


## Segunda entrega de S4-BE-02

- Migración `20260902_03` creada.
- Presupuesto vinculado explícitamente con la inspección.
- Tabla `solicitud_presupuesto_idempotente` definida.
- Identidad del taller resuelta al proveedor persistido.
- Inspección y siniestro bloqueados antes de modificar.
- Versión del siniestro validada con conflicto HTTP 409.
- Transición a `presupuesto_recibido` validada.
- Presupuesto, estado, versión, auditoría e idempotencia comparten una transacción.
- Repetición idempotente devuelve el resultado previo; contenido diferente produce HTTP 409.
- API conectada automáticamente a PostgreSQL cuando existe `DATABASE_URL`.
- Siete pruebas nuevas publicadas.
- Validación Cloud Shell: **250/250 pruebas aprobadas en 2.31 segundos**.
- Evidencia: `104_evidencia_regresion_s4_be_02.md`.
- Pendiente: aplicar migración y ejecutar prueba PostgreSQL con rollback.
