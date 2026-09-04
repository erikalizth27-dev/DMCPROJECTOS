# Frontend React en Cloud Run

La imagen compila React/Vite con Node y sirve los archivos estáticos mediante
Nginx sin privilegios en el puerto 8080.

## Parámetros de compilación

- `VITE_API_BASE_URL`: URL del BFF terminada en `/api/v1`.
- `VITE_IDENTITY_PLATFORM_API_KEY`: clave web restringida de Identity Platform.

Estas variables quedan incorporadas al bundle del navegador. La API key identifica
el proyecto, pero no reemplaza autenticación ni autorización.

## Validación local

```bash
docker build \
  --build-arg VITE_API_BASE_URL=https://BFF/api/v1 \
  --build-arg VITE_IDENTITY_PLATFORM_API_KEY=CLAVE_DE_PRUEBA \
  --tag siniestro-facil-frontend:local \
  .

docker run --rm -p 8081:8080 siniestro-facil-frontend:local
```

Comprobar `http://localhost:8081/healthz` y la aplicación en
`http://localhost:8081/`.
