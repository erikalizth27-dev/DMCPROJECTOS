# Evidencia de regresión — segunda entrega S4-BE-02

## Contexto

- Fecha: 2 de septiembre de 2026.
- Entorno: Google Cloud Shell.
- Rama: `agent/sprint-4-backend`.
- Alcance: persistencia e idempotencia de presupuestos.

## Resultado

- Pruebas recolectadas: **250**.
- Pruebas aprobadas: **250**.
- Fallos: **0**.
- Advertencias: **1**, deprecación conocida de Starlette TestClient con httpx.
- Duración: **2.31 segundos**.

## Capacidades verificadas

- Modelo del vínculo presupuesto–inspección.
- Modelo del registro idempotente.
- Identidad de taller vinculada al proveedor.
- Bloqueo de inspección y siniestro.
- Control de versión.
- Transición a `presupuesto_recibido`.
- Escritura atómica de presupuesto, estado, versión, auditoría e idempotencia.
- Repetición idempotente y conflicto por contenido diferente.
- Dependencia API PostgreSQL.

## Conclusión

La regresión automatizada fue exitosa. Resta aplicar `20260902_03` con privilegios administrativos y ejecutar la validación transaccional contra Cloud SQL.
