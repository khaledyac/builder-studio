# 16 · Platform API

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** L · **Blocked by:** 02, 03 · **Needs later:** 07 (to deploy)

## Why

The single backend for the UI: sessions, messages, status and Publish. Architecture: §2 (Experience and APIs), §3, §9.

## Build

In `services/platform-api`, a FastAPI service behind IAP:

- **Identity:** verify the IAP JWT with the `libs/common` helper (step 03) and map Okta groups to roles (builder, Domain Owner, reviewer, Platform Owner).
- **Endpoints:**
  - `me`,
  - `apps`: mine, plus a read-only gallery list,
  - `sessions`: create (calls the session manager), get, close,
  - `messages`: a builder message enqueues an agent step through `libs/tasks`,
  - `stream`: server-sent events of UI events, fanned out through Valkey.
  - Publish (step 25) and costs (step 29) come later.
- **Storage:** Firestore models for apps, sessions and conversations. Valkey for live state and fan-out.
- **Safety:** idempotency keys on every POST, and rate limits per user.
- Every log line and trace carries the user, app and session IDs.

## Out of scope

The agent logic (steps 20 to 24) and bootstrap (step 18).

## Acceptance criteria

- [ ] Contract tests against the OpenAPI in `contracts/` pass.
- [ ] With a fake agent, a builder creates a session and receives streamed events.
- [ ] A builder can only read their own sessions (authorisation tests).
- [ ] Logs and traces carry the three IDs (test).

## Notes

- Server-sent events through the load balancer: send heartbeats, and let the client reconnect with `Last-Event-ID`.
