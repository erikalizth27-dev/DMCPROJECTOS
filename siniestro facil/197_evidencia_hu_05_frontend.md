# Evidencia — HU-05 Adjuntar evidencia desde React

## Entrega

Se incorporó el flujo autenticado para adjuntar fotografías y documentos a un siniestro visible:

1. React valida formato y límite de 10 MiB.
2. FastAPI valida nuevamente y emite una URL firmada V4.
3. React carga el original directamente al bucket privado.
4. React calcula SHA-256 y registra la evidencia mediante el endpoint existente.
5. El BFF conserva la autenticación de usuario y el aislamiento del backend privado.

## Archivos principales

- `backend/src/siniestro_facil/infrastructure/evidence_upload.py`
- `backend/src/siniestro_facil/api/routes/claims.py`
- `backend/src/siniestro_facil/api/schemas.py`
- `frontend/src/api/client.ts`
- `frontend/src/App.tsx`
- `backend/scripts/32_configure_evidence_upload.sh`

## Validación requerida antes de producción

```bash
cd "$HOME/DMCPROJECTOS/siniestro facil/backend"
python -m pytest -q

cd "$HOME/DMCPROJECTOS/siniestro facil/frontend"
npm ci
npm run typecheck
npm run build
```

Después de fusionar, ejecutar el script de configuración GCP, desplegar primero el backend y después el frontend. La prueba integral debe confirmar carga real, registro de metadatos y ausencia de acceso público al bucket.
