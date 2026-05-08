---
name: azcli-appservicemi-deploy
description: Deployment steps for Azure App Service Managed Identity under the AzCLI flow
---

# AzCLI App Service Managed Identity Deployment

This skill provides deployment guidance for Azure App Service Managed Identity under the AzCLI flow. It is designed to be called when Azure App Service Managed Identity is identified as the target compute host for a service.

## Execution Steps
  **Below are the steps for Copilot to follow; ask Copilot to update or execute this plan. Add check list for the steps.** 
  Execution Steps:
    1. Env setup for AzCLI:
      1. Install AZ CLI if not installed.
      2. Ensure there is a default subscription set. If provided, override the default subscription with the provided subscription ID.
      3. Subscription ID: Use default subscription
      4. Install Service Connector AzCLI extension: az extension add --name serviceconnector-passwordless --upgrade
    2. Provisioning:
      - [MANDATORY] You MUST check if the resource group is missing or lacks any Azure resources. you MUST use EXACTLY one of the following skills (no alternative): `infrastructure-terraform-generation` or `infrastructure-bicep-generation` to generate IaC files and provision missing Azure resources if needed.
    3. Check Azure resources existence:
      1. Azure App Service Managed Instance for app fakeservice0:
        - name: <>, resource group: <>, subscription: <>, provisioningState: Succeeded, runningStatus: Running. Check with 'az webapp show -o json'
        - Check dependencies existence:
          1. azurecosmosdb: name: <>, resource group: <>.
          2. azuresqldatabase: name: <>, resource group: <>.
      2. Create missing resources:
        - If any resource is missing, ask user to provide the resource id or create a new one, then get the resource information with Az CLI command
        - If user want to create new resources, generate a script to do so using Azure CLI command. Run the script and confirms all resources are ready.
    4. Deployment:
      1. Azure App Service Managed Instance Deployment:
        1. Create deploy script as a separate file under `deploy-scripts/` to deploy the application with Azure CLI. Reference the script path in the plan instead of inlining it.
        2. Output: Azure CLI scripts in `deploy-scripts/`
      2. Deployment Validation:
        1. Call tool `appmod-get-app-logs` to check application logs and ensure the services are running.

## Tools Checklist
- Copilot MUST call the following tools as specified in the Execution Step. Mark tools complete when called. Do not make substitutions.
- [] appmod-get-app-logs  