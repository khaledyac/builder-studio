# 26 · Policy, tier gates, Staging and Production

**Milestone:** M4 · **Tag:** ready-for-agent · **Size:** L · **Blocked by:** 09, 12, 17

## Why

Each app follows the path its risk tier allows, and nothing else reaches production. Architecture: §8, §12.

## Build

- **Policy as code** (OPA with Conftest, in `verify.yml`) on `app.yaml`:
  - only the domain's allowed connectors and the approved modules,
  - the tier from `libs/policy`,
  - the protected files.
- **Data classification** from Dataplex Universal Catalog tags on the connectors' datasets. It feeds the tier and replaces the static file from step 02.
- **`deploy.yml` v2:**
  - Lab for every tier. Tier 1 stops there.
  - Staging, then Production, for Tiers 2 and 3, as GitHub environments with required reviewers:
    - Tier 2: the Domain Owner,
    - Tier 3: an engineer and security, plus the DPO when the app uses personal data.
- **Binary Authorization:** the pipeline attests the image after verify and test, and the policy on every environment requires that attestation.
- **Registry gate** on every environment, with deploy status written back to the registry.
- **Re-tiering:** sharing an app beyond its author moves it to Tier 2, in the registry and the policy.

## Out of scope

Masked data (step 27), evals and tracked reviews (step 28).

## Acceptance criteria

- [ ] A Tier 1 app's merge deploys to Lab only, with no Staging or Production jobs.
- [ ] A Tier 2 app waits for the Domain Owner's approval in GitHub before Production.
- [ ] An image the pipeline didn't build is refused by Binary Authorization.
- [ ] Adding `clients-readonly` to `app.yaml` moves the app to Tier 3 on the next pull request.
