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

## Validaciones

```bash
python -m compileall -q src tests
python -m pytest
```

La conexión con servicios GCP, CI/CD y observabilidad se mantiene diferida según `20_plan_detallado_sprint_0.md`.

