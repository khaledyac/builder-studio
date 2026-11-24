# 15 · Preview proxy

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 07, 08, 14

## Why

The builder sees their running app in the preview panel, and nobody else can. Architecture: §2, §3, §12.

## Build

In `services/preview-proxy`, behind the load balancer and IAP:

- Read the IAP JWT, and check in Firestore that the user is the session's author.
- Proxy HTTP and WebSocket traffic (for hot reload) to the workspace's dev server, authenticating with a Google ID token.
- Route by path, `/preview/<session>/...` (or as decided in ADR 0004), and rewrite base paths for the dev server.
- Tolerate long-lived connections and reconnects: Cloud Run caps a request at 60 minutes.

## Out of scope

The UI panel itself (step 19).

## Acceptance criteria

- [ ] The author sees the live app, and another builder gets a 403.
- [ ] Hot reload works through the proxy.
- [ ] A dropped WebSocket reconnects without reloading the page.
- [ ] An expired session returns a clear "session ended, reopen the app" page.

## Notes

- Don't inject anything into the app's pages. The UI draws the "synthetic data · only you" badge.
