# Evidencia de validación — Sprint 0 Backend

## Contexto

Validación manual ejecutada desde Google Cloud Shell contra la infraestructura del proyecto.

| Elemento | Valor |
|---|---|
| Project ID | `project-77c17016-86bc-4fc4-a97` |
| Instancia Cloud SQL | `dmcappasistidaia` |
| Base de datos | `DMCSINIESTROFACIL` |
| Esquema esperado | `siniestro_facil` |
| Backend | FastAPI local en Cloud Shell |
| Fecha de registro | 2026-08-20 |

## Resultado de readiness integrado

Petición ejecutada:

```bash
curl --fail --show-error \
  http://127.0.0.1:8080/health/ready |
python3 -m json.tool
```

Respuesta observada:

```json
{
  "status": "ready",
  "errors": []
}
```

## Conclusión

- El proceso FastAPI respondió correctamente.
- `DATABASE_URL` estuvo disponible únicamente en memoria.
- El backend pudo conectarse a PostgreSQL mediante Cloud SQL Proxy.
- `SELECT 1` finalizó correctamente.
- El esquema `siniestro_facil` fue encontrado.
- El endpoint devolvió HTTP 200.
- No se registraron contraseñas, puertos temporales ni credenciales.

## Validaciones aún pendientes de evidencia

- Ejecución de la suite actualizada con resultado esperado de 14 pruebas.
- Prueba negativa con proxy detenido, esperando HTTP 503.
- Prueba negativa con un nombre de esquema inexistente, esperando HTTP 503.
