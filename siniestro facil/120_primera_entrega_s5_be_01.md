# Primera entrega S5-BE-01 — Evaluación y alertas

## Implementación

- Caso de uso de evaluación antifraude.
- Adaptador determinístico aprobado por S5-DEC-03.
- Registro temporal de alertas reproducibles.
- Regla de efectos por severidad de S5-DEC-01.
- Idempotencia con repetición segura y conflicto HTTP 409.
- Consulta de alerta con detalle según RBAC.
- Operador y ajustador reciben resumen.
- Investigador y supervisor reciben detalle reproducible.
- Endpoint POST de evaluación.
- Endpoint GET de alerta.

## Controles

- Solo investigador o supervisor puede iniciar la evaluación.
- Una alerta no confirma fraude ni rechaza automáticamente.
- Regla/modelo, versión de política, explicación y entradas forman parte del resultado.
- Solo hechos booleanos explícitos activan reglas.
- Autenticación denegada por defecto.

## Pruebas

- Siete pruebas del servicio.
- Cinco pruebas de API.
- Total esperado: **293 pruebas**.
- Estado: pendiente de validación en Cloud Shell.

## Pendiente para cerrar S5-BE-01

- Persistencia PostgreSQL.
- Idempotencia persistente.
- Política vigente desde base de datos.
- Señales, alertas y auditoría en una transacción.
- Validación real con rollback y cero residuos.
