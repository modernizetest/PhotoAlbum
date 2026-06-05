# Layer 0 + Layer 1 — Static endpoint model & Object Dependency Graph

Build a framework-neutral model of the module's HTTP endpoints, then enrich it into an
Object Dependency Graph (ODG). The composite scenarios in
[scenario-authoring.md](scenario-authoring.md) are authored by walking this graph, so the
model must be **grounded in the actual code** — never invent an endpoint or an edge.

**Layer 0 is produced by a mandatory static-analysis tool, not by reading controllers by
hand.** The bundled script `endpoint-model-sa.py` runs IBM CLDK `codeanalyzer` over the module
and emits the endpoint model mechanically. The agent never hand-simulates this step: the whole
point of Step 3a is that every scenario is grounded in a model the application's bytecode
actually produced. Layer 1 (the semantic ODG edges) is the part the agent reasons about, and
the tool re-validates that reasoning afterward.

## Layer 0 — run the static-analysis tool (mandatory)

Run the bundled driver to produce the endpoint model:

```
python endpoint-model-sa.py build <module-path> ${modernization-work-folder}/${taskid}/scenario-coverage/endpoint-model.json
```

### Prerequisites (provision before running — do not skip)

The tool requires a real static-analysis runtime. This is a hard prerequisite of Step 3a.
Python 3, a JDK, and IBM CLDK are required on every platform; WSL is an additional Windows-only
prerequisite.

- **Python 3** on PATH.
- **A JDK** on PATH (`codeanalyzer` is a Java program).
- **IBM CLDK** providing the `codeanalyzer` jar: `pip install cldk` (or set
  `SAINT_CODEANALYZER_JAR` to an existing jar path).
- **Windows only — WSL:** on Windows the tool runs `codeanalyzer` under WSL because the jar's
  default exclude regex is invalid on Windows-style paths; on Linux and macOS the jar runs
  natively and WSL plays no part. Set `SAINT_WSL_DISTRO` to pick a distro when more than one is
  installed.

### Preflight: check the environment and install what is missing

Before the first `build`, verify each prerequisite and install the ones that can be installed.
Run these checks; act on each result, then proceed only when all required pieces are present:

1. **Python 3** — `python --version` (or `python3 --version`). If absent, install Python 3 with
   the platform package manager (e.g. `winget install Python.Python.3.12`, `apt-get install -y
   python3`, `brew install python`).
2. **JDK** — `java -version`. If absent, install a JDK 17+ (e.g. `winget install
   Microsoft.OpenJDK.21`, `apt-get install -y openjdk-21-jdk`, `brew install openjdk@21`).
3. **IBM CLDK** (the `codeanalyzer` jar) — `python -c "import cldk"`. If it errors, install it
   with `pip install cldk` (this is always installable and is the usual missing piece). If
   `pip` cannot reach the package index, set `SAINT_CODEANALYZER_JAR` to a pre-downloaded jar.
4. **On Windows only — WSL** — `wsl --status`. If WSL is missing, install it with
   `wsl --install` (this needs administrator rights and a reboot). Ensure the chosen distro has
   a JDK (`wsl java -version`); install one inside the distro if needed
   (`wsl -- sudo apt-get install -y openjdk-21-jdk`). Set `SAINT_WSL_DISTRO` when several
   distros exist.

After installing the missing pieces, run `build`. If a prerequisite **cannot** be installed in
this environment (e.g. WSL requires elevation that is unavailable), the tool exits non-zero and
Step 3a **fails closed** — see the exit-code table. Do not work around a missing tool by
hand-writing the model.

### Exit codes and what to do

| Exit | Meaning | Action |
|---|---|---|
| 0 | model written (≥1 endpoint) | proceed to Layer 1 |
| 2 | no supported web framework detected | **skip Step 3a** for this module; keep the per-endpoint baseline from Step 3 |
| 3 | static analysis could not run (missing jar / JDK, or — on Windows — WSL) | provision the prerequisite and re-run; **do not** hand-write the model |
| 4 | codeanalyzer ran but produced no usable symbol table | check the module builds / has source; re-run |

**Fail closed.** If the tool cannot run (exit 3/4), the module gets **no** composite scenario
cases — its per-endpoint baseline from Step 3 still stands. Never substitute a hand-read or
LLM-guessed endpoint model for the tool's output; an ungrounded model defeats the gate.

## Endpoint model shape (what the tool writes)

```jsonc
{
  "schema": "saint-endpoint-model/1",
  "frameworksDetected": ["spring-mvc"],
  "endpointCount": 2,
  "endpoints": [
    {
      "id": "EP01",                       // stable: sorted by (path, method), then EP01..EPnn
      "controllerClass": "com.acme.OrderController",
      "handlerSignature": "createOrder(OrderRequest)",
      "path": "/orders",                  // normalized: leading '/', path vars as "{}"
      "httpMethod": "POST",               // GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS
      "parameters": [
        { "name": "body", "type": "OrderRequest", "kind": "body", "provenance": "SA" }
      ],
      "interParamDependencies": [],        // filled by the agent in Layer 1
      "databaseOperations": ["INSERT orders"],
      "responseSchema": "OrderResponse",
      "framework": "spring-mvc",
      "provenance": "SA"
    }
  ],
  "dtoSchemas": { "OrderRequest": { "fields": [ { "name": "items", "type": "List<Item>",
                  "validationAnnotations": ["@NotEmpty"], "provenance": "SA" } ] } },
  "odg": { "nodes": [ { "id": "EP01", "functionalSummary": null, "provenance": "SA" } ],
           "edges": [ { "from": "EP01", "to": "EP02", "type": "resource", "provenance": "SA" } ] },
  "authModel": { "fragments": [ /* security-config evidence */ ] }
}
```

## How the tool builds Layer 0 (for auditing)

You do not execute these rules — the tool does. They are documented so you can audit the
model and understand its limits.

- **Parameter kinds.** Every handler parameter is one of:
  `path`, `query`, `header`, `body`, `form`, `cookie`, `unknown`.
- **Framework adapters** (one endpoint-producing framework per class):
  - **Spring MVC** (incl. annotated WebFlux): `@Controller` / `@RestController`;
    `@RequestMapping` (+ its `method=`), `@GetMapping`/`@PostMapping`/`@PutMapping`/
    `@PatchMapping`/`@DeleteMapping`; class-level `@RequestMapping` prefix joined to each method
    path. `@PathVariable`→path, `@RequestParam`→query, `@RequestHeader`→header,
    `@RequestBody`→body, `@CookieValue`→cookie.
  - **JAX-RS**: `@Path` + `@GET`/`@POST`/`@PUT`/`@DELETE`/…; `@PathParam`→path,
    `@QueryParam`→query, `@HeaderParam`→header, `@FormParam`→form, `@CookieParam`→cookie; an
    un-annotated non-primitive parameter is the request body.
  - **Micronaut HTTP**: `@Controller`; `@Get`/`@Post`/`@Put`/`@Delete`/… with `@Body`,
    `@PathVariable`, `@QueryValue`, `@Header`.
  - **Servlet API**: `HttpServlet` subclasses / `@WebServlet`; `doGet`/`doPost`/`doPut`/
    `doDelete` → GET/POST/PUT/DELETE. Parameters read via `request.getParameter(...)` are
    unresolved at symbol level — those endpoints are flagged
    `paramExtraction == "unsupported-at-symbol-level"` and the agent infers their parameters in
    Layer 1. A servlet whose mapping lives only in `web.xml` gets the sentinel path
    `/__servlet-mapping-unknown__`.
- **Path normalization.** Each path becomes a leading `/`, segments joined by `/`, and **every
  path-variable segment replaced by `{}`** (e.g. `/orders/{orderId}/items` →
  `/orders/{}/items`). This is the canonical form the grounding gate matches against — apply the
  same normalization when checking scenario steps.
- **DTO schemas.** For every body type, the fields and their **bean-validation annotations**
  (the standard set — `@NotNull`, `@NotEmpty`, `@NotBlank`, `@Size`, `@Min`, `@Max`, `@Email`,
  `@Pattern`, `@Positive`, `@PositiveOrZero`, `@Negative`, `@NegativeOrZero`, `@Digits`,
  `@Past`, `@Future`, `@DecimalMin`, `@DecimalMax`, `@AssertTrue`, `@AssertFalse` — plus any
  project annotation meta-annotated `@Constraint`). A DTO whose fields carry **no** such
  annotation is **unconstrained at the binding layer** — remember this for the grounding gate (a
  "missing/empty required field → strict 4xx" claim is only valid when the field is actually
  constrained).
- **Auth model.** Auth rules from security configuration (Spring Security
  `SecurityFilterChain`/matchers, JAX-RS `@RolesAllowed`/`@PermitAll`, Micronaut `@Secured`).
- **Resource edges (deterministic).** Endpoints are grouped by resource key (normalized path
  with a trailing `/{}` stripped, e.g. `/orders` and `/orders/{}` share key `/orders`); within a
  group every writer (`POST`/`PUT`/`PATCH`) is linked to every reader (`GET`/`DELETE`) as a
  `resource` edge — "the reader depends on state the writer produced". These edges are
  `provenance: "SA"`.

## Layer 1 — ODG enrichment (agent reasoning, then re-validated by the tool)

The resource edges above are structural. Add the two **semantic** edge classes, the functional
summaries, the inter-parameter dependencies, and any inferred Servlet parameters by reading
handler bodies, following [model-enrich.txt](model-enrich.txt) (the reused SAINT enrichment
contract):

- **producer-consumer**: endpoint A returns an identifier/resource (e.g. a created `orderId`
  in its response body or `Location` header) that endpoint B takes as a `path`/`query`/`body`
  input. Edge `A → B`, type `producer-consumer`. This is the backbone of multi-step scenarios.
- **database**: endpoint A writes a table/row that endpoint B subsequently reads or mutates
  (read-after-write on the same entity), even when no id is passed through the HTTP layer.
  Edge `A → B`, type `database`.

Tag every field you add with `"provenance": "LLM"` (each semantic edge, each functional
summary, each inter-parameter dependency) and record a one-line rationale citing the evidence
(the field/header carrying the id, or the table name). Inter-parameter dependency
`relationType` must be one of the seven categories in
[model-enrich.txt](model-enrich.txt) (`AllOrNone`, `Requires`, `OnlyOne`, `Or`, `ZeroOrOne`,
`Arithmetic`, `Complex`).

**Re-validate the enriched model with the tool** — the deterministic gate over your reasoning:

```
python endpoint-model-sa.py validate ${modernization-work-folder}/${taskid}/scenario-coverage/endpoint-model.json
```

Exit 0 means the merged model is structurally sound: semantic edges are provenance LLM,
resource edges stay provenance SA, IPD categories are from the fixed catalog, and ODG nodes
equal the endpoint ids. Fix any reported violation before authoring scenarios.

## Output

The model lives at
`${modernization-work-folder}/${taskid}/scenario-coverage/endpoint-model.json`
(scratch — not frozen). Once it validates, proceed to
[scenario-authoring.md](scenario-authoring.md).
