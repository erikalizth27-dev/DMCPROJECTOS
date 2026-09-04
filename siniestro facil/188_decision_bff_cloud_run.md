# Decisión — BFF Dockerizado para el frontend

Fecha: 2026-09-04  
Estado: implementación inicial

## Decisión

El frontend React no invocará directamente el backend privado. Usará un BFF
Dockerizado en Cloud Run:

1. React obtiene un ID token mediante Identity Platform.
2. El BFF público valida firma, revocación y claims funcionales.
3. El BFF mantiene ese token en `Authorization`.
4. La identidad `siniestro-bff-prod` obtiene un ID token para el backend y lo
   envía en `X-Serverless-Authorization`.
5. Cloud Run autoriza al BFF y el backend conserva el contexto humano para RBAC.

## Controles

- Backend continúa privado.
- BFF solo acepta `/api/v1`.
- CORS restringido a `FRONTEND_ORIGIN`.
- No se reenvían cookies, `Host` ni tokens de infraestructura entrantes.
- Límite de cuerpo: 2 MiB.
- Correlación extremo a extremo sin registrar secretos.
- Imagen Docker inmutable publicada en Artifact Registry.

## Pendiente para desplegar

- Registrar `package-lock.json` después de `npm install`.
- Crear la cuenta `siniestro-bff-prod`.
- Concederle `roles/run.invoker` únicamente sobre el backend productivo.
- Sustituir el origen del frontend en Cloud Build.
- Desplegar y validar CORS, autenticación y proxy.
