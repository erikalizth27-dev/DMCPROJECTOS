# Estado Sprint 4 — Backend Siniestro Fácil

## Estado general

- Avance: **5% — rama, alcance y trazabilidad inicial preparados**.
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

- **S4-DEC-01:** definir la vigencia de un presupuesto; las entrevistas exigen registrarla pero no indican duración.
- **S4-DEC-02:** definir qué roles pueden aprobar, observar o rechazar un presupuesto durante el piloto.
- **S4-DEC-03:** definir si los montos requieren niveles o umbrales de autorización; no existe información suficiente para inventarlos.

## Restricciones

- No se inventan días de vigencia, montos, monedas ni umbrales.
- No se habilita reparación, pago o cierre del siniestro dentro de Sprint 4.
- No se integra un taller externo real sin autorización posterior.
- No se fusiona el PR sin autorización explícita del Product Owner.
