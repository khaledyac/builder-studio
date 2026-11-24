# 0001 · Monorepo and stack

- **Status:** accepted
- **Date:** 2026-11-24
- **Step:** 01

## Context

Every later step builds in this repo. Settling the layout, tooling and CI once keeps each step small. `AGENTS.md` sets the defaults. This ADR records them, and the choices step 01 had to make on top of them.

## Decision

From `AGENTS.md`:

- **One platform monorepo,** `builder-studio`. Everything the app repos use lives in `builder-kit` (step 10).
- **Python 3.14,** the standard build, in one uv workspace, with FastAPI, Pydantic v2, pydantic-settings, pytest, ruff and pyright.
- **Task** runs every command, locally and in CI. There's no Makefile.
- **React, TypeScript and Vite** for `web/`, with Vitest and ESLint.
- **Terraform, GitHub Actions** and Conventional Commits.

Made in step 01:

- **The `studio` namespace for libs:** `studio.common` now, and later `studio.github`, `studio.tasks` and so on. Short top-level names like `github` and `tasks` would clash with third-party packages.
- **Pinned versions:** `uv.lock`, `package-lock.json`, `.python-version` and `mise.toml`. CI installs the `mise.toml` versions with mise. Locally, mise is optional.
- **Strict checks:** ruff enforces complexity under 10 and under 40 statements per function, as `AGENTS.md` asks. pyright runs in strict mode. Ruff formats Python only, so the Markdown shipped with the plan stays untouched.
- **gitleaks through pre-commit:** pre-commit builds gitleaks, and installs Go first if it's missing, so developers install nothing extra. CI runs the same hook definitions (`task secrets`), after a self-test that proves a fake secret is caught.
- **terraform fmt through Docker** in the commit hook, so Terraform isn't one more prerequisite.
- **`/health`, not `/healthz`,** because Cloud Run reserves paths that end in `z`.
- **One `ci` gate job** that the branch rules require, so adding a CI job never means editing the rules.

## Consequences

- A fresh clone needs only uv, Task, Node and Docker.
- The first commit, or the first `task secrets`, takes about a minute while gitleaks builds. After that it's cached.
- Upgrading a tool is an explicit change to a lockfile or `mise.toml`, reviewed like any other.
