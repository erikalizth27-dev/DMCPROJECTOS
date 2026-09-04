# Decisión — Frontend React Dockerizado en Cloud Run

Fecha: 2026-09-04  
Estado: desplegado con ajuste operacional pendiente de promoción

## Decisión

El frontend React se compila como contenido estático y se publica en una
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
- Endpoint `/health/live` para validación operacional.
- Sin credenciales de servicio dentro de React.

## Evidencia del primer despliegue

- Servicio: `siniestro-facil-frontend-prod`.
- Revisión: `siniestro-facil-frontend-prod-00001-llv`.
- Imagen: `sha256:328c9b7e3d38ea49e32f19188e0eae1df5c2ad9ca2743cd959c1e0ae8ead0fe5`.
- Página principal: HTTP 200.
- La ruta `/healthz` fue atendida por la capa de Google con HTTP 404; se
  sustituye por `/health/live`.

## Pendiente

- Validar y promover la imagen con `/health/live`.
- Actualizar `FRONTEND_ORIGIN` del BFF con el dominio productivo.
- Restringir la API key al dominio productivo.
- Registrar el dominio en Identity Platform.
- Ejecutar la prueba autenticada integral.
