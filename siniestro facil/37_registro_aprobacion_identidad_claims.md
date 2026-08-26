# Registro de aprobación — Identidad y claims

## Decisión

El Product Owner aprobó explícitamente `ID-01`, `ID-02`, `ID-03`, `ID-04`,
`ID-05` e `ID-06` el 25 de agosto de 2026.

## Línea base aprobada

- Identity Platform para identidades humanas.
- IAM y cuentas de servicio para comunicación entre cargas.
- Claims estándar JWT más `role`, `actor_type` y `tenant_id`.
- Alcance de recursos resuelto en PostgreSQL, no dentro del token.
- Denegación por defecto y códigos `401`, `403`, `404` y `422`.
- Prohibición de almacenar JWT, credenciales o secretos.

## Implementación Sprint 0

`backend/src/siniestro_facil/domain/identity.py` valida claims provenientes de
un JWT cuya firma ya haya verificado el adaptador de Identity Platform:

- emisor y audiencia exactos;
- expiración y fechas futuras;
- sujeto y tenant obligatorios;
- rol dentro del catálogo RBAC;
- tipo de actor permitido.

La configuración utiliza `IDENTITY_ISSUER` e `IDENTITY_AUDIENCE`. Estas
variables no contienen secretos.

## Separación de responsabilidades

La validación criptográfica del JWT pertenece al futuro adaptador de Identity
Platform. `validate_verified_claims` no acepta tokens crudos y documenta que la
firma debe verificarse antes. No se configuró Identity Platform ni IAM en GCP.

## Pruebas agregadas

- Nueve pruebas del contrato de claims.
- Dos pruebas adicionales de configuración.
- Total esperado de la suite: 53 pruebas.

## Artefactos actualizados

- `36_propuesta_identidad_claims.md`.
- `12_api_backend_openapi.yaml`.
- `13_seguridad_rbac.md`.
- `17_preguntas_abiertas_backend.md`.
- `backend/.env.example`.
- `backend/src/siniestro_facil/config.py`.
- `backend/src/siniestro_facil/domain/identity.py`.
- `backend/tests/test_config.py`.
- `backend/tests/test_identity.py`.
