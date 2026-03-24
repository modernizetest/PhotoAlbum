# .NET Upgrade Task Guidelines

Only add an upgrade task if the .NET version is out of mainstream support, is a non-LTS release (e.g., STS releases like .NET 9), or the user explicitly requests it. The upgrade task must be the first task if it exists.

## Latest Stable Versions

- .NET: 10 (LTS)

## Supported Upgrade Versions

- .NET Framework: 4.6.2, 4.7, 4.7.1, 4.7.2, 4.8, 4.8.1
- .NET Core: 3.1
- Modern .NET: 6.0, 8.0, 10.0

## Framework Compatibility

| Source Framework | Target Framework | SDK-Style Conversion Required | Key Migration Notes |
|-----------------|:----------------:|:----------------------------:|:-------------------:|
| .NET Framework 4.x | net10.0 | Yes | Full migration: SDK-style project, API changes, NuGet updates |
| .NET Core 3.1 | net10.0 | No | TFM update, API changes, NuGet updates |
| .NET 5 (EOL) | net10.0 | No | TFM update, NuGet updates |
| .NET 6 (LTS, EOL) | net10.0 | No | TFM update, NuGet updates |
| .NET 7 (STS, EOL) | net10.0 | No | TFM update, NuGet updates |
| .NET 8 (LTS) | net10.0 | No | TFM update, NuGet updates |
| .NET 9 (STS) | net10.0 | No | TFM update, NuGet updates |

## Upgrade Task Types and Included Changes

| Task Type | SDK-Style Conversion | TFM Update | NuGet Package Updates | API Migration |
|-----------|:--------------------:|:----------:|:---------------------:|:-------------:|
| .NET Framework to modern .NET | Yes | Yes | Yes | Yes |
| .NET LTS upgrade (e.g., 8.0 to 10.0) | No | Yes | Yes | If needed |
| .NET STS to LTS upgrade (e.g., 9 to 10) | No | Yes | Yes | If needed |
| Specific .NET version upgrade | No | Yes | Yes | If needed |

## .NET Task Selection Rules

When selecting the .NET upgrade task type, follow these rules in order:

- **Rule 1 -- Single task only**: Always create a **single** upgrade task that encompasses **all** necessary changes -- including SDK-style project conversion (if needed), target framework update, NuGet package updates, and API migration. **Never** split these into separate tasks in the main plan; the `create-dotnet-upgrade-plan` skill handles the detailed breakdown internally.
- **Rule 2 -- .NET Framework migration**: If the project uses .NET Framework, create a single task: "Migrate from .NET Framework to .NET 10" that includes SDK-style conversion, TFM update, NuGet updates, and API migration. Use `create-dotnet-upgrade-plan` skill with location `builtin`.
- **Rule 3 -- Out-of-support or STS version**: If the project uses an out-of-support version or STS release (e.g., .NET 9), create a single task: "Upgrade .NET to latest LTS (net10.0)". Use `create-dotnet-upgrade-plan` skill with location `builtin`.
- **Rule 4 -- User-specified version**: If the user explicitly requests a specific version, create a single task: "Upgrade .NET to version X". Use `create-dotnet-upgrade-plan` skill with location `builtin`.
