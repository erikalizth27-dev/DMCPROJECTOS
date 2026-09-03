# Registro de aprobación de decisiones Sprint 4

## Aprobación

El 2 de septiembre de 2026, el Product Owner aprobó S4-DEC-01, S4-DEC-02 y S4-DEC-03.

## S4-DEC-01 — Vigencia del presupuesto

- Vigencia: 15 días calendario desde la presentación.
- Un presupuesto vencido no puede aprobarse.
- Al vencer debe presentarse como una nueva versión.
- La versión anterior permanece disponible para auditoría.

## S4-DEC-02 — Roles de decisión

- Operador asignado: puede observar.
- Ajustador asignado: puede observar.
- Supervisor: puede aprobar o rechazar.
- Toda operación aplica alcance, identidad, RBAC y auditoría.
- Un actor fuera de alcance no obtiene información sobre el recurso.

## S4-DEC-03 — Umbrales monetarios

- Durante el piloto no existen umbrales monetarios diferenciados.
- No se inventan niveles de autorización basados en montos.
- Toda aprobación o rechazo corresponde al supervisor.
- La ausencia de umbrales debe revisarse antes de producción.

## Reglas complementarias

- Toda decisión debe registrar actor, fecha, resultado y justificación disponible.
- Las modificaciones usan concurrencia optimista.
- Los comandos repetibles deben ser idempotentes.
- El presupuesto original no se sobrescribe al crear una nueva versión.
- La fusión del PR de Sprint 4 requiere autorización explícita posterior.
