# Test Cases

## Metadata

| Field | Value |
|-------|-------|
| Project | [Application Name] |
| Migration Scope | [e.g. migrate from AWS S3 to Azure Blob Storage] |
| Created At | [Date] |
| Status | baseline |

## API Types

Choose the type that matches the application's public boundary. A project may use more than one type.

| Type | Entry Point | Example |
|------|------------|---------|
| HTTP | REST / gRPC endpoint | `POST /api/files/upload` |
| Method | Public method call | `FileService.upload(name, stream)` |
| CLI | Command-line invocation | `app upload --file sample.jpg` |
| Event | Message / event handler | `onMessage(QueueEvent)` |

## Test Cases

### [TC-001] [Operation Name] — Happy Path

| Field | Value |
|-------|-------|
| ID | TC-001 |
| Category | happy-path |
| Type | [HTTP \| Method \| CLI \| Event] |
| Entry Point | [e.g. `POST /api/files/upload` or `FileService.upload(name, stream)`] |
| Description | [What this test verifies at the API/UX boundary] |

**Input:**

```
[Request / arguments / command — application-boundary only]
```

**Expected Output:**

```
[Response / return value / stdout — application-boundary only]
```

**Preconditions:**

- [Any required application state before the test]

---

### [TC-002] [Operation Name] — Error / Failure

| Field | Value |
|-------|-------|
| ID | TC-002 |
| Category | failure |
| Type | [HTTP \| Method \| CLI \| Event] |
| Entry Point | [e.g. `GET /api/files/nonexistent` or `FileService.download("missing")`] |
| Description | [What failure scenario this test covers] |

**Input:**

```
[Request / arguments / command]
```

**Expected Output:**

```
[Error response / exception / exit code]
```

**Preconditions:**

- [Any required application state before the test]

---

## Rules

- Each test case describes **only API/UX-level inputs and outputs** — no service-specific SDK types, no backend implementation details.
- Test cases must be **backend-agnostic**: they must make sense whether the underlying service is the old technology, the new technology, or an in-memory mock.
- Per operation, cover **four buckets**: happy path, boundary values, special inputs, and failure mapping. Add more `[TC-NNN]` sections as needed.
- Use **2–5 representative records per entity** (table, queue, container, etc.).
- All payload data referenced in test cases must be externalized under `testdata/shared/` — no inline byte literals or hardcoded values in test source.