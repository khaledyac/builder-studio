# 23 · Router and fast path

**Milestone:** M2 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 20

## Why

Small, safe changes appear in seconds, without the spec and tickets. Architecture: §4, §6.

## Build

- **Router:**
  - hard rules first: anything touching data or connectors, `app.yaml`, auth, dependencies, or adding a page goes to the full path,
  - then a Haiku 5.5 classification into fast, full or clarify, with a reason, parsed into a Pydantic model. An answer that doesn't validate goes to the full path.
- **Fast path:**
  1. one agent works on a `fast/<id>` branch in its own worktree,
  2. quick checks: ruff and pyright on the changed files, and the tests nearest the change,
  3. a size limit: 2 files at most, and no protected file,
  4. a priority merge into `build/<app>`, taking the merge lock in Valkey,
  5. a Conventional Commit, one line added to the spec's change log, and a preview refresh event.
- **Escalation:** if the change grows past the limit, the agent stops, explains why in plain words, and switches to the full path.
- **Undo:** "undo last change" in the chat reverts the last commit.
- **Clarify:** one question back, with a suggested answer.

## Out of scope

The full path (step 24).

## Acceptance criteria

- [ ] On a labelled set of 50 messages: router accuracy of 90% or more, and zero rule violations (a message touching data never takes the fast path).
- [ ] In hub-dev, "make the title bigger" shows in the preview in under 30 seconds (median).
- [ ] A fast change that grows past the limit stops and moves to the full path.
- [ ] Undo restores the previous preview.
