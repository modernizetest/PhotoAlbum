---
name: verify-test-baseline
description: Verify frozen baseline tests after modernization and add post-migration tests that prove behavior parity.
---

# Goal

Re-run frozen baseline tests against the new implementation and add `*PostMigrationIT` tests that cover the same scenarios end-to-end. This skill runs after the migration engineer replaces the old implementation.

## User Input

- `migration-scope`: Scope of the completed migration.
- `taskid`: Identifier for this verification task.
- `modernization-work-folder`: Folder for the summary report.

## Principles

- Baseline artifacts (`baseline/`, `test-cases.md`, and `testdata/shared/`) are frozen. Never edit them.
- Post-migration tests are additions, never replacements.
- Reuse baseline inputs from `testdata/shared/`. Do not generate new fixtures for existing baseline scenarios.

## Workflow

### Step 1: Verify Baseline Integrity

Confirm `baseline/`, `test-cases.md`, and `testdata/shared/` are byte-identical to the baseline commit. Any drift is a critical issue; request revert rather than fixing forward.

### Step 2: Build Infra Decision Table

For every external dependency of the new implementation, decide whether to use a real resource or a mock.

1. Read root `infra/` files (`*.md`, `*.yml`, `*.yaml`) and extract provisioned resources, endpoints, and credentials.
2. Classify each dependency in `postmigration/infra-decision-table.md` with columns: `Dependency | Infra Match | Decision | Reason`.
3. If a dependency matches `infra/`, use the real resource. If it does not, mock at the SDK or HTTP boundary seeded from `testdata/shared/`.

Do not proceed until the table is saved.

### Step 3: Run Frozen Baseline Tests

Execute baseline test classes unchanged. Require 100% pass and the same test count as recorded baseline. Any failure is a migration regression; return to the migration engineer instead of patching tests.

### Step 4: Plan Post-Migration Tests

Use `test-cases.md`, `infra-decision-table.md`, and baseline test sources.

- Mirror each baseline scenario with one `*PostMigrationIT` method hitting the same entry point with the same inputs and expected outputs.
- Fulfill every `TODO(verify-baseline)` marker as a resource assertion against the new resource.
- If an orchestration entry point is missing end-to-end coverage, add a post-migration test case with the `postmigration` tag. Only these new scenarios may use `testdata/postmigration/`.

### Step 5: Generate Post-Migration Tests

- Use the same application entry points as baseline tests.
- Boot the full application stack when any dependency is marked `real`.
- Never stub, fake, or mock a dependency marked `real`.
- Mock only dependencies marked `mock`, and seed them from shared fixtures.
- Put test-only configuration in the project-standard test configuration mechanism.
- Use a random key per test run for created entities and clean up in teardown or `finally`.

### Step 6: Validate and Run

Check generated code against `infra-decision-table.md`, then run all `*PostMigrationIT` tests. Require 100% pass.

- Test bug: fix the test.
- Production bug: report to the coordinator; do not patch production code.
- Authentication failure: request credentials or use the project's documented local/CI credential path. Never fall back to mocking a real dependency.

### Step 7: Report

Create `${modernization-work-folder}/${taskid}/verification-summary.md` summarizing decisions, baseline integrity, test results, and gaps. Do not create extra reports.
