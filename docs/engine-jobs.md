# Engine jobs on the server

The prototype runs the existing underwriting engine in a separate worker with one job at a time. Each versioned job request names an asset class. The worker discovers installed engine plug-ins and rejects unsupported classes; MCA is the first installed class. A SQLite queue and copied inputs/configuration live in `job-state/`; a separate notifier delivers results directly through Telegram. There is no public API or Docker socket. Hermes uses the file-backed client interface in `deployment/jobs/client.py`.

The engine source is a private, ignored snapshot of Zivoe/zivoe-underwriter commit `2f30ddc1b9c223fc15ddb94808c7177a2c7a9a09`. The integration repository contains the adapter and build instructions, not a copy of the private engine repository. The build pins the Hermes base image and Codex CLI version; the deployed engine image is selected by its exact local SHA256. Python package versions are recorded inside the image at `/opt/engine-dependencies.txt`; rebuilding from unlocked upstream package ranges may produce a different image and requires retesting.

## Server commands

From `/opt/underwriting-agent`, use all three Compose files and the image selection file for integration operations:

```sh
docker compose --env-file engine.env -f compose.yaml -f compose.server.yaml -f compose.engine.yaml ps --all
```

One-time engine authentication, separate from Hermes (stop an active worker before altering its login):

```sh
docker compose --env-file engine.env -f compose.yaml -f compose.server.yaml -f compose.engine.yaml stop engine-worker
docker compose --env-file engine.env -f compose.yaml -f compose.server.yaml -f compose.engine.yaml run --rm --entrypoint codex engine-worker login --device-auth
docker compose --env-file engine.env -f compose.yaml -f compose.server.yaml -f compose.engine.yaml up -d engine-worker engine-notifier
```

Use the same combined Compose invocation when configuring Telegram or starting/recreating Hermes, so `/jobs` and `/job-channel` stay mounted. The token helper syncs only this bot's token and numeric private-user allowlist to `channel-state/telegram.json`, mode 0600. The notifier mounts this directory read-only; the engine never receives the Telegram token. Existing credentials can be synced with:

```sh
docker compose --env-file engine.env -f compose.yaml -f compose.server.yaml -f compose.engine.yaml run --rm -T hermes /opt/hermes/.venv/bin/python /deployment/jobs/sync_channel.py
```

Run this with the gateway stopped, or use `exec -T --user hermes hermes` in place of `run --rm -T hermes` when it is already running. No tokens appear in command arguments or output. Sync again after token rotation/revocation or allowlist changes. Private chats are the only permitted destinations in this prototype.

## Submission and result contract

Inside Hermes, `/opt/hermes/.venv/bin/python /deployment/jobs/client.py` supports `submit`, `status`, `list`, `health`, and `cancel`. `submit` accepts an Excel tape, a required `--asset-class` and idempotency/request key, supported engine options, optional complete config or a selected deal YAML overlay, and no arbitrary shell command. Session environment supplies the originating Telegram chat. An operator can explicitly pass `--chat-id` outside a gateway session; it must be in the copied private-user allowlist. `--offline` suppresses delivery for a deliberate local test.

Source locations are restricted to `/workspace`, Hermes' attachment cache, and prior `/jobs` artifacts. Sources are copied and SHA256-checked before queueing and checked again by the worker. Each job gets a private baseline config copy; generated AI mapping drafts remain with that job. Reuse requires an explicit config selection, rather than allowing one deal to silently modify all later runs. Deal YAML is validated by the real engine; its terms still require source review.

The result separates engine validation PASS/FAIL, process failure, and AI review status. `results.zip` contains engine artifacts and input/config provenance, excluding vendor credentials and raw execution logs. A PASS does not establish credit approval, cash-flow completeness, or independently verified lender data. Excel live-formula recalculation is not supplied by this Linux worker.

## Restart and delivery behavior

- Engine computation is independent of Hermes. Closing Telegram or restarting Hermes does not stop the separate engine process.
- A worker restart marks previously running jobs interrupted. Partial files are retained; a new explicit request key/parent-job creates a separate attempt. Queued work remains queued. A host restart cannot resume an arbitrary Python calculation mid-instruction.
- Cancellation and the configured one-hour engine timeout terminate the process group, including model subprocesses. The limit is a maximum execution time, not an estimated completion time.
- Completion state and delivery intent are committed together. The notifier records Telegram message IDs separately for the summary and result ZIP.
- Confirmed rate-limit rejections receive bounded retries. Network timeouts, ambiguous server errors or a notifier restart during sending become `uncertain`, preventing automatic duplicate sends. Review the chat before an explicit retry. Telegram has no exactly-once send guarantee.
- Missing credentials leave delivery pending. Revoked/unauthorized destinations and rejected sends remain visible as failed. Result bundles above the current 49 MiB send threshold remain on the server; the summary says so.
- Workspaces, queue and channel files are owned by UID/GID 10000 and not committed. Back them up together with the engine login volume and Hermes state. Shared files are a trusted single-agent boundary, not tenant isolation.

Operator-only delivery retry (no analysis rerun):

```sh
docker compose --env-file engine.env -f compose.yaml -f compose.server.yaml -f compose.engine.yaml exec -T engine-notifier /opt/hermes/.venv/bin/python /deployment/jobs/notifier.py --retry DELIVERY_ID
```

For an `uncertain` send, first confirm the original did not arrive; the retry additionally requires `--acknowledge-duplicate-risk`. Never retry a confirmed `sent` delivery automatically.

## Prototype limits and validation

The durable queue covers tape inspection, config validation, engine calculation, packaging and file delivery. It does not yet execute a full multi-document review or synthesize a final memo without another Hermes turn. The skill saves document-review checkpoints and makes this distinction explicit. Automatic ZIP intake, scheduled weekly reporting, large-file Telegram, Google Drive, email and group authorization are not added by this deployment.

`deployment/jobs/test_jobs.py` tests snapshot/idempotency, permitted inputs/destinations, exclusive claims, cancellation, subprocess timeout, interrupted work, result/validation failure distinctions, outbox receipts, uncertain sends, rate limits and restart behavior with no real provider calls. `evaluation/make_engine_demo.py` creates a fictional workbook and configuration for a real deterministic engine smoke run. A synthetic no-AI run is not evidence of live AI mapping/review or Telegram receipt; report those checks separately.

## Adding an asset class

The shared queue, snapshots, status, cancellation, recovery, packaging and delivery have no MCA calculations. Add the new class package using the engine's existing AssetClass registry contract, package its schema/configuration and analytics, and deploy a tested engine image that includes it. Worker health advertises the installed classes. Add class-specific Hermes skills and acceptance fixtures; general diligence and learning skills remain shared. The request schema has an explicit version so future non-Excel inputs or extra engine options can be added deliberately. Current Excel input support follows the installed engine intake contract. Never route an unsupported class through MCA.

For server operations, ash scripts/server.sh ... is a convenience wrapper that automatically includes the installed engine overlay and image selection file. Use this instead of omitting the overlay during a future Hermes recreation.

An engine PASS accompanied by reported extension failures, warnings, or a failed/unknown requested AI review becomes completed_with_warnings. The Telegram summary explicitly identifies missing analytics; inspect the original run report before use. The initial synthetic flat-cohort case exposed an upstream NoneType formatting error during stratification generation; that engine source is unchanged. A varied synthetic case and the retained flat case exercise the distinction.

See [recorded validation](engine-validation-2026-10-09.md) and [private Telegram setup](private-demo-setup.md).
