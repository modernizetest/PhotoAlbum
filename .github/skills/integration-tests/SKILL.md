---
name: integration-tests
description: Run multi-layer integration tests for modernized applications. Supports 4 layers - Layer 1 (Local Integration Tests with TestContainers), Layer 2 (Smoke Tests for basic health checks), Layer 3 (Azure Integration Tests against real cloud services), Layer 4 (Behavioral Comparison between old and new versions). Use when validating migrated/modernized code works correctly at any testing layer.
---

# Integration Tests

Run multi-layer integration tests to validate modernized applications work correctly.

## User Input

- **layer** (Optional): Which layer to test (1, 2, 3, or 4). Default: 1
- **original-app-path** (Optional, Layer 4 only): Path to original application for comparison
- **azure-config** (Optional, Layer 3 only): Azure environment configuration
- **modernization-work-folder** (Optional): Directory path for generating plan and summary files. Default: `.github/integration-tests`

The current working directory is used as the test root. All application modules found in the directory are included in integration tests.

## Layer Overview

| Layer | Name | Question Answered | Pass Criteria |
|-------|------|-------------------|---------------|
| 1 | Local Integration | "Do all integration tests pass correctly?" | Business logic behaves as expected |
| 2 | Smoke Tests | "Does it run?" | No crashes, basic responses work |
| 3 | Azure Integration | "Does it work in real cloud?" | Works with production-like infrastructure |
| 4 | Behavioral Comparison | "Does it match original?" | Migrated code behaves identically |

## Test Isolation Convention

When multiple layers coexist in the same project, tests must be distinguishable. **Every layer MUST use a distinct class name suffix AND tag/category** so tests from different layers never interfere with each other.

### Naming Convention

| Layer | Class Name Suffix | Example Class Name |
|-------|-------------------|--------------------|
| 1 | `L1IT` | `BlobStorageL1IT`, `OrderServiceL1IT` |
| 2 | N/A - No test classes | Layer 2 uses shell-based smoke tests, not test classes. See [layer2-smoke-tests.md](./references/layer2-smoke-tests.md) |
| 3 | `L3IT` | `AzureSqlL3IT`, `BlobStorageL3IT` |
| 4 | `L4BT` | `OrderApiL4BT`, `UserServiceL4BT` |

### Tagging / Category Convention

Test classes for Layers 1, 3, 4 **MUST** be annotated with a layer-specific tag so the runner script can filter precisely. **Layer 2 does not use test classes** (see [layer2-smoke-tests.md](./references/layer2-smoke-tests.md)).

| Language / Framework | Layer 1 | Layer 2 | Layer 3 | Layer 4 |
|---------------------|---------|---------|---------|--------|
| **Java (JUnit 5)** | `@Tag("Layer1")` | N/A - No test classes | `@Tag("Layer3")` | `@Tag("Layer4")` |
| **Java (JUnit 4)** | `@Category(Layer1.class)` | N/A - No test classes | `@Category(Layer3.class)` | `@Category(Layer4.class)` |
| **.NET (xUnit)** | `[Trait("Category", "Layer1")]` | N/A - No test classes | `[Trait("Category", "Layer3")]` | `[Trait("Category", "Layer4")]` |
| **.NET (NUnit)** | `[Category("Layer1")]` | N/A - No test classes | `[Category("Layer3")]` | `[Category("Layer4")]` |
| **Python (pytest)** | `@pytest.mark.layer1` | `@pytest.mark.layer2` | `@pytest.mark.layer3` | `@pytest.mark.layer4` |
| **Node.js (Jest)** | Test file in `__tests__/layer1/` | Test file in `__tests__/layer2/` | Test file in `__tests__/layer3/` | Test file in `__tests__/layer4/` |

> **Rule**: Never rely solely on class name patterns for filtering. Always use tags/categories as the primary filter mechanism. The naming suffix is a secondary convention for human readability.

## Integration Tests Writing Principles

Analyze the project if integration tests have covered all components, if not **DO ADD** new integration tests by the following principles:

**CRITICAL - Read Reference Docs First:**
- **Before starting ANY layer**, read the corresponding reference file in [references/](./references/) directory

- **Purpose:** Ensures combined components function as a whole, focusing on "in-between" logic rather than individual module functionality.
- **Scope:** Validates interactions between modules, databases, messaging services, and file systems.
- **DO create** an integration test plan file before starting implementation to outline the testing strategy and approach.
- **DO use** top-down approach to add integration tests. For example, if an application has controller layer, service layer, and database layer. The integration tests should set up real connections to the database, and then test against the controller layer, to validate all functionalities.
- **DO write** comprehensive integration covering **ALL** components.
- **DO use** the layer-specific class name suffix from the Test Isolation Convention (e.g., `L1IT` for Layer 1, `L3IT` for Layer 3, `L4BT` for Layer 4). **Layer 2 does not use test classes.**
- **DO annotate** every test class with the layer-specific tag/category from the Test Isolation Convention.
- **DO execute** integration tests to check the results.
- **DO analyze failures** using the Test vs Source Code Decision Framework to determine what to fix.
- **DO fix issues** in the appropriate place (test or source code) based on the analysis.
- **DO create** a summary file documenting all changes made, tests added, and results achieved.
- **DO commit** changes separately for each layer with meaningful commit messages. Do not combine changes from different layers into a single commit.
  - **Layer 1, 3, 4**: Single commit per layer (e.g., `Add Layer 1 local integration tests`)
  - **Layer 2**: Multi-commit sequence as defined in [layer2-smoke-tests.md](./references/layer2-smoke-tests.md) (artifacts → auth → restore). **CRITICAL: Layer 2 does NOT create test classes - it uses shell-based smoke tests with docker-compose.**
- **DO NOT** change the technical stack, architure selection, libary using in the source code. The goal is to validate the existing application code, not change it to pass tests.
- **DO NOT** add extra modules for integration tests, write integration tests in the existing modules.
- **DO generate** standardized runner scripts after all tests pass (see Standardized Runner Scripts section at the end of this document).

## Workflow

Based on the requested layer, follow the corresponding reference guide:

### Layer 1: Local Integration Tests
**Read [references/layer1-local-integration.md](references/layer1-local-integration.md) first**, then create TestContainers-based integration test classes.

### Layer 2: Smoke Tests
**CRITICAL: Read [references/layer2-smoke-tests.md](references/layer2-smoke-tests.md) first.** Layer 2 uses shell-based smoke tests with docker-compose, NOT JUnit/xUnit test classes. Follow the exact multi-commit workflow (artifacts → auth → restore) documented in the reference file.

### Layer 3: Azure Integration Tests
**Read [references/layer3-azure-integration.md](references/layer3-azure-integration.md) first**, then create integration test classes that connect to real Azure services.

### Layer 4: Behavioral Comparison
**Read [references/layer4-behavioral-comparison.md](references/layer4-behavioral-comparison.md) first**, then create comparison tests that validate behavior matches between old and new implementations.

## Quick Decision Tree

```
User requests testing
    │
    ├─ Layer 1 → Use TestContainers, test all azure dependencies with multiple scenarios
    │
    ├─ Layer 2 → Auto-detect app type, start app, hit each endpoint once
    │
    ├─ Layer 3 → Deploy to Azure staging, test against real services
    │
    └─ Layer 4 → Run both versions side-by-side, compare outputs
```

## Handling Test Failures

When integration tests fail during execution, use this framework to determine whether to fix the test code or the source code:

### Fix Source Code When:

**Business Logic Violations**
- Error indicates source code violates business rules (e.g., negative inventory allowed)
- Multiple similar tests fail with same pattern

**Specification Compliance**  
- Source code doesn't implement required functionality properly
- Error messages show missing or incorrect behavior

**Cross-Component Integration Issues**
- Test setup is correct and realistic
- Source code fails to properly communicate between modules
- Data transformation or mapping errors between layers

**Resource Management Problems**
- Test uses proper connection/resource patterns
- Source code has leaks, deadlocks, or improper disposal
- Timing issues in source code (not test race conditions)

### Fix Test Code When:

**Test Implementation Issues**
- Unrealistic test data or scenarios
- Incorrect test setup (wrong mocks, invalid configurations) 
- Testing implementation details rather than behavior
- Race conditions or timing issues in test logic

**Environmental Problems**
- Wrong container configurations or versions
- Test dependencies not properly isolated
- Hard-coded values that should be configurable
- Test cleanup issues affecting subsequent tests

**Test Design Flaws**
- Tests making too many assumptions about internal state
- Over-mocking leading to false confidence
- Testing edge cases that don't reflect real usage
- Assertions on wrong data or wrong timing

### Analysis Steps:

1. **Review Test Quality**: Does the test follow established patterns and realistic scenarios?
2. **Check Business Logic**: Does the failure indicate business rule violations in source code?
3. **Verify Setup**: Are test dependencies and configurations realistic and correct?
4. **Assess Error Type**: Is it a logic error, integration error, or test infrastructure issue?
5. **Consider Impact**: Would fixing source code improve real application behavior?

### Decision Process:

```
Test Failure
    │
    ├─ Does test model realistic business scenario? 
    │   ├─ No → Fix Test Code
    │   └─ Yes ↓
    │
    ├─ Does source code violate business rules?
    │   ├─ Yes → Fix Source Code  
    │   └─ No ↓
    │
    ├─ Is test setup and environment correct?
    │   ├─ No → Fix Test Code
    │   └─ Yes ↓
    │
    └─ Does error show integration/logic problem?
        ├─ Yes → Fix Source Code
        └─ No → Fix Test Code
```

## Standardized Runner Scripts

After all tests are written, executed, and fixed to pass, generate a fixed runner script so users can re-run integration tests with a single command regardless of project type.

| Layer | Script Path | Command (Unix) | Command (Windows) |
|-------|-------------|----------------|--------------------||
| 1 | `{modernization-work-folder}/run-layer1-tests.sh` / `.ps1` | `bash .github/integration-tests/run-layer1-tests.sh` | `powershell .github/integration-tests/run-layer1-tests.ps1` |
| 2 | `{modernization-work-folder}/run-layer2-tests.sh` / `.ps1` | `bash .github/integration-tests/run-layer2-tests.sh` | `powershell .github/integration-tests/run-layer2-tests.ps1` |
| 3 | `{modernization-work-folder}/run-layer3-tests.sh` / `.ps1` | `bash .github/integration-tests/run-layer3-tests.sh` | `powershell .github/integration-tests/run-layer3-tests.ps1` |
| 4 | `{modernization-work-folder}/run-layer4-tests.sh` / `.ps1` | `bash .github/integration-tests/run-layer4-tests.sh` | `powershell .github/integration-tests/run-layer4-tests.ps1` |

### Runner Script Requirements

1. **Always generate both `.sh` and `.ps1` variants** for cross-platform support.
2. The script **MUST** encapsulate all project-specific details (build tool, test runner, filters, working directory, container setup/teardown).
3. The script **MUST** be self-contained — users should not need to know the build system or test framework to run it.
4. The script **MUST** exit with code 0 on success and non-zero on failure.
5. The script **MUST** print a human-readable result summary at the end:
   - **On success**: `✅ Layer 1 integration tests PASSED`
   - **On failure**: `❌ Layer 1 integration tests FAILED`
   - The test runner's own console output already includes detailed counts, failure logs, assertion messages, and stack traces — the script only needs a clear pass/fail signal at the end.
6. For Layer 1, the script **MUST** verify Docker is running before starting tests.
7. For Layer 2, the script **MUST** handle starting and stopping the application.
8. For Layer 3, the script **SHOULD** accept Azure configuration via environment variables.
9. For Layer 4, the script **MUST** handle starting both old and new application versions.

### Runner Script Filtering

**Layers 1, 3, 4** use tag/category filters to execute test classes. **Layer 2 uses shell commands** (see [layer2-runner-script-templates.md](./references/layer2-runner-script-templates.md)).

| Layer | Maven | Gradle | dotnet test | pytest |
|-------|-------|--------|------------|--------|
| 1 | `mvn verify -Dgroups=Layer1` | `./gradlew test -Dgroups=Layer1` | `dotnet test --filter Category=Layer1` | `pytest -m layer1` |
| 2 | Shell-based smoke tests (no Maven/Gradle commands) | Shell-based smoke tests | Shell-based smoke tests | Shell-based smoke tests |
| 3 | `mvn verify -Dgroups=Layer3` | `./gradlew test -Dgroups=Layer3` | `dotnet test --filter Category=Layer3` | `pytest -m layer3` |
| 4 | `mvn verify -Dgroups=Layer4` | `./gradlew test -Dgroups=Layer4` | `dotnet test --filter Category=Layer4` | `pytest -m layer4` |

### Example Runner Script Structure (Layer 1)

```bash
#!/bin/bash
set -euo pipefail

# --- Auto-generated integration test runner ---
# Project type: <detected>
# Generated on: <date>

# Verify prerequisites
if ! docker info > /dev/null 2>&1; then
  echo "ERROR: Docker is not running. Please start Docker and try again."
  exit 1
fi

# Run integration tests (project-specific command is embedded here)
# IMPORTANT: Always filter by the layer-specific tag to avoid running other layers' tests
# Test output (including any failure logs) goes directly to the console.
cd "$(dirname "$0")/../.."

<project-specific-test-command>
# e.g., mvn verify -Dgroups=Layer1, dotnet test --filter Category=Layer1, ./gradlew test -Dgroups=Layer1

TEST_EXIT=$?

# --- Print summary ---
echo ""
echo "========================================"
if [ $TEST_EXIT -eq 0 ]; then
  echo "✅ Layer 1 integration tests PASSED"
else
  echo "❌ Layer 1 integration tests FAILED"
fi
echo "========================================"
exit $TEST_EXIT
```

> **Note to implementers:** Replace `<project-specific-test-command>` with the real test command for the detected project type (Maven/Gradle/dotnet/pytest). The test runner's own console output already includes detailed results — the script just appends a clear pass/fail signal at the end.

## Completion Criteria

1. **Integration Test Plan**: Create and output a plan file at `{modernization-work-folder}/integration-test-plan.md` that includes:
   - Analysis of existing test coverage gaps
   - Identified components requiring integration testing
   - Testing strategy and approach for each component
   - Dependencies and test setup requirements
   - Expected test scenarios and validation criteria

2. All tests for the requested layer **run and pass**, show the running results to the user

3. Test results are reported with clear pass/fail status

4. Any failures are properly analyzed and resolved (see Handling Test Failures section)

5. Test artifacts (logs, screenshots, comparison reports) are saved

6. **Version Control**: Commit changes separately for each layer with meaningful commit messages. Do not combine changes from different layers into a single commit.
   - **Layer 1, 3, 4**: Single commit per layer (e.g., `Add Layer 1 local integration tests`)
   - **Layer 2**: Multi-commit sequence as defined in [layer2-smoke-tests.md](./references/layer2-smoke-tests.md) (minimum 3 commits: artifacts → auth → restore)

7. **Integration Test Summary**: Create and output a summary file at `{modernization-work-folder}/integration-test-summary.md` that documents:
   - All integration tests added (with file paths and descriptions)
   - Test coverage improvements achieved
   - Issues identified and resolved (both in source code and test code)
   - Final test execution results
   - Paths to generated runner scripts and the fixed commands to execute them
   - Source code changes made during testing and their purpose

8. **Runner Scripts**: Generate standardized runner scripts at `{modernization-work-folder}/run-layer{N}-tests.sh` and `.ps1` (see Standardized Runner Scripts section). The scripts must embed all project-specific commands so users always run the same fixed command.

Note: If `modernization-work-folder` is not provided, use `.github/integration-tests` as the default directory.
