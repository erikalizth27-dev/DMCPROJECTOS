#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"
DEPLOYER="siniestro-deployer-prod@${PROJECT_ID}.iam.gserviceaccount.com"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
IMAGE_TAG="$(git -C "${CASE_DIR}" rev-parse --short=7 HEAD)"

: "${IDENTITY_PLATFORM_API_KEY:?IDENTITY_PLATFORM_API_KEY no configurada}"

gcloud builds submit "${CASE_DIR}"   --project="${PROJECT_ID}"   --config="${CASE_DIR}/frontend/cloudbuild.production.yaml"   --service-account="projects/${PROJECT_ID}/serviceAccounts/${DEPLOYER}"   --substitutions="_IMAGE_TAG=${IMAGE_TAG},_IDENTITY_PLATFORM_API_KEY=${IDENTITY_PLATFORM_API_KEY}"
