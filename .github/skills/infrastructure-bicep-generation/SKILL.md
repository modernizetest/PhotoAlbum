---
name: infrastructure-bicep-generation
description: Generate Bicep IaC files for Azure infrastructure provisioning
---

# Infrastructure Bicep Generation

## Overview

Generate Bicep files to provision Azure infrastructure.

## Workflow

1. **Gather rules** (call these tools before generating):
   - Call `appmod-get-available-region-sku` to get available regions and SKUs for all needed Azure resource types.
   - Call `appmod-get-iac-rules` with **deploymentTool=azcli** (Do NOT use azd)
   - For Azure landing zone, also call `appmod-get-waf-rules` to ensure Azure Well-Architected Framework compliance
   - Validate all generated files to ensure they are runnable and free of syntax errors: call 'get_errors' on all generated files and iterate until all errors are resolved.

2. **Generate files** Create a subfolder ${taskid} under ${modernization-work-folder}. Create a subfolder `./infra/` Generate files in the following structure:

```
/${modernization-work-folder}/${taskid}/
├── plan.md                 # What resources to provision and execution steps

./infra/
├── main.bicep              # Main template, orchestrates all modules
├── parameters.json         # Environment-specific parameters
├── modules/                # Reusable Bicep modules
│   └── [resource].bicep    # One module per resource type
├── deploy.sh               # Deployment script for Linux/macOS
├── deploy.ps1              # Deployment script for Windows
├── README.md               # Infrastructure documentation
├── resources-summary.md            # Machine-readable summary of provisioned Azure resources (see template below)
└── compliance.md           # Rules compliance report

```

3. **Deployment scripts** must use Azure CLI (`az deployment`), NOT azd.

4. **Generate resources-summary.md** after successful provisioning following the template in [../resources-summary-template.md](../resources-summary-template.md). This file is critical for downstream tasks (deployment, integration tests) to discover provisioned resources. Key requirements:
   - Include subscription ID, resource group, and location
   - List all compute resources with their endpoints
   - List all data resources (SQL, Cosmos, Storage) with connection string environment variable names
   - List all messaging resources (Service Bus, Event Hub) with namespace endpoints
   - Include the machine-readable JSON block at the end for programmatic parsing
   - Retrieve actual resource values using Azure CLI commands (e.g., `az resource show`, `az sql db show-connection-string`)

## Success Criteria

- All Bicep files pass `az bicep build` validation
- Deployment scripts are executable
- README.md documents all resources and parameters
- resources-summary.md is generated with actual provisioned resource information following the template format
- The JSON block in resources-summary.md contains valid, parseable resource metadata