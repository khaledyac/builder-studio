# 27 · Staging data and connectors

**Milestone:** M4 · **Tag:** ready-for-agent · data owners sign off · **Size:** L · **Blocked by:** 09, 11

## Why

Apps read real domain data only through read-only connectors, and Staging sees masked data only. Architecture: §2 (Spoke), §8, §12.

## Build

- **Connector gateway** (Apigee or the corporate gateway, as decided in step 04): read-only domain connectors per environment.
  - Lab: non-sensitive data only.
  - Staging: masked datasets.
  - Production: real data, within the app's approved scope.
  - Callers authenticate with the app's service account.
- **Masking:** Sensitive Data Protection de-identification jobs write masked copies of the Retail datasets to BigQuery in the non-production project, on a schedule.
- **Connector client** in the base template (`src/app/data/gateway.py`): retries, timeouts, and typed responses that match `connectors.yaml`.
- The workspace keeps using synthetic data from Cloud Storage. Nothing changes there.

## Out of scope

New domains beyond Retail.

## Acceptance criteria

- [ ] Tests show a Lab app can't read client data, and a Staging app reads masked data only.
- [ ] The data owners sign off the masking rules.
- [ ] The gateway logs every call with the app ID and the environment.
