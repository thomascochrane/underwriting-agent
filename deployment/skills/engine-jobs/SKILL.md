---
name: engine-jobs
description: "Submit engine jobs and track results without waiting."
version: 0.2.1
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux]
metadata:
  hermes:
    tags: [underwriting, mca, jobs]
---

# Engine jobs

Use the installed persistent job service for engine work. Each job snapshots inputs, runs outside the chat process and records computation and Telegram delivery separately. Jobs name an asset class explicitly; the worker discovers installed engine plug-ins. Only MCA is installed initially. Delivery currently supports authorized private Telegram chats.

## When to Use

- Inspect or analyze an uploaded MCA tape, check a running job, cancel work, or investigate missing results.
- Use with `mca-tape-analysis` for methodology and interpretation; this skill supplies the execution interface.

## Prerequisites

`/deployment/jobs/client.py` and writable `/jobs` must exist. Run `/opt/hermes/.venv/bin/python /deployment/jobs/client.py health` and check the worker heartbeat is recent (normally within seconds; more than 30 seconds old needs investigation). Do not claim the engine is connected merely because the skill exists. The worker's engine login is separate from the Hermes login. Notifications require the configured Telegram token and private-user allowlist.

## Procedure

1. Extract supplied archives into the deal's own `/workspace` directory with the available archive tools; reject paths escaping that directory. Inventory the material using `diligence-intake`. Select the actual Excel tape and establish asset class, population, sheet and as-of date. Check the worker health response for supported asset_classes; do not substitute MCA for an unsupported class. Reading the ZIP or a prior memo is not equivalent to examining every enclosed file.
2. Save an intake checkpoint under the deal's versioned review directory: sources examined, documents still pending, questions, and next step. Preserve this between document-review batches so a new conversation can continue from files. This engine queue does not automatically schedule the remaining document review or a final credit memo.
3. Prepare applicable configuration using the engine's supported schema and sourced terms. For a deal override, write a draft YAML in the deal workspace plus a separate evidence table mapping each override to its source/locator and interpretation. Unknown terms stay unresolved. Do not modify house rules or treat an unapproved methodology change as an accepted policy. Use `--deal-config` with `--deal` for the selected, authorized draft; the service overlays it onto a private copy of baseline config and validates the combined configuration before analysis. For an already prepared complete config directory, use `--config` instead. YAML validation checks schema, not documentary truth.
4. Submit via `terminal` using the example below with verified, safely quoted paths. Use a stable `--request-key` for this exact user request; save it in the review record. Retrying an uncertain submission with the same key returns the same job. A changed input or requested new run gets a new key. Telegram destination is taken from the current session environment; never supply another recipient or use `--offline` silently.

   ```sh
   /opt/hermes/.venv/bin/python /deployment/jobs/client.py submit '/workspace/DEAL/tape.xlsx' --asset-class mca --request-key 'DEAL-REVIEW-tape-1'
   ```

   Optional switches: `--as-of YYYY-MM-DD`, `--sheet 'Sheet Name'`, `--originator name`, `--deal name --deal-config '/workspace/DEAL/deal.yaml'`, `--config '/workspace/DEAL/config'`, `--profile external`. `--inspect-only` queues layout inspection without analysis. `--no-ai --offline` is only for an explicitly requested limited local diagnostic test, not a fallback to conceal missing login.

5. Retain the returned job ID and input manifest reference. Reply promptly that it is queued, with its ID and any unresolved limitations. End the chat turn; do not keep a terminal session polling, use a sleeping loop, or repeatedly ask the model for progress. The independent worker runs one job at a time. The notifier sends the factual completion summary and ZIP to the original authorized private chat when finished, without needing an active model conversation.
6. When asked for progress, run `.../client.py status JOB_ID` once (same Python executable as above). `list` shows recent jobs. States distinguish queued, running, succeeded, completed_with_warnings, validation_failed, failed, interrupted, cancelled. Stage is actual recorded progress, not an estimated percentage. `succeeded` with engine PASS is not credit approval and does not certify that AI review succeeded. Inspect the run report and AI status before making claims.
7. On completion the package contains raw engine artifacts/configuration provenance, not final branded diligence deliverables. Preserve these originals. Apply `/deployment/branding/README.md` to presentation copies and companion reports when preparing the final Hermes deliverables. Broader diligence review and the credit memo are separate work. Inspect the retained outputs under `/jobs/JOB_ID/`, use `mca-tape-analysis` to interpret them, and incorporate findings into the versioned evidence records. Tell the user what is still unreviewed. Do not duplicate the notifier's file send just because its delivery is pending.
8. Cancellation: `.../client.py cancel JOB_ID` requests a stop; verify the resulting state before saying it stopped. After failure/interruption, diagnose first. An authorized rerun uses a new request key and `--parent-job OLD_JOB_ID`; original inputs/outputs remain available. Restarts do not automatically rerun potentially completed calculations.

## Pitfalls

- Files and records persist outside the conversation, but an interrupted engine calculation generally starts again rather than resuming at an arbitrary instruction.
- Delivery states are independent: pending/retry, sent, failed, uncertain. A Telegram message ID confirms API acceptance, not that a person read it.
- An uncertain send may already have arrived. Check with the user before requesting an operator retry; do not resend blindly. Rate-limit rejections are retried with a bounded delay. Fixing delivery must not rerun analysis.
- The current standard Telegram connection still has its 20 MB inbound limit; result packages over 49 MiB are retained locally and explicitly flagged. Large-file Telegram setup is deferred.
- No Docker socket, host commands, arbitrary engine command, email, group access or cross-user delivery is exposed by this interface. The shared filesystem is for this trusted single underwriting agent, not a multi-tenant security boundary.

## Verification

Record job ID, engine revision, input/config hashes, selected methodology, result status and delivery state. Confirm outputs exist and agree with the run report. If worker/notifier is unavailable, report the queued state honestly. Never promise that broad document review or a final memo will finish automatically merely because a tape job was submitted.
