#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"
REGION="${REGION:-us-central1}"
DATABASE="${DATABASE:-DMCSINIESTROFACIL_PROD}"
SERVICE="${SERVICE:-siniestro-facil-backend-prod}"
MIGRATION_JOB="${MIGRATION_JOB:-siniestro-facil-migrator-prod}"
DEPLOYER_SA_NAME="${DEPLOYER_SA_NAME:-siniestro-deployer-prod}"
DEPLOYER_SA="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short=12 HEAD)}"
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$(cd "${BACKEND_DIR}/.." && pwd)"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

for command_name in gcloud git; do
  command -v "${command_name}" >/dev/null 2>&1 || fail "No se encontró ${command_name}."
done

[[ -z "$(git status --short)" ]] || fail "El árbol Git debe estar limpio."
[[ "$(git branch --show-current)" == "main" ]] || fail "La promoción debe ejecutarse desde main."
git fetch origin main --quiet
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || fail "main local no coincide con origin/main."

ACTIVE_PROJECT="$(gcloud config get-value project 2>/dev/null)"
[[ "${ACTIVE_PROJECT}" == "${PROJECT_ID}" ]] || fail "Proyecto activo inesperado: ${ACTIVE_PROJECT}."

DATABASE_FOUND="$(gcloud sql databases list --project="${PROJECT_ID}" --instance=dmcappasistidaia --filter="name=${DATABASE}" --format='value(name)')"
[[ "${DATABASE_FOUND}" == "${DATABASE}" ]] || fail "No existe la base aislada ${DATABASE}."

gcloud run jobs describe "${MIGRATION_JOB}" --project="${PROJECT_ID}" --region="${REGION}" >/dev/null
gcloud run services describe "${SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" >/dev/null
gcloud iam service-accounts describe "${DEPLOYER_SA}" --project="${PROJECT_ID}" >/dev/null

echo "Promoción Docker a producción"
echo "  Proyecto:  ${PROJECT_ID}"
echo "  Región:    ${REGION}"
echo "  Base:      ${DATABASE}"
echo "  Servicio:  ${SERVICE}"
echo "  Migrador:  ${MIGRATION_JOB}"
echo "  Imagen tag:${IMAGE_TAG}"
echo
read -r -p "Escriba PROMOVER para iniciar: " CONFIRMATION
[[ "${CONFIRMATION}" == "PROMOVER" ]] || fail "Promoción cancelada."

cd "${CASE_DIR}"
gcloud builds submit   --project="${PROJECT_ID}"   --region="${REGION}"   --config=backend/cloudbuild.production.yaml   --service-account="projects/${PROJECT_ID}/serviceAccounts/${DEPLOYER_SA}"   --substitutions="_REGION=${REGION},_IMAGE_TAG=${IMAGE_TAG},_SERVICE=${SERVICE},_MIGRATION_JOB=${MIGRATION_JOB},_DEPLOYER_SA=${DEPLOYER_SA_NAME}"   .

echo "Promoción Docker completada."
