# 12 · Shared GitHub workflows

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 09, 10

## Why

Each app's workflow only calls shared workflows, so a pipeline fix is made once. Architecture: §2 (GitHub, Supply chain), §7, §8.

## Build

In `builder-kit/.github/workflows/`, released with the kit's version tags. App repos call them pinned to the major tag, such as `@v1`. The kit's own CI files start with `kit-`, so the two never mix:

- **`verify.yml`:**
  - `task lint` (ruff and pyright) and a Conventional Commits check,
  - gitleaks and pip-audit,
  - the protected-files check against the template's manifest,
  - `app.yaml` schema validation and tier computation, using the `libs/policy` CLI or container; the tier becomes a job output.
- **`test.yml`:** `task test`, with the coverage threshold.
- **`release.yml`:** on merge to main, semantic release writes the version, changelog and tag, then calls deploy as a reusable workflow, not a listener.
- **`deploy.yml`:**
  - reusable, and also runnable by hand with a version for rollbacks,
  - builds the image and pushes it to Artifact Registry,
  - runs Terraform plan and apply in the app's `infra/` with the environment's service account through Workload Identity Federation,
  - v1 deploys to Lab only; step 26 adds Staging and Production.
- **`template-update.yml`:** a weekly `copier update` that opens a pull request.
- **Thin callers** in the base template, pinned by tag.

## Out of scope

The registry gate, Binary Authorization and the tier-based environments (step 26). The review check (step 25).

## Acceptance criteria

- [ ] In the sandbox org, a generated app goes from pull request to Lab automatically on merge, with no stored cloud keys.
- [ ] A pull request that changes `AGENTS.md` fails verify.
- [ ] Running deploy by hand with an earlier version redeploys that version.

## Notes

- A release made with the default `GITHUB_TOKEN` doesn't trigger other workflows. That is why release calls deploy directly.
