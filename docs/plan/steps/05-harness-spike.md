# 05 · Harness spike and ADR

**Milestone:** M0 · **Tag:** ready-for-agent · human decision at the end · **Size:** M · **Blocked by:** 02, 03 · **Needs later:** 04 (the real Trust Layer, for the final benchmark run)

## Why

The agent service needs a coding harness that:
- runs Anthropic models through the Trust Layer,
- loads skills,
- edits files and runs commands in the workspace,
- works with git worktrees.

This step decides which harness. Architecture: §2, §4, §14 (open point).

## Build

- **`libs/harness`:** the small interface the agent service will use. `run_step(session, messages, tools)` returns a stream of events. Tool calls follow the workspace API contract from step 02, and model calls go through `libs/trustlayer`. For the spike, a minimal stub of that contract runs the tools in a local container. The real workspace API is step 13.
- **`libs/trustlayer`:** the client that follows the Trust Layer contract. It always sends the user, app and session IDs, and supports streaming and prompt caching.
- **Adapter A, Google ADK:**
  - Claude through a custom model class that calls the Trust Layer,
  - skills loaded with `SkillToolset`,
  - tools mapped to the workspace API.
- **Adapter B:** one off-the-shelf coding harness, picked at kickoff (for example the Claude Agent SDK or OpenHands), wired to the same Trust Layer client and the same tools.
- **Benchmark** on a small FastAPI starter app written for the spike, close to the future `form-workflow` type, with 3 tasks run 5 times each:
  1. a small UI change,
  2. a list page with filters and tests,
  3. a read-only call to a stub connector, with tests.
- **Measures:** success rate, wall time, tokens and cost, tool calls, and failures that needed a human.
- **ADR 0003, "Agent harness":** the results table and the recommendation.

## Out of scope

The production agent service (step 20).

## Acceptance criteria

- [ ] Both adapters run the 3 tasks end to end against the local stack (the fake or dev Trust Layer) and the stub workspace.
- [ ] Both adapters run on Python 3.14. If a candidate can't, the ADR says so and how it would be isolated.
- [ ] The results table is in the ADR, with raw logs under `docs/adr/0003/`.
- [ ] The Platform Owner's decision is recorded in the ADR.

## Notes

- How well a harness handles skills, worktrees and Trust Layer routing counts as much as its raw success rate.
- Keep the interface thin, so the losing adapter can simply be deleted.
