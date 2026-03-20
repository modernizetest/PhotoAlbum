#!/bin/bash
# deploy-to-azure.sh – Build the Docker image, push it to Azure Container
# Registry, and update the running Container App.
#
# Prerequisites:
#   - Azure CLI (az) logged in
#   - Docker daemon running
#   - Azure infrastructure already provisioned via azure-setup.sh
#
# Usage:
#   ./deploy-to-azure.sh \
#     [--resource-group photoalbum-rg] \
#     [--prefix photoalbum] \
#     [--acr <acr-login-server>] \
#     [--tag latest]

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────
PREFIX="photoalbum"
RESOURCE_GROUP="${PREFIX}-rg"
IMAGE_TAG="latest"
ACR_LOGIN_SERVER=""

# ── Argument parsing ───────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --resource-group) RESOURCE_GROUP="$2"; shift 2 ;;
    --prefix)         PREFIX="$2";         shift 2 ;;
    --acr)            ACR_LOGIN_SERVER="$2"; shift 2 ;;
    --tag)            IMAGE_TAG="$2";       shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# ── Require az login ───────────────────────────────────────────────────────
if ! az account show > /dev/null 2>&1; then
  echo "❌  Not logged in to Azure. Run 'az login' first."
  exit 1
fi

# ── Discover ACR if not provided ───────────────────────────────────────────
if [[ -z "$ACR_LOGIN_SERVER" ]]; then
  ACR_NAME="${PREFIX//[-_]/}acr"
  echo "🔍  Looking up ACR '$ACR_NAME' in resource group '$RESOURCE_GROUP'..."
  ACR_LOGIN_SERVER=$(az acr show \
    --name "$ACR_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query loginServer -o tsv)
fi

IMAGE_NAME="${ACR_LOGIN_SERVER}/photo-album:${IMAGE_TAG}"
CONTAINER_APP_NAME="${PREFIX}-app"

echo "📦  Building Docker image: $IMAGE_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"

echo "🔐  Logging in to ACR: $ACR_LOGIN_SERVER"
az acr login --name "${ACR_LOGIN_SERVER%%.*}"

echo "📤  Pushing image to ACR..."
docker push "$IMAGE_NAME"

echo "🔄  Updating Container App '$CONTAINER_APP_NAME' with new image..."
az containerapp update \
  --name "$CONTAINER_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --image "$IMAGE_NAME" \
  --output none

APP_FQDN=$(az containerapp show \
  --name "$CONTAINER_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo "✅  Deployment complete!"
echo ""
echo "══════════════════════════════════════════════════════"
echo "  Image    : $IMAGE_NAME"
echo "  App URL  : https://$APP_FQDN"
echo "══════════════════════════════════════════════════════"
