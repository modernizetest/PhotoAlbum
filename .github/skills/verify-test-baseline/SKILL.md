---
name: verify-test-baseline
description: Verify that the frozen baseline tests still pass after migration, and add post-migration tests.
---

# Goal

Verify that the frozen baseline tests still pass after migration, and add post-migration tests. This skill runs in Phase 3 of the migration pipeline, after the migration-engineer has replaced the old implementation.

## User Input

- **migration-scope**: The scope of the migration that was completed.

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

### Step 2: Determine Test Infrastructure

Identify the external dependencies required by the new implementation (Azure resources, backend services, etc.), then decide per-dependency how to provide them.

- Scan the project root `infra/` directory for configuration files (`env-config.md`, `*.yml`) that define Azure resource settings and credentials.
- For each dependency:
  - If a matching Azure resource is found in `infra/` → use the **real resource** with the provided credentials.
  - If no matching Azure resource is found → **mock it** at the SDK / HTTP boundary. Seed mock data from `testdata/shared/`.
- External backend services (non-Azure third-party APIs, partner services, etc.) are always **mocked**. Mock data must come from `testdata/shared/` or `testdata/postmigration/`.

### Step 3: Run Frozen Baseline Tests

Execute the same baseline test classes, unchanged. Required outcome: **100% pass** with the same test count as the recorded baseline. Any failure is a migration regression — return it to the migration-engineer; do not patch tests.

### Step 4: Add Post-Migration Tests

Derive post-migration tests from the baseline test cases documented in `test-cases.md`. Each baseline scenario maps to a corresponding `*PostMigrationIT` test that verifies the **same API/UX-level behavior** against the new implementation.

**Critical rule:** Post-migration tests must test at the **same boundary as baseline tests** — the application's HTTP endpoints, public methods, or CLI commands. Do NOT write pure resource-interface tests that directly call Azure SDK APIs (e.g. `BlobClient.upload()`, `ServiceBusSenderClient.sendMessage()`). Such tests verify the SDK works, not that the migrated application works. The goal is to confirm that the same user-facing operations defined in `test-cases.md` produce the same results after migration.

**How to mirror baseline scenarios:**
- For each test case in `test-cases.md`, create a `*PostMigrationIT` test method that exercises the same entry point (e.g. `POST /s3/upload`, `FileProcessor.downloadOriginal(key, path)`) with the same inputs and expected outputs.
- The difference from baseline: post-migration tests run against the real new backend (or mocked new backend), whereas baseline tests mock the service interface.

#### Real Azure Resources

For dependencies with matching `infra/` configuration:
- Load environment variables and credentials from the infra configuration files.
- Prepare test data according to the infra setup — provision required resources (containers, queues, tables, etc.) in isolated namespaces per test run.
- Run tests against the real Azure service.
- Capture request/response logs for diagnostics.
- Verify account permissions before running tests — any permission failure is a critical blocker.

#### Azure Authentication for Local and CI Environments

The migrated code may configure Managed Identity (MI) as the primary credential. In environments where MI is not available (developer workstations, non-Azure CI runners), authentication must fall back to the developer's local Azure credentials (e.g. `az login` session) or CI service-principal environment variables.

- Provide a test-only configuration that disables MI and lets the Azure SDK fall back to local credentials. Do **not** modify the production configuration.
- Before running any real-resource test, perform a pre-flight authentication check. If it fails, abort with a clear message indicating which credential was attempted and how to fix it.

#### Mocked Dependencies

For Azure resources without `infra/` configuration, and for all external backend services:
- Mock at the SDK / HTTP boundary — never at the application layer.
- Seed mock data from `testdata/shared/` or `testdata/postmigration/`. Never duplicate or hardcode content.
- Assert on outbound requests (verb, URL, key headers), not just return values.
- Document which dependencies are mocked as technical debt.

Post-migration tests reuse `testdata/shared/` fixtures, are always additions (never replacements), and extend `test-cases.md` with their own test case entries.

### Step 5: Run Post-Migration Tests

Build and execute all `*PostMigrationIT` test classes. Required outcome: **100% pass**. If a test fails:
- If the failure is caused by the test itself (wrong assertion, missing test data) — fix the test.
- If the failure is caused by the migrated production code — do **not** fix it. Report the failure back to the coordinator so the migration-engineer can address it.
- If the failure is an **authentication error** (401/403, credential unavailable, IMDS timeout) — resolve the credential issue first before investigating test logic. Ensure the test-only configuration that disables MI is active when running outside Azure.

### Step 6: Fix Coverage Gaps Backwards

If verification reveals a missing scenario, coordinate a baseline rework (unfreeze → add → re-record → re-freeze). Never silently patch only `postmigration/`.

### Step 7: Report Results

Create a subfolder ${taskid} under ${modernization-work-folder}. You only need to generate a summary report "verification-summary.md", under this subfolder to summarize the changes, and there is no need to generate any other documents.

**Important:** If a test failure is caused by the migrated code (not by the test case itself), do **not** fix it yourself. Report the failure back to the coordinator so the migration-engineer can address it. The integration-tester only fixes test-related issues; production code regressions are the migration-engineer's responsibility.

