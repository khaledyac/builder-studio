# 02 · Contracts and schemas

**Milestone:** M0 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 01

## Why

The hub services, the workspace, the templates and the pipelines are built in parallel. Shared contracts are how they meet. Architecture: §2, §4, §7, §8, §9.

## Build

In `contracts/`, written as **Pydantic v2 models**, which are the source of truth. The version is a value, not a folder (ADR 0002). JSON Schema is exported from them, the workspace API's OpenAPI comes from a FastAPI router built on the same models, and the TypeScript types for `web/` are generated from those files. Each contract has examples:

- **`need.yml`:** problem, users, 2–3 examples, data (connector IDs), read or write, audience, out of scope, domain, project type.
- **`app.yaml`:** app name, owner (Okta ID), domain, project type, connectors with access mode, resources from approved modules, audience, risk tier (computed, read-only), expiry.
- **Registry record:** app ID, owner, domain, tier, expiry, repo, environments, status (`draft`, `live-lab`, `live-prod`, `expired`, `archived`).
- **Workspace API (OpenAPI):**
  - run a command, with streamed output and a timeout,
  - read, write and list files,
  - git: status, commit, branch, worktree add and remove, merge, push,
  - preview: start, status, URL,
  - bootstrap, restore, health.
- **Agent step message** (the Cloud Tasks payload): session ID, user ID, app ID, step kind, input, idempotency key.
- **Events** (Pub/Sub, CloudEvents format):
  - `session.started`, `session.ready`, `session.idle`, `session.deleted`,
  - `intake.confirmed`, `plan.approved`, `ticket.updated`, `merge.done`, `preview.refreshed`,
  - `publish.requested`, `check.completed`, `deploy.completed` (with environment and version),
  - `review.requested`, `review.completed`, `budget.exceeded`.
- **UI stream events** (server-sent events): message, question card, summary card, plan card, status, preview refresh, cost.
- **`libs/policy`:** the risk tier as a pure function. It takes `app.yaml` plus the connectors' data classification and returns tier 1, 2 or 3 with its reasons, following the table in §8.

## Out of scope

The services behind these contracts.

## Acceptance criteria

- [ ] Every contract has at least one valid and one invalid example, checked by `task contracts-check` in CI.
- [ ] CI regenerates the JSON Schema, OpenAPI and TypeScript files from the models, and any drift fails it.
- [ ] Tier function tests:
  - personal, non-sensitive and read-only gives tier 1,
  - shared beyond the author gives at least tier 2,
  - client data or any write gives tier 3,
  - unknown classification gives tier 3 (fail safe).
- [ ] ADR 0002, "Contracts and versioning", explains how to make a breaking change.

## Notes

- Keep schemas small, and add fields only when a step needs them.
- Until step 26 wires up Dataplex, the connectors' classification comes from a static file in each domain pack.
