#!/bin/bash
# azure-setup.sh – Provision Azure infrastructure for the Photo Album application.
# Prerequisites: Azure CLI (az) logged in, Bicep CLI available.
#
# Usage:
#   ./azure-setup.sh [--location eastus] [--prefix photoalbum] [--resource-group photoalbum-rg]
#
# The script creates:
#   - Resource group
#   - Azure Container Registry
#   - Azure Container Apps environment (with Log Analytics)
#   - Azure Database for PostgreSQL Flexible Server
#   - Azure Container App (placeholder image on first deploy)

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────
LOCATION="eastus"
PREFIX="photoalbum"
RESOURCE_GROUP="${PREFIX}-rg"

# ── Argument parsing ───────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --location) LOCATION="$2"; shift 2 ;;
    --prefix)   PREFIX="$2";   shift 2 ;;
    --resource-group) RESOURCE_GROUP="$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# ── Require az login ───────────────────────────────────────────────────────
if ! az account show > /dev/null 2>&1; then
  echo "❌  Not logged in to Azure. Run 'az login' first."
  exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✅  Using subscription: $SUBSCRIPTION_ID"

# ── PostgreSQL password ────────────────────────────────────────────────────
if [[ -z "${POSTGRES_ADMIN_PASSWORD:-}" ]]; then
  read -r -s -p "Enter PostgreSQL admin password: " POSTGRES_ADMIN_PASSWORD
  echo
fi

if [[ ${#POSTGRES_ADMIN_PASSWORD} -lt 8 ]]; then
  echo "❌  Password must be at least 8 characters."
  exit 1
fi

# ── Resource group ─────────────────────────────────────────────────────────
echo "🔄  Creating resource group '$RESOURCE_GROUP' in '$LOCATION'..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none

echo "✅  Resource group ready."

# ── Deploy Bicep template ──────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BICEP_FILE="$SCRIPT_DIR/infra/main.bicep"

echo "🔄  Deploying Azure infrastructure (this may take several minutes)..."
DEPLOY_OUTPUT=$(az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$BICEP_FILE" \
  --parameters \
      prefix="$PREFIX" \
      location="$LOCATION" \
      postgresAdminUser="photoalbum" \
      postgresAdminPassword="$POSTGRES_ADMIN_PASSWORD" \
  --output json)

ACR_LOGIN_SERVER=$(echo "$DEPLOY_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['properties']['outputs']['acrLoginServer']['value'])")
POSTGRES_HOST=$(echo "$DEPLOY_OUTPUT"    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['properties']['outputs']['postgresHost']['value'])")
APP_FQDN=$(echo "$DEPLOY_OUTPUT"         | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['properties']['outputs']['containerAppFqdn']['value'])")

echo ""
echo "✅  Infrastructure deployment complete!"
echo ""
echo "══════════════════════════════════════════════════════"
echo "  ACR Login Server : $ACR_LOGIN_SERVER"
echo "  PostgreSQL Host  : $POSTGRES_HOST"
echo "  App URL          : https://$APP_FQDN"
echo "══════════════════════════════════════════════════════"
echo ""
echo "Next step – build and deploy the application image:"
echo "  POSTGRES_ADMIN_PASSWORD='<password>' \\"
echo "  ./deploy-to-azure.sh \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --prefix $PREFIX \\"
echo "    --acr $ACR_LOGIN_SERVER"
