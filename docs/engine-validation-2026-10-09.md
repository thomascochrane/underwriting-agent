# Engine integration validation — 2026-10-09

Engine source snapshot: `2f30ddc1b9c223fc15ddb94808c7177a2c7a9a09` from the separate Zivoe engine checkout. That checkout was not edited.

Deployed engine image: `sha256:50eb7c4a39ddb08c725e901a27d6e216a60e7cbc1daf2b093d10056cda43af5d`. Codex CLI: 0.162.0. The runtime supports the CLI flags used by the existing engine backend. Full Python dependency versions are retained in the image at `/opt/engine-dependencies.txt`.

## Completed checks

- 29 offline job/delivery tests passed, including input snapshots, duplicate submissions, asset-class routing/rejection, cancellation, timeout, process-result classification, rate limiting, receipts and ambiguous-send recovery.
- The existing 4 deployment smoke tests and 7 skill installation tests passed; all 10 installed skills matched the integration source.
- Combined Compose configuration validated. Worker and notifier have no published ports and no Docker socket. The engine has its own login volume; the notifier receives only the underwriting bot credentials and private-user allowlist when configured.
- A separate test container was forcibly killed while processing a synthetic job. On restart it marked the job interrupted and did not rerun it. No credentials or provider calls were involved.
- Two jobs queued while the production worker was stopped were processed after it restarted. They ran sequentially.
- The real engine processed a six-row varied fictional tape with `--no-ai`: PASS, no engine notes, 17 workbook sheets including Stratifications, and a valid result ZIP. Job: `6dba129177644a4faeea1549de8b821f`.
- A six-row flat-cohort fixture exposed an upstream `NoneType` formatting error in stratification generation. The engine still reports tape-validation PASS; the connector correctly reports `completed_with_warnings` and explicitly marks the workbook incomplete. Regression job: `6929248c90d24a8390867082b6ac656c`. The engine bug was not patched in this integration.

These are fictional test artifacts. No actual diligence package, Telegram recipient or model was used in these tests.

## Still to verify after account setup

Hermes ChatGPT login, engine Codex login, live private Telegram intake and confirmed file delivery, AI mapping/review, full document-review behavior, and performance on representative real deal packages. Native Excel formula recalculation is not provided by the Linux worker. The durable queue covers engine jobs, not an automatically scheduled full diligence/memo workflow.

See [private demo setup](private-demo-setup.md) for the remaining interactive steps.
