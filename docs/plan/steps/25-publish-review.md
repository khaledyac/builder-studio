# 25 · Publish, review runner and status

**Milestone:** M4 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 17, 21, 24

## Why

Publish is the only way out, and every pull request gets a separate review. Architecture: §3, §8.

## Build

- **Publish** (Platform API and UI): opens a pull request from `build/<app>` to `main`. Its body uses the pr template: summary, evidence, merge danger, tier.
- **Review runner** (`jobs/review-runner`, a Cloud Run job):
  - started by pull request events from Pub/Sub,
  - runs `code-review` (Standards and Spec) with Sonnet 5.5 through the Trust Layer,
  - posts a GitHub check run with its findings,
  - is a required check on `main`.
- **Fixing:** agents fix failing checks on the build branch when the builder asks. Lint failures are fixed automatically.
- **Stepper** in the UI: checks, Lab, Staging, approval, live. It is driven by the statuses projected in step 17.
- **Safety:** Publish is blocked while a fast-path or ticket merge is in progress.

## Out of scope

The tier gates and the Staging and Production environments (step 26).

## Acceptance criteria

- [ ] A pull request with an injected deviation from the spec gets a failing review check with a clear finding.
- [ ] The builder sees each status change within 10 seconds.
- [ ] Publish can't start during a merge.
