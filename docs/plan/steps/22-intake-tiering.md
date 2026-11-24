# 22 · Intake agent and tiering

**Milestone:** M2 · **Tag:** ready-for-agent · usability test with builders · **Size:** M · **Blocked by:** 19, 20, 21

## Why

Turn a plain-language need into a spec-ready `need.yml`, a risk tier and the reviews it requires, while the workspace starts. Architecture: §3, §8, §12.

## Build

- **Start:** the intake begins when the builder clicks New app or picks a gallery app. The session, and so the workspace, starts at the same moment, and drafts the app locally while the builder answers (step 13).
- **Intake skill:**
  - 6–7 questions, each with a suggested answer: the problem, the users, 2–3 examples, the data (from the domain catalogue), read or write, who sees it, what it must not do,
  - follow-ups only where an answer is missing,
  - a plain summary for the builder to confirm.
  - Write it as an `intake` skill in `builder-kit/skills/` (step 21), starting from the forked `grilling` and `to-questionnaire`.
- **Outputs:**
  - `need.yml` and `app.yaml`, validated against the Pydantic contracts before the summary card is shown,
  - the tier from `libs/policy`, explained in plain words ("the Domain Owner approves production", "a DPO review is needed").
- **Screening:**
  - EU AI Act high-risk uses, from the list legal agreed in step 04 (for example hiring or rating employees), are blocked or routed to legal before any code is written,
  - personal data raises a DPO review, opened as a tracked task.
- **Examples:** the builder's 2–3 examples become acceptance test stubs and eval cases in the repo.
- **Gallery start:** when starting from a gallery app, the intake only asks what should change.
- **UI:** question cards with suggested-answer chips, and a summary card with "Looks right" and "Change something".

## Out of scope

The tracked reviews' full workflow (step 28).

## Acceptance criteria

- [ ] 10 scripted builder personas each produce a valid `need.yml` and `app.yaml`, with the expected tier from a table.
- [ ] An app idea for rating employees is flagged and routed to legal, and is never built silently.
- [ ] In a usability test with 5 builders, the median intake takes under 3 minutes (done by a person).

## Notes

- Hard rules in `libs/policy` always override what the model suggests.
