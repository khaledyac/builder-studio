# 0002 · Contracts and versioning

- **Status:** accepted
- **Date:** 2026-11-24
- **Step:** 02

## Context

The hub services, the workspace, the templates and the pipelines are built in parallel, and they meet at shared contracts. The contracts need one source of truth, generated artifacts that can't drift from it, and a safe way to change.

We chose not to put the version in the layout: there are no `v1/` or `v2/` folders or packages. The version is a value instead.

## Decision

**Source of truth.** The Pydantic models in `contracts/` (`studio.contracts`) are the source of truth. Everything else is generated into `contracts/generated/`, and nobody edits it by hand:

- **JSON Schema:** one file per contract in `generated/schemas/`, and one per event type in `generated/events/`.
- **OpenAPI:** the workspace API's document, in `generated/workspace-api/openapi.json`.
- **TypeScript:** types for `web/`, in `generated/ts/`.

`task contracts-gen` regenerates them. `task contracts-check`, which runs in CI, checks every contract's valid and invalid examples, then fails if the generated files differ from the models.

**One version, read at runtime.** There's one semver for all contracts: the `version` in `contracts/pyproject.toml`. Code reads it as `studio.contracts.version.CONTRACT_VERSION`, and every generated file is stamped with it. Changing the version without regenerating is drift, so CI fails.

**Payloads say which version wrote them:**

- `need.yml`, `app.yaml`, registry records and agent steps carry a `contract_version` field.
- Events carry the CloudEvents extension attribute `contractversion`.

A reader accepts any version with its own major, and rejects another major with an error that says to migrate.

Two kinds of contract aren't versioned per message:

- **UI events:** the platform API and the web UI ship together.
- **Workspace API calls:** the OpenAPI document's `info.version` is the API's version.

**Readers are tolerant, except of `need.yml` and `app.yaml`.** Unknown fields are ignored, so a newer minor version can add fields without breaking older readers. `need.yml` and `app.yaml` are the exception: people and agents edit them by hand, and ignoring a misspelled key could hide data access and lower the risk tier. An unknown key there is an error, so even an additive change to those two ships readers before writers.

**The generated files enforce the same rules as the models.** Some rules are checked in code, such as the major version and paths staying inside the repo. They also appear in the generated schemas, as patterns. `task contracts-check` runs every example through both the models and the generated files, so the two can't disagree.

## How to change a contract

Change a contract only in a plan step that says so (the hard rule in `AGENTS.md`).

**Additive change (minor bump):** a new optional field, a new event type or a new operation.

1. Change the model and bump the minor version.
2. Add or update the examples.
3. Run `task contracts-gen`, and commit the generated files with the change.

**Breaking change (major bump):** removing or renaming a field, making a field required, tightening validation, changing what a field means, removing an operation, or adding an enum value that old readers would reject.

1. Change the model and bump the major version.
2. Add a migration from the previous major to `studio.contracts.migrations` for every affected contract that's stored or queued: `need.yml`, `app.yaml`, registry records, agent steps and events. Readers upgrade old payloads instead of rejecting them. The first breaking change creates that module, and the old examples become its tests.
3. Ship the readers before the writers.
4. For the workspace API, add the new operation next to the old one, and remove the old one once no caller uses it.
5. Remove the migration once no stored document or queued message uses the old major.

## Consequences

- There are no parallel version folders. Older versions live in git history.
- Every stored or queued payload says which version wrote it, so a mismatch is caught at the boundary with a clear message.
- A breaking change costs a migration and an ordered rollout. That's deliberate: it should be rare.
