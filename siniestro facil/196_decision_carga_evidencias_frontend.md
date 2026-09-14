# Decisión — Carga de evidencias del asegurado

## Estado

Aprobada el 2026-09-08.

## Alcance aprobado

- Carga directa al bucket privado mediante política firmada V4 POST de corta duración.
- Formatos admitidos: JPG, PNG y PDF.
- Tamaño máximo: 10 MiB por archivo.
- Conservación del archivo original en `gs://project-77c17016-86bc-4fc4-a97-siniestro-evidencias`.
- Registro posterior de URI, SHA-256, tipo, nombre, MIME y tamaño en el modelo físico existente.

## Controles

El backend autentica al usuario, verifica visibilidad del siniestro y valida extensión, MIME y tamaño antes de firmar. La política POST autoriza un objeto único y exige MIME permitido y tamaño entre 1 byte y 10 MiB. El navegador calcula el SHA-256; el backend verifica en GCS la URI, pertenencia, tamaño, MIME y hash antes de registrar los metadatos.

La identidad `siniestro-backend-prod` requiere `roles/storage.objectCreator` y `roles/storage.objectViewer` sobre el bucket y `roles/iam.serviceAccountTokenCreator` sobre sí misma para firmar. El bucket admite CORS únicamente desde el origen productivo del frontend.
