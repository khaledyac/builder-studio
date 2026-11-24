# 01 · Platform monorepo and conventions

**Milestone:** M0 · **Tag:** ready-for-agent · **Size:** S · **Blocked by:** none

## Why

Every later step builds in this repo. Settle the layout, tooling and CI once, so each step stays small. Architecture: the whole document, especially §11 and §12.

## Build

- The `builder-studio` monorepo with the layout in `AGENTS.md`. `docs/` holds `architecture.md`, `adr/`, `plan/` and `dev.md`.
- **Python 3.14:** one uv workspace with one package per service and per lib, `requires-python = ">=3.14,<3.15"` and a `.python-version`. ruff, pyright and pytest target 3.14 and are configured once at the root.
- **Web:** a `web/` skeleton with Vite, React and TypeScript, plus Vitest and ESLint.
- **Taskfile** (`Taskfile.yml`, Task v3): `dev`, `dev-down`, `test`, `lint`, `fmt`, `contracts-check` and `tf-validate`. Placeholders are fine for tasks later steps fill in. `web/` and each service can add their own Taskfile, pulled in with `includes`.
- **pre-commit:** ruff, eslint, terraform fmt, gitleaks and a Conventional Commits message check.
- **CI for this repo** (`.github/workflows/ci.yml`): runs the same `task` commands as developers (lint, types, tests, Terraform fmt and validate), plus gitleaks, pip-audit and npm audit. GitHub-hosted runners, no cloud access.
- **`libs/common`:**
  - structured JSON logging with `user_id`, `app_id` and `session_id` fields,
  - an OpenTelemetry setup helper,
  - a settings base class on pydantic-settings that every service extends,
  - a FastAPI health router.
- `docs/adr/0000-template.md` and ADR 0001, "Monorepo and stack", recording the defaults in `AGENTS.md`.
- `CODEOWNERS` and a pull request template with the step number and an acceptance checklist.

## Out of scope

Any cloud resource or service logic.

## Acceptance criteria

- [ ] `task lint test` passes on a fresh clone with only uv, Task, Node and Docker installed.
- [ ] CI runs on every pull request, and a failure blocks the merge.
- [ ] A commit containing a fake secret is rejected by pre-commit and by CI.
- [ ] `libs/common` logging emits one JSON line per event, including the three ID fields when they are set (unit test).

## Notes

- Pin tool versions: `uv.lock`, `package-lock.json`, and a `mise.toml` for Python 3.14, uv, Task, Node and Terraform.
- Keep the root README short: what this is, how to run it, where the plan lives.
- Keep `.claude/skills/` and `docs/agents/` exactly as they shipped with the plan. They give every code assistant the same skills and tracker settings, and step 10 replaces them with the kit's `agents` layer.
