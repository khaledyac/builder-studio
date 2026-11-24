# 10 · Template kit: builder-kit, layers and golden app

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** L · **Blocked by:** 02 · **Needs later:** 05 (ADR 0003, for the agent hooks' format), 09 (ADR 0006, for the app's ingress and access check)

## Why

Every repo starts from the same tested foundation with the rules already in place, and keeps receiving the platform's best practices through `copier update`. Architecture: §7, §12, and the Template board of the deck.

## Build

- **Repo `builder-kit`,** the second platform repo. It holds everything the app repos use:

  ```
  copier.yml           picks the layer to apply
  templates/agents/    skills and tracker settings
  templates/base/      best practices every app gets
  templates/types/     one folder per project type
  templates/packs/     one folder per domain
  skills/              upstream copy now, adapted in step 21
  .github/workflows/   shared workflows (step 12)
  terraform/modules/   approved app modules
  tests/               conformance tests, golden app job
  CODEOWNERS           each champion owns their pack
  ```

- **Layers in one repo:** the root `copier.yml` picks the layer from a `template` answer, through a templated `_subdirectory`, and saves each layer's answers to its own `.copier-answers.<layer>.yml`, so each layer updates on its own.
  - Each file belongs to exactly one layer, so updates never conflict.
  - Layers extend each other through includes: the base `Taskfile.yml` includes the type's `Taskfile.type.yml`, and `AGENTS.md` links to `docs/agents/*.md`.
- **Releases:** semantic-release tags `vX.Y.Z` from the commit messages, and moves the major tag (`vX`) that apps pin. A release triggers the golden app job and the workspace image rebuild (step 07).
- **`agents` layer,** applied to every repo:
  - the skills, rendered from `skills/` into `.claude/skills/`, in one of two flavours: `upstream`, exactly as published, for the platform team's code assistants; or `platform`, adapted in step 21 for the platform's agents (until then, apps get `upstream`),
  - the tracker settings in `docs/agents/`: GitHub Issues, the triage labels and the domain docs layout, so no setup command is ever needed,
  - app repos get it as their first layer, and both platform repos apply it with `copier copy --data template=agents gh:<org>/builder-kit .`. In `builder-studio`, this replaces the copy that shipped with the plan.
- **`base` layer:** the best practices every app repo gets:
  - **Agent rules:** `AGENTS.md.jinja` (KISS, DRY and SOLID kept light; the `ui/`, `services/`, `data/` and `auth/` structure; the files never to edit; models only through the Trust Layer client; Conventional Commits), and agent hooks in the format of the harness chosen in ADR 0003 (format and lint after each edit, block edits to protected files).
  - **Python and tooling:** a uv project on Python 3.14; `pyproject.toml` with ruff (complexity 10 or less, 40 statements or less), pyright, and pytest with coverage of at least 70%; pre-commit with gitleaks; and a `Taskfile.yml` with the standard tasks every project type implements: `preview`, `test`, `lint`, `fmt`, and `check` (lint, types and tests together).
  - **Pydantic:** `src/app/settings.py` on pydantic-settings, and Pydantic models for `app.yaml`, form inputs and connector responses.
  - **Secure defaults:** `src/app/auth/` (IAP JWT check), CSRF protection for forms, security headers, structured logging and OpenTelemetry, and a Dockerfile on a pinned Python 3.14 slim image that runs as a non-root user.
  - **Delivery:** thin workflow callers pinned to `builder-kit@v1` (step 12), a `CODEOWNERS` file for the protected paths, and a pull request template.
  - **App skeleton:** `src/app/data/gateway.py` (a connector client and a Trust Layer client stub), `tests/`, `app.yaml` rendered from `need.yml`, a protected-files manifest, and the brand tokens as CSS variables.
- **`packs/example`:** a domain pack with fake connectors, so this step doesn't wait for step 11.
- **`types/form-workflow`:**
  - FastAPI with Jinja2 and HTMX pages (the request-form-and-list example from the deck),
  - its `Taskfile.type.yml`, including `preview` with hot reload,
  - `infra/` using the kit's approved Cloud Run module from `terraform/modules/`: ingress from the spoke's load balancer only, wired as ADR 0006 decides (step 09).
- **ADR 0005, "Builders' app stack":** why FastAPI, Jinja2 and HTMX for generated apps.
- **ADR 0007, "One kit repo":** why one `builder-kit` instead of one repo per template, and how its layers share one version.
- **Golden app job,** run nightly and on every kit release:
  - generate an app from the agents, base, example pack and form-workflow layers with a fixture `need.yml`,
  - run `task check` and build its image,
  - push it to a `golden-app` repo in the sandbox organisation, overwriting it, so the shared workflows run on a real app repo,
  - deploy it to a test Lab once step 12 exists.

## Out of scope

The Retail pack (step 11), the shared workflows (step 12), adapting the skills (step 21) and the other project types (step 31).

## Acceptance criteria

- [ ] `copier copy` of the agents, base, example pack and form-workflow layers with the fixture produces a repo where `task check` passes, and `task preview` serves a branded hello page.
- [ ] A conformance test checks a generated repo against every best practice listed above (files present, settings on, versions pinned).
- [ ] After a kit change, `copier update` of one layer changes only that layer's files, with a clean, reviewable diff.
- [ ] `builder-studio` gets its skills and tracker settings through the `agents` layer, and a kit release updates them with one pull request.
- [ ] A local script detects a change to any protected file (step 12 later turns it into a CI check).
- [ ] With the kit and its dependencies in the workspace image, applying the layers takes under 10 seconds.

## Notes

- Generated workflow files have no `.jinja` suffix, so GitHub expressions survive Copier untouched.
- The `upstream` flavour keeps the skills exactly as published, so they keep using Claude Code's subagents for parallel work.
