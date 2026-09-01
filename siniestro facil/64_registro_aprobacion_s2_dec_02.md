# Registro de aprobación S2-DEC-02

## Decisión

- ID: `S2-DEC-02`.
- Fecha: 28 de agosto de 2026.
- Responsable: Product Owner.
- Estado: **APROBADA**.

## Configuración aprobada

- Bucket: `project-77c17016-86bc-4fc4-a97-siniestro-evidencias`.
- Región: `us-central1`.
- Acceso uniforme a nivel de bucket.
- Versionado de objetos habilitado.
- Sin acceso público.
- Sin bloqueo de política de retención hasta definir la normativa aplicable.

## Reglas de implementación

- Los objetos originales utilizan claves únicas y no se sobrescriben.
- El backend conserva SHA-256, URI, metadatos, fecha y fuente.
- Las versiones derivadas referencian explícitamente su original.
- La API de aplicación no elimina originales.
- La base de datos conserva la trazabilidad aunque el almacenamiento genere versiones.
- La creación del bucket requiere comandos explícitos y validación posterior en Cloud Shell.
- No se activa `retention lock` durante Sprint 2.

## Impacto

La decisión elimina el bloqueo de Definition of Ready de `S2-BE-03`. La retención definitiva continúa como decisión previa a producción.
