# Primera entrega S6-BE-01 — Pagos

## Alcance implementado

- Preparación de pagos por operador, ajustador o supervisor autorizado.
- Pago preparado en estado `bloqueado`.
- Autorización exclusiva del supervisor.
- Segregación de funciones entre preparador y autorizador.
- Bloqueo ante alerta crítica pendiente de revisión humana.
- Control optimista de versión.
- Idempotencia y conflicto HTTP 409.
- Eventos de auditoría en el repositorio en memoria.
- Adaptador determinístico simulado sin transferencia monetaria real.
- Endpoints autenticados de preparación y autorización.

## Endpoints

- `POST /api/v1/siniestros/{siniestro_id}/pagos`
- `POST /api/v1/siniestros/{siniestro_id}/pagos/{pago_id}/autorizacion`

## Archivos principales

- `backend/src/siniestro_facil/application/manage_payment.py`
- `backend/src/siniestro_facil/api/routes/payments.py`
- `backend/src/siniestro_facil/main.py`

## Pruebas añadidas

- Servicio de pagos: 11 casos.
- API de pagos: 6 casos.
- Total nuevo: **17 pruebas**.
- Total esperado de la suite: **378 pruebas**.

## Restricciones preservadas

- No se transfiere dinero real.
- No se invoca un proveedor externo.
- La alerta crítica no autoriza rechazo ni fraude automático.
- Un identificador sin autorización no concede acceso.
- La persistencia PostgreSQL aún no está conectada a los endpoints.

## Pendiente

- Validación en Cloud Shell.
- Repositorio PostgreSQL, auditoría atómica e idempotencia persistente.
- Migración de soporte si resulta necesaria.
- Validación PostgreSQL con rollback.
