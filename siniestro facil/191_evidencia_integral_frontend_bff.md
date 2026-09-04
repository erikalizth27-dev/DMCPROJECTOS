# Evidencia integral — Frontend, BFF e Identity Platform

Fecha: 2026-09-04  
Estado: validación productiva completada

## Componentes desplegados

| Componente | Revisión | Imagen |
|---|---|---|
| Frontend React | `siniestro-facil-frontend-prod-00002-vg6` | `sha256:572250af0d5e852f7053d251e5939bc126a92a67e3b12c8d39f6af641d328076` |
| Backend FastAPI | `siniestro-facil-backend-prod-00002-qmg` | `sha256:e95b167ecea3a815d69da15b1ff8890bff515d0de825f3cfb25fda5a7bb2d8cd` |
| BFF | `siniestro-facil-bff-prod` | `sha256:9b8b55d4972019e59c9bc895636d9e25b3c69ca960c1e00390121636be8a0b83` |

## Controles verificados

- Frontend público servido por Nginx sin privilegios.
- `/health/live` del frontend responde `{"status":"ok"}`.
- API key dedicada limitada a Identity Toolkit y al dominio productivo.
- Identity Platform habilitado para correo y contraseña.
- Dominio productivo registrado como autorizado.
- BFF limitado por CORS al frontend productivo.
- Backend continúa privado.
- BFF invoca el backend con `roles/run.invoker`.
- Backend verifica criptográficamente el JWT humano.
- Claims aprobados: `externo`, `asegurado`, `seguro-horizonte`.

## Resultado extremo a extremo

La consulta autenticada de un identificador inexistente devolvió:

```text
HTTP 404
codigo: CLAIM-NOT-FOUND
mensaje: Siniestro no encontrado
```

El resultado confirma que la petición atravesó Identity Platform, BFF, IAM de
Cloud Run, validación JWT, autorización funcional y persistencia, sin regresar
`AUTHENTICATION-REQUIRED`.

## Hardening del pipeline

El primer Cloud Build construyó y publicó la imagen, pero el deploy falló porque
usó la cuenta Compute predeterminada. El pipeline corregido:

- usa `siniestro-deployer-prod` como identidad de Cloud Build;
- despliega con `siniestro-frontend-prod` como identidad de ejecución;
- usa un tag de Git explícito;
- envía `siniestro facil` como contexto y excluye dependencias locales.
