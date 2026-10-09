# Finish the private Telegram demo

Open PowerShell on your computer:

```powershell
ssh root@2.29.3.5
```

On the server:

```sh
cd /opt/underwriting-agent
bash scripts/server.sh stop hermes
bash scripts/server.sh run --rm hermes /opt/hermes/.venv/bin/python /deployment/runtime.py telegram
```

Paste the dedicated BotFather token at the hidden prompt, then your numeric Telegram user ID. This allows your private chat only. The helper also configures the independent result-delivery service. Do not paste tokens into chat or shell command arguments.

Sign Hermes in using its own ChatGPT session:

```sh
bash scripts/server.sh run --rm hermes auth add openai-codex --no-browser
```

Sign in the engine's separate Codex session. Follow the device-login instructions shown:

```sh
bash scripts/server.sh stop engine-worker
bash scripts/server.sh run --rm --entrypoint codex engine-worker login --device-auth
bash scripts/server.sh up -d engine-worker engine-notifier
```

Check Hermes prerequisites, then start it if the check succeeds:

```sh
bash scripts/server.sh run --rm -T hermes /opt/hermes/.venv/bin/python /deployment/runtime.py check
bash scripts/server.sh up -d hermes
```

In Telegram, open the bot, press Start and send:

> Check the engine worker's health and tell me which asset classes are installed. Do not submit a job yet.

Then, for an explicitly limited delivery test using the existing fictional workbook:

> Run the fictional MCA tape at /workspace/engine-demo-varied/synthetic-tape.xlsx with /workspace/engine-demo-varied/config, originator synthetic-demo and as-of 2026-09-02. For this test only, disable engine AI. Submit it as a background engine job, return its ID immediately, and send the resulting files here when complete.

This checks real private-chat submission and result delivery without requiring an unfamiliar live tape. Next, run an explicitly requested AI-enabled test and inspect `ai_review` separately. Only a received Telegram message/file establishes live delivery; a queued job or configuration check does not.

Always use `bash scripts/server.sh` for this installed deployment. It includes the engine overlay automatically, preserving shared job mounts when Hermes is recreated. Google Drive, email, group access and the large-file Telegram service remain deferred.
