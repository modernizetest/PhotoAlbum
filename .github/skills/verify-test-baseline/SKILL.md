---
name: verify-test-baseline
description: Generate and run post-migration tests from the frozen baseline specification.
---

# Goal

Generate executable `*PostMigrationIT` tests from the frozen baseline specification and run them against the migrated application. 

The baseline phase produces **no test code** — it produces a precise specification, including the test-cases, infra-decision-table, and testdata. This skill is the sole place where integration test code is generated. 

## User Input

- **taskid** — Identifier for this verification run.
- **modernization-work-folder** — Folder under which the verification summary and decision table are written.

## Terminology

**Event-sourced subscriber** — any entry point invoked by an external event source rather than by a synchronous caller: message-queue listeners, event-bus / event-hub / event-grid handlers, storage-event triggers (e.g. blob-created or object-deleted handlers), DB change-feed / CDC handlers, inbound-email handlers, file-system watchers. Throughout this document, "event-sourced subscriber" refers to this entire family; the only legitimate trigger for such an entry point is a real event produced on the declared source via its SDK or wire protocol.

## Principles

- The spec is the source of truth. If a test case cannot be generated from its fields as-written, the defect is in the spec — coordinate a re-freeze (Step 7), do not invent details in the generated test.
- Post-migration tests are **additions**, never replacements.
- **Strict 1:1 mapping.** Exactly one test method per `TC-*` in `test-cases.md`. No extra tests (no "connectivity smoke", no "SDK sanity", no backing-store CRUD that has no entry point in the inventory). No missing tests. Test count == TC count.
- **Trigger fidelity over convenience.** The trigger is the contract. Any test whose trigger is not the declared `Entry Point` — for example, one that invokes a cloud SDK, a repository, an internal service, or a private helper instead — is invalid and must be regenerated, even if it passes.
- **Assertion completeness.** A test must assert every bullet under `Expected Response`, `Resource Verification`, and `Negative Verification`. Existence-only or no-throw-only checks (asserting only that a resource exists, that a call did not throw, or that a value is non-null) are insufficient on their own.
- **No production-bug workarounds.** If a test fails because the migrated code is wrong, hand the work back to the migration engineer per Step 6. Do not patch the test to bypass the broken entry point, and do not loosen / rewrite assertions to accept the buggy response. "Documenting the current behavior" by changing expected response codes, status, or payload to match what the broken code returns is a workaround — not a fix.
- **No hardcoded environment topology.** Generated tests must not hardcode environment-specific resource identifiers (account names, namespaces, queue/topic names, hostnames, connection strings, tenant/subscription IDs, database hosts, secrets). Resolve these from test-only configuration wired to `infra/` outputs and environment variables.

## Layout

Inputs (frozen, produced by the setupBaseline task) live under the project's **test source root** — the directory the build tool already uses for tests (e.g. `src/test/` for Maven/Gradle Java, `tests/` for Python / Node / Go, `<module>/test/` for multi-module repos):

```
<test-source-root>/
└── test-cases/                 # FROZEN folder — created in Phase 1
    ├── test-cases.md           # FROZEN — the behavior spec
    ├── infra-decision-table.md # FROZEN — mock/real decision per external dependency
    └── testdata/               # FROZEN — fixtures referenced by test-cases.md
```

Outputs of this skill:

- `${modernization-work-folder}/${taskid}/post-migration-plan.md` — the TC→test planning table written in Step 4 (created/overwritten on each run).
- `*PostMigrationIT` source files — follow the project's existing test layout conventions.
- `${modernization-work-folder}/${taskid}/verification-summary.md` — final report (Step 8).

Reused inputs from the baseline phase:

- `<test-source-root>/test-cases/infra-decision-table.md` — mock/real decision per external dependency, produced by `create-test-baseline`. This skill consumes it as-is.

## Workflow

### Step 1 — Verify Baseline Integrity

Locate `<test-source-root>/test-cases/` and confirm `test-cases.md`, `infra-decision-table.md`, and `testdata/` are byte-identical to the baseline commit. Any drift → request revert. If `test-cases.md` is missing entirely, abort: the setupBaseline task was supposed to run first — surface this as a plan-ordering bug, do not proceed.

### Step 2 — Load Infra Decision Table from Baseline (mandatory gate)

The mock/real decision for every external dependency is made in the baseline phase, not here. Verification reuses it as-is.

1. Load `<test-source-root>/test-cases/infra-decision-table.md` produced by `create-test-baseline`. If it is missing, abort and surface this as a plan-ordering bug — do not regenerate it here.
2. Sanity-check the table against the current repo-root `infra/` directory: every row marked **real** must still have a matching provisioned resource in `infra/`. If `infra/` has drifted (resource removed, endpoint changed, credential type changed) such that a "real" row is no longer valid, surface the drift → Step 7 (re-freeze cycle); do not silently downgrade to mock here.
3. Treat the loaded table as the source of truth for all subsequent steps.

Do not proceed until the table is loaded and the sanity check passes.

### Step 3 — Validate Spec Readiness

Before generating code, audit `test-cases.md` against the **Required Field Checklist** defined in Step 5 of the `create-test-baseline` skill.

- Every test case has all required fields populated (ID, Category, Entry Point Type, Entry Point, Trigger, Preconditions, Expected Response, Resource Verification, Negative Verification where required, Data References).
- No banned phrasings remain.
- Every `testdata/...` path referenced exists.
- The Entry-Point Inventory matches what is exercised by the cases.

Any defect → Step 7 (re-freeze cycle). Do not paper over spec defects in generated code.

### Step 4 — Plan Post-Migration Tests

Inputs: `test-cases.md`, the infra decision table loaded in Step 2.

1. **Mirror the spec, exactly once.** For each `TC-*` in `test-cases.md`, plan exactly one test method. No extra tests. No collapsing two TCs into one. No splitting one TC across multiple test methods (sub-steps go inside the single method body).
2. **Map each entry point to its concrete trigger mechanism on the new stack.** The `Trigger` field is technology-agnostic; resolve it to the actual mechanism that exists in the migrated codebase. Always trigger via the same outside-in path the entry point is invoked from in production. Pick the most realistic public driver the test framework offers:
   - HTTP / network handlers → framework's HTTP test client.
   - CLI commands → CLI runner / process invocation.
   - Library APIs → call the published API directly.
   - **Event-sourced subscribers** (see Terminology) → produce a real event on the declared source via its SDK or wire protocol (publish a message to the queue/topic, upload/delete the blob, insert/update the watched DB row, send an SMTP message, write the watched file). The application is the subscriber; the only realistic trigger is a real event on the source it subscribes to.
   - Scheduled jobs / cron → framework's "run now" hook (e.g. scheduler `triggerJob`, manual invocation of the scheduled-task dispatcher). This is framework-driven, not SDK-driven.

   When in doubt, prefer the mechanism a real external caller or event source would use over a test-only shortcut.
3. **Reject in-spec but infeasible-as-real cases early.** If a test case requires failure injection on a dependency marked **real** (e.g. "storage unavailable", "backend throws IOException", "corrupt object content") and there is no way to trigger that condition from the declared entry point with a real backend, do not silently skip and do not silently switch to a mock — surface the conflict → Step 7 (re-freeze) so the infra-decision-table is amended (e.g. that dependency becomes `mock` for the relevant failure cases) or the case is reformulated.
4. **Close entry-point coverage gaps.** Scan production code for orchestration entry points. For each one not present in the Entry-Point Inventory of `test-cases.md`, surface the gap → Step 7 (re-freeze) so the spec is updated first. Do not silently add post-migration-only cases.
5. **Produce a planning table (mandatory artifact).** Before writing any code, emit the TC→test mapping table and **save it to `${modernization-work-folder}/${taskid}/post-migration-plan.md`** (create or overwrite). The file MUST contain one row per `TC-*`; rows whose `Trigger Mechanism` is anything other than the declared entry point's outside-in driver, or whose `Fixtures Loaded` is empty while `Data References` is non-empty, must be revised before proceeding. The same table is later linked from the Step 8 verification summary.

   | TC ID | Test Location (class/file → method) | Declared Entry Point | Trigger Mechanism (concrete) | Fixtures Loaded (from `Data References`) | Real Deps Touched | Config Source | Cleanup Path |
   |---|---|---|---|---|---|---|---|
   | TC-XXX-001 | _e.g._ `FooPostMigrationIT.uploadHappyPath` | _e.g._ `POST /foo/upload` | _e.g._ HTTP test client multipart POST to `/foo/upload` | `testdata/inputs/sample.jpg`, `testdata/expectations/upload-success.json` | _e.g._ Blob, Queue, DB | _e.g._ `application-integrationtest.yml` + env vars mapped from `infra/` outputs | _e.g._ `POST /foo/delete/{key}` |

   The row above is illustrative; use the test-class / method / driver naming conventions of the migrated project's language and framework.
   `Config Source` is mandatory and must name where each real dependency endpoint/identifier comes from. Any row that implies inline literals in test code must be revised before generation.

#### Forbidden trigger patterns (auto-reject in code review)

- HTTP entry point in spec, but the test calls a cloud / storage / messaging SDK directly as the trigger _(e.g. invoking a blob client's upload method, a queue sender client's send method, an object-store put-object call)_.
- HTTP entry point in spec, but the test calls an internal application service, handler, repository, or sender component directly as the trigger.
- Event-sourced subscriber entry point in spec (see Terminology), but the test calls the subscriber's internal handler method directly _(e.g. invoking the processing service method that the listener delegates to, or feeding a hand-built mocked message/event context into the handler, including via reflection on a private method)_ instead of producing a real event on the declared source.
- Scheduled job entry point in spec, but the test calls the job's run method directly instead of using the framework's scheduled-task invocation hook.
- Backing store (DB, cache, blob container, search index, etc.) used as the *trigger* of a test when no entry point in the inventory exposes that store. Backing stores are not entry points; they may only appear in **Preconditions / Resource Verification**, never as the trigger.
- Any private helper in the test that re-implements production parsing or key-derivation logic _(e.g. a local copy of an "extract original key from thumbnail key" routine)_ — assert against the spec's declared post-state, not against a re-derived expectation.

### Step 5 — Generate Post-Migration Tests

#### Pre-generation trigger audit (mandatory gate)

Before writing any test code, emit a **trigger-line pseudocode table** for every planned test method. For each row, write the single line of code (or pseudocode) that will serve as the trigger, then self-check it against the Forbidden trigger patterns in Step 4. The table format:

| TC ID | Trigger pseudocode | Entry Point Type (from spec) | Violates Step 4 forbidden patterns? |
|---|---|---|---|
| TC-XXX-001 | `serviceBusSender.sendMessage(queue, messageBody)` | Message-queue listener | No — publishes real event to declared source |

Any row whose last column is anything other than `No` MUST be revised until it passes. Do not proceed to code generation with any unresolved row.

#### Trigger rules

- **Trigger only via the declared entry point.** The constraint applies to the **trigger** of the test, not to setup/teardown. See the Forbidden trigger patterns in Step 4 for the concrete anti-patterns that must be rejected.
- **Seeding preconditions and resource verification may use SDKs directly.** When a test case's `Preconditions` or `Resource Verification` requires state on a real resource (object in a container, row in a table, message on a queue) and the application exposes no public entry point to create or read that state, the test setup / verification step MAY call the resource's SDK directly. Seed data comes from `testdata/`. This is setup/observation, not the trigger.
- **Async event-sourced tests** must wait on the **observable post-condition** using the language/framework's idiomatic async-wait helper that polls until the condition holds or a timeout elapses _(e.g. an `Awaitility`-style polling helper in JVM languages, `WaitFor` / polling loops in .NET, `pytest`-style retry helpers in Python)_. Never use a fixed-duration sleep, and never assert immediately after emitting the event.

#### Assertion rules

- **Every bullet in the spec is an assertion.** Walk `Expected Response`, `Resource Verification`, and `Negative Verification` bullet-by-bullet. Each bullet maps to at least one assertion in the test body. Missing any bullet → regenerate.
- **Load every fixture in `Data References`.** Each path under `Data References` must be loaded by the test through the language's normal resource-loading mechanism _(e.g. classpath resource stream in JVM, embedded resource / file read in .NET, file open in Python/Node/Go)_ and used either as input or as the expected value for an assertion. Unused fixtures are a planning bug — either the test under-asserts, or the spec lists a fixture it doesn't need (→ Step 7).
- **No existence-only / no-throw-only tests.** Assertions that only check resource existence, only check that a call did not throw, or only check non-null do not satisfy `Resource Verification`. Assert content, fields, sizes, statuses, redirect targets, message bodies, and DB column values exactly as the spec states.
- **Negative verification is mandatory where the spec lists it.** For every bullet under `Negative Verification` _(e.g. "no new row inserted", "no message published", "no thumbnail created")_, the test must perform the observation that proves the negative — not just skip it.

#### Test isolation rules

- **One TC = one independent test method.** No shared mutable state across test methods in the same class/module. No ordered-execution chains where one method's success is required for the next _(e.g. JUnit `@Order`, NUnit `[Order]`, xUnit `IClassFixture` for ordering, pytest fixture ordering tricks)_. No skip-when-previous-test-passed coupling _(e.g. `Assumptions.assumeTrue(previousState != null)`, `Skip.If(...)`)_. Every test sets up its own preconditions and tears them down.
- **Random keys per test run.** Use a fresh unique suffix (GUID / random string / timestamp+nonce) for every created entity; never deterministic names, since real resources are shared across parallel runs and re-runs.

#### Stack & dependency rules

- **Boot the full application stack** — no sliced/partial test contexts when any dependency is "real".
- **Real dependencies stay real.** Do not stub, fake, or mock anything marked "real" in the decision table at any layer.
- **Mocked dependencies** (only those marked "mock"): mock at SDK / HTTP boundary, seed from `testdata/`, assert on outbound requests as well as return values.
- **Test-only configuration** points to real endpoints from `infra/` via the project's standard mechanism (Spring profile, `.env`, `appsettings.IntegrationTest.json`, env vars). Activated for these tests only; do not modify production config.

#### Auth & cleanup rules

- **Pre-flight auth check** in test setup.
  - **Local runs (non-Azure host).** Managed Identity is unavailable — the test MUST authenticate as the developer's `az login` principal (e.g. via `DefaultAzureCredential` / `AzureCliCredential`). Do not fabricate a managed-identity client ID, do not point at IMDS, and do not require a service-principal secret for local runs.
  - **CI / Azure-hosted runs.** Use the configured Managed Identity when available, otherwise the CI service-principal env vars (`AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_CLIENT_SECRET` or federated credentials).
- **Cleanup via entry points first.** Prefer the application's own delete entry point for cleanup so test credentials need no extra data-plane permissions. Fall back to SDK cleanup only when no delete entry point exists. Run cleanup in `finally` / teardown; ignore "not found". Never use SDK cleanup as a workaround for a broken application delete path — if the application's delete entry point fails, that is a production bug (Step 6), not a cleanup-strategy choice.

### Step 6 — Validate and Run

Before running, run the **pre-run validation checklist** against generated code. Any `No` → regenerate (Step 5) or escalate to Step 7. Do not proceed to execution with a failing checklist.

**Coverage & mapping**

- [ ] Test method count equals `TC-*` count in `test-cases.md` (no extras, no missing).
- [ ] Every `TC-*` is referenced by exactly one test method, identifiable from the test name, display name, or an inline comment (use whatever the language idiomatically supports).
- [ ] No test class / module exists for an entry point absent from the Entry-Point Inventory (no DB-only / cache-only / SDK-only test class when those are backing stores rather than entry points).
- [ ] `${modernization-work-folder}/${taskid}/post-migration-plan.md` exists and has one row per `TC-*`.

**Trigger correctness (per test)**

- [ ] The line that invokes the system under test matches the declared `Entry Point` and does not match any pattern in Step 4 "Forbidden trigger patterns".
- [ ] For event-sourced subscriber entry points (see Terminology): the trigger produces a real event on the declared source via its SDK or wire protocol; an async-wait helper polls for the post-condition; no direct call to the subscriber's handler method (including via reflection) and no hand-fabricated message/event context.

**Assertion completeness (per test)**

- [ ] Every bullet under `Expected Response` is asserted.
- [ ] Every bullet under `Resource Verification` is asserted.
- [ ] Every bullet under `Negative Verification` is asserted (where the spec lists it).
- [ ] Every path in `Data References` is loaded by the test.
- [ ] No test relies solely on existence / non-null / no-throw assertions.

**Isolation**

- [ ] No shared mutable state across test methods.
- [ ] No ordered-execution chains where later tests depend on earlier tests succeeding.
- [ ] All created entities use random suffixes.

**Infra alignment**

- [ ] No mocks/stubs/fakes for any "real" dependency.
- [ ] Full application stack boots when any dependency is "real".
- [ ] Test-only configuration exists and points at the real endpoints in `infra/`.
- [ ] No hardcoded environment-specific topology in generated test source; all dependency identifiers/endpoints are supplied via test-only config and/or env vars.
- [ ] No generated "global cleanup" or "queue drain" step that alters shared resources beyond the TC-scoped setup/cleanup required by the spec.
- [ ] No test case requires failure injection (e.g. "storage unavailable", "backend throws IOException") on a dependency marked **real** without the ability to trigger that condition from the declared entry point. Any such case should have been surfaced in Step 4.3 and sent to Step 7 (re-freeze).

Run all `*PostMigrationIT` tests. Required: **100% pass**.

**Classifying a failure** — the spec is the source of truth. Before deciding it is a test bug, prove the test contradicts the spec. The default classification of any disagreement between spec and runtime behavior is **production bug**.

- **Test bug** (the generated test does not faithfully implement what the spec says) → fix the test. Examples: wrong fixture loaded, wrong assertion value relative to the spec, wrong trigger mechanism, missing async wait. The signal: the spec says X, the test asserts Y, the runtime returns X.
- **Production bug** (the runtime contradicts the spec) → **stop, do not patch the test.** Hand back to the migration developer per the teams SOP hand-back flow. The hand-back message must include: which `TC-*` failed, the declared expected behavior from the spec, the observed behavior from the run, and the suspected production cause. **Never** rewrite the trigger to bypass the broken entry point _(e.g. if a delete endpoint test fails, do not switch it to a direct storage-SDK delete just to make it pass)_, and **never** change the test's expected response / status / payload to match what the broken code returns. The broken entry point is the finding; the test must continue to fail until the production code is fixed.
- **Spec gap** (case requires failure injection that real infra cannot produce, fixture missing, entry point unlisted) → Step 7 (re-freeze). Do not silently downgrade a "real" dependency to a mock to make a test pass.
- **Infra issue** (auth/identity/role/network/endpoint problem on the real resource — e.g. AAD user or managed identity not created on the database / storage / Service Bus, missing role assignment, wrong principal expected by the resource, endpoint unreachable, no `az login` or no MI on the host) → handover to the Infra agent if one exists, otherwise call `ask_user`. Do not patch the test's auth setup beyond what Step 5 prescribes, and do not change the resource-side identity expectation (e.g. datasource username) from inside the test. Do not proceed until resolved.

### Step 7 — Re-Freeze Cycle for Spec Defects

Whenever any of the following occurs — the Step 3 audit fails; Step 4 finds an uncovered entry point, an infeasible-as-real failure-injection case, or a planning gap that cannot be expressed against the current spec; Step 6 finds a generated test cannot be reconciled with the spec; or any new fixture / scenario is needed — **coordinate a baseline re-freeze**: unfreeze the contents of `test-cases/` → amend (`test-cases.md`, `testdata/`, and/or `infra-decision-table.md`) → re-run the create-test-baseline freeze gate → re-freeze. There is no side channel for adding fixtures or cases in Phase 3.

### Step 8 — Report

Create `${modernization-work-folder}/${taskid}/verification-summary.md` summarizing decisions, results, and gaps. No other documents.
