# Definition of Ready — Backend Siniestro Fácil

## Objetivo

Una historia puede entrar a un sprint de implementación backend únicamente cuando cumple todos los criterios de esta especificación.

## Criterios obligatorios

- Identificador de historia y actor definidos en `01_historias_usuario.md`.
- Criterios de aceptación verificables y sin marcas `[Pendiente]` aplicables a la historia.
- Requerimientos funcionales y no funcionales asociados.
- Flujo principal, alternos y errores de negocio definidos.
- Roles autorizados para cada operación.
- Datos de entrada, salida y reglas de validación definidos.
- Entidades afectadas y reglas de consistencia identificadas.
- Operaciones sensibles, auditables o idempotentes identificadas.
- Dependencias externas y comportamiento ante indisponibilidad definidos.
- Contrato API acordado o marcado explícitamente como cambio de contrato.
- Pruebas de aceptación, integración, seguridad y persistencia identificadas.
- Ninguna pregunta abierta de prioridad bloqueante.

## Definición de Done mínima

- Código revisado y fusionado mediante pull request.
- Pruebas unitarias, de integración y de contrato aprobadas.
- Migraciones aplicables y reversibles cuando exista cambio de datos.
- Autorización por rol y auditoría verificadas.
- Errores sin información sensible.
- Métricas, logs estructurados y trazas incorporados.
- Documentación OpenAPI actualizada.
- Criterios de aceptación demostrados en un ambiente no productivo.

## Estado actual

Las historias pueden priorizarse y estimarse. No deben marcarse listas para implementación mientras conserven decisiones `POR CONFIRMAR` en `17_preguntas_abiertas_backend.md`.

