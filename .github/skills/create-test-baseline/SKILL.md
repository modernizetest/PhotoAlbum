---
name: create-test-baseline
description: Create a test baseline for the project to be modernized. The baseline will be used for later verification of modernization tasks.
---

# Goal

Create a test baseline for the project to be modernized. The baseline captures externally observable behavior that must be preserved across migration — including API/UX surfaces, events, and other external interfaces. It produces a `test-cases.md` describing all test scenarios, then generates `*BaselineIT` test classes from those scenarios.

## User Input

- **migration-scope**: The scope of the migration, e.g. "migrate from AWS S3 to Azure Blob Storage", "upgrade from Java 8 to Java 11" etc.

## Principles

- Baseline tests describe behavior at **external boundaries** — HTTP endpoints, CLI commands, public API surfaces, published/consumed events, message queues, and other external interfaces.
- Baseline tests must be **technology-agnostic**: they must NOT import or reference any service-specific SDK packages (old or new). Since migration uses a replace strategy (old implementation is deleted entirely), tests must only verify externally observable behavior that is independent of the underlying service implementation.
- All test data must be **externalized** under `testdata/shared/` — no inline byte literals, hardcoded keys, or hand-built JSON strings in test source code.
- Baseline artifacts are **FROZEN** after this skill completes — never modified, renamed, moved, or deleted by subsequent phases.

## Output Layout

```
<module>/test/
├── test-cases.md              # Test case document (from test-cases-template.md)
├── <baseline>/                # FROZEN after completion
│   └── *BaselineIT            # Behavior tests at external boundaries (API, events, etc.)
└── testdata/
    └── shared/                # FROZEN — fixtures reused by baseline AND post-migration
        ├── inputs/            # e.g. raw input files
        ├── expectations/      # e.g. golden outputs at the application boundary
        └── ...                # other data as needed (configuration, seed data, etc.)
```

## Naming Conventions

| Artifact | Pattern |
|---|---|
| Test case document | `test-cases.md` |
| Baseline integration test | `*BaselineIT` |

## Workflow

### Step 1: Analyze and Document Test Cases

Analyze the application's external boundaries affected by the migration scope. Produce `test-cases.md` under `<module>/test/` using [test-cases-template.md](test-cases-template.md) as the template.

**Requirements:**
- Identify all external boundaries affected by the migration scope: API endpoints, CLI commands, public operations, published/consumed events, message queue interactions, and other external interfaces.
- For each boundary, define test cases covering **four buckets**: happy path, boundary values (empty, max, page boundary), special inputs (unicode, reserved characters, missing resource), and failure mapping (simulated backend error → application response).
- Use **2–5 representative records per entity** (table, queue, container, etc.).
- Each test case must describe **only externally observable inputs and expected outputs** — no service-specific SDK types, no backend implementation details. These are behaviors visible to the end user, API consumer, or event subscriber that must remain unchanged after migration.
### Step 2: Generate Baseline Tests

Generate `*BaselineIT` test classes from the test cases documented in `test-cases.md`.

**Requirements:**
- Each test case in `test-cases.md` maps to one or more test methods in `*BaselineIT` classes.
- Tests must exercise the application at **external boundaries** (HTTP endpoints, event interfaces, message queues, etc.) — never by importing service-specific SDK classes.
- Tests in `baseline/` must NOT import any old-technology SDK package. Since the old implementation will be entirely replaced, baseline tests must remain compilable and meaningful after deletion of old dependencies.

### Step 3: Externalize Test Data

All payload data referenced by test cases must be externalized under `testdata/shared/`.

**Requirements:**
- Organize test data under `testdata/shared/` in subdirectories by purpose (e.g. `inputs/`, `expectations/`, `configuration/`, `seed-data/`).
- Tests must not contain inline byte literals, hardcoded keys, or hand-built JSON strings — load all inputs and expected values from `testdata/shared/`.

### Step 4: Verify and Freeze

1. **Verify compile-independence**: confirm baseline tests compile when old-technology dependencies are removed from the classpath (since the old implementation will be entirely deleted during migration). If they don't, refactor the test to remove the leaking import.
2. **Run baseline tests** with the active old implementation and record results.
3. Declare baseline **FROZEN** and report frozen paths to the coordinator.

## Step 5: Output
1) Create a subfolder ${taskid} under ${modernization-work-folder}. You only need to generate a summary report "baseline-summary.md", under this subfolder to summarize the changes, and there is no need to generate any other documents.
2) Make a commit when the task is completed with the changes made in the modernization task.