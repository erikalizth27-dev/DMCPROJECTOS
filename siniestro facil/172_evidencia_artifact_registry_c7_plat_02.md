# Evidencia — Artifact Registry y Cloud Build C7-PLAT-02

## Resultado

La imagen del backend fue construida por Cloud Build y publicada en Artifact Registry.

## Recursos

- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Región: `us-central1`.
- Repositorio: `siniestro-facil`.
- Imagen etiquetada: `backend:44e590b320ac`.
- Digest: `sha256:37e81b3ed7dd0aee3f85d2ce286ecc541a44162677a01cad91932cd455612381`.
- Imagen inmutable: `us-central1-docker.pkg.dev/project-77c17016-86bc-4fc4-a97/siniestro-facil/backend@sha256:37e81b3ed7dd0aee3f85d2ce286ecc541a44162677a01cad91932cd455612381`.
- Build ID: `bc424709-0f2b-4d4c-b3b8-81618b18fe6d`.
- Estado: `SUCCESS`.
- Duración reportada: 1 minuto 12 segundos.

## Incidente controlado

El primer intento falló porque la cuenta de ejecución de Cloud Build no podía leer el objeto fuente del bucket temporal.

Se concedieron:

- `roles/storage.objectViewer` sobre el bucket de Cloud Build.
- `roles/artifactregistry.writer` sobre el repositorio.
- `roles/logging.logWriter` para los logs de construcción.

El segundo intento terminó correctamente.

## Alcance

- Artifact Registry: validado.
- Cloud Build: validado.
- Imagen inmutable: validada.
- Cloud Run: todavía no desplegado.
- Secret Manager e identidades de runtime/migración: pendientes.
