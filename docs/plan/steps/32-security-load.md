# 32 · Security hardening and load test

**Milestone:** M5 · **Tag:** ready-for-agent · security team signs off · **Size:** L · **Blocked by:** 27, 28, 29

## Why

Agents run code they just wrote, on data that matters. Prove the guardrails hold before the pilot. Architecture: §12, §14.

## Build

- **Threat model** (STRIDE) of the workspace and the agent paths.
- **Prompt-injection tests:** malicious content in the repo, in connector data and in issues, checked against what the tools are allowed to do.
- **Egress tests:** the workspace can't reach anything outside the allowlist, the spokes, or another project's metadata server.
- **Perimeter:** VPC Service Controls move from dry-run to enforced. Review the Organization Policies and triage the Security Command Center findings.
- **Load test:**
  - 100 sessions in 10 minutes (Admin API quota, number of services, Trust Layer rate limits),
  - 300 agent loops running at once.
- **Runbooks:** workspace stuck, Trust Layer outage, GitHub outage, budget exceeded, production break-glass.
- **External penetration test** (done by people).

## Out of scope

Features.

## Acceptance criteria

- [ ] No high or critical finding left open.
- [ ] The load test meets its targets without quota errors, and the limits are documented.
- [ ] The on-call team has reviewed the runbooks.
