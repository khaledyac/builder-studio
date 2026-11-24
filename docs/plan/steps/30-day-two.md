# 30 · Day two: updates, expiry, reopen and gallery

**Milestone:** M5 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 18, 22, 26

## Why

Apps stay current, nothing lives forever by accident, and good apps get reused. Architecture: §10, §12.

## Build

- **Template updates:**
  - a weekly `copier update` pull request across all app repos and both platform repos (their `agents` layer), so new best practices reach every repo,
  - patch updates auto-merge when green; anything else notifies the owner.
  - a minimum supported template version: `verify` fails when an app's Copier answers are older, so nobody can skip a security fix for long.
- **Expiry:**
  - a Cloud Scheduler job reads the registry and reminds the owner at 30, 7 and 1 days,
  - at expiry, the app is switched off (scaled to zero, invoker rights removed),
  - after a grace period, its deployments are removed,
  - renewal is done from the UI.
- **Idle drafts:** after N days, the repo is archived and its Lab deployment removed.
- **Reopen a live app:** a new session from `main`, then the same build and Publish path.
- **Gallery:**
  - the owner opts in,
  - "Start from this" copies the code, never the data access,
  - the copy keeps its Copier answers, reruns the intake for what changes, and is tiered again.

## Out of scope

Cross-company sharing.

## Acceptance criteria

- [ ] A template patch reaches every pilot app within a week, with no manual work.
- [ ] An app below the minimum template version fails `verify` until it merges the update pull request.
- [ ] An expired app is unreachable, and its owner was warned three times beforehand.
- [ ] A gallery copy has no data access until its own approval.
