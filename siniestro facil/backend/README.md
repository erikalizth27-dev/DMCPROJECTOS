# Backend Siniestro Fácil — Sprint 0

Esqueleto técnico local. No configura CI/CD, observabilidad ni despliegue operativo en GCP.

## Requisitos

- Python 3.12+
- PostgreSQL compatible con el modelo físico

## Preparación local

```bash
cd "siniestro facil/backend"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
cp .env.example .env
```

No almacenes contraseñas reales en `.env.example` ni en GitHub.

## Ejecución local

```bash
uvicorn siniestro_facil.main:app --reload
```

Endpoints iniciales:

- `GET /health/live`
- `GET /health/ready`

`/health/ready` ejecuta `SELECT 1`, comprueba el esquema `siniestro_facil` y
devuelve HTTP 503 si PostgreSQL o el esquema no están disponibles.

Los contratos Pydantic de Sprint 0 se encuentran en

```text
src/siniestro_facil/api/schemas.py
```

Rechazan campos desconocidos y aplican las validaciones iniciales del OpenAPI.

La política RBAC inicial y la separación de funciones para pagos están en:

```text
src/siniestro_facil/domain/authorization.py
```

La autorización comprueba tanto el permiso del rol como el alcance del recurso.

## Validaciones

```bash
python -m compileall -q src tests
python -m pytest
```

## Migraciones con Alembic

Alembic toma la conexión exclusivamente de `DATABASE_URL`. Para inspeccionar el
estado sin ejecutar cambios:

```bash
alembic current
alembic history
```

La revisión inicial está en
`alembic/versions/20260825_01_sprint0_modelado.py`. Sólo después de aprobar las
decisiones de `26_decisiones_modelado_sprint_0.md`, se podrá ejecutar:

```bash
alembic upgrade head
```

No ejecutes `alembic downgrade` sobre una base con datos sin respaldo y
autorización explícita, porque elimina los objetos creados por la revisión.

### Ejecución desde Cloud Shell

No basta con tener la conexión en otra terminal: `DATABASE_URL` debe existir en el
proceso que ejecuta Alembic. El script prepara el proxy y la variable temporalmente:

```bash
bash scripts/01_migrate_cloudsql.sh
```

El script valida proyecto, instancia y base; pide escribir `MIGRAR`; solicita la
contraseña sin mostrarla; ejecuta `alembic upgrade head`; confirma la revisión
`20260825_01`; y limpia conexión, contraseña y proxy al terminar.

La conexión con servicios GCP, CI/CD y observabilidad se mantiene diferida según `20_plan_detallado_sprint_0.md`.

## Validación manual con Cloud SQL Proxy

El proxy y el backend deben ejecutarse en terminales separadas. La contraseña se
mantiene únicamente en memoria y nunca se escribe en `.env` ni en GitHub.


## Validaciones HTTP negativas de readiness

Con el ambiente virtual activo, los dos escenarios negativos se ejecutan en un
solo paso y sin conexión a Cloud SQL:

```bash
bash scripts/02_validate_readiness_negative.sh
```

El script exige HTTP 503 y valida los errores de `DATABASE_URL` ausente y
`DATABASE_SCHEMA` inválido. Los servidores temporales se cierran al finalizar.
