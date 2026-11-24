# Developer guide

## Prerequisites

uv, Task (v3), Node 24 and Docker. That's all a fresh clone needs: uv installs Python 3.14, and pre-commit installs Go to build gitleaks.

[mise](https://mise.jdx.dev) is optional. `mise install` gives you the exact versions in `mise.toml`, which is what CI uses.

## First time

```bash
task setup
```

This installs the Python packages (`uv sync`), the web packages (`npm ci`) and the git hooks.

## Commands

| Command | What it does |
|---|---|
| `task lint` | ruff, the ruff format check, pyright (strict), ESLint and the TypeScript check |
| `task test` | pytest for every workspace package, and Vitest for `web/` |
| `task fmt` | formats the Python code, and auto-fixes lint findings in the Python and web code |
| `task secrets` | proves the secret scanners catch a fake secret, then scans the current branch's history |
| `task audit` | pip-audit on the locked Python packages, and npm audit (high and critical) |
| `task web:dev` | the Vite dev server for the UI, with hot reload |
| `task web:build`, `task web:preview` | build the UI, and serve the build locally |
| `task dev`, `task dev-down` | start and stop the local stack (step 03) |
| `task contracts-check` | fails when the generated schemas drift from the contracts (step 02) |
| `task tf-validate` | Terraform fmt, validate and security scan (step 06) |

`task --list` shows them all.

## Layout

The top-level folders follow `AGENTS.md`. Each one arrives with the first step that needs it: `contracts/` in step 02, `infra/` in step 06, `workspace/` in step 13, `services/` from step 14, and `jobs/` in steps 25 and 28.

- **Python:** one uv workspace, with one package per lib, service and job (`libs/*`, `services/*`, `jobs/*`). To add one, create its folder with a `pyproject.toml`, and the workspace picks it up. Libraries share the `studio` namespace, so `libs/common` is imported as `studio.common` ([ADR 0001](adr/0001-monorepo-and-stack.md)).
- **Web:** the UI lives in `web/`, with its own `Taskfile.yml` that the root one includes as `web:`.
- **Repo tooling tests:** `tests/tooling/` tests the tooling itself. For now that's the secret-scanner self-test, which `task secrets` runs.

## Shared helpers in `libs/common`

Every service starts the same way:

```python
from fastapi import FastAPI

from studio.common.health import health_router
from studio.common.logs import configure_logging, log_context
from studio.common.settings import ServiceSettings
from studio.common.telemetry import configure_tracing


class Settings(ServiceSettings):
    service_name: str = "platform-api"


settings = Settings()
configure_logging(settings.log_level)
app = FastAPI()
configure_tracing(settings, app)
app.include_router(health_router(settings.service_name))

with log_context(user_id="u-1", app_id="a-1", session_id="s-1"):
    ...  # every log line in here carries the three IDs
```

- **Logging:** one JSON line per event, with `time`, `severity`, `message` and `logger`. It also includes `user_id`, `app_id` and `session_id` when they're set, either by `log_context` or on one call with `extra=`.
- **Settings:** read from environment variables: `SERVICE_NAME`, `ENV` (`local`, `dev` or `prod`) and `LOG_LEVEL`. Secrets come from Secret Manager, never from settings.
- **Tracing:** when `OTEL_EXPORTER_OTLP_ENDPOINT` holds a collector's base URL, spans go to its `/v1/traces`. When it's unset, nothing is exported. The service's own health check isn't traced.
- **Health:** `GET /health`. Not `/healthz`, because Cloud Run reserves paths that end in `z`.

## Git hooks

`task setup` installs them. On each commit they run ruff and ESLint, terraform fmt (through Docker, on Terraform files), and gitleaks on the staged changes. They also check that the message follows [Conventional Commits](https://www.conventionalcommits.org). The first commit takes about a minute, while pre-commit builds gitleaks.

## CI

`.github/workflows/ci.yml` runs on every pull request and on `main`, using the tool versions in `mise.toml`:

- **checks:** `task lint`, `task test`, `task contracts-check` and `task tf-validate`.
- **secret scan:** `task secrets`. It covers every commit reachable from the branch under test, not other branches.
- **dependency audit:** `task audit`.
- **ci:** passes only when the others pass. Make it a required status check in the ruleset for `main`. Until then, a red CI doesn't block a merge.

If the secret scan finds a real secret, rotate it first. Then, if it can't be removed from history, add the finding's fingerprint (printed by gitleaks) to a `.gitleaksignore` file at the root.
