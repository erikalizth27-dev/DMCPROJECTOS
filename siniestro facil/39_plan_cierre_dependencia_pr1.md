# Plan de cierre — Dependencia entre PR #1 y PR #2

## Estado verificado

| Pull request | Contenido | Estado |
|---|---|---|
| PR #1 | Modelo físico, DDL, constraints, despliegue y datos sintéticos | Abierto, borrador, fusionable, no fusionado |
| PR #2 | SPEC Sprint 0, backend, Alembic, contratos y pruebas | Abierto, borrador |

PR #2 depende del modelo físico incorporado por PR #1. La base Cloud SQL ya
contiene el modelo y la revisión Alembic `20260825_01`, pero `main` todavía no
contiene todos los artefactos versionados del PR #1.

## Orden recomendado

1. Confirmar que PR #1 conserva los siete archivos esperados y no contiene
   secretos.
2. Confirmar que PR #1 es fusionable y no tiene comentarios bloqueantes.
3. Cambiar PR #1 de borrador a listo para revisión.
4. Fusionar PR #1 en `main` mediante merge commit o squash según la política del
   repositorio.
5. Actualizar la rama `agent/sprint-0-backend-specs` con el nuevo `main`.
6. Resolver cualquier conflicto sin eliminar migraciones ni evidencia.
7. Ejecutar nuevamente compilación y suite backend.
8. Confirmar que PR #2 permanece fusionable.

## Criterios de aceptación

- `main` contiene el modelo físico, DDL, pruebas y scripts aprobados.
- PR #1 figura como fusionado.
- PR #2 ya no declara una dependencia abierta de PR #1.
- No se duplican ni renombran revisiones Alembic aplicadas.
- La suite backend permanece completamente aprobada.
- No se ejecuta nuevamente el DDL inicial sobre Cloud SQL.

## Riesgos y controles

| Riesgo | Control |
|---|---|
| Ejecutar nuevamente el esquema inicial | La fusión Git no ejecuta SQL; no correr scripts de despliegue |
| Conflictos entre documentación física y migración | Conservar PR #1 como línea base y Alembic como cambios incrementales |
| Pérdida de cambios de PR #2 | Actualización no destructiva y revisión del diff antes de publicar |
| Fusionar un borrador sin aprobación | Requiere autorización explícita del Product Owner |

## Autorización requerida

La preparación documental está autorizada por el Sprint 0. Marcar PR #1 como
listo y fusionarlo son acciones de repositorio separadas y requieren confirmación
explícita.
