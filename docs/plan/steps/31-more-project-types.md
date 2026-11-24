# 31 · More project types

**Milestone:** M5 · **Tag:** ready-for-agent · **Size:** M per type · **Blocked by:** 10, 26

## Why

Builders need more than forms: dashboards, assistants, records apps and ADK agents. Architecture: §7.

## Build

One folder per type in `builder-kit/templates/types/`, with the same contract as `form-workflow`: a skeleton, tests, its `Taskfile.type.yml` for the standard tasks (`preview`, `test`, `lint`, `fmt`, `check`), an infra module in the kit's `terraform/modules/`, a variant of the golden app, and skills that tell the agent how to build it.

- **`dashboard`:** charts over read-only data.
- **`chat-assistant`:** chat through the Trust Layer, with guardrails and evals.
- **`records`:** Firestore or Cloud SQL, through the approved modules.
- **`adk-agent`:** an ADK agent deployed as the architecture describes, with evals.

Do them one at a time, in the order the pilot needs them.

## Out of scope

Types that need new GCP services. Those go through an architecture review first.

## Acceptance criteria

- [ ] Each type goes through the golden app job to Lab.
- [ ] The chat assistant and ADK agent types run their evals in Staging.
- [ ] The router and intake know each new type (eval set updated).
