# Frontend React — Siniestro Fácil

Aplicación React + TypeScript del Ciclo 8 para reportar siniestros, consultar casos y adjuntar evidencias.

## Alcance

- HU-01: reportar un siniestro desde teléfono o escritorio.
- HU-03: crear el reporte con información mínima.
- HU-05: adjuntar fotografías, archivos PNG y documentos PDF.
- HU-06: consultar estado, siguiente paso e historial.
- Contratos tomados de `../12_api_backend_openapi.yaml`.

## Arquitectura productiva

El navegador se autentica con Identity Platform y envía el token al BFF público. El BFF valida el origen, conserva la identidad humana e invoca el backend privado de Cloud Run. Los archivos se cargan directamente al bucket privado mediante una política firmada; el backend verifica URI, tamaño, tipo y SHA-256 antes de registrar la evidencia.

El frontend no almacena contraseñas, tokens ni credenciales GCP.

## Desarrollo local

```bash
cd "$HOME/DMCPROJECTOS/siniestro facil/frontend"
cp .env.example .env
npm ci
npm run dev
```

Configura `VITE_API_BASE_URL` y `VITE_IDENTITY_PLATFORM_API_KEY` con valores apropiados para el entorno.

## Validación estática

```bash
npm audit
npm run typecheck
npm run build
```

## Prueba E2E autenticada

La prueba consulta un caso existente y verifica su historial sin crear reportes ni cargar archivos. Las credenciales se reciben exclusivamente por variables de entorno.

```bash
export E2E_BASE_URL="https://frontend.example"
export E2E_EMAIL="usuario@example.com"
export E2E_CASE_ID="14"
read -rsp "Contraseña: " E2E_PASSWORD
echo
export E2E_PASSWORD

npm run test:e2e

unset E2E_PASSWORD E2E_EMAIL E2E_CASE_ID E2E_BASE_URL
```

Nunca registres la contraseña ni los valores reales de autenticación en Git.
