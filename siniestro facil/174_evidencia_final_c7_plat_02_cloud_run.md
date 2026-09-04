# Evidencia final — C7-PLAT-02 Cloud Run privado

## Resultado

**C7-PLAT-02 aprobado.**

El backend fue desplegado en Cloud Run mediante la imagen inmutable publicada en Artifact Registry.

## Configuración validada

- Proyecto: `project-77c17016-86bc-4fc4-a97`.
- Región: `us-central1`.
- Servicio: `siniestro-facil-backend-piloto`.
- Exposición: privada; acceso no autenticado deshabilitado.
- Cuenta de ejecución: `siniestro-backend-piloto@project-77c17016-86bc-4fc4-a97.iam.gserviceaccount.com`.
- Cloud SQL: conexión administrada a `dmcappasistidaia`.
- Secreto de runtime: `siniestro-database-url-piloto:1`.
- Imagen: `backend@sha256:37e81b3ed7dd0aee3f85d2ce286ecc541a44162677a01cad91932cd455612381`.
- Versión reportada por la aplicación: `44e590b320ac`.

## Smoke tests autenticados

### Liveness

```json
{
  "status": "ok",
  "service": "Siniestro Facil Backend",
  "version": "44e590b320ac"
}
```

### Readiness

```json
{
  "status": "ready",
  "errors": []
}
```

## Controles confirmados

- La invocación se realizó con token de identidad.
- No se habilitó acceso público.
- El contenedor inició correctamente.
- Cloud Run pudo acceder al secreto autorizado.
- La conexión desde Cloud Run hasta Cloud SQL fue exitosa.
- No se modificó el esquema de base de datos.

## Observación de terminal

Los mensajes posteriores `{status:: command not found` fueron producidos al pegar JSON de ejemplo en Bash. No afectaron el servicio ni las validaciones.
