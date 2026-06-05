---
name: azcli-staticwebapp-deploy
description: Deployment steps for Azure Static Web App under the AzCLI flow
---

# AzCLI Static Web App Deployment

This skill provides deployment guidance for Azure Static Web App under the AzCLI flow. It is designed to be called when Azure Static Web App is identified as the target compute host for a service.

## Execution Steps
  **Below are the steps for Copilot to follow; ask Copilot to update or execute this plan. Add checklist for the steps.**
Execution Steps:
    1. Env setup for AzCLI:
        1. Install AZ CLI if not installed.
        2. Ensure there is a default subscription set. If provided, override the default subscription with the provided subscription ID.
        3. Subscription ID: Use default subscription
        4. For Azure Static Web App, make sure to install the latest Azure Static Web Apps CLI: npm install -g @azure/static-web-apps-cli
    2. Provisioning:
      - [MANDATORY] You MUST check if the resource group is missing or lacks any Azure resources. you MUST use EXACTLY one of the following skills (no alternative): `infrastructure-terraform-generation` or `infrastructure-bicep-generation` to generate IaC files and provision missing Azure resources if needed.
    3. Check Azure resources existence:
      1. Azure Static Web Apps for app fakeservice0:
        - name: <>, resource group: <>, subscription: <>, provisioningState: Succeeded. Check with 'az staticwebapp show -n <> -g <> -o json' (or 'az staticwebapp list -o json' for discovery)
        - Check dependencies existence:
          1. azurecosmosdb: name: <>, resource group: <>.
          2. azuresqldatabase: name: <>, resource group: <>.
      2. Create missing resources:
        - If any resource is missing, ask the user to provide the resource ID or create a new one, then get the resource information with an Azure CLI command
        - If the user wants to create new resources, generate a script to do so using Azure CLI commands. Run the script and confirm all resources are ready.
    4. Deployment:
      1. Azure Static Web App Deployment:
        1. Create deploy script as a separate file under `deploy-scripts/` to deploy the application with Azure CLI. Reference the script path in the plan instead of inlining it.
        2. Output: Azure CLI scripts in `deploy-scripts/`