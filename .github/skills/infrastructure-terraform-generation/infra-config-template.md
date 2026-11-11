# Azure Resources Config

**IMPORTANT: (DO NOT include this section in output)**

- DO NOT include any sensitive information such as connection strings or credentials in this file. Instead, only include the names of environment variables where such information is stored, and ensure those environment variables are defined in the deployment scripts.
- Output ONLY the two sections below. No additional section or info not listed in the template. ONLY include resource table in section Resource List.

## Environment Info

| Property | Value |
|----------|-------|
| Subscription ID | `{subscription-id}` |
| Resource Group | `{resource-group-name}` |
| Location | `{location}` |

## Resource List

| Resource Type | Name | Region | Config Details |
|---------------|------|---------|----------------|
| {type} | `{name}` | {region} | {Resource name and key connection info only. e.g., login server for ACR, FQDN for databases, endpoint/URI for services, connection string for App Insights, client ID for Managed Identity} |
