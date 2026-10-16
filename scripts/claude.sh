#!/usr/bin/env bash
# Run from the server checkout; never copy another agent's Claude credentials.
set -euo pipefail
cd "$(dirname "$0")/.."
action="${1:-status}"
case "$action" in install|login|status) ;; *) echo 'Usage: bash scripts/claude.sh install|login|status' >&2; exit 2 ;; esac
if [[ -n "$(bash scripts/server.sh ps --status running -q hermes)" ]]; then
  echo 'Stop this underwriting Hermes gateway before maintenance.' >&2
  exit 1
fi
claude=/opt/data/claude-cli/node_modules/.bin/claude
case "$action" in
  install)
    bash scripts/server.sh run --rm --no-deps -T --user 10000:10000 --entrypoint /bin/bash hermes -c '
      set -euo pipefail
      umask 077
      mkdir -p /opt/data/claude-config
      chmod 700 /opt/data/claude-config
      npm install --prefix /opt/data/claude-cli --cache /opt/data/.npm-claude --no-audit --no-fund @anthropic-ai/claude-code@2.1.301
      cd /opt/data/claude-cli
      npm install-scripts approve @anthropic-ai/claude-code
      npm rebuild @anthropic-ai/claude-code --cache /opt/data/.npm-claude
      /opt/hermes/bin/hermes plugins install claude-subscription-directsdk --ref ad20043d4faf61081a905fc684d7c0ba3dfe9d6b --yes-deps --enable
      /opt/data/claude-cli/node_modules/.bin/claude --version
    '
    ;;
  login)
    bash scripts/server.sh run --rm --no-deps --user 10000:10000 --entrypoint "$claude" hermes auth login
    ;;
  status)
    bash scripts/server.sh run --rm --no-deps -T --user 10000:10000 --entrypoint "$claude" hermes auth status
    ;;
esac
