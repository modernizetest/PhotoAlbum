# Layer 2 — Scenario authoring (composite test cases)

Walk the ODG from [endpoint-model.md](endpoint-model.md) to compose **cross-endpoint,
stateful scenarios**, and write each scenario **directly** as one composite case in the
module's `test-cases/test-cases.md` using [test-cases-template.md](../test-cases-template.md).
No `scenarios.json` is produced — the scenario reasoning lands straight in markdown.

Walk only the ODG that `endpoint-model-sa.py validate` has accepted (the tool-built Layer 0
plus the agent's re-validated Layer 1 enrichment). The composition reasoning below reuses the
SAINT scenario method: order atomic steps by their dependency edges so a step that consumes a
resource is always reached after the step that produces it.

## What a scenario is

A scenario is a short, ordered story over several endpoints that exercises real state
flow, expressed in Given / When / Then terms:

- **Given** — preconditions established by earlier write endpoints (seed state).
- **When** — an ordered chain of endpoint calls (the producer-consumer / resource path).
- **Then** — the observable outcome on the **focal** endpoint (the one being asserted).

Compose scenarios by following ODG edges:

- A **producer-consumer** edge `A → B` yields a 2-step chain "call A, feed its id into B".
- Chaining edges (`A → B → C`) yields longer create→read→mutate→delete flows.
- A **resource** edge backs read-after-write checks ("after POST, the GET reflects it").
- A **database** edge backs cross-controller state checks ("after A writes, C sees it").

Aim for the highest-value flows first: full lifecycle of each in-scope resource
(create → fetch → update → fetch → delete → fetch-404), plus the cross-resource flows the
migration touches. Keep each scenario minimal — only the steps needed to set up and assert
one outcome.

## One scenario = one composite test case

A scenario maps to **exactly one** `TC-<MODULE>-NNN`. The multiple HTTP calls do **not**
become multiple test cases — they live **inside** that single case:

| Scenario element | Lands in test-case field |
|---|---|
| Scenario name / intent | **Description** |
| Focal endpoint (the one `Then` asserts) | **Entry Point** (`METHOD /path`) + **Entry Point Type** = `HTTP` |
| Outcome class (success / invalid / unauthorized…) | **Category** (`happy-path` / `boundary` / `special-input` / `failure`) |
| **Given** + any setup-only calls | **Preconditions** (ordered setup calls + seed data refs) |
| **When** ordered call chain | **Trigger** — numbered steps `1..N`, last step is the focal call |
| **Then** on the focal endpoint | **Expected Response** (status + body assertions) |
| Intermediate-step assertions, resource/database-edge checks | **Resource Verification** (state that must hold after the chain) |
| Failure expectations (auth, conflict, not-found) | **Negative Verification** |
| Ids/resources produced mid-chain and reused | **Data References** (+ externalized `testdata/` fixtures) |

Ordering inside `Trigger` follows the producer-consumer dependency: a step that consumes an
id is numbered **after** the step that produces it.

### When to split into multiple cases

If a single story would assert **two independent focal outcomes** (e.g. "the update
succeeds" *and* "a second concurrent update conflicts"), split it into **two** test cases —
each with one focal endpoint and one asserted outcome. Do not pack unrelated assertions into
one case.

## Category selection

- `happy-path` — the chain runs with valid inputs and the focal call returns its success
  status.
- `boundary` — the chain drives the focal input to an edge of a **constrained** field
  (from the DTO schema: min/max length, numeric bounds, empty collection where `@NotEmpty`).
- `special-input` — encoding/format edges (unicode, escaping, large payloads) on the chain.
- `failure` — the focal call is expected to fail: missing/invalid auth (only if the endpoint
  is in the auth model), not-found on a deleted id, conflict on a duplicate write, or a
  validation rejection on a **constrained** field.

## Grounding gate (mandatory before freeze)

Every `Trigger` and `Preconditions` step must reference a **real** endpoint from the
tool-built, tool-validated Layer 0 model. Validate each step's `METHOD /path` against the
model exactly as the static pipeline does:

1. Normalize the step path (path-variable segments → `{}`).
2. A step matches an endpoint when **method is identical** and the paths have the **same
   number of segments**, where each model segment is either a literal equal to the step
   segment, or a `{}` path-variable (which matches any concrete segment).
3. If **no** endpoint matches a step → the scenario references a non-existent endpoint:
   **fix or drop the step**. Do not freeze a scenario with an unmatched step.

Also reconcile validation claims with the DTO schema: a `failure` case asserting a strict
`4xx` for a missing/empty field is only valid when that field carries a binding-layer
constraint (Layer 0 DTO schema). If the field is unconstrained, the rejection is
service-level — relax the expectation to `4xx/5xx` or assert the service-level behavior the
code actually produces.

## Worked example

ODG fragment: `EP01 POST /orders` —producer-consumer→ `EP02 GET /orders/{}` ;
`EP01` —resource→ `EP03 DELETE /orders/{}` ; `EP03` —producer-consumer→ `EP02`.

Scenario: *"Create an order, read it back, delete it, then confirm it is gone."* →

```markdown
| Field | Value |
|---|---|
| ID | TC-ORDERS-007 |
| Category | happy-path |
| Entry Point Type | HTTP |
| Entry Point | GET /orders/{orderId} |
| Description | Order lifecycle: create, fetch, delete, then fetch returns not-found |

**Trigger**
1. POST /orders with body `order-valid.json` → capture `orderId` from response.
2. GET /orders/{orderId} (using captured `orderId`).
3. DELETE /orders/{orderId}.
4. GET /orders/{orderId} (focal call).

**Preconditions**
- No order with the `order-valid.json` business key exists (clean state).

**Expected Response**
- Step 4 (focal): 404 Not Found.

**Resource Verification**
- After step 1: GET in step 2 returns 200 with the same items as `order-valid.json`.
- After step 3: the order row no longer exists.

**Negative Verification**
- Re-issuing DELETE on the already-deleted `orderId` does not resurrect the order.

**Data References**
- Input: `testdata/orders/order-valid.json`
- Runtime-produced: `orderId` (captured at step 1, reused in steps 2–4)
```

Note the single `TC-ORDERS-007` carries four HTTP calls; the focal/asserted call is the
final `GET`, so `Entry Point` is `GET /orders/{orderId}` and `Category` is `happy-path`
(the lifecycle completes as designed).

## After authoring

Append the composite cases into the module's `test-cases/test-cases.md`, externalize any new
fixtures into `testdata/`, and continue with Step 4 (testdata), Step 5 (infra decision-table —
use Layer 0 `databaseOperations` + `authModel`), Step 6 (validation, incl. the grounding gate
above), and Step 7 (freeze).
