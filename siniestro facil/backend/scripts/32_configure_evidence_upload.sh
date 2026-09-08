#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"
BUCKET="${EVIDENCE_BUCKET:-project-77c17016-86bc-4fc4-a97-siniestro-evidencias}"
BACKEND_SA="siniestro-backend-prod@${PROJECT_ID}.iam.gserviceaccount.com"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CORS_FILE="${SCRIPT_DIR}/../config/evidence-bucket-cors.production.json"

gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --project="${PROJECT_ID}" \
  --member="serviceAccount:${BACKEND_SA}" \
  --role="roles/storage.objectCreator"

gcloud iam service-accounts add-iam-policy-binding "${BACKEND_SA}" \
  --project="${PROJECT_ID}" \
  --member="serviceAccount:${BACKEND_SA}" \
  --role="roles/iam.serviceAccountTokenCreator"

gcloud storage buckets update "gs://${BUCKET}" \
  --project="${PROJECT_ID}" \
  --cors-file="${CORS_FILE}"

echo "OK: permisos de firma, escritura y CORS configurados para evidencias."
