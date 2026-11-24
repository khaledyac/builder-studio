# 09 · Terraform: spoke module and the Retail spoke

**Milestone:** M1 · **Tag:** ready-for-agent · a human applies · **Size:** L · **Blocked by:** 06

## Why

Each domain gets two projects and keyless deploys from GitHub. Architecture: §2 (Spoke, Supply chain), §8, §12.

## Build

- **Module `spoke`,** in `builder-studio` at `infra/terraform/modules/spoke`:
  - a non-production project (Lab and Staging) and a production project,
  - budgets per project, labels, and log sinks to the hub's central bucket,
  - read access to the hub's Artifact Registry for the deploy service accounts.
- **Workload Identity Federation for GitHub Actions:**
  - a pool and an OIDC provider, restricted to the app repos' organisation,
  - one deploy service account per environment (lab, staging, production), each bound only to the matching GitHub `environment` claim.
- **Production:** no human role can write. A break-glass group is documented and disabled by default.
- **App edge, per environment:** an external Application Load Balancer with Cloud Armor, a wildcard certificate and IAP (Okta through Workforce Identity Federation, as in step 08). Apps accept traffic only from the load balancer. Never enable IAP directly on Cloud Run: that isn't generally available.
- **ADR 0006, "App exposure in spokes":** how a new app gets its route and its access rule without hand edits. Two options:
  - one backend per environment, with a serverless NEG URL mask (`<app>.lab.<domain>…`): IAP admits the domain's group, and each app checks its own audience from `app.yaml` (simplest),
  - one backend per app, so IAP enforces each app's audience, with a platform job that rebuilds the URL map from the registry.
- **Terraform state:** one bucket per domain, for the apps' infrastructure.
- **Instantiate for Retail:** `spoke-retail-nonprod` and `spoke-retail-prod`.

## Out of scope

The app-level modules (they live in `builder-kit`, step 10) and the tier gates (step 26).

## Acceptance criteria

- [ ] In the sandbox org, a GitHub Actions job with environment `lab` deploys a hello Cloud Run service to Lab and cannot touch Staging or Production.
- [ ] Nobody in the builders or Domain Owner groups has a write role in the production project (policy test).
- [ ] Budgets alert the Domain Owner at 50%, 90% and 100%.
- [ ] The hello service is reachable through the spoke's load balancer after an Okta sign-in, and its `run.app` URL refuses direct calls.
- [ ] ADR 0006 is decided, and a test shows a user outside an app's audience is refused.

## Notes

- Restrict the provider with an attribute condition on `repository_owner`, and each binding with the `environment` claim.
