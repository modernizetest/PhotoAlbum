---
name: assessment
description: Run application assessment for a single repository
---

# Application Assessment

This skill performs application assessment for a single repository using AppCAT tools.

## Input Parameters

- `workspace-path` (optional): Path to the project to assess. Defaults to the current directory (repository root) when not specified. All assessment outputs are written relative to this path (e.g. `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`). For a repository with multiple sub-projects, pass the sub-project directory path so that each sub-project's outputs are isolated.

## When to Use This Skill

Use this skill when you need to:

- Assess a Java or .NET application for cloud readiness and migration issues
- Generate detailed assessment reports with issue analysis and recommendations
- Understand application dependencies, frameworks, and potential migration blockers

## What This Skill Does

This skill performs a simplified assessment workflow:

1. **Check Project Type and Prerequisites**:
   - **For Java projects**: Verify that MCP tools are available ('appmod-precheck-assessment' and 'appmod-run-assessment')
     - If these MCP tools are not configured, return immediately with setup instructions
   - **For .NET projects**: Check if .NET SDK is available
     - No MCP tools required for .NET assessment

2. **Run Assessment**:
   - **For Java projects**: Trigger AppCAT analysis via Assessment MCP server
     - Uses 'appmod-precheck-assessment' and 'appmod-run-assessment' MCP tools
     - Auto-detects project configuration within `{workspace-path}`
   - **For .NET projects**: Install and run AppCAT directly
     - Install: `dotnet tool update dotnet-appcat`
     - Find all .csproj files under `{workspace-path}`
     - Join project paths with semicolons: `projectPaths="project1.csproj;project2.csproj"`
     - Run: `dotnet-appcat analyze $projectPaths --source Solution --target Any --serializer APPMODJSON --code --privacyMode Restricted --non-interactive --report {workspace-path}\.github\modernize\assessment\report.json`
   - Analyzes code for cloud migration issues
   - Generates structured assessment data

3. **Save Report to Versioned Directory**:
   - **For Java projects**: Search for `report.json` under `{workspace-path}/.github/appmod/appcat/result/` subdirectories
   - **For .NET projects**: The report is at `{workspace-path}/.github/modernize/assessment/report.json`
   - Read the generated `report.json` and extract the `metadata.analysisStartTime` field
   - Format the timestamp as `yyyyMMddHHmmss` to produce the `reportId` (e.g. `2024-06-15T14:30:52Z` becomes `20240615143052`)
   - Create the versioned directory: `mkdir -p {workspace-path}/.github/modernize/assessment/reports/report-{reportId}`
   - Move the report to: `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`
   - This versioned report should be included in the pull request

## How to Use

### Prerequisites

**For Java projects**:
- MCP tools must be available: 'appmod-precheck-assessment' and 'appmod-run-assessment'
- If tools are not configured, the skill will return instructions for setup

**For .NET projects**:
- .NET SDK must be installed
- No MCP tools required - appcat will be installed and run directly via .NET CLI
- The assessment will automatically install `dotnet-appcat` tool if not already present

### Triggering Assessment

Simply express the intent to assess the application. Example prompts:

- "Assess the application"
- "Run assessment for this project"

The assessment process automatically:
- Detects project language and framework within `{workspace-path}`
- **For Java**: Uses MCP tools to install and run AppCAT
- **For .NET**: Installs dotnet-appcat tool and runs analysis directly
- Executes comprehensive analysis

### Report Saving

**For Java projects**:
1. Search for `report.json` files under `{workspace-path}/.github/appmod/appcat/result/` subdirectories
2. If multiple reports exist, identify the most recently modified one
3. Read the report and extract `metadata.analysisStartTime`, format as `yyyyMMddHHmmss` to get `reportId`
4. Move the report to `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`
5. Include this versioned report in the pull request

**For .NET projects**:
1. Report is initially generated at `{workspace-path}/.github/modernize/assessment/report.json`
2. Read the report and extract `metadata.analysisStartTime`, format as `yyyyMMddHHmmss` to get `reportId`
3. Move the report to `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`
4. Include this versioned report in the pull request

## Report Output Location

Report location depends on project type:

**For Java projects** (via MCP server):
- Initially stored under `{workspace-path}/.github/appmod/appcat/result/` subdirectories
- Saved to versioned directory: `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`

**For .NET projects** (direct execution):
- Initially generated at: `{workspace-path}/.github/modernize/assessment/report.json`
- Moved to versioned directory: `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`

Final report location (include this in pull request):
- `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`

Where `{reportId}` is derived from `metadata.analysisStartTime` in the report, formatted as `yyyyMMddHHmmss`.

## Success Criteria

Assessment is complete when:
- ✅ **For Java**: MCP server is available (or clear instructions provided if not)
- ✅ **For .NET**: .NET SDK is available and dotnet-appcat tool is installed
- ✅ AppCAT analysis executes without errors
- ✅ Report generated at `{workspace-path}/.github/modernize/assessment/reports/report-{reportId}/report.json`
- ✅ Report metadata includes assessment tool version, timestamp, and configuration

## Troubleshooting

**Prerequisites Not Met**:
- **For Java**: Verify MCP tools are available ('appmod-precheck-assessment' and 'appmod-run-assessment')
  - Return immediately with setup instructions if tools are not available
  - Do not attempt to run assessment without MCP
- **For .NET**: Verify .NET SDK is installed
  - Check with `dotnet --version` command
  - Provide installation instructions if .NET SDK is missing

**Assessment Failures**:
- Unsupported project type (only Java and .NET supported)
- **For Java**: MCP server communication errors
- **For .NET**:
  - dotnet-appcat tool installation failure
  - dotnet-appcat command execution errors
- Invalid project structure or build configuration

**Report Generation Issues**:
- **For Java**: No report.json found under `{workspace-path}/.github/appmod/appcat/result/` subdirectories after MCP execution
- **For .NET**: Report not generated at `{workspace-path}/.github/modernize/assessment/report.json`, or `metadata.analysisStartTime` missing from report
- Report file is corrupted or invalid JSON

For any failure, provide clear error messages and troubleshooting steps.
