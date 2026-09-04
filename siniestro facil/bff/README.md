# Siniestro Fácil BFF

Puerta pública controlada entre React y el backend privado de Cloud Run.

- Valida el ID token de Identity Platform.
- Exige `actor_type`, `role` y `tenant_id`.
- Conserva el token humano en `Authorization`.
- Añade el token de servicio en `X-Serverless-Authorization`.
- Solo reenvía rutas bajo `/api/v1` y una lista reducida de cabeceras.
- No registra tokens ni cuerpos.

## Desarrollo

```bash
npm install
npm test
BACKEND_URL="https://..." npm start
```

El servicio usa credenciales predeterminadas de Google. En Cloud Run debe ejecutarse
como `siniestro-bff-prod@PROJECT_ID.iam.gserviceaccount.com`, con
`roles/run.invoker` sobre el backend privado.
