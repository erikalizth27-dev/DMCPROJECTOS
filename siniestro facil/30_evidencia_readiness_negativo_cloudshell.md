# Evidencia — Readiness negativo en Cloud Shell

## Resultado

**APROBADO**. Los dos escenarios negativos del endpoint `GET /health/ready`
devolvieron HTTP `503` y el error funcional esperado.

## Destino de ejecución

| Elemento | Valor |
|---|---|
| Proyecto GCP | `project-77c17016-86bc-4fc4-a97` |
| Ejecución | Google Cloud Shell |
| Script | `backend/scripts/02_validate_readiness_negative.sh` |
| Escenarios | 2 |
| Aprobados | 2 |

## Resultados registrados

```text
OK: database_url_ausente devolvió HTTP 503 y el error esperado.
OK: esquema_invalido devolvió HTTP 503 y el error esperado.
OK: las 2 validaciones negativas de readiness finalizaron correctamente.
```

## Comportamientos verificados

1. Sin `DATABASE_URL`, el servicio responde `not_ready` y reporta
   `DATABASE_URL no configurada`.
2. Con `DATABASE_SCHEMA` diferente de `siniestro_facil`, el servicio responde
   `not_ready` e identifica la configuración inválida.
3. Ambos escenarios usan HTTP `503`.
4. Los procesos Uvicorn temporales finalizan después de cada prueba.
5. Los escenarios no requieren conexión ni cambios en Cloud SQL.

## Conclusión

El health check distingue correctamente disponibilidad del proceso (`live`) y
preparación de dependencias (`ready`). Queda cerrada la validación manual
negativa de readiness del Sprint 0.
