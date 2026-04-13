# .NET Upgrade Plan Template

## Schema Rules

- Use `upgradeTask` type from `tasks-schema.json`
- `successCriteria` values: **strings** (`"true"`, `"false"`)
- `skills.location`: `"builtin"` | `"project"` | `"remote"`
- `status`: `"pending"`

## Example: tasks.json

```json
{
  "$schema": "tasks-schema.json",
  "description": ".NET version upgrade plan from .NET Framework 4.6.1 to .NET 10.0",
  "tasks": [
    {
      "type": "upgrade",
      "id": "001-upgrade-dotnet-to-net10",
      "description": "Upgrade ContosoUniversity from .NET Framework 4.6.1 to .NET 10.0",
      "reason": ".NET Framework 4.6.1 reached end of support on April 26, 2022 and does not meet the minimum .NET Framework 4.6.2 requirement for Azure SDK (.NET Standard 2.0) compatibility. Upgrading to .NET 10.0 LTS ensures long-term support, access to modern APIs, and full Azure SDK compatibility.",
      "requirements": "Convert legacy non-SDK-style .csproj to modern SDK-style format. Change TargetFramework to net10.0. Change Sdk to Microsoft.NET.Sdk.Web. Remove packages.config after conversion. Remove packages included in framework. Remove incompatible packages. Upgrade remaining NuGet packages to .NET 10.0 compatible versions. Address any security vulnerabilities in dependencies.",
      "environmentConfiguration": null,
      "skills": [],
      "successCriteria": {
        "passBuild": "true",
        "generateNewUnitTests": "false",
        "passUnitTests": "true",
        "securityComplianceCheck": "true"
      },
      "status": "pending"
    }
  ],
  "metadata": {
    "planName": "upgrade-to-lts",
    "projectName": "ContosoUniversity",
    "language": "dotnet",
    "createdAt": "2026-02-13T00:00:00.000Z",
    "version": "1.0"
  }
}
```
