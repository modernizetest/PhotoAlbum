# Infra Decision Table

> This document is part of the **frozen baseline bundle**. It records, for every external dependency the migrated application talks to, whether the post-migration tests will exercise it as a **real** provisioned resource or as a **mock** at the SDK / HTTP boundary. The decision is made once here and reused as-is by the `verify-test-baseline` skill.

## Metadata

| Field | Value |
|-------|-------|
| Project | [Application name] |
| Module | [e.g. `web`, `worker`] |
| Migration Scope | [e.g. migrate from AWS S3 + SQS to Azure Blob Storage + Service Bus] |
| Created At | [YYYY-MM-DD] |
| `infra/` Snapshot | [git SHA or "infra-missing" if no infra folder] |
| Status | baseline (frozen) |

## Decision Table

One row per external dependency. The dependency list is derived from the target stack and the entry-point inventory in `test-cases.md` (Step 1 of `create-test-baseline`). No dependency the application talks to may be omitted.

| Dependency | Infra Match | Decision | Auth Method | Reason |
|---|---|---|---|---|
| [Dependency name + identifier, e.g. `Azure Blob Storage (sthve4rw7qkv7k4)`] | [`Yes — <path/in/infra>` \| `No`] | [`real` \| `mock`] | [see allowed values below] | [Single sentence; see rules below] |

### Required column values

- **Dependency** — Name the concrete resource the application binds to, including its identifier when applicable (account / namespace / database / topic name). Generic categories alone (e.g. "object storage") are not acceptable.
- **Infra Match** — Exactly one of:
  - `Yes — <relative path under infra/>` when a provisioned endpoint + credentials are documented in `infra/`.
  - `No` when no matching resource exists in `infra/` (or `infra/` does not exist at all).
- **Decision** — Exactly one of `real` or `mock`. No conditional values, no per-test-case overrides in this column.
- **Auth Method** — How the application authenticates to this dependency at runtime. Exactly one of:
  - `managed-identity` — user-assigned or system-assigned managed identity (cloud workload identity). **Only valid when the application is hosted on a cloud platform that issues managed identities** (e.g. Azure App Service / Container Apps / AKS / VM for Azure MI, IAM Roles for Service Accounts on EKS, etc.). Must NOT be selected for applications that also run on developer laptops or any non-cloud host — those targets have no MI issuer and must use a different credential type from this list. Local-only / non-cloud-hosted apps therefore pick `service-principal`, `username-password`, `connection-string`, etc. (Test-time fallback for local runs on a cloud-hosted app is a separate concern, handled by `verify-test-baseline` Step 5.)
  - `service-principal` — client-id + secret / certificate / federated credential.
  - `username-password` — basic auth, DB user + password, etc.
  - `connection-string` — opaque connection string that embeds the secret (e.g. classic storage / Service Bus / DB connection strings).
  - `sas-token` — shared-access signature or equivalent scoped token.
  - `api-key` — static API key / subscription key / bearer token issued out-of-band.
  - `mtls` — mutual TLS / client certificate.
  - `anonymous` — no authentication (public endpoint).
  - `n/a` — only allowed when `Decision = mock` and the mock layer does not perform real authentication.
  
  When the migration changes the auth method (e.g. password → managed-identity), record the **post-migration** value here; do not list both. The pre-migration value belongs in the migration scope description, not in this table.
- **Reason** — One sentence. Must justify the Decision against the Infra Match per the rules below.

### Decision rules (must match Step 2 of `create-test-baseline`)

- `Infra Match = Yes` → Decision MUST be `real`. Mocking a provisioned dependency is a bug.
- `Infra Match = No` and `infra/` exists → Decision MUST be `mock`. Reason should state that the dependency is not provisioned.
- `infra/` does not exist at all → every row's Decision is `mock` and the Reason is `infra-missing`. Set the `infra/` Snapshot field to `infra-missing`.
- `Auth Method = n/a` is allowed **only** when `Decision = mock`. A `real` row must declare a concrete auth method.

### Banned phrasings (auto-reject)

- Decision values other than `real` / `mock` (e.g. `mostly real`, `real-with-fallback`, `tbd`).
- Auth Method values outside the allowed list above. Free-form descriptions (e.g. "DefaultAzureCredential", "whatever the SDK picks") are not acceptable — pick the concrete underlying credential type instead.
- Auth Method = `managed-identity` on an application that is not hosted on a managed-identity-issuing platform (e.g. on-prem deployment, generic VM without MI, local-only tool).
- Auth Method = `n/a` on a `real` row.
- Reasons that do not reference either `infra/` or `infra-missing` (e.g. "for performance", "to keep tests fast", "team preference").
- Per-test-case carve-outs ("real for happy-path, mock for failure"). Failure-injection conflicts are handled in `verify-test-baseline` Step 4 via a re-freeze, not by splitting a row here.
- Missing or empty cells.

## Worked Example (reference; do not copy verbatim)

| Dependency | Infra Match | Decision | Auth Method | Reason |
|---|---|---|---|---|
| Azure Blob Storage (`sthve4rw7qkv7k4`, container `assets`) | Yes — `infra/env-config.md` | real | managed-identity | Provisioned storage account with container `assets` in resource group `rg-app-demo`. |
| Azure Service Bus (`sbhve4rw7qkv7k4`, queue `image-processing`) | Yes — `infra/env-config.md` | real | managed-identity | Provisioned namespace with queue `image-processing` in resource group `rg-app-demo`. |
| Azure Database for PostgreSQL (`pg6kt67kwkpeqji2`, database `app`) | Yes — `infra/env-config.md` | real | managed-identity | Provisioned flexible server with database `app`; migration moves from password to managed identity. |
| Third-party email API (`api.example-mail.com`) | No | mock | n/a | No provisioned credentials in `infra/`; mock at the HTTP boundary, seed from `testdata/`. |
