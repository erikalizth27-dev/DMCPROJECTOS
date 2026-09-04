#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-siniestro-facil-backend-piloto}"
MIGRATION_JOB="${MIGRATION_JOB:-siniestro-facil-migrator-piloto}"
RUNTIME_SECRET="${RUNTIME_SECRET:-siniestro-database-url-piloto}"
MIGRATOR_SECRET="${MIGRATOR_SECRET:-siniestro-migrator-database-url-piloto}"
RUNTIME_SA="siniestro-backend-piloto@${PROJECT_ID}.iam.gserviceaccount.com"
MIGRATOR_SA="siniestro-migrator-piloto@${PROJECT_ID}.iam.gserviceaccount.com"
CORRELATION_ID="c7-acceptance-$(date -u +%Y%m%d%H%M%S)"
TEMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${TEMP_DIR}"
}
trap cleanup EXIT

echo "1/7 — Código, pruebas y Alembic"
python -m compileall -q src tests alembic
python -m pytest -q
alembic current

echo "2/7 — Cloud Run listo y privado"
SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}"   --project="${PROJECT_ID}"   --region="${REGION}"   --format='value(status.url)')"
READY_REVISION="$(gcloud run services describe "${SERVICE_NAME}"   --project="${PROJECT_ID}"   --region="${REGION}"   --format='value(status.latestReadyRevisionName)')"
test -n "${SERVICE_URL}"
test -n "${READY_REVISION}"

gcloud run services get-iam-policy "${SERVICE_NAME}"   --project="${PROJECT_ID}"   --region="${REGION}"   --format=json > "${TEMP_DIR}/service-iam.json"

python - "${TEMP_DIR}/service-iam.json" <<'PY'
import json
import sys

policy = json.load(open(sys.argv[1], encoding="utf-8"))
members = {
    member
    for binding in policy.get("bindings", [])
    for member in binding.get("members", [])
}
for forbidden in ("allUsers", "allAuthenticatedUsers"):
    if forbidden in members:
        raise SystemExit(f"Acceso público detectado: {forbidden}")
print("Acceso público: no detectado")
PY

echo "3/7 — Liveness y readiness autenticados"
IDENTITY_TOKEN="$(gcloud auth print-identity-token)"
curl -fsS   -H "Authorization: Bearer ${IDENTITY_TOKEN}"   -H "X-Correlation-ID: ${CORRELATION_ID}"   "${SERVICE_URL}/health/live" > "${TEMP_DIR}/live.json"
curl -fsS   -H "Authorization: Bearer ${IDENTITY_TOKEN}"   "${SERVICE_URL}/health/ready" > "${TEMP_DIR}/ready.json"

python - "${TEMP_DIR}/live.json" "${TEMP_DIR}/ready.json" <<'PY'
import json
import sys

live = json.load(open(sys.argv[1], encoding="utf-8"))
ready = json.load(open(sys.argv[2], encoding="utf-8"))
if live.get("status") != "ok":
    raise SystemExit(f"Liveness inválido: {live}")
if ready.get("status") != "ready" or ready.get("errors") != []:
    raise SystemExit(f"Readiness inválido: {ready}")
print("Liveness: OK")
print("Readiness: OK")
PY

echo "4/7 — Log estructurado y seguro"
for attempt in 1 2 3 4 5 6; do
  gcloud logging read     "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${SERVICE_NAME}\" AND jsonPayload.correlationId=\"${CORRELATION_ID}\""     --project="${PROJECT_ID}"     --limit=1     --order=desc     --format=json > "${TEMP_DIR}/log.json"
  if [[ "$(tr -d '[:space:]' < "${TEMP_DIR}/log.json")" != "[]" ]]; then
    break
  fi
  sleep 5
done

python - "${TEMP_DIR}/log.json" "${CORRELATION_ID}" <<'PY'
import json
import sys

entries = json.load(open(sys.argv[1], encoding="utf-8"))
if not entries:
    raise SystemExit("No apareció el log correlacionado")
entry = entries[0]
payload = entry.get("jsonPayload", {})
http = entry.get("httpRequest", {})
if payload.get("correlationId") != sys.argv[2]:
    raise SystemExit("Correlation ID inconsistente")
if payload.get("event") != "http_request":
    raise SystemExit("Evento estructurado ausente")
if http.get("status") != 200:
    raise SystemExit(f"Estado HTTP inesperado: {http}")
rendered = json.dumps(entry).lower()
for forbidden in (
    "authorization",
    "password",
    "database_url",
    "requestbody",
    "responsebody",
):
    if forbidden in rendered:
        raise SystemExit(f"Campo sensible detectado: {forbidden}")
print("Log estructurado: OK")
print("Datos sensibles: no detectados")
PY

echo "5/7 — Separación de secretos"
gcloud secrets get-iam-policy "${RUNTIME_SECRET}"   --project="${PROJECT_ID}"   --format=json > "${TEMP_DIR}/runtime-secret.json"
gcloud secrets get-iam-policy "${MIGRATOR_SECRET}"   --project="${PROJECT_ID}"   --format=json > "${TEMP_DIR}/migrator-secret.json"

python - "${TEMP_DIR}/runtime-secret.json" "${TEMP_DIR}/migrator-secret.json" "${RUNTIME_SA}" "${MIGRATOR_SA}" <<'PY'
import json
import sys

def members(path: str) -> set[str]:
    policy = json.load(open(path, encoding="utf-8"))
    return {
        member
        for binding in policy.get("bindings", [])
        if binding.get("role") == "roles/secretmanager.secretAccessor"
        for member in binding.get("members", [])
    }

runtime = members(sys.argv[1])
migrator = members(sys.argv[2])
runtime_sa = "serviceAccount:" + sys.argv[3]
migrator_sa = "serviceAccount:" + sys.argv[4]

if runtime_sa not in runtime or migrator_sa in runtime:
    raise SystemExit("Política del secreto runtime inválida")
if migrator_sa not in migrator or runtime_sa in migrator:
    raise SystemExit("Política del secreto migrador inválida")
print("Secretos e identidades separados: OK")
PY

echo "6/7 — Job migrador disponible"
JOB_READY="$(gcloud run jobs describe "${MIGRATION_JOB}"   --project="${PROJECT_ID}"   --region="${REGION}"   --format='value(status.conditions[0].status)')"
LAST_EXECUTION="$(gcloud run jobs executions list   --job="${MIGRATION_JOB}"   --project="${PROJECT_ID}"   --region="${REGION}"   --limit=1   --format='value(metadata.name)')"
test "${JOB_READY}" = "True"
test -n "${LAST_EXECUTION}"
echo "Job migrador: Ready"
echo "Última ejecución: ${LAST_EXECUTION}"

echo "7/7 — Entrega verificada"
LAST_SUCCESSFUL_BUILD="$(gcloud builds list   --project="${PROJECT_ID}"   --region="${REGION}"   --filter='status=SUCCESS'   --limit=1   --format='value(id)')"
test -n "${LAST_SUCCESSFUL_BUILD}"
echo "Revisión activa: ${READY_REVISION}"
echo "Build exitoso: ${LAST_SUCCESSFUL_BUILD}"
echo "CICLO 7 — VALIDACIÓN INTEGRAL COMPLETADA"
