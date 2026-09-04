#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"
REGION="${REGION:-us-central1}"
DEPLOYER_SERVICE_ACCOUNT="${DEPLOYER_SERVICE_ACCOUNT:-siniestro-deployer-piloto@${PROJECT_ID}.iam.gserviceaccount.com}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short=12 HEAD)}"
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$(cd "${BACKEND_DIR}/.." && pwd)"

if [[ -n "$(git status --short)" ]]; then
  echo "ERROR: el árbol Git debe estar limpio" >&2
  exit 1
fi

echo "Commit: $(git rev-parse HEAD)"
echo "Etiqueta: ${IMAGE_TAG}"
echo "Servicio: siniestro-facil-backend-piloto"
echo "Migración: siniestro-facil-migrator-piloto"

cd "${CASE_DIR}"

gcloud builds submit --project="${PROJECT_ID}" --region="${REGION}" --config=backend/cloudbuild.yaml --service-account="projects/${PROJECT_ID}/serviceAccounts/${DEPLOYER_SERVICE_ACCOUNT}" --substitutions="_REGION=${REGION},_IMAGE_TAG=${IMAGE_TAG}" .
