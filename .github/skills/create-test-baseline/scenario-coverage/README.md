# Composite Scenario Coverage (Step 3a sub-routine)

A focused add-on to the `create-test-baseline` skill that produces **cross-endpoint,
stateful behavioral test cases** for HTTP/REST modules, grounded in static analysis.
It does **not** replace Step 3 — it runs *after* Step 3's per-endpoint coverage to add
the multi-endpoint scenarios a single-endpoint pass tends to miss (create → read →
mutate → delete data-flows that span several controllers).

This sub-routine is the integration of an endpoint-modeling + scenario-generation
method (a weakened SAINT pipeline) into the baseline skill. Only the **composite
scenario** half is fused; per-endpoint input-space breadth stays the skill's native
Step 3 job. The endpoint model is produced by a **mandatory** static-analysis tool
(`endpoint-model-sa.py`, which runs IBM CLDK `codeanalyzer`); the composite scenarios it
grounds are then authored **directly** as `test-cases.md` cases using the existing
[test-cases-template.md](../test-cases-template.md).

## Activation gate

Run this sub-routine for a module **only when both** hold:

1. The module is **in-scope** per Step 1 (it directly touches a migration-relevant
   resource).
2. The module exposes **HTTP/REST** entry points implemented with one of the
   recognized frameworks: **Spring MVC** (including annotated WebFlux controllers),
   **JAX-RS**, **Micronaut HTTP**, or the **Servlet API**.

If a module has no HTTP entry points (pure CLI, message-queue listener, scheduled job,
library API), skip this sub-routine and rely on the skill's native Step 3 — composite
HTTP scenarios do not apply.

## Two layers, then authoring

```
Layer 0  Static endpoint model   →  endpoint-model.md   (run endpoint-model-sa.py — forced CLDK)
Layer 1  Object Dependency Graph  →  endpoint-model.md   (agent enrichment, re-validated by the tool)
Layer 2  Scenario authoring       →  scenario-authoring.md (walk ODG → composite test cases)
```

- **Layer 0 — Static endpoint model.** Run `endpoint-model-sa.py build` to produce a
  framework-neutral model of every HTTP endpoint (the 8-tuple), its DTO schemas, its auth
  model, and the deterministic **resource** edges of the dependency graph. See
  [endpoint-model.md](endpoint-model.md). Static analysis is **mandatory** here because every
  scenario step must reference a **real** endpoint — scenarios are only as trustworthy as the
  model the bytecode actually produced.
- **Layer 1 — Object Dependency Graph (ODG).** Enrich the model with **producer-consumer**
  and **database** edges by reading handler bodies (following the reused enrichment contract
  [model-enrich.txt](model-enrich.txt)): which endpoint produces an id/resource that another
  consumes, and which endpoints read-after-write the same table. Then re-validate the enriched
  model with `endpoint-model-sa.py validate`. See [endpoint-model.md](endpoint-model.md).
- **Layer 2 — Scenario authoring.** Walk the ODG to compose cross-endpoint scenarios and
  write each one **directly** as a single composite `test-cases.md` case (one `TC-<MODULE>-NNN`,
  multiple HTTP calls inside the `Trigger`). See [scenario-authoring.md](scenario-authoring.md).

## Where it plugs into the 7-step workflow

| Step | Contribution of this sub-routine |
|---|---|
| Step 1 | Layer 0 gives an exhaustive HTTP entry-point inventory; reconcile it with the Step 1 catalog (anti-omission). |
| Step 3 | **Step 3a** (this sub-routine): after the native per-endpoint cases, add composite scenario cases authored from Layer 2. |
| Step 5 | Layer 0's `databaseOperations` + `authModel` feed the infra decision-table dependency rows. |
| Step 6 | The **scenario-grounding gate** (every scenario step matches a real endpoint) runs as part of freeze validation. |

## Artifacts and where they live

- The endpoint model + ODG is **working scratch only**, written under
  `${modernization-work-folder}/${taskid}/scenario-coverage/endpoint-model.json`
  (or held in context). It is **not** part of the frozen `test-cases/` bundle.
- The only frozen output is the composite scenario cases appended into the module's
  `test-cases/test-cases.md`, plus any new `testdata/` fixtures they reference — same
  freeze rules as the rest of the baseline.
- The endpoint model **is** materialized as `endpoint-model.json` (scratch only); **no**
  `endpoint-requests.json` and **no** `scenarios.json` are produced — the scenario reasoning
  lands straight in markdown.

## Forced static analysis (prerequisite)

Layer 0 is produced by the bundled `endpoint-model-sa.py`, which runs IBM CLDK
`codeanalyzer` at symbol-table level and applies the framework adapters described in
[endpoint-model.md](endpoint-model.md). This static-analysis run is **mandatory** — the
model is never hand-written or LLM-guessed. Provision its prerequisites before running
Step 3a: **Python 3**, a **JDK**, **IBM CLDK** (`pip install cldk`, or set
`SAINT_CODEANALYZER_JAR`), and on **Windows** the **WSL** runtime (`codeanalyzer` runs under
WSL there). Run the **preflight environment check** in [endpoint-model.md](endpoint-model.md)
to verify each piece and install the missing ones first. If the tool cannot run, Step 3a
**fails closed** for that module: it produces no composite scenario cases and the per-endpoint
Step 3 baseline stands unchanged. See the exit-code table in [endpoint-model.md](endpoint-model.md).
