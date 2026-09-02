# Evidencia de regresión — segunda entrega S4-BE-03

## Contexto

- Fecha: 2 de septiembre de 2026.
- Entorno: Google Cloud Shell.
- Rama: `agent/sprint-4-backend`.

## Resultado

- Pruebas recolectadas: **269**.
- Pruebas aprobadas: **269**.
- Fallos: **0**.
- Advertencias: **1**, deprecación conocida de Starlette TestClient con httpx.
- Duración: **2.74 segundos**.

## Capacidades verificadas

- Autorización formal y cambio de presupuesto.
- Alcance por identidad, rol y asignación.
- Bloqueo de presupuesto y siniestro.
- Control optimista de versión.
- Restricción de aprobación de presupuestos vencidos.
- Persistencia atómica de decisión, cambio, estado, auditoría e idempotencia.
- Conflicto de Idempotency-Key.
- Migración `20260902_04` reversible.

## Conclusión

La regresión de la segunda entrega de S4-BE-03 fue exitosa. Resta desplegar la migración y validar el comportamiento real sobre PostgreSQL.
