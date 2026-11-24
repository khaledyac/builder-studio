# 20 · Agent runtime

**Milestone:** M2 · **Tag:** ready-for-agent · **Size:** L · **Blocked by:** 05, 13, 16

## Why

A shared, stateless agent service that drives each session's workspace. Architecture: §2 (Agents and state), §4, §9.

## Build

In `services/agent-service`:

- **Harness:** the one chosen in ADR 0003, used through `libs/harness`.
- **One agent step per request,** run by a Cloud Tasks HTTP target:
  1. load the conversation and plan (Firestore, Valkey),
  2. call the model through `libs/trustlayer` with the user, app and session IDs,
  3. run the tool calls,
  4. save, emit UI events, and enqueue the next step.
  - Each step has an idempotency key, so retries are safe.
- **Tools:**
  - the workspace API (run, read, write, git, preview),
  - GitHub issues and pull requests through the GitHub App,
  - "ask the builder", which sends a question card.
- **Models by role,** from config: Haiku 5.5 for routing and the fast path, Sonnet 5.5 for the lead and workers. Opus 5.5 only with an approval flag.
- **Budgets:** per session and per user per day. Going over emits `budget.exceeded` and gives the builder a clear message.
- **Prompt caching** wherever the harness supports it, which matters most for cost.

## Out of scope

The intake (step 22), the router and fast path (step 23) and the full path (step 24).

## Acceptance criteria

- [ ] A scripted conversation on the fake Trust Layer runs end to end, and survives an instance being killed mid-step: the retry resumes it.
- [ ] No step runs past the Cloud Run request timeout. Long work is split into steps.
- [ ] Every model call carries the user, app and session IDs (asserted by the fake Trust Layer).
- [ ] Once the budget is exceeded, no new model call is made, and the builder is told why.
