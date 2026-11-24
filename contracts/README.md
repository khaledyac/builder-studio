# Contracts

The shared contracts that the hub services, the workspace, the templates and the web UI build against. The Pydantic models in `src/studio/contracts/` are the source of truth. Everything in `generated/` comes from them.

| Contract | Model | Generated |
|---|---|---|
| `need.yml` | `need.Need` | `schemas/need.schema.json`, `ts/need.schema.d.ts` |
| `app.yaml` | `app.AppManifest` | `schemas/app.schema.json`, `ts/app.schema.d.ts` |
| Registry record | `registry.RegistryRecord` | `schemas/registry-record.schema.json`, `ts/…` |
| Agent step (Cloud Tasks) | `agent_step.AgentStep` | `schemas/agent-step.schema.json`, `ts/…` |
| Events (Pub/Sub, CloudEvents) | `events.Event` | `schemas/event.schema.json`, `events/<type>.schema.json`, `ts/…` |
| UI events (server-sent) | `ui_events.UiEvent` | `schemas/ui-event.schema.json`, `ts/…` |
| Workspace API | `workspace_api.router` | `workspace-api/openapi.json` |

All the generated paths are under `generated/`. The risk tier isn't a contract: it's computed by `libs/policy` from `app.yaml`.

## Commands

- **`task contracts-gen`** regenerates everything in `generated/`. Commit the result with the change.
- **`task contracts-check`** runs the example tests, then fails if `generated/` differs from the models. CI runs it.

## Examples

Each contract has examples in `examples/<contract>/valid/` and `examples/<contract>/invalid/`, as YAML or JSON. An invalid example is named `<field>.<what's wrong>`, for example `examples.only-one.yaml`. The test checks that it fails on that field only, not on a typo somewhere else. Every example also runs through the generated schema or OpenAPI, which must agree with the model.

## Changing a contract

Change a contract only in a plan step that says so. Bump the version in `pyproject.toml` (a minor bump for an additive change, a major bump for a breaking one), then regenerate. [ADR 0002](../docs/adr/0002-contracts-and-versioning.md) explains the rules and how to ship a breaking change.
