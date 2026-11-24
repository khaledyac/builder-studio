# 21 · Skills fork

**Milestone:** M2, can start once `builder-kit` exists · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 10 · **Needs later:** 05 (to run the evals with the chosen harness)

## Why

The agents' way of working (spec, tickets, TDD, review) comes from a pinned, adapted fork of [mattpocock/skills](https://github.com/mattpocock/skills). Architecture: §4, §7, §14.

## Build

In `builder-kit/skills/`, keeping the MIT licence and attribution:

- **Start** from the upstream copy at commit `abeeaf9` (the one that ships with the plan), keeping only what the platform uses: `grilling`, `to-questionnaire` (the intake), `to-spec`, `to-tickets`, `triage`, `implement-spec`, `tdd`, `code-review` and `pr`.
- **Adapt,** as the `platform` flavour (the `upstream` flavour stays exactly as published, for the platform team's code assistants):
  - labels: `ready-for-agent` and `ready-for-human`; GitHub Issues as the tracker,
  - `implement-spec`: the workspace's worktrees and the merge queue, with no Claude Code-specific features,
  - `code-review`: reads the repo's `AGENTS.md` as its Standards and the spec as its Spec,
  - the `pr` template: maps "Merge Danger" to the risk tier,
  - every output meant for builders is in plain language.
- **Triggering:** the platform triggers the workflow skills (`to-questionnaire`, `to-spec`, `to-tickets`, `triage`, `implement-spec`, `code-review`, `pr`), never the model on its own. `grilling` and `tdd` stay callable by the agents that use them, because `implement-spec` loads `tdd` for every ticket.
- **Release:** with the kit's version. The `agents` layer (step 10) renders them into `.claude/skills/` in every repo, as protected files.
- **Platform skills:** the platform's own skills live here too, starting with `intake` (step 22).
- **Evals:** a set per skill (inputs and expected outputs), run in CI with the chosen harness.

## Out of scope

The orchestration that calls the skills (step 24).

## Acceptance criteria

- [ ] Each adapted skill passes its eval set with the chosen harness.
- [ ] The licence and attribution are kept.
- [ ] A skills change reaches every app repo and both platform repos through the normal Copier update.
