# 29 · Observability and FinOps

**Milestone:** M5 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 06, 20

## Why

One view across the hub and the spokes, and the cost of every session, app and user. Architecture: §2 (Observability and FinOps), §9, §13.

## Build

- **Signals:**
  - log sinks from the hub and the spokes to a central bucket with Log Analytics,
  - OpenTelemetry traces from the services and from generated apps (through the base template) to Cloud Trace,
  - Error Reporting.
- **Dashboards and alerts** (Cloud Monitoring):
  - session start time and workspace failures,
  - agent step errors and Trust Layer errors,
  - merge queue wait and deploy failures,
  - SLOs for the UI and the API.
- **FinOps:**
  - the billing export to BigQuery,
  - Trust Layer usage ingested into BigQuery (tokens and cost by user, app and session),
  - Looker Studio dashboards by domain, app and user,
  - budgets with alerts,
  - the cost per session shown in the UI.

## Out of scope

Security monitoring beyond Security Command Center (step 32).

## Acceptance criteria

- [ ] The cost per session shown in the UI is within 10% of the next day's billing export.
- [ ] An alert fires when the 95th percentile of workspace creation time goes over target.
- [ ] One dashboard answers who spends what, on which app, in which domain.
