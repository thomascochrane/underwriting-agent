#!/usr/bin/env bash
# Always preserve installed integration mounts when managing the server deployment.
set -euo pipefail
cd "$(dirname "$0")/.."
args=(-f compose.yaml -f compose.server.yaml)
if [[ -f engine.env ]]; then
  args=(--env-file engine.env "${args[@]}" -f compose.engine.yaml)
fi
exec docker compose "${args[@]}" "$@"
