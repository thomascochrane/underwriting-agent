# Repository instructions

This repository deploys the Zivoe Hermes assistant. Current scope is the base
underwriting runtime, ChatGPT authentication, and future Telegram/email connections.

- Keep credentials and actual deal data out of Git and tool output.
- Runtime credentials/state live in the Docker volume; workspace content is ignored.
- Do not modify or stop unrelated containers (including hermes and openwebui).
- Do not edit the separate underwriting engine as part of deployment work.
- Pin container images by digest. Do not silently update to latest.
- Keep dashboards and host ports disabled unless explicitly requested.
- Telegram uses a dedicated bot and an explicit numeric user allowlist.
- Do not connect an inbox or send external messages without user authorization.
- Do not add other profiles or full diligence workflows until requested.
- Validate Compose configuration and run bootstrap/idempotence/readiness smoke checks
  when changing deployment behavior. Do not print secret values while testing.