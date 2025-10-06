#!/bin/bash

# Hostinger deployment helper for PrioritiAI stack
# This script is intended to run on the Hostinger VPS via CI/CD (e.g. GitHub Actions)
# It ensures the repository is present, checks out the desired branch, and restarts the stack.

set -euo pipefail

REPO_URL=${REPO_URL:-}
REPO_DIR=${REPO_DIR:-/opt/TaskPriority}
DEPLOY_BRANCH=${DEPLOY_BRANCH:-main}
ENV_FILE=${ENV_FILE:-${REPO_DIR}/.env.production}
COMPOSE_FILE=${COMPOSE_FILE:-${REPO_DIR}/docker-compose-prod.yml}

if [[ -z "${REPO_URL}" ]]; then
  echo "REPO_URL environment variable must be set" >&2
  exit 1
fi

if [[ ! -d "${REPO_DIR}" ]]; then
  echo "📁 Cloning repository into ${REPO_DIR}"
  git clone "${REPO_URL}" "${REPO_DIR}"
fi

cd "${REPO_DIR}"

echo "🔄 Fetching latest changes for ${DEPLOY_BRANCH}"
if git show-ref --verify --quiet "refs/heads/${DEPLOY_BRANCH}"; then
  git checkout "${DEPLOY_BRANCH}"
else
  git checkout -b "${DEPLOY_BRANCH}" "origin/${DEPLOY_BRANCH}"
fi

git fetch origin "${DEPLOY_BRANCH}"
git reset --hard "origin/${DEPLOY_BRANCH}"

echo "🧾 Ensuring environment file exists at ${ENV_FILE}"
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Environment file ${ENV_FILE} not found. Create it before deploying." >&2
  exit 1
fi

echo "🐳 Deploying stack with docker compose"
docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  pull

docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  up -d --build --remove-orphans

echo "✅ Deployment complete"
