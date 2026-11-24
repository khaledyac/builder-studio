# 07 · Platform delivery pipeline

**Milestone:** M1 · **Tag:** ready-for-agent · a person approves production · **Size:** M · **Blocked by:** 01, 06

## Why

The platform's own services reach hub-dev and hub-prod the way apps do: through pipelines, with no deploys by hand and no human write access to production. Architecture: §2 (Supply chain), §8, §12.

## Build

In `builder-studio/.github/workflows/`, running on GitHub-hosted runners:

- **Identity:** a Workload Identity Federation provider that trusts this repo only, and one deploy service account per hub environment, added to the hub Terraform from step 06.
- **Images:** on every merge to `main`, build only what changed (path filters): each service, each job, the web UI and the workspace image. Scan them, then push them to Artifact Registry tagged with the commit SHA.
- **hub-dev:** deploy the changed Cloud Run services and jobs, then run smoke tests against their health endpoints.
- **hub-prod:** a release tag promotes the exact images tested in hub-dev, by digest and without rebuilding, after approval in a GitHub `hub-prod` environment.
- **Binary Authorization:** the pipeline attests each image it builds, and hub-prod accepts only attested images.
- **Terraform:** `plan` on every pull request that touches `infra/`, posted as a comment, and `apply` through the same environments after merge. From then on, nobody applies Terraform by hand.
- **Workspace image:** rebuilt every night, and whenever `builder-kit` publishes a release (its release workflow sends a dispatch to this repo).
- **Rollback:** one workflow run puts a service back on its previous image.

## Out of scope

The apps' delivery (steps 12 and 26) and the dashboards (step 29).

## Acceptance criteria

- [ ] A merge that changes one service deploys only that service to hub-dev, and its smoke test passes.
- [ ] A release tag sends the images tested in hub-dev to hub-prod after approval, and nobody can deploy to hub-prod by hand.
- [ ] A Terraform change shows its plan on the pull request and is applied after merge, without anyone running Terraform locally.
- [ ] One workflow run rolls a service back to its previous image.

## Notes

- Write one reusable workflow per kind of deploy (service, job) and call it with the component's name, rather than copying it per service.
- Until this step is done, a person applies the Terraform from steps 06, 08 and 09. After that, only the pipeline does.
