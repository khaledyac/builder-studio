# 08 · Terraform: edge and identity

**Milestone:** M1 · **Tag:** ready-for-agent · a human applies · **Size:** M · **Blocked by:** 03, 06

## Why

Builders get a single entry point: load balancer, WAF, and IAP signing them in through Okta. Architecture: §2 (Edge and identity), §9.

## Build

- **Load balancer:** a global external Application Load Balancer with serverless NEGs for the web UI, the platform API, the preview proxy and the webhook receiver.
- **TLS and DNS:** Certificate Manager certificates and Cloud DNS records for the hostnames from step 04.
- **Cloud Armor:** the preconfigured OWASP rules plus per-IP rate limits. On the webhook path, rate limits only; the receiver checks signatures (step 17).
- **IAP:**
  - on the UI, API and preview backends, using Workforce Identity Federation with the Okta pool from step 04,
  - access granted by Okta group,
  - not on the webhook backend, because GitHub can't authenticate through IAP.
- **Identity check:** configure the `libs/common` IAP helper from step 03 with each backend's real audience.
- **ADR 0004, "Preview URLs":** one host with the session in the path (simplest), or a subdomain per session with a wildcard certificate.

## Out of scope

The services behind the load balancer. Deploy hello-world placeholders to test.

## Acceptance criteria

- [ ] An Okta user in the builders group reaches a hello endpoint on each IAP backend, and a user outside the group is refused.
- [ ] In hub-dev, each backend receives the IAP JWT, and the helper from step 03 validates it.
- [ ] The webhook path is reachable from GitHub without IAP.
- [ ] Cloud Armor blocks a test SQL-injection request.

## Notes

- Use IAP on the load balancer, which is generally available, rather than IAP directly on Cloud Run.
