# Builder Studio

An internal vibe coding platform. Business users ("AI builders") describe an app in plain language. Agents build it in an isolated workspace while the builder watches a live preview. Publishing opens a pull request, and GitHub deploys the app according to its risk tier.

## Run it

You need [uv](https://docs.astral.sh/uv/), [Task](https://taskfile.dev), [Node](https://nodejs.org) 24 and [Docker](https://www.docker.com/).

```bash
task setup
```

```bash
task lint test
```

`task setup` installs the dependencies and the git hooks. `task lint test` runs the lint, type and test checks from CI. `task --list` shows every command, and [docs/dev.md](docs/dev.md) explains them, including the secret scan and the dependency audit that CI also runs.

## Where things are

- **Plan:** [docs/plan/README.md](docs/plan/README.md). The platform is built one step at a time.
- **Architecture:** [docs/architecture.md](docs/architecture.md).
- **Rules for code assistants:** [AGENTS.md](AGENTS.md).
- **Decisions:** [docs/adr/](docs/adr/).

## Licence

All rights reserved. See [LICENSE](LICENSE).
