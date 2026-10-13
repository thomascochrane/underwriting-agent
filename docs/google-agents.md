# Shared Agents Google connection

The hosted entry point is `https://zamisla.com/google/agents/`. Its only accepted
Google identity is `agents@zivoe.com`. The route name and credential directory are
general purpose; underwriting is the initial consumer. No other agent receives
this identity automatically.

## Operator setup

1. In Google Cloud project `zamisla-zivoe-internal`, create a **Web application**
   client named **Zivoe Agents** with this exact authorized redirect URI:
   `https://zamisla.com/google/agents/callback`. Retain the Internal audience.
2. Verify Gmail, Drive, Docs, and Sheets APIs are enabled. Download the client JSON.
   Install it as `/opt/zivoe-google-agents/google_client_secret.json`, owned by
   `10000:10000`, mode `0600`. The parent directory is mode `0700`. Never commit it.
3. Create private `google.env` with `GOOGLE_ACCESS_EMAIL=thor@zivoe.com`.
   This is the human connection administrator, not the Google account being
   connected. `scripts/server.sh` automatically adds `compose.google.yaml`.
4. Start only the new service: `bash scripts/server.sh up -d --no-deps google-agents`.
   It listens on host loopback port **9222** only. Keep existing services running.
5. In the existing Cloudflare Tunnel add hostname `zamisla.com`, path
   `^/google/agents(?:/.*)?$`, service `http://localhost:9222`, before the hostname
   catch-all. Protect the entire route, including callback, with Cloudflare Access
   restricted to the operator. Use the matching Access application/audience if
   Tunnel Access validation is enabled. The application verifies the trusted
   Access email header as well; do not expose the origin port or bypass Access.
6. Open the page, authenticate to Cloudflare as the operator, then connect Google
   as **agents@zivoe.com**. Wrong Google identities and partial grants are rejected.
7. Recreate the underwriting Hermes service with this overlay when it is ready
   to run so it receives `/google-agents`. No restart of Jay/Thor/Kristal is needed.

Google tokens persist separately from Hermes in `/opt/zivoe-google-agents`.
Authorization uses expiring, single-use state, PKCE, fixed Google endpoints,
verified email, and atomic private token writes. Callback URLs are not logged.
This follows Zamisla's hosted OAuth pattern without importing its CRM skills.

## Hermes usage

Use the built-in `google-workspace` skill's command reference through this wrapper:

```sh
/opt/hermes/.venv/bin/python /deployment/google/workspace.py drive search "diligence" --max 5
/opt/hermes/.venv/bin/python /deployment/google/workspace.py gmail search "is:unread" --max 5
```

Only this command receives `HERMES_HOME=/google-agents`; Hermes' own memory,
Telegram settings and model authentication remain in `/opt/data`. The Google
client saves refreshes to the mounted directory. Do not run setup.py to authorize
another account. Reconnect through the hosted page.

Requested permissions: Gmail read/send/drafts, Drive read/write, Docs and Sheets
read/write, and verified identity. Calendar and Contacts are not requested.
Granted email capability is not authorization to send messages; obey the user's
instructions. Drive access requires sharing the relevant folders or Shared Drive
with agents@zivoe.com. OAuth itself does not grant access to all company files.

Verify the real Gmail profile, list a shared Drive folder, and upload/download a
small test file in an approved output folder after consent. Token presence alone
does not prove API access. No email should be sent as a connectivity test.

## Future consumers

Another trusted agent can be deliberately configured to use this connection.
Every direct consumer acts as the same Google user with the same permissions and
can access the refresh token. For concurrent agents, introduce a central API broker
to serialize refreshes and enforce per-agent access; do not assume this directory
mount provides per-agent isolation. No additional consumers are configured here.

## Local tests and removal

Run `python -m unittest discover -s deployment/google -p 'test_*.py'`.
Run the repository deployment smoke checks as well. Stop `google-agents` and remove
its Tunnel route to withdraw the sign-in page; do not remove unrelated routes.
To revoke existing API access, revoke the app grant in the Google account too.
Stopping the sign-in page alone does not revoke previously issued tokens.
