# 18 · Bootstrap: repo, registry draft and hello world in Lab

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 07, 11, 12, 14, 16, 17

## Why

Prove the whole path on day one, in the background, so the builder never waits. Architecture: §3, §6, §8.

## Build

Run when the intake is confirmed. For M1, run it on "New app" with a fixture `need.yml`.

1. **Template:** the workspace completes the draft it started at New app (step 13), with the project type layer and the final answers, and commits the baseline.
2. **Repo:** the GitHub App creates the app repo in the apps organisation, then sets:
   - branch protection on `main`, with checks required,
   - the `lab` environment (step 26 adds `staging` and `production`),
   - the labels `ready-for-agent`, `ready-for-human`, `tier-1`, `tier-2` and `tier-3`,
   - code owner review required on the protected paths, using the template's `CODEOWNERS`.
3. **Push:** the baseline goes to `main`, and a branch `build/<app>` is created.
4. **Registry:** a draft entry with owner, tier and expiry.
5. **Hello world:** a `chore: bootstrap` pull request from `build/<app>` to `main`. It is auto-merged when its checks pass (only the bootstrap PR is), which releases `v0.1.0` and deploys hello world to Lab.

Each sub-step is recorded, so the flow is idempotent and can resume after a failure.

## Out of scope

The intake (step 22). Until then, the fixture `need.yml` drives everything.

## Acceptance criteria

- [ ] Clicking "New app" ends with hello world live in Lab within 15 minutes, while the builder keeps working.
- [ ] Running bootstrap twice for the same app changes nothing.
- [ ] A test checks the repo settings against the policy: protection, environments, labels, CODEOWNERS.

## Notes

- `main` only ever changes through Publish. The bootstrap pull request is simply the first Publish.
