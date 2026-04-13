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
  "description": ".NET version upgrade plan from .NET Framework 4.8 to .NET 10.0",
  "tasks": [
    {
      "type": "upgrade",
      "id": "001-upgrade-dotnet-to-net10",
      "description": "Upgrade ContosoUniversity from .NET Framework 4.8 to .NET 10.0",
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
