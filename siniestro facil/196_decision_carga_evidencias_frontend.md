# Decisión — Carga de evidencias del asegurado

## Estado

Aprobada el 2026-09-08.

## Alcance aprobado

- Carga directa al bucket privado mediante URL firmada V4 de corta duración.
- Formatos admitidos: JPG, PNG y PDF.
- Tamaño máximo: 10 MiB por archivo.
- Conservación del archivo original en `gs://project-77c17016-86bc-4fc4-a97-siniestro-evidencias`.
- Registro posterior de URI, SHA-256, tipo, nombre, MIME y tamaño en el modelo físico existente.

## Controles

El backend autentica al usuario, verifica visibilidad del siniestro y valida extensión, MIME y tamaño antes de firmar. La URL solo autoriza un `PUT` para un objeto único. El navegador calcula el SHA-256 y registra los metadatos después de completar la carga.

La identidad `siniestro-backend-prod` requiere `roles/storage.objectCreator` sobre el bucket y `roles/iam.serviceAccountTokenCreator` sobre sí misma para firmar. El bucket admite CORS únicamente desde el origen productivo del frontend.
