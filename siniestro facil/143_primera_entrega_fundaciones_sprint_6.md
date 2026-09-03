# Primera entrega de fundaciones — Sprint 6

## Alcance implementado

- Dominio base de pagos con estados físicos `bloqueado` y `emitido`.
- Validación de monto, siniestro y preparador.
- Segregación entre preparador y supervisor autorizador.
- Bloqueo ante alerta crítica pendiente de revisión humana.
- Adaptador determinístico simulado que declara explícitamente que no transfiere dinero.
- Contratos de indicadores con disponibilidad explícita y fuentes.
- Ausencia de eventos representada como `no_disponible`, nunca como cero.
- Proyección de auditoría por rol con redacción del detalle sensible.
- Mapeo SQLAlchemy de las tablas físicas `pago` y `comunicacion`.

## Archivos principales

- `backend/src/siniestro_facil/domain/payment.py`
- `backend/src/siniestro_facil/domain/operational_metrics.py`
- `backend/src/siniestro_facil/domain/audit.py`
- `backend/src/siniestro_facil/infrastructure/payment_adapter.py`
- `backend/src/siniestro_facil/persistence/models.py`

## Pruebas añadidas

- `test_payment_foundations.py`: 7 casos.
- `test_operational_metrics.py`: 7 casos efectivos.
- `test_audit_foundations.py`: 5 casos.
- Total nuevo esperado: **19 pruebas**.
- Total de suite esperado: **361 pruebas**.

## Base de datos

No se requiere migración: `pago` y `comunicacion` ya existen en el modelo físico. Esta entrega solamente incorpora su mapeo ORM.

## Restricciones preservadas

- No existe transferencia monetaria real.
- No existe proveedor externo de pagos.
- No se inventaron fórmulas ni fuentes de indicadores.
- No se inventaron umbrales de autenticación o rate limiting.
- Los detalles sensibles se restringen por rol.

## Pendiente de validación

Ejecutar compilación, las 361 pruebas esperadas y `alembic current` en Cloud Shell.
