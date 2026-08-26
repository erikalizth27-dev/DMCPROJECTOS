# Decisiones de modelado — Cierre Sprint 0

## Estado

DM-01 a DM-04 están **MATERIALIZADAS** y validadas mediante la revisión Alembic `20260825_01`. DM-05 está **APROBADA** como política documental, sin automatización de borrado.

## DM-01 — Relación del tercero autorizado — MATERIALIZADA

Se agrega `reportante.relacion_asegurado`.

- Valores iniciales: `familiar`, `dependiente`, `testigo`, `otro`.
- Debe ser nulo cuando `es_titular = true`.
- Es obligatorio cuando `es_titular = false`.
- Declarar una relación no concede permisos sobre cobertura, reparación o pagos.

Origen: cierre simulado de la definición de persona autorizada y HU-04.

## DM-02 — Concurrencia optimista — MATERIALIZADA

Se agrega `siniestro.version` como entero no negativo, iniciado en cero.

- Todo comando de modificación recibe la versión conocida.
- La actualización utiliza `WHERE id_siniestro = ? AND version = ?`.
- Si ninguna fila cambia, el API devuelve HTTP 409.
- Una actualización correcta incrementa la versión en uno.

Esta regla evita que dos operadores sobrescriban cambios concurrentes.

## DM-03 — Siguiente paso calculado — MATERIALIZADA

`siguientePaso` no se almacena como columna.

Se calcula usando:

- estado actual;
- rol del solicitante;
- evidencia pendiente;
- asistencia, inspección y presupuesto;
- alertas bloqueantes y autorizaciones.

La respuesta puede variar por rol sin duplicar estado persistente. Las reglas se versionarán si pasan a ser configurables.

## DM-04 — Historial de asignaciones — MATERIALIZADA

Se crea `asignacion_siniestro` para materializar HU-11 y HU-12.

| Atributo | Propósito |
|---|---|
| id_asignacion | Identificador estructural |
| id_siniestro | Caso asignado |
| id_usuario | Responsable interno |
| motivo | Razón de asignación o reasignación |
| asignado_en | Inicio de responsabilidad |
| finalizado_en | Fin de responsabilidad, nulo si está activa |

Sólo puede existir una asignación activa por siniestro.

## DM-05 — Retención de auditoría — APROBADA

Se aprueba conservar eventos y accesos sensibles durante cinco años desde el cierre del siniestro.

- No implica eliminar automáticamente al cumplir el plazo.
- La eliminación o anonimización requiere política aprobada y proceso separado.
- El plazo debe validarse con normativa y política corporativa antes de producción.

## Impacto

- Modelo lógico: agrega dos atributos y una entidad.
- Modelo físico: requiere migración PostgreSQL.
- OpenAPI: `version` ya es obligatoria al cambiar estado.
- Sprint 1: concurrencia, asignación y cálculo de siguiente paso quedan desbloqueados.
- HU-04 conserva pendiente el mecanismo que demuestra autorización del tercero; la relación declarada ya está resuelta.
- DM-05 no habilita eliminación automática. Cualquier eliminación o anonimización requiere revisión normativa y una decisión separada antes de producción.

