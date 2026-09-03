# Backlog refinado — Sprint 5 Backend

## Objetivo

Implementar señales de riesgo, alertas reproducibles, revisión humana, relaciones entre casos y política versionada, sin decisiones automáticas sensibles.

## S5-BE-01 — Registrar señales y generar alertas reproducibles

| Campo | Definición |
|---|---|
| Historias | HU-22, HU-23, HU-26 |
| Requisitos | RF-19, RF-20, RF-26, RF-27 |
| Caso de uso | CU-07 |
| Datos | senal_riesgo, alerta, politica_alerta, evento_linea_tiempo |

Criterios:

- Diferenciar señales determinísticas y de modelo.
- Registrar tipo, severidad, explicación, datos de origen y fecha.
- Conservar identificador y versión de la regla o modelo.
- Permitir reconstruir la alerta con sus entradas históricas.
- No convertir una inconsistencia en fraude confirmado.
- Aplicar idempotencia, alcance y auditoría atómica.

## S5-BE-02 — Revisar alertas y auditar accesos sensibles

| Campo | Definición |
|---|---|
| Historias | HU-22, HU-24, HU-30 |
| Requisitos | RF-21, RF-23, RF-27 |
| Casos de uso | CU-07, CU-09 |
| Datos | alerta, identidad_actor, evento_linea_tiempo |

Criterios:

- Investigador o supervisor puede confirmar, descartar o solicitar información.
- Toda revisión requiere justificación.
- Operador y ajustador ven solo el resumen autorizado.
- El detalle queda restringido a investigador y supervisor.
- Consultas sensibles y revisión humana quedan auditadas.
- Aplicar idempotencia y concurrencia.

## S5-BE-03 — Relacionar casos y aplicar política versionada

| Campo | Definición |
|---|---|
| Historias | HU-25, HU-26, HU-27 |
| Requisitos | RF-22, RF-24, RF-25, RF-26 |
| Casos de uso | CU-07, CU-08 |
| Datos | relacion_casos, politica_alerta, alerta, siniestro |

Criterios:

- Relacionar expedientes sin fusionarlos.
- Conservar valor declarado y normalizado cuando exista.
- Registrar el criterio que produjo cada relación.
- Asociar cada alerta con la versión de política aplicada.
- Mantener reproducibilidad aunque cambie la política.
- No aplicar umbrales no aprobados.

## Fuera de alcance

- Confirmación automática de fraude.
- Rechazo automático de cobertura.
- Integración productiva con un modelo externo de IA.
- Pagos e indemnización.
- CI/CD, Cloud Run y observabilidad productiva.

## Definition of Ready

| Incremento | Estado | Condición pendiente |
|---|---|---|
| S5-BE-01 | Completado | Evidencia PostgreSQL y rollback aprobados |
| S5-BE-02 | Completado | Evidencia PostgreSQL y rollback aprobados |
| S5-BE-03 | Listo | S5-DEC-01 y S5-DEC-02 aprobadas |


## Evidencia de ejecución

- S5-BE-01: **completado**.
- Migración: `20260903_01`.
- Evidencia final: `124_evidencia_final_s5_be_01_postgresql.md`.


- S5-BE-02: **completado** en `129_evidencia_final_s5_be_02_postgresql.md`.
