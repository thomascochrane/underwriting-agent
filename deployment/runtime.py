"""Small deployment helper; credentials and mutable settings stay in /opt/data."""
from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import sys

sys.path.insert(0, '/opt/hermes')

import hermes_yaml as yaml
from dotenv import dotenv_values, set_key

HOME = Path(os.environ.get("HERMES_HOME", "/opt/data"))
SEED = Path("/deployment")
MARKER = HOME / ".zivoe-underwriting-initialized"


def initialize() -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    if MARKER.exists():
        print("Already initialized; existing configuration, credentials, and memory preserved.")
        return
    config_path = HOME / "config.yaml"
    config = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    config = config or {}
    seed = yaml.safe_load((SEED / "config.yaml").read_text())
    for section, values in seed.items():
        config[section] = {**(config.get(section) or {}), **values}
    # The upstream example contains an OpenRouter endpoint. Let the explicit
    # openai-codex provider resolve its own endpoint and OAuth credentials.
    for key in ("base_url", "api_key"):
        config["model"].pop(key, None)
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    shutil.copyfile(SEED / "SOUL.md", HOME / "SOUL.md")
    env_path = HOME / ".env"
    env_path.touch(exist_ok=True)
    for key, value in {
        "API_SERVER_ENABLED": "false",
        "TELEGRAM_ALLOW_ALL_USERS": "false",
        "GATEWAY_ALLOW_ALL_USERS": "false",
        "EMAIL_ALLOW_ALL_USERS": "false",
    }.items():
        set_key(str(env_path), key, value)
    os.chmod(env_path, 0o600)
    config_path.chmod(0o600)
    MARKER.write_text("Base underwriting deployment initialized.\n", encoding="utf-8")
    print("Initialized underwriting settings. ChatGPT login and Telegram setup are separate steps.")


def codex_logged_in() -> bool:
    from hermes_cli.auth import get_codex_auth_status
    return bool(get_codex_auth_status().get("logged_in"))


def readiness() -> dict:
    env = dotenv_values(HOME / ".env")
    token = env.get("TELEGRAM_BOT_TOKEN", "") or ""
    users = env.get("TELEGRAM_ALLOWED_USERS", "") or ""
    return {
        "initialized": MARKER.exists(),
        "chatgpt_logged_in": codex_logged_in(),
        "telegram_token_present": bool(re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]+", token)),
        "telegram_users_configured": bool(re.fullmatch(r"[0-9]+(?:\s*,\s*[0-9]+)*", users)),
        "workspace_writable": os.access("/workspace", os.W_OK),
    }


def configure_telegram() -> None:
    if not MARKER.exists():
        raise SystemExit("Run Initialize first.")
    print("Use a NEW BotFather bot token dedicated to this deployment.")
    token = getpass.getpass("Telegram bot token (hidden): ").strip()
    if not re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]+", token):
        raise SystemExit("Token format is invalid; nothing saved.")
    users = input("Allowed numeric Telegram user IDs (comma-separated): ").strip()
    if not re.fullmatch(r"[0-9]+(?:\s*,\s*[0-9]+)*", users):
        raise SystemExit("Numeric user IDs are required; nothing saved.")
    env_path = HOME / ".env"
    set_key(str(env_path), "TELEGRAM_BOT_TOKEN", token)
    set_key(str(env_path), "TELEGRAM_ALLOWED_USERS", ",".join(x.strip() for x in users.split(",")))
    set_key(str(env_path), "TELEGRAM_ALLOW_ALL_USERS", "false")
    env_path.chmod(0o600)
    print("Telegram settings saved in the Docker volume. Start the gateway to connect.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["initialize", "status", "check", "telegram", "gateway"])
    action = parser.parse_args().action
    if action == "initialize":
        initialize()
        return
    if action == "telegram":
        configure_telegram()
        return
    state = readiness()
    if action == "status":
        print(json.dumps(state, indent=2))
        return
    missing = [key for key, ready in state.items() if not ready]
    if missing:
        print("Not ready: " + ", ".join(missing), file=sys.stderr)
        raise SystemExit(78)
    if action == "check":
        print("Local prerequisites are present. Live provider and Telegram connectivity still require a smoke test.")
        return
    os.execvp("hermes", ["hermes", "gateway", "run"])


if __name__ == "__main__":
    main()