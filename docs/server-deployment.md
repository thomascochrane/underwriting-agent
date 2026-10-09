# Server deployment

Deployment directory: `/opt/underwriting-agent`. Compose project: `zivoe-agents`.
Use both Compose files for every server operation so the 3 GiB memory and 2 CPU
limits are applied. Limits are ceilings, not reservations. No host ports are exposed.
The optional engine worker is described in [engine jobs](engine-jobs.md). On servers using it, add `--env-file engine.env` and `-f compose.engine.yaml` to Compose commands, including Hermes credential setup and recreation.

The deployment uses a Git archive of a recorded commit, not a checkout with GitHub
credentials. `DEPLOYED_COMMIT` records that revision; `source.sha256` records the
transferred archive hash. Server-only provenance files are not part of Git.

## Initial setup

From the deployment directory:

```sh
docker compose -f compose.yaml -f compose.server.yaml config --quiet
docker compose -f compose.yaml -f compose.server.yaml pull hermes
# The pinned image runs Hermes as UID/GID 10000.
chown 10000:10000 workspace
chmod 750 workspace
docker compose -f compose.yaml -f compose.server.yaml run --rm -T hermes /opt/hermes/.venv/bin/python /deployment/runtime.py initialize
docker compose -f compose.yaml -f compose.server.yaml run --rm -T hermes /opt/hermes/.venv/bin/python /deployment/skills.py install
docker compose -f compose.yaml -f compose.server.yaml create hermes
```

Until sign-in and Telegram setup are completed, leave the persistent container
stopped. Initialization and skill installation do not connect a model or bot.
Credentials and conversations will live in `zivoe-agents_hermes-state`; files and
outputs go in `workspace/`. Existing agents' state and credentials are not mounted.

## Connect later

Use an interactive SSH terminal. Stop this gateway before changing credentials.

```sh
docker compose -f compose.yaml -f compose.server.yaml run --rm hermes auth add openai-codex --no-browser
docker compose -f compose.yaml -f compose.server.yaml run --rm hermes /opt/hermes/.venv/bin/python /deployment/runtime.py telegram
docker compose -f compose.yaml -f compose.server.yaml run --rm -T hermes /opt/hermes/.venv/bin/python /deployment/runtime.py check
docker compose -f compose.yaml -f compose.server.yaml up -d hermes
```

The last command is appropriate only after the prerequisite check succeeds.
Complete login directly with the provider and enter the dedicated Telegram token
at the hidden prompt. Do not put credentials in this repository or copy another
assistant's login. Live replies must be tested after those connections are ready.

## Operations

```sh
docker compose -f compose.yaml -f compose.server.yaml ps --all
docker compose -f compose.yaml -f compose.server.yaml logs --tail 100 hermes
docker compose -f compose.yaml -f compose.server.yaml stop hermes
```

Change CPU/memory ceilings in `compose.server.yaml`, validate the combined config,
and recreate only this service. Back up the state volume and workspace before
upgrades; backups contain private data and credentials. Do not prune server images,
stop unrelated services, or delete state volumes as part of updating this agent.
