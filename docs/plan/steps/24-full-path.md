# 24 · Full path: spec, tickets, parallel workers and merge queue

**Milestone:** M3 · **Tag:** ready-for-agent · **Size:** L · **Blocked by:** 21, 23

## Why

Bigger asks are split into tickets that up to 3 agents build in parallel, with a preview that only moves on passing tests. Architecture: §4, §5, §6.

## Build

- **Lead agent (Sonnet 5.5):**
  - `to-spec` writes the spec to `docs/spec.md` in the app repo and to a GitHub Issue,
  - `to-tickets` splits it into vertical slices, as GitHub Issues with labels and "blocked by" links.
- **Plan card** in the UI: the plan in plain words. The builder approves it or asks for changes, and approval applies `ready-for-agent`.
- **`implement-spec`:**
  - up to 3 workers, each on `ticket/<n>` in its own worktree, building its ticket with `tdd`,
  - before finishing, a worker merges the latest build branch into its own.
- **Merge queue:**
  - a lock in Valkey allows one merge at a time,
  - a merge into `build/<app>` happens only when tests pass,
  - each merge triggers a preview refresh and a ticket status update in the UI.
- **Human tickets:** `ready-for-human` issues notify the platform team (on the channel agreed in step 04). A person does the work, and it merges the same way.
- **Recovery:** after a workspace restart, a run resumes from the issues and branches.

## Out of scope

Publish (step 25).

## Acceptance criteria

- [ ] The benchmark task "list page with filters and an export" completes as 3 tickets built in parallel, with all tests green and the preview updated after each merge.
- [ ] Under induced contention, two merges never run at once.
- [ ] Killing the workspace during a run loses at most the ticket step in progress.
