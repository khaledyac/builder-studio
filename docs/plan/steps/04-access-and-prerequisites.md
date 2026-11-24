# 04 · Access and prerequisites

**Milestone:** M0 · **Tag:** ready-for-human · **Size:** M · **Blocked by:** none (start on day one)

## Why

The cloud and integration steps stall without these. Most of them need approvals from other teams, so start now. Architecture: §2, §9, §14.

## To obtain

- [ ] **Google Cloud:**
  - a folder for the platform and a linked billing account,
  - the right to create projects (hub-dev, hub-prod, and spoke projects per domain),
  - the owner of the Organization Policies.
- [ ] **Okta:**
  - an application for Builder Studio,
  - a Workforce Identity Federation pool and provider in Google Cloud,
  - groups for builders, Domain Owners, reviewers and Platform Owners.
- [ ] **DNS:** the hostname for the UI and the preview, and the certificate approach.
- [ ] **GitHub:**
  - the organisation for app repos, plus a sandbox organisation for tests,
  - a registered GitHub App with permissions for contents, pull requests, issues, checks, workflows, administration (repo creation, environments, branch protection) and webhooks,
  - the runner policy.
- [ ] **Trust Layer:**
  - dev and prod endpoints,
  - the API contract: request and response format, headers for user, app and session IDs, streaming, error codes, budgets, rate limits,
  - the allowed models: Sonnet 5.5 and Haiku 5.5, plus Opus 5.5 on approval.
- [ ] **Security, DPO and legal:**
  - an architecture walkthrough,
  - agreement on the tier rules, the review turnaround times, the AI Act screening list and the GDPR register fields.
- [ ] **Retail domain:**
  - a domain champion who owns the Retail pack,
  - the connector specs,
  - the data owners for masking.
- [ ] **Connector gateway:** Apigee or the corporate gateway.
- [ ] **Egress:** does a corporate egress proxy exist that workspaces can use? Reusing it saves about $900 a month.
- [ ] **Budget:** approval for the pilot, about $3,600 a month at list prices.

## Deliverables

- `docs/prerequisites.md`, listing each item with its owner, status and date.
- The Trust Layer contract, stored in `contracts/trustlayer/`.

## Done when

Every item is granted or has a date, and the Trust Layer contract is in the repo.
