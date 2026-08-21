# Runbook — Validaciones negativas de readiness

## Alcance

Pruebas de sólo lectura. No crean, modifican ni eliminan datos o estructuras de PostgreSQL.

## Precondiciones

- Rama `agent/sprint-0-backend-specs` actualizada.
- Entorno virtual activado.
- Cloud SQL Proxy disponible.
- `DATABASE_URL` configurada únicamente en memoria.
- Contraseña no almacenada ni mostrada.

## Prueba 1 — Suite automatizada

```bash
cd ~/DMCPROJECTOS/"siniestro facil/backend"
source .venv/bin/activate
python -m pytest -v
```

Resultado esperado: `14 passed`.

## Prueba 2 — Esquema inexistente

Detener Uvicorn con `Ctrl+C`, sin detener Cloud SQL Proxy.

En la terminal del backend:

```bash
export DATABASE_SCHEMA="siniestro_facil_validacion_inexistente"

uvicorn siniestro_facil.main:app \
  --host=127.0.0.1 \
  --port=8080
```

En otra terminal:

```bash
curl --silent --show-error \
  --output /tmp/readiness_missing_schema.json \
  --write-out '%{http_code}\n' \
  http://127.0.0.1:8080/health/ready

python3 -m json.tool /tmp/readiness_missing_schema.json
```

Resultado esperado:

```text
503
```

```json
{
  "status": "not_ready",
  "errors": [
    "El esquema requerido siniestro_facil_validacion_inexistente no existe"
  ]
}
```

Restaurar la variable después de detener Uvicorn:

```bash
export DATABASE_SCHEMA="siniestro_facil"
```

## Prueba 3 — Conexión PostgreSQL interrumpida

Iniciar nuevamente Uvicorn con el esquema correcto y confirmar primero HTTP 200.

Después detener únicamente Cloud SQL Proxy con `Ctrl+C` en su terminal.

Ejecutar:

```bash
curl --silent --show-error \
  --max-time 15 \
  --output /tmp/readiness_database_unavailable.json \
  --write-out '%{http_code}\n' \
  http://127.0.0.1:8080/health/ready

python3 -m json.tool /tmp/readiness_database_unavailable.json
```

Resultado esperado:

```text
503
```

```json
{
  "status": "not_ready",
  "errors": [
    "No fue posible conectar con PostgreSQL"
  ]
}
```

El mensaje no debe incluir contraseña, host, puerto, stack trace ni detalle de la excepción.

## Restauración

1. Reiniciar Cloud SQL Proxy.
2. Reiniciar Uvicorn si fuera necesario.
3. Confirmar:

```bash
curl --fail --show-error \
  http://127.0.0.1:8080/health/ready |
python3 -m json.tool
```

Resultado esperado:

```json
{
  "status": "ready",
  "errors": []
}
```

## Evidencia

Registrar únicamente:

- fecha;
- prueba ejecutada;
- código HTTP;
- respuesta sin secretos;
- resultado aprobado o fallido.

No registrar `DATABASE_URL`, contraseña ni puerto temporal.
