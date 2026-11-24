# 06 · Terraform: hub foundations

**Milestone:** M1 · **Tag:** ready-for-agent · a human applies · **Size:** L · **Blocked by:** 04

## Why

Everything in the hub runs on these resources. Architecture: §2 (Hub, Supply chain, Security), §11, §12.

## Build

In `infra/terraform/`, with `modules/` and `envs/hub-dev` and `envs/hub-prod`:

- **State:** remote, in a versioned Cloud Storage bucket per environment.
- **Projects:** hub-dev and hub-prod, with their enabled APIs. Use the company's project process if there is one.
- **Network:**
  - a VPC with a subnet for Cloud Run Direct VPC egress, and Private Google Access,
  - Secure Web Proxy in explicit proxy mode, with an allowlist: Trust Layer endpoints, Artifact Registry, `github.com`, `api.github.com`, `codeload.github.com`, `objects.githubusercontent.com`,
  - a VPC firewall rule that denies every other egress from the workspace subnet, so nothing can bypass the proxy.
  - If step 04 found a corporate egress proxy, use it instead of Secure Web Proxy.
- **Artifact Registry:** a Docker repository, plus remote repositories for PyPI and npm (the package mirror).
- **Data and messaging:**
  - Firestore in Native mode,
  - Memorystore for Valkey over private connectivity,
  - Pub/Sub topics from `contracts/generated/events`,
  - Cloud Tasks queues (`agent-steps`, with rate limits),
  - Cloud Scheduler (its jobs are added by later steps).
- **Secret Manager:** create the secrets empty; a human sets the values.
- **Service accounts,** one per component, with least-privilege IAM: platform-api, agent-service, session-manager, preview-proxy, registry-api, webhook-receiver, review-runner, eval-runner, workspace.
- **BigQuery** dataset for FinOps and evals, and a central log bucket.
- **Labels** on everything: domain, app, env, component.
- **Folder-level Organization Policies** as agreed: EU regions only, no service account keys, no public IPs except the load balancer, uniform bucket access.
- **VPC Service Controls** in dry-run mode. Step 32 enforces it.

## Out of scope

The load balancer and IAP (step 08), the spokes (step 09) and the services themselves.

## Acceptance criteria

- [ ] `terraform plan` for hub-dev is clean, and a human applies it.
- [ ] `infra/README.md` has a table of each service account and its roles, and nothing has more than it needs.
- [ ] A test Cloud Run service with Direct VPC egress reaches the Trust Layer dev endpoint and GitHub through the proxy, and is blocked from any other site.
- [ ] A Terraform security scan (trivy config or checkov) runs in CI with no high findings.

## Notes

- Write everything as reusable modules. The spoke step and the hub-prod environment reuse them.
