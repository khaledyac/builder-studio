# 17 · Registry API and webhook receiver

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 02, 03 · **Needs later:** 07 (to deploy)

## Why

No registry entry, no deployment. And GitHub's events have to reach the UI. Architecture: §2, §8, §10.

## Build

- **`services/registry-api`:**
  - create a draft, update tier, status and expiry, get,
  - `check`, for deploy workflows: called with a Google ID token obtained through Workload Identity Federation, it returns allow or deny with a reason.
- **`services/webhook-receiver`:**
  - verifies GitHub's HMAC signature, drops duplicates by delivery ID,
  - turns events into CloudEvents and publishes them to Pub/Sub.
- **Projection worker:** a Pub/Sub push subscriber that updates app and session status in Firestore (pull requests, checks, deploys, reviews) for the UI.

## Out of scope

Expiry jobs (step 30) and the tier gates (step 26).

## Acceptance criteria

- [ ] `check` allows a registered app and refuses an unknown or expired one, with a reason (contract tests). Deploy workflows start calling it in step 26.
- [ ] Unsigned or replayed webhooks are rejected, and duplicates are ignored.
- [ ] Replaying recorded GitHub events (pull request opened, check completed, deployment finished) updates Firestore within seconds.

## Notes

- Keep the registry API small. It is a gate, not a CMDB.
