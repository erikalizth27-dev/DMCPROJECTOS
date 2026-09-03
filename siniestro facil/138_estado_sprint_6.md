# Estado Sprint 6 — Backend Siniestro Fácil

## Estado general

- Avance: **5% — rama, alcance y decisiones pendientes definidos**.
- Rama: `agent/sprint-6-backend`.
- Punto de partida: `main` en `50c5de8852ef74297d4056c46f0146da9d9f857e`.
- Duración de referencia: 2 semanas.
- Objetivo: pagos, auditoría integral, indicadores, seguridad y estabilización funcional.
- Línea base heredada: Sprint 5 cerrado al 100%, **342 pruebas** y Alembic `20260903_03 (head)`.

## Distribución porcentual

| Fase | Resultado | Peso | Acumulado |
|---|---|---:|---:|
| Preparación | Rama, alcance, trazabilidad y decisiones | 5% | 5% |
| Fundaciones | Contratos de pagos, auditoría e indicadores | 10% | 15% |
| S6-BE-01 | Preparación y autorización de pagos | 25% | 40% |
| S6-BE-02 | Línea de tiempo y auditoría consolidada | 20% | 60% |
| S6-BE-03 | Indicadores operativos verificables | 20% | 80% |
| Estabilización | Seguridad, regresión y PostgreSQL | 15% | 95% |
| Cierre | Evidencias, acta y PR | 5% | 100% |

## Incrementos propuestos

- **S6-BE-01:** preparar y autorizar pagos con segregación de funciones, control de alertas críticas, concurrencia, idempotencia y auditoría.
- **S6-BE-02:** consultar la línea de tiempo completa del caso y registrar accesos sensibles según rol y alcance.
- **S6-BE-03:** exponer únicamente indicadores calculables con datos disponibles y documentar explícitamente los no calculables.

## Decisiones pendientes

- **S6-DEC-01 — Adaptador de pagos del piloto:** confirmar si se utilizará un adaptador determinístico simulado, sin transferencia monetaria real ni proveedor externo.
- **S6-DEC-02 — Indicadores:** confirmar que se calcularán solo métricas con eventos y datos disponibles; satisfacción, costo operativo y pérdidas evitadas quedarán sin valor hasta disponer de fuentes aprobadas.
- **S6-DEC-03 — Seguridad:** confirmar que no se inventarán umbrales de autenticación reciente ni rate limiting; se validarán RBAC, alcance, segregación, auditoría y ausencia de secretos en respuestas/logs.

## Restricciones

- La persona que prepara un pago no puede autorizarlo.
- Solo el supervisor puede autorizar pagos.
- Una alerta crítica bloquea el pago hasta revisión humana.
- No se emite dinero real durante el piloto sin aprobación de proveedor e integración.
- No se inventan fórmulas, ventanas, SLA ni umbrales.
- No se fusionará el PR sin autorización explícita del Product Owner.

## Próximo paso

Aprobar S6-DEC-01, S6-DEC-02 y S6-DEC-03; después ejecutar la línea base y comenzar las fundaciones.
