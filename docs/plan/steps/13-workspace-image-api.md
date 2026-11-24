# 13 · Workspace image and workspace API

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** L · **Blocked by:** 02, 03 · **Needs later:** 04 (sandbox GitHub org), 07 (image build and cold start on Cloud Run)

## Why

The workspace is the only place agent-written code runs. Architecture: §2 (Session workspace), §5, §12.

## Build

In `workspace/`:

- **Image:**
  - a non-root user, git, uv, Python 3.14, Task, Node LTS and Copier,
  - the kit at its latest version, with every layer's dependencies pre-installed (warm uv and npm caches),
  - the workspace API server,
  - rebuilt by the platform pipeline (step 07) every night and on each kit release.
- **Workspace API** (FastAPI, implementing `contracts/v1/workspace-api`):
  - runs commands with streamed output and timeouts, with no sudo,
  - reads and writes files inside the repo root only, blocking path traversal,
  - git operations including worktrees, one per worker,
  - starts and stops the preview by running the project's `task preview` (hot reload),
  - health and readiness endpoints.
- **Draft at New app:** while the builder answers the intake, render a local draft from the `agents`, `base` and domain pack layers under a temporary name (the domain comes with the session), install its dependencies and start the preview. Nothing is created on GitHub.
- **Bootstrap, on confirmation:**
  - apply the project type layer and render again with the final answers from `need.yml`, then hand over to step 18, which creates the repo,
  - set the git identity to the platform bot,
  - hold the short-lived GitHub token it receives in memory only.
- **Restore:** rebuild the working copy from the `build/<app>` branch.
- **Auth:** verify a Google ID token whose audience is this service. Allow only the agent service, session manager and preview proxy service accounts.
- **Proxy:** set `HTTPS_PROXY` for git, uv and npm, so every outbound call goes through the egress proxy.

## Out of scope

Creating and deleting workspaces (step 14), and the agents themselves (step 20).

## Acceptance criteria

- [ ] On the local stack: start a draft, see the branded app in the preview, confirm it with a fixture `need.yml`, edit a file, see the change served, then commit and push to the sandbox GitHub.
- [ ] Until the builder confirms, nothing exists on GitHub, and an abandoned draft disappears with its workspace.
- [ ] Tests show that path traversal, sudo and requests without a valid token are refused.
- [ ] Two worktrees run their tests in parallel without interfering.
- [ ] Cold start on Cloud Run, measured and recorded in `docs/dev.md`. Target: ready within 60 seconds, so it fits inside the intake.

## Notes

- Cloud Run's filesystem lives in memory. Size the repo, the caches and the worktrees within the 8 GiB.
