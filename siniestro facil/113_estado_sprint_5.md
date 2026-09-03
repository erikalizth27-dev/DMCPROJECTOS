# Estado Sprint 5 — Backend Siniestro Fácil

## Estado general

- Avance: **50% — primera entrega S5-BE-02 validada; persistencia PostgreSQL en preparación**.
- Rama: `agent/sprint-5-backend`.
- Punto de partida: `main` en `83d17c2cf2c2cc7c0922c457ebc28f389c11c618`.
- Duración de referencia: 2 semanas.
- Objetivo: fraude, alertas reproducibles, relaciones entre casos y revisión humana.
- Línea base heredada: Sprint 4 cerrado al 100% y Alembic `20260902_05 (head)`.

## Distribución porcentual

| Fase | Resultado | Peso | Acumulado |
|---|---|---:|---:|
| Preparación | Rama, alcance, trazabilidad y decisiones | 5% | 5% |
| Fundaciones | Contratos, modelos y persistencia antifraude | 10% | 15% |
| S5-BE-01 | Señales y alertas reproducibles | 25% | 40% |
| S5-BE-02 | Revisión humana y acceso sensible | 25% | 65% |
| S5-BE-03 | Relaciones y política versionada | 20% | 85% |
| Integración | PostgreSQL y pruebas integrales | 10% | 95% |
| Cierre | Evidencias, acta y PR | 5% | 100% |

## Incrementos propuestos

- **S5-BE-01:** registrar señales determinísticas o de modelo y generar alertas explicables con versión y datos de origen.
- **S5-BE-02:** permitir al investigador o supervisor confirmar, descartar o solicitar información, registrando justificación, revisión humana y accesos sensibles.
- **S5-BE-03:** relacionar casos por criterios permitidos sin fusionarlos y aplicar una política antifraude configurable y versionada.

## Decisiones aprobadas

- **S5-DEC-01 — APROBADA:** aprobar para el piloto la política existente: crítica bloquea pago hasta revisión; alta deriva a investigación; media o baja aumenta prioridad. Ninguna alerta confirma fraude ni rechaza automáticamente.
- **S5-DEC-02 — APROBADA:** detectar relaciones únicamente mediante coincidencias exactas de valores normalizados disponibles; generar candidatos para revisión humana, sin fusión automática ni inferencia cuando falten datos.
- **S5-DEC-03 — APROBADA:** usar temporalmente un adaptador determinístico simulado de reglas/modelos, conservando versión, entradas y explicación; no integrar un modelo externo de IA en Sprint 5.

## Restricciones

- No se inventan umbrales monetarios ni ponderaciones.
- No se declara fraude automáticamente.
- No se rechaza cobertura ni se emite pago por una alerta.
- No se fusionan expedientes relacionados.
- El detalle antifraude permanece restringido a investigador y supervisor.
- No se fusiona el PR sin autorización explícita del Product Owner.

## Próximo paso

Ejecutar la línea base heredada y comenzar las fundaciones antifraude. Los tres incrementos están listos para desarrollo.

Evidencia de aprobación: `116_registro_aprobacion_s5_decisiones.md`.

## Línea base validada

- Compilación: aprobada.
- Suite heredada: **270/270 pruebas aprobadas en 2.79 segundos**.
- Alembic: `20260902_05 (head)`.
- Fallos: cero.
- Advertencia Starlette: conocida y no bloqueante.
- Evidencia: `117_evidencia_linea_base_sprint_5_cloudshell.md`.
- Próximo paso: contratos, catálogos y persistencia base antifraude.

## Primera entrega de fundaciones

- Dominio antifraude y efectos por severidad implementados.
- Normalización exacta y relación canónica sin autofusión.
- Adaptador determinístico, versionado y reproducible.
- Modelos de las cuatro tablas antifraude existentes.
- Once pruebas nuevas publicadas.
- Total esperado: **281 pruebas**.
- No requiere migración.
- Evidencia: `118_primera_entrega_fundaciones_sprint_5.md`.

## Fundaciones validadas

- Cloud Shell: **281/281 pruebas aprobadas en 2.64 segundos**.
- Alembic: `20260902_05 (head)`.
- Fallos: cero.
- Evidencia: `119_evidencia_fundaciones_sprint_5_cloudshell.md`.
- Estado de fundaciones: **completado**.
- Próximo incremento: S5-BE-01 — señales y alertas reproducibles.

## Primera entrega S5-BE-01

- Evaluación antifraude determinística y versionada.
- Efectos por severidad sin confirmación automática de fraude.
- Idempotencia y conflicto HTTP 409.
- Consulta de resumen o detalle según rol.
- Endpoints POST y GET autenticados.
- Doce pruebas nuevas publicadas.
- Total esperado: **293 pruebas**.
- Evidencia: `120_primera_entrega_s5_be_01.md`.
- Pendiente: PostgreSQL, auditoría atómica y validación con rollback.

## Primera entrega S5-BE-01 validada

- Cloud Shell: **293/293 pruebas aprobadas en 3.02 segundos**.
- Alembic: `20260902_05 (head)`.
- Fallos: cero.
- Evidencia: `121_evidencia_primera_entrega_s5_be_01.md`.
- Próximo paso: persistencia PostgreSQL, idempotencia persistente y auditoría atómica.


## Segunda entrega S5-BE-01

- Repositorio PostgreSQL para señales y alertas.
- Política antifraude localizada por versión exacta.
- Señales, alertas, auditoría e idempotencia en una transacción.
- Bloqueo del siniestro durante el registro.
- Recuperación segura frente a carreras de idempotencia.
- API conectada a PostgreSQL cuando existe `DATABASE_URL`.
- Migración Alembic `20260903_01` y script administrativo.
- Siete verificaciones nuevas; total esperado: **300 pruebas**.
- Evidencia de entrega: `122_segunda_entrega_s5_be_01.md`.
- Pendiente: aplicar migración, ejecutar regresión y validar PostgreSQL con rollback.


## Cierre S5-BE-01

- Migración aplicada: `20260903_01 (head)`.
- Regresión: **300 pruebas esperadas, sin fallos reportados**.
- PostgreSQL: señales, alertas y política versionada validadas.
- Idempotencia: repetición estable y conflicto HTTP 409 validados.
- Auditoría: dos evaluaciones registradas atómicamente.
- Limpieza: rollback sin registros residuales.
- Evidencia final: `124_evidencia_final_s5_be_01_postgresql.md`.
- Estado: **completado**.
- Próximo incremento: S5-BE-02 — revisión humana y acceso sensible.


## Primera entrega S5-BE-02

- Tres decisiones humanas admitidas.
- Justificación obligatoria.
- Control optimista de versión.
- Idempotencia y conflicto HTTP 409.
- Autorización restringida a investigador y supervisor.
- Endpoint PATCH autenticado.
- Catorce pruebas nuevas; total esperado: **314 pruebas**.
- Evidencia de entrega: `125_primera_entrega_s5_be_02.md`.
- Pendiente: validación Cloud Shell y persistencia PostgreSQL.


## Primera entrega S5-BE-02 validada

- Compilación: aprobada.
- Suite esperada: **314 pruebas**, sin fallos reportados.
- Alembic: `20260903_01 (head)`.
- Evidencia: `126_evidencia_primera_entrega_s5_be_02_cloudshell.md`.
- Próximo paso: persistencia, concurrencia y auditoría sensible.
