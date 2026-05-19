---
name: verify-test-baseline
description: Verify that the frozen baseline tests still pass after migration, and add post-migration tests.
---

# Goal

Verify that the frozen baseline tests still pass after migration, and add post-migration tests. This skill runs in Phase 3 of the migration pipeline, after the migration-engineer has replaced the old implementation.

## User Input

- **migration-scope**: The scope of the migration that was completed.
- **taskid**: The task identifier for this verification run.
- **modernization-work-folder**: The folder to save the modernization plan and related documents.

## Principles

- **Do not rewrite baseline tests.** Reuse them as-is. The `postmigration/` package exists only for verifying the new implementation against baseline scenarios.
- **Baseline integrity is non-negotiable.** Any modification to frozen artifacts is a critical issue — request a revert, do not "fix forward".
- Post-migration tests are always **additions**, never replacements.

## Naming Conventions

| Artifact | Pattern |
|---|---|
| Post-migration integration test | `*PostMigrationIT` |

## Workflow

### Step 1: Verify Baseline Integrity

Confirm all files under `baseline/`, `test-cases.md`, and `testdata/shared/` are byte-identical to the baseline commit. Any modification is a critical issue — request a revert, do not "fix forward".

### Step 2: Determine Test Infrastructure (mandatory gate)

**This step is a mandatory gate — you MUST complete it and record your decisions before writing any test code in Step 4.**

Identify the external dependencies required by the new implementation (Azure resources, backend services, etc.), then decide per-dependency how to provide them.

1. **Scan `infra/` first.** Read the project root `infra/` directory. Parse all `*.md`, `*.yml`, and `*.yaml` files to extract provisioned resource names, endpoints, and credentials.
2. **Classify each dependency.** For every external dependency used by the migrated code, check whether a matching resource exists in `infra/`. Produce a decision table with columns: Dependency | Infra Match | Decision (real / mock) | Reason.
3. **Apply the rules:**
   - If a matching resource is found in `infra/` → you **MUST** use the **real resource**. Mocking a dependency that has a provisioned resource is a bug.
   - If no matching resource is found in `infra/` → **mock it** at the SDK / HTTP boundary. Seed mock data from `testdata/shared/` or `testdata/postmigration/`.
4. **Save the decision table** to `postmigration/infra-decision-table.md` in the test directory. This file is the source of truth for Steps 4 and 5 — all subsequent test code must conform to it.
5. **Do NOT proceed to Step 4 until the decision table is saved.** If you skip this step or default to mocking without checking `infra/`, the resulting tests are invalid.

**Common mistake:** The decision table says "real" but the generated test code stubs or mocks that dependency (e.g., mock objects, test doubles, in-memory fakes, or framework-specific mock annotations). If your decision table marks a dependency as "real", the generated test code MUST NOT mock that dependency at any layer. Go back and verify your generated code matches the decision table before proceeding.

### Step 3: Run Frozen Baseline Tests

Execute the same baseline test classes, unchanged. Required outcome: **100% pass** with the same test count as the recorded baseline. Any failure is a migration regression — return it to the migration-engineer; do not patch tests.

### Step 4: Add Post-Migration Tests

**Prerequisite:** The decision table from Step 2 (`postmigration/infra-decision-table.md`) must exist.

Derive post-migration tests from the baseline test cases documented in `test-cases.md`. Each baseline scenario maps to a corresponding `*PostMigrationIT` test that verifies the **same API/UX-level behavior** against the new implementation.

**Critical rule — "same boundary" means same entry points, NOT same test infrastructure:**

- Post-migration tests exercise the **same entry points** as baseline tests (HTTP endpoints, public methods, CLI commands).
- Unlike baseline tests that mock service dependencies, post-migration tests boot the **full application stack** with real service implementations connected to real resources (for dependencies marked "real" in Step 2).
- Do NOT write pure resource-interface tests that directly call cloud SDK APIs. The goal is to confirm that user-facing operations from `test-cases.md` produce the same results after migration.

**How to mirror baseline scenarios:**
- For each test case in `test-cases.md`, create a `*PostMigrationIT` test method that exercises the same entry point with the same inputs and expected outputs.
- Post-migration tests run with the full application stack connected to real resources (as determined by Step 2), whereas baseline tests mock the service interface.

Post-migration tests reuse `testdata/shared/` fixtures, are always additions (never replacements), and extend `test-cases.md` with their own test case entries.

#### Real Resources (REQUIRED when infra/ match exists — this is the DEFAULT)

When `infra/` contains configuration files (`*.md`, `*.yml`, `*.yaml`) that list provisioned resources, this is the primary test mode. Most post-migration tests should follow this path.

For dependencies marked "real" in the decision table:

1. **Create a test-only configuration** that points to the real endpoints, account names, queue names, and connection strings extracted from the `infra/` configuration files. Use the project's standard configuration mechanism (e.g., Spring profile, `.env` file, `appsettings.IntegrationTest.json`, environment variables). This configuration MUST be activated when the post-migration tests run.
2. **Boot the full application stack** — not a partial/sliced test context. Send HTTP requests (or call public APIs) through the full stack, not through mocked layers.
3. **Prepare test data** in isolated namespaces per test run. Clean up test data in teardown hooks.
4. **Add a pre-flight authentication check** in test setup that verifies credentials are available. If authentication fails, skip or abort the test with a clear message (e.g., "Credentials required: run `az login` first") — do NOT fall back to mocking.
5. **Capture request/response logs** for diagnostics.

**Authentication note:** The migrated code may configure Managed Identity (MI) as the primary credential. In environments where MI is not available (developer workstations, non-Azure CI runners), provide a test-only configuration that disables MI and falls back to local credentials (e.g. `az login` session) or CI service-principal environment variables. Do **not** modify the production configuration.

#### Mocked Dependencies (ONLY when no infra/ match exists)

**You may only mock a dependency if it was marked "mock" in the Step 2 decision table** — meaning no matching resource was found in `infra/`. If a resource IS provisioned in `infra/` but you mock it anyway, the tests are invalid and must be rewritten.

For dependencies without a matching `infra/` resource:
- Mock at the SDK / HTTP boundary — never at the application layer.
- Seed mock data from `testdata/shared/` or `testdata/postmigration/`. Never duplicate or hardcode content.
- Assert on outbound requests (verb, URL, key headers), not just return values.
- Document which dependencies are mocked as technical debt.

### Step 5: Validate and Run Post-Migration Tests

**Before running, validate the generated test code against the decision table (`postmigration/infra-decision-table.md`):**
- For every dependency marked "real": confirm the test code does NOT stub, fake, or mock that dependency.
- Confirm the test boots the full application stack (not a partial/sliced context) when any dependency is "real".
- Confirm a test-only configuration file exists with real endpoints from the `infra/` configuration files.
- If any of these checks fail, go back to Step 4 and regenerate the tests.

Build and execute all `*PostMigrationIT` test classes. Required outcome: **100% pass**. If a test fails:
- If the failure is caused by the test itself (wrong assertion, missing test data) — fix the test.
- If the failure is caused by the migrated production code — do **not** fix it. Report the failure back to the coordinator so the migration-engineer can address it.
- If the failure is an **authentication error** (401/403, credential unavailable, IMDS timeout) — resolve the credential issue first. Ensure the test-only configuration that disables MI is active when running outside Azure.

### Step 6: Fix Coverage Gaps Backwards

If verification reveals a missing scenario, coordinate a baseline rework (unfreeze → add → re-record → re-freeze). Never silently patch only `postmigration/`.

### Step 7: Report Results

Create a subfolder ${taskid} under ${modernization-work-folder}. Generate a summary report "verification-summary.md" under this subfolder to summarize the changes. No other documents are needed.

