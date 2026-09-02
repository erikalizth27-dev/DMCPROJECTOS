# Evidencia de regresión — segunda entrega S4-BE-01

## Contexto

- Fecha: 2 de septiembre de 2026.
- Entorno: Google Cloud Shell.
- Rama: `agent/sprint-4-backend`.
- Alcance: persistencia PostgreSQL para programación y consulta de inspecciones.

## Ejecución

```bash
python -m compileall -q src tests alembic
python -m pytest -v
alembic current
```

## Resultado

- Pruebas recolectadas: **233**.
- Pruebas aprobadas: **233**.
- Fallos: **0**.
- Advertencias: **1**, correspondiente a la deprecación conocida de `starlette.testclient` con `httpx`.
- Duración: **2.28 segundos**.
- Alembic: `20260902_02 (head)`.

## Capacidades verificadas

- Validación de roles y solicitudes de programación.
- Persistencia PostgreSQL preparada.
- Alcance por identidad y asignación activa.
- Bloqueo pesimista del siniestro.
- Control optimista mediante versión.
- Máquina de estados aplicada antes de persistir.
- Escritura atómica de inspección, estado, versión y auditoría.
- Consulta restringida al siniestro y actor autorizados.

## Conclusión

La regresión automatizada de la segunda entrega de S4-BE-01 fue exitosa. Resta ejecutar la validación transaccional contra Cloud SQL para cerrar el incremento.
