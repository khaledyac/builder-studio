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
| `task fmt` | formats and auto-fixes the Python and web code |
| `task secrets` | proves the secret scanners catch a fake secret, then scans the whole git history |
| `task audit` | pip-audit on the locked Python packages, and npm audit (high and critical) |
| `task dev`, `task dev-down` | start and stop the local stack (step 03) |
| `task contracts-check` | fails when the generated schemas drift from the contracts (step 02) |
| `task tf-validate` | Terraform fmt, validate and security scan (step 06) |

`task --list` shows them all. `task web:build` builds the UI.

## Layout

The uv workspace has one package per lib, service and job: `libs/*`, `services/*` and `jobs/*`. To add one, create its folder with a `pyproject.toml`, and the workspace picks it up. Libraries share the `studio` namespace, so `libs/common` is imported as `studio.common` ([ADR 0001](adr/0001-monorepo-and-stack.md)).

The web UI lives in `web/` and has its own `Taskfile.yml`, which the root one includes as `web:`.

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

- **Logging:** one JSON line per event, with `time`, `severity`, `message`, `logger`, and `user_id`, `app_id` and `session_id` when they're set.
- **Settings:** read from environment variables: `SERVICE_NAME`, `ENV` (`local`, `dev` or `prod`), `LOG_LEVEL` and `OTEL_EXPORTER_OTLP_ENDPOINT`. Secrets come from Secret Manager, never from settings.
- **Tracing:** spans go to the OTLP endpoint when one is set. Health checks aren't traced.
- **Health:** `GET /health`. Not `/healthz`, because Cloud Run reserves paths that end in `z`.

## Git hooks

`task setup` installs them. On each commit they run ruff, ESLint, terraform fmt (through Docker, on `.tf` files only), and gitleaks on the staged changes. They also check that the message follows [Conventional Commits](https://www.conventionalcommits.org). The first commit takes about a minute, while pre-commit builds gitleaks.

## CI

`.github/workflows/ci.yml` runs on every pull request and on `main`, using the tool versions in `mise.toml`:

- **checks:** `task lint`, `task test`, `task contracts-check` and `task tf-validate`.
- **secret scan:** `task secrets`, over the whole history.
- **dependency audit:** `task audit`.
- **ci:** passes only when the others pass. It's the status check that the branch rules for `main` require.
