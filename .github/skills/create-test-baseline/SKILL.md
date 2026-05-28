---
name: create-test-baseline
description: Create frozen behavior baseline tests and shared test data before modernization so later verification can prove behavior parity.
---

# Goal

Create a test baseline for the project to be modernized. The baseline captures externally observable behavior that must be preserved across migration, including API surfaces, UX flows, CLI commands, events, message queues, and other public interfaces. Produce `test-cases.md`, shared test data, and `*BaselineIT` test classes.

## User Input

- `migration-scope`: Scope of the migration, such as "migrate from AWS S3 to Azure Blob Storage" or "upgrade from Java 8 to Java 17".
- `taskid`: Identifier for this baseline task.
- `modernization-work-folder`: Folder for the summary report.

## Principles

- Baseline tests verify behavior at external boundaries only. Do not test private helpers as the primary baseline.
- Baseline tests are technology agnostic. They must not import old or new service-specific SDK packages.
- All payload data lives under `testdata/shared/`; no inline byte literals, hardcoded keys, or hand-built JSON strings in test source.
- Baseline artifacts are frozen after this skill completes. Subsequent phases must not modify, rename, move, or delete them.

## Output Layout

```text
<module>/test/
├── test-cases.md
├── baseline/
│   └── *BaselineIT
└── testdata/
    └── shared/
        ├── inputs/
        ├── expectations/
        └── ...
```

## Workflow

### Step 1: Analyze and Document Test Cases

Analyze external boundaries affected by `migration-scope`. Create `<module>/test/test-cases.md` using [test-cases-template.md](test-cases-template.md).

Requirements:
- Identify affected boundaries: HTTP endpoints, CLI commands, public operations, published or consumed events, message queues, and similar interfaces.
- Identify orchestration entry points such as controllers, listeners, scheduled tasks, CLI runners, and event handlers. Each must have at least one end-to-end test case that triggers it with realistic input and verifies final observable outcome.
- Cover happy path, boundary values, special inputs, and failure mapping for each affected boundary.
- Use 2-5 representative records per entity.
- Describe only externally observable inputs and expected outputs.

### Step 2: Generate Baseline Tests

Generate `*BaselineIT` classes from `test-cases.md`.

Requirements:
- Each test case maps to one or more test methods.
- Tests exercise application boundaries, never old-technology SDK clients.
- Do not implement resource assertions in baseline tests. For each `Resource Verification` bullet, add a `TODO(verify-baseline)` comment at the natural assertion point.
- Each TODO references the test case ID and exact verification bullet text.

Example:

```java
// TODO(verify-baseline) TC-001: object `uploads/sample.jpg` exists with content matching testdata/shared/inputs/sample.jpg.
```

### Step 3: Externalize Test Data

Place all reusable inputs and expected outputs under `testdata/shared/`, organized by purpose.

### Step 4: Verify and Freeze

1. Confirm baseline tests compile without old-technology SDK imports.
2. Run baseline tests with the active old implementation.
3. Record results and report frozen paths to the coordinator.

### Step 5: Report

Create `${modernization-work-folder}/${taskid}/baseline-summary.md` summarizing test cases, generated baseline tests, shared data, run results, and frozen paths. Do not create extra reports.

Commit the baseline changes when the task is complete.
