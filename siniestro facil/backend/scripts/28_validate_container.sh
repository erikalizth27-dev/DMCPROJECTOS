#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE_NAME="siniestro-facil-backend:ciclo-7-local"
CONTAINER_NAME="siniestro-facil-c7-validation"
PORT_VALUE="${PORT_VALUE:-8080}"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL no está configurada" >&2
  exit 1
fi

cleanup() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

echo "1/5 — Construcción"
docker build --pull -t "${IMAGE_NAME}" .

echo "2/5 — Usuario no privilegiado"
CONTAINER_USER="$(docker image inspect --format '{{.Config.User}}' "${IMAGE_NAME}")"
test "${CONTAINER_USER}" = "10001:10001"
echo "Usuario ${CONTAINER_USER}: OK"

echo "3/5 — Ausencia de secretos en configuración de imagen"
if docker image inspect "${IMAGE_NAME}" | grep -Fq "${DATABASE_URL}"; then
  echo "ERROR: DATABASE_URL encontrada en la configuración" >&2
  exit 1
fi
echo "Secretos embebidos: no detectados"

echo "4/5 — Arranque y salud"
docker run -d   --name "${CONTAINER_NAME}"   --network host   -e PORT="${PORT_VALUE}"   -e APP_ENV="validation"   -e APP_NAME="Siniestro Facil Backend"   -e APP_VERSION="ciclo-7-validation"   -e DATABASE_URL="${DATABASE_URL}"   -e DATABASE_SCHEMA="${DATABASE_SCHEMA:-siniestro_facil}"   -e IDENTITY_ISSUER="${IDENTITY_ISSUER:-https://identity.example.invalid}"   -e IDENTITY_AUDIENCE="${IDENTITY_AUDIENCE:-siniestro-facil-backend}"   "${IMAGE_NAME}"

python - "${PORT_VALUE}" <<'PY'
import json
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

port = sys.argv[1]
deadline = time.monotonic() + 30
last_error = None
while time.monotonic() < deadline:
    try:
        with urlopen(f"http://127.0.0.1:{port}/health/live", timeout=2) as response:
            live = json.load(response)
        if live.get("status") == "ok":
            break
    except (URLError, TimeoutError, ValueError) as exc:
        last_error = exc
        time.sleep(1)
else:
    raise SystemExit(f"El contenedor no respondió: {last_error}")

with urlopen(f"http://127.0.0.1:{port}/health/ready", timeout=10) as response:
    ready = json.load(response)
if ready.get("status") != "ready":
    raise SystemExit(f"Readiness inválido: {ready}")

print("Liveness: OK")
print("Readiness Cloud SQL: OK")
PY

echo "5/5 — Alembic dentro de la imagen"
docker exec "${CONTAINER_NAME}" alembic current

echo "C7-PLAT-01 — CONTENEDOR VALIDADO"
