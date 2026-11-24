# 14 · Session manager

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 07, 13

## Why

One workspace per session: created when the intake starts, deleted when idle, rebuilt from the branch. Architecture: §2, §5, §14.

## Build

In `services/session-manager`:

- **Create a workspace,** as one Cloud Run service per session through the Cloud Run Admin API:
  - max instances 1, and min instances 1 while the session is active,
  - instance-based billing, 4 vCPU and 8 GiB,
  - Direct VPC egress through the proxy, running as the workspace service account,
  - labels: domain, app, user, session,
  - internal ingress, with invoker rights only for the agent service, preview proxy and session manager service accounts.
- **Readiness:** poll until ready, then ask the workspace to start a draft (a new app, with the builder's domain) or to restore (an existing app).
- **GitHub tokens:** mint short-lived GitHub App installation tokens scoped to the app's repo, and refresh them before they expire.
- **Limits:**
  - open sessions per user (default 2),
  - a guard on the number of services per project (the quota is 1,000 per project and region),
  - a rate limiter on Admin API writes (180 per minute per project and region).
- **Idle reaper:** Cloud Scheduler calls it every 5 minutes, and it deletes workspaces idle for 30 minutes. Reopening the app restores from the branch.
- **Local driver:** behind the same interface, `task dev` starts the workspace as a local container instead of a Cloud Run service, so the whole flow runs on a laptop.
- **State:** session to workspace URL in Valkey, the session record in Firestore, and `session.*` events.

## Out of scope

The preview proxy (step 15) and the agent's token budget enforcement (step 20).

## Acceptance criteria

- [ ] On the local stack, creating a session starts a workspace container and returns its URL.
- [ ] In hub-dev, creating a session returns a ready workspace URL. Time to ready is recorded.
- [ ] A session idle for 30 minutes is deleted, and reopening it restores the build branch.
- [ ] Creation is idempotent per session ID, and a failed creation is cleaned up.
- [ ] A load test of 50 creations in 5 minutes passes without quota errors.

## Notes

- Cloud Run can briefly run more than the max of 1 during traffic spikes. The workspace must tolerate a second instance by staying stateless beyond the branch.
