# 19 · Web UI shell

**Milestone:** M1 · **Tag:** ready-for-agent · **Size:** M · **Blocked by:** 15, 16

## Why

What builders see: three panels, live status and the preview. Architecture: §1, §3, and the UI example on the Whiteboard.

## Build

In `web/`, a React and TypeScript app served by Cloud Run behind IAP. There is no login screen: IAP handles Okta.

- **Layout,** following the Whiteboard UI example:
  - top bar: app name, tier badge, status chips, session budget, Publish button,
  - left: "My apps" and "Domain gallery" tabs,
  - centre: the chat,
  - right: the preview, in an iframe served by the preview proxy, with a "synthetic data · only you see this" badge.
- **Streaming:** a server-sent events client with reconnection, and optimistic sending of messages.
- **Flows:** New app (for M1, it creates a session with a fixture `need.yml`) and opening an existing app.
- **Design:** the brand tokens, keyboard navigation and accessible contrast.
- **Tests:** Playwright end-to-end tests against the local stack.

## Out of scope

The intake cards (step 22), the plan cards (step 24) and the Publish stepper (step 25).

## Acceptance criteria

- [ ] On the local stack: sign in as a seed builder, click New app, and the starter appears in the preview. The status chips follow replayed deploy events.
- [ ] In hub-dev, sign-in through IAP and the preview work for the session's author.
- [ ] The gallery tab lists apps their owners have shared (read-only for now).
- [ ] Lighthouse accessibility score of 90 or more.
