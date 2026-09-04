# Frontend React — Siniestro Fácil

Aplicación React + TypeScript iniciada para el Ciclo 8.

## Alcance inicial

- HU-01: reportar un siniestro desde el teléfono.
- HU-03: crear el reporte con información mínima.
- HU-06: consultar el estado y siguiente paso.
- Contratos tomados de `../12_api_backend_openapi.yaml`.

No se implementa un proveedor de autenticación hasta aprobar el mecanismo definitivo para usuarios del navegador. El cliente API admite un token inyectado, sin persistirlo.

## Desarrollo local

```bash
cd "$HOME/DMCPROJECTOS/siniestro facil/frontend"
cp .env.example .env
npm install
npm run dev
```

El backend local debe estar disponible en la URL configurada mediante `VITE_API_BASE_URL`.

## Validación

```bash
npm run typecheck
npm run build
```

## Integración con producción

El servicio Cloud Run es privado. El frontend no debe incorporar credenciales GCP ni llamar directamente al backend productivo hasta implementar la autenticación perimetral o una capa BFF aprobada.
