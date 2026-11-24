# 03 · Local development stack

**Milestone:** M0 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 01, 02 · **Needs later:** 04 (sandbox GitHub org, for integration tests)

## Why

Engineers and code assistants must be able to run and test everything without cloud access. Architecture: §2, §9.

## Build

- **`task dev`:** a Docker Compose stack with the Firestore emulator, the Pub/Sub emulator, Valkey and a fake Trust Layer. Later steps add the services and a local workspace container.
- **Fake Trust Layer:** a small FastAPI app that follows the Trust Layer contract from step 04 (until then, an Anthropic Messages-compatible API). It:
  - returns scripted responses from fixtures,
  - records every call with its user, app and session IDs,
  - refuses calls that lack them,
  - can simulate budget and rate-limit errors.
- **`libs/tasks`:** one interface for enqueuing agent steps (payload, idempotency key, delay). It has a Cloud Tasks implementation and a local HTTP implementation. Cloud Tasks has no official emulator, so keep the interface thin.
- **`libs/github`:** a thin GitHub App client (installation tokens, repos, issues, pull requests, checks). Unit tests use a recorded-fixtures mode. Integration tests use the sandbox org from step 04.
- **IAP identity helper** in `libs/common`: verifies the IAP-signed JWT (signature, audience, issuer, expiry) and returns the user and their Okta groups. Locally, a small stand-in in front of the services signs a test JWT for a chosen seed user, and the helper trusts that local key only when `ENV=local`.
- **Seed data:** one builder, one Domain Owner, the `retail` domain, one draft app and a synthetic data sample.
- **`docs/dev.md`:** how to run, debug and reset the stack.

## Out of scope

Cloud resources and the real services.

## Acceptance criteria

- [ ] `task dev` brings the stack up in under 2 minutes on a laptop, and `task dev-down` removes it cleanly.
- [ ] One example integration test runs against the emulators in CI, using Compose services.
- [ ] The fake Trust Layer rejects a call without user and app IDs, as the real one will.
- [ ] Both `libs/tasks` implementations pass the same test suite.
- [ ] The IAP helper accepts a valid test token, and refuses an expired one, a wrong audience, and the local key outside `ENV=local`.

## Notes

- No real credentials in the stack. The fake GitHub mode must be the default for tests.
