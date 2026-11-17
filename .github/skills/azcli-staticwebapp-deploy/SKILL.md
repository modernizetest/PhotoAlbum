---
name: azcli-staticwebapp-deploy
description: Deployment steps for Azure Static Web App under the AzCLI flow
---

# AzCLI Static Web Deployment

## Overview

This skill provides deployment guidance for Azure Static Web App under the AzCLI flow, using some existing Azure resources. It is designed to be called when Azure Static Web App is identified as the target compute host for a service.

## Output file structure:

Create a subfolder ${taskid} under ${modernization-work-folder}. Generate files strictly in the following structure. DO NOT omit or add files or folders, and use exact file names for tracking:

```
/${modernization-work-folder}/${taskid}/
├── plan.md                 # Deployment plan with architecture, execution steps, and tracking
├── progress.md             # Deployment progress with real-time updates
├── deployment-summary.md   # Summary of deployment plan for quick reference
├── deploy-scripts/         # scripts for deployment
```

**IMPORTANT - Structural Rules (DO NOT include this section in output)**
- The plan MUST strictly follow the sections listed below, in the EXACT order.
- Do NOT add any additional sections such as: "Rollback Plan", "Cost Estimation", "Documentation Links", "Post-Deployment Recommendations" or any other sections not listed.
- You MUST generate the plan file strictly following the pattern first, then execute the plan. Do NOT execute any deployment scripts before the plan file is generated.

## Workflow

{Agent should fill in and polish the markdown template below to generate a deployment plan for the project. Then save it to '/${modernization-work-folder}/${taskid}/plan.md' file. Don't add extra validation steps unless it is required! Don't change the tool name!}

# Azure Deployment Plan for TestProject Project
## **Goal**
Based on the project to provide a plan to deploy the project to Azure using AZCLI. Since the IaC option is not specified, we will use bicep as the IaC option based on the target app services.

## **Project Information**
{
Summarize the project setup, example:  
**AppName**  
- **Stack**: ASP.NET Core 7.0 Razor Pages  
- **Type**: Task Manager web app with client-side JS  
- **Containerization**: Dockerfile present  
- **Dependencies**: None detected  
- **Hosting**: Azure Static Web Apps
}

## **Azure Resources Architecture**
> **Install the mermaid extension in IDE to view the architecture.**
(do not use </br> in strings when generating the diagram):
```mermaid
graph TD
%% Services
svcazurestaticwebapps_fakeservice0["`Name: fakeservice0
Path: ../test/project/fakeservice0
Language: js`"]
subgraph "Compute Resources"
%% Resources
azurestaticwebapps_fakeservice0("`fakeservice0 (Azure Static Web Apps)`")
end
subgraph "Dependency Resources"
%% Dependency Resources
azurecosmosdb_db0["`db0 (Azure Cosmos DB)`"]
azuresqldatabase_db1["`db1 (Azure SQL Database)`"]
azureappconfiguration_appconfig0["`appconfig0 (azureappconfiguration)`"]
azurestorageaccount_storage0["`storage0 (Azure Storage Account)`"]
azurekeyvault_keyvault["`Key Vault (Optional)`"]
end
%% Relationships
svcazurestaticwebapps_fakeservice0 --> |"hosted on"| azurestaticwebapps_fakeservice0
azurestaticwebapps_fakeservice0 -.-> |"secret"| azurecosmosdb_db0
azurestaticwebapps_fakeservice0 -.-> |"user-identity"| azuresqldatabase_db1
azurestaticwebapps_fakeservice0 -.-> |"user-identity"| azureappconfiguration_appconfig0
azurestaticwebapps_fakeservice0 -.-> |"user-identity"| azurestorageaccount_storage0
azureappconfiguration_appconfig0 -.-> |"Key Vault references"| azurekeyvault_keyvault
```


## **Existing Azure Resources**
| Resource Type | Name | SKU | Purpose | 
|---------------|------|-----|--------|
| Azure Static Web Apps | myapp | Standard |  Used to deploy project1 |
| Log Analytics | mylog | Standard  |  Not used |


** Missing resource**
{List required but missing resources.}


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
    5. Summarize Result:
      1. Use `appmod-summarize-result` tool to summarize the deployment result.
      2. Generating files: /${modernization-work-folder}/${taskid}/deployment-summary.md

## **Progress Tracking**
- Copilot must create and update `/${modernization-work-folder}/${taskid}/progress.md` after each step.  
- Progress should include:  
  - ✅ Completed tasks  
  - 🔲 Pending tasks  
  - ❌ Failed tasks with error notes
If a script fails, log the error, regenerate/fix the script, and retry until the step completes.  
- Example format:
- [x] Containerization complete (Dockerfile found at ./Dockerfile)
- [] Deployment in progress
  - Attempt 1 failed: ACR push error (unauthorized).
  - Fixed by regenerating deploy script with correct az acr login. Retrying...

## **Tools Checklist**
- Copilot MUST call the following tools as specified in the Execution Step. Mark tools complete when called. Do not make substitutions.
- [] appmod-summarize-result