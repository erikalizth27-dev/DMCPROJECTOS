# Registro de aprobación — DM-05 Retención de auditoría

## Decisión

El Product Owner aprobó DM-05 el 25 de agosto de 2026:

> Conservar auditoría durante cinco años desde el cierre, sin eliminación
> automática y sujeto a revisión normativa antes de producción.

## Alcance aprobado

- Eventos de línea de tiempo del siniestro.
- Accesos y consultas sensibles.
- Decisiones humanas y cambios de estado auditables.
- Evidencia de preparación y autorización de pagos.
- Revisiones de alertas y decisiones antifraude.

## Inicio del plazo

El período de cinco años comienza cuando el siniestro alcanza el estado
`cerrado`.

## Salvaguardas

- Cumplir cinco años no elimina ni anonimiza registros automáticamente.
- Antes de producción debe revisarse normativa, país y política corporativa.
- Cualquier eliminación futura requiere SPEC, autorización, migración/proceso,
  respaldo, pruebas y evidencia independiente.
- Las evidencias originales conservan su política propia; DM-05 no fija su plazo.

## Impacto técnico actual

No requiere migración PostgreSQL: la decisión define conservación, no borrado.
No se crea tarea programada, trigger, TTL ni política operativa en GCP durante
Sprint 0.

## Artefactos afectados

- `04_requerimientos_no_funcionales.md`.
- `13_seguridad_rbac.md`.
- `24_backlog_sprint_1_refinado.md`.
- `25_matriz_trazabilidad_sprint_1.md`.
- `26_decisiones_modelado_sprint_0.md`.
