# Decisión — Frontend React Dockerizado en Cloud Run

Fecha: 2026-09-04  
Estado: implementación inicial

## Decisión

El frontend React se compilará como contenido estático y se publicará en una
imagen Docker:

1. Node ejecuta typecheck y build de Vite.
2. Nginx sin privilegios sirve el resultado en el puerto 8080.
3. Cloud Run publica el frontend.
4. React consume exclusivamente el BFF productivo.
5. El BFF restringe CORS al dominio resultante del frontend.

## Controles

- Compilación reproducible mediante `npm ci`.
- Imagen de ejecución sin herramientas de compilación.
- Navegación SPA con fallback a `index.html`.
- Assets versionados con caché inmutable.
- Documento principal sin caché.
- Cabeceras contra MIME sniffing, framing y permisos innecesarios.
- Endpoint `/healthz` para validación operacional.
- Sin credenciales de servicio dentro de React.

## Pendiente

- Validar typecheck, build e imagen local.
- Proporcionar la API key web restringida de Identity Platform al build.
- Publicar la imagen en Artifact Registry.
- Desplegar el servicio `siniestro-facil-frontend-prod`.
- Actualizar `FRONTEND_ORIGIN` del BFF con el dominio productivo.
- Registrar el dominio en Identity Platform.
- Ejecutar la prueba autenticada integral.
