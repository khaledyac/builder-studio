# 28 · Eval runner and tracked reviews

**Milestone:** M4 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 22, 25, 26

## Why

Production approval rests on evidence: the evals pass and the required reviews are done. Architecture: §8, §10.

## Build

- **Eval runner** (`jobs/eval-runner`, a Cloud Run job):
  - runs on `deploy.completed` for Staging,
  - runs the app's eval cases (from the intake examples), plus benchmark prompts for the chat assistant and ADK agent types,
  - writes results to BigQuery and posts a summary to the pull request and the registry,
  - a threshold gates the Production approval.
- **Tracked reviews:**
  - DPO, legal and security reviews are GitHub Issues with labels, an owner and a target date, opened from the intake flags (step 22),
  - their status is projected to the UI,
  - Production can't be approved while a required review is open.

## Out of scope

Observability dashboards (step 29).

## Acceptance criteria

- [ ] A regression in an eval case blocks the Production approval, with a visible reason.
- [ ] While a required DPO review is open, the Production environment can't be approved.
- [ ] The builder sees which review is pending and who owns it.
