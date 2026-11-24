# 11 · Template: Retail domain pack

**Milestone:** M1 · **Tag:** ready-for-agent · domain champion signs off · **Size:** M · **Blocked by:** 10

## Why

The domain pack gives the agent the domain's knowledge and data, without real data in the workspace. Architecture: §7, §12.

## Build

- **Pack format** (folder `templates/packs/<domain>/` in `builder-kit`, owned by the domain champion through CODEOWNERS):
  - `skills/`: one `SKILL.md` per data area, with wording and display rules,
  - `connectors.yaml`: connector IDs, fields, data classification and access mode,
  - synthetic data: a seeded generator and fixtures that match the connector schemas,
  - `gallery/`: empty for now.
- **Retail pack v1:**
  - connectors `stores-readonly` and `products-readonly` (internal, non-sensitive) and `clients-readonly` (client data),
  - synthetic data for all three,
  - a `retail-data` skill, starting from the deck's Template board.
- **Publishing:** each pack version uploads its synthetic data to the hub's Cloud Storage bucket.

## Out of scope

The real connectors and masking (step 27).

## Acceptance criteria

- [ ] The domain champion signs off the field names, the wording rules and how realistic the synthetic data is.
- [ ] The synthetic data validates against `connectors.yaml`, and contains no real names, emails or IDs (a Sensitive Data Protection scan or a pattern test in CI).
- [ ] With `libs/policy`:
  - an app using `stores-readonly` gets tier 1 or 2, depending on its audience,
  - adding `clients-readonly` makes it tier 3.

## Notes

- Keep `AGENTS.md` short. Domain detail belongs in the pack's skills, loaded only when relevant.
