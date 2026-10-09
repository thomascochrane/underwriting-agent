# Zivoe underwriting agent

Base Hermes deployment for Zivoe underwriting. Runs independently of the existing
Hermes/Open WebUI installation. Current scope: one assistant, ChatGPT subscription
authentication, Telegram when configured, and a persistent local workspace.
Email is a later connection; no browser frontend or public ports are enabled.

## Quick start (Windows / Docker Desktop)

From this repository in PowerShell:

```powershell
.\scripts\hermes.ps1 -Action Initialize
.\scripts\hermes.ps1 -Action Login
```

Login creates a separate Hermes OAuth session using your ChatGPT subscription.
Open the URL printed by Hermes, enter its temporary device code, and complete
sign-in yourself. Host Codex credentials are not mounted or copied. The initial
model is gpt-5.4; use `-Action Model` to choose another available model.

Telegram is intentionally deferred. When ready:

1. In Telegram, open the verified @BotFather and create a **new** bot with /newbot.
2. Obtain your numeric Telegram user ID (for example, from @userinfobot).
3. Run the commands below. The token prompt is hidden and writes directly to the
   Docker volume, not to this repository. Do not reuse the existing agent's bot token.

```powershell
.\scripts\hermes.ps1 -Action Telegram
.\scripts\hermes.ps1 -Action Start
.\scripts\hermes.ps1 -Action Status
```

Open the new bot, press Start, and ask it to identify its role. Confirm a reply.
The local Check command checks configuration presence, not live network access.
The gateway deliberately refuses to start until initialization, ChatGPT login,
a Telegram token, and numeric allowed-user IDs are present.

## Files and persistence

| Location | Purpose |
| --- | --- |
| Docker volume `zivoe-agents_hermes-state` | Config, OAuth credentials, bot token, memory, skills, sessions |
| `workspace/` | Deal folders, working files, and outputs; mounted at /workspace |
| `deployment/` | Versioned initial configuration, assistant instructions, deployment helper |
| `scripts/hermes.ps1` | Local management commands |

Runtime state uses a Linux Docker volume rather than a OneDrive-hosted SQLite
database. Files under workspace are gitignored, but **OneDrive can still sync
them**, because this checkout lives under OneDrive. Use only appropriate files.
Other local diligence folders and the underwriting-engine checkout are not mounted.

The default Hermes profile is the underwriting assistant. More profiles can be
added later. Profiles separate agent state, not filesystem permissions.

Initialize applies defaults once. Repeating it preserves settings and credentials.
Editing the seed configuration or SOUL.md later does not overwrite an existing
volume; use Hermes configuration commands inside `-Action Shell` for live changes.

## Operation

```powershell
.\scripts\hermes.ps1 -Action Status
.\scripts\hermes.ps1 -Action Logs
.\scripts\hermes.ps1 -Action Stop
.\scripts\hermes.ps1 -Action Chat
```

Stop the gateway before Login, Model, Telegram, Chat, or Shell. This avoids a second
agent process editing the same state while the gateway runs. Chat lets you test
the model before Telegram is connected. Starting Docker Desktop may also start
other previously configured containers; this project only manages its own service.

The container starts as root for the official image bootstrap, then drops the
Hermes process to the image's non-root hermes user. It has no Docker socket or host
home directory mount. No incoming host ports are published. Telegram uses outbound
long polling. Bot access is restricted to the entered numeric user IDs.

`docker compose stop` and `docker compose down` preserve the state volume.
**Do not use `docker compose down -v` unless you intend to erase credentials,
memory, and conversations.** Container persistence is not a backup. Before an
upgrade, stop the gateway and back up the Docker state volume using Docker Desktop's
volume export/backup facility, plus workspace separately. Backups contain secrets.

## Version and upgrades

The official stable image downloaded on 2026-10-08 is pinned by SHA256 in compose.yaml.
Upstream revision: `818c13be1dc4fd28987e1e881a9408224afd4535`.
The image provenance reports version 0.0.0, so the digest and revision identify it.
There are no automatic image upgrades. To upgrade, back up, test a new official
image, update the digest deliberately, then Initialize (preserves state) and Start.
Restoring an older image may also require restoring its matching state backup.

## Validation

Run `.\scripts\hermes.ps1 -Action Test` for offline deployment tests. These check
first-time initialization, preservation of later settings and credentials, explicit
Telegram user restrictions, and refusal to launch without required credentials.
They do not contact a model, Telegram, or an email provider.

## What is not connected yet

- ChatGPT login (deferred by the owner; no authenticated model test yet).
- Telegram token and allowed-user IDs (deferred by the owner).
- Email; see [email setup notes](docs/email.md).
- The separate underwriting engine and Windows Excel recalculation.
- Automated document review, lender outreach, or access to live deal folders.

This container is the runtime foundation, not a finished underwriting workflow.

## References

- [Official Docker deployment](https://hermes-agent.nousresearch.com/docs/user-guide/docker)
- [Telegram setup](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)
- [Model providers](https://hermes-agent.nousresearch.com/docs/integrations/providers/)
## General diligence and MCA skills

Nine custom skills cover intake, evidence reconciliation, financial review,
transaction structure, memo drafting, MCA tape analysis, MCA servicing review,
ongoing performance review, and evidence-backed underwriting learning.
Install them with `.\scripts\hermes.ps1 -Action Skills` while the gateway is stopped.
This works before authentication. See [skill scope, installation and demo cases](docs/skills.md).
The engine retains its own AI mapper and reviewer; connecting the engine remains a separate step.