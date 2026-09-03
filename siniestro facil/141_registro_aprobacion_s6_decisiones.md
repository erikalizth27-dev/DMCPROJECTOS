# Registro de aprobación — Decisiones Sprint 6

## Identificación

- Fecha: 3 de septiembre de 2026.
- Aprobador: Product Owner.
- Rama: `agent/sprint-6-backend`.
- Estado: **APROBADO**.

## S6-DEC-01 — Adaptador de pagos del piloto

- Se utilizará un adaptador determinístico simulado.
- No se realizarán transferencias monetarias reales.
- No se integrará todavía un proveedor externo de pagos.
- Se conservarán segregación de funciones, idempotencia y auditoría.

## S6-DEC-02 — Fuentes de indicadores

- Solo se calcularán indicadores cuando existan eventos y datos aprobados.
- La ausencia de datos no se representará como cero.
- Satisfacción, costo operativo y pérdidas evitadas se presentarán como no disponibles mientras no existan fuentes definidas.
- No se inventarán fórmulas, ventanas de agregación ni datos sintéticos.

## S6-DEC-03 — Estabilización de seguridad

- No se inventarán umbrales de autenticación reciente.
- No se inventarán valores de rate limiting.
- Se verificarán RBAC, alcance y segregación de funciones.
- Se verificarán auditoría y protección de información sensible.
- Los controles numéricos pendientes deberán aprobarse antes de producción.

## Impacto

- S6-BE-01 queda habilitado para fundaciones y desarrollo con simulación.
- S6-BE-02 permanece listo para desarrollo.
- S6-BE-03 queda habilitado con indicadores parciales y disponibilidad explícita.
- La estabilización de seguridad queda delimitada sin incorporar reglas no trazables.
